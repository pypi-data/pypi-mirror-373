from __future__ import annotations

from contextlib import suppress
import json
from pathlib import Path
import re
import shlex
import sys
from argparse import ArgumentParser

from ._base import __version__, logger

parser = ArgumentParser("httpc", "Web development utilities")
parser.add_argument("--version", action="version", version=__version__)
subparsers = parser.add_subparsers(title="Commands")

headers_subparser = subparsers.add_parser("headers", help="Extract headers from curl commands")
headers_subparser.set_defaults(subparser_name="headers")
headers_subparser.add_argument(
    "file",
    nargs="?",
    default="-",
    help="Path to the script file. Defaults to stdin.",
)

next_parser = subparsers.add_parser("next", help="Extract next data from httpc script")
next_parser.set_defaults(subparser_name="next")
next_parser.add_argument("file", default="-", help="Path to the script file. Defaults to stdin.")
next_parser.add_argument("--include-prefixed", "-p", action="store_true")
next_parser.add_argument("--include", "-i", action="append", type=str, default=[], help="Include only specific prefixes.")
next_parser.add_argument("--exclude", "-x", action="append", type=str, default=[], help="Exclude specific prefixes.")
next_parser.add_argument("--overview", nargs="?", default="NOTSET", help="Show data overview.")
next_parser.add_argument("--no-rich-data", "-n", action="store_true", help="Do not use rich for data output.")

cookies_parser = subparsers.add_parser("cookies", help="Extract cookie text from JSON formatted cookie.txt")
cookies_parser.set_defaults(subparser_name="cookies")
cookies_parser.add_argument(
    "file",
    nargs="?",
    default="-",
    help="Path to the script file. Defaults to stdin.",
)


def main() -> None:
    args = parser.parse_args()

    if not hasattr(args, "subparser_name"):
        args = parser.parse_args(["--help"])
        return

    match args.subparser_name:
        case "headers":
            _handle_headers(args)
        case "next":
            _handle_next_data(args)
        case "cookies":
            _handle_cookies(args)
        case other:
            logger.error(f"Invalid subparser name: {other}")


def get_input() -> str:
    """text input을 받는 코드. 직접 붙여넣기 하는 것뿐 아니라 stdin으로 오는 값도 잘 처리합니다."""
    text = ""
    with suppress(EOFError):
        while line := input():
            text += line + "\n"
    return text.rstrip("\n ")


def _parse_curl(curl_command: str) -> dict:
    command = shlex.split(curl_command)
    command = [arg for arg in reversed(command) if arg not in ("\n", "--compressed")]

    header_re = re.compile("(?P<name>[^:]+): (?P<value>.+)")
    assert command.pop() == "curl"

    # URL은 앞에도 마지막에도 있을 수 있음
    if command[-1] == "-H":
        url = command.pop(0)
    else:
        url = command.pop()

    method = "GET"
    headers = {}
    data = None
    try:
        while True:
            match command.pop():
                case "-H":
                    header = command.pop()
                    matched = header_re.match(header)
                    assert matched
                    name = matched["name"]
                    value = matched["value"]

                case "-b":
                    name = "cookie"
                    value = command.pop()

                case "--data-raw":
                    data = command.pop()
                    continue

                case "-X":
                    method = command.pop()
                    continue

                case option:
                    value = command.pop()
                    raise ValueError(f"Unknown option {option!r} with value: {value!r}")

            if name not in headers:
                headers[name] = value
                continue

            if name.lower() != "cookie":
                headers[name] += f"; {value}"

            raise ValueError(f"Duplicate header: {name}, new: {value!r}, old: {headers[name]!r}")
    except IndexError:
        pass

    return dict(url=url, headers=headers, data=data, method=method)


def _handle_headers(args) -> None:
    # Devtools와 mitmproxy의 curl 복사에서 헤더 추출에 사용
    if args.file == "-":
        print("Enter the curl command below.")
        text = get_input()
    else:
        text = Path(args.file).read_text("utf-8")
    data = _parse_curl(text)
    url, headers, data, method = data["url"], data["headers"], data["data"], data["method"]

    cookie = headers.get(key := "cookie", None) or headers.get(key := "Cookie", None)
    if cookie:
        headers[key] = "<cookie>"

    from rich.console import Console

    console = Console()

    if url:
        if method == "GET":
            console.rule("[b]URL[/b]")
        else:
            console.rule(f"[b][blue]{method}[/blue] REQUEST[/b]")
        print(url)

    if cookie:
        console.rule("[b]Cookie[/b]")
        print(cookie)

    if data:
        if data.startswith("$"):
            console.rule("[b]Payload[/b] (It may not be accurate!)")
        else:
            console.rule("[b]Payload[/b]")
        print(repr(data))

    console.rule("[b]Headers[/b]")
    # double quotes를 선호하기 위해 일부러 json.loads 사용
    # 일반적으로는 그냥 console.print만 사용해도 OK
    console.print(json.dumps(headers, indent=4, ensure_ascii=False).replace('"<cookie>"', "cookie"))
    # console.print(headers)


def _handle_next_data(args) -> None:
    from pathlib import Path

    if args.file == "-":
        print("Enter html text below.")
        text = get_input()
    else:
        text = Path(args.file).read_text("utf-8")

    from rich.console import Console

    from httpc import ParseTool

    console = Console()
    text = ParseTool(text).extract_next_data()

    if not args:
        for item in text:
            console.rule(f"[b]{item.hexdigit}[/b]")
            console.print(item.value)
        return

    if args.overview != "NOTSET":
        from rich.table import Table

        table = Table(title="Next Data Overview")
        table.add_column("[blue]Hexdigit", style="cyan", no_wrap=True, justify="right")
        if args.include_prefixed:
            table.add_column("[blue]Prefix", style="magenta", no_wrap=True)
        table.add_column("[blue]Length", style="green", justify="right")
        table.add_column("[blue]Value Starting", style="green", justify="left")

        for item in text:
            if args.include and item.hexdigit not in args.include:
                continue
            if args.exclude and item.hexdigit in args.exclude:
                continue
            if not args.include_prefixed and item.prefix:
                continue
            data_raw = json.dumps(item.value, ensure_ascii=False)
            truncated_limit = int(args.overview) or 80
            truncated = data_raw[:truncated_limit]
            if len(data_raw) < truncated_limit:
                truncated = truncated + " " + "." * (truncated_limit - len(truncated))
            if not args.include_prefixed:
                table.add_row(item.hexdigit, str(len(data_raw)), truncated)
            else:
                table.add_row(item.hexdigit, item.prefix, str(len(data_raw)), truncated)

        console.print(table)
        return

    for item in text:
        if args.include and item.hexdigit not in args.include:
            continue
        if args.exclude and item.hexdigit in args.exclude:
            continue
        if not args.include_prefixed and item.prefix:
            continue
        console.rule(f"[b]{item.hexdigit} start[/b]")
        if args.no_rich_data:
            print(item.value)
        else:
            console.print(item.value)
        console.rule(f"[b]{item.hexdigit} end  [/b]")
    return


def _handle_cookies(args) -> None:
    if args.file == "-":
        print("Enter cookies.txt (JSON format) below.")
        text = get_input()
    else:
        text = Path(args.file).read_text("utf-8")

    cookies = json.loads(text.strip())
    cookies_text = []
    for cookie in cookies:
        cookies_text.append(f'{cookie["name"]}={cookie["value"]}')
    value = "; ".join(cookies_text)

    print(json.dumps(value))


if __name__ == "__main__":
    main()
    sys.exit(0)
