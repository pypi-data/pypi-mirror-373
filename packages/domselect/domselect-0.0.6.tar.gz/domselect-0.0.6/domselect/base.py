from __future__ import annotations

from abc import abstractmethod
from typing import Generic, TypeVar, overload

from .errors import AttributeNotFoundError, NodeNotFoundError
from .unset import UNSET, UnsetType

DEFAULT_STRIP_TEXT = True
RawNodeT = TypeVar("RawNodeT")


class BaseSelector(Generic[RawNodeT]):
    __slots__ = ["raw_node"]

    def __init__(self, raw_node: RawNodeT) -> None:
        self.raw_node = raw_node

    @classmethod
    @abstractmethod
    def from_content(cls, content: bytes | str) -> BaseSelector[RawNodeT]: ...

    @overload
    def first(
        self, query: str, default: UnsetType = UNSET
    ) -> BaseSelector[RawNodeT]: ...

    @overload
    def first(self, query: str, default: None) -> None | BaseSelector[RawNodeT]: ...

    def first(
        self, query: str, default: None | UnsetType = UNSET
    ) -> None | BaseSelector[RawNodeT]:
        try:
            return self.__class__(self.find_raw(query)[0])
        except IndexError as ex:
            if default is None:
                return None
            raise NodeNotFoundError(
                "Node not found for query: {}".format(query)
            ) from ex

    @overload
    def first_raw(self, query: str, default: UnsetType = UNSET) -> RawNodeT: ...

    @overload
    def first_raw(self, query: str, default: None) -> None | RawNodeT: ...

    def first_raw(
        self, query: str, default: None | UnsetType = UNSET
    ) -> None | RawNodeT:
        try:
            return self.find_raw(query)[0]
        except IndexError as ex:
            if default is None:
                return None
            raise NodeNotFoundError(
                "Node not found for query: {}".format(query)
            ) from ex

    def find(self, query: str) -> list[BaseSelector[RawNodeT]]:
        return [self.__class__(x) for x in self.find_raw(query)]

    @abstractmethod
    def find_raw(self, query: str) -> list[RawNodeT]:
        raise NotImplementedError

    def exists(self, query: str) -> bool:
        return self.first(query, default=None) is not None

    @overload
    def attr(self, name: str, default: UnsetType = UNSET) -> str: ...

    @overload
    def attr(self, name: str, default: None) -> None | str: ...

    @overload
    def attr(self, name: str, default: str) -> str: ...

    def attr(self, name: str, default: None | UnsetType | str = UNSET) -> None | str:
        try:
            return self.get_raw_attr(name)
        except AttributeNotFoundError:
            if default is UNSET:
                raise
            return default

    @abstractmethod
    def get_raw_attr(self, name: str) -> str:
        raise NotImplementedError

    @overload
    def first_text(
        self, query: str, default: UnsetType = UNSET, strip: bool = DEFAULT_STRIP_TEXT
    ) -> str: ...

    @overload
    def first_text(
        self, query: str, default: None, strip: bool = DEFAULT_STRIP_TEXT
    ) -> None | str: ...

    @overload
    def first_text(
        self, query: str, default: str, strip: bool = DEFAULT_STRIP_TEXT
    ) -> str: ...

    def first_text(
        self,
        query: str,
        default: None | UnsetType | str = UNSET,
        strip: bool = DEFAULT_STRIP_TEXT,
    ) -> None | str:
        try:
            return self.first(query).text(strip=strip)
        except NodeNotFoundError:
            if default is UNSET:
                raise
            return default

    @abstractmethod
    def text(self, strip: bool = DEFAULT_STRIP_TEXT) -> str:
        raise NotImplementedError

    @abstractmethod
    def tag(self) -> str:
        raise NotImplementedError

    @overload
    def first_attr(self, query: str, name: str, default: UnsetType = UNSET) -> str: ...

    @overload
    def first_attr(self, query: str, name: str, default: str) -> str: ...

    @overload
    def first_attr(self, query: str, name: str, default: None) -> None | str: ...

    def first_attr(
        self, query: str, name: str, default: None | UnsetType | str = UNSET
    ) -> None | str:
        try:
            return self.first(query).attr(name, default=default)
        except NodeNotFoundError:
            if default is UNSET:
                raise
            return default

    @abstractmethod
    def parent(self) -> BaseSelector[RawNodeT]:
        raise NotImplementedError

    @overload
    def first_contains(
        self, query: str, pattern: str, default: UnsetType = UNSET
    ) -> BaseSelector[RawNodeT]: ...

    @overload
    def first_contains(
        self, query: str, pattern: str, default: None
    ) -> None | BaseSelector[RawNodeT]: ...

    def first_contains(
        self, query: str, pattern: str, default: None | UnsetType = UNSET
    ) -> None | BaseSelector[RawNodeT]:
        for sel in self.find(query):
            if pattern in sel.text():
                return sel
        if default is None:
            return None
        raise NodeNotFoundError(
            "Node not found for query [{}] and text [{}]".format(query, pattern)
        )
