import unittest
from exposedfunctionality import (
    exposed_method,
    get_exposed_methods,
    assure_exposed_method,
    is_exposed_method,
)


class TestExposedMethodDecorator(unittest.TestCase):
    """
    Test cases for the exposed_method decorator.
    """

    def test_decorator_function_metadata(self):
        """Test that exposed_method adds the necessary metadata to a function."""

        @exposed_method(name="new_name")
        def example_func():
            pass

        self.assertTrue(is_exposed_method(example_func))
        self.assertEqual(example_func.ef_funcmeta["name"], "new_name")

    def test_decorator_with_input_output_params(self):
        """Test that exposed_method correctly adds or updates input and output params."""
        from exposedfunctionality.function_parser import function_method_parser

        self.maxDiff = None
        inputs = [
            {"name": "myparam", "type": "int", "positional": True},
            {"name": "unknown_input", "type": "str"},
        ]
        outputs = [
            {"name": "result", "type": "int"},
            {"name": "unknown_output", "type": "str"},
        ]

        @exposed_method(name="new_name", inputs=inputs, outputs=outputs)
        def example_func(param1: int) -> int:
            return param1

        self.assertEqual(len(example_func.ef_funcmeta["input_params"]), 2)
        self.assertEqual(len(example_func.ef_funcmeta["output_params"]), 2)
        self.assertEqual(example_func.ef_funcmeta["input_params"][0]["name"], "myparam")
        self.assertEqual(example_func.ef_funcmeta["output_params"][0]["name"], "result")

        expected = function_method_parser(example_func)
        expected["name"] = "new_name"
        expected["_name"] = "example_func"
        expected["input_params"][0].update(inputs[0])
        expected["output_params"][0].update(outputs[0])
        expected["output_params"][0]["_name"] = "out"
        expected["input_params"].append(inputs[1])
        expected["output_params"].append(outputs[1])

        expected["input_params"][0]["_name"] = "param1"

        self.assertEqual(
            example_func.ef_funcmeta["output_params"][0], expected["output_params"][0]
        )
        self.assertEqual(
            example_func.ef_funcmeta["input_params"][0], expected["input_params"][0]
        )

        self.assertEqual(example_func.ef_funcmeta, expected)


class TestGetExposedMethods(unittest.TestCase):
    """
    Test cases for the get_exposed_methods function.
    """

    def test_fetch_exposed_methods(self):
        """Test that get_exposed_methods fetches only the methods decorated with exposed_method."""

        class ExampleClass:
            @exposed_method()
            def method1(self):
                pass

            def method2(self):
                pass

        exposed_methods = get_exposed_methods(ExampleClass())

        self.assertIn("method1", exposed_methods)
        self.assertNotIn("method2", exposed_methods)


class TestAssureExposedMethod(unittest.TestCase):
    """
    Test cases for the assure_exposed_method function.
    """

    def test_ensure_function_is_exposed(self):
        """Test that assure_exposed_method ensures a function is decorated with exposed_method."""

        def example_func():
            pass

        exposed_func = assure_exposed_method(example_func, name="new_name")

        self.assertTrue(is_exposed_method(exposed_func))
        self.assertEqual(exposed_func.ef_funcmeta["name"], "new_name")

    def test_already_exposed_function(self):
        """Test that assure_exposed_method returns the function as-is if it's already exposed."""

        @exposed_method(name="original_name")
        def example_func():
            pass

        exposed_func = assure_exposed_method(example_func, name="new_name")

        # Should remain with the original name since it's already exposed
        self.assertEqual(exposed_func.ef_funcmeta["name"], "original_name")

    def test_exposed_methodclass(self):
        from exposedfunctionality import exposed_method, get_exposed_methods

        class MathOperations:
            @exposed_method(
                name="add",
                inputs=[{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
                outputs=[{"name": "sum", "type": "int"}],
            )
            def add_numbers(self, a, b):
                """Add two numbers."""
                return a + b

        math_operations = MathOperations()
        exposed_methods = get_exposed_methods(math_operations)

        self.assertEqual(len(exposed_methods), 1)
        self.assertIn("add_numbers", exposed_methods)
        self.assertTrue(
            exposed_methods["add_numbers"][1],
            {
                "name": "add",
                "input_params": [
                    {"name": "a", "type": "int", "positional": True},
                    {"name": "b", "type": "int", "positional": True},
                ],
                "outputs": [{"name": "sum", "type": "int"}],
                "docstring": {
                    "summary": "Add two numbers.",
                    "original": "Add two numbers.",
                    "input_params": [],
                    "output_params": [],
                    "exceptions": {},
                },
            },
        )
        print(exposed_methods["add_numbers"][1])


if __name__ == "__main__":
    unittest.main()
