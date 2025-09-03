import unittest


class DoctringExtractionTests:
    BASIC_DOCSTRING: str
    EMPTY_DOCSTRING = ""
    JUST_SUMMARY: str = """
        Just a summary.
        """
    ONLY_PARAM: str
    ONLY_RETURN: str
    ONLY_EXCEPT: str
    UNDOC_EXCEPT: str
    P_WO_TYPE: str
    MULTI_EXCEPT: str
    NO_SUM: str
    MILTILINE_DESC: str

    def setUp(self) -> None:
        self.maxDiff = None
        return super().setUp()

    def get_parser(self):
        raise NotImplementedError()

    def test_basic_docstring(self):
        result = self.get_parser()(self.BASIC_DOCSTRING)
        expected = {
            "summary": "A basic function.",
            "input_params": [
                {
                    "name": "a",
                    "description": "The first parameter.",
                    "type": "int",
                    "positional": False,
                    "optional": True,
                    "default": 1,
                },
                {
                    "name": "b",
                    "description": "The second parameter.",
                    "type": "str",
                    "positional": True,
                    "optional": False,
                },
            ],
            "exceptions": {"ValueError": "When something is wrong."},
            "output_params": [
                {
                    "description": "A string representation.",
                    "type": "str",
                    "name": "out",
                }
            ],
            "original": self.BASIC_DOCSTRING,
        }

        self.assertEqual(result, expected)

    def test_only_summary(self):
        result = self.get_parser()(self.JUST_SUMMARY)
        expected = {
            "summary": "Just a summary.",
            "input_params": [],
            "output_params": [],
            "exceptions": {},
            "original": self.JUST_SUMMARY,
        }

        self.assertEqual(result, expected)

    def test_only_params(self):
        result = self.get_parser()(self.ONLY_PARAM)
        expected = {
            "summary": "Summary here.",
            "input_params": [
                {
                    "name": "a",
                    "description": "Description for a.",
                    "type": "int",
                    "positional": True,
                    "optional": False,
                },
                {
                    "name": "b",
                    "description": "b is an optional integer.",
                    "type": "int",
                    "positional": False,
                    "optional": True,
                },
            ],
            "output_params": [],
            "exceptions": {},
            "original": self.ONLY_PARAM,
        }
        self.assertEqual(result, expected)

    def test_only_return(self):
        result = self.get_parser()(self.ONLY_RETURN)
        expected = {
            "summary": "Summary for this one.",
            "input_params": [],
            "output_params": [
                {"description": "Some output.", "type": "int", "name": "out"}
            ],
            "exceptions": {},
            "original": self.ONLY_RETURN,
        }
        self.assertEqual(result, expected)

    def test_only_exceptions(self):
        result = self.get_parser()(self.ONLY_EXCEPT)
        expected = {
            "summary": "Exception function.",
            "input_params": [],
            "output_params": [],
            "exceptions": {"ValueError": "If value is wrong."},
            "original": self.ONLY_EXCEPT,
        }
        self.assertEqual(result, expected)

    def test_undoc_exceptions(self):
        result = self.get_parser()(self.UNDOC_EXCEPT)
        expected = {
            "summary": "Exception function.",
            "input_params": [],
            "output_params": [],
            "exceptions": {"ValueError": "", "TypeError": ""},
            "original": self.UNDOC_EXCEPT,
        }
        self.assertEqual(result, expected)

    def test_params_without_type(self):
        result = self.get_parser()(self.P_WO_TYPE)
        expected = {
            "summary": "Function without types.",
            "input_params": [
                {
                    "name": "a",
                    "description": "Description for a.",
                    "positional": True,
                    "optional": False,
                },
                {
                    "name": "b",
                    "description": "Description for b.",
                    "positional": True,
                    "optional": False,
                },
            ],
            "output_params": [],
            "exceptions": {},
            "original": self.P_WO_TYPE,
        }
        self.assertEqual(result, expected)

    def test_multiple_exceptions(self):
        result = self.get_parser()(self.MULTI_EXCEPT)
        expected = {
            "summary": "Function with multiple exceptions.",
            "input_params": [],
            "output_params": [],
            "exceptions": {
                "ValueError": "If value is wrong.",
                "TypeError": "If type is wrong.",
            },
            "original": self.MULTI_EXCEPT,
        }
        self.assertEqual(result, expected)

    def test_no_summary(self):
        result = self.get_parser()(self.NO_SUM)
        expected = {
            "input_params": [
                {
                    "name": "a",
                    "description": "Description for a.",
                    "positional": True,
                    "optional": False,
                },
                {
                    "name": "b",
                    "description": "Description for b.",
                    "positional": True,
                    "optional": False,
                },
            ],
            "output_params": [],
            "exceptions": {},
            "original": self.NO_SUM,
        }
        self.assertEqual(result, expected)

    def test_missing_type_docstring(self):
        result = self.get_parser()(self.MISSING_TYPE_DOCSTRING)
        expected = {
            "input_params": [
                {
                    "name": "a",
                    "description": "The first parameter.",
                    "positional": True,
                    "optional": False,
                },
            ],
            "output_params": [],
            "exceptions": {},
            "original": self.MISSING_TYPE_DOCSTRING,
        }
        self.assertEqual(result, expected)

    def test_multiline_descriptions(self):
        result = self.get_parser()(self.MILTILINE_DESC)

        expected = {
            "summary": "Function with multiline descriptions. Even the summary is multiline.",
            "input_params": [
                {
                    "name": "a",
                    "description": "Description for a. This continues.",
                    "positional": True,
                    "optional": False,
                },
                {
                    "name": "b",
                    "description": "Description for b.",
                    "positional": True,
                    "optional": False,
                },
            ],
            "output_params": [
                {
                    "description": "Some output. This continues.",
                    "type": "int",
                    "name": "out",
                }
            ],
            "exceptions": {
                "ValueError": "If value is wrong. This explains why.",
                "TypeError": "If type is wrong.",
            },
            "original": self.MILTILINE_DESC,
        }

        self.assertEqual(result, expected)

    def test_only_param_name(self):
        result = self.get_parser()(self.ONLY_PARAM_NAME)
        expected = {
            "input_params": [
                {
                    "name": "a",
                    "positional": True,
                    "optional": False,
                },
            ],
            "output_params": [],
            "exceptions": {},
            "original": self.ONLY_PARAM_NAME,
        }
        self.assertEqual(result, expected)

    def test_empty_docstring(self):
        expected = {
            "input_params": [],
            "output_params": [],
            "exceptions": {},
            "original": self.EMPTY_DOCSTRING,
        }
        result = self.get_parser()(self.EMPTY_DOCSTRING)
        self.assertEqual(result, expected)

    def test_only_param_type_only(self):
        result = self.get_parser()(self.ONLY_PARAM_TYPE)
        expected = {
            "input_params": [
                {
                    "name": "a",
                    "type": "int",
                    "positional": True,
                    "optional": False,
                },
            ],
            "output_params": [],
            "exceptions": {},
            "original": self.ONLY_PARAM_TYPE,
        }
        self.assertEqual(result, expected)

    def test_optional_without_type(self):
        result = self.get_parser()(self.OPTIONAL_WO_TYPE)
        expected = {
            "input_params": [
                {
                    "name": "a",
                    "default": "1",
                    "positional": False,
                    "optional": True,
                },
            ],
            "output_params": [],
            "exceptions": {},
            "original": self.OPTIONAL_WO_TYPE,
        }
        self.assertEqual(result, expected)

    def test_unknown_section(self):
        result = self.get_parser()(self.UNKNOWN_SECTION)
        expected = {
            "input_params": [
                {
                    "name": "a",
                    "description": "defaults to.",
                    "positional": True,
                    "optional": False,
                },
            ],
            "output_params": [],
            "exceptions": {},
            "original": self.UNKNOWN_SECTION,
        }
        self.assertEqual(result, expected)


class TestParseRestructuredDocstring(DoctringExtractionTests, unittest.TestCase):
    BASIC_DOCSTRING = """
        A basic function.
        
        :param a: The first parameter, defaults to '1'
        :type a: int, optional
        :param b: The second parameter
        :type b: str
        :raises ValueError: When something is wrong.
        :return: A string representation.
        :rtype: str
        """

    MISSING_TYPE_DOCSTRING = """
       :param a: The first parameter
        """

    ONLY_PARAM = """
        Summary here.
        
        :param a: Description for a.
        :type a: int

        :param b: b is an optional integer.
        :type : int, optional
        """

    ONLY_PARAM_TYPE = """
       :param a
       :type int
        """

    OPTIONAL_WO_TYPE = """
       :param a: defaults to "1"
       :type a: optional
        """

    ONLY_PARAM_NAME = """
       :param a
        """

    UNKNOWN_SECTION = """
       :param a:defaults to

       :unknown test
        """
    ONLY_RETURN = """
        Summary for this one.
        
        :return: Some output.
        :rtype: int
        """

    ONLY_EXCEPT = """
        Exception function.
        
        :raises ValueError: If value is wrong.
        """
    UNDOC_EXCEPT = """
        Exception function.
        
        :raises ValueError:
        :raises TypeError
        """

    P_WO_TYPE = """
        Function without types.
        
        :param a: Description for a.
        :param b: Description for b.
        """

    MULTI_EXCEPT = """
        Function with multiple exceptions.
        
        :raises ValueError: If value is wrong.
        :raises TypeError: If type is wrong.
        """

    NO_SUM = """
        :param a: Description for a.
        :param b: Description for b.
        """
    MILTILINE_DESC = """
        Function with multiline descriptions.
        Even the summary is multiline.

        :param a: Description for a.
            This continues.
        :param b: Description for b.
        
        :return: Some output.
            This continues.
        :rtype: int

        :raises ValueError: If value is wrong.
            This explains why.
        
        :raises TypeError: If type is wrong.
        """

    def get_parser(self):
        from exposedfunctionality.function_parser.docstring_parser import (
            parse_restructured_docstring,
        )

        return parse_restructured_docstring

    def test_rtype_without_para(self):
        docstring = """
        :rtype: int
        """
        with self.assertRaises(ValueError):
            self.get_parser()(docstring)

    def test_type_without_para(self):
        docstring = """
        :type : int
        """
        with self.assertRaises(ValueError):
            self.get_parser()(docstring)

    def test_type_wrong_ref(self):
        docstring = """
        :param a: aparam
        :type b: int
        """
        with self.assertRaises(ValueError):
            self.get_parser()(docstring)

    def test_empty_raises(self):
        docstring = """
        :raises 
        """
        with self.assertRaises(ValueError):
            self.get_parser()(docstring)
        docstring = """
        :raises :
        """
        with self.assertRaises(ValueError):
            self.get_parser()(docstring)

    def test_invalid_apram(self):
        docstring = """
        :param
        """
        with self.assertRaises(ValueError):
            self.get_parser()(docstring)


class TestParseGoogleStyledDocstring(DoctringExtractionTests, unittest.TestCase):
    BASIC_DOCSTRING = """
        A basic function.
        
        Args:
            a (int, optional): The first parameter, defaults to "1".
            b (str): The second parameter.

        Raises:
            ValueError: When something is wrong.

        Returns:
            str: A string representation.
        """

    MISSING_TYPE_DOCSTRING = """
    Args:
       a: The first parameter
    """

    ONLY_PARAM_TYPE = """
    Args:
        a (int)
    """

    OPTIONAL_WO_TYPE = """
    Args:
        a (optional): defaults to "1"
    """

    ONLY_PARAM = """
        Summary here.
        
        Args:
            a (int): Description for a.
            b (int, optional): b is an optional integer.
        """

    ONLY_PARAM_NAME = """
        Args:
            a:
        """

    UNKNOWN_SECTION = """
        Args:
            a: defaults to 
        Unknown:
            test
        """

    ONLY_RETURN = """
        Summary for this one.
        
        Returns:
            int: Some output.
        """

    ONLY_EXCEPT = """
        Exception function.
        
        Raises:
            ValueError: If value is wrong.
        """

    UNDOC_EXCEPT = """
        Exception function.
        
        Raises:
            ValueError:
            TypeError:
        """

    P_WO_TYPE = """
        Function without types.
        
        Args:
            a: Description for a.
            b: Description for b.
        """

    MULTI_EXCEPT = """
        Function with multiple exceptions.
        
        Raises:
            ValueError: If value is wrong.
            TypeError: If type is wrong.
        """

    NO_SUM = """
        Args:
            a: Description for a.
            b: Description for b.
        """

    MILTILINE_DESC = """
        Function with multiline descriptions.
        Even the summary is multiline.

        Args:
            a: Description for a.
                This continues.
            b: Description for b.

        Returns:
            int: Some output.
                This continues.

        Raises:
            ValueError: If value is wrong.
                This explains why.
            TypeError: If type is wrong.
        """

    def get_parser(self):
        from exposedfunctionality.function_parser.docstring_parser import (
            parse_google_docstring,
        )

        return parse_google_docstring

    def test_raises_wo_except(self):
        docstring = """
        Raises: 
            safdsaf
    """

        res = self.get_parser()(docstring)
        expected = {
            "input_params": [],
            "output_params": [],
            "exceptions": {},
            "original": docstring,
        }
        self.assertEqual(res, expected)

    def test_returns_wo_param(self):
        docstring = """
        Returns: 
            safdsaf
    """

        res = self.get_parser()(docstring)
        expected = {
            "input_params": [],
            "output_params": [],
            "exceptions": {},
            "original": docstring,
        }
        self.assertEqual(res, expected)


class TestAutoDetectRetring(DoctringExtractionTests, unittest.TestCase):
    BASIC_DOCSTRING = TestParseRestructuredDocstring.BASIC_DOCSTRING
    JUST_SUMMARY = TestParseRestructuredDocstring.JUST_SUMMARY
    ONLY_PARAM = TestParseRestructuredDocstring.ONLY_PARAM
    ONLY_RETURN = TestParseRestructuredDocstring.ONLY_RETURN
    ONLY_EXCEPT = TestParseRestructuredDocstring.ONLY_EXCEPT
    P_WO_TYPE = TestParseRestructuredDocstring.P_WO_TYPE
    MULTI_EXCEPT = TestParseRestructuredDocstring.MULTI_EXCEPT
    NO_SUM = TestParseRestructuredDocstring.NO_SUM
    MILTILINE_DESC = TestParseRestructuredDocstring.MILTILINE_DESC
    MISSING_TYPE_DOCSTRING = TestParseRestructuredDocstring.MISSING_TYPE_DOCSTRING
    ONLY_PARAM_NAME = TestParseRestructuredDocstring.ONLY_PARAM_NAME
    ONLY_PARAM_TYPE = TestParseRestructuredDocstring.ONLY_PARAM_TYPE
    OPTIONAL_WO_TYPE = TestParseRestructuredDocstring.OPTIONAL_WO_TYPE
    UNKNOWN_SECTION = TestParseRestructuredDocstring.UNKNOWN_SECTION
    UNDOC_EXCEPT = TestParseRestructuredDocstring.UNDOC_EXCEPT

    def get_parser(self):
        from exposedfunctionality.function_parser import (
            parse_docstring,
        )

        return parse_docstring


class TestAutoDetectGoogltring(DoctringExtractionTests, unittest.TestCase):
    BASIC_DOCSTRING = TestParseGoogleStyledDocstring.BASIC_DOCSTRING
    JUST_SUMMARY = TestParseGoogleStyledDocstring.JUST_SUMMARY
    ONLY_PARAM = TestParseGoogleStyledDocstring.ONLY_PARAM
    ONLY_RETURN = TestParseGoogleStyledDocstring.ONLY_RETURN
    ONLY_EXCEPT = TestParseGoogleStyledDocstring.ONLY_EXCEPT
    P_WO_TYPE = TestParseGoogleStyledDocstring.P_WO_TYPE
    MULTI_EXCEPT = TestParseGoogleStyledDocstring.MULTI_EXCEPT
    NO_SUM = TestParseGoogleStyledDocstring.NO_SUM
    MILTILINE_DESC = TestParseGoogleStyledDocstring.MILTILINE_DESC
    MISSING_TYPE_DOCSTRING = TestParseGoogleStyledDocstring.MISSING_TYPE_DOCSTRING
    ONLY_PARAM_NAME = TestParseGoogleStyledDocstring.ONLY_PARAM_NAME
    ONLY_PARAM_TYPE = TestParseGoogleStyledDocstring.ONLY_PARAM_TYPE
    OPTIONAL_WO_TYPE = TestParseGoogleStyledDocstring.OPTIONAL_WO_TYPE
    UNKNOWN_SECTION = TestParseGoogleStyledDocstring.UNKNOWN_SECTION
    UNDOC_EXCEPT = TestParseGoogleStyledDocstring.UNDOC_EXCEPT

    def get_parser(self):
        from exposedfunctionality.function_parser import parse_docstring

        return parse_docstring


class TestUnifyParserResults(unittest.TestCase):
    def test_complete_docstring(self):
        from exposedfunctionality.function_parser.docstring_parser import (
            _unify_parser_results,
        )

        result = {
            "input_params": [
                {
                    "description": "  A param with  default.  defaults to '1' ",
                    "type": "int",
                },
                {"description": "A positional param."},
            ],
            "output_params": [
                {"description": "Output 1.", "type": str},
                {"description": "Output 2.", "type": float},
            ],
            "summary": "  Summary of function.  ",
            "exceptions": {"ValueError": "  An error occurred.  "},
        }
        docstring = "Sample docstring."
        unified_result = _unify_parser_results(result, docstring)
        self.maxDiff = None
        expected = {
            "original": docstring,
            "input_params": [
                {
                    "description": "A param with default.",
                    "default": 1,
                    "type": "int",
                    "positional": False,
                    "optional": True,
                },
                {
                    "description": "A positional param.",
                    "positional": True,
                    "optional": False,
                },
            ],
            "output_params": [
                {"description": "Output 1.", "name": "out0", "type": "str"},
                {"description": "Output 2.", "name": "out1", "type": "float"},
            ],
            "summary": "Summary of function.",
            "exceptions": {"ValueError": "An error occurred."},
        }

        self.assertEqual(unified_result, expected)

    def test_missing_fields(self):
        from exposedfunctionality.function_parser.docstring_parser import (
            _unify_parser_results,
        )

        result = {
            "input_params": [
                {"description": "A param.  defaults to 123 ", "type": "int"},
            ],
        }
        docstring = "Missing fields docstring."
        unified_result = _unify_parser_results(result, docstring)

        expected = {
            "original": docstring,
            "input_params": [
                {
                    "description": "A param.",
                    "default": 123,
                    "type": "int",
                    "positional": False,
                    "optional": True,
                },
            ],
            "output_params": [],
            "exceptions": {},
        }

        self.assertEqual(unified_result, expected)

    def test_empty_or_missing_descriptions(self):
        from exposedfunctionality.function_parser.docstring_parser import (
            _unify_parser_results,
        )

        result = {
            "input_params": [{"description": "  "}, {}],
            "output_params": [{"description": "  "}, {}],
        }
        docstring = "Docstring with empty descriptions."
        unified_result = _unify_parser_results(result, docstring)

        expected = {
            "original": docstring,
            "input_params": [
                {"optional": False, "positional": True},
                {"optional": False, "positional": True},
            ],
            "output_params": [{"name": "out0"}, {"name": "out1"}],
            "exceptions": {},
        }

        self.assertEqual(unified_result, expected)

    # Add more tests as needed to cover other scenarios.
