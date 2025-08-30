"""
Asynchronous task management for WinUp.

Provides a simple decorator to run long-running functions on a background
thread without freezing the UI, with a callback for when the task is complete.
"""
import traceback
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from typing import Callable

class WorkerSignals(QObject):
    """Defines the signals available from a running worker thread."""
    finished = Signal(object) # Signal to emit the function's return value
    error = Signal(tuple)     # Signal to emit any exception details

class Worker(QRunnable):
    """Worker thread for executing a function."""
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            trace = traceback.format_exc()
            self.signals.error.emit((e, trace))

class TaskManager:
    """A global manager for running background tasks."""
    def __init__(self):
        self.threadpool = QThreadPool()
        # Recommended to leave one thread free for other system tasks
        max_threads = max(1, self.threadpool.maxThreadCount() - 1)
        self.threadpool.setMaxThreadCount(max_threads)
        print(f"Task manager initialized with {self.threadpool.maxThreadCount()} background threads.")

    def run(self, on_finish: Callable = None, on_error: Callable = None, on_start: Callable = None):
        """
        Decorator to run a function in the background.

        Args:
            on_finish: A function to call with the result when the task is successful.
            on_error: A function to call with the exception details if the task fails.
            on_start: A function to call just before the task begins.
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                if on_start:
                    on_start()
                
                worker = Worker(func, *args, **kwargs)
                
                if on_finish:
                    worker.signals.finished.connect(on_finish)
                if on_error:
                    worker.signals.error.connect(on_error)
                
                # Execute
                self.threadpool.start(worker)
            return wrapper
        return decorator

# Create a private singleton instance of the manager
_task_manager = TaskManager()

# Expose the 'run' method directly at the module level for the @tasks.run syntax
run = _task_manager.run 