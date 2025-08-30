from enum import Enum
from dataclasses import dataclass, field
from typing import (
    TypeVar, Generic, Callable, Any, Optional, Dict, List, 
    Union, Protocol, runtime_checkable
)

# GENERIC TYPES
T = TypeVar('T')

####
##      WORKER STATE
#####
class WorkerState(Enum):
    """Possible state of a worker"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


####
##      EXECUTION PRIORITY
#####
class Priority(Enum):
    """Task execution priority"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


####
##      WORKER RESULT
#####
@dataclass
class WorkerResult(Generic[T]):
    """Worker execution result"""

    worker_id: str
    state: WorkerState
    result: Optional[T] = None
    error: Optional[Exception] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


####
##      WORKER POOL CONFIGURATION
#####
@dataclass
class WorkerPoolConfig:
    """Worker Pool Configuration."""

    max_workers: int = 4
    queue_size: int = 100
    enable_priority: bool = True
    timeout: Optional[float] = None
    auto_shutdown: bool = True