import unittest
from unittest.mock import patch
from typing import Any
from src.StructResult.result import Option, Bool, Ok, OK, Error, List, SimpleOrError, Simple


class TestResultSystem(unittest.TestCase):
    def test_ok_singleton(self) -> None:
        self.assertTrue(OK.is_ok())
        self.assertIsInstance(OK, Ok)

    def test_error_creation(self) -> None:
        exc = ValueError("test error")
        err = Error.from_e(exc, "context")
        self.assertFalse(err.is_ok())
        self.assertIsNotNone(err.err)
        self.assertEqual(len(err.err.exceptions), 1)
        self.assertIsInstance(err.err.exceptions[0], ValueError)

    def test_simple_success(self) -> None:
        res: Option[str] = Option("success")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), "success")
        self.assertIsNone(res.err)

    def test_simple_failure(self) -> None:
        exc = TypeError("type error")
        res: Option[str] = Option("test").append_e(exc)
        self.assertFalse(res.is_ok())
        self.assertIsNotNone(res.err)
        with self.assertRaises(ExceptionGroup):
            res.unwrap()

    def test_bool_type(self) -> None:
        true_res = Bool(value=True)
        false_res = Bool(value=False)
        self.assertTrue(true_res.unwrap())
        self.assertFalse(false_res.unwrap())

    def test_error_propagation(self) -> None:
        exc1 = RuntimeError("error 1")
        exc2 = KeyError("error 2")
        res1: Option[int] = Option().append_e(exc1, "op1")
        res2: Option[int] = Option().append_e(exc2, "op2")
        res1.propagate_err(res2)
        self.assertFalse(res1.is_ok())
        if res1.err is not None:
            self.assertEqual(len(res1.err.exceptions), 2)
            self.assertIsInstance(res1.err.exceptions[0], RuntimeError)
            self.assertIsInstance(res1.err.exceptions[1].exceptions[0], KeyError)

    def test_list_collector(self) -> None:
        lst: List[int] = List()
        lst.append(Option(42))
        lst.append(Error.from_e(ValueError("bad value"), "item2"))
        lst.append(OK)
        lst.append(Option(100))
        self.assertEqual(len(lst.value), 4)
        self.assertEqual(lst.value[0], 42)
        self.assertIsInstance(lst.value[2], Ok)
        self.assertEqual(lst.value[3], 100)
        self.assertFalse(lst.is_ok())
        self.assertEqual(len(lst.err.exceptions), 1)
        self.assertIsInstance(lst.err.exceptions[0], ValueError)

    def test_list_operator_overload(self) -> None:
        lst: List[str] = List[str]() + Option("hello")
        lst += Error.from_e(TypeError("type error"), "second")
        self.assertEqual(len(lst.value), 2)
        self.assertEqual(lst.value[0], "hello")
        self.assertFalse(lst.is_ok())

    def test_exception_group_merging(self) -> None:
        exc1 = ValueError("val1")
        exc2 = TypeError("type1")
        exc3 = KeyError("key1")
        res1: Option[object] = Option().append_e(exc1, "group1").append_e(exc2)
        res2: Option[object] = Option().append_e(exc3, "group1")
        res1.propagate_err(res2)
        self.assertEqual(len(res1.err.exceptions), 3)
        self.assertEqual(res1.err.message, "group1")

    def test_different_error_groups(self) -> None:
        exc1 = ValueError("val1")
        exc2 = TypeError("type1")
        res1: Option[object] = Option().append_e(exc1, "group1")
        res2: Option[object] = Option().append_e(exc2, "group2")
        res1.propagate_err(res2)
        self.assertEqual(len(res1.err.exceptions), 2)
        self.assertIsInstance(res1.err.exceptions[1], ExceptionGroup)

    def test_set_operation(self) -> None:
        main: Option[str] = Option()
        other: Option[str] = Option("data")
        result = main.set(other)
        self.assertEqual(main.value, "data")
        self.assertEqual(result, "data")
        self.assertTrue(main.is_ok())

    def test_bool_set_operation(self) -> None:
        main = Bool()
        other = Bool(value=True)
        result = main.set(other)
        self.assertTrue(main.value)
        self.assertTrue(result)

    def test_simple_none_value(self) -> None:
        res: Option[int] = Option()
        self.assertTrue(res.is_ok())
        self.assertIsNone(res.unwrap())

    def test_bool_false_with_error(self) -> None:
        res = Bool(value=False)
        res.append_e(ValueError("bool error"))
        self.assertFalse(res.value)
        self.assertFalse(res.is_ok())
        with self.assertRaises(ExceptionGroup):
            res.unwrap()

    def test_nested_exception_groups(self) -> None:
        inner_group = ExceptionGroup("inner", [ValueError("v1"), TypeError("t1")])
        outer_group = ExceptionGroup("outer", [inner_group, KeyError("k1")])
        res: Option[int] = Option().append_err(outer_group)
        if res.err is not None:
            self.assertEqual(len(res.err.exceptions), 2)
            self.assertIsInstance(res.err.exceptions[0], ExceptionGroup)
            self.assertEqual(res.err.exceptions[0].message, "inner")
            self.assertEqual(res.err.message, "outer")

    def test_list_empty(self) -> None:
        lst: List[str] = List()
        self.assertTrue(lst.is_ok())
        self.assertEqual(len(lst.value), 0)
        self.assertIsNone(lst.err)

    def test_list_mixed_types(self) -> None:
        lst: List[str | int] = List()
        lst.append(Option(42))
        lst.append(Option("hello"))
        lst.append(Error.from_e(ValueError("error"), "error"))
        self.assertEqual(len(lst.value), 3)
        self.assertEqual(lst.value[0], 42)
        self.assertEqual(lst.value[1], "hello")
        self.assertIsInstance(lst.value[2], type(None))

    def test_propagate_none(self) -> None:
        res: Option[int] = Option(42)
        res.propagate_err(Option())
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 42)

    def test_type_hints(self) -> None:
        def processor() -> Option[str]:
            return Option("result")

        result = processor()
        value: str | None = result.unwrap()
        self.assertEqual(value, "result")

    def test_combined_workflow(self) -> None:
        main: List[int] = List()
        main += Option(10)
        main += Option(20)
        main += Error.from_e(ValueError("invalid value"), "op3")
        main += Option(30)
        self.assertEqual(len(main.value), 4)
        self.assertEqual(main.value[0], 10)
        self.assertEqual(main.value[1], 20)
        self.assertEqual(main.value[3], 30)
        self.assertFalse(main.is_ok())
        self.assertEqual(len(main.err.exceptions), 1)
        with self.assertRaises(ExceptionGroup):
            main.unwrap()

    def test_multiple_propagations(self) -> None:
        res1: Option[int] = Option().append_e(ValueError("v1"), msg="first")
        res2: Option[int] = Option().append_e(TypeError("t1"), msg="second")
        res3: Option[int] = Option().append_e(KeyError("k1"), msg="third")
        main: Option[int] = Option()
        main.propagate_err(res1)
        main.propagate_err(res2)
        main.propagate_err(res3)
        self.assertEqual(len(main.err.exceptions), 3)

    @patch.object(Option, "append_err")
    def test_propagate_err_calls(self, mock_append: Any) -> None:
        err_res: Option[int] = Option()
        err_res.err = ExceptionGroup("error", [ValueError("test")])
        main: Option[int] = Option()
        main.propagate_err(err_res)
        mock_append.assert_called_once_with(err_res.err)

    def test_iterator_protocol(self) -> None:
        res: Option[str] = Option("test")
        values = list(res)
        self.assertEqual(len(values), 2)
        self.assertEqual(values[0], "test")
        self.assertIsNone(values[1])

    def test_bool_truthiness(self) -> None:
        true_res = Bool(value=True)
        false_res = Bool(value=False)
        self.assertTrue(true_res.value)
        self.assertFalse(false_res.value)
        self.assertTrue(bool(true_res.unwrap()))
        self.assertFalse(bool(false_res.unwrap()))

    def test_equal(self) -> None:
        res: Option[str] = Option()
        group = ExceptionGroup("1", (ValueError("1"),))
        res.append_err(group)
        self.assertEqual(res.err, group)

    def test_SimpleOrError(self) -> None:
        def foo(val: int) -> SimpleOrError[int]:
            if val < 0:
                return Error.from_e(ValueError())
            else:
                return Simple(1)
