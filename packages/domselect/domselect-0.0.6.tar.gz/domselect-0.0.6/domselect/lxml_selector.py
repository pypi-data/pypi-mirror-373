from __future__ import annotations

import threading
from abc import abstractmethod
from typing import TypedDict, cast

import lxml.html
from lxml.cssselect import CSSSelector
from lxml.html import HtmlElement, fromstring
from typing_extensions import Self

from .base import DEFAULT_STRIP_TEXT, BaseSelector
from .errors import AttributeNotFoundError, InvalidQueryError, NodeNotFoundError

__all__ = ["LxmlCssSelector", "LxmlXpathSelector"]

LXML_CSS_SELECTOR_CACHE: dict[str, CSSSelector] = {}
THREAD_STORE = threading.local()


class ThreadStoreCache(TypedDict, total=False):
    paser: lxml.html.HTMLParser


class BaseLxmlSelector(BaseSelector[HtmlElement]):
    @abstractmethod
    def find_raw(self, query: str) -> list[HtmlElement]:
        raise NotImplementedError

    @classmethod
    def get_html_parser(cls) -> lxml.html.HTMLParser:
        if not hasattr(THREAD_STORE, "cache"):
            THREAD_STORE.cache = ThreadStoreCache()
        # Each thread should operate with its own parser instance (for speed)
        return cast(
            lxml.html.HTMLParser,
            THREAD_STORE.cache.setdefault("parser", lxml.html.HTMLParser()),
        )

    @classmethod
    def from_content(cls, content: bytes | str) -> Self:
        return cls(fromstring(content, parser=cls.get_html_parser()))

    def get_raw_attr(self, name: str) -> str:
        try:
            return self.raw_node.attrib[name]
        except KeyError as ex:
            raise AttributeNotFoundError(
                "Element does not have attribute with name [{}]".format(name)
            ) from ex

    def text(self, strip: bool = DEFAULT_STRIP_TEXT) -> str:
        res = self.raw_node.text_content()
        if strip:
            return res.strip()
        return res

    def tag(self) -> str:
        return str(self.raw_node.tag)

    def parent(self) -> Self:
        node = self.raw_node.getparent()
        if node is None:
            raise NodeNotFoundError("Parent node does not exists")
        return self.__class__(node)


class LxmlCssSelector(BaseLxmlSelector):
    __slots__ = []

    def find_raw(self, query: str) -> list[HtmlElement]:
        res = LXML_CSS_SELECTOR_CACHE.setdefault(query, CSSSelector(query))(
            self.raw_node
        )
        if not isinstance(res, list):
            raise InvalidQueryError(
                "Selector support only queries which results in list of DOM nodes"
            )
        return res


class LxmlXpathSelector(BaseLxmlSelector):
    __slots__ = []

    def find_raw(self, query: str) -> list[HtmlElement]:
        res = self.raw_node.xpath(query)
        if not isinstance(res, list):
            raise InvalidQueryError(
                "Selector support only queries which results in list of DOM nodes"
            )
        return res
