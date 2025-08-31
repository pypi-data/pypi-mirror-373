from collections import defaultdict
import random
from typing import Union

from fastapi import FastAPI, HTTPException  # type: ignore

app = FastAPI()
_fail_with_id_storage = defaultdict(int)


@app.get("/random-fail")
def read_root():
    if random.randrange(10) < 5:
        raise HTTPException(500, "Internal Sever Error")
    return {"Hello": "World"}


@app.get("/success-after-fail/")
def read_fail_with_id(attempt: int, id: str):
    _fail_with_id_storage[id] += 1
    if _fail_with_id_storage[id] < attempt:
        raise HTTPException(500, "Internal Sever Error")
    return {"Hello": "World"}


@app.get("/fail/{fail_or_success}")
def read_fail(fail_or_success: str):
    if fail_or_success == "fail":
        raise HTTPException(500, "Internal Sever Error")
    else:
        return {"Hello": "World", "value": fail_or_success}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
