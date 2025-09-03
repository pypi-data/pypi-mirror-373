from typing import Any, Dict


class MockUdfInput:
    def __init__(self, data: Any) -> None:
        self._data = data

    def as_udf_args(self) -> Dict[str, Any]:
        kwargs = {}
        if self._data is not None:
            kwargs["bounds"] = self._data

        return kwargs
