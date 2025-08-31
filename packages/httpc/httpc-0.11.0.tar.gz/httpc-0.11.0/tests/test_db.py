import asyncio
from pathlib import Path

import httpx
import pytest

import httpc
from httpc.catcher import AsyncCatcherTransport, DBError, TransactionDatabase

RESOURCE_DIR = Path(__file__).parent.joinpath("resource")


def test_db():
    RESOURCE_DIR.mkdir(exist_ok=True)

    db_path = RESOURCE_DIR / "test.db"
    db = TransactionDatabase(db_path, "Test")
    try:
        req = httpx.Request("GET", "https://hello.world", content=b"hello world content")
        res = httpx.Response(200, text="hello, world!")
        db[req] = res
        fetched_res = db[req]
        # 일관성을 유지하기 어려운 파라미터 제거
        del res._decoder, fetched_res.stream, res.stream
        assert vars(fetched_res) == vars(res)

        assert len(db) == 1
        del db[req]
        assert not db
    finally:
        db.close()
        db_path.unlink(missing_ok=True)


@pytest.mark.skip
@pytest.mark.parametrize("compress", [False, True])
def test_catcher(compress):
    asyncio.run(async_test_catcher(compress=compress))


async def async_test_catcher(compress):
    db_path = RESOURCE_DIR / "test.db"
    with TransactionDatabase(db_path, "transactions", compress_response=compress) as db:
        transport = AsyncCatcherTransport(db, "hybrid")
        async with httpc.AsyncClient(transport=transport) as client:
            res = await client.get("https://www.google.com", headers={"hello": "world"})

            req = httpx.Request("GET", "https://www.google.com", headers={"hello": "world"})
            assert transport.db[req]

            req = httpx.Request("GET", "https://www.google.com", headers={"hello": "NOT world"})
            assert transport.db[req]

            # 원래는 이렇게 중간에 distinguish_headers를 바꾸면 안 되지만 테스트를 간편화하기 위해 허용
            transport.db.distinguish_headers = True

            req = httpx.Request("GET", "https://www.google.com", headers=res.request.headers)
            assert transport.db[req]

            req = httpx.Request("GET", "https://www.google.com", headers={"hello": "NOT world"})
            with pytest.raises(KeyError):
                transport.db[req]

            # test dropping table
            transport.db.drop()
            with pytest.raises(DBError, match="no such table: transactions"):
                transport.db[req] = res

    db_path.unlink(missing_ok=True)
