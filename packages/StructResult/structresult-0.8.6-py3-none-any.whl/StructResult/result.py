from dataclasses import dataclass, field
from typing import Optional, Self, Protocol, Iterator, Any, Never, TypeGuard

"""
Functional error handling system with:
- Result composition
- Error accumulation
- Type-safe operations

Core concepts:
- Result: Operation outcome (success/failure)
- ErrorPropagator: Error accumulation mechanism
- Collector: Value container with error handling
"""


class Result(Protocol):
    """Protocol for operation results"""
    def is_ok(self) -> bool:
        """Returns True if successful (no errors)"""

    def unwrap(self) -> Any:
        """Returns value or raises exception if errors exist"""


class Ok(Result):
    """Singleton success marker without value"""
    def is_ok(self) -> bool:
        return True

    def __str__(self) -> str:
        return "OK"

    @property
    def value(self) -> "Ok":
        return OK

    def unwrap(self) -> "Ok":
        """Always return OK"""
        return OK


OK = Ok()


class ErrorPropagator(Result, Protocol):
    """Protocol for error-accumulating types"""
    err: Optional[ExceptionGroup]

    def is_ok(self) -> bool:
        return self.err is None

    def append_e(self, e: Exception, msg: str = "") -> Self:
        """adds to existing group or creates new one"""
        if self.err is None:
            self.err = ExceptionGroup(msg, (e,))
        elif msg == self.err.message:
            self.err = ExceptionGroup(msg, (*self.err.exceptions, e))
        else:
            self.err = ExceptionGroup(msg, (e, self.err))
        return self

    def append_err(self, err: ExceptionGroup) -> Self:
        """Adds an exception or exception group to the collector.
        Rules:
        - For ExceptionGroup with matching message: merges exceptions
        - For ExceptionGroup with different message: preserves structure
        """
        if self.err is None:
            self.err = err
        elif self.err.message == err.message:
            self.err = ExceptionGroup(err.message, (*self.err.exceptions, *err.exceptions))
        else:
            self.err = ExceptionGroup(err.message, (*self.err.exceptions, err))
        return self

    def propagate_err[T](self, res: "Collector[T] | ErrorAccumulator") -> Optional[T]:
        """Merges errors from another result and returns its value:
        1. If res has errors - merges them into current
        2. Returns res's value (if exists)
        """
        if res.err is not None:
            self.append_err(res.err)
        return res.value if hasattr(res, "value") else None


@dataclass(slots=True)
class Error(ErrorPropagator):
    """Error-only result container"""
    err: ExceptionGroup

    @classmethod
    def from_e(cls, e: Exception, msg: str = "") -> "Error":
        return cls(ExceptionGroup(msg, (e,)))

    def with_msg(self, msg: str) -> "Error":
        """Returns a new Error instance with updated message context
        while preserving the original exception structure
        """
        return Error(err=ExceptionGroup(msg, (self.err,)))

    def unwrap(self) -> Never:
        """Always raises exception"""
        raise self.err


@dataclass(slots=True)
class ErrorAccumulator(ErrorPropagator):
    """Base container for error propagation with status conversion"""
    err: Optional[ExceptionGroup] = field(init=False, default=None)

    @property
    def result(self) -> Ok | Error:
        """
        Finalize error accumulation and return simple Result.
        Converts this accumulator to either:
        - Ok: if no errors occurred
        - Error: with accumulated ExceptionGroup otherwise
        After conversion, this accumulator should not be used further.
        """
        if self.err is None:
            return OK
        return Error(self.err)

    def unwrap(self) -> Never:
        """ErrorAccumulator is not meant to be unwrapped directly"""
        raise RuntimeError("ErrorAccumulator should be converted to Result first")


class Collector[T](ErrorPropagator, Protocol):
    """Protocol for value containers with error handling"""
    value: T

    def __iter__(self) -> Iterator[Any]:
        return iter((self.value, self.err))

    def unwrap(self) -> T:
        """Returns value or raises exception if errors exist"""
        if self.err:
            raise self.err
        return self.value


@dataclass(slots=True)
class Simple[T](Collector[T], Result):
    """Basic collector for values"""
    value: T
    err: Optional[ExceptionGroup] = field(init=False, default=None)

    def set(self, res: "Simple[T]") -> T:
        """set value and append errors"""
        self.value = res.value
        if res.err is not None:
            self.append_err(res.err)
        return res.value


@dataclass(slots=True)
class Bool(Simple[bool], Result):
    """Specialized collector for boolean results"""
    value: bool = field(default=False)
    err: Optional[ExceptionGroup] = field(init=False, default=None)


@dataclass(slots=True)
class Option[T](Simple[Optional[T]], Result):
    """Basic collector for optional values"""
    value: Optional[T] = field(default=None)


@dataclass(slots=True)
class List[T](Collector[list[Optional[T | Ok]]], Result):
    """List collector with error accumulation"""
    value: list[Optional[T] | Ok] = field(init=False, default_factory=list)
    err: Optional[ExceptionGroup] = field(init=False, default=None)

    def append(self, res:  Option[T] | Simple[T] | Error | Ok) -> None:
        """Appends result with rules:
        - For OK: adds OK marker
        - For Error: adds None and merges errors
        - For Collector: adds value and merges errors
        """
        if isinstance(res, Ok):
            self.value.append(OK)
            return
        if res.err is not None:
            self.append_err(res.err)
        if isinstance(res, Error):
            self.value.append(None)
        else:
            self.value.append(res.value)

    def __add__(self, other: Option[T] | Simple[T] | Error | Ok) -> Self:
        self.append(other)
        return self


type SimpleOrError[T: Any] = Simple[T] | Error


__all__ = [
    "SimpleOrError"
]
