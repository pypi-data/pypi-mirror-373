from __future__ import annotations

import typing
from collections.abc import Callable

from ._base import FullDunder

__all__ = ["BroadcastList"]

T = typing.TypeVar("T")


class BroadcastList(typing.Generic[T], list[T]):
    def __call__(self, *args, **kwargs) -> typing.Self:
        # In order to empty broadcasting works properly, it needs to swallow calls.
        return self

    @property
    def bc(self) -> Broadcaster[T]:
        return Broadcaster(self)

    @property
    def chain(self) -> Chainer[T]:
        return Chainer(self)


class Broadcaster(typing.Generic[T], FullDunder):
    __slots__ = ("__value",)

    def __init__(self, sequence: BroadcastList[T], /) -> None:
        self.__value = sequence

    def __getattr__(self, name: str, /) -> Callable[..., BroadcastList] | BroadcastList:
        if not self.__value:
            # Skip operations
            return BroadcastList()

        first_attr = getattr(self.__value[0], name)
        # Treat BroadcastList and FullDunder as attribute, not callable.
        if not isinstance(first_attr, (BroadcastList, FullDunder)) and callable(first_attr):
            # broadcast callables
            def broadcaster(*args, **kwargs):
                return BroadcastList(getattr(i, name)(*args, **kwargs) for i in self.__value)

            return broadcaster

        else:
            # broadcast attributes
            return BroadcastList(getattr(i, name) for i in self.__value)

    def __setattr__(self, name: str, value) -> None:
        if name == "_Broadcaster__value":
            object.__setattr__(self, name, value)
        else:
            super(Broadcaster).__setattr__(name, value)

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.__value!r})"

    def str(self) -> BroadcastList[str]:
        return BroadcastList(str(i) for i in self.__value)

    def repr(self) -> BroadcastList[str]:
        return BroadcastList(repr(i) for i in self.__value)


class Chainer(Broadcaster, typing.Generic[T]):
    __slots__ = ()

    def __getattr__(self, name: str, /) -> Callable[..., BroadcastList[T]]:
        def broadcaster(*args, **kwargs) -> BroadcastList[T]:
            for i in self._Broadcaster__value:  # type: ignore
                getattr(i, name)(*args, **kwargs)
            return self._Broadcaster__value  # type: ignore

        return broadcaster


if typing.TYPE_CHECKING:
    from collections.abc import Iterator

    from selectolax.lexbor import LexborAttributes as Attributes
    from selectolax.lexbor import LexborNode as Node
    from selectolax.lexbor import LexborSelector as Selector

    DefaultT = typing.TypeVar("DefaultT")

    class NodeBroadcastList(BroadcastList[Node]):
        @property
        def bc(self) -> NodeBroadcaster:
            return NodeBroadcaster(self)

    class NodeBroadcaster(Broadcaster[Node]):
        @property
        def attributes(self) -> BroadcastList[dict[str, None | str]]:
            """Get all attributes that belong to the current node.

            The value of empty attributes is None."""
            ...

        @property
        def attrs(self) -> BroadcastList[Attributes]:
            """A dict-like object that is similar to the attributes property, but operates directly on the Node data."""
            ...

        @property
        def id(self) -> BroadcastList[str | None]:
            """Get the id attribute of the node.

            Returns None if id does not set."""
            ...

        def mem_id(self) -> BroadcastList[int]:
            """Get the mem_id of the node.

            Returns 0 if mem_id does not set."""
            ...

        def __hash__(self) -> BroadcastList[int]:
            """Get the hash of this node
            :return: int
            """
            ...

        def text(self, deep: bool = True, separator: str = "", strip: bool = False) -> BroadcastList[str]:
            """Returns the text of the node including text of all its child nodes."""
            ...

        def iter(self, include_text: bool = False) -> BroadcastList[Iterator[Node]]:
            """Iterate over nodes on the current level."""
            ...

        def traverse(self, include_text: bool = False) -> BroadcastList[Iterator[Node]]:
            """Iterate over all child and next nodes starting from the current level."""
            ...

        @property
        def tag(self) -> BroadcastList[str]:
            """Return the name of the current tag (e.g. div, p, img)."""
            ...

        @property
        def child(self) -> BroadcastList[None | Node]:
            """Return the child node."""
            ...

        @property
        def parent(self) -> BroadcastList[None | Node]:
            """Return the parent node."""
            ...

        @property
        def next(self) -> BroadcastList[None | Node]:
            """Return next node."""
            ...

        @property
        def prev(self) -> BroadcastList[None | Node]:
            """Return previous node."""
            ...

        @property
        def last_child(self) -> BroadcastList[None | Node]:
            """Return last child node."""
            ...

        @property
        def html(self) -> BroadcastList[None | str]:
            """Return HTML representation of the current node including all its child nodes."""
            ...

        def css(self, query: str) -> BroadcastList[list[Node]]:
            """Evaluate CSS selector against current node and its child nodes."""
            ...

        def any_css_matches(self, selectors: tuple[str]) -> BroadcastList[bool]:
            """Returns True if any of CSS selectors matches a node"""
            ...

        def css_matches(self, selector: str) -> BroadcastList[bool]:
            """Returns True if CSS selector matches a node."""
            ...

        @typing.overload
        def css_first(self, query: str, default: None = None, strict: bool = False) -> BroadcastList[Node | None]: ...

        @typing.overload
        def css_first(self, query: str, default: DefaultT, strict: bool = False) -> BroadcastList[Node | DefaultT]: ...

        def css_first(self, query, default=None, strict=False) -> typing.Any:
            """Evaluate CSS selector against current node and its child nodes."""
            ...

        def decompose(self, recursive: bool = True) -> BroadcastList[None]:
            """Remove a Node from the tree."""
            ...

        def remove(self, recursive: bool = True) -> BroadcastList[None]:
            """An alias for the decompose method."""
            ...

        def unwrap(self) -> BroadcastList[None]:
            """Replace node with whatever is inside this node."""
            ...

        def strip_tags(self, tags: list[str], recursive: bool = False) -> BroadcastList[None]:
            """Remove specified tags from the HTML tree."""
            ...

        def unwrap_tags(self, tags: list[str]) -> BroadcastList[None]:
            """Unwraps specified tags from the HTML tree.

            Works the same as the unwrap method, but applied to a list of tags."""
            ...

        def replace_with(self, value: str | bytes | None) -> BroadcastList[None]:
            """Replace current Node with specified value."""
            ...

        def insert_before(self, value: str | bytes | None) -> BroadcastList[None]:
            """Insert a node before the current Node."""
            ...

        def insert_after(self, value: str | bytes | None) -> BroadcastList[None]:
            """Insert a node after the current Node."""
            ...

        @property
        def raw_value(self) -> BroadcastList[bytes]:
            """Return the raw (unparsed, original) value of a node.

            Currently, works on text nodes only."""
            ...

        def select(self, query: str | None = None) -> BroadcastList[Selector]:
            """Select nodes given a CSS selector.

            Works similarly to the css method, but supports chained filtering and extra features.
            """
            ...

        def scripts_contain(self, query: str) -> BroadcastList[bool]:
            """Returns True if any of the script tags contain specified text.

            Caches script tags on the first call to improve performance."""
            ...

        def script_srcs_contain(self, queries: tuple[str]) -> BroadcastList[bool]:
            """Returns True if any of the script SRCs attributes contain on of the specified text.

            Caches values on the first call to improve performance."""
            ...

        @property
        def text_content(self) -> BroadcastList[str | None]:
            """Returns the text of the node if it is a text node.

            Returns None for other nodes. Unlike the text method, does not include child nodes.
            """
            ...

        def merge_text_nodes(self) -> BroadcastList[None]:
            """Iterates over all text nodes and merges all text nodes that are close to each other.

            This is useful for text extraction."""
            ...
