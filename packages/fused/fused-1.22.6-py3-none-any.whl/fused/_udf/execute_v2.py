import ast
import datetime
import time
from contextlib import ExitStack
from typing import Any

import fused
from fused._options import options as OPTIONS
from fused._udf.compile_v2 import compile_udf_and_run_with_kwargs
from fused._udf.state import (
    _isolate_streams,
    decorator_src_override_context,
)
from fused.models.udf import EMPTY_UDF, AnyBaseUdf
from fused.models.udf._eval_result import UdfEvaluationResult


def execute_against_sample(
    udf: AnyBaseUdf,
    input: list[Any],
    validate_imports: bool | None = None,
    _return_response: bool = False,
    cache_max_age: int | None = None,
    **kwargs,
) -> UdfEvaluationResult:
    if udf is EMPTY_UDF:
        raise ValueError("Empty UDF cannot be evaluated. Use `set_udf` to set a UDF.")

    # Validate import statements correspond to valid modules
    validate_imports_whitelist(udf, validate_imports=validate_imports)

    if not OPTIONS.local_engine_cache:
        cache_max_age = 0

    if cache_max_age is None:
        if udf.cache_max_age is not None:
            cache_max_age = udf.cache_max_age
        else:
            cache_max_age = int(datetime.timedelta(days=90).total_seconds())

    # Run UDF
    # TODO capture output
    exception_raised = None
    _output = None
    has_exception = False
    errormsg = None
    exception_class = None
    time_start = time.perf_counter()
    try:
        with _isolate_streams():
            if cache_max_age == 0:
                _output = compile_udf_and_run_with_kwargs(udf, *input, **kwargs)
            else:
                wrapped = fused.cache(
                    compile_udf_and_run_with_kwargs,
                    cache_max_age=cache_max_age,
                    cache_verbose=False,
                )
                _output = wrapped(udf, *input, **kwargs)
    except Exception as exc:
        exception_raised = exc
        has_exception = True
        exception_class = exc.__class__.__name__
        errormsg = f"{exception_class}: {str(exc)}"
        # TODO proper error traceback
        # traceback.print_tb(exc.__traceback__, file=err_buf)
    time_end = time.perf_counter()
    time_taken_seconds = time_end - time_start

    if _return_response:
        return UdfEvaluationResult(
            data=_output,
            udf=udf,
            time_taken_seconds=time_taken_seconds,
            stdout=None,
            stderr=None,
            error_message=errormsg,
            has_exception=has_exception,
            exception_class=exception_class,
        )
    if exception_raised:
        raise exception_raised
    return _output


def execute_for_decorator(udf: AnyBaseUdf) -> AnyBaseUdf:
    """Evaluate a UDF for the purpose of getting the UDF object out of it."""
    # Define custom function in environment

    # This is a stripped-down version of execute_against_sample, above.

    src = udf.code

    exec_globals_locals = {"fused": fused}

    with ExitStack() as stack:
        stack.enter_context(decorator_src_override_context(src))

        # Add headers to sys.meta_path
        if udf.headers is not None:
            for header in udf.headers:
                stack.enter_context(header._register_custom_finder())

        exec(src, exec_globals_locals, exec_globals_locals)

        if udf.entrypoint not in exec_globals_locals:
            raise NameError(
                f"Could not find {udf.entrypoint}. You need to define a UDF with `def {udf.entrypoint}()`."
            )

        _fn = exec_globals_locals[udf.entrypoint]

        return _fn


def validate_imports_whitelist(udf: AnyBaseUdf, validate_imports: bool | None = None):
    # Skip import validation if the option is set
    if not fused.options.default_validate_imports and validate_imports is not True:
        return

    # Skip import validation if not logged in
    if not fused.api.AUTHORIZATION.is_configured():
        return

    from fused._global_api import get_api

    # Get the dependency whitelist from the cached API endpoint
    api = get_api()
    package_dependencies = api.dependency_whitelist()

    # Initialize a list to store the import statements
    import_statements = []

    # Parse the source code into an AST
    tree = ast.parse(udf.code)

    # Traverse the AST to find import statements
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_statements.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            import_statements.append(module_name)

    # Check for unavailable modules
    header_modules = [header.module_name for header in udf.headers]
    fused_modules = ["fused"]  # assume fused is always available
    available_modules = (
        list(package_dependencies["dependency_whitelist"].keys())
        + header_modules
        + fused_modules
    )
    unavailable_modules = []
    for import_statement in import_statements:
        if import_statement.split(".", 1)[0] not in available_modules:
            unavailable_modules.append(import_statement)

    if unavailable_modules:
        raise ValueError(
            f"The following imports in the UDF might not be available: {repr(unavailable_modules)}. Please check the UDF headers and imports and try again."
        )

    # TODO: check major versions for some packages
