from __future__ import annotations

from contextlib import suppress
import typing

from httpc._next_data import NextData, extract_next_data
import httpx
from selectolax.lexbor import LexborHTMLParser as HTMLParser
from selectolax.lexbor import LexborNode as Node

from ._broadcaster import BroadcastList

if typing.TYPE_CHECKING:
    from ._broadcaster import NodeBroadcastList

__all__ = ["ParseTool", "Response"]

T = typing.TypeVar("T")
_ABSENT = object()


class ParseTool:
    __slots__ = "text", "_cache"

    def __init__(self, text: str | None) -> None:
        if text is not None:
            self.text: str = text

    def parse(self, *, new: bool = False, refresh: bool = False) -> HTMLParser:
        if refresh:
            self._cache = HTMLParser(self.text)

        if new:
            return HTMLParser(self.text)

        with suppress(AttributeError):
            return self._cache

        # 위의 코드와 합치면 간결하긴 하지만 text attribute가 없다는 예외가 발생할 경우
        # traceback이 겹쳐서 보기 불편해짐
        self._cache = HTMLParser(self.text)
        return self._cache

    def match(self, query: str, *, new: bool = False) -> NodeBroadcastList:
        return BroadcastList(self.parse(new=new).css(query))  # type: ignore

    @typing.overload
    def single(self, query: str, default: T, *, remain_ok: bool = False, new: bool = False) -> Node | T: ...

    @typing.overload
    def single(self, query: str, *, remain_ok: bool = False, new: bool = False) -> Node: ...

    def single(self, query, default=_ABSENT, *, remain_ok=False, new: bool = False):
        css_result = self.parse(new=new).css(query)
        length = len(css_result)

        if length == 0:
            if default is _ABSENT:
                raise ValueError(f"Query {query!r} matched with no nodes{self._get_url_note()}.")
            else:
                return default
        elif remain_ok or length == 1:
            return css_result[0]
        else:
            raise ValueError(f"Query {query!r} matched with {length} nodes{self._get_url_note()}.")

    def extract_next_data(self, prefix_to_ignore: typing.Container | None = None) -> list[NextData]:
        scripts = [script.text(strip=True) for script in self.match("script")]
        next_data = extract_next_data(scripts, prefix_to_ignore=prefix_to_ignore)
        return next_data

    def next_data(self, *, exclude_prefixed: bool = True) -> dict[str, typing.Any]:
        prefix_to_ignore = ("HL", "I") if exclude_prefixed else None
        next_data = self.extract_next_data(prefix_to_ignore=prefix_to_ignore)
        return {
            data.hexdigit: data.value
            for data in next_data
        }

    def _get_url_note(self) -> str:
        try:
            url = self.url  # type: ignore
        except AttributeError:
            url_note = ""
        else:
            url_note = f" (error from '{url}')"
        return url_note


class Response(httpx.Response, ParseTool):
    _response: httpx.Response

    @classmethod
    def from_httpx(cls, response: httpx.Response) -> Response:
        response.encoding  # type: ignore  # noqa  # AttributeError: 'Headers' object has no attribute '_encoding' 오류를 피하기 위해 불러옴
        self = cls.__new__(cls)
        self.__dict__ = response.__dict__
        self._response = response
        return self
