from typing import Generic, TypeVar, Any, cast, overload
from typingutils import get_generic_arguments
from weakref import WeakValueDictionary, WeakKeyDictionary

from delegate.pattern.core.protocols.delegate_protocol import DelegateProtocol
from delegate.pattern.core.protocols.readonly_passthrough_delegate_protocol import ReadonlyPassthroughDelegateProtocol
from delegate.pattern.core.protocols.writable_passthrough_delegate_protocol import WritablePassthroughDelegateProtocol
from delegate.pattern.core.protocols.supports_delete_protocol import SupportsDeleteProtocol
from delegate.pattern.core.protocols.protocol_error import ProtocolError
from delegate.pattern.core.delegator_error import DelegatorError

T = TypeVar("T", bound = DelegateProtocol)
Tp = TypeVar("Tp", bound = WritablePassthroughDelegateProtocol)
Tout = TypeVar("Tout")

ATTR = "__delegates__"

DELEGATES: WeakValueDictionary[tuple[type[Any], bool], 'Delegate[Any]'] = WeakValueDictionary()

class Delegate(Generic[T]):
    __slots__ = [ "__weakref__", "__delegate_proto", "__passthrough" ]
    __delegate_proto: type[T]
    __passthrough: bool

    def __new__(cls, passthrough: bool = False):
        delegate_proto = cast(type[T], get_generic_arguments(cls)[0])

        if dlg := DELEGATES.get((delegate_proto, passthrough)):
            return dlg

        instance = super().__new__(cls)
        instance.__delegate_proto = delegate_proto
        instance.__passthrough = passthrough

        DELEGATES[(delegate_proto, passthrough)] = instance
        return instance


    def __get__(self, delegator: object, cls: type[Any]) -> T:
        if delegator is None:
            # __get__ is called on a class instance, and should therefore
            # return it self rather than a delegate
            return self # pyright: ignore[reportReturnType]

        delegate = self.__get_delegate(delegator)

        if self.__passthrough and isinstance(delegate, (WritablePassthroughDelegateProtocol, ReadonlyPassthroughDelegateProtocol)):
            return delegate.__get__()
        elif self.__passthrough:
            raise ProtocolError("Delegate protocol is not a valid WritablePassthroughDelegateProtocol or ReadonlyPassthroughDelegateProtocol")
        else:
            return delegate

    def __get_delegate(self, delegator: object) -> T:
        delegates: WeakKeyDictionary[Delegate[T], T] | None = None

        if hasattr(delegator, ATTR):
            delegates = cast(WeakKeyDictionary[Delegate[T], T], getattr(delegator, ATTR))
        else:
            try:
                delegates = WeakKeyDictionary()
                setattr(delegator, ATTR, delegates)
            except AttributeError:
                check_slots(type(delegator))
                raise # pragma: no cover

        if not ( delegate := delegates.get(self) ):
            delegate = self.__delegate_proto(delegator)
            delegates[self] = delegate

        return delegate


    def __set__(self, delegator: object, value: T) -> None:
        delegate = self.__get_delegate(delegator)

        if self.__passthrough and isinstance(delegate, WritablePassthroughDelegateProtocol):
            delegate.__set__(value)
            return
        elif self.__passthrough:
            raise ProtocolError("Delegate protocol is not a valid WritablePassthroughDelegateProtocol")

        if value is delegate:
            pass # pragma: no cover
        else:
            raise AttributeError("Delegate attribute cannot be changed" + str(self.__passthrough) + str(delegate))

    def __delete__(self, delegator: object):
        delegate = self.__get_delegate(delegator)
        if self.__passthrough and isinstance(delegate, SupportsDeleteProtocol):
            delegate.__delete__()
        elif self.__passthrough:
            raise ProtocolError("Delegate protocol is not a valid SupportsDeleteProtocol")
        pass # pragma: no cover

@overload
def delegate(delegate: type[T]) -> Delegate[T]:
    """
    Creates a delegate of type T.

    Args:
        delegate (type[T]): The delegate protocol type

    Returns:
        Delegate[T]: Returns a Delegate[T] object.
    """
    ...
@overload
def delegate(delegate: type[Tp], type_out: type[Tout]) -> Tout:
    """
    Creates a passthrough delegate of type Tp with an out type of Tout. This implementation
    makes type checkers believe that a value of Tout is the actual returned object, which
    is the case when retrieved afterwards.

    Args:
        delegate (type[Tp]): The delegate protocol type

    Returns:
        Delegate[Tp]: Returns a Delegate[Tp] object.
    """
    ...
def delegate(delegate: type[T], type_out: type[Tout] | None = None) -> Delegate[T] | Tout:
    return Delegate[delegate](type_out is not None)

def check_slots(cls: type[Any]) -> None: # pragma: no cover
    if hasattr(cls, "__slots__"):
        slots = getattr(cls, "__slots__")
        if not ATTR in slots:
            raise DelegatorError(f"Delegator class {cls.__name__} uses slots, and attribute '{ATTR}' is not defined. Please make sure that attributes '__weakref__' and '{ATTR}' are both defined in class slots.")
        if not "__weakref__" in slots:
            raise DelegatorError(f"Delegator class {cls.__name__} uses slots, and attribute '__weakref__' is not defined. Please make sure that attributes '__weakref__' and '{ATTR}' are both defined in class slots.")
