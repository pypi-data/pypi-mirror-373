import json
from operator import attrgetter
import re
import typing

next_f_data = re.compile(r"self\.__next_f\.push\(\[\d+,\s*(.*)\]\)", re.DOTALL)
line_regex = re.compile(r"^\s*(?P<hexdigit>[0-9a-fA-F]+):(?P<data_prefix>[A-Z]*)(?P<data_raw>.*)")


class NextData(typing.NamedTuple):
    script_no: int
    line_no: int
    hexdigit: str
    prefix: str
    value: typing.Any


def extract_next_data(scripts: typing.Iterable[str], prefix_to_ignore: typing.Container[str] | None = None) -> list[NextData]:
    line: str
    to_be_continued: str | None = None
    next_data = []
    for script_no, script in enumerate(scripts):
        matched = next_f_data.match(script)
        if not matched:
            # assert "self.__next_f.push(1" not in script, script
            continue
        for line_no, line in enumerate(json.loads(matched[1]).split("\n")):
            if not line:
                continue
            matched = line_regex.match(line)
            if not matched:
                if to_be_continued is None:
                    raise ValueError(f"Line {line_no} in script {script_no} does not match the expected format: {line!r}")

                data_raw = to_be_continued + line
                to_be_continued = None
                if prefix_to_ignore and data_prefix in prefix_to_ignore:  # noqa: F821
                    continue
                # script_no와 line_no 데이터는 continuation의 데이터가 사용되고,
                # hexdigit과 data_prefix는 이전 matched의 데이터를 사용
                # 가능하면 script_no와 line_no 데이터도 이전 matched의 데이터를 사용하면 좋지만,
                # 굳이 중요한 건 아니니 이렇게 구현함
                next_data.append(NextData(script_no, line_no, hexdigit, data_prefix, json.loads(data_raw)))  # noqa: F821
                continue
            elif to_be_continued is not None:
                raise ValueError(f"Line {line_no} in script {script_no} does not match the expected format: {line!r}")

            hexdigit = matched["hexdigit"]
            data_prefix = matched["data_prefix"]
            data_raw = matched["data_raw"]
            try:
                json_data = json.loads(data_raw)
            except json.JSONDecodeError:
                to_be_continued = data_raw
                continue
            if prefix_to_ignore and data_prefix in prefix_to_ignore:
                continue
            next_data.append(NextData(script_no, line_no, hexdigit, data_prefix, json_data))

    next_data.sort(key=lambda x: int(x.hexdigit, 16))
    return next_data
