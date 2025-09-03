from typing import Any, Iterable, Iterator, Optional, Union

from fused._udf.context import get_global_context


class SecretsManager:
    """Access secrets stored in the Fused backend for the current kernel."""

    _client_id: Optional[str] = None
    """Which instance (kernel) to retrieve and set secrets on."""

    def __init__(self, client_id: Optional[str] = None):
        """ """
        self._client_id = client_id

    def __getattribute__(self, key: str) -> Union[Any, str]:
        try:
            return super().__getattribute__(key)
        except AttributeError:
            try:
                return self[key]
            # Note that we need to raise an AttributeError, **not a KeyError** so that
            # IPython's _repr_html_ works here
            except KeyError:
                raise AttributeError(
                    f"object of type {type(self).__name__} has no attribute {key}"
                ) from None

    def __getitem__(self, key: str) -> str:
        context = get_global_context()
        return context.get_secret(key=key, client_id=self._client_id)

    def __dir__(self) -> Iterable[str]:
        context = get_global_context()
        return context.list_secrets(client_id=self._client_id)

    def __iter__(self) -> Iterator[str]:
        yield from dir(self)

    def __len__(self) -> int:
        return len(dir(self))

    def __setitem__(self, key: str, value: str):
        context = get_global_context()
        return context.set_secret(key=key, value=value, client_id=self._client_id)

    def __delitem__(self, key: str):
        context = get_global_context()
        return context.delete_secret(key=key, client_id=self._client_id)


secrets = SecretsManager()
"""
Access secrets stored in the Fused backend for the current kernel.

Examples:
    Retrieve a secret value:
    ```py
    my_secret_value = fused.secrets["my_secret_key"]
    ```

    or:
    ```py
    my_secret_value = fused.secrets.my_secret_key
    ```

    List all secret keys:
    ```py
    print(dir(fused.secrets))
    ```
"""
