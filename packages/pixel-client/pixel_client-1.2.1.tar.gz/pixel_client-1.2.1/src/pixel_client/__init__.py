from functools import lru_cache
from importlib.metadata import version
from typing import Literal, Unpack, overload

from ._base import PixelClientAsync, PixelClientKwargs
from ._sync import PixelClient
from .models import *  # noqa: F403
from .settings import PixelApiSettings

__version__ = version("pixel_client")


class PackageUpdateWarning(Warning): ...


def _version_check():
    """
    Check if there is a newer version of the pixel-client package available.
    This function imports the version from the package and checks it against the latest version available on PyPI.
    If the version is not the latest, it raises a warning to the user.
    This function should be called at the start of the application to ensure that the user is aware of any updates.
    Usage:
    ```python
    from pixel_client import _version_check
    _version_check()
    ```
    """
    import warnings
    from importlib.metadata import version

    import httpx
    from packaging.version import parse as parse_version

    current_version = version("pixel_client")

    try:
        response = httpx.get(
            "https://pypi.org/pypi/pixel-client/json",
            timeout=10.0,
        )
        response.raise_for_status()
        latest_version = response.json()["info"]["version"]
    except httpx.RequestError:
        warnings.warn(
            "Could not check for the latest version of pixel-client.",
            PackageUpdateWarning,
            stacklevel=2,  # This ensures the warning points to the caller, not this function
        )
        return

    if parse_version(current_version) < parse_version(latest_version):
        warnings.warn(
            f"A newer version of pixel-client is available: {latest_version}. "
            "Please consider updating with `pip install --upgrade pixel-client`.",
            PackageUpdateWarning,
            stacklevel=2,
        )


@overload
def get_client(
    async_: Literal[False] = ...,
    settings: PixelApiSettings | None = None,
    **kwargs: Unpack[PixelClientKwargs],
) -> PixelClient: ...


@overload
def get_client(
    async_: Literal[True] = ...,
    settings: PixelApiSettings | None = None,
    **kwargs: Unpack[PixelClientKwargs],
) -> PixelClientAsync: ...


def get_client(
    async_: bool = False,
    settings: PixelApiSettings | None = None,
    **kwargs: Unpack[PixelClientKwargs],
) -> PixelClientAsync | PixelClient:
    """
    Get the pixel client.

    Args:
        async_ (bool): Whether to return an asynchronous client.
        settings (PixelApiSettings | None): Settings for the Pixel API client. If None, defaults are used.
        **kwargs: Additional keyword arguments to pass to the client constructor.
    Returns:
        PixelClientAsync | PixelClient: An instance of the Pixel API client, either synchronous or asynchronous.

    Example:
        ```python
        from pixel_client import get_client, PixelApiSettings
        # Settings from environment variables
        async_client = get_client(async_=True)
        # Settings from a .env file, see https://docs.pydantic.dev/latest/concepts/pydantic_settings/#dotenv-env-support
        settings = PixelApiSettings(_env_file="path/to/.env")
        # async_ defaults to False, so this will return a synchronous client
        sync_client = get_client(settings=settings)
        ```

    Note:
        The client is cached and will be reused on subsequent calls, unless the settings change.
    """
    return _cached_get_client(async_, settings or PixelApiSettings(), **kwargs)  # type: ignore


@lru_cache
def _cached_get_client(
    async_: bool, settings: PixelApiSettings, **kwargs: Unpack[PixelClientKwargs]
) -> PixelClientAsync | PixelClient:
    if settings.PIXEL_CLIENT_NO_VERSION_CHECK is False:
        _version_check()
    async_client = PixelClientAsync.from_settings(settings, **kwargs)
    if async_:
        return async_client
    return PixelClient(async_client)
