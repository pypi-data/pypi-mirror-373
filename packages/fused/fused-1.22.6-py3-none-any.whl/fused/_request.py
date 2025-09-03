from __future__ import annotations

from contextlib import contextmanager
from http import HTTPStatus

from aiohttp import ClientResponse, ClientResponseError
from requests import HTTPError, Response, Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from fused._options import options as OPTIONS


def raise_for_status(r: Response):
    """
    A wrapper around Response.raise_for_status to give more information on 422.
    """
    # Look for an error message from model parsing
    if r.status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
        error_msg = r.json()
        raise HTTPError(error_msg, response=r)

    # Look for a Fused error message
    if 400 <= r.status_code < 600:
        to_raise: Exception | None = None
        try:
            if r.headers["Content-Type"] == "application/json":
                error_msg = r.json()
                if "message" in error_msg:
                    error_msg = error_msg["message"]
                to_raise = HTTPError(error_msg, response=r)
        except:  # noqa: E722
            # Fall through to raise_for_status, below
            pass
        if to_raise is not None:
            raise to_raise

    r.raise_for_status()


async def raise_for_status_async(r: ClientResponse):
    # Look for an error message from model parsing

    if r.status == HTTPStatus.UNPROCESSABLE_ENTITY:
        error_msg = await r.json()
        raise ClientResponseError(
            request_info=r.request_info,
            status=r.status,
            message=error_msg,
            headers=r.headers,
            history=r.history,
        )

    # Look for a Fused error message
    if 400 <= r.status < 600:
        to_raise: Exception | None = None
        try:
            if r.headers["Content-Type"] == "application/json":
                error_msg = await r.json()
                if "message" in error_msg:
                    error_msg = error_msg["message"]
                to_raise = ClientResponseError(
                    request_info=r.request_info,
                    status=r.status,
                    message=error_msg,
                    headers=r.headers,
                    history=r.history,
                )
        except:  # noqa: E722
            # Fall through to raise_for_status, below
            pass
        if to_raise is not None:
            raise to_raise

    r.raise_for_status()


default_retry_strategy = Retry(
    total=OPTIONS.request_max_retries,
    status_forcelist=[502, 503],
    backoff_factor=OPTIONS.request_retry_base_delay,
    allowed_methods=["HEAD", "GET", "OPTIONS", "PUT", "POST", "DELETE", "PATCH"],
)


@contextmanager
def session_with_retries(
    total_retries: int | None = None,
    backoff_factor: float | None = None,
):
    """
    Context manager that provides a Session with retry logic.

    :param total_retries: Total number of retries to allow.
    :param backoff_factor: A backoff factor (waiting time) to apply between attempts.
    """
    total_retries = total_retries or OPTIONS.request_max_retries
    backoff_factor = backoff_factor or OPTIONS.request_retry_base_delay

    session = Session()
    retry_strategy = Retry(
        total=total_retries,
        status_forcelist=[502, 503],
        backoff_factor=backoff_factor,
        allowed_methods=["HEAD", "GET", "OPTIONS", "PUT", "POST", "DELETE", "PATCH"],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    try:
        yield session
    finally:
        session.close()
