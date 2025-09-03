import timeit
from typing import Any, TypeGuard
from src.StructResult import result
from src.StructResult.result import Ok, Error, Simple, Result, Collector

# test data
ok_result = Simple(value=1)
error_result = Error.from_e(ValueError("fail"))


# var 1: if not result.is_ok()
def check_is_ok[T](res: Collector[T] | Error | Ok) -> TypeGuard[Collector[T] | Ok]:
    return not res.is_ok()


# var 2: if not isinstance(result, Error)
def check_isinstance(res: Result) -> bool:
    return not isinstance(res, Error)


def foo(res: Simple[Any] | Error) -> None:
    if not check_is_ok(res):
        raise ValueError()
    print(res.value)


# OK_result speed
time_is_ok_ok = timeit.timeit(lambda: check_is_ok(ok_result), number=1_000_000)
time_isinstance_ok = timeit.timeit(lambda: check_isinstance(ok_result), number=1_000_000)


# Error_result speed
time_is_ok_err = timeit.timeit(lambda: check_is_ok(error_result), number=1_000_000)
time_isinstance_err = timeit.timeit(lambda: check_isinstance(error_result), number=1_000_000)

print(f"Ok-res:")
print(f"  is_ok():      {time_is_ok_ok:.6f} sec (1M calls)")
print(f"  isinstance(): {time_isinstance_ok:.6f} sec (1M calls)")

print(f"\nError-res:")
print(f"  is_ok():      {time_is_ok_err:.6f} sec (1M calls)")
print(f"  isinstance(): {time_isinstance_err:.6f} sec (1M calls)")
