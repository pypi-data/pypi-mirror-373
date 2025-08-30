"""
Parallel worker system.
Similar to Qt's QRunnable but more flexible and type-safe
"""

from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
import functools
from threading import Lock, Event
from typing import (
    TypeVar, Generic, Callable, Any, Optional, Dict, List, 
    Protocol, runtime_checkable
)
import logging
import traceback
from functools import wraps
import time

from fletx.core.concurency.config import (
    WorkerState, T, Priority, WorkerResult,
    WorkerPoolConfig
)

# GENERIC TYPES
R = TypeVar('R')


####
##      RUNNABLE OBJECTS PROTOCOL
#####
@runtime_checkable
class Runnable(Protocol):
    """Runnable objects Protocol"""

    def run(self) -> Any:
        """Main execution method"""
        ...


####
##      BASE CLASS FOR WORKERS
#####
class BaseWorker(ABC, Generic[T]):
    """Base class for all workers"""
    
    def __init__(
        self, 
        worker_id: Optional[str] = None, 
        priority: Priority = Priority.NORMAL
    ):
        self.worker_id = worker_id or f"worker_{id(self)}"
        self.priority = priority
        self.state = WorkerState.PENDING
        self._result: Optional[T] = None
        self._error: Optional[Exception] = None
        self._execution_time: float = 0.0
        self._metadata: Dict[str, Any] = {}
        self._cancelled = Event()
        
    @abstractmethod
    def execute(self) -> T:
        """
        Abstract worker logic execution method.
        This method should be overridden by worker subclasses
        to implement custom logic.
        """
        pass
    
    def run(self) -> WorkerResult[T]:
        """Executes the worker and return a worker result"""

        if self._cancelled.is_set():
            self.state = WorkerState.CANCELLED
            return self._create_result()
            
        self.state = WorkerState.RUNNING
        start_time = time.time()
        
        try:
            self._result = self.execute()
            self.state = WorkerState.COMPLETED

        except Exception as e:
            self._error = e
            self.state = WorkerState.FAILED
            logging.error(f"Worker {self.worker_id} failed: {e}")
            logging.debug(traceback.format_exc())

        finally:
            self._execution_time = time.time() - start_time
            
        return self._create_result()
    
    def cancel(self) -> bool:
        """Cancel worker execution"""

        # Set state to cancelled
        if self.state == WorkerState.PENDING:
            self._cancelled.set()
            self.state = WorkerState.CANCELLED
            return True
        return False
    
    def is_cancelled(self) -> bool:
        """Checks if worker is cancelled"""

        return self._cancelled.is_set()
    
    def _create_result(self) -> WorkerResult[T]:
        """Creates worker result"""

        return WorkerResult(
            worker_id = self.worker_id,
            state = self.state,
            result = self._result,
            error = self._error,
            execution_time = self._execution_time,
            metadata = self._metadata.copy()
        )


####
##      FUNCTIONS WORKER CLASS
#####
class FunctionWorker(BaseWorker[T]):
    """Worker that wraps a function"""
    
    def __init__(
        self, 
        func: Callable[..., T], 
        *args, 
        worker_id: Optional[str] = None,
        priority: Priority = Priority.NORMAL,
        **kwargs
    ):
        super().__init__(worker_id, priority)
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
    def execute(self) -> T:
        """Run the function with arguments"""

        return self.func(*self.args, **self.kwargs)


####
##      RUNNABLE WORKER CLASS
#####
class RunnableWorker(BaseWorker[Any]):
    """Worker that wraps runnable object."""
    
    def __init__(
        self, 
        runnable: Runnable, 
        worker_id: Optional[str] = None,
        priority: Priority = Priority.NORMAL
    ):
        super().__init__(worker_id, priority)
        self.runnable = runnable
        
    def execute(self) -> Any:
        """Executes runnable object"""

        return self.runnable.run()


####
##      WORKER POOL 
#####
class WorkerPool:
    """Thread-safe worker pool with priority management"""
    
    def __init__(
        self, 
        config: WorkerPoolConfig = WorkerPoolConfig()
    ):
        self.config = config
        self._executor = ThreadPoolExecutor(max_workers = config.max_workers)
        self._pending_workers: List[BaseWorker] = []
        self._running_futures: Dict[str, Future] = {}
        self._completed_results: Dict[str, WorkerResult] = {}
        self._lock = Lock()
        self._shutdown = False
        
    def submit_worker(self, worker: BaseWorker[T]) -> str:
        """Submit a worker for execution"""

        if self._shutdown:
            raise RuntimeError("WorkerPool is shutdown")
            
        with self._lock:

            # Priority based sorted insertion
            if self.config.enable_priority:
                inserted = False

                # Insert the worker just before the first lower 
                # priority worker found in the list (worker.priority > item.prority)
                for i, pending_worker in enumerate(self._pending_workers):
                    if worker.priority.value > pending_worker.priority.value:
                        self._pending_workers.insert(i, worker)
                        inserted = True
                        break
                
                # Append it to the end else
                if not inserted:
                    self._pending_workers.append(worker)
            
            # Just append the worker to the pending list
            else:
                self._pending_workers.append(worker)
                
        self._process_pending()
        return worker.worker_id
    
    def submit_function(
        self, 
        func: Callable[..., T], 
        *args, 
        worker_id: Optional[str] = None,
        priority: Priority = Priority.NORMAL,
        **kwargs
    ) -> str:
        """Submit a function for execution"""

        worker = FunctionWorker(
            func, *args, 
            worker_id = worker_id, 
            priority = priority, 
            **kwargs
        )
        return self.submit_worker(worker)
    
    def submit_runnable(
        self, 
        runnable: Runnable, 
        worker_id: Optional[str] = None,
        priority: Priority = Priority.NORMAL
    ) -> str:
        """Submit a runnable object for execution"""

        worker = RunnableWorker(
            runnable, 
            worker_id = worker_id, 
            priority = priority
        )
        return self.submit_worker(worker)
    
    def get_result(
        self, 
        worker_id: str, 
        timeout: Optional[float] = None
    ) -> WorkerResult:
        """return a given worker result"""

        # Is worker execution already completed ???
        with self._lock:

            # Then return the result from completed reults list
            if worker_id in self._completed_results:
                return self._completed_results[worker_id]
        
        # Wait till completion
        future = self._running_futures.get(worker_id)
        if future:
            try:
                result = future.result(timeout=timeout or self.config.timeout)
                with self._lock:
                    self._completed_results[worker_id] = result
                    self._running_futures.pop(worker_id, None)
                return result
            
            except Exception as e:
                # Create error result
                error_result = WorkerResult(
                    worker_id = worker_id,
                    state = WorkerState.FAILED,
                    error = e
                )
                # And add it to completed results list
                with self._lock:
                    self._completed_results[worker_id] = error_result
                return error_result
        
        raise ValueError(f"Worker {worker_id} not found")
    
    def wait_all(
        self, 
        timeout: Optional[float] = None
    ) -> Dict[str, WorkerResult]:
        """Wait for all pending workers completion."""
        
        results = {}
        
        with self._lock:
            futures = dict(self._running_futures)
        
        # Execute workers and store results
        for worker_id, future in futures.items():
            try:
                result = future.result(timeout=timeout)
                results[worker_id] = result

            except Exception as e:
                results[worker_id] = WorkerResult(
                    worker_id = worker_id,
                    state = WorkerState.FAILED,
                    error = e
                )
        
        return results
    
    def cancel_worker(self, worker_id: str) -> bool:
        """Cancel a worker"""

        with self._lock:

            # Search in pending workers
            for worker in self._pending_workers:
                if worker.worker_id == worker_id:
                    worker.cancel()
                    self._pending_workers.remove(worker)
                    self._completed_results[worker_id] = worker._create_result()
                    return True
            
            # Search in pending futures
            future = self._running_futures.get(worker_id)
            if future:
                return future.cancel()
        
        return False
    
    def get_stats(self) -> Dict[str, int]:
        """Returns pool stats"""

        with self._lock:
            return {
                "pending": len(self._pending_workers),
                "running": len(self._running_futures),
                "completed": len(self._completed_results)
            }
    
    def _process_pending(self):
        """Process oending worers"""

        with self._lock:
            while (
                self._pending_workers and 
                len(self._running_futures) < self.config.max_workers
            ):
                worker = self._pending_workers.pop(0)
                future = self._executor.submit(worker.run)
                self._running_futures[worker.worker_id] = future
    
    def shutdown(self, wait: bool = True):
        """Shutdown the pool"""

        self._shutdown = True
        self._executor.shutdown(wait=wait)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.config.auto_shutdown:
            self.shutdown()


_global_pool = None

def get_global_pool() -> WorkerPool:
    """Get or create the global pool"""

    global _global_pool
    if _global_pool is None:
        config = WorkerPoolConfig(max_workers=6, enable_priority=True)
        _global_pool = WorkerPool(config)
    return _global_pool

def set_global_pool(pool: WorkerPool):
    """Define the global pool"""

    global _global_pool
    _global_pool = pool


####
##      BOUND WORKER METHOD PROXY
#####
class BoundWorkerMethod:
    """
    Proxy object that binds a `WorkerTaskWrapper` to an instance (self),
    allowing decorated instance methods to work seamlessly with all
    background execution capabilities.

    This enables you to use:

        instance.method()
        instance.method.async_call(...)
        instance.method.run_and_wait(...)

    without losing access to wrapper methods.

    Attributes:
        _wrapper: The original WorkerTaskWrapper
        _instance: The instance to bind as the first argument
    """

    def __init__(self, wrapper: 'WorkerTaskWrapper', instance: object):
        """
        Initialize the proxy with the wrapper and the instance.

        Args:
            wrapper: The WorkerTaskWrapper object
            instance: The object instance to bind to the call
        """
        self._wrapper = wrapper
        self._instance = instance

    def __call__(self, *args, **kwargs):
        """
        Synchronous execution with the bound instance.
        Equivalent to: wrapper(instance, *args, **kwargs)
        """
        return self._wrapper(self._instance, *args, **kwargs)

    def async_call(self, *args, **kwargs) -> str:
        """
        Asynchronous execution with the bound instance.
        Returns a worker_id.
        """
        return self._wrapper.async_call(self._instance, *args, **kwargs)

    def submit(self, *args, **kwargs) -> str:
        """
        Alias for async_call().
        """
        return self._wrapper.submit(self._instance, *args, **kwargs)

    def run_and_wait(self, *args, timeout: Optional[float] = None, **kwargs):
        """
        Executes the task in the background, then waits for and returns the result.

        Raises:
            RuntimeError: if the task is cancelled
            Exception: if the task failed with an error
        """
        return self._wrapper.run_and_wait(self._instance, *args, timeout=timeout, **kwargs)

    def set_pool(self, pool: 'WorkerPool'):
        """
        Sets a specific pool to use for this task.
        """
        self._wrapper.set_pool(pool)

    def shutdown_default_pool(self):
        """
        Shuts down the default pool used by this function, if created.
        """
        self._wrapper.shutdown_default_pool()

    def __getattr__(self, name):
        """
        Fallback to the wrapper’s attributes for completeness.
        This makes sure any missing attributes are forwarded.
        """
        return getattr(self._wrapper, name)


####
##      WRAPPER FOR WORKER TASK 
#####
class WorkerTaskWrapper:
    """
    Wrapper for @worker_task decorated functions.
    It provides more flexibilities when calling a @worker_task function.
    """
    
    def __init__(
        self, 
        func: Callable[..., T], 
        priority: Priority = Priority.NORMAL
    ):
        self.func = func
        self.priority = priority
        self._pool: Optional[WorkerPool] = None
        self._default_pool: Optional[WorkerPool] = None
        
        # Copy original function metadata
        self.__name__ = func.__name__
        self.__doc__ = func.__doc__
        self.__module__ = func.__module__
        self.__qualname__ = getattr(func, '__qualname__', func.__name__)
        self.__annotations__ = getattr(func, '__annotations__', {})
    
    def __call__(self, *args, **kwargs) -> T:
        """direct call - executes the function synchronously"""

        return self.func(*args, **kwargs)
    
    def async_call(self, *args, **kwargs) -> str:
        """Asynchronous call – returns a worker_id"""

        pool = self._get_pool()
        return pool.submit_function(
            self.func, 
            *args, 
            priority = self.priority, 
            **kwargs
        )
    
    def submit(self, *args, **kwargs) -> str:
        """Alias for async_call"""

        return self.async_call(*args, **kwargs)
    
    def run_and_wait(
        self, 
        *args, 
        timeout: Optional[float] = None, 
        **kwargs
    ) -> T:
        """Executes in parallel and waits for the result"""

        pool = self._get_pool()
        worker_id = pool.submit_function(
            self.func, *args, priority=self.priority, **kwargs
        )
        result = pool.get_result(worker_id, timeout=timeout)
        
        # Failed ???
        if result.state == WorkerState.FAILED:
            raise result.error
        
        # Or cancelled ???
        elif result.state == WorkerState.CANCELLED:
            raise RuntimeError("Task was cancelled")
        
        return result.result
    
    def set_pool(self, pool: WorkerPool):
        """Sets the pool to use"""

        self._pool = pool
    
    def _get_pool(self) -> WorkerPool:
        """Gets the pool to use"""

        # 1. Explicitly defined pool
        if self._pool is not None:
            return self._pool
        
        # 2. Global pool if exists
        global _global_pool
        if _global_pool is not None:
            return _global_pool
        
        # 3. Create a default pool for this function
        if self._default_pool is None:
            config = WorkerPoolConfig(max_workers=2, auto_shutdown=False)
            self._default_pool = WorkerPool(config)
        
        return self._default_pool
    
    def shutdown_default_pool(self):
        """Shuts down the default pool for this function"""

        if self._default_pool is not None:
            self._default_pool.shutdown()
            self._default_pool = None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        # Lie l'instance (self) à la fonction
        return BoundWorkerMethod(self, instance)


####    WORKER TASK DECORATOR
def worker_task(priority: Priority = Priority.NORMAL):
    """
    Decorator that converts a function in to a worker task
    Usage:
    ```python
    @worker_task()
    def my_function(x):
        return x * 2
    
    # Direct call (synchronous)
    result = my_function(5)  # -> 10
    
    # Asynchronous call 
    worker_id = my_function.async_call(5)
    # or
    worker_id = my_function.submit(5)
    
    # Parallel execution with waiting
    result = my_function.run_and_wait(5)
    ```
    """

    def decorator(func: Callable[[], T]) -> WorkerTaskWrapper:
        return WorkerTaskWrapper(func, priority)
    return decorator

####    PARALLEL TASK DECORATOR
def parallel_task(priority: Priority = Priority.NORMAL):
    """Decorator that forces parallel eecution
    
    Usage:
    ```python
    @parallel_task()
    def my_fonction(x):
        return x * 2
    
    # This call will always be parallel and always return a worker_id
    worker_id = ma_fonction(5)
    ```
    """

    def decorator(func: Callable[..., T]) -> Callable[..., str]:
        wrapper = WorkerTaskWrapper(func, priority)
        
        @wraps(func)
        def parallel_wrapper(*args, **kwargs) -> str:
            return wrapper.async_call(*args, **kwargs)
        
        # Add utility methods
        parallel_wrapper.set_pool = wrapper.set_pool
        parallel_wrapper.run_and_wait = wrapper.run_and_wait
        parallel_wrapper.sync_call = wrapper.__call__
        parallel_wrapper.shutdown_default_pool = wrapper.shutdown_default_pool
        
        return parallel_wrapper
    return decorator

    