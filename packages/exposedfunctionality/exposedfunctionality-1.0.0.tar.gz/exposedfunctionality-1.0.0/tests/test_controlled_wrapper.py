import unittest
from exposedfunctionality import controlled_wrapper, update_wrapper, controlled_unwrap


class TestWrapperFunctions(unittest.TestCase):
    def setUp(self):
        # Sample functions to be used in tests
        def sample_function():
            """Sample function docstring."""
            pass

        def wrapper_function():
            pass

        self.sample_function = sample_function
        self.wrapper_function = wrapper_function

    def test_docstring_update(self):
        """Test if the wrapper function docstring is updated from the wrapped function."""
        wrapped = update_wrapper(self.wrapper_function, self.sample_function)
        self.assertEqual(wrapped.__doc__, self.sample_function.__doc__)

    def test_docstring_no_update_if_not_empty(self):
        """Test that the wrapper's docstring is not overwritten if it is not empty."""
        # Changing the wrapper function's docstring to non-empty
        self.wrapper_function.__doc__ = "Non-empty docstring"
        wrapped = update_wrapper(
            self.wrapper_function,
            self.sample_function,
            update_if_empty=(),
            update_docstring=False,
        )
        self.assertEqual(wrapped.__doc__, "Non-empty docstring")

    def test_update_if_missing(self):
        """Test attribute update if missing in wrapper."""
        self.sample_function.custom_attribute = "Custom Value"
        wrapped = update_wrapper(self.wrapper_function, self.sample_function)
        self.assertTrue(hasattr(wrapped, "custom_attribute"))
        self.assertEqual(wrapped.custom_attribute, "Custom Value")

    def test_never_update(self):
        """Test that attributes listed in never_update are not updated."""
        self.sample_function.custom_attribute = "Custom Value"
        self.wrapper_function.custom_attribute = ""
        wrapped = update_wrapper(
            self.wrapper_function,
            self.sample_function,
            never_update=("custom_attribute",),
        )
        self.assertEqual(wrapped.custom_attribute, "")

    def test_update_always_with_dicts(self):
        """Test that dictionary attributes are updated, not replaced, when update_dicts is True."""
        self.sample_function.__dict__.update({"a": 1, "b": 2})
        self.wrapper_function.__dict__.update({"b": 3, "c": 4})
        wrapped = update_wrapper(self.wrapper_function, self.sample_function)
        self.assertEqual(
            {"a": wrapped.a, "b": wrapped.b, "c": wrapped.c}, {"a": 1, "b": 2, "c": 4}
        )

    def test_controlled_wrapper_usage(self):
        """Test using controlled_wrapper to create a decorator that updates wrapper functions."""

        @controlled_wrapper(self.sample_function)
        def new_wrapper_function():
            pass

        self.assertEqual(new_wrapper_function.__doc__, self.sample_function.__doc__)

    def test_update_wrapper_missing_attributes(self):
        def original_function():
            """Original function docstring"""
            pass

        def wrapper_function():
            pass

        updated_wrapper = update_wrapper(wrapper_function, original_function)
        self.assertEqual(updated_wrapper.__doc__, original_function.__doc__)
        self.assertEqual(updated_wrapper.__name__, original_function.__name__)
        self.assertEqual(updated_wrapper.__module__, original_function.__module__)

    def test_update_wrapper_existing_attributes(self):
        def original_function():
            """Original function docstring"""
            pass

        def wrapper_function():
            """Wrapper function docstring"""
            pass

        updated_wrapper = update_wrapper(
            wrapper_function, original_function, update_docstring=False
        )
        self.assertNotEqual(updated_wrapper.__doc__, original_function.__doc__)
        self.assertEqual(updated_wrapper.__doc__, "Wrapper function docstring")

    def test_update_wrapper_with_empty_attributes(self):
        def original_function():
            pass

        def wrapper_function():
            pass

        updated_wrapper = update_wrapper(wrapper_function, original_function)
        self.assertEqual(updated_wrapper.__doc__, original_function.__doc__)
        self.assertEqual(
            updated_wrapper.__annotations__, original_function.__annotations__
        )

    def test_controlled_unwrap_no_wrapping(self):
        def original_function():
            pass

        unwrapped_function = controlled_unwrap(original_function)
        self.assertIs(unwrapped_function, original_function)

    def test_controlled_unwrap_with_wrapping(self):
        def original_function():
            pass

        wrapped_function = controlled_wrapper(original_function)(lambda: None)
        unwrapped_function = controlled_unwrap(wrapped_function)
        self.assertIs(unwrapped_function, original_function)

    def test_wrapper_function_has_same_name_as_wrapped(self):
        """Test when wrapper function has the same name as the wrapped function."""

        def wrapper_function():
            pass

        wrapper_function.__name__ = self.sample_function.__name__
        updated_wrapper = update_wrapper(wrapper_function, self.sample_function)
        self.assertEqual(updated_wrapper.__name__, self.sample_function.__name__)

    def test_wrapper_function_overrides_existing_attributes(self):
        """Test when wrapper function overrides existing attributes from wrapped function."""
        self.wrapper_function.__doc__ = "Wrapper docstring"
        self.wrapper_function.__name__ = "wrapper_function"
        updated_wrapper = update_wrapper(self.wrapper_function, self.sample_function)
        self.assertEqual(updated_wrapper.__doc__, self.sample_function.__doc__)
        self.assertEqual(updated_wrapper.__name__, self.sample_function.__name__)

    def test_custom_wrapper_attribute(self):
        """Test when using a custom wrapper attribute name."""
        updated_wrapper = update_wrapper(
            self.wrapper_function,
            self.sample_function,
            wrapper_attribute="__custom_wrapped__",
        )
        self.assertTrue(hasattr(updated_wrapper, "__custom_wrapped__"))
        self.assertIs(
            getattr(updated_wrapper, "__custom_wrapped__"), self.sample_function
        )

    def test_controlled_unwrap_with_custom_wrapper_attribute(self):
        """Test controlled_unwrap with a custom wrapper attribute name."""
        wrapped_function = controlled_wrapper(
            self.sample_function, wrapper_attribute="__custom_wrapped__"
        )(lambda: None)
        unwrapped_function = controlled_unwrap(
            wrapped_function, wrapper_attribute="__custom_wrapped__"
        )
        self.assertIs(unwrapped_function, self.sample_function)

    def test_update_wrapper_handles_inherited_attributes(self):
        """Test that update_wrapper correctly handles inherited attributes."""

        class BaseFunction:
            __doc__ = "Base docstring"

        def wrapper_function():
            pass

        wrapped_function = update_wrapper(wrapper_function, BaseFunction)
        self.assertEqual(wrapped_function.__doc__, "Base docstring")

    def test_update_wrapper_with_existing_non_empty_attributes(self):
        """Test update_wrapper when the wrapper function has existing non-empty attributes."""
        self.wrapper_function.__annotations__ = {"param": "int"}
        self.sample_function.__annotations__ = {"param": "str"}
        wrapped_function = update_wrapper(
            self.wrapper_function, self.sample_function, update_annotations=True
        )
        self.assertEqual(
            wrapped_function.__annotations__, self.sample_function.__annotations__
        )

    def test_controlled_unwrap_with_stop_condition(self):
        """Test controlled_unwrap with a stopping condition."""

        def stop_condition(f):
            return hasattr(f, "__stop_here__")

        def custom_wrapper_function():
            pass

        custom_wrapper_function.__stop_here__ = True
        # Wrap the sample function with the custom wrapper function
        wrapped_function = controlled_wrapper(self.sample_function)(
            custom_wrapper_function
        )

        # Unwrap using the stop condition
        unwrapped_function = controlled_unwrap(wrapped_function, stop=stop_condition)

        # Check that unwrapped_function is indeed the custom_wrapper_function
        self.assertIs(unwrapped_function, custom_wrapper_function)

    def test_update_wrapper_with_falsy_attributes(self):
        """Test update_wrapper with falsy attributes in the wrapper."""
        self.wrapper_function.custom_attribute = None
        self.sample_function.custom_attribute = "Non-None Value"
        wrapped_function = update_wrapper(
            self.wrapper_function,
            self.sample_function,
            update_if_empty=("custom_attribute",),
        )
        self.assertEqual(wrapped_function.custom_attribute, "Non-None Value")

    def test_controlled_unwrap_with_cyclic_wrapping(self):
        """Test controlled_unwrap raises an error with cyclic wrapping."""

        def cyclic_wrapper_function():
            pass

        cyclic_wrapper_function.__wrapped__ = cyclic_wrapper_function
        with self.assertRaises(ValueError):
            controlled_unwrap(cyclic_wrapper_function)

    def test_update_wrapper_preserves_existing_callable_attributes(self):
        """Test that update_wrapper does not override existing callable attributes."""
        self.wrapper_function.custom_callable = lambda: "Wrapper callable"
        self.sample_function.custom_callable = lambda: "Sample callable"
        wrapped_function = update_wrapper(
            self.wrapper_function,
            self.sample_function,
            update_if_missing=("custom_callable",),
        )
        self.assertEqual(wrapped_function.custom_callable(), "Wrapper callable")

    def test_controlled_unwrap_with_missing_wrapper_attribute(self):
        """Test controlled_unwrap when wrapper_attribute is missing."""

        def original_function():
            pass

        def wrapper_function():
            pass

        wrapper_function.__wrapped__ = original_function
        unwrapped = controlled_unwrap(wrapper_function, wrapper_attribute="__missing__")
        self.assertIs(unwrapped, wrapper_function)

    def test_update_wrapper_handles_multiple_inheritance(self):
        """Test update_wrapper correctly handles attributes with multiple inheritance."""

        class BaseFunction1:
            """Base1 docstring"""

        class BaseFunction2:
            __name__ = "BaseFunction2"

        def wrapper_function():
            pass

        wrapped_function = update_wrapper(
            wrapper_function,
            BaseFunction1,
            update_docstring=True,
        )
        wrapped_function = update_wrapper(wrapped_function, BaseFunction2)
        self.assertEqual(BaseFunction1.__doc__, "Base1 docstring")
        self.assertEqual(wrapped_function.__name__, "BaseFunction2")
        self.assertEqual(wrapped_function.__doc__, "Base1 docstring")

    def test_controlled_wrapper_with_non_callable_wrapped(self):
        """Test controlled_wrapper with a non-callable wrapped object."""

        @controlled_wrapper("not a function")
        def wrapper_function():
            pass

        self.assertEqual(wrapper_function.__doc__, str.__doc__)
