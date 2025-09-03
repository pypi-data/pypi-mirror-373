import unittest
from typing import Callable, Any

OnChangeEvent = Callable[[Any, Any], None]


class TestMinMaxClamp(unittest.TestCase):
    """
    Tests for the min_max_clamp function.
    """

    def test_clamp_with_min_max_none(self):
        from exposedfunctionality.variables.middleware import (
            min_max_clamp,
            ExposedValueData,
        )

        """
        Test clamping when both min and max are None.
        """
        data = ExposedValueData()
        value = 5
        clamped_value = min_max_clamp(value, data)
        self.assertEqual(clamped_value, value)

    def test_clamp_with_min(self):
        from exposedfunctionality.variables.middleware import (
            min_max_clamp,
            ExposedValueData,
        )

        """
        Test clamping with only the min value.
        """
        data = ExposedValueData(min=10)
        value = 5
        clamped_value = min_max_clamp(value, data)
        self.assertEqual(clamped_value, 10)

    def test_clamp_with_max(self):
        from exposedfunctionality.variables.middleware import (
            min_max_clamp,
            ExposedValueData,
        )

        """
        Test clamping with only the max value.
        """
        data = ExposedValueData(max=10)
        value = 15
        clamped_value = min_max_clamp(value, data)
        self.assertEqual(clamped_value, 10)

    def test_clamp_within_bounds(self):
        from exposedfunctionality.variables.middleware import (
            min_max_clamp,
            ExposedValueData,
        )

        """
        Test clamping when value is within the min and max bounds.
        """
        data = ExposedValueData(min=5, max=15)
        value = 10
        clamped_value = min_max_clamp(value, data)
        self.assertEqual(clamped_value, value)

    def test_clamp_outside_bounds(self):
        from exposedfunctionality.variables.middleware import (
            min_max_clamp,
            ExposedValueData,
        )

        """
        Test clamping when value is outside the min and max bounds.
        """
        data = ExposedValueData(min=5, max=15)
        value = 20
        clamped_value = min_max_clamp(value, data)
        self.assertEqual(clamped_value, 15)

    def test_clamp_with_max_less_than_min(self):
        from exposedfunctionality.variables.middleware import (
            min_max_clamp,
            ExposedValueData,
        )

        """
        Test clamping when max is less than min. It should raise a ValueError.
        """
        data = ExposedValueData(min=20, max=10)
        value = 15
        with self.assertRaises(ValueError):
            min_max_clamp(value, data)

    def test_clamp_with_external_min_max(self):
        from exposedfunctionality.variables.middleware import (
            min_max_clamp,
            ExposedValueData,
        )

        """
        Test clamping when external min and max values are provided.
        """
        data = ExposedValueData(min=5, max=20)
        value = 25
        clamped_value = min_max_clamp(value, data, min=10, max=15)
        self.assertEqual(clamped_value, 15)

    def test_clamp_as_valuechecker(self):
        from exposedfunctionality.variables.middleware import (
            min_max_clamp,
        )
        from exposedfunctionality import ExposedValue

        class A:
            data = ExposedValue("data", min=5, max=20, valuechecker=[min_max_clamp])

        a = A()
        a.data = 25
        self.assertEqual(a.data, 20)
