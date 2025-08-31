from __future__ import annotations

import logging
from abc import abstractmethod

__version__ = "0.11.0"

logger = logging.getLogger("httpc")

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "ko-KR,ko;q=0.9",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version-list": '"Chromium";v="134.0.6998.89", "Not:A-Brand";v="24.0.0.0", "Google Chrome";v="134.0.6998.89"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"19.0.0"',
    "sec-ch-ua-wow64": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
}


class FullDunder:
    @abstractmethod
    def __getattr__(self, name: str, /):
        raise NotImplementedError

    def __getattr(self, __name, *args, **kwargs):
        return self.__getattr__(__name)(*args, **kwargs)

    async def __agetattr(self, __name, *args, **kwargs):
        return await self.__getattr__(__name)(*args, **kwargs)

    def __setattr__(self, *args, **kwargs):
        try:
            return self.__getattr("__setattr__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __setitem__(self, *args, **kwargs):
        try:
            return self.__getattr("__setitem__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __getitem__(self, *args, **kwargs):
        try:
            return self.__getattr("__getitem__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __delitem__(self, *args, **kwargs):
        try:
            return self.__getattr("__delitem__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __eq__(self, *args, **kwargs):
        try:
            return self.__getattr("__eq__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __ge__(self, *args, **kwargs):
        try:
            return self.__getattr("__ge__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __gt__(self, *args, **kwargs):
        try:
            return self.__getattr("__gt__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __le__(self, *args, **kwargs):
        try:
            return self.__getattr("__le__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __ne__(self, *args, **kwargs):
        try:
            return self.__getattr("__ne__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __lt__(self, *args, **kwargs):
        try:
            return self.__getattr("__lt__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __hash__(self, *args, **kwargs):
        try:
            return self.__getattr("__hash__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __add__(self, *args, **kwargs):
        try:
            return self.__getattr("__add__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __and__(self, *args, **kwargs):
        try:
            return self.__getattr("__and__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __divmod__(self, *args, **kwargs):
        try:
            return self.__getattr("__divmod__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __floordiv__(self, *args, **kwargs):
        try:
            return self.__getattr("__floordiv__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __lshift__(self, *args, **kwargs):
        try:
            return self.__getattr("__lshift__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __matmul__(self, *args, **kwargs):
        try:
            return self.__getattr("__matmul__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __mod__(self, *args, **kwargs):
        try:
            return self.__getattr("__mod__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __mul__(self, *args, **kwargs):
        try:
            return self.__getattr("__mul__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __or__(self, *args, **kwargs):
        try:
            return self.__getattr("__or__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __pow__(self, *args, **kwargs):
        try:
            return self.__getattr("__pow__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rshift__(self, *args, **kwargs):
        try:
            return self.__getattr("__rshift__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __sub__(self, *args, **kwargs):
        try:
            return self.__getattr("__sub__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __truediv__(self, *args, **kwargs):
        try:
            return self.__getattr("__truediv__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __xor__(self, *args, **kwargs):
        try:
            return self.__getattr("__xor__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __radd__(self, *args, **kwargs):
        try:
            return self.__getattr("__radd__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rand__(self, *args, **kwargs):
        try:
            return self.__getattr("__rand__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rdiv__(self, *args, **kwargs):
        try:
            return self.__getattr("__rdiv__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rdivmod__(self, *args, **kwargs):
        try:
            return self.__getattr("__rdivmod__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rfloordiv__(self, *args, **kwargs):
        try:
            return self.__getattr("__rfloordiv__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rlshift__(self, *args, **kwargs):
        try:
            return self.__getattr("__rlshift__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rmatmul__(self, *args, **kwargs):
        try:
            return self.__getattr("__rmatmul__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rmod__(self, *args, **kwargs):
        try:
            return self.__getattr("__rmod__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rmul__(self, *args, **kwargs):
        try:
            return self.__getattr("__rmul__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __ror__(self, *args, **kwargs):
        try:
            return self.__getattr("__ror__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rpow__(self, *args, **kwargs):
        try:
            return self.__getattr("__rpow__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rrshift__(self, *args, **kwargs):
        try:
            return self.__getattr("__rrshift__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rsub__(self, *args, **kwargs):
        try:
            return self.__getattr("__rsub__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rtruediv__(self, *args, **kwargs):
        try:
            return self.__getattr("__rtruediv__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __rxor__(self, *args, **kwargs):
        try:
            return self.__getattr("__rxor__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __abs__(self, *args, **kwargs):
        try:
            return self.__getattr("__abs__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __neg__(self, *args, **kwargs):
        try:
            return self.__getattr("__neg__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __pos__(self, *args, **kwargs):
        try:
            return self.__getattr("__pos__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __invert__(self, *args, **kwargs):
        try:
            return self.__getattr("__invert__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __index__(self, *args, **kwargs):
        try:
            return self.__getattr("__index__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __trunc__(self, *args, **kwargs):
        try:
            return self.__getattr("__trunc__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __floor__(self, *args, **kwargs):
        try:
            return self.__getattr("__floor__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __ceil__(self, *args, **kwargs):
        try:
            return self.__getattr("__ceil__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __round__(self, *args, **kwargs):
        try:
            return self.__getattr("__round__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __iter__(self, *args, **kwargs):
        try:
            return self.__getattr("__iter__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __len__(self, *args, **kwargs):
        try:
            return self.__getattr("__len__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __reversed__(self, *args, **kwargs):
        try:
            return self.__getattr("__reversed__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __contains__(self, *args, **kwargs):
        try:
            return self.__getattr("__contains__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __next__(self, *args, **kwargs):
        try:
            return self.__getattr("__next__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __int__(self, *args, **kwargs):
        try:
            return self.__getattr("__int__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __bool__(self, *args, **kwargs):
        try:
            return self.__getattr("__bool__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __complex__(self, *args, **kwargs):
        try:
            return self.__getattr("__complex__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __float__(self, *args, **kwargs):
        try:
            return self.__getattr("__float__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __format__(self, *args, **kwargs):
        try:
            return self.__getattr("__format__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __call__(self, *args, **kwargs):
        try:
            return self.__getattr("__call__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __str__(self, *args, **kwargs):
        try:
            return self.__getattr("__str__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __repr__(self, *args, **kwargs):
        try:
            return self.__getattr("__repr__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __bytes__(self, *args, **kwargs):
        try:
            return self.__getattr("__bytes__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    def __fspath__(self, *args, **kwargs):
        try:
            return self.__getattr("__fspath__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    async def __aiter__(self, *args, **kwargs):
        try:
            return await self.__agetattr("__aiter__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    async def __anext__(self, *args, **kwargs):
        try:
            return await self.__agetattr("__anext__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None

    async def __await__(self, *args, **kwargs):
        try:
            return await self.__agetattr("__await__", *args, **kwargs)
        except BaseException as exc:
            raise exc.with_traceback(None) from None
