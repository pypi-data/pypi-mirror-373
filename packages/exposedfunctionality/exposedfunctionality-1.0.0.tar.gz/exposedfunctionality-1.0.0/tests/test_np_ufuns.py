import unittest
from exposedfunctionality import (
    exposed_method,
    get_exposed_methods,
    assure_exposed_method,
    is_exposed_method,
)
import numpy as np

np.datetime_data
from exposedfunctionality.function_parser.docstring_parser import (
    select_extraction_function,
    parse_numpy_docstring,
)
from pprint import pprint


class TestExposedMethodDecorator(unittest.TestCase):
    def test_ufuncs_docstring(self):
        """Test that exposed_method adds the necessary metadata to a function."""
        for f, summarycheck, ipsum, ipnamecheck, opsum, opnamecheck in [
            (
                np.sin,
                "Trigonometric sine, element-wise.",
                3,
                ["x"],
                1,
                ["y"],
            ),
            (
                np.arccos,
                "Trigonometric inverse cosine, element-wise.",
                3,
                ["x"],
                1,
                ["angle"],
            ),
            (np.add, "Add arguments element-wise.", 4, ["x1", "x2"], 1, ["add"]),
            (
                np.abs,
                "Calculate the absolute value element-wise.",
                3,
                ["x", "out", "where"],
                1,
                ["absolute"],
            ),
            (
                np.split,
                "Split an array into multiple sub-arrays as views into `ary`",
                3,
                ["ary"],
                1,
                ["sub-arrays"],
            ),
        ]:
            self.assertTrue(f.__doc__ is not None)
            prser = select_extraction_function(f.__doc__)
            self.assertTrue(
                prser is parse_numpy_docstring, str(prser) + "\n\n" + f.__doc__
            )
            parseddocs = parse_numpy_docstring(f.__doc__)
            self.assertTrue(
                summarycheck in parseddocs["summary"],
                parseddocs["summary"],
            )
            self.assertEqual(parseddocs["original"], f.__doc__)
            inputs = parseddocs["input_params"]
            self.assertEqual(len(inputs), ipsum, inputs)
            for i, n in enumerate(ipnamecheck):
                self.assertEqual(inputs[i]["name"], n)
            self.assertEqual(
                len(parseddocs["output_params"]), opsum, parseddocs["output_params"]
            )
            for i, n in enumerate(opnamecheck):
                self.assertEqual(parseddocs["output_params"][i]["name"], n)

    def test_ufunfs(self):
        """Test that exposed_method adds the necessary metadata to a function."""
        f = np.sin
        func = assure_exposed_method(f)
        self.assertTrue(is_exposed_method(func))
        self.assertTrue(func.ef_funcmeta["docstring"] is not None)

    def test_arange(self):
        """Test that exposed_method adds the necessary metadata to a function."""
        f = np.arange
        func = assure_exposed_method(f)
        self.assertTrue(is_exposed_method(func))
        self.assertTrue(func.ef_funcmeta["docstring"] is not None)

    def test_arange_docstring(self):
        """Test that exposed_method adds the necessary metadata to a function."""
        f, summarycheck, ipsum, ipnamecheck, opsum, opnamecheck = (
            np.arange,
            "Return evenly spaced values within a given interval.",
            6 if int(np.__version__[0]) >= 2 else 5,
            ["start", "stop", "step"],
            1,
            ["arange"],
        )
        self.assertTrue(f.__doc__ is not None)
        prser = select_extraction_function(f.__doc__)

        self.assertTrue(prser is parse_numpy_docstring, prser)
        parseddocs = parse_numpy_docstring(f.__doc__)

        self.assertTrue(
            summarycheck in parseddocs["summary"],
            parseddocs["summary"],
        )
        self.assertEqual(parseddocs["original"], f.__doc__)
        inputs = parseddocs["input_params"]
        self.assertEqual(len(inputs), ipsum, inputs)
        for i, n in enumerate(ipnamecheck):
            self.assertEqual(inputs[i]["name"], n)
        self.assertEqual(len(parseddocs["output_params"]), opsum)
        for i, n in enumerate(opnamecheck):
            self.assertEqual(parseddocs["output_params"][i]["name"], n)
