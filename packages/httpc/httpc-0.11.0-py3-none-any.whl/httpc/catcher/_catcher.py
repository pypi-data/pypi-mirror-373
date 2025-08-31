import logging
import ssl
from contextlib import contextmanager, suppress
from os import PathLike
from typing import Literal

import httpx

from ._db import TransactionDatabase

VerifyType = ssl.SSLContext | str | bool
PathType = PathLike | str | bytes
ContentKey = tuple[str, str, bytes]
ModeType = Literal["store", "use", "hybrid", "passive"]

DEFAULT_LOGGER = logging.getLogger(__name__)
_httpx_installed = False
_httpc_installed = False


class RequestNotFoundError(ValueError):
    request: httpx.Request

    @classmethod
    def from_request(cls, request: httpx.Request):
        method = "" if request.method == "GET" else request.method + " "
        content = request.content
        if not content:
            self = cls(f"There's no stored response for a {method}response for {request.url}")
        elif len(content) <= 20:
            self = cls(f"There's no stored response for a {method}response for {request.url} (with content: {content!r})")
        else:
            self = cls(f"There's no stored response for a {method}response for {request.url} (with {len(content)} length content)")

        self.request = request
        return self


class AsyncCatcherTransport(httpx.AsyncHTTPTransport):
    logger = DEFAULT_LOGGER
    valid_modes = "store", "use", "hybrid", "passive"

    def __init__(
        self,
        db: TransactionDatabase,
        mode: ModeType,
        *,
        verify: VerifyType | None = None,
        **kwargs,
    ) -> None:
        if mode not in self.valid_modes:
            raise ValueError(f"mode should be within {self.valid_modes}, not {mode!r}.")

        verify = ssl.create_default_context() if verify is None else verify
        super().__init__(verify=verify, **kwargs)
        self.db = db
        self.mode = mode

    @classmethod
    @contextmanager
    def with_db(
        cls,
        db_path: PathType,
        mode: ModeType,
        table_name: str = "transactions",
        *,
        distinguish_headers: bool = False,
        compress_response: bool = False,
        migrate_old_database: bool = True,
    ):
        with TransactionDatabase(
            db_path,
            table_name,
            flag="c",
            distinguish_headers=distinguish_headers,
            compress_response=compress_response,
            migrate_old_database=migrate_old_database,
        ) as db:
            yield cls(db=db, mode=mode)

    async def store_async_requests(self, request: httpx.Request, response: httpx.Response) -> None:
        # content에 대한 fetching이 무조건 끝나도록 강제함.
        # 대부분의 경우에는 flushing만으로도 충분하지만
        # content와 await 사이가 remote한 아주 일부 경우 (썸네일 다운로드 등) flushing으로 부족함.
        request.read()
        await response.aread()
        self.db[request] = response

    def find_request(self, request: httpx.Request) -> httpx.Response:
        try:
            response = self.db[request]
        except KeyError:
            raise RequestNotFoundError.from_request(request) from None

        response._request = request
        # response.stream = None
        return response

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        if self.mode == "use":
            await request.aread()
            return self.find_request(request)

        if self.mode == "hybrid":
            with suppress(RequestNotFoundError):
                await request.aread()
                return self.find_request(request)

        response = await super().handle_async_request(request)
        if self.mode != "passive":
            await self.store_async_requests(request, response)

        return response


def install_httpx(db_path: PathType, mode: ModeType):
    global _httpx_installed
    if _httpx_installed:
        return

    import atexit

    import httpx

    transport_initializer = AsyncCatcherTransport.with_db(db_path, mode)
    transport = transport_initializer.__enter__()
    atexit.register(transport_initializer.__exit__, None, None, None)
    # monkey patching transport
    httpx.AsyncClient.__init__.__kwdefaults__["transport"] = transport  # type: ignore

    _httpx_installed = True


def install_httpc(db_path: PathType, mode: ModeType):
    global _httpc_installed
    if _httpc_installed:
        return

    import atexit

    import httpc

    transport_initializer = AsyncCatcherTransport.with_db(db_path, mode)
    transport = transport_initializer.__enter__()
    atexit.register(transport_initializer.__exit__, None, None, None)
    # monkey patching transport
    httpc.AsyncClient.__init__.__kwdefaults__["transport"] = transport  # type: ignore

    _httpc_installed = True
