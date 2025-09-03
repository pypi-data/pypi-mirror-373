import unittest
from typing import Annotated, Optional, Tuple

from exposedfunctionality import InputMeta, OutputMeta
from exposedfunctionality.function_parser import function_method_parser


class TestAnnotatedMetadata(unittest.TestCase):
    def test_input_annotated_description(self):
        def fn(
            a: Annotated[int, InputMeta(description="Number of items")],
            b: Annotated[Optional[str], InputMeta(description="Optional label")] = None,
        ) -> None:
            pass

        ser = function_method_parser(fn)
        self.maxDiff = None
        self.assertEqual(
            ser["input_params"],
            [
                {
                    "name": "a",
                    "type": "int",
                    "positional": True,
                    "description": "Number of items",
                },
                {
                    "name": "b",
                    "type": "Union[str, None]",
                    "positional": False,
                    "default": None,
                    "description": "Optional label",
                },
            ],
        )

    def test_output_annotated_single(self):
        def fn() -> Annotated[
            int, OutputMeta(description="value", name="res", type=float)
        ]:
            return 1

        ser = function_method_parser(fn)
        self.assertEqual(
            ser["output_params"],
            [{"name": "res", "_name": "out", "type": "float", "description": "value"}],
        )

    def test_output_annotated_tuple(self):
        def fn() -> Tuple[
            Annotated[int, OutputMeta(description="first", name="left")],
            Annotated[str, OutputMeta(description="second", type=int, name="right")],
        ]:
            return 1, "x"

        ser = function_method_parser(fn)
        self.assertEqual(
            ser["output_params"],
            [
                {
                    "name": "left",
                    "_name": "out0",
                    "type": "int",
                    "description": "first",
                },
                {
                    "name": "right",
                    "_name": "out1",
                    "type": "int",
                    "description": "second",
                },
            ],
        )

    def test_docstring_does_not_override_annotated(self):
        def fn(a: Annotated[int, InputMeta(description="annotated desc")]):
            """
            Args:
                a (int): docstring desc.
            """

            pass

        ser = function_method_parser(fn)
        self.assertEqual(
            ser["input_params"],
            [
                {
                    "name": "a",
                    "type": "int",
                    "positional": True,
                    "optional": False,
                    "description": "annotated desc",
                }
            ],
        )

    def test_input_annotated_full_fields(self):
        def fn(
            a: Annotated[
                int,
                InputMeta(
                    name="alpha",
                    type=str,
                    default="x",
                    optional=True,
                    positional=False,
                    description="renamed",
                ),
            ],
        ) -> None:
            pass

        ser = function_method_parser(fn)
        self.assertEqual(
            ser["input_params"],
            [
                {
                    "name": "alpha",
                    "_name": "a",
                    "type": "str",
                    "positional": False,
                    "optional": True,
                    "default": "x",
                    "description": "renamed",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
