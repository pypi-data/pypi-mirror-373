import importlib.abc
import importlib.util
import linecache
import sys
from types import CodeType, ModuleType
from typing import Any, Dict, Literal, Optional

import requests
from pydantic import BaseModel, ConfigDict, PrivateAttr
from typing_extensions import override

from fused._formatter.udf import fused_header_repr
from fused._options import options as OPTIONS
from fused._str_utils import is_url


def _compile_with_line_cache(src: str, module_name: str) -> CodeType:
    file_name = f"<module {module_name}>"
    linecache.cache[file_name] = (
        len(src),
        None,
        [line + "\n" for line in src.splitlines()],
        file_name,
    )
    return compile(src, file_name, mode="exec")


class Header(BaseModel):
    """A header represents a reusable source module included with a UDF."""

    module_name: str
    """The name by which the header may be imported"""
    source_code: Optional[str] = None
    """The code of the header module"""
    source_file: Optional[str] = None
    """The name of the original source file"""
    _finder_instance_id: Optional[int] = PrivateAttr(None)
    """The ID of this header's StringModuleFinder instance, used for cleanup."""
    _prev_sys_module: Optional[ModuleType] = PrivateAttr(None)
    """The module object that was previously in sys.modules for this header's name, if any, saved during registration and restored on exit."""

    def _repr_html_(self) -> str:
        return fused_header_repr([self])

    @classmethod
    def from_code(
        cls, module_name: str, source_file: str, source: Literal["disk", "url"] = "disk"
    ):
        """Read a header from a location.

        Args:
            module_name: The name by which the module may be imported
            source_file: Where to read from
            source: Source type, must be `"disk"` (read a file from disk) or `"url"` (read a file from URL)
        """
        if source == "url" or is_url(source_file):
            return cls._read_code_from_url(module_name, source_file)
        elif source == "disk":
            _header = cls._read_code_from_disk(module_name, source_file)
            if _header:
                # del _header.source_file
                # warnings.warn(
                # "The local header path specified in the UDF source might not resolve if this UDF code is ran elsewhere.\
                # Consider setting a remote header.",
                # FusedWarning,
                # )
                pass
            return _header

    @classmethod
    def _read_code_from_disk(cls, module_name, source_file):
        with open(source_file) as file:
            source_code = file.read()

        return cls(
            module_name=module_name, source_file=source_file, source_code=source_code
        )

    @classmethod
    def _read_code_from_url(cls, module_name, source_file):
        r = requests.get(source_file, timeout=OPTIONS.request_timeout)
        r.raise_for_status()
        source_code = r.text
        return cls(
            module_name=module_name, source_file=source_file, source_code=source_code
        )

    def write_code(self):
        # TODO: select between write_code_to_disk and possible write_code_to_gist
        self._write_code_to_disk()

    def write_to_disk(self, path: str):
        raise NotImplementedError

    def _exec(self) -> Dict[str, Any]:
        """
        Execute the header and return it's locals. This is comparable to importing the header.
        """
        import fused

        ret = {"fused": fused}
        try:
            compiled_code = _compile_with_line_cache(
                src=self.source_code, module_name=self.module_name
            )
            exec(compiled_code, ret)
        except SyntaxError as e:
            # If the syntax error is in the header, make sure it gets a different type so the caller knows
            # it wasn't in the UDF itself.
            raise HeaderSyntaxError(e.msg) from e
        return ret

    def _register_custom_finder(self):
        module_name = self.module_name
        source_code = self.source_code

        class StringModuleFinder(importlib.abc.MetaPathFinder):
            @override
            def find_spec(self, fullname, path, target=None):
                if fullname == module_name:
                    loader = StringModuleLoader(module_name, source_code)
                    spec = importlib.util.spec_from_loader(module_name, loader)
                    return spec
                return None

        # Register the custom finder
        finder_instance = StringModuleFinder()
        self._finder_instance_id = id(finder_instance)
        sys.meta_path.insert(0, finder_instance)

        # Save previous module and reset modules cache
        try:
            self._prev_sys_module = sys.modules.pop(module_name, None)
        except Exception:  # noqa: F841
            pass
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Reset modules
        try:
            sys.meta_path = [
                importer
                for importer in sys.meta_path
                if id(importer) != self._finder_instance_id
            ]
            if self._prev_sys_module:
                sys.modules[self.module_name] = self._prev_sys_module
            else:
                del sys.modules[self.module_name]
        except Exception:  # noqa: F841
            pass

    def _generate_cell_code(self):
        # If remote, comment remote path. Otherwise, set %%file.
        if self.source_file and is_url(self.source_file):
            file_name = self.module_name + ".py"
            return f"%%file {file_name}\n# Remote file: {self.source_file}\n{self.source_code}"
        else:
            file_name = self.source_file or self.module_name + ".py"
            return f"%%file {file_name}\n{self.source_code}"

    @override
    def __getstate__(self):
        state = super().__getstate__()

        new_state = state.copy()
        if "_prev_sys_module" in new_state:
            del new_state["_prev_sys_module"]

        return new_state

    @override
    def __setstate__(
        self,
        state: dict[str, Any],
    ) -> None:
        super().__setstate__(state)

    def __deepcopy__(self, memo=None):
        # Do not use model_copy as it will call __deepcopy__.
        # This will cause issues with _prev_sys_module.
        # TODO: Move this state off the header object itself into a specific context object.
        return Header.model_validate(self.model_dump())

    model_config = ConfigDict(arbitrary_types_allowed=True)


class StringModuleLoader(importlib.abc.Loader):
    def __init__(self, module_name, source_code):
        self.module_name = module_name
        self.source_code = source_code

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        import fused

        module.__dict__["fused"] = fused
        try:
            compiled_code = _compile_with_line_cache(
                src=self.source_code, module_name=self.module_name
            )
            exec(compiled_code, module.__dict__)
        except SyntaxError as e:
            # If the syntax error is in the header, make sure it gets a different type so the caller knows
            # it wasn't in the UDF itself.
            raise HeaderSyntaxError(
                f"{e.msg}: File {e.filename} at line {e.lineno}, position {e.offset}: {e.text.rstrip()}"
            ) from e


class HeaderSyntaxError(Exception):
    pass
