from __future__ import annotations

import json
import os
import pickle
import sqlite3
import typing
from collections.abc import MutableMapping
from contextlib import closing, suppress
from pathlib import Path

import httpx


class DBError(OSError):
    pass


_ERR_CLOSED = "DBM object has already been closed"
_ERR_REINIT = "DBM object does not support reinitialization"

if typing.TYPE_CHECKING:
    RequestTuple = tuple[str, str, str, bytes]
    NoHeadersRequestTuple = tuple[str, str, bytes]


class TransactionDatabase(MutableMapping[httpx.Request, httpx.Response]):
    _MEDIA_TYPES = ("image/", "video/", "audio/")

    def __init__(
        self,
        path: os.PathLike | str | bytes,
        table: str,
        *,
        flag: typing.Literal["r", "w", "c", "n"] = "c",
        mode: int = 0o666,
        protocol: int = pickle.DEFAULT_PROTOCOL,
        distinguish_headers: bool = False,
        compress_response: bool = False,
        migrate_old_database: bool = True,
    ) -> None:
        self._protocol = protocol
        # 주의: distinguish_headers를 사용할 때는 한 테이블에 대해 항상 일관적일 것.
        # 데이터를 저장할 때 distinguish_headers가 True이면,
        # False일 때 동일한 데이터로 간주되는 두 요청이 다른 데이터로 중복 저장될 수 있다.
        self.distinguish_headers = distinguish_headers
        self.compress_response = compress_response
        # 미디어 파일들은 압축률이 좀 낮음
        # 실제 내부 데이터베이스를 분석한 결과
        # 압축 안 함: 589MB
        # 미디어 파일이 아닌 것만 압축함: 572MB(-17MB)
        # 모두 압축함: 551MB(-38MB)
        # 즉, 미디어 파일을 용량이 줄어들긴 하나 그 압축률이 그렇게 크진 않다.
        # 장단이 있으니 잘 생각해 보자.
        #
        # 조금 더 깊게 분석해 보자.
        # 위의 데이터는 데이터베이스 자체 크기를 재는 무식한 방법으로 잰 것이다.
        # 실제로 데이터가 어떻게 압축되었는지를 좀 더 자세히 확인하려면 어떻게 해야 할까?
        # 우선 전체 response의 크기를 재고, 미디어를 압축했을 때의 response의 크기를 재고,
        # 미디어가 아닌 것을 압축했을 때의 response의 크기를 재고, 이에 따라 압축률을 구하면 된다.
        #
        # 그렇게 계산하면 아래와 같은 결과가 나온다.
        # 미디어가 아닌 것의 압축률: 60.78%
        # 미디어의 압축률: 96.04%
        # 모두 압축 시 압축률: 93.38%
        #
        # 즉, 나의 데이터베이스에 미디어인 것이 많아서 압축률이 구려보이고, 실제보다 미디어의 압축률이
        # 커보이지만, 실제로는 미디어는 압축이 거의 안 되는 수준이고, 미디어가 아닌 경우에는 괄목한 압축률을 보인다.
        # 따라서 compress_media는 False로 놓는 것이 대체로 맞을 것이다.
        self.compress_media = False

        if self.compress_response:
            import zstd

            self.zstd = zstd
        else:
            try:
                import zstd
            except ModuleNotFoundError:
                pass
            else:
                self.zstd = zstd

        if hasattr(self, "_cx"):
            raise DBError(_ERR_REINIT)

        path = Path(os.fsdecode(path))
        match flag:
            case "r":
                flagged = "ro"
            case "w":
                flagged = "rw"
            case "c":
                flagged = "rwc"
                path.touch(mode=mode, exist_ok=True)
            case "n":
                flagged = "rwc"
                path.unlink(missing_ok=True)
                path.touch(mode=mode)
            case _:
                raise ValueError(f"Flag must be one of 'r', 'w', 'c', or 'n', not {flag!r}")

        # We use the URI format when opening the database.
        uri = self._normalize_uri(path)
        uri = f"{uri}?mode={flagged}"

        try:
            self._cx = sqlite3.connect(uri, autocommit=True, uri=True)
        except sqlite3.Error as exc:
            raise DBError(str(exc)) from None

        # This is an optimization only; it's ok if it fails.
        with suppress(sqlite3.OperationalError):
            self._cx.execute("PRAGMA journal_mode = wal")

        self._build_queries(table)

        if flagged == "rwc":
            self._execute(self._build_table)

        if migrate_old_database:
            with suppress(DBError):
                self._execute(self._add_compressed_column)

    def _execute(self, *args, **kwargs):
        if not self._cx:
            raise DBError(_ERR_CLOSED)
        try:
            return closing(self._cx.execute(*args, **kwargs))
        except sqlite3.Error as exc:
            raise DBError(str(exc)) from None

    def _build_queries(self, table: str) -> None:
        if not table.isidentifier():
            raise ValueError(f"Table name must be an identifier, not {table!r}")
        if table.startswith("sqlite_"):
            raise ValueError("Table name should not start with 'sqlite_', since it's reserved for internal use in sqlite")

        self._build_table = f"""
        CREATE TABLE IF NOT EXISTS {table} (
            method TEXT NOT NULL,
            url TEXT NOT NULL,
            headers TEXT NOT NULL,
            content BLOB NOT NULL,
            response BLOB NOT NULL,
            compressed BOOLEAN NOT NULL DEFAULT FALSE
        )
        """
        # TODO: 적용하기
        self._build_index = f"""
        CREATE INDEX IF NOT EXISTS {table}_idx (method, url, content)
        """
        self._get_size = f"SELECT COUNT() FROM {table}"
        self._lookup_key = f"""
        SELECT * FROM {table} WHERE (
            method = CAST(? AS TEXT)
            AND url = CAST(? AS TEXT)
            AND content = CAST(? AS BLOB)
        )
        """
        self._lookup_key_with_headers = f"""
        SELECT * FROM {table} WHERE (
            method = CAST(? AS TEXT)
            AND url = CAST(? AS TEXT)
            AND json(headers) = json(CAST(? AS TEXT))
            AND content = CAST(? AS BLOB)
        )
        """
        self._store_kv = f"""
        INSERT INTO {table} (method, url, headers, content, response, compressed) VALUES (
            CAST(? AS TEXT), CAST(? AS TEXT), CAST(? AS TEXT), CAST(? AS BLOB), CAST(? AS BLOB), CAST(? AS BOOLEAN)
        )
        """
        self._delete_key = f"""DELETE FROM {table} WHERE (
            method = CAST(? AS TEXT)
            AND url = CAST(? AS TEXT)
            AND content = CAST(? AS BLOB)
        )"""
        self._delete_key_with_headers = f"""DELETE FROM {table} WHERE (
            method = CAST(? AS TEXT)
            AND url = CAST(? AS TEXT)
            AND json(headers) = json(CAST(? AS TEXT))
            AND content = CAST(? AS BLOB)
        )"""
        self._iter_keys = f"SELECT (method, url, headers, content) FROM {table}"
        self._drop_table = f"DROP TABLE {table}"
        self._add_compressed_column = f"ALTER TABLE {table} ADD COLUMN compressed BOOLEAN NOT NULL DEFAULT FALSE"
        self._iter_uncompressed = f"SELECT ROWID, response FROM {table} WHERE compressed == FALSE"
        self._update_uncompressed = f"UPDATE {table} SET response = ?, compressed = ? WHERE ROWID = ?"

    @staticmethod
    def _normalize_uri(path: Path) -> str:
        uri = path.absolute().as_uri()
        while "//" in uri:
            uri = uri.replace("//", "/")
        return uri

    def _prepare_response(self, response: httpx.Response) -> tuple[bytes, bool]:
        response_dumped = pickle.dumps(response, protocol=self._protocol)
        if self.compress_response and self.compress_media:
            compress = True
        else:
            content_type: str = response.headers.get("Content-Type", "")
            compress = content_type[:6] not in self._MEDIA_TYPES

        if compress:
            response_dumped = self.zstd.compress(response_dumped)

        return response_dumped, compress

    def _restore_response(self, response: bytes, compressed: bool | None = None) -> httpx.Response:
        compressed = compressed if compressed is not None else self.compress_response
        if compressed:
            return pickle.loads(self.zstd.decompress(response))
        else:
            return pickle.loads(response)

    @staticmethod
    def _disassemble_request(request: httpx.Request) -> RequestTuple:
        return request.method, str(request.url), json.dumps(dict(request.headers)), request.content

    @staticmethod
    def _disassemble_request_without_headers(request: httpx.Request) -> NoHeadersRequestTuple:
        return request.method, str(request.url), request.content

    @staticmethod
    def _assemble_request(request_tuple: RequestTuple) -> httpx.Request:
        method, url, headers, content = request_tuple
        return httpx.Request(method, url, headers=json.loads(headers), content=content)

    def __len__(self) -> int:
        with self._execute(self._get_size) as cu:
            row = cu.fetchone()
        return row[0]

    def __getitem__(self, request: httpx.Request) -> httpx.Response:
        if self.distinguish_headers:
            with self._execute(self._lookup_key_with_headers, self._disassemble_request(request)) as cu:
                row = cu.fetchone()
        else:
            with self._execute(self._lookup_key, self._disassemble_request_without_headers(request)) as cu:
                row = cu.fetchone()
        if not row:
            raise KeyError(request)

        method, url, headers, content, response, compressed = row
        return self._restore_response(response, compressed)

    def __setitem__(self, request: httpx.Request, response: httpx.Response) -> None:
        with suppress(KeyError):
            del self[request]
        self._execute(self._store_kv, (*self._disassemble_request(request), *self._prepare_response(response)))

    def __delitem__(self, request: httpx.Request) -> None:
        if self.distinguish_headers:
            with self._execute(self._delete_key_with_headers, self._disassemble_request(request)) as cu:
                if not cu.rowcount:
                    raise KeyError(request)
        else:
            with self._execute(self._delete_key, self._disassemble_request_without_headers(request)) as cu:
                if not cu.rowcount:
                    raise KeyError(request)

    def __iter__(self) -> typing.Iterator[httpx.Request]:
        try:
            with self._execute(self._iter_keys) as cu:
                for row in cu:
                    yield self._assemble_request(row)
        except sqlite3.Error as exc:
            raise DBError(str(exc)) from None

    def compress_all(self, force: bool = False) -> None:
        if not self.compress_response:
            raise ValueError("Compression is disabled")

        with self._execute(self._iter_uncompressed) as cu:
            for row in cu:
                rowid, response = row
                if force or self.compress_media:
                    data = self.zstd.compress(response)
                    compressed = True
                else:
                    data, compressed = self._prepare_response(self._restore_response(response, compressed=False))
                self._execute(self._update_uncompressed, (data, compressed, rowid))

    def close(self) -> None:
        if self._cx:
            self._cx.close()
            self._cx = None

    def drop(self) -> None:
        try:
            self._execute(self._drop_table)
        except sqlite3.Error as exc:
            raise DBError(str(exc)) from None

    def keys(self) -> list[httpx.Request]:
        return list(super().keys())

    def __enter__(self) -> typing.Self:
        return self

    def __exit__(self, *_) -> None:
        self.close()
