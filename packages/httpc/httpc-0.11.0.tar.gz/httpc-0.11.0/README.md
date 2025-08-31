# httpc

[![Sponsoring](https://img.shields.io/badge/Sponsoring-Patreon-blue?logo=patreon&logoColor=white)](https://www.patreon.com/ilotoki0804)
[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Filotoki0804%2Fhttpc&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://github.com/ilotoki0804/httpc)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/httpc)](https://pypi.org/project/httpc/)
[![image](https://img.shields.io/pypi/l/httpc.svg)](https://github.com/ilotoki0804/httpc/blob/main/LICENSE)
[![image](https://img.shields.io/pypi/pyversions/httpc.svg)](https://pypi.org/project/httpc/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/ilotoki0804/httpc/blob/main/pyproject.toml)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/ilotoki0804/httpc/blob/main/pyproject.toml)

**httpx with CSS**

## Installation

```console
pip install -U httpc
```

## Examples

```python
>>> import httpc
>>> response = httpc.get("https://www.python.org/")
>>> response.match("strong")  # CSS Matching
[<Node strong>, <Node strong>, <Node strong>]
>>> response.match("strong").bc.text()  # Broadcasting
['Notice:', 'A A', 'relaunched community-run job board']
>>> response.single("div")  # .single() method
ValueError: Query 'div' matched with 47 nodes (error from 'https://www.python.org/').
>>> response.single("div", remain_ok=True)  # .single() method
<Node div>
>>> response.single("#content")
<Node div>
>>> httpc.get("https://python.org")
<Response [301 Moved Permanently]>
>>> httpc.common.get("https://python.org")  # ClientOptions and httpc.common
<Response [200 OK]>
>>> httpc.common.get("https://hypothetical-unstable-website.com/", retry=5)  # retry parameter
Attempting fetch again (ConnectError)...
Attempting fetch again (ConnectError)...
Successfully retrieve 'https://hypothetical-unstable-website.com/'
<Response [200 OK]>
>>> httpc.get("https://httpbin.org/status/400")
<Response [400 BAD REQUEST]>
>>> httpc.get("https://httpbin.org/status/400", raise_for_status=True)  # raise_for_status as parameter
httpx.HTTPStatusError: Client error '400 BAD REQUEST' for url 'https://httpbin.org/status/400'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
>>> httpc.get("https://httpbin.org/status/500", raise_for_status=True, retry=3)
Attempting fetch again (status code 500)...
Attempting fetch again (status code 500)...
Attempting fetch again (status code 500)...
httpx.HTTPStatusError: Server error '500 INTERNAL SERVER ERROR' for url 'https://httpbin.org/status/500'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/500
```

## Release Note

* 0.11.0: `httpc`를 통해 cli 접근, `httpc cookies` 추가, 기타 다양한 기능 개선
* 0.10.0.post1: httpc-clean에서 method 입력 (-X)도 인식, ParseTool.extract_next_data와 ParseTool.next_data 추가, httpc-next-data cli 추가, 기타 버그 수정 및 리팩토링
* 0.9.1: 버그 수정 및 개선
* 0.9.0: catcher에서 헤더가 다를 경우 다른 request로 취급하는 distinguish_headers 추가, ValueError 대신 RequestNotFoundError 사용, headers 최신화, 기타 리팩토링
* 0.8.0: httpc-clean 기능 data와 cookie 파라미터도 받도록 확장, 파이썬 3.10 이상으로 지원 범위 좁힘, catcher.install 함수를 catcher.install_httpx으로 이름 변경, retry 설정 시 httpx의 오류에만 retry하도록 변경
* 0.7.0: Add httpc.catcher (from [httpx-catcher](https://github.com/ilotoki0804/httpx-catcher)), add httpc-clean CLI script for sanitizing headers
* 0.6.0: Remove deprecated parameters, remove ClientOptions
* 0.5.0: Use Lexbor as default backend, fix and improve retry and raise_for_status
* 0.4.0: Fix incorrect type hint, rename CSSTool to ParseTool, CSSResponse to Response, bugfixes and small improvements
* 0.3.0: Add `new` parameter, remove `select` method, rename `css` to `match` from CSSTool, remove cache_api.py (unused script), add url note, retry if server error on raise_for_status, bugfix
* 0.2.0: Initial release
