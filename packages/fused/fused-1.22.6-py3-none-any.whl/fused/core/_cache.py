from __future__ import annotations

import ast
import contextlib
import functools
import hashlib
import inspect
import itertools
import os
import pickle
import re
import sys
import time
import urllib.parse
import warnings
from dataclasses import dataclass, fields
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Awaitable, Callable, Iterable, TypeVar
from uuid import uuid4

import fsspec
from loguru import logger

import fused
from fused._environment import is_pyodide
from fused._optional_deps import (
    HAS_PANDAS,
    PD_DATAFRAME,
    PD_HASH_OBJECT_FN,
    PD_INDEX,
    PD_SERIES,
)
from fused._options import StorageStr, cache_directory, get_writable_dir
from fused._options import options as OPTIONS
from fused.core._impl._download_impl import filesystem
from fused.models.udf import BaseUdf
from fused.warnings import FusedDeprecationWarning

DEFAULT_CACHE_MAX_AGE = "12h"


class CacheResultError(Exception):
    pass


class LockError(Exception):
    pass


@dataclass
class CacheLogEntry:
    created: datetime
    expiration: datetime
    uuid: str
    status: str

    # TODO: Make class responsible for serialization to consolidate logic
    @classmethod
    def byte_length(cls):
        create_length = 25  # datetime.isoformat
        ex_length = 25  # datetime.isoformat
        uuid = 36  # str(uuid4())
        status = 1  # char
        commas = len(fields(cls)) - 1
        newline = 1
        return create_length + ex_length + uuid + status + commas + newline

    def relative_create_time_str(self):
        now = datetime.now(timezone.utc)
        diff = now - self.created

        days = diff.days
        hours = diff.seconds // 3600
        minutes = (diff.seconds // 60) % 60
        seconds = diff.seconds % 60
        decimal_seconds = diff.microseconds / 1e6
        parts = []
        max_parts = 2
        if days:
            unit = "days" if days > 1 else "day"
            parts.append(f"{days} {unit}")
        if hours:
            unit = "hours" if hours > 1 else "hour"
            parts.append(f"{hours} {unit}")
        if minutes and len(parts) < max_parts:
            unit = "minutes" if minutes > 1 else "minute"
            parts.append(f"{minutes} {unit}")
        if not days and seconds and len(parts) < max_parts:
            unit = "seconds" if seconds > 1 else "second"
            parts.append(f"{seconds} {unit}")
        elif not days and not seconds and len(parts) < max_parts:
            parts.append(f"{decimal_seconds:.2f} seconds")

        return f"{' '.join(parts)}"


@dataclass
class ArgumentParseResult:
    arg_end_index: int = -1
    """Index specifying the end of positional arguments"""
    exclude_var_positional: bool = False
    """Whether variable positional arguments (*param_name) are excluded"""
    param_names: list[str] = None
    """List of all parsed param names defined on the function. Used to specifically map the order of params to their name"""


def print_message(message, verbose=None):
    verbose = verbose if verbose is not None else OPTIONS.verbose_cached_functions
    if verbose:
        print(message, file=sys.stdout)


# TODO: Possibly move all related methods to a class


class _UdfScopeAst:
    """
    Hashes a UDF based on the main entrypoint and all objects in scope.
    """

    tree: ast.AST
    code: str
    entrypoint_func: ast.FunctionDef | ast.AsyncFunctionDef | None = None
    all_functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    all_objects: dict[str, ast.Assign] = {}

    def __init__(self, code: str):
        self.code = code
        self.tree = ast.parse(code)

    def _find_entrypoint_function(
        self, entrypoint: str
    ) -> ast.FunctionDef | ast.AsyncFunctionDef:
        """
        Find the entrypoint function in an AST tree.
        """
        entrypoint_func: ast.FunctionDef | ast.AsyncFunctionDef | None = None
        for node in ast.walk(self.tree):
            if (
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == entrypoint
                and len(node.decorator_list) > 0  # Entrypoint must have a decorator
            ):
                if entrypoint_func is not None:
                    raise ValueError(
                        f"Multiple entrypoint functions found for {entrypoint}"
                    )
                entrypoint_func = node

        assert entrypoint_func is not None, "Could not find entrypoint function"
        return entrypoint_func

    def _find_objects_in_scope(self):
        """
        Find all non-local functions and objects in scope of the entrypoint function.
        """
        # Build parent mapping and get parent scopes for entrypoint
        parent_map: dict[int, ast.AST] = {}
        for node in ast.walk(self.tree):
            for child in ast.iter_child_nodes(node):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    parent_map[id(child)] = node

        # Create list of parent scopes (from entrypoint up to root)
        parent_scopes: list[ast.AST] = []
        current = parent_map.get(id(self.entrypoint_func))
        while current is not None:
            parent_scopes.append(current)
            current = parent_map.get(id(current))

        # Collect functions and objects only from parent scopes
        for scope in parent_scopes:
            for node in ast.iter_child_nodes(scope):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if node.name not in self.all_functions:
                        self.all_functions[node.name] = node
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            if target.id not in self.all_objects:
                                self.all_objects[target.id] = node

    def _collect_dependencies(
        self, entrypoint_func: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[ast.stmt]:
        """
        Collect all dependencies of the entrypoint function.
        """
        visited: set[int] = set()
        relevant_nodes: list[ast.stmt] = []

        # Find all functions and objects in scope
        self._find_objects_in_scope()

        def collect_dependencies_recursive(node: ast.stmt):
            """Recursively collect all nodes that are dependencies of the given node."""
            if id(node) in visited:
                return
            visited.add(id(node))
            relevant_nodes.append(node)

            # Walk through the node recursively to find dependencies
            # Most other classes will end up in a Name sub-class
            for child in ast.walk(node):
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Load):
                    # Variable references: some_var
                    name = child.id
                    if name in self.all_functions:
                        collect_dependencies_recursive(self.all_functions[name])
                    elif name in self.all_objects:
                        collect_dependencies_recursive(self.all_objects[name])
                elif isinstance(child, ast.Call):
                    # Function calls: func(), obj.method()
                    match child.func:
                        case ast.Name():
                            func_name = child.func.id
                            if func_name in self.all_functions:
                                collect_dependencies_recursive(
                                    self.all_functions[func_name]
                                )
                        case ast.Attribute():
                            if isinstance(child.func.value, ast.Name):
                                obj_name = child.func.value.id
                                if obj_name in self.all_objects:
                                    collect_dependencies_recursive(
                                        self.all_objects[obj_name]
                                    )
                        case _:
                            # The above cases are all the documented node types to cover.
                            pass

        # Start dependency collection from the entrypoint function
        collect_dependencies_recursive(entrypoint_func)
        return relevant_nodes

    def hashify_udf(self, entrypoint: str) -> str:
        """
        Parse UDF code using AST and recursively hash the code starting from the entrypoint function.
        This creates a more stable hash that focuses on the changes in the code that affect the execution of the function.
        """

        # Find the entrypoint function
        self.entrypoint_func = self._find_entrypoint_function(entrypoint)
        # Start dependency collection from the entrypoint function
        relevant_nodes = self._collect_dependencies(self.entrypoint_func)
        # Create a normalized representation for hashing
        # Sort nodes by their line number for consistent ordering
        relevant_nodes.sort(key=lambda n: n.lineno)
        # Create a string representation of the relevant AST nodes
        # Use original source code to preserve whitespace and comments
        code_lines = self.code.splitlines()

        hash_content = []
        for node in relevant_nodes:
            try:
                # Extract original source code for this node to preserve whitespace and comments
                start_line = node.lineno - 1  # Convert to 0-based indexing
                end_line = node.end_lineno  # end_lineno is inclusive, so no -1 needed

                # Extract the source lines for this node
                node_source_lines = code_lines[start_line:end_line]
                node_str = "\n".join(node_source_lines)
                hash_content.append(node_str)
            except Exception:
                # Fallback to dumping the AST structure
                hash_content.append(ast.dump(node, include_attributes=False))

        # Create the final hash
        combined_content = "\n".join(hash_content)
        return _hashify(combined_content)


def _hashify(func) -> str:
    hash_object = hashlib.sha256()
    try:
        if hasattr(func, "__fused_cached_fn"):
            return _hashify(func.__fused_cached_fn)
        elif isinstance(func, BaseUdf):
            # Must be before callable(func) as it is callable but has no __code__ attribute
            if func.metadata and func.metadata.get("fused:id"):
                udf_id = func.metadata.get("fused:id", "")
                udf_last_modified = func.metadata.get("fused:gitLastModified", "")
                # gitLastModified is only set for UDFs stored in git AND loaded using token (no pinned version URL)
                # So for most cases, we just use the UDF ID as the hash
                hash_object.update(f"{udf_id}:{udf_last_modified}".encode("utf-8"))
            else:
                try:
                    # Use AST-based hashing for UDF code starting from the entrypoint for local UDFs
                    ast_hash = _UdfScopeAst(func.code).hashify_udf(func.entrypoint)
                    hash_object.update(ast_hash.encode("utf-8"))
                except Exception as e:
                    logger.warning(f"Error hashing UDF: {e}")
                    return _hashify(func.model_dump_json())
        elif callable(func):
            hash_object.update(inspect.getsource(func).encode("utf8"))
        else:
            if HAS_PANDAS and isinstance(func, (PD_DATAFRAME, PD_SERIES, PD_INDEX)):
                hash_target = PD_HASH_OBJECT_FN(func).to_numpy()
            else:
                hash_target = str(func).encode("utf-8")

            hash_object.update(hash_target)
        return hash_object.hexdigest()
    except Exception as e:
        logger.warning(f"Error Hashing {e}")
        return ""


def parse_function_arguments(
    func: Callable, excluded_parameters: set
) -> ArgumentParseResult:
    """Parse a cache decorated function's arguments to help with calculating the function's cache hash key.

     Inspect parameters to identify arg names and their index. Also noting the position where normal positional
     arguments end and deciding whether to include variable positional arguments in the hash key.

    Args:
        func: The function to inspect
        excluded_parameters: Set of parameter names to exclude in hash calculation

    Returns:
        ArgumentParseResult
    """
    sig = inspect.signature(func)
    arg_end_index = -1
    exclude_var_positional = False

    param_names = []
    for i, (name, p) in enumerate(sig.parameters.items()):
        if p.kind == p.POSITIONAL_ONLY or p.kind == p.POSITIONAL_OR_KEYWORD:
            arg_end_index = i
        elif p.kind == p.VAR_POSITIONAL and p.name in excluded_parameters:
            exclude_var_positional = True
        param_names.append(name)

    return ArgumentParseResult(arg_end_index, exclude_var_positional, param_names)


def _parse_time_format(t: str | int) -> timedelta:
    if t == 0 or (isinstance(t, str) and t.strip() == "0"):
        return timedelta(0)

    if isinstance(t, int):
        t = f"{t}s"

    quantifier = re.match(r"(\d+)([smhd])$", t.strip().lower())
    if not quantifier:
        raise ValueError(
            f"Invalid time format {t!r}: Use a number followed by one of 's' (seconds), 'm' (minutes), 'h' (hours), or 'd' (days)."
        )
    value, unit = int(quantifier.group(1)), quantifier.group(2)
    if value < 0:
        raise ValueError(f"Time format {t!r} cannot be less than zero")

    delta_map = {
        "s": timedelta(seconds=value),
        "m": timedelta(minutes=value),
        "h": timedelta(hours=value),
        "d": timedelta(days=value),
    }

    return delta_map[unit]


def _format_now_with_delta(delta: timedelta) -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    return (now + delta).isoformat()


def _write_cache_file(
    func: Callable,
    args: tuple,
    kwargs: dict,
    cache_path: Path,
    uuid: str,
    max_age_delta: timedelta,
    timeout_delta: timedelta,
    file_interface: fsspec.AbstractFileSystem,
):
    logger.debug(f"Caching {func.__qualname__} under {uuid}")
    in_prog_expires = _format_now_with_delta(timeout_delta)
    # Acquire lock and set status to in-progress
    _write_cache_log(
        cache_path, uuid, in_prog_expires, status="p", file_interface=file_interface
    )
    try:
        data = func(*args, **kwargs)
    except Exception as e:
        logger.debug(f"Error running {func.__qualname__}: {e}")
        # Release lock and set status to fail
        expires = _format_now_with_delta(timedelta(0))
        _write_cache_log(
            cache_path, uuid, expires, status="f", file_interface=file_interface
        )
        raise

    with file_interface.open(str(cache_path / f"{uuid}.pickle"), "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    # Release lock and set status to done
    expires = _format_now_with_delta(max_age_delta)
    _write_cache_log(
        cache_path, uuid, expires, status="d", file_interface=file_interface
    )
    return data


async def _write_cache_file_async(
    func: Callable,
    args: tuple,
    kwargs: dict,
    cache_path: Path,
    uuid: str,
    max_age_delta: timedelta,
    timeout_delta: timedelta,
    file_interface: fsspec.AbstractFileSystem,
):
    logger.debug(f"Caching {func.__qualname__} under {uuid}")
    in_prog_expires = _format_now_with_delta(timeout_delta)
    # Acquire lock and set status to in-progress
    _write_cache_log(
        cache_path, uuid, in_prog_expires, status="p", file_interface=file_interface
    )
    try:
        data = await func(*args, **kwargs)
    except Exception as e:
        logger.debug(f"Error running {func.__qualname__}: {e}")
        # Release lock and set status to fail
        expires = _format_now_with_delta(timedelta(0))
        _write_cache_log(
            cache_path, uuid, expires, status="f", file_interface=file_interface
        )
        raise

    with file_interface.open(str(cache_path / f"{uuid}.pickle"), "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    # Release lock and set status to done
    expires = _format_now_with_delta(max_age_delta)
    _write_cache_log(
        cache_path, uuid, expires, status="d", file_interface=file_interface
    )
    return data


def _cleanup_expired_links(directory: Path, max_age: timedelta):
    max_age_ns = max_age.total_seconds() * 1e9
    now_ns = time.time_ns()
    for link in directory.iterdir():
        last_modified = int(link.name.split("-", maxsplit=1)[0])
        diff = now_ns - last_modified
        if diff > max_age_ns:
            logger.debug(f"Removing expired {link} link: {diff}, {max_age_ns}")
            link.unlink(missing_ok=True)


def _cleanup_expired_file_locks(directory: Path, max_age: timedelta):
    max_age_ns = max_age.total_seconds() * 1e9
    now_ns = time.time_ns()
    for lock in directory.iterdir():
        with open(lock) as lockfile:
            last_modified = int(lockfile.read())
        diff = now_ns - last_modified
        if diff > max_age_ns:
            logger.debug(f"Removing expired {lock} lock: {diff}, {max_age_ns}")
            lock.unlink(missing_ok=True)


@contextlib.contextmanager
def _get_lock(target: Path, lock_dir, new_cache_uuid, cache_interface):
    critera = cache_interface, is_pyodide()
    match critera:
        case "filesystem", True:
            lock_file = lock_dir / f"{target.name}.lock"
            lock_method = _file_lock(lock_file)
        case "filesystem", False:
            now_ns = time.time_ns()
            lock_file = lock_dir / f"{now_ns}-{new_cache_uuid}.log"
            lock_method = _link_based_lock(lock_file, target)
        case "s3", _:
            lock_key = ""
            lock_method = _redis_lock(lock_key)
        case "gs", _:
            lock_key = ""
            lock_method = _redis_lock(lock_key)
        case _:
            raise NotImplementedError(critera)

    with lock_method:
        yield


@contextlib.contextmanager
def _redis_lock(lock_key: str):
    yield


@contextlib.contextmanager
def _file_lock(lock_file: Path):
    # Cleanup expired locks if they were not cleaned up from previous runs
    _cleanup_expired_file_locks(lock_file.parent, timedelta(seconds=5))

    lock_fd = None
    try:
        lock_fd = os.open(lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        os.write(lock_fd, str(time.time_ns()).encode("utf8"))
        os.close(lock_fd)
        yield
    except FileExistsError as e:
        raise LockError(f"Could not lock {e}")
    finally:
        if lock_fd:
            os.remove(lock_file)


@contextlib.contextmanager
def _link_based_lock(link_file: Path, target: Path):
    logger.debug(f"Attempting to lock {target}")
    # Cleanup expired links if they were not cleaned up from previous runs
    _cleanup_expired_links(link_file.parent, timedelta(seconds=5))

    try:
        # TODO: convert to link_file.hardlink_to(target) once 3.9 is no longer supported
        os.link(target, link_file)
    except OSError as e:
        raise LockError(f"Could not lock {e}")

    # nlink = 2 because we have 1 from the target file, then 1 from the link serving as a lock.
    # nlink > 2 means multiple links were created and target currently "locked".
    if target.stat().st_nlink == 2:
        logger.debug(f"Lock acquired on {target}")
    else:
        link_file.unlink(missing_ok=True)
        raise LockError("Too many locks")

    try:
        yield
    finally:
        logger.debug(f"Unlocking {target}")
        link_file.unlink()


def _write_cache_log(
    cache_path: Path,
    uuid: str,
    expires_on: str,
    status: str,
    file_interface: fsspec.AbstractFileSystem,
):
    log_file = str(cache_path / "index.log")
    created = _format_now_with_delta(timedelta())
    # Not all interfaces support append and will instead overwrite the file (e.g. gcsfs).
    # We don't need to work around this as we use a "last write wins" approach anyway, and we don't read past entries.
    with file_interface.open(log_file, "a") as f:
        f.write(f"{created},{expires_on},{uuid},{status}\n")

    logger.debug(f"Wrote {uuid} to cache log {log_file} with status {status}")


def _read_cache_log(
    cache_path: Path, file_interface: fsspec.AbstractFileSystem
) -> CacheLogEntry | None:
    log_file = cache_path / "index.log"
    recent_cache_entry = None
    try:
        with file_interface.open(str(log_file), "rb") as logfile:
            if logfile.size > 0:
                logfile.seek(CacheLogEntry.byte_length() * -1, 2)
                recent_cache_entry = logfile.read().strip().decode("utf8")
    except OSError as e:
        # TODO: Maybe check for both pyodide and regular file empty codes?
        # file is not empty
        if "invalid argument" not in str(e).lower():
            logger.debug(f"Reading log file failed: {e}")
            raise

    if recent_cache_entry:
        try:
            created, expiration, uuid, status = (
                d.strip() for d in recent_cache_entry.split(",")
            )
            logger.debug(
                f"Recent cache entry found in {log_file}: {expiration!r}, {uuid!r}, {status!r}"
            )
            return CacheLogEntry(
                datetime.fromisoformat(created),
                datetime.fromisoformat(expiration),
                uuid,
                status,
            )
        except (TypeError, ValueError) as e:
            logger.debug(
                f"Issues with parsing last line in log {e}. Truncating logfile {log_file}"
            )
            # Any issue with parsing the last line. This could mean the file is corrupted or the cache entry format has
            # changed, therefore we clear the file.
            with file_interface.open(str(log_file), "w") as logfile:
                logfile.truncate()

    return None


def _read_cache_file(
    cache_path: Path, uuid: str, file_interface: fsspec.AbstractFileSystem
):
    cache_file = str(cache_path / f"{uuid}.pickle")
    try:
        with file_interface.open(cache_file, "rb") as f:
            data = pickle.load(f)
            return data
    except Exception as e:
        raise CacheResultError(f"Error reading cache file {cache_file}") from e


def wait_for_ready_result(
    fn_name: str,
    start_time: datetime,
    max_retries: int,
    wait_time_seconds: int,
    path_dir: Path,
    file_interface: fsspec.AbstractFileSystem,
    *,
    result_expected_soon: bool = False,
    cache_verbose: bool | None = None,
):
    """Wait until a cache entry is ready to be read or immediately return if no result is found.

    A ready result is one that is no longer in-progress of execution or being written by another parallel invocation.
    This can either be successful (cache written and can be read) or failure (function that was decorated with cache
    decorator failed mid-execution). When this is used for reading the cache for the first time, and an expired
    in-progress or no result could exist, we do not want to wait for one to be ready. However, in the case where we
    know another invocation has acquired a lock and will write an entry, `result_expected_soon` can be used during
    these situations to continue to wait.

    Args:
        fn_name (str): Function name to log
        start_time (datetime): Baseline datetime used to check expiration
        max_retries (int): Max amount of attempts to read a valid cache entry
        wait_time_seconds (int): Amount of time to wait per retry
        path_dir (Path): Directory where cache files exist for the function
        result_expected_soon (bool): Whether to wait if an expired in-progress or no cache entry is detected. Useful
            when the caller knows that an entry will soon be available.
        cache_verbose: Print a message when a cached result is returned

    Raises:
        CacheResultError: When max retries has been reached, cache entry has expired, no cache entry exists, or a
            failed entry was detected.
    Returns:
        Un-serialized cache data if a non-expired, successful entry exists
    """

    retries = 0
    now = start_time
    while True:
        log_msg = ""
        log_params = {}
        cache_entry = _read_cache_log(path_dir, file_interface)
        if cache_entry is None:
            if not result_expected_soon:
                break
            # In the situation where no entry exists and multiple invocations attempt to write to the log file, only one
            # will successfully acquire the lock while the others will wait for the result in this loop. In this case,
            # we want to wait for the result, so we do not break out of the loop.
            log_msg = "Sleeping. No entry found yet. Retry [{retries}/{max_retries}]"
        elif cache_entry.status == "p" and now < cache_entry.expiration:
            log_msg = (
                "Sleeping. Cache entry reporting {cache_status}, {now} < {expiration}, "
                "current write might be in progress. Retry [{retries}/{max_retries}]"
            )
            log_params = {
                "cache_status": cache_entry.status,
                "now": now,
                "expiration": cache_entry.expiration,
            }
        elif cache_entry.status == "p" and now >= cache_entry.expiration:
            # In the situation where a stale in-progress entry exists and multiple invocations attempt to write to the
            # log file, only one will successfully acquire the lock while the others will wait for result in this loop.
            # In this case, we want to wait for the result, so we do not raise a cache error.
            if not result_expected_soon:
                raise CacheResultError(f"Expired: {cache_entry.expiration}")
        else:
            # Cache entry no longer in progress
            break

        retries += 1
        if retries > max_retries:
            raise TimeoutError("Max retries reached")

        if log_msg:
            log_params.update({"retries": retries, "max_retries": max_retries})
            logger.debug(log_msg.format(**log_params))
        time.sleep(wait_time_seconds)

    if cache_entry is None:
        raise CacheResultError("No cache result")

    logger.debug(
        f"Detected status is {cache_entry.status} and expiration is {cache_entry.expiration}"
    )
    if cache_entry.status == "d" and now < cache_entry.expiration:
        logger.debug(f"Reading cache for {fn_name} under {cache_entry.uuid}")
        print_message(
            f"'{fn_name}' returned cached result: {cache_entry.relative_create_time_str()} old",
            verbose=cache_verbose,
        )
        # Cache exists and valid
        return _read_cache_file(path_dir, cache_entry.uuid, file_interface)
    raise CacheResultError(
        f"Failed status or expired: {cache_entry.uuid}. {cache_entry.status}, {cache_entry.expiration}"
    )


def _hash_func_closures(func) -> str:
    id_str = ""
    closure_vars = inspect.getclosurevars(func)
    # Globals - global objects referenced within the function
    # Nonlocals - closure objects (objects defined in an outer function scope) referenced within the inner function
    func_closures = itertools.chain(
        closure_vars.globals.items(),
        closure_vars.nonlocals.items(),
    )

    for _k, v in func_closures:
        # Handles UDF.utils references
        if isinstance(v, fused.models.udf.base_udf.AttrDict):
            udf = v["_udf"]
        # Handles UDF references
        elif isinstance(v, fused.models.udf.BaseUdf):
            udf = v
        else:
            continue
        id_str += _hashify(udf)
    return id_str


def _get_file_interface(
    cache_interface: str, enable_async=False
) -> fsspec.AbstractFileSystem:
    from fused.api import FdFileSystem

    kwargs = {
        "skip_instance_cache": True,
        "use_listings_cache": False,
        "asynchronous": enable_async,
    }

    match cache_interface:
        case "filesystem":
            return filesystem("file", **kwargs)
        case "s3":
            return FdFileSystem(**kwargs)
        case "gs":
            kwargs["project"] = OPTIONS.gcp_project_name
            return FdFileSystem(**kwargs)
        case _:
            raise NotImplementedError(cache_interface)


def _cache(
    func: Callable,
    *args,
    cache_max_age: str | int = DEFAULT_CACHE_MAX_AGE,
    cache_folder_path: str = "tmp",
    concurrent_lock_timeout: str | int = 120,
    cache_reset: bool | None = None,
    cache_storage: StorageStr | None = None,
    cache_key_exclude: Iterable[str] = None,
    cache_verbose: bool | None = None,
    **kwargs: dict[str, Any],
) -> Any:
    """Internal method used by cache decorator to cache a function's pickleable response to a file.

    Args:
        func: The decorated function.
        *args: Positional arguments to the decorated function.
        cache_max_age: A string with a numbered component and units. Supported units are seconds (s), minutes (m),
            hours (h), and days (d) (e.g. "48h", "10s", etc.).
        cache_folder_path: Folder to append to the configured cache directory.
        concurrent_lock_timeout: Max amount of time for concurrent calls to wait for the decorated function
            to finish execution and to write the cache file currently being written by another concurrent call.
            Waiting will end before the timeout if a finished cache file is detected after reading the most recent entry
            in the log. Otherwise, after the timeout, it will either find a finished cached file to read, or it will
            write a new one if a cache file has not been recorded in the log.
        cache_reset: Ignore `cache_max_age` and overwrite cached result.
        cache_storage: Set where the cache data is stored. Supported values are "auto", "mount", "local", and
            "object". Auto will automatically select the storage location defined in options (mount if it
            exists, otherwise local) and ensures that it exists and is writable. Mount gets shared across executions
            where local will only be shared within the same execution.
        cache_key_exclude: An iterable of parameter names to exclude from the cache key calculation. Useful for
            arguments that do not affect the result of the function and could cause unintended cache expiry (e.g.
            database connection objects)
        cache_verbose: Print a message when a cached result is returned
        **kwargs: Keyword arguments to the decorated function.

    Returns:
        Any: Result from the cached function
    """
    # Calculate expires_on
    if cache_storage is None:
        cache_storage = OPTIONS.cache_storage
    max_age_delta = _parse_time_format(cache_max_age)
    timeout_delta = _parse_time_format(concurrent_lock_timeout)
    cache_interface = _get_cache_interface(cache_storage)
    file_interface = _get_file_interface(cache_interface)
    try:
        path = _get_cache_base_path(cache_folder_path, cache_storage)
        # TODO: ignore `_`

        if cache_key_exclude is None:
            cache_key_exclude = set()
        elif isinstance(cache_key_exclude, str):
            cache_key_exclude = {cache_key_exclude}
        elif isinstance(cache_key_exclude, bytes):
            raise ValueError(
                "'cache_key_exclude' must be a collection of parameter names or a single name as a string."
            )
        else:
            cache_key_exclude = set(cache_key_exclude)

        # 1. Hashify function
        id = _hashify(func)

        parsed_result = parse_function_arguments(func, cache_key_exclude)

        # 2. Hashify args
        for i, name in enumerate(parsed_result.param_names):
            # Any args after arg_end_index are variable positional
            if i > parsed_result.arg_end_index and parsed_result.exclude_var_positional:
                break

            if name not in cache_key_exclude and i < len(args):
                id += "_" + _hashify(args[i])

        # 3. Hashify kwargs
        for k in kwargs:
            if k not in cache_key_exclude:
                id += "_" + k + _hashify(kwargs[k])
        # 4. Hashify cache_max_age
        id += "_" + _hashify(max_age_delta)
        # 5. Check UDF references
        id += "_" + _hashify(_hash_func_closures(func))
        # 6. Hashify composite id
        id = _hashify(id)

        path_dir = path / f"data_{id}"
        locks_dir = path / f"data_{id}" / "locks"

        file_interface.mkdirs(str(path_dir), exist_ok=True)
        file_interface.mkdirs(str(locks_dir), exist_ok=True)
        log_file = path_dir / "index.log"
        # Ensure log file exists
        # File will exist on average cases, so we check first to reduce the amount of calls and exception handling
        if not file_interface.exists(str(log_file)):
            # Parallel requests can occur where the atomic file creation will succeed, and others will fail, so we make
            # sure we handle that.
            try:
                file_interface.touch(str(log_file), truncate=False)
            except (NotImplementedError, ValueError):
                # gcsfs - NotImplementedError, s3fs - ValueError
                # Some interfaces don't support file metadata updates if the file already exists
                pass

        new_cache_uuid = str(uuid4())
        timeout_seconds = timeout_delta.total_seconds()
        now = datetime.now(timezone.utc)
        wait_time_seconds = 1
        max_retries = int(timeout_seconds // wait_time_seconds)
        fn_name = func.__name__

        if not cache_reset:
            try:
                return wait_for_ready_result(
                    fn_name,
                    now,
                    max_retries,
                    wait_time_seconds,
                    path_dir,
                    file_interface=file_interface,
                    cache_verbose=cache_verbose,
                )
            except (CacheResultError, TimeoutError) as e:
                logger.debug(f"Cache entry not valid: {e}")
                # A completed cache result could not be found and needs to be written. Continue to write logic.
                pass

        # Multiple simultaneous write calls can happen. We attempt to lock and those that fail will wait for the cache
        # entry to complete. This is extremely helpful for cached functions that need a "run once" and perform
        # operations in a non-parallel safe way.
        try:
            with _get_lock(
                path_dir / "index.log", locks_dir, new_cache_uuid, cache_interface
            ):
                return _write_cache_file(
                    func,
                    args,
                    kwargs,
                    path_dir,
                    new_cache_uuid,
                    max_age_delta,
                    timeout_delta,
                    file_interface=file_interface,
                )
        except LockError as e:
            logger.debug(f"LockError: {e}")

            # Lock currently in use to write cache entry, wait for result.
            # If invocation that has the lock errors due to an error in the decorated function or otherwise, this will
            # either time out or an exception will be raised that a failed result was detected.
            return wait_for_ready_result(
                fn_name,
                now,
                max_retries,
                wait_time_seconds,
                path_dir,
                file_interface=file_interface,
                result_expected_soon=True,
                cache_verbose=cache_verbose,
            )

    except Exception as e:
        logger.debug(f"Error Caching {e}")
        if isinstance(e, TimeoutError):
            msg = f"Wait time exceeded concurrent_lock_timeout of {timeout_delta.total_seconds()}s"
            raise TimeoutError(msg) from e
        raise e


async def _cache_async(
    func: Callable,
    *args,
    cache_max_age: str | int = DEFAULT_CACHE_MAX_AGE,
    cache_folder_path: str = "tmp",
    concurrent_lock_timeout: str | int = 120,
    cache_reset: bool | None = None,
    cache_storage: StorageStr | None = None,
    cache_key_exclude: Iterable[str] = None,
    cache_verbose: bool | None = None,
    **kwargs: dict[str, Any],
) -> Any:
    """Async internal method used by cache decorator to cache a function's pickleable response to a file.

    Args:
        func: The decorated function.
        *args: Positional arguments to the decorated function.
        cache_max_age: A string with a numbered component and units. Supported units are seconds (s), minutes (m),
            hours (h), and days (d) (e.g. "48h", "10s", etc.).
        cache_folder_path: Folder to append to the configured cache directory.
        concurrent_lock_timeout: Max amount of time for concurrent calls to wait for the decorated function
            to finish execution and to write the cache file currently being written by another concurrent call.
            Waiting will end before the timeout if a finished cache file is detected after reading the most recent entry
            in the log. Otherwise, after the timeout, it will either find a finished cached file to read, or it will
            write a new one if a cache file has not been recorded in the log.
        cache_reset: Ignore `cache_max_age` and overwrite cached result.
        cache_storage: Set where the cache data is stored. Supported values are "auto", "mount", "local", and
            "object". Auto will automatically select the storage location defined in options (mount if it
            exists, otherwise local) and ensures that it exists and is writable. Mount gets shared across executions
            where local will only be shared within the same execution.
        cache_key_exclude: An iterable of parameter names to exclude from the cache key calculation. Useful for
            arguments that do not affect the result of the function and could cause unintended cache expiry (e.g.
            database connection objects)
        cache_verbose: Print a message when a cached result is returned
        **kwargs: Keyword arguments to the decorated function.

    Returns:
        Any: Result from the cached function
    """
    # Calculate expires_on
    if cache_storage is None:
        cache_storage = OPTIONS.cache_storage
    max_age_delta = _parse_time_format(cache_max_age)
    timeout_delta = _parse_time_format(concurrent_lock_timeout)
    cache_interface = _get_cache_interface(cache_storage)
    file_interface = _get_file_interface(cache_interface)
    try:
        path = _get_cache_base_path(cache_folder_path, cache_storage)
        # TODO: ignore `_`

        if cache_key_exclude is None:
            cache_key_exclude = set()
        elif isinstance(cache_key_exclude, str):
            cache_key_exclude = {cache_key_exclude}
        elif isinstance(cache_key_exclude, bytes):
            raise ValueError(
                "'cache_key_exclude' must be a collection of parameter names or a single name as a string."
            )
        else:
            cache_key_exclude = set(cache_key_exclude)

        # 1. Hashify function
        id = _hashify(func)

        parsed_result = parse_function_arguments(func, cache_key_exclude)

        # 2. Hashify args
        for i, name in enumerate(parsed_result.param_names):
            # Any args after arg_end_index are variable positional
            if i > parsed_result.arg_end_index and parsed_result.exclude_var_positional:
                break

            if name not in cache_key_exclude and i < len(args):
                id += "_" + _hashify(args[i])

        # 3. Hashify kwargs
        for k in kwargs:
            if k not in cache_key_exclude:
                id += k + _hashify(kwargs[k])

        # 4. Hashify cache_max_age
        id += _hashify(max_age_delta)

        # 5. Check UDF references
        id += _hashify(_hash_func_closures(func))

        # 6. Hashify composite id
        id = _hashify(id)

        path_dir = path / f"data_{id}"
        locks_dir = path / f"data_{id}" / "locks"

        file_interface.mkdirs(str(path_dir), exist_ok=True)
        file_interface.mkdirs(str(locks_dir), exist_ok=True)
        log_file = path_dir / "index.log"
        # Ensure log file exists
        # File will exist on average cases, so we check first to reduce the amount of calls and exception handling
        if not file_interface.exists(str(log_file)):
            # Parallel requests can occur where the atomic file creation will succeed, and others will fail, so we make
            # sure we handle that.
            try:
                file_interface.touch(str(log_file), truncate=False)
            except (NotImplementedError, ValueError):
                # gcsfs - NotImplementedError, s3fs - ValueError
                # Some interfaces don't support file metadata updates if the file already exists
                pass

        new_cache_uuid = str(uuid4())
        timeout_seconds = timeout_delta.total_seconds()
        now = datetime.now(timezone.utc)
        wait_time_seconds = 1
        max_retries = int(timeout_seconds // wait_time_seconds)
        fn_name = func.__name__

        if not cache_reset:
            try:
                return wait_for_ready_result(
                    fn_name,
                    now,
                    max_retries,
                    wait_time_seconds,
                    path_dir,
                    file_interface=file_interface,
                    cache_verbose=cache_verbose,
                )
            except (CacheResultError, TimeoutError) as e:
                logger.debug(f"Cache entry not valid: {e}")
                # A completed cache result could not be found and needs to be written. Continue to write logic.
                pass

        # Multiple simultaneous write calls can happen. We attempt to lock and those that fail will wait for the cache
        # entry to complete. This is extremely helpful for cached functions that need a "run once" and perform
        # operations in a non-parallel safe way.
        try:
            with _get_lock(
                path_dir / "index.log", locks_dir, new_cache_uuid, cache_interface
            ):
                return await _write_cache_file_async(
                    func,
                    args,
                    kwargs,
                    path_dir,
                    new_cache_uuid,
                    max_age_delta,
                    timeout_delta,
                    file_interface=file_interface,
                )
        except LockError as e:
            logger.debug(f"LockError: {e}")

            # Lock currently in use to write cache entry, wait for result.
            # If invocation that has the lock errors due to an error in the decorated function or otherwise, this will
            # either time out or an exception will be raised that a failed result was detected.
            return wait_for_ready_result(
                fn_name,
                now,
                max_retries,
                wait_time_seconds,
                path_dir,
                file_interface=file_interface,
                result_expected_soon=True,
                cache_verbose=cache_verbose,
            )

    except Exception as e:
        logger.debug(f"Error Caching {e}")
        if isinstance(e, TimeoutError):
            msg = f"Wait time exceeded concurrent_lock_timeout of {timeout_delta.total_seconds()}s"
            raise TimeoutError(msg) from e
        raise e


def _cache_internal(func, **decorator_kwargs):
    # Handle deprecated parameters from decorator
    deprected_param_map = {
        "path": "cache_folder_path",
        "storage": "cache_storage",
        "reset": "cache_reset",
    }
    for old_param, new_param in deprected_param_map.items():
        if decorator_kwargs.get(old_param) is not None:
            warnings.warn(
                f"The '{old_param}' keyword is deprecated. Use '{new_param}' instead",
                FusedDeprecationWarning,
            )
            decorator_kwargs[new_param] = decorator_kwargs.get(old_param)
        decorator_kwargs.pop(old_param, None)

    def decorator(func):
        if inspect.iscoroutinefunction(func):

            @functools.wraps(func)
            async def wrapper_async(*args, **kwargs):
                # Handle kwargs passed from function
                cache_reset_not_passed = (
                    "cache_reset" not in kwargs
                    and decorator_kwargs["cache_reset"] is None
                )
                if cache_reset_not_passed and kwargs.get("reset") is not None:
                    warnings.warn(
                        "The 'reset' keyword is deprecated. Use 'cache_reset' instead",
                        FusedDeprecationWarning,
                    )
                    kwargs["cache_reset"] = kwargs["reset"]
                    kwargs.pop("reset", None)

                # Allow passing cache kwargs through fn kwargs. decorator_kwargs are specified from cache decorator
                for k in decorator_kwargs:
                    if k in kwargs:
                        decorator_kwargs[k] = kwargs.pop(k)

                return await _cache_async(
                    func,
                    *args,
                    **decorator_kwargs,
                    **kwargs,
                )

            wrapper_async.__fused_cached_fn = func

            return wrapper_async
        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Handle kwargs passed from function
                cache_reset_not_passed = (
                    "cache_reset" not in kwargs
                    and decorator_kwargs["cache_reset"] is None
                )
                if cache_reset_not_passed and kwargs.get("reset") is not None:
                    warnings.warn(
                        "The 'reset' keyword is deprecated. Use 'cache_reset' instead",
                        FusedDeprecationWarning,
                    )
                    kwargs["cache_reset"] = kwargs["reset"]
                    kwargs.pop("reset", None)
                # Allow passing cache kwargs through fn kwargs. decorator_kwargs are specified from cache decorator
                for k in decorator_kwargs:
                    if k in kwargs:
                        decorator_kwargs[k] = kwargs.pop(k)

                return _cache(
                    func,
                    *args,
                    **decorator_kwargs,
                    **kwargs,
                )

            wrapper.__fused_cached_fn = func

            return wrapper

    if callable(func):  # w/o args
        return decorator(func)
    else:  # w/ args
        return decorator


def cache(
    func: Callable[..., Any] | None = None,
    cache_max_age: str | int = DEFAULT_CACHE_MAX_AGE,
    cache_folder_path: str = "tmp",
    concurrent_lock_timeout: str | int = 120,
    cache_reset: bool | None = None,
    cache_storage: StorageStr | None = None,
    cache_key_exclude: Iterable[str] = None,
    cache_verbose: bool | None = None,
    **kwargs: Any,
) -> Callable[..., Any]:
    """Decorator to cache the return value of a function.

    This function serves as a decorator that can be applied to any function
    to cache its return values. The cache behavior can be customized through
    keyword arguments.

    Args:
        func (Callable, optional): The function to be decorated. If None, this
            returns a partial decorator with the passed keyword arguments.
        cache_max_age: A string with a numbered component and units. Supported units are seconds (s), minutes (m), hours (h), and
            days (d) (e.g. "48h", "10s", etc.).
        cache_folder_path: Folder to append to the configured cache directory.
        concurrent_lock_timeout: Max amount of time in seconds for subsequent concurrent calls to wait for a previous
            concurrent call to finish execution and to write the cache file.
        cache_reset: Ignore `cache_max_age` and overwrite cached result.
        cache_storage: Set where the cache data is stored. Supported values are "auto", "mount" and "local". Auto will
            automatically select the storage location defined in options (mount if it exists, otherwise local) and
            ensures that it exists and is writable. Mount gets shared across executions where local will only be shared
            within the same execution.
        cache_key_exclude: An iterable of parameter names to exclude from the cache key calculation. Useful for
            arguments that do not affect the result of the function and could cause unintended cache expiry (e.g.
            database connection objects)
        cache_verbose: Print a message when a cached result is returned
    Returns:
        Callable: A decorator that, when applied to a function, caches its
        return values according to the specified keyword arguments.

    Examples:
        Use the `@cache` decorator to cache the return value of a function in a custom path.

        ```py
        @cache(path="/tmp/custom_path/")
        def expensive_function():
            # Function implementation goes here
            return result
        ```

        If the output of a cached function changes, for example if remote data is modified,
        it can be reset by running the function with the `cache_reset` keyword argument. Afterward,
        the argument can be cleared.

        ```py
        @cache(path="/tmp/custom_path/", cache_reset=True)
        def expensive_function():
            # Function implementation goes here
            return result
        ```
    """
    return _cache_internal(
        func=func,
        cache_max_age=cache_max_age,
        cache_folder_path=cache_folder_path,
        concurrent_lock_timeout=concurrent_lock_timeout,
        cache_reset=cache_reset,
        cache_storage=cache_storage,
        cache_key_exclude=cache_key_exclude,
        cache_verbose=cache_verbose,
        **kwargs,
    )


T = TypeVar("T")


def cache_call(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Directly calls a function with caching.

    This function directly calls the provided function with the given arguments
    and keyword arguments, caching its return value. The cache used depends on
    the implementation of the `_cache` function.

    Args:
        func (Callable): The function to call and cache its result.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The cached return value of the function.

    Raises:
        Exception: Propagates any exception raised by the function being called
        or the caching mechanism.
    """
    return _cache(func, *args, **kwargs)


async def cache_call_async(
    func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any
) -> T:
    """Asynchronously calls a function with caching.

    Similar to `cache_call`, but for asynchronous functions. This function
    awaits the provided async function, caches its return value, and then
    returns it. The specifics of the caching mechanism depend on the
    implementation of `_cache_async`.

    Args:
        func (Callable): The asynchronous function to call and cache its result.
        *args: Positional arguments to pass to the async function.
        **kwargs: Keyword arguments to pass to the async function.

    Returns:
        The cached return value of the async function.

    Raises:
        Exception: Propagates any exception raised by the async function being
        called or the caching mechanism.

    Examples:
        async def fetch_data(param):
            # Async function implementation goes here
            return data

        # Usage
        result = await cache_call_async(fetch_data, 'example_param')
    """
    return await _cache_async(func, *args, **kwargs)


def _get_cache_base_path(sub_path: str, storage: StorageStr = "auto") -> Path:
    sub_path = sub_path.strip("/")
    # TODO: consider udf name in path once available from Fused global context

    if (
        OPTIONS.cache_directory is not None
        and storage != "auto"
        and not str(OPTIONS.cache_directory).startswith(str(get_writable_dir(storage)))
    ):
        warnings.warn(
            f"Ignoring cache_storage={storage} because `options.cache_directory` is already set."
        )

    base_path = (
        OPTIONS.cache_directory
        if OPTIONS.cache_directory is not None
        else cache_directory(storage)
    )

    return base_path / sub_path


def _get_cache_interface(storage: StorageStr) -> str:
    if storage == "object":
        # e.g. s3 or gs
        prefix = urllib.parse.urlparse(OPTIONS.fd_prefix).scheme
        assert prefix, "fd_prefix is required to be set to use object storage"
        return prefix
    return "filesystem"
