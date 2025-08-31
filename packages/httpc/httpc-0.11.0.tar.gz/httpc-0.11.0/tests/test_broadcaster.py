from httpc._broadcaster import Broadcaster, BroadcastList


def test_broadcast_list():
    my = BroadcastList(list(i) for i in ("hello", "world", "google", "ha"))
    assert my.bc[1] == ["e", "o", "o", "a"]

    assert my.chain.sort().bc[1] == ["h", "l", "g", "h"]

    my = BroadcastList([])
    assert my.bc.anything == BroadcastList([])
    assert my.bc.any_method() == BroadcastList([])

    class Attr:
        def __init__(self, attr) -> None:
            self.attr = attr

        @property
        def returns_broadcast_list(self) -> BroadcastList:
            return BroadcastList([self.attr])

        @property
        def returns_broadcaster(self) -> Broadcaster:
            return BroadcastList([self.attr]).bc

        def __repr__(self):
            return f"Attr({self.attr!r})"

    my = BroadcastList([Attr(4), Attr("hello"), Attr(4.5), Attr([3])])
    assert my.bc.attr == [4, "hello", 4.5, [3]]

    assert my.bc.returns_broadcast_list == BroadcastList([BroadcastList([4]), BroadcastList(["hello"]), BroadcastList([4.5]), BroadcastList([[3]])])

    assert my.bc.attr.bc.str() == BroadcastList(["4", "hello", "4.5", "[3]"])
    assert my.bc.attr.bc.repr() == BroadcastList(["4", "'hello'", "4.5", "[3]"])
    assert str(my.bc) == "Broadcaster([Attr(4), Attr('hello'), Attr(4.5), Attr([3])])"
    assert repr(my.bc) == "Broadcaster([Attr(4), Attr('hello'), Attr(4.5), Attr([3])])"

    assert my.bc.returns_broadcaster.bc.str() == [
        "Broadcaster([4])",
        "Broadcaster(['hello'])",
        "Broadcaster([4.5])",
        "Broadcaster([[3]])",
    ]
