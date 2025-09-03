import unittest
from src.StructResult.result import Option, Error, List, Simple
from src.StructResult.formatter import format_eg


class TestFormatEG(unittest.TestCase):
    def setUp(self) -> None:
        self.simple_error = ValueError("Option error")
        self.nested_group = ExceptionGroup("Nested", [TypeError("Type error")])

        # Create a complex group with at least one exception in each subgroup
        self.complex_group = ExceptionGroup("Complex", [
            self.simple_error,
            self.nested_group,
            ExceptionGroup("With content", [ValueError("Placeholder")])  # Changed from Empty
        ])

        # Create test Result objects
        self.simple_result = Option("test")
        self.error_result = Error.from_e(self.simple_error, msg="error occurred")
        self.list_result = List[int]()
        self.list_result.append(Simple(42))
        self.list_result.append(Option())

    def test_basic_exception_group(self) -> None:
        eg = ExceptionGroup("Test", [self.simple_error])
        result = format_eg(eg)
        expected = "Test (1 sub-exception):\n  - ValueError('Option error')"
        self.assertEqual(result, expected)

    def test_nested_exception_group(self) -> None:
        result = format_eg(self.nested_group)
        expected = "Nested (1 sub-exception):\n  - TypeError('Type error')"
        self.assertEqual(result, expected)

    def test_complex_exception_group(self) -> None:
        result = format_eg(self.complex_group)
        expected = (
            "Complex (3 sub-exceptions):\n"
            "  - ValueError('Option error')\n"
            "  Nested (1 sub-exception):\n"
            "    - TypeError('Type error')\n"
            "  With content (1 sub-exception):\n"
            "    - ValueError('Placeholder')"
        )
        self.assertEqual(result, expected)

    def test_with_result_protocol(self) -> None:
        error_result: Option[int] = Option()
        error_result.append_err(self.complex_group)
        if error_result.err is not None:
            result = format_eg(error_result.err)
            expected = (
                "Complex (3 sub-exceptions):\n"
                "  - ValueError('Option error')\n"
                "  Nested (1 sub-exception):\n"
                "    - TypeError('Type error')\n"
                "  With content (1 sub-exception):\n"
                "    - ValueError('Placeholder')"
            )
            self.assertEqual(result, expected)

    def test_custom_formatting(self) -> None:
        eg = ExceptionGroup("Custom", [self.simple_error])
        result = format_eg(
            eg,
            prefix="    ",
            bullet="* ",
            show_count=False,
            repr_fn=lambda e: f"{type(e).__name__}: {str(e)}"
        )
        expected = "Custom:\n    * ValueError: Option error"
        self.assertEqual(result, expected)

    def test_with_list_result_errors(self) -> None:
        list_result = List[int]()
        list_result.append(Simple(1))
        error_result = Simple(2)
        error_result.append_e(self.simple_error)
        list_result.append(error_result)

        if list_result.err:
            result = format_eg(list_result.err)
            expected = " (1 sub-exception):\n  - ValueError('Option error')"
            self.assertTrue(result.endswith(expected))

    def test_protocol_compatibility(self) -> None:
        error_result = Error(self.complex_group).with_msg(msg="test")

        self.assertIsInstance(error_result.err, BaseExceptionGroup)
        if error_result.err is not None:
            formatted = format_eg(error_result.err)
            self.assertIn("Complex (3 sub-exceptions)", formatted)

    def test_multiple_nesting_levels(self) -> None:
        level3 = ExceptionGroup("Level3", [RuntimeError("Deep error")])
        level2 = ExceptionGroup("Level2", [level3])
        level1 = ExceptionGroup("Level1", [level2])

        result = format_eg(level1)
        expected = (
            "Level1 (1 sub-exception):\n"
            "  Level2 (1 sub-exception):\n"
            "    Level3 (1 sub-exception):\n"
            "      - RuntimeError('Deep error')"
        )
        self.assertEqual(result, expected)
