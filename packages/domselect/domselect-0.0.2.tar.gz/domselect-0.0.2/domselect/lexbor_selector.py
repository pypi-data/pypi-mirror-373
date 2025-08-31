from __future__ import annotations

from typing import overload

from selectolax.lexbor import LexborHTMLParser, LexborNode

from .base import DEFAULT_STRIP_TEXT, BaseSelector
from .errors import AttributeNotFoundError, NodeNotFoundError
from .unset import UNSET, UnsetType


class LexborSelector(BaseSelector[LexborNode]):
    __slots__ = []

    @classmethod
    def from_content(cls, content: bytes | str) -> LexborSelector:
        root = LexborHTMLParser(content).root
        assert root is not None
        return LexborSelector(root)

    def find_raw(self, query: str) -> list[LexborNode]:
        return self.raw_node.css(query)

    def parent(self) -> LexborSelector:
        node = self.raw_node.parent
        if node is None:
            raise NodeNotFoundError("Parent node does not exists")
        return LexborSelector(node)

    def tag(self) -> str:
        # It might be None
        return self.raw_node.tag or ""

    def text(self, strip: bool = DEFAULT_STRIP_TEXT) -> str:
        # Do not use lexbor strip here because it fails preserve
        # space before bar here:
        # <span><b>foo</b> bar</span>
        res = self.raw_node.text(strip=False)
        if strip:
            return res.strip()
        return res

    def get_raw_attr(self, name: str) -> str:
        try:
            # for attributes with no value
            # the ".attributes" dict contains None value
            return self.raw_node.attributes[name] or ""
        except KeyError as ex:
            raise AttributeNotFoundError(
                "Element does not have attribute with name [{}]".format(name)
            ) from ex

    @overload
    def first_raw(self, query: str, default: UnsetType = UNSET) -> LexborNode: ...

    @overload
    def first_raw(self, query: str, default: None) -> None | LexborNode: ...

    # optimization: use css_first instead of base css()[0]
    def first_raw(
        self, query: str, default: None | UnsetType = UNSET
    ) -> None | LexborNode:
        res = self.raw_node.css_first(query)
        if res:
            return res
        if default is None:
            return None
        raise NodeNotFoundError("Node not found for query: {}".format(query))

    # optimizatoin: use css_matches instead of base find_one()
    def exists(self, query: str) -> bool:
        return bool(self.raw_node.css_matches(query))
