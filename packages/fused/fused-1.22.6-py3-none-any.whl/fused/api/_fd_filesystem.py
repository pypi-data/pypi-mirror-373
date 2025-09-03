from pathlib import Path
from urllib.parse import urlparse

import fsspec
from fsspec.implementations.dirfs import DirFileSystem
from fsspec.registry import register_implementation

from fused._global_api import get_api
from fused._options import options as OPTIONS


class FdFileSystem(DirFileSystem):
    protocol = "fd"

    def __init__(self, dirfs_options=None, **storage_options):
        # fused team directory
        # Save an API call when set by rt2 or job2
        if OPTIONS.fd_prefix:
            root = OPTIONS.fd_prefix
            root_parsed = urlparse(root)
        else:
            api = get_api()
            root = api._resolve("fd://")
            root_parsed = urlparse(root)

        # Path operations are done via string appends, so normalize the root path without a trailing slash to avoid
        # inconsistencies.
        scheme, bucket, path = (
            root_parsed.scheme,
            root_parsed.netloc,
            Path(root_parsed.path),
        )
        root = f"{scheme}://{bucket}{path}"

        super().__init__(
            path=root,
            fs=fsspec.filesystem(root_parsed.scheme, **storage_options),
            **(dirfs_options or {}),
        )

    def _join(self, path):
        """Overridden to fix joining absolute and relative paths.

        Since self.path is already treated as the root path, this allows the user to join either path types to
        achieve the same result.

        For the path (regarded as root) <bucket_name>/root_dir/subdir we want to be able to join /dir1 and dir1/ to
        the root path such that we end up with <bucket_name>/root_dir/subdir/dir1

        """
        if isinstance(path, str):
            if not self.path:
                return path
            if not path:
                return self.path
            p_path = Path(self._strip_protocol(path))
            if p_path.is_absolute():
                path = p_path.relative_to("/")
            return str(Path(self.path) / path)
        if isinstance(path, dict):
            return {self._join(_path): value for _path, value in path.items()}
        return [self._join(_path) for _path in path]


register_implementation("fd", FdFileSystem, True)
