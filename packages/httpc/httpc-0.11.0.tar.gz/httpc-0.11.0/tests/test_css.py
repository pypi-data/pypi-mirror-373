import pickle
from pathlib import Path

import pytest

from httpc import ParseTool

SAMPLE_HTML = R"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Coverage report</title>
    <link rel="icon" sizes="32x32" href="favicon_32_cb_58284776.png">
    <link rel="stylesheet" href="style_cb_718ce007.css" type="text/css">
    <script src="coverage_html_cb_497bf287.js" defer></script>
</head>
<body class="indexfile">
<header>
    <div class="content">
        <h1>Coverage report:
            <span class="pc_cov">33%</span>
        </h1>
        <aside id="help_panel_wrapper">
            <input id="help_panel_state" type="checkbox">
            <label for="help_panel_state">
                <img id="keyboard_icon" src="keybd_closed_cb_ce680311.png" alt="Show/hide keyboard shortcuts">
            </label>
            <div id="help_panel">
                <p class="legend">Shortcuts on this page</p>
                <div class="keyhelp">
                    <p>
                        <kbd>f</kbd>
                        <kbd>s</kbd>
                        <kbd>m</kbd>
                        <kbd>x</kbd>
                        <kbd>c</kbd>
                        &nbsp; change column sorting
                    </p>
                    <p>
                        <kbd>[</kbd>
                        <kbd>]</kbd>
                        &nbsp; prev/next file
                    </p>
                    <p>
                        <kbd>?</kbd> &nbsp; show/hide this help
                    </p>
                </div>
            </div>
        </aside>
        <form id="filter_container">
            <input id="filter" type="text" value="" placeholder="filter...">
            <div>
                <input id="hide100" type="checkbox" >
                <label for="hide100">hide covered</label>
            </div>
        </form>
        <h2>
                <a class="button current">Files</a>
                <a class="button" href="function_index.html">Functions</a>
                <a class="button" href="class_index.html">Classes</a>
        </h2>
        <p class="text">
            <a class="nav" href="https://coverage.readthedocs.io/en/7.6.1">coverage.py v7.6.1</a>,
            created at 2024-09-23 17:48 +0900
        </p>
    </div>
</header>
<main id="index">
    <table class="index" data-sortable>
        <thead>
            <tr class="tablehead" title="Click to sort">
                <th id="file" class="name left" aria-sort="none" data-shortcut="f">File<span class="arrows"></span></th>
                <th id="statements" aria-sort="none" data-default-sort-order="descending" data-shortcut="s">statements<span class="arrows"></span></th>
                <th id="missing" aria-sort="none" data-default-sort-order="descending" data-shortcut="m">missing<span class="arrows"></span></th>
                <th id="excluded" aria-sort="none" data-default-sort-order="descending" data-shortcut="x">excluded<span class="arrows"></span></th>
                <th id="coverage" class="right" aria-sort="none" data-shortcut="c">coverage<span class="arrows"></span></th>
            </tr>
        </thead>
        <tbody>
            <tr class="region">
                <td class="name left"><a href="z_1a14af2ddc1a1530___init___py.html">src\httpc\__init__.py</a></td>
                <td>8</td>
                <td>0</td>
                <td>0</td>
                <td class="right" data-ratio="8 8">100%</td>
            </tr>
            <tr class="region">
                <td class="name left"><a href="z_1a14af2ddc1a1530__api_py.html">src\httpc\_api.py</a></td>
                <td>31</td>
                <td>12</td>
                <td>0</td>
                <td class="right" data-ratio="19 31">61%</td>
            </tr>
            <tr class="region">
                <td class="name left"><a href="z_1a14af2ddc1a1530__base_py.html">src\httpc\_base.py</a></td>
                <td>358</td>
                <td>275</td>
                <td>0</td>
                <td class="right" data-ratio="83 358">23%</td>
            </tr>
            <tr class="region">
                <td class="name left"><a href="z_1a14af2ddc1a1530__broadcaster_py.html">src\httpc\_broadcaster.py</a></td>
                <td>136</td>
                <td>103</td>
                <td>0</td>
                <td class="right" data-ratio="33 136">24%</td>
            </tr>
            <tr class="region">
                <td class="name left"><a href="z_1a14af2ddc1a1530__client_py.html">src\httpc\_client.py</a></td>
                <td>134</td>
                <td>97</td>
                <td>0</td>
                <td class="right" data-ratio="37 134">28%</td>
            </tr>
            <tr class="region">
                <td class="name left"><a href="z_1a14af2ddc1a1530__css_py.html">src\httpc\_css.py</a></td>
                <td>45</td>
                <td>23</td>
                <td>0</td>
                <td class="right" data-ratio="22 45">49%</td>
            </tr>
            <tr class="region">
                <td class="name left"><a href="z_1a14af2ddc1a1530__options_py.html">src\httpc\_options.py</a></td>
                <td>65</td>
                <td>14</td>
                <td>0</td>
                <td class="right" data-ratio="51 65">78%</td>
            </tr>
            <tr class="region">
                <td class="name left"><a href="z_a44f0ac069e85531_test_broadcaster_py.html">tests\test_broadcaster.py</a></td>
                <td>4</td>
                <td>0</td>
                <td>0</td>
                <td class="right" data-ratio="4 4">100%</td>
            </tr>
            <tr class="region">
                <td class="name left"><a href="z_a44f0ac069e85531_test_css_py.html">tests\test_css.py</a></td>
                <td>0</td>
                <td>0</td>
                <td>0</td>
                <td class="right" data-ratio="0 0">100%</td>
            </tr>
        </tbody>
        <tfoot>
            <tr class="total">
                <td class="name left">Total</td>
                <td>781</td>
                <td>524</td>
                <td>0</td>
                <td class="right" data-ratio="257 781">33%</td>
            </tr>
        </tfoot>
    </table>
    <p id="no_rows">
        No items found using the specified filter.
    </p>
</main>
<footer>
    <div class="content">
        <p>
            <a class="nav" href="https://coverage.readthedocs.io/en/7.6.1">coverage.py v7.6.1</a>,
            created at 2024-09-23 17:48 +0900
        </p>
    </div>
    <aside class="hidden">
        <a id="prevFileLink" class="nav" href="z_a44f0ac069e85531_test_css_py.html"></a>
        <a id="nextFileLink" class="nav" href="z_1a14af2ddc1a1530___init___py.html"></a>
        <button type="button" class="button_prev_file" data-shortcut="["></button>
        <button type="button" class="button_next_file" data-shortcut="]"></button>
        <button type="button" class="button_show_hide_help" data-shortcut="?"></button>
    </aside>
</footer>
</body>
</html>
"""


@pytest.fixture
def soup() -> ParseTool:
    return ParseTool(SAMPLE_HTML)


@pytest.fixture
def res() -> ParseTool:
    TEST_DIR = Path(__file__).parent
    # response from https://www.python.org/
    with open(TEST_DIR / "resources/response.pickle", "rb") as f:
        return pickle.load(f)


def generate_res() -> None:
    import httpc

    TEST_DIR = Path(__file__).parent
    res = httpc.get("https://www.python.org/")
    with open(TEST_DIR / "resources/response.pickle", "wb") as f:
        pickle.dump(res, f)


def test_single(soup):
    assert soup.match("kbd").bc.text() == ["f", "s", "m", "x", "c", "[", "]", "?"]

    assert "Coverage report" in soup.single("h1").text()

    with pytest.raises(ValueError, match="5"):
        soup.single("div")

    assert "coverage.py" in soup.single("div", remain_ok=True).text()

    with pytest.raises(ValueError, match="no"):
        soup.single("not-exist")

    assert soup.single("not-exist", None) is None


def test_parse(soup):
    header, main, footer = soup.parse().body.iter()  # type: ignore
    assert header.tag == "header"
    assert main.tag == "main"
    assert footer.tag == "footer"


def test_res(res):
    assert res.url == "https://www.python.org/"
    with pytest.raises(ValueError, match=r"https://www.python.org/"):
        res.single("div")
    with pytest.raises(ValueError, match=r"https://www.python.org/"):
        res.single("no-matching-result")


if __name__ == "__main__":
    generate_res()
