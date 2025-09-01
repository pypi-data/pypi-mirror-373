# pylint: disable=redefined-outer-name
import pytest
from selectolax.lexbor import LexborHTMLParser, LexborNode

from domselect import LexborSelector
from domselect.errors import NodeNotFoundError

HTML = """
<body>
    <h1>Heading</h1>
    <div>
        <span class="first">first option</span>
        <span class="second">second option</span>
        <span class="third"><bold>third</bold> option</span>
    </div>
</body>
"""


@pytest.fixture
def sel() -> LexborSelector:
    return LexborSelector.from_content(HTML)


def test_from_content() -> None:
    sel = LexborSelector.from_content(HTML)
    assert sel.first_text("h1") == "Heading"


def test_init() -> None:
    raw_node = LexborHTMLParser(HTML).root
    assert raw_node is not None
    sel = LexborSelector(raw_node)
    assert sel.first_text("h1") == "Heading"


def test_find(sel: LexborSelector) -> None:
    result = sel.find("span")
    assert result[2].text() == "third option"
    assert isinstance(result[0], LexborSelector)


def test_first(sel: LexborSelector) -> None:
    result = sel.first("span")
    assert isinstance(result, LexborSelector)
    assert result.text() == "first option"


def test_find_raw(sel: LexborSelector) -> None:
    result = sel.find_raw("span")
    assert result[2].text() == "third option"
    assert isinstance(result[0], LexborNode)


def test_first_raw(sel: LexborSelector) -> None:
    result = sel.first_raw("span")
    assert isinstance(result, LexborNode)
    assert result.text() == "first option"


def test_parent(sel: LexborSelector) -> None:
    assert sel.first(".first").parent().tag() == "div"


def test_exists(sel: LexborSelector) -> None:
    assert sel.exists(".first") is True
    assert sel.exists(".abracadabra") is False


def test_first_contains(sel: LexborSelector) -> None:
    assert sel.first_contains("span", "second").text() == "second option"


def test_first_contains_subchild(sel: LexborSelector) -> None:
    assert sel.first_contains("span", "third").text() == "third option"


def test_first_contains_raise(sel: LexborSelector) -> None:
    with pytest.raises(NodeNotFoundError):
        sel.first_contains("span", "abracadabra")
    with pytest.raises(NodeNotFoundError):
        sel.first_contains("abracadabra", "abracadabra")


def test_attr(sel: LexborSelector) -> None:
    assert sel.first("span").attr("class") == "first"


def test_text(sel: LexborSelector) -> None:
    assert sel.first(".second").text() == "second option"


def test_text_subchilds(sel: LexborSelector) -> None:
    assert sel.first(".third").text() == "third option"


def test_tag(sel: LexborSelector) -> None:
    assert sel.first(".third").tag() == "span"
