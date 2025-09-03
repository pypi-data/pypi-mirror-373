# Tests for the exposed_var module
import unittest
import asyncio


class TestExposedValue(unittest.TestCase):
    """Tests for the ExposedValue descriptor."""

    def test_init_default_type(self):
        """Test the initialization with default type inference."""

        from exposedfunctionality import ExposedValue

        ev = ExposedValue("name", 10)
        self.assertEqual(ev.name, "name")
        self.assertEqual(ev.default, 10)
        self.assertEqual(ev.type, int)

    def test_init_explicit_type(self):
        """Test the initialization with default type inference."""

        from exposedfunctionality import ExposedValue

        ev = ExposedValue("name", 10, type_=float)
        self.assertEqual(ev.type, float)

        # Test conversions that are okay
        ExposedValue("name", 10.0, type_=int)
        ExposedValue("name", "10", type_=int)

        # Test conversions that should raise errors
        with self.assertRaises(TypeError):
            ExposedValue("name", "10.1", type_=int)

    def test_example(self):
        from exposedfunctionality import add_exposed_value

        class A:
            pass

        a = A()
        add_exposed_value(a, "attr", 10, int)
        b = A()
        self.assertFalse(hasattr(b, "attr"))
        b = a.__class__()
        self.assertEqual(b.attr, 10)
        b.attr = 20
        self.assertEqual(b.attr, 20)
        self.assertEqual(a.attr, 10)

        c = a.__class__()
        self.assertEqual(c.attr, 10)
        add_exposed_value(c, "attr2", 20, int)
        c.attr = 30
        self.assertEqual(
            {k: v for k, v in c.__dict__.items() if not k.startswith("_")},
            {"attr": 30, "attr2": 20},
        )
        self.assertEqual(
            {k: v for k, v in a.__dict__.items() if not k.startswith("_")}, {"attr": 10}
        )

    def test_get(self):
        """Test getting the value using the descriptor."""
        from exposedfunctionality import ExposedValue

        class TestClass:
            attr = ExposedValue("attr", 10)

        tc = TestClass()
        self.assertEqual(tc.attr, 10)
        tc.attr = 20
        self.assertEqual(tc.attr, 20)

    def test_set(self):
        """Test getting the value using the descriptor."""
        from exposedfunctionality import ExposedValue

        class TestClass:
            attr = ExposedValue("attr", 10)

        tc = TestClass()

        # Try setting to an invalid value
        with self.assertRaises(TypeError):
            tc.attr = "invalid"

    def test_delete(self):
        """Test that deletion of the attribute is prevented."""

        from exposedfunctionality import ExposedValue

        class TestClass:
            attr = ExposedValue("attr", 10)

        tc = TestClass()
        with self.assertRaises(AttributeError):
            del tc.attr

    def test_repr(self):
        """Test that deletion of the attribute is prevented."""

        from exposedfunctionality import ExposedValue

        ev = ExposedValue("attr", 10)
        self.assertEqual(repr(ev), "ExposedValue(attr)")

    def test_valuechecker(self):
        from exposedfunctionality import ExposedValue

        def valuechecker(value, valuedata):
            return value + 5

        class TestClass:
            attr = ExposedValue("attr", valuechecker=[valuechecker])

        tc = TestClass()

        tc.attr = 5

        self.assertEqual(tc.attr, 10)

    def test_invalid_default(self):
        from exposedfunctionality import ExposedValue

        with self.assertRaises(TypeError) as cm:
            ExposedValue("attr", "invalid", type_=int)
        self.assertEqual(
            str(cm.exception),
            "Expected default value of type <class 'int'>, got <class 'str'>",
        )

        with self.assertRaises(TypeError) as cm:
            ExposedValue("attr", 10.1, type_=int)
            # get the from the exception
        exc = cm.exception
        parent_exc = exc.__cause__
        self.assertEqual(
            str(parent_exc),
            "Can convert default value of type <class 'float'> to <class 'int'>, "
            "and back again, but not without loss of information.",
        )


#       ExposedValue("attr", 10.1, type_=int)


class TestExposedValueFunctions(unittest.TestCase):
    """Test that deletion of the attribute is prevented."""

    def test_add_exposed_value_instance(self):
        """Test dynamically adding an ExposedValue to an instance."""

        from exposedfunctionality import add_exposed_value

        class TestClass:
            pass

        tc = TestClass()
        add_exposed_value(tc, "new_attr", 20, int)
        self.assertEqual(tc.new_attr, 20)
        tc.new_attr = 25
        self.assertEqual(tc.new_attr, 25)

        # Test if adding an already existing attribute raises error
        with self.assertRaises(AttributeError):
            add_exposed_value(tc, "new_attr", 30, int)

        # Try setting to an invalid value
        with self.assertRaises(TypeError):
            tc.new_attr = "invalid"

        self.assertEqual(tc.__class__.__name__, "_TestClass")

    def test_add_exposed_value_class(self):
        """Test dynamically adding an ExposedValue to a class."""
        from exposedfunctionality import add_exposed_value

        class TestClass:
            pass

        add_exposed_value(TestClass, "new_attr", 20, int)
        instance = TestClass()
        self.assertEqual(instance.new_attr, 20)  # noqa: E1101 pylint: disable=E1101

        # type: ignore # of course it does not exist on checking

        # Test if adding an already existing attribute raises error
        with self.assertRaises(AttributeError):
            add_exposed_value(TestClass, "new_attr", 30, int)

    def test_get_exposed_values(self):
        # Test if adding an already existing attribute raises error
        from exposedfunctionality import (
            get_exposed_values,
            add_exposed_value,
            ExposedValue,
        )

        class TestClass:
            attr = ExposedValue("attr", 10)

        tc = TestClass()
        # Checking for existing attributes
        self.assertEqual(
            str(get_exposed_values(tc)), str({"attr": ExposedValue("attr", 10)})
        )
        self.assertEqual(
            str(get_exposed_values(TestClass)), str({"attr": ExposedValue("attr", 10)})
        )

        # Adding a new attribute and testing again
        add_exposed_value(tc, "new_attr", 20, int)
        self.assertEqual(
            str(get_exposed_values(tc)),
            str(
                {
                    "attr": ExposedValue("attr", 10),
                    "new_attr": ExposedValue("new_attr", 20),
                }
            ),
        )

    def test_disable_type_checking(self):
        """Test disabling type checking."""

        from exposedfunctionality import ExposedValue

        class TestClass:
            a = ExposedValue("a", 10, type_=None)

        tc = TestClass()
        self.assertEqual(tc.a, 10)
        tc.a = "string"
        self.assertEqual(tc.a, "string")

    def test_new_ins_from_inst_with_added_exposed(self):
        """Test creating a new instance from an instance with added ExposedValues."""

        from exposedfunctionality import (
            get_exposed_values,
            add_exposed_value,
            ExposedValue,
        )

        class TestClass:
            attr = ExposedValue("attr", 10)

        tc = TestClass()
        add_exposed_value(tc, "new_attr", 20, int)
        self.assertEqual(tc.__class__.__name__, "_TestClass")
        tc2 = tc.__class__()
        self.assertEqual(tc2.__class__.__name__, "_TestClass")

        def get_exposed_values_dict(obj):
            return {k: getattr(obj, k) for k, v in get_exposed_values(obj).items()}

        self.assertEqual(
            get_exposed_values_dict(tc2),
            {
                "attr": 10,
                "new_attr": 20,
            },
        )

        tc = TestClass()
        add_exposed_value(tc, "attr2", 10, int)
        tc.attr = 0
        tc2 = TestClass()
        tc.attr = 40
        self.assertEqual(tc2.attr, 10)
        tc2.attr = 20
        self.assertEqual(tc2.attr, 20)
        self.assertEqual(tc.attr, 40)

        tc3 = tc.__class__()
        self.assertEqual(tc3.attr2, 10)
        add_exposed_value(tc3, "attr3", 20, int)

        self.assertEqual(tc3.attr3, 20)  # noqa: E1101 pylint: disable=E1101
        self.assertEqual(tc3.__class__.__name__, "__TestClass")
        tc3.attr2 = 30

        self.assertEqual(get_exposed_values_dict(tc), {"attr2": 10, "attr": 40})
        self.assertEqual(get_exposed_values_dict(tc2), {"attr": 20})

        # Exposed values are added to the class dict on first access
        with self.assertRaises(KeyError):
            self.assertEqual(tc3.__dict__["attr"], 10)
        self.assertEqual(
            get_exposed_values_dict(tc3), {"attr": 10, "attr2": 30, "attr3": 20}
        )
        self.assertEqual(tc3.attr, 10)
        self.assertEqual(tc3.__dict__["attr"], 10)
        self.assertEqual(
            get_exposed_values_dict(tc3), {"attr": 10, "attr2": 30, "attr3": 20}
        )


class TestExposedValueData(unittest.IsolatedAsyncioTestCase):
    """
    Tests for the ExposedValueData class.
    """

    async def test_add_on_change_callback_and_invoke(self):
        """
        Test that the on_change_callback is correctly added and subsequently invoked when data changes.
        """
        from exposedfunctionality.variables import ExposedValueData

        data = ExposedValueData()
        callback_triggered = False

        def callback(new_value, old_value):
            nonlocal callback_triggered
            callback_triggered = True

        data.add_on_change_callback(callback)
        data.call_on_change_callbacks(5, 3)

        self.assertTrue(callback_triggered, "Callback was not triggered.")

    async def test_add_on_change_callback_with_async(self):
        """
        Test adding an asynchronous on_change_callback and ensure it's invoked when data changes.
        """
        from exposedfunctionality.variables import ExposedValueData

        data = ExposedValueData()
        callback_triggered_event = asyncio.Event()

        async def async_callback(new_value, old_value):
            callback_triggered_event.set()

        data.add_on_change_callback(async_callback)
        tasks: list[asyncio.Task] = data.call_on_change_callbacks(5, 3)

        # Wait for the async callback to complete
        await asyncio.gather(*tasks)
        self.assertTrue(
            callback_triggered_event.is_set(), "Async callback was not triggered."
        )

    def test_attribute_access(self):
        """
        Test that accessing attributes of ExposedValueData returns expected values.
        """
        from exposedfunctionality.variables import ExposedValueData

        data = ExposedValueData(attr1="value1", attr2="value2")

        self.assertEqual(
            data.attr1, "value1", "Attribute 'attr1' did not return expected value."
        )
        self.assertEqual(
            data.attr2, "value2", "Attribute 'attr2' did not return expected value."
        )

        with self.assertRaises(AttributeError):
            _ = data.nonexistent_attr

    async def test_call_on_change_callback_receives_correct_values(self):
        """
        Test that the on_change_callback receives the correct new and old values.
        """
        from exposedfunctionality.variables import ExposedValueData

        data = ExposedValueData()
        received_values = []

        def callback(new_value, old_value):
            received_values.append((new_value, old_value))

        data.add_on_change_callback(callback)
        data.call_on_change_callbacks(5, 3)

        self.assertEqual(
            received_values, [(5, 3)], "Callback did not receive expected values."
        )
