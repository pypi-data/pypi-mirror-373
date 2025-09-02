from typing import Protocol, Any, runtime_checkable

@runtime_checkable
class DelegateProtocol(Protocol):
    """
    A basic delegate protocol. Since the delegator argument type is Any,
    there's no restriction when implementing, as long as it's the only argument.
    """
    def __init__(self, delegator: Any):
        ... # pragma: no cover
