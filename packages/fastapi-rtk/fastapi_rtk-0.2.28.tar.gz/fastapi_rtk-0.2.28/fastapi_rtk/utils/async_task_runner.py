import asyncio
import contextvars
import inspect
import typing

from .prettify_dict import prettify_dict

__all__ = ["AsyncTaskRunner"]


class CallerInfo(typing.TypedDict):
    """
    Represents information about the caller of a function.
    This is used to capture the context in which an async task was added.
    """

    filename: str
    lineno: int
    name: str


class AsyncTaskRunnerException(Exception):
    """
    Base exception for AsyncTaskRunner-related errors.
    """


class AsyncTaskException(AsyncTaskRunnerException):
    def __init__(
        self, *args, original_exception: Exception, caller: CallerInfo | None = None
    ):
        super().__init__(*args)
        self.original_exception = original_exception
        self.caller = caller


def wrap_in_async_task_exception(
    task: typing.Callable[[], typing.Coroutine | None] | typing.Coroutine,
    /,
    caller: CallerInfo | None = None,
):
    async def wrapper():
        try:
            tsk = task
            if callable(tsk):
                tsk = tsk()
            if tsk is None:
                return None
            return await tsk
        except Exception as e:
            raise AsyncTaskException(str(e), original_exception=e, caller=caller) from e

    return wrapper


class AsyncTask:
    """
    Represents a task to be run asynchronously.

    This is a callable that returns an awaitable (coroutine) or a coroutine directly.
    """

    def __init__(
        self,
        task: typing.Callable[[], typing.Coroutine | None] | typing.Coroutine,
        /,
        caller: CallerInfo | None = None,
        tags: list[str] | None = None,
    ):
        self.task = wrap_in_async_task_exception(task, caller=caller)
        self.caller = caller
        self.tags = tags or []

    def __call__(self):
        if callable(self.task):
            return self.task()
        return self.task


class AsyncTaskRunner:
    """
    A context manager for queuing and running async tasks at the end of an async with block.

    Supports nested contexts and is safe in multithreaded async environments.

    You can add either a callable that returns an awaitable (coroutine), a normal function, or a coroutine directly. But a callable is preferred
    to avoid warning about "coroutine was never awaited" in case the task fails to run.

    Example:

    Some async function that you want to run at the end of the context:
    ```python
    async def some_async_function():
        # Some asynchronous operation
        await asyncio.sleep(1)
        print("Task completed")
    ```

    Using the AsyncTaskRunner class:
    ```python
    from fastapi_rtk import AsyncTaskRunner

    # Using the AsyncTaskRunner class directly
    async with AsyncTaskRunner():
        AsyncTaskRunner.add_task(lambda: some_async_function())
        # The task will be executed when exiting the context
    ```

    Using the AsyncTaskRunner class with a variable:
    ```python
    from fastapi_rtk import AsyncTaskRunner

    # Using the AsyncTaskRunner class with a variable
    async with AsyncTaskRunner() as runner:
        runner.add_task(lambda: some_async_function())
        # The task will be executed when exiting the context

    # Using the AsyncTaskRunner class with a variable and nested context
    async with AsyncTaskRunner() as runner:
        runner.add_task(lambda: some_async_function())
        async with AsyncTaskRunner() as nested_runner:
            nested_runner.add_task(lambda: some_async_function())
            # The task will be executed when exiting the nested context
    # The task will be executed when exiting the outer context
    ```
    """

    # Each context will get a stack of task lists to support nesting
    _task_stack: contextvars.ContextVar[typing.Optional[list[list[AsyncTask]]]] = (
        contextvars.ContextVar("_task_stack", default=None)
    )

    def __init__(self, run_tasks_even_if_exception=False):
        """
        Initializes the AsyncTaskRunner.

        Args:
            run_tasks_even_if_exception (bool, optional): Whether to run tasks even if an exception occurs in the context. Defaults to False.
        """
        self.run_tasks_even_if_exception = run_tasks_even_if_exception

    @staticmethod
    def add_task(
        *tasks: typing.Callable[[], typing.Coroutine | None] | typing.Coroutine,
        tags: list[str] | None = None,
    ):
        stack = AsyncTaskRunner._task_stack.get()
        if not stack:
            raise RuntimeError(
                "AsyncTaskRunner.add_task() called outside of context. "
                "Use `async with AsyncTaskRunner():` before calling this."
            )

        # Get caller info
        frame = inspect.currentframe()
        caller = inspect.getouterframes(frame, 2)[1] if frame else None

        async_tasks = [
            AsyncTask(
                task,
                caller=CallerInfo(
                    filename=caller.filename if caller else "<unknown>",
                    lineno=caller.lineno if caller else 0,
                    name=task.__name__ if callable(task) else "<coroutine>",
                ),
                tags=tags,
            )
            if not isinstance(task, AsyncTask)
            else task
            for task in tasks
        ]
        stack[-1].extend(async_tasks)  # Add to the top context

    @staticmethod
    def remove_tasks_by_tag(tag: str):
        """
        Removes tasks with the specified tag from the current context's task list.

        Args:
            tag (str): The tag to filter tasks by.
        """
        stack = AsyncTaskRunner._task_stack.get()
        if not stack or not stack[-1]:
            return

        # Filter tasks in the current context's task list
        stack[-1] = [task for task in stack[-1] if tag not in task.tags]

    async def __aenter__(self):
        stack = self._task_stack.get()
        if stack is None:
            stack = []
            self._token = self._task_stack.set(stack)
        else:
            self._token = None  # Only reset when we set a new stack

        stack.append([])  # Push a new task list for this context
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        stack = self._task_stack.get()
        if not stack:
            raise RuntimeError("Task stack corrupted or not initialized.")

        tasks = stack.pop()  # Pop the current context's task list

        if self._token:
            self._task_stack.reset(self._token)

        if exc_type and not self.run_tasks_even_if_exception:
            return

        if tasks:
            exceptions: list[AsyncTaskException] = []
            futures = await asyncio.gather(
                *(task() for task in tasks), return_exceptions=True
            )
            for future in futures:
                if isinstance(future, AsyncTaskException):
                    # Handle exceptions from tasks
                    exceptions.append(future)

            if exceptions:
                raise AsyncTaskRunnerException(
                    f"\n{
                        prettify_dict(
                            {
                                'message': 'One or more tasks failed.',
                                'exceptions': {
                                    f'Task {index + 1}': {
                                        'message': str(exc),
                                        'caller': exc.caller,
                                        'traceback': exc.original_exception.__traceback__,
                                    }
                                    for index, exc in enumerate(exceptions)
                                },
                            }
                        )
                    }"
                )
