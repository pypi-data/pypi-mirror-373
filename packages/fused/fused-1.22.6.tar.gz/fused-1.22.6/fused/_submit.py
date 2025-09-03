import asyncio
import concurrent.futures
import json
import time
import warnings
from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime, timedelta
from math import floor
from types import FunctionType
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
    overload,
)

from requests.exceptions import ReadTimeout

from fused._optional_deps import HAS_PANDAS, PD_DATAFRAME
from fused._options import options as OPTIONS
from fused._run import ResultType
from fused._run import run as fused_run
from fused._run import run_async as fused_run_async
from fused._udf import udf as fused_udf
from fused._udf.decorators import _parse_ttl
from fused.core._cache import DEFAULT_CACHE_MAX_AGE
from fused.core._cache import cache as fused_cache
from fused.models.udf import Udf
from fused.models.udf.base_udf import BaseUdf
from fused.models.udf.udf import AnyBaseUdf
from fused.types import UdfRuntimeError, UdfSerializationError, UdfTimeoutError
from fused.warnings import (
    FusedDeprecationWarning,
)

if TYPE_CHECKING:
    import pandas as pd

# Check for nest_asyncio availability
# Required for environments with an existing event loop, like jupyter notebooks
# Otherwise calling a sync function that creating async tasks within this environment will deadlock processing these
# tasks since the event loop is blocked by that sync function.
try:
    import nest_asyncio

    HAS_NEST_ASYNCIO = True
except ImportError:
    HAS_NEST_ASYNCIO = False

Status = Literal["cancelled", "running", "timeout", "error", "success", "pending"]
STATUS_NOT_FINISHED = ("running", "pending")
STATUS_FAILED = ("error", "timeout")
ExecutionType = Literal["thread_pool", "async_loop"]


def _coerce_hashable(df: "pd.DataFrame"):
    """Make the values in the DataFrame hashable.
    E.g. Python `list` cannot be hashed."""

    for index in df.index:
        for column in df.columns:
            existing_value = df.loc[index, column]

            if isinstance(existing_value, list):
                # list we know a way to make it a hashable type
                existing_value = tuple(existing_value)

            try:
                # Some other types like `dict` we don't have a strategy
                # for, so instead try coercing to json.
                hash(existing_value)
            except TypeError:
                existing_value = json.dumps(existing_value)

            df.at[index, column] = existing_value

    return df


class BaseFuture(ABC):
    """Base class for Future implementations"""

    def __init__(self, index, args):
        self._index = index
        self._args = args
        self._started_at: Optional[datetime] = None
        self._ended_at: Optional[datetime] = None

    def time(self) -> Optional[timedelta]:
        """How long this future took to complete, or None
        if the future is not complete."""
        if self._started_at is None or self._ended_at is None:
            return None
        return self._ended_at - self._started_at

    @abstractmethod
    def done(self) -> bool:
        pass

    @abstractmethod
    def result(self):
        pass

    @abstractmethod
    def exception(self) -> Optional[Exception]:
        pass

    @abstractmethod
    def logs(self) -> str:
        pass

    @abstractmethod
    def status(self) -> Status:
        pass

    def __repr__(self) -> str:
        return f"<fused.Future [status: {('done - ' if self.done() else '') + self.status()}]>"


class Future(BaseFuture):
    """Thread-based Future implementation"""

    def __init__(self, future, index, args):
        super().__init__(index, args)
        self._future: concurrent.futures.Future = future

    def done(self) -> bool:
        return self._future.done()

    def result(self):
        response = self._future.result()
        if isinstance(response, Exception):
            raise response
        if hasattr(response, "error_message") and response.error_message is not None:
            exc = self.exception()
            if exc is not None:
                raise exc
        return response.data

    def exception(self) -> Optional[Exception]:
        try:
            response = self._future.result()
        except concurrent.futures.CancelledError as e:
            return e

        if isinstance(response, Exception):
            return response
        if hasattr(response, "error_message") and response.error_message is not None:
            if response.error_type == "timeout_error":
                return UdfTimeoutError(response.error_message)
            elif response.error_type == "serialization_error":
                return UdfSerializationError(response.error_message)
            return UdfRuntimeError(
                f"[Run #{self._index} {self._args}] {response.error_message}",
                child_exception_class=getattr(response, "exception_class", None),
            )
        future_exc = self._future.exception()
        return future_exc if isinstance(future_exc, Exception) else None

    def logs(self) -> str:
        response = self._future.result()
        if isinstance(response, Exception):
            return str(response)
        out = ""
        if response.stdout:
            out += "stdout\n------\n" + response.stdout
        if response.stderr:
            out += "\nstderr\n------\n" + response.stderr
        return out

    def status(self) -> Status:
        if self._future.cancelled():
            return "cancelled"
        elif self._future.running():
            return "running"
        elif self._future.done():
            exc = self.exception()
            if exc:
                if isinstance(
                    exc, (ReadTimeout, UdfTimeoutError)
                ) or "504 Server Error: Gateway Timeout" in str(exc):
                    return "timeout"
                if isinstance(exc, concurrent.futures.CancelledError):
                    return "cancelled"
                return "error"
            return "success"  # or "finished"?
        else:
            return "pending"


class AsyncFuture(BaseFuture):
    """Async-based Future implementation"""

    def __init__(self, task, index, args):
        super().__init__(index, args)
        self._task: asyncio.Task = task

    def done(self) -> bool:
        return self._task.done()

    def result(self):
        if not self._task.done():
            raise RuntimeError("Task is not done yet")

        response = self._task.result()
        if isinstance(response, Exception):
            raise response

        if hasattr(response, "error_message") and response.error_message is not None:
            exc = self.exception()
            if exc is not None:
                raise exc
        return response.data

    def exception(self) -> Optional[Exception]:
        if not self._task.done():
            return None

        try:
            response = self._task.result()
        except asyncio.CancelledError as e:
            return e

        if isinstance(response, Exception):
            return response
        if hasattr(response, "error_message") and response.error_message is not None:
            return UdfRuntimeError(
                f"[Run #{self._index} {self._args}] {response.error_message}",
                child_exception_class=getattr(response, "exception_class", None),
            )
        task_exc = self._task.exception()
        return task_exc if isinstance(task_exc, Exception) else None

    def logs(self) -> str:
        if not self._task.done():
            return ""

        response = self._task.result()
        if isinstance(response, Exception):
            return str(response)

        out = ""
        if response.stdout:
            out += "stdout\n------\n" + response.stdout
        if response.stderr:
            out += "\nstderr\n------\n" + response.stderr
        return out

    def status(self) -> Status:
        if self._task.cancelled():
            return "cancelled"
        elif not self._task.done():
            return "running"  # asyncio doesn't distinguish between running and pending
        else:
            if exc := self.exception():
                timeout_msg = "504 Server Error: Gateway Timeout"
                if isinstance(exc, ReadTimeout) or timeout_msg in str(exc):
                    return "timeout"
                # Should be handled already but keeping for consistency with sync version
                if isinstance(exc, asyncio.CancelledError):
                    return "cancelled"
                return "error"
            return "success"


class BaseJobPool(ABC):
    """Base class for JobPool implementations"""

    def __init__(
        self,
        udf,
        arg_list,
        kwargs=None,
        engine="remote",
        max_retry=2,
        before_run=None,
        wait_sleep=0.01,
        before_submit=0.01,
    ):
        self.udf = udf
        self.arg_list = arg_list
        self.n_jobs = len(self.arg_list)
        self._kwargs = kwargs or {}
        self._engine = engine
        self._max_retry = max_retry
        self._before_run = before_run
        self._wait_sleep = wait_sleep
        self._before_submit = before_submit
        self._restarted_at = None
        self._started_at = None
        self._cancel_retry = False
        self._futures: List[BaseFuture] = []

    @abstractmethod
    def _create_future(self, index, args) -> BaseFuture:
        pass

    @abstractmethod
    def _start_jobs(self):
        pass

    @abstractmethod
    def cancel(self, wait: bool = False):
        pass

    def _get_status(self) -> List[bool]:
        return [f.done() for f in self._futures]

    def _status_counts(self) -> Dict[Status, int]:
        counts = defaultdict(int)
        for f in self._futures:
            counts[f.status()] += 1

        # TODO: always sort counts keys by status order
        return counts

    def _status_message(self) -> str:
        counts = self._status_counts()

        message_parts = []
        for status in ("running", "timeout", "error", "success", "pending"):
            c = counts[status]
            if c:
                message_parts.append(f"{c} {status}")

        if len(message_parts) == 0:
            return "empty"

        return ", ".join(message_parts)

    def _get_progress(self) -> Tuple[int, str]:
        # floor as to not show 100 if not every one is actually done
        percentage = floor(sum(self._get_status()) / self.n_jobs * 100)
        return percentage, f"{sum(self._get_status())}/{self.n_jobs}"

    def retry(self):
        """Rerun any tasks in error or timeout states. Tasks are rerun in the same pool."""
        old_futures = self._futures

        def _create_new_future(index, args):
            if old_futures[index].status() in ("error", "timeout"):
                return self._create_future(index, args)
            return old_futures[index]

        self._restarted_at = datetime.now()
        self._futures = [
            _create_new_future(index, args) for index, args in enumerate(self.arg_list)
        ]

    def total_time(self, since_retry: bool = False) -> timedelta:
        """Returns how long the entire job took.

        If only partial results are available, returns based on the last task to have been completed.
        """
        started_at = (
            self._restarted_at
            if since_retry and self._restarted_at is not None
            else self._started_at
        )
        if started_at is None:
            raise ValueError("JobPool has not been started")
        all_result_at = [f._ended_at for f in self._futures if f._ended_at is not None]
        if not len(all_result_at):
            raise ValueError("No result is available yet")
        last_result_at = max(all_result_at)
        return last_result_at - self._started_at

    def times(self) -> list[Optional[timedelta]]:
        """Time taken for each task.

        Incomplete tasks will be reported as None."""
        return [f.time() for f in self._futures]

    def done(self) -> bool:
        """True if all tasks have finished, regardless of success or failure."""
        return all(fut.done() for fut in self._futures)

    def all_succeeded(self) -> bool:
        """True if all tasks finished with success"""
        return all(f.status() == "success" for f in self._futures)

    def any_failed(self) -> bool:
        """True if any task finished with an error"""
        return any(f.status() in ("error", "timeout") for f in self._futures)

    def any_succeeded(self) -> bool:
        """True if any task finished with success"""
        return any(f.status() == "success" for f in self._futures)

    def arg_df(self):
        """The arguments passed to runs as a DataFrame"""
        if not HAS_PANDAS:
            raise ImportError("pandas is required to use this method")

        import pandas as pd

        return pd.DataFrame(self.arg_list)

    def status(self):
        """Return a Series indexed by status of task counts"""
        return self.df().value_counts("status")

    def wait(self):
        """Wait until all jobs are finished

        Use fused.options.show.enable_tqdm to enable/disable tqdm.
        Use pool._wait_sleep to set if sleep should occur while waiting.
        """

        def _noop(*args, **kwargs):
            pass

        after = _noop
        update = _noop
        if OPTIONS.show.enable_tqdm:
            from tqdm.auto import tqdm

            t = tqdm(total=self.n_jobs, bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt}")

            def _tqdm_after():
                t.update(self.n_jobs - t.n)
                t.close()

            after = _tqdm_after
            update = lambda n_done: t.update(n_done - t.n)

        while not self.done():
            n_done = sum(self._get_status())
            update(n_done)
            if self._wait_sleep is not None:
                time.sleep(self._wait_sleep)

        after()

    def tail(self, stop_on_exception=False):
        """Wait until all jobs are finished, printing statuses as they become available.

        This is useful for interactively watching for the state of the pool.

        Use pool._wait_sleep to set if sleep should occur while waiting.
        """
        seen = set(self.results_now(return_exceptions=not stop_on_exception).keys())
        if len(seen):
            print(self._status_message())

            if len(seen) == len(self._futures):
                # Nothing left to tail
                return

        while len(seen) != len(self._futures):
            done = self.results_now(return_exceptions=not stop_on_exception)
            for new_key in done.keys():
                if new_key not in seen:
                    seen.add(new_key)
                    # TODO: Logger support, rather than print statement?
                    print(
                        f"[{datetime.now()}] Run #{new_key} {self._futures[new_key]._args} {self._futures[new_key].status()} ({self._status_message()})"
                    )

            if self._wait_sleep is not None:
                time.sleep(self._wait_sleep)

        print(f"End of tail\n{self._status_message()}")

    def results(self, return_exceptions=False) -> List[Any]:
        """Retrieve all results of the job.

        Results are ordered by the order of the args list."""
        results = []
        for fut in self._futures:
            try:
                results.append(fut.result())
            except Exception:
                if return_exceptions:
                    results.append(fut.exception())
                else:
                    raise
        return results

    def results_now(self, return_exceptions=False) -> Dict[int, Any]:
        """Retrieve the results that are currently done.

        Results are indexed by position in the args list."""
        results = {}
        for index, fut in enumerate(self._futures):
            if fut.done():
                try:
                    results[index] = fut.result()
                except Exception:
                    if return_exceptions:
                        results[index] = fut.exception()
                    else:
                        raise
        return results

    def df(
        self,
        status_column: Optional[str] = "status",
        result_column: Optional[str] = "result",
        time_column: Optional[str] = "time",
        logs_column: Optional[str] = "logs",
        exception_column: Optional[str] = None,
        include_exceptions: bool = True,
    ):
        """
        Get a DataFrame of results as they are currently.
        The DataFrame will have columns for each argument passed, and columns for:
        `status`, `result`, `time`, `logs` and optionally `exception`.
        """
        if not HAS_PANDAS:
            raise ImportError("pandas is required to use this method")

        import pandas as pd

        results_df = pd.DataFrame(self.arg_list)
        status_list = [f.status() for f in self._futures]
        if status_column:
            results_df[status_column] = status_list

        if time_column:
            time_list = [None] * len(self._futures)
            for i, fut in enumerate(self._futures):
                t = fut.time()
                if t is not None:
                    time_list[i] = t.total_seconds()

            results_df[time_column] = pd.Series(time_list, dtype=float)

        if result_column:
            result_list = [None] * len(self._futures)
            for i, fut in enumerate(self._futures):
                if status_list[i] not in STATUS_NOT_FINISHED:
                    try:
                        res = fut.result()
                    except Exception:
                        res = fut.exception() if include_exceptions else None

                    result_list[i] = res

            results_df[result_column] = result_list

        if logs_column:
            logs_list = [None] * len(self._futures)
            for i, fut in enumerate(self._futures):
                if status_list[i] not in STATUS_NOT_FINISHED:
                    logs_list[i] = fut.logs()

            results_df[logs_column] = logs_list

        if exception_column:
            results_df[exception_column] = [fut.exception() for fut in self._futures]

        return results_df

    def get_status_df(self):
        warnings.warn(
            "the 'get_status_df()' method is deprecated, use '.df()' instead.",
            FusedDeprecationWarning,
        )
        return self.df()

    def get_results_df(self, ignore_exceptions=False):
        warnings.warn(
            "the 'get_results_df()' method is deprecated, use '.df()' instead.",
            FusedDeprecationWarning,
        )
        self.wait()
        return self.df(include_exceptions=not ignore_exceptions)

    def errors(self) -> Dict[int, Exception]:
        """Retrieve the results that are currently done and are errors.

        Results are indexed by position in the args list."""
        errors = {}
        for index, fut in enumerate(self._futures):
            if fut.status() in STATUS_FAILED:
                errors[index] = fut.exception()
        return errors

    def first_error(self) -> Optional[Exception]:
        """Retrieve the first (by order of arguments) error result, or None."""
        for fut in self._futures:
            if fut.status() in STATUS_FAILED:
                return fut.exception()

        return None

    def logs(self) -> list[Optional[str]]:
        """Logs for each task.

        Incomplete tasks will be reported as None."""
        return [
            (f.logs() if f.status() not in STATUS_NOT_FINISHED else None)
            for f in self._futures
        ]

    def first_log(self) -> Optional[str]:
        """Retrieve the first (by order of arguments) logs, or None."""
        for f in self._futures:
            if f.status() not in STATUS_NOT_FINISHED:
                return f.logs()

    def success(self) -> Dict[int, Any]:
        """Retrieve the results that are currently done and are successful.

        Results are indexed by position in the args list."""
        success = {}
        for index, fut in enumerate(self._futures):
            if fut.status() in ("success",):
                success[index] = fut.result()
        return success

    def pending(self) -> Dict[int, Any]:
        """Retrieve the arguments that are currently pending and not yet submitted."""
        pending = {}
        for index, fut in enumerate(self._futures):
            if fut.status() in ("pending",):
                pending[index] = fut._args
        return pending

    def running(self) -> Dict[int, Any]:
        """Retrieve the results that are currently running."""
        running = {}
        for index, fut in enumerate(self._futures):
            if fut.status() in ("running",):
                running[index] = fut._args
        return running

    def cancelled(self) -> Dict[int, Any]:
        """Retrieve the arguments that were cancelled and not run."""
        cancelled = {}
        for index, fut in enumerate(self._futures):
            if fut.status() in ("cancelled",):
                cancelled[index] = fut._args
        return cancelled

    def collect(self, ignore_exceptions=False, flatten=True):
        """Collect all results into a DataFrame"""
        if not HAS_PANDAS:
            raise ImportError("pandas is required to use this method")

        import pandas as pd

        # Handles both thread and async
        self.wait()
        results = self.results(return_exceptions=ignore_exceptions)
        mask = [not isinstance(r, Exception) for r in results]
        results = dict(
            res
            for res in zip(range(self.n_jobs), results)
            if not isinstance(res[1], Exception)
        )

        results_pandas = all(isinstance(res, pd.DataFrame) for res in results.values())
        if results_pandas and len(results) and flatten:
            # TODO: flatten can un-occur depending on results, this seems wrong
            results_df = pd.concat(results)
        else:
            results_df = pd.DataFrame({"result": pd.Series(results)})
            results_df.index = pd.MultiIndex.from_product([results_df.index])

        args_df = pd.DataFrame(self.arg_list)
        args_df = args_df[mask]

        _coerce_hashable(args_df)

        # combine concatenated results with arguments as prepended index levels
        assert len(results_df.index.levels[0]) == len(args_df)
        args_index = pd.MultiIndex.from_frame(args_df)
        args_codes = [c.take(results_df.index.codes[0]) for c in args_index.codes]
        new_idx = pd.MultiIndex(
            levels=list(args_index.levels) + results_df.index.levels[1:],
            codes=args_codes + results_df.index.codes[1:],
            names=list(args_df.columns) + results_df.index.names[1:],
        )
        if new_idx.nlevels == 1:
            new_idx = new_idx.get_level_values(0)
        results_df.index = new_idx
        return results_df

    def __getitem__(self, idx: int) -> BaseFuture:
        return self._futures[idx]

    def __len__(self) -> int:
        return self.n_jobs

    def __repr__(self) -> str:
        return f"<JobPool with {self.n_jobs} jobs [{self._status_message()}]>"

    def _repr_html_(self) -> str:
        # TODO we could provide a more informative repr in notebooks (e.g. showing
        # a table of the individual jobs and their status?)
        counts = self._status_counts()
        status_table_data = [
            f"<tr><td>{status}</td><td>{count}</td></tr>"
            for status, count in counts.items()
        ]
        return f"<table><tr><th>Status</th><th>Count</th></tr>{''.join(status_table_data)}</table>"


class JobPool(BaseJobPool):
    """Thread-based JobPool implementation using ThreadPoolExecutor"""

    def __init__(
        self,
        udf,
        arg_list,
        kwargs=None,
        engine="remote",
        max_workers=None,
        max_retry=2,
        before_run=None,
        wait_sleep=0.01,
        before_submit=0.01,
    ):
        super().__init__(
            udf,
            arg_list,
            kwargs,
            engine,
            max_retry,
            before_run,
            wait_sleep,
            before_submit,
        )
        self._pool = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

    def _create_future(self, index, args) -> Future:
        future = Future(None, index, args)

        def _run(args):
            # currently we have to add a small delay between starting the UDF runs
            # to avoid overloading the server
            if self._before_run is not None:
                time.sleep(self._before_run)

            try:
                future._started_at = datetime.now()

                return fused_run(
                    self.udf,
                    engine=self._engine,
                    _return_response=True,
                    max_retry=self._max_retry,
                    _cancel_callback=lambda: self._cancel_retry,
                    **args,
                    **self._kwargs,
                )
            except Exception as exc:
                # ReadTime or HTTPError can happen on time-out or other server error
                return exc
            finally:
                future._ended_at = datetime.now()

        if self._before_submit:
            time.sleep(self._before_submit)

        future._future = self._pool.submit(_run, args)

        return future

    def _start_jobs(self):
        self._started_at = datetime.now()
        self._futures = [
            self._create_future(index, args) for index, args in enumerate(self.arg_list)
        ]

    def cancel(self, wait: bool = False):
        """Cancel any pending (not running) tasks.

        Note it will not be possible to retry on the same JobPool later."""
        # Signal running tasks to stop retrying
        self._cancel_retry = True

        self._pool.shutdown(wait=wait, cancel_futures=True)
        counts = self._status_counts()

        if not wait:
            message = f"{counts['cancelled']} task(s) cancelled successfully"
            if counts["running"]:
                message += f", {counts['running']} task(s) already in progress and can not be cancelled."
            print(message)


class AsyncJobPool(BaseJobPool):
    """Async-based JobPool implementation using asyncio"""

    def __init__(
        self,
        udf,
        arg_list,
        kwargs=None,
        engine="remote",
        max_workers=None,
        max_retry=2,
        before_run=None,
        wait_sleep=0.01,
        before_submit=0.01,
    ):
        super().__init__(
            udf,
            arg_list,
            kwargs,
            engine,
            max_retry,
            before_run,
            wait_sleep,
            before_submit,
        )
        self._semaphore = asyncio.Semaphore(max_workers)

    def __repr__(self) -> str:
        return f"<AsyncJobPool with {self.n_jobs} jobs [{self._status_message()}]>"

    def check_loop(self):
        try:
            _ = asyncio.get_running_loop()
            if not HAS_NEST_ASYNCIO:
                raise ImportError(
                    "nest_asyncio is required to use AsyncJobPool in environments with an existing event loop "
                    "(like Jupyter notebooks). Install it with: pip install nest_asyncio"
                )
        except RuntimeError:
            # No event loop running, which is fine
            pass

    async def _create_future(self, index, args) -> AsyncFuture:
        future = AsyncFuture(None, index, args)

        async def _run(args):
            async with self._semaphore:
                # currently we have to add a small delay between starting the UDF runs
                # to avoid overloading the server
                if self._before_run is not None:
                    await asyncio.sleep(self._before_run)

                try:
                    future._started_at = datetime.now()

                    result = await fused_run_async(
                        self.udf,
                        engine=self._engine,
                        _return_response=True,
                        max_retry=self._max_retry,
                        _cancel_callback=lambda: self._cancel_retry,
                        **args,
                        **self._kwargs,
                    )
                    return result
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    return e
                finally:
                    future._ended_at = datetime.now()

        if self._before_submit:
            await asyncio.sleep(self._before_submit)

        future._task = asyncio.create_task(_run(args))

        return future

    async def _start_jobs(self):
        self._started_at = datetime.now()
        self._futures = []

        for index, args in enumerate(self.arg_list):
            future = await self._create_future(index, args)
            self._futures.append(future)

    def cancel(self, wait: bool = False):
        """Cancel any pending (not running) tasks."""
        self.check_loop()

        return asyncio.run(self.cancel_async(wait))

    async def cancel_async(self, wait: bool = False):
        self._cancel_retry = True

        for future in self._futures:
            if not future._task.done():
                future._task.cancel()

        counts = self._status_counts()

        if not wait:
            message = f"{counts['cancelled']} task(s) cancelled successfully"
            if counts["running"]:
                message += f", {counts['running']} task(s) already in progress and can not be cancelled."
            print(message)
        else:
            await asyncio.gather(
                *(f._task for f in self._futures), return_exceptions=True
            )

    async def _wait_with_progress_async(self, update_progress):
        """Async wait with incremental progress updates"""
        if not self._futures:
            return

        while not self.done():
            n_done = sum(1 for f in self._futures if f.done())
            update_progress(n_done)

            if self._wait_sleep is not None:
                await asyncio.sleep(self._wait_sleep)
            else:
                # Small sleep to prevent busy waiting
                await asyncio.sleep(0.01)

    async def results_now_async(self, return_exceptions=False) -> Dict[int, Any]:
        """Async version of results_now that doesn't block the event loop"""
        results = {}
        for index, fut in enumerate(self._futures):
            if fut.done():
                try:
                    results[index] = fut.result()
                except Exception:
                    if return_exceptions:
                        results[index] = fut.exception()
                    else:
                        raise
        return results

    async def results_async(self, return_exceptions=False) -> List[Any]:
        """Async version of results that assumes waiting has already been done"""
        results = []
        for fut in self._futures:
            try:
                results.append(fut.result())
            except Exception:
                if return_exceptions:
                    results.append(fut.exception())
                else:
                    raise
        return results

    async def tail_async(self, stop_on_exception=False):
        """Async version of tail that doesn't block the event loop"""
        seen = set(
            (
                await self.results_now_async(return_exceptions=not stop_on_exception)
            ).keys()
        )
        if len(seen):
            print(self._status_message())

            if len(seen) == len(self._futures):
                # Nothing left to tail
                return

        while len(seen) != len(self._futures):
            done = await self.results_now_async(return_exceptions=not stop_on_exception)
            for new_key in done.keys():
                if new_key not in seen:
                    seen.add(new_key)
                    print(
                        f"[{datetime.now()}] Run #{new_key} {self._futures[new_key]._args} {self._futures[new_key].status()} ({self._status_message()})"
                    )

            if self._wait_sleep is not None:
                await asyncio.sleep(self._wait_sleep)

        print(f"End of tail\n{self._status_message()}")

    def tail(self, stop_on_exception=False):
        """Override tail to handle async context properly"""
        self.check_loop()

        # Either a new loop is created or we are able to nest
        return asyncio.run(self.tail_async(stop_on_exception))

    def results_now(self, return_exceptions=False) -> Dict[int, Any]:
        """Override results_now to handle async context properly"""
        self.check_loop()

        # Either a new loop is created or we are able to nest
        return asyncio.run(self.results_now_async(return_exceptions))

    def results(self, return_exceptions=False) -> List[Any]:
        """Override results to handle async context properly"""
        self.check_loop()

        # Either a new loop is created or we are able to nest
        return asyncio.run(self.results_async(return_exceptions))

    async def df_async(
        self,
        status_column: Optional[str] = "status",
        result_column: Optional[str] = "result",
        time_column: Optional[str] = "time",
        logs_column: Optional[str] = "logs",
        exception_column: Optional[str] = None,
        include_exceptions: bool = True,
    ):
        """Async version of df() that doesn't block the event loop"""
        if not HAS_PANDAS:
            raise ImportError("pandas is required to use this method")

        import pandas as pd

        results_df = pd.DataFrame(self.arg_list)
        status_list = [f.status() for f in self._futures]
        if status_column:
            results_df[status_column] = status_list

        if time_column:
            time_list = [None] * len(self._futures)
            for i, fut in enumerate(self._futures):
                t = fut.time()
                if t is not None:
                    time_list[i] = t.total_seconds()

            results_df[time_column] = pd.Series(time_list, dtype=float)

        if result_column:
            result_list = [None] * len(self._futures)
            for i, fut in enumerate(self._futures):
                if status_list[i] not in STATUS_NOT_FINISHED:
                    try:
                        res = fut.result()
                    except Exception:
                        res = fut.exception() if include_exceptions else None

                    result_list[i] = res

            results_df[result_column] = result_list

        if logs_column:
            logs_list = [None] * len(self._futures)
            for i, fut in enumerate(self._futures):
                if status_list[i] not in STATUS_NOT_FINISHED:
                    logs_list[i] = fut.logs()

            results_df[logs_column] = logs_list

        if exception_column:
            results_df[exception_column] = [fut.exception() for fut in self._futures]

        return results_df

    def df(
        self,
        status_column: Optional[str] = "status",
        result_column: Optional[str] = "result",
        time_column: Optional[str] = "time",
        logs_column: Optional[str] = "logs",
        exception_column: Optional[str] = None,
        include_exceptions: bool = True,
    ):
        """Override df to handle async context properly"""
        self.check_loop()

        # Either a new loop is created or we are able to nest
        return asyncio.run(
            self.df_async(
                status_column,
                result_column,
                time_column,
                logs_column,
                exception_column,
                include_exceptions,
            )
        )

    async def success_async(self) -> Dict[int, Any]:
        """Async version of success that doesn't block the event loop"""
        success = {}
        for index, fut in enumerate(self._futures):
            if fut.status() in ("success",):
                success[index] = fut.result()
        return success

    def success(self) -> Dict[int, Any]:
        """Override success to handle async context properly"""
        self.check_loop()

        # Either a new loop is created or we are able to nest
        return asyncio.run(self.success_async())

    async def errors_async(self) -> Dict[int, Exception]:
        """Async version of errors that doesn't block the event loop"""
        errors = {}
        for index, fut in enumerate(self._futures):
            if fut.status() in STATUS_FAILED:
                errors[index] = fut.exception()
        return errors

    def errors(self) -> Dict[int, Exception]:
        """Override errors to handle async context properly"""
        self.check_loop()

        # Either a new loop is created or we are able to nest
        return asyncio.run(self.errors_async())

    async def first_error_async(self) -> Optional[Exception]:
        """Async version of first_error that doesn't block the event loop"""
        for fut in self._futures:
            if fut.status() in STATUS_FAILED:
                return fut.exception()
        return None

    def first_error(self) -> Optional[Exception]:
        """Override first_error to handle async context properly"""
        self.check_loop()

        # Either a new loop is created or we are able to nest
        return asyncio.run(self.first_error_async())

    async def logs_async(self) -> list[Optional[str]]:
        """Async version of logs that doesn't block the event loop"""
        return [
            (f.logs() if f.status() not in STATUS_NOT_FINISHED else None)
            for f in self._futures
        ]

    def logs(self) -> list[Optional[str]]:
        """Override logs to handle async context properly"""
        self.check_loop()

        # Either a new loop is created or we are able to nest
        return asyncio.run(self.logs_async())

    async def first_log_async(self) -> Optional[str]:
        """Async version of first_log that doesn't block the event loop"""
        for f in self._futures:
            if f.status() not in STATUS_NOT_FINISHED:
                return f.logs()
        return None

    def first_log(self) -> Optional[str]:
        """Override first_log to handle async context properly"""
        self.check_loop()

        # Either a new loop is created or we are able to nest
        return asyncio.run(self.first_log_async())

    def status(self):
        """Override status to handle async context properly"""
        self.check_loop()

        # Either a new loop is created or we are able to nest
        return asyncio.run(self.df_async()).value_counts("status")

    def wait(self):
        """Wait until all jobs are finished (sync wrapper around wait_async)"""
        if not self._futures:
            return

        self.check_loop()

        # Set up progress tracking (same as BaseJobPool.wait)
        def _noop(*args, **kwargs):
            pass

        after = _noop
        update = _noop
        if OPTIONS.show.enable_tqdm:
            from tqdm.auto import tqdm

            t = tqdm(total=self.n_jobs, bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt}")

            def _tqdm_after():
                t.update(self.n_jobs - t.n)
                t.close()

            after = _tqdm_after
            update = lambda n_done: t.update(n_done - t.n)

        # Run async wait with progress updates
        asyncio.run(self._wait_with_progress_async(update))
        after()

    async def wait_async(self):
        if not self._futures:
            return

        self.check_loop()

        # Set up progress tracking (same as BaseJobPool.wait)
        def _noop(*args, **kwargs):
            pass

        after = _noop
        update = _noop
        if OPTIONS.show.enable_tqdm:
            from tqdm.auto import tqdm

            t = tqdm(total=self.n_jobs, bar_format="{l_bar}{bar} | {n_fmt}/{total_fmt}")

            def _tqdm_after():
                t.update(self.n_jobs - t.n)
                t.close()

            after = _tqdm_after
            update = lambda n_done: t.update(n_done - t.n)

        await self._wait_with_progress_async(update)
        after()

    async def _retry_async(self):
        old_futures = self._futures

        async def _create_new_future(index, args):
            if old_futures[index].status() in ("error", "timeout"):
                return await self._create_future(index, args)
            return old_futures[index]

        self._restarted_at = datetime.now()
        self._futures = []
        for index, args in enumerate(self.arg_list):
            future = await _create_new_future(index, args)
            self._futures.append(future)

    def retry(self):
        self.check_loop()

        # Either a new loop is created or we are able to nest
        asyncio.run(self._retry_async())


def _validate_arg_list(arg_list, udf):
    if not len(arg_list):
        raise ValueError("arg_list must be a non-empty")

    if HAS_PANDAS and isinstance(arg_list, PD_DATAFRAME):
        return arg_list.to_dict(orient="records")

    if not isinstance(arg_list[0], dict):
        if not isinstance(udf, Udf):
            raise ValueError(
                "arg_list must be a list of dictionaries. A simple list to pass "
                "as first positional argument is only supported for UDF objects."
            )
        if udf._parameter_list is None:
            # TODO: Run _parameter_list detection here
            raise NotImplementedError(
                "arg_list must be a list of dictionaries. Could not detect the first "
                "positional argument name."
            )
        if len(udf._parameter_list) == 0:
            raise ValueError(
                "arg_list must be a list of dictionaries. UDF does not accept any arguments."
            )
        name = udf._parameter_list[0]
        arg_list = [{name: arg} for arg in arg_list]

    return arg_list


@overload
def submit(
    udf: AnyBaseUdf | FunctionType | str,
    arg_list,
    /,
    *,
    engine: Optional[Literal["remote", "local"]] = "remote",
    max_workers: Optional[int] = None,
    max_retry: int = 2,
    debug_mode: Literal[False] = False,
    collect: Literal[True] = True,
    execution_type: ExecutionType = "thread_pool",
    **kwargs,
) -> "pd.DataFrame": ...


@overload
def submit(
    udf: AnyBaseUdf | FunctionType | str,
    arg_list,
    /,
    *,
    engine: Optional[Literal["remote", "local"]] = "remote",
    max_workers: Optional[int] = None,
    max_retry: int = 2,
    debug_mode: Literal[False] = False,
    collect: Literal[False] = False,
    execution_type: ExecutionType = "thread_pool",
    **kwargs,
) -> Union[JobPool, AsyncJobPool]: ...


@overload
def submit(
    udf: AnyBaseUdf | FunctionType | str,
    arg_list,
    /,
    *,
    engine: Optional[Literal["remote", "local"]] = "remote",
    max_workers: Optional[int] = None,
    max_retry: int = 2,
    debug_mode: Literal[True] = True,
    collect: Literal[True] = True,
    execution_type: ExecutionType = "thread_pool",
    **kwargs,
) -> ResultType: ...


def submit(
    udf: AnyBaseUdf | FunctionType | str,
    arg_list,
    /,
    *,
    engine: Optional[Literal["remote", "local"]] = "remote",
    max_workers: Optional[int] = None,
    max_retry: int = 2,
    debug_mode: bool = False,
    collect: bool = True,
    execution_type: ExecutionType = "thread_pool",
    cache_max_age: Optional[str] = None,
    cache: bool = True,
    ignore_exceptions: bool = False,
    flatten: bool = True,
    _before_run: Optional[float] = None,
    _before_submit: Optional[float] = 0.01,
    **kwargs,
) -> Union[BaseJobPool, ResultType, "pd.DataFrame"]:
    """
    Executes a user-defined function (UDF) multiple times for a list of input
    parameters, and return immediately a "lazy" JobPool object allowing
    to inspect the jobs and wait on the results.

    Each individual UDF run will be cached following the standard caching logic as with `fused.run()`
    and the specified `cache_max_age`. Additionally, when `collect=True` (the default), the collected results
    are cached locally for the duration of `cache_max_age` or 12h by default.

    See `fused.run` for more details on the UDF execution.

    Args:
        udf: the UDF to execute.
            See `fused.run` for more details on how to specify the UDF.
        arg_list: a list of input parameters for the UDF. Can be specified as:
            - a list of values for parametrizing over a single parameter, i.e.
              the first parameter of the UDF
            - a list of dictionaries for parametrizing over multiple parameters
            - A DataFrame for parametrizing over multiple parameters where each
              row is a set of parameters

        engine: The execution engine to use. Defaults to 'remote'.
        max_workers: The maximum number of workers to use. Defaults to 32.
        max_retry: The maximum number of retries for failed jobs. Defaults to 2.
        debug_mode: If True, executes only the first item in arg_list directly using
            `fused.run()`, useful for debugging UDF execution. Default is False.
        collect: If True, waits for all jobs to complete and returns the collected DataFrame
            containing the results. If False, returns a JobPool object, which is non-blocking
            and allows you to inspect the individual results and logs.
            Default is True.
        execution_type: The type of batching to use. Either "thread_pool" (default) for
            ThreadPoolExecutor-based concurrency or "async_loop" for asyncio-based concurrency.
        cache_max_age: The maximum age when returning a result from the cache.
            Supported units are seconds (s), minutes (m), hours (h), and days (d)
            (e.g. "48h", "10s", etc.).
            Default is `None` so a UDF run with `fused.run()` will follow
            `cache_max_age` defined in `@fused.udf()` unless this value is changed.
        cache: Set to False as a shortcut for `cache_max_age='0s'` to disable caching.
        ignore_exceptions: Set to True to ignore exceptions when collecting results.
            Runs that result in exceptions will be silently ignored. Defaults to False.
        flatten: Set to True to receive a DataFrame of results, without nesting of a
            `results` column, when collecting results. When False, results will be nested
            in a `results` column. If the UDF does not return a DataFrame (e.g. a string
            instead,) results will be nested in a `results` column regardless of this setting.
            Defaults to True.
        **kwargs: Additional (constant) keyword arguments to pass to the UDF.

    Returns:
        JobPool, AsyncJobPool, or DataFrame depending on execution_type and collect parameters

    Examples:
        Run a UDF multiple times for the values 0 to 9 passed to as the first
        positional argument of the UDF:
        ```py
        df = fused.submit("username@fused.io/my_udf_name", range(10))
        ```

        Using async batch type:
        ```py
        df = fused.submit(udf, range(10), execution_type="async_loop")
        ```

        Being explicit about the parameter name:
        ```py
        df = fused.submit(udf, [dict(n=i) for i in range(10)])
        ```

        Get the pool of ongoing tasks:
        ```py
        pool = fused.submit(udf, [dict(n=i) for i in range(10)], collect=False)
        ```

    """
    if execution_type not in ("thread_pool", "async_loop"):
        raise ValueError(
            f"'execution_type' must be 'thread_pool' or 'async_loop', got {execution_type}"
        )

    if isinstance(udf, FunctionType):
        if udf.__name__ == "<lambda>":
            # This will not work correctly in fused.udf. If we find a way to parse just the AST
            # of the lambda (without any surrounding function call, assignment, etc.) then we can
            # support lambda here
            raise TypeError(
                """Lambda expressions cannot be passed into fused.submit(). Create a function with @fused.udf instead:
@fused.udf
def udf(x):
    return x

fused.submit(udf, arg_list)
"""
            )
        # TODO: Move this logic to fused.run?
        udf: Udf = fused_udf(udf)

    arg_list = _validate_arg_list(arg_list, udf)

    if cache_max_age is not None:
        kwargs["cache_max_age"] = cache_max_age
    if not cache:
        kwargs["cache"] = cache

    if debug_mode:
        if not collect:
            warnings.warn(
                "'debug_mode=True' and 'collect=False' are mutually exclusive (the "
                "result of the first run is always returned directly), and the collect "
                "keyword is ignored in this case."
            )
        return fused_run(udf, engine=engine, **arg_list[0], **kwargs)

    max_workers = min(max_workers or 32, 1024)

    # set the cache_max_age if not provided, to be used for caching the submit collect results
    submit_cache_max_age = _parse_ttl(cache_max_age, cache=cache)
    if submit_cache_max_age is None:
        if isinstance(udf, BaseUdf) and udf.cache_max_age is not None:
            submit_cache_max_age = udf.cache_max_age
        elif isinstance(udf, str):
            submit_cache_max_age = 0
        else:
            submit_cache_max_age = _parse_ttl(DEFAULT_CACHE_MAX_AGE)

    if collect and submit_cache_max_age != 0:
        udf_name = udf if isinstance(udf, str) else udf.name or udf.entrypoint

        # cache the submit collect results
        fn = fused_cache(
            _submit_internal,
            cache_max_age=submit_cache_max_age,
            cache_folder_path=f"submit-{udf_name}",
            cache_reset=kwargs.get("cache_reset", None),
            cache_verbose=kwargs.get("cache_verbose", None),
            cache_storage=kwargs.get("cache_storage", "auto"),
        )
    else:
        fn = _submit_internal

    return fn(
        udf,
        arg_list,
        engine=engine,
        max_workers=max_workers,
        max_retry=max_retry,
        collect=collect,
        execution_type=execution_type,
        ignore_exceptions=ignore_exceptions,
        flatten=flatten,
        _before_run=_before_run,
        _before_submit=_before_submit,
        **kwargs,
    )


def _submit_internal(
    udf: AnyBaseUdf | str,
    arg_list: Any,
    /,
    *,
    engine: Literal["remote", "local"],
    max_workers: int,
    max_retry: int,
    collect: bool,
    execution_type: ExecutionType,
    ignore_exceptions: bool,
    flatten: bool,
    _before_run: float | None,
    _before_submit: float,
    **kwargs,
):
    """
    Helper function that can be cached conditionally
    """
    if execution_type == "async_loop":
        if HAS_NEST_ASYNCIO:
            nest_asyncio.apply()
        else:
            raise ImportError("async_loop execution_type requires 'nest_asyncio'")

        job_pool = AsyncJobPool(
            udf,
            arg_list,
            kwargs,
            engine=engine,
            max_workers=max_workers,
            max_retry=max_retry,
            before_run=_before_run,
            before_submit=_before_submit,
        )

        async def _run_async_batch():
            await job_pool._start_jobs()
            if collect:
                return job_pool.collect(
                    ignore_exceptions=ignore_exceptions, flatten=flatten
                )
            return job_pool

        # Either loop exists or needs to be created.
        return asyncio.run(_run_async_batch())

    else:
        job_pool = JobPool(
            udf,
            arg_list,
            kwargs,
            engine=engine,
            max_workers=max_workers,
            max_retry=max_retry,
            before_run=_before_run,
            before_submit=_before_submit,
        )
        job_pool._start_jobs()
        if collect:
            return job_pool.collect(
                ignore_exceptions=ignore_exceptions, flatten=flatten
            )
        return job_pool
