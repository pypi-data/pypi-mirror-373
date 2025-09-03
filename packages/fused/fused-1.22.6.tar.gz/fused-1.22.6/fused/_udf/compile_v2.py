import inspect
import linecache
import warnings
from contextlib import ExitStack
from typing import Any, Callable, Iterable, Mapping

from fused._udf.state import decorator_import_globals_disable_context
from fused.core._impl._context_impl import context_in_batch
from fused.models.udf import MockUdfInput, Udf

has_line_profiler = False
try:
    import line_profiler  # noqa: F401

    has_line_profiler = True
except ImportError:
    pass


def _compile_and_get_local(udf: Udf, profile_output: dict | None = None) -> Callable:
    """
    Compile and exec the UDF's code, returning a callable that can be used
    to run the UDF.

    - Compile the UDF code ensuring proper line numbers
    - Exec the code in a context that includes the `fused` module
    - Extract the entrypoint function from the exec'd code
    - Wrap the entrypoint function to include preprocessing of (keyword) arguments
      (coerce based on the type annotations in the UDF signature)
    """
    import fused
    from fused._udf.args import coerce_arg
    from fused.warnings import FusedDeprecationWarning, FusedImportWarning

    code = udf.code
    local_name = udf.entrypoint

    # Ensure stack traces, getsource, etc work correctly with the exec'd code:
    compile_name = f"<udf {local_name}>"
    linecache.cache[compile_name] = (
        len(code),
        None,
        [line + "\n" for line in code.splitlines()],
        compile_name,
    )

    # Contextual reading: eval vs exec vs compile.
    # https://stackoverflow.com/questions/2220699/whats-the-difference-between-eval-exec-and-compile
    # mode="exec" is used to compile the code in the form of a module.
    compiled_python = compile(code, compile_name, mode="exec")

    # At this point, the compiled_python code could look like this in bytecode terms:
    #
    #   @fused.udf
    #   def udf():
    #       print("hello world")
    #
    # And when we exec the bytecode object, it injects the udf into the
    # exec_globals_locals below.
    def entrypoint_wrapper(*args, **kwargs):
        exec_globals_locals = {"fused": fused}
        """
        exec_globals_locals must be the same exact reference, or else the following will crash:
        In [10]: exec('''
        ...: import pandas as pd
        ...:
        ...: def aaa():
        ...:   print(pd.DataFrame())
        ...:
        ...: aaa()
        ...: ''', {}, {})
        See here for why exec_globals_locals must be the same reference:
        https://docs.python.org/3/library/functions.html#exec
        """
        exec(compiled_python, exec_globals_locals, exec_globals_locals)
        if local_name not in exec_globals_locals:
            raise NameError(
                f"Could not find {local_name}. You need to define a UDF with `def {local_name}()`."
            )
        # Reference to a callable or UDF object
        entrypoint = exec_globals_locals[local_name]

        # Ensure the entrypoint is something callable (not a UDF object)
        if isinstance(entrypoint, Udf):
            entrypoint = entrypoint._nested_callable

        kwargs_to_pass = udf.parameters or {}

        # Fixup parameters with special meaning
        # kwargs comes from try_running_partition_function in udf.py, this just confirms that since this function
        # doesn't have the parameters explicitly defined.
        signature = inspect.signature(entrypoint)
        param_names = signature.parameters.keys()
        if kwargs is not None:
            for key, value in kwargs.items():
                if key in param_names:
                    kwargs_to_pass[key] = value

        input_kwargs = {}
        input_as_udf_args = kwargs["input"].as_udf_args() if "input" in kwargs else {}
        for key, data in input_as_udf_args.items():
            param = signature.parameters.get(key)
            if param is not None:
                input_kwargs[key] = coerce_arg(data, param)

        # Temp fix for backwards compatibility: try to pass bbox as first positional param if 'bbox' arg not defined
        if (
            "bounds" not in input_kwargs
            and len(args) == 0
            and "bounds" in input_as_udf_args
            and len(signature.parameters) > 0
        ):
            bounds = input_as_udf_args["bounds"]
            param = None

            # first check for a bbox keyword argument
            if "bbox" in signature.parameters and "bbox" not in kwargs_to_pass:
                param = signature.parameters["bbox"]
                kwargs_to_pass["bbox"] = bounds

            # otherwise pass to first positional argument
            else:
                param = list(signature.parameters.values())[0]
                # Check to ensure that the user didn't already provide this value as a kwarg
                if param in kwargs_to_pass:
                    raise TypeError(f"Multiple values provided for argument '{param}'.")
                kwargs_to_pass[param.name] = coerce_arg(bounds, param)

            if param:
                warnings.warn(
                    "The tile bounds are being passed in through the argument "
                    f"'{param.name}'. This behavior is deprecated in favor of "
                    "using the 'bounds' argument explicitly. "
                    f"Consider renaming '{param.name}' to 'bounds'.",
                    FusedDeprecationWarning,
                )

        if context_in_batch():
            converted_args = convert_args_to_kwargs(entrypoint, args)
            kwargs_to_pass.update(converted_args)
        elif args:
            raise ValueError(
                "Unhandled UDF use-case passing args. Calling code needs to adapt to pass args as kwargs."
            )

        has_kwargs = any(
            [
                signature.parameters[param_name].kind == inspect.Parameter.VAR_KEYWORD
                for param_name in signature.parameters
            ]
        )
        reformatted_kwargs_to_pass = {
            key: coerce_arg(
                arg,
                signature.parameters.get(key),
                default_annotation=(
                    None if key in signature.parameters and key != "input" else str
                ),
            )
            for key, arg in kwargs_to_pass.items()
            # If this corresponds to a parameter on the UDF, then pass it in.
            # Otherwise, simply ignore it.
            if (key in signature.parameters and key != "input") or has_kwargs
        }

        if profile_output is not None and has_line_profiler:
            from ._line_profiler_vendored import LineProfiler

            profile = LineProfiler()

            for key, val_maybe_fn in exec_globals_locals.items():
                if (
                    inspect.isfunction(val_maybe_fn)
                    and val_maybe_fn.__globals__ is exec_globals_locals
                ):
                    exec_globals_locals[key] = profile(val_maybe_fn)
                elif (  # Decorated functions
                    inspect.isfunction(val_maybe_fn)
                    and hasattr(val_maybe_fn, "__wrapped__")
                    and val_maybe_fn.__wrapped__.__globals__ is exec_globals_locals
                ):
                    val_maybe_fn.__wrapped__ = profile(val_maybe_fn.__wrapped__)
                    exec_globals_locals[key] = val_maybe_fn
            try:
                return profile(entrypoint)(**input_kwargs, **reformatted_kwargs_to_pass)
            finally:
                profile_output["stats"] = profile.get_stats()
        else:
            if profile_output is not None:
                warnings.warn(
                    "`profile` option is being ignored because `line_profiler` is not installed.",
                    FusedImportWarning,
                )
            return entrypoint(**input_kwargs, **reformatted_kwargs_to_pass)

    return entrypoint_wrapper


def convert_args_to_kwargs(udf_fn: Callable, args: tuple) -> dict:
    """Convert batch args into kwargs

    A single positional arg can only be passed when using arg_list. This function handles converting positional
    arguments to keyword arguments for the case where a user wants a single dict to be used as keyword arguments for
    the entire UDF. If the input dict does not match the UDF signature, we fall back to passing the dict to the first
    parameter.
    """
    signature = inspect.signature(udf_fn)
    kwargs = {}
    if args:
        # Treat dict values as kwargs if keys are a subset of the parameter names
        if isinstance(args[0], dict) and args[0].keys() <= signature.parameters.keys():
            return args[0]

        first_param_name = None
        for name in list(signature.parameters.keys()):
            first_param_name = name
            break
        if first_param_name:
            kwargs = {first_param_name: args[0]}

    return kwargs


def compile_udf_and_run_v2_simple(
    code: Udf,
    args: Iterable[Any] = (),
    kwargs: Mapping[str, Any] | None = None,
):
    from fused._udf.state import (
        decorator_src_override_context,
        decorator_udf_override_context,
    )

    with ExitStack() as stack:
        if code.headers is not None:
            for header in code.headers:
                stack.enter_context(header._register_custom_finder())

        # Without this the UDF object will only get the function it is wrapping.
        # Because then that fn cannot reference anythng else in the UDF.
        stack.enter_context(decorator_src_override_context(code.code))
        # Without this the UDF object will only get the code, but not any of the
        # other fields on the UDF object
        stack.enter_context(decorator_udf_override_context(code))

        entrypoint = _compile_and_get_local(code)
        kwargs_to_pass = kwargs if kwargs else {}
        return entrypoint(*args, **kwargs_to_pass)


def compile_udf_and_run_v3(
    code: Udf,
    input: MockUdfInput,
    profile_output: dict | None = None,
):
    from fused._udf.state import (
        decorator_src_override_context,
        decorator_udf_override_context,
    )

    with ExitStack() as stack:
        # UDF's that are created inside a running UDF.
        if code.headers is not None:
            # Python modules.
            for header in code.headers:
                # Needed to hack imports.
                #
                # We inject the whole UDF object below so we do not need to
                # enter these headers into the context here.
                stack.enter_context(header._register_custom_finder())

        # Without this the UDF object will only get the function it is wrapping.
        # Because then that fn cannot reference anythng else in the UDF.
        stack.enter_context(decorator_src_override_context(code.code))
        # Without this the UDF object will only get the code, but not any of the
        # other fields on the UDF object
        stack.enter_context(decorator_udf_override_context(code))
        # Without this the UDF will try to import its own globals during execution.
        # We want to suppress this as we're already executing the function.
        stack.enter_context(decorator_import_globals_disable_context())

        # entrypoint is either an object (wrapping another UDF) or a function.
        # Ensure that from this point onwards, entrypoint is always a function.
        entrypoint = _compile_and_get_local(code, profile_output=profile_output)
        result = entrypoint(input=input)

    return result


def compile_udf_and_run_with_kwargs(udf: Udf, *args, **kwargs):
    udf = udf.model_copy(deep=True)
    udf.parameters = {
        **(udf.parameters if udf.parameters else {}),
        **kwargs,
    }

    if len(args) == 0:
        input = MockUdfInput(None)
    elif len(args) == 1:
        input = MockUdfInput(args[0])
    else:
        raise ValueError(
            "Unexpected number of positional arguments to UDF. Pass keyword arguments instead."
        )
    result = compile_udf_and_run_v3(udf, input=input)

    return result
