# pylint: disable=redefined-outer-name
import pytest
from lxml.html import HtmlElement, fromstring

from domselect import LxmlXpathSelector
from domselect.errors import NodeNotFoundError

# pylint: disable=R0801
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
def sel() -> LxmlXpathSelector:
    return LxmlXpathSelector.from_content(HTML)


def test_from_content() -> None:
    sel = LxmlXpathSelector.from_content(HTML)
    assert sel.first_text("h1") == "Heading"


def test_init() -> None:
    raw_node = fromstring(HTML)
    # assert raw_node is not None
    sel = LxmlXpathSelector(raw_node)
    assert sel.first_text("//h1") == "Heading"


def test_find(sel: LxmlXpathSelector) -> None:
    result = sel.find("//span")
    assert result[2].text() == "third option"
    assert isinstance(result[0], LxmlXpathSelector)


def test_first(sel: LxmlXpathSelector) -> None:
    result = sel.first("//span")
    assert isinstance(result, LxmlXpathSelector)
    assert result.text() == "first option"


def test_find_raw(sel: LxmlXpathSelector) -> None:
    result = sel.find_raw("//span")
    assert result[2].text_content() == "third option"
    assert isinstance(result[0], HtmlElement)


def test_first_raw(sel: LxmlXpathSelector) -> None:
    result = sel.first_raw("//span")
    assert isinstance(result, HtmlElement)
    assert result.text_content() == "first option"


def test_parent(sel: LxmlXpathSelector) -> None:
    assert sel.first('//*[contains(@class, "first")]').parent().tag() == "div"


def test_exists(sel: LxmlXpathSelector) -> None:
    assert sel.exists('//*[contains(@class, "first")]') is True
    assert sel.exists('//*[contains(@class, "abracadabra")]') is False


def test_first_contains(sel: LxmlXpathSelector) -> None:
    assert sel.first_contains("//span", "second").text() == "second option"


def test_first_contains_subchild(sel: LxmlXpathSelector) -> None:
    assert sel.first_contains("//span", "third").text() == "third option"


def test_first_contains_raise(sel: LxmlXpathSelector) -> None:
    with pytest.raises(NodeNotFoundError):
        sel.first_contains("//span", "abracadabra")
    with pytest.raises(NodeNotFoundError):
        sel.first_contains("//abracadabra", "abracadabra")


def test_attr(sel: LxmlXpathSelector) -> None:
    assert sel.first("//span").attr("class") == "first"


def test_text(sel: LxmlXpathSelector) -> None:
    assert sel.first('//*[contains(@class, "second")]').text() == "second option"


def test_text_subchilds(sel: LxmlXpathSelector) -> None:
    assert sel.first('//*[contains(@class, "third")]').text() == "third option"


def test_tag(sel: LxmlXpathSelector) -> None:
    assert sel.first('//*[contains(@class, "third")]').tag() == "span"
