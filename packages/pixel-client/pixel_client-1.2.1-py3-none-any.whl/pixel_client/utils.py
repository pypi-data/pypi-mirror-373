import logging
import asyncio
from pathlib import Path
import base64
import httpx
from typing import IO, Awaitable
import hashlib
from typing import Coroutine, Any, TypeVar, Iterator, AsyncGenerator
from contextlib import contextmanager


T = TypeVar("T")


def run_sync(coro: Coroutine[Any, Any, T] | Awaitable[T]) -> T:
    """
    Run an async function synchronously.
    """
    if asyncio.iscoroutinefunction(coro):
        raise ValueError("method is already synchronous")
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


def iter_over_async(async_gen: AsyncGenerator[T, None]) -> Iterator[T]:
    """
    Iterate over an async generator synchronously.
    """
    async_iter = async_gen.__aiter__()
    try:
        while True:
            yield run_sync(async_iter.__anext__())
    except StopAsyncIteration:
        pass


def chunks(lst: list[T], n: int) -> Iterator[list[T]]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


@contextmanager
def silence_logger(logger: logging.Logger | None = None):
    """
    Temporarily disable a logger.
    """
    logger = logger or logging.getLogger()
    try:
        logger.disabled = True
        yield
    finally:
        logger.disabled = False


def calculate_md5_base64_from_file(file_path: Path) -> str:
    """
    Calculate the MD5 hash of a file and return it as a base64 encoded string.
    """
    with open(file_path, "rb") as f:
        return calculate_md5_base64(f.read())


def calculate_md5_base64(content: bytes) -> str:
    """
    Calculate the MD5 hash of a byte string and return it as a base64 encoded string.
    """
    return base64.b64encode(hashlib.md5(content).digest()).decode()


def iter_file_parts(
    file_path: Path, part_size: int
) -> Iterator[tuple[int, str, bytes]]:
    """
    Iterate over a file in parts. Each part is a tuple of the part size, the MD5 hash of the part, and the part itself.
    """
    with open(file_path, "rb") as f:
        while True:
            part = f.read(part_size)
            if not part:
                break
            yield len(part), calculate_md5_base64(part), part


def download_from_url(url: str, out: IO[bytes]) -> None:
    """
    Download a file from a URL and write it to a file-like object.
    """
    with httpx.stream("GET", url) as response:
        for chunk in response.iter_bytes():
            out.write(chunk)
