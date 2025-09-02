from typing import Protocol, Any, runtime_checkable

@runtime_checkable
class WritablePassthroughDelegateProtocol(Protocol):
    """
    A passthrough delegate prototol used when implementing a "property-like" writable delegate.
    """

    def __init__(self, delegator: Any):
        ... # pragma: no cover

    def __get__(self) -> Any:
        ... # pragma: no cover

    def __set__(self, value: Any) -> None:
        ... # pragma: no cover