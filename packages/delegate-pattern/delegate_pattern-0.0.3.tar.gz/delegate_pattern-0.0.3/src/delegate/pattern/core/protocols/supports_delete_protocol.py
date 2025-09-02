from typing import Protocol, runtime_checkable

@runtime_checkable
class SupportsDeleteProtocol(Protocol):
    def __delete__(self) -> None:
        ... # pragma: no cover