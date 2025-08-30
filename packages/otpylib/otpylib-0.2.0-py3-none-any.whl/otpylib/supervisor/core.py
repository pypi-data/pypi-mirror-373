"""
Static supervisor for managing persistent, long-running processes.

The static supervisor is designed to manage services that should continuously
run and be restarted when they fail - things like web servers, database 
connections, message processors, etc.

For one-off tasks or batch jobs, use other patterns like genserver.
"""

from collections.abc import Callable, Awaitable
from typing import Any, Dict, List, Optional
import logging
import time

from collections import deque
from dataclasses import dataclass, field

import anyio
from anyio import CancelScope

from otpylib.types import (
    NormalExit, ShutdownExit, BrutalKill, GracefulShutdown, TimedShutdown, 
    ShutdownStrategy, RestartStrategy, SupervisorStrategy,
    Permanent, Transient, OneForOne, OneForAll, RestForOne
)


@dataclass
class child_spec:
    id: str
    task: Callable[..., Awaitable[None]]
    args: List[Any]
    restart: RestartStrategy = Permanent()
    shutdown: ShutdownStrategy = TimedShutdown(5000)


@dataclass
class options:
    """Supervisor options."""
    max_restarts: int = 3
    max_seconds: int = 5
    strategy: SupervisorStrategy = OneForOne()
    shutdown_strategy: ShutdownStrategy = TimedShutdown(5000)


@dataclass
class _ChildProcess:
    """Runtime state of a child."""
    spec: child_spec
    cancel_scope: CancelScope
    task: Optional[anyio.abc.TaskGroup] = None
    restart_count: int = 0
    failure_times: deque = field(default_factory=lambda: deque())
    last_exception: Optional[Exception] = None


class _SupervisorState:
    """Shared state for coordinating children."""
    
    def __init__(self, specs: List[child_spec], opts: options):
        self.opts = opts
        self.children: Dict[str, _ChildProcess] = {}
        self.start_order: List[str] = []
        self.task_group: Optional[anyio.abc.TaskGroup] = None
        self.failed_children: List[tuple[str, Exception]] = []
        self.shutting_down = False
        
        # Initialize children
        for spec in specs:
            self.children[spec.id] = _ChildProcess(
                spec=spec,
                cancel_scope=CancelScope()
            )
            self.start_order.append(spec.id)

    def should_restart_child(self, child_id: str, failed: bool, exception: Optional[Exception] = None) -> bool:
        """Check if a specific child should restart."""
        child = self.children[child_id]
        
        # If shutting down, don't restart
        if self.shutting_down:
            return False

        # For TRANSIENT: only restart on actual exceptions (not normal completion or NormalExit)
        if isinstance(child.spec.restart, Transient):
            if not failed or isinstance(exception, NormalExit):
                return False

        # Only count actual failures (exceptions that aren't NormalExit) for restart limits
        if failed and isinstance(exception, Exception) and not isinstance(exception, NormalExit):
            # Check if within time window
            current_time = time.time()
            child.failure_times.append(current_time)
            
            # Remove failures outside the time window
            cutoff_time = current_time - self.opts.max_seconds
            while child.failure_times and child.failure_times[0] < cutoff_time:
                child.failure_times.popleft()
            
            # Check if we've exceeded max_restarts within the time window
            if len(child.failure_times) > self.opts.max_restarts:
                return False

        return True

    def get_affected_children(self, failed_child_id: str, exceeded_limit: bool) -> List[str]:
        """Determine which children are affected by a failure."""
        if not exceeded_limit:
            return [failed_child_id]  # Just restart the one
            
        if isinstance(self.opts.strategy, OneForOne):
            # Even if limit exceeded, only this child is terminated
            return [failed_child_id]
        elif isinstance(self.opts.strategy, OneForAll):
            # All children must restart
            return list(self.children.keys())
        elif isinstance(self.opts.strategy, RestForOne):
            # This child and all started after it
            idx = self.start_order.index(failed_child_id)
            return self.start_order[idx:]
        else:
            # Default fallback
            return [failed_child_id]


async def start(
    child_specs: List[child_spec],
    opts: options,
    task_status=None,
) -> None:
    """Start the supervisor with the given children and strategy."""
    
    state = _SupervisorState(child_specs, opts)
    logger = logging.getLogger("otpylib.supervisor")
    
    try:
        async with anyio.create_task_group() as tg:
            state.task_group = tg
            
            # Start all children initially
            for child_id in state.start_order:
                tg.start_soon(_run_child, state, child_id, logger)
            
            # Signal supervisor is ready
            if task_status:
                task_status.started(None)
    except* Exception as eg:
        # Re-raise the exception group, which will contain any child failures
        raise

async def _run_child(state: _SupervisorState, child_id: str, logger: logging.Logger) -> None:
    """Run and monitor a single child, coordinating with supervisor on failures."""

    child = state.children[child_id]

    while not state.shutting_down:
        failed = False
        exception = None
        
        try:
            with child.cancel_scope:
                await child.spec.task(*child.spec.args)
            
            # Task completed - this is unusual for persistent services
            logger.warning(f"Child {child_id} completed unexpectedly (persistent services should not exit)")

        except anyio.get_cancelled_exc_class():
            logger.info(f"Child {child_id} cancelled by supervisor")
            return

        except ShutdownExit:
            # ShutdownExit means never restart regardless of strategy
            logger.info(f"Child {child_id} requested shutdown")
            return

        except NormalExit as e:
            # NormalExit respects restart strategy
            logger.info(f"Child {child_id} exited normally")
            exception = e
            # This will be handled by restart logic below

        except Exception as e:
            failed = True
            exception = e
            child.last_exception = e
            logger.error(f"Child {child.spec.id} failed", exc_info=e)

        # Decide what to do next
        should_restart = state.should_restart_child(child_id, failed, exception)

        if not should_restart:
            if failed:
                # Check if this was due to restart limit being exceeded
                if len(child.failure_times) > state.opts.max_restarts:
                    # Restart intensity exceeded → crash the supervisor
                    logger.error(f"Child {child.spec.id} terminated (restart limit exceeded)")
                    state.shutting_down = True
                    # Raise the exception to crash the task group
                    raise RuntimeError(
                        f"Supervisor shutting down: restart limit exceeded for child {child_id}"
                    ) from exception
                else:
                    # TRANSIENT with normal exit
                    logger.info(f"Child {child_id} completed and will not be restarted")
                    return
            elif isinstance(exception, NormalExit):
                # NormalExit with non-restarting strategy is normal
                logger.info(f"Child {child_id} completed with NormalExit and will not be restarted")
                return
            else:
                # Normal completion (no exception): just stop child
                logger.info(f"Child {child_id} completed and will not be restarted")
                return

        # Otherwise restart the child after a small delay
        if not state.shutting_down:
            logger.info(f"Restarting child {child_id}")
            child.restart_count += 1
            await anyio.sleep(0.01)  # Small delay before restart
