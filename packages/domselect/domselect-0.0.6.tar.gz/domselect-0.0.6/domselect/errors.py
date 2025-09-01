class SelectorError(Exception):
    pass


class InvalidQueryError(SelectorError):
    pass


class NodeNotFoundError(SelectorError):
    pass


class AttributeNotFoundError(SelectorError):
    pass
