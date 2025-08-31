from httpc._base import _parse_curl


def test_extract_headers():
    sample = r"""
curl 'https://peps.python.org/pep-0649/' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: ko-KR,ko;q=0.9' \
  -H 'priority: u=0, i' \
  -H 'sec-ch-ua: "Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Windows"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: none' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36' \
  --data-raw '{"operationName":"getLgMvnoMmlyRmndUsagsWithLimit","variables":{"contnum":"510150463935","limit":1},"query":"query getLgMvnoMmlyRmndUsagsWithLimit($contnum: String\u0021, $limit: Float) {\\n  getLgMvnoMmlyRmndUsagsWithLimit(contnum: $contnum, limit: $limit) {\\n    isSuccess\\n    code\\n    message\\n    data\\n    __typename\\n  }\\n}\\n'
"""

    data = _parse_curl(sample)
    url, headers, data, method = data["url"], data["headers"], data["data"], data["method"]
    assert url == "https://peps.python.org/pep-0649/"
    assert headers == {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "ko-KR,ko;q=0.9",
        "priority": "u=0, i",
        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    }
    expected = '{"operationName":"getLgMvnoMmlyRmndUsagsWithLimit","variables":{"contnum":"510150463935","limit":1},"query":"query getLgMvnoMmlyRmndUsagsWithLimit($contnum: String\\u0021, $limit: Float) {\\\\n  getLgMvnoMmlyRmndUsagsWithLimit(contnum: $contnum, limit: $limit) {\\\\n    isSuccess\\\\n    code\\\\n    message\\\\n    data\\\\n    __typename\\\\n  }\\\\n}\\\\n'
    assert data == expected
    assert method == "GET"
