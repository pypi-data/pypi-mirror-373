from __future__ import annotations
import re
import warnings

from typing import Callable
from .types import (
    string_to_type,
    type_to_string,
    cast_to_type,
)

from .ser_types import (
    FunctionInputParam,
    FunctionOutputParam,
    DocstringParserResult,
    TypeNotFoundError,
)


def _unify_parser_results(
    result: DocstringParserResult, docstring=str
) -> DocstringParserResult:
    # default empty lists

    result["original"] = docstring
    if "input_params" not in result:
        result["input_params"] = []
    if "output_params" not in result:
        result["output_params"] = []
    if "exceptions" not in result:
        result["exceptions"] = {}

    if "summary" in result:
        result["summary"] = result["summary"].strip()

        if not result["summary"]:
            del result["summary"]

    # strip and remove empty descriptions
    for param in result["input_params"]:
        if "description" not in param:
            param["description"] = None

        if param["description"]:
            param["description"] = param["description"].strip()

            if "defaults to" in param["description"].lower():
                pattern = r"[Dd]efaults to (`[^`]+`|'[^']+'|\"[^\"]+\"|[^\s.,]+)"
                match = re.search(pattern, param["description"])
                if match:
                    description = param["description"]
                    description = (
                        description[: match.start()] + description[match.end() :]
                    )
                    default_val = match.group(1)

                    param["default"] = default_val

                    param["description"] = description.strip(" ,.")
        if "default" in param and isinstance(param["default"], str):
            if param["default"].startswith(("`", "'", '"')):
                param["default"] = param["default"][1:-1]
        if "default" in param and "type" in param:
            try:
                param["default"] = cast_to_type(
                    param["default"], string_to_type(param["type"])
                )
            except (ValueError, TypeNotFoundError):
                pass
        if "type" in param:
            param["type"] = type_to_string(param["type"])

        if param["description"]:
            param["description"] = (
                param["description"]
                .replace("  ", " ")
                .replace(" .", ".")
                .replace(" ,", ",")
                .replace(" :", ":")
                .replace(",.", ".")
            ).strip()
            # add dot if missing

        if param["description"] and not param["description"].endswith("."):
            param["description"] += "."

        if "positional" not in param:
            if "default" in param or ("optional" in param and param["optional"]):
                param["positional"] = False
            else:
                param["positional"] = True

        if "optional" not in param:
            if "default" in param or not param["positional"]:
                param["optional"] = True
            else:
                param["optional"] = False

        if not param["description"]:
            del param["description"]

    for i, param in enumerate(result["output_params"]):
        if "name" not in param:
            param["name"] = f"out{i}" if len(result["output_params"]) > 1 else "out"

        if "type" in param:
            param["type"] = type_to_string(param["type"])

    # strip and remove empty errors

    for error in list(result["exceptions"].keys()):
        result["exceptions"][error] = result["exceptions"][error].strip()

    # strip  and remove empty return
    for op in result["output_params"]:
        if "description" not in op:
            op["description"] = None

        if op["description"]:
            op["description"] = op["description"].strip()
        if not op["description"]:
            del op["description"]

    # strip summary
    if "summary" in result:
        result["summary"] = result["summary"].strip()

    return result


def parse_restructured_docstring(docstring: str) -> DocstringParserResult:
    """Extracts the parameter descriptions from a reStructuredText docstring.

    Args:
        docstring (str): The docstring from which the parameter descriptions are extracted.

    Returns:
        dict: A dictionary of parameter names to their descriptions.


    Format:
        ```[Summary]

        :param [ParamName]: [ParamDescription], defaults to [DefaultParamVal]
        :type [ParamName]: [ParamType](, optional)
        ...
        :raises [ErrorType]: [ErrorDescription]
        ...
        :return: [ReturnDescription]
        :rtype: [ReturnType]
        ```

    Examples:
    ```python
    docstring = '''
    This is a docstring.

    :param a: The first parameter.
    :param b: The second parameter.
    '''
    print(extract_param_descriptions_reStructuredText(docstring))
    # Returns: {'a': 'The first parameter.', 'b': 'The second parameter.'}
    ```
    """

    # prepend :summary: to the docstring
    original_ = docstring
    docstring = ":summary:\n" + docstring
    lines = docstring.strip().split("\n")
    lines = [line.strip() for line in lines if line.strip()]

    sections = []
    current_section = []
    for line in lines:
        if line.startswith(":") and current_section:
            sections.append(current_section)
            current_section = []
        current_section.append(line)

    # even empty docstring would have :summary:
    sections.append(current_section)

    sections = [" ".join(section) for section in sections]

    result: DocstringParserResult = {
        "input_params": [],
        "output_params": [],
        "exceptions": {},
    }

    for section in sections:
        if section.startswith(":summary:"):
            s = section.replace(":summary:", "").strip()
            if s:
                result["summary"] = s
        elif section.startswith(":param"):
            psection = section.replace(":param", "").strip()
            param_match = re.match(r"([\w_]+):(.+)", psection)
            if not param_match:
                # maybe only a name is given
                param_match = re.match(r"([\w_]+)", psection)

                if not param_match:
                    raise ValueError(f"Could not parse line '{section}' as parameter")
            param = {"name": param_match.group(1)}

            if len(param_match.groups()) > 1:
                # if param_match.group(2): not necessary since by stripping it cannot be an empty string
                param["description"] = param_match.group(2).strip()
            else:
                param["description"] = None
            # default optional
            param["optional"] = False

            result["input_params"].append(param)
        elif section.startswith(":type"):
            if len(result["input_params"]) == 0:
                raise ValueError("Type section without parameter")
            psection = section.replace(":type", "").strip()

            # get param name or last param
            param = None
            if ":" in psection:
                param_name, psection = psection.split(":", 1)
                param_name = param_name.strip()
                if not param_name:
                    # there is always one available otherwise it would have failes ~10 lines before:
                    param_name = result["input_params"][-1]["name"]

                for _param in result["input_params"]:
                    if _param["name"] == param_name:
                        param = _param
                        break
            else:
                param = result["input_params"][-1]
            if param is None:
                raise ValueError(
                    f"Could not find parameter for type section '{section}'"
                )

            _type = psection.strip()
            if "optional" in _type:
                param["optional"] = True
                _types = [t.strip() for t in _type.replace("optional", "").split(",")]
                _types = [t for t in _types if t]
                if len(_types) >= 1:
                    _type = _types[0]
                else:
                    _type = None
            else:
                param["optional"] = False
            if _type:
                try:
                    param["type"] = string_to_type(_type)
                except Exception:
                    pass

        elif section.startswith(":raises"):
            rsection = section.replace(":raises", "").strip()
            if ":" in rsection:
                rsection += " "
                raise_match = re.match(r"([\w_]+):(.+)", rsection)
                if not raise_match:
                    raise ValueError(f"Could not parse line '{section}' as raise")
                result["exceptions"][raise_match.group(1)] = raise_match.group(
                    2
                ).strip()
            else:
                _excep = rsection.split()
                if len(_excep) != 1:
                    raise ValueError(f"Could not parse line '{section}' as raise")
                result["exceptions"][_excep[0]] = ""
        elif section.startswith(":return"):
            rsection = section.replace(":return:", "").strip()
            return_desc = {"description": rsection}
            result["output_params"].append(return_desc)
        elif section.startswith(":rtype"):
            if len(result["output_params"]) == 0:
                raise ValueError("Type section without return")
            rsection = section.replace(":rtype:", "").strip()
            try:
                result["output_params"][0]["type"] = string_to_type(rsection)
            except Exception:
                pass

    return _unify_parser_results(result, docstring=original_)


def parse_google_docstring(docstring: str) -> DocstringParserResult:
    """Extracts the parameter descriptions from a Google-style docstring.

    Args:
        docstring (str): The docstring from which the parameter descriptions are extracted.

    Returns:
        dict: A dictionary of parameter names to their descriptions.

    Examples:
    ```python
    docstring = '''
    This is a docstring.

    Args:
        a (int): The first parameter.
            This continues.
        b (int): The second parameter.
    '''
    print(extract_param_descriptions_google(docstring))
    # Returns: {'a': 'The first parameter. This continues.', 'b': 'The second parameter.'}
    ```

    Format:
        ```[Summary]

        Args:
            [ParamName] ([ParamType]): [ParamDescription]
            ...
        Raises:
            [ErrorType]: [ErrorDescription]
            ...
        Returns:
            [ReturnDescription]
        ```
    """

    # Split the docstring by lines
    pre_strip_lines = [line for line in docstring.split("\n") if line.strip()]

    lines = [line.strip() for line in pre_strip_lines]

    diffs = [len(line) - len(lines[i]) for i, line in enumerate(pre_strip_lines)]

    # if (len(set(diffs))) > 2:
    #     warnings.warn(
    #         "More than two different initendation levels which might come from invalid formatted docstrings."
    #         f"Docstring:\n{docstring}"
    #     )

    section_intentation = (
        min(diffs) if len(diffs) > 0 else 0
    )  # check length for empty docstings

    # Prepare the result object
    result: DocstringParserResult = {
        "input_params": [],
        "output_params": [],
        "exceptions": {},
    }

    # Define a variable to track the current section being parsed
    section = "Sum"
    last_param: dict = {}  # to append multi-line descriptions
    last_exception = None
    for li, line in enumerate(lines):
        if line.startswith("Args:"):
            section = "Args"
        elif line.startswith("Returns:"):
            section = "Returns"
        elif line.startswith("Raises:"):
            section = "Raises"
        elif (
            ":" in line
            and line.split(":")[0].rstrip()
            == pre_strip_lines[li].split(":")[0].rstrip()[section_intentation:]
            and len(line.split(":")[0].rstrip().split()) == 1
        ):
            # unknown section
            section = line.split(":")[0].rstrip()

            warnings.warn(f"Encounterd unknown section: {section}")

        else:
            if section == "Sum":
                if "summary" in result:
                    result["summary"] += " " + line
                else:
                    result["summary"] = line
            if section == "Args":
                param_match_full = re.match(r"^(\w+) \(([\w\[\], ]+)\): (.+)$", line)
                param_match_desc = re.match(r"^(\w+): (.+)$", line)
                param_match_type = re.match(r"^(\w+) \(([\w\[\], ]+)\)$", line)
                param_match_name_only = re.match(r"^(\w+):$", line)

                if param_match_full:
                    param_match = param_match_full
                    name = param_match.group(1)
                    type_opt = param_match.group(2)
                    description = param_match.group(3)
                elif param_match_type:
                    param_match = param_match_type
                    name = param_match.group(1)
                    type_opt = param_match.group(2)
                    description = ""
                elif param_match_desc:
                    param_match = param_match_desc
                    name = param_match.group(1)
                    type_opt = None
                    description = param_match.group(2)
                elif param_match_name_only:
                    param_match = param_match_name_only
                    name = param_match.group(1)
                    type_opt = None
                    description = None

                else:
                    last_param["description"] = (
                        last_param["description"] + " " + line
                        if "description" in last_param
                        else line
                    )
                    continue

                optional = False
                if type_opt and "optional" in type_opt:
                    optional = True
                    type_opt = type_opt.split(",")
                    if len(type_opt) > 1:
                        paramtype = type_opt[0]
                    else:
                        paramtype = None
                else:
                    paramtype = type_opt

                param = {
                    "name": name,
                    "description": description,
                    "optional": optional,
                }
                if paramtype:
                    try:
                        param["type"] = string_to_type(paramtype)
                    except Exception:
                        pass
                del paramtype
                result["input_params"].append(param)
                last_param = param
            elif section == "Returns":
                return_match = re.match(r"([\w\[\], ]+): (.+)", line)
                if return_match:
                    return_param = {
                        "description": return_match.group(2),
                    }
                    try:
                        return_param["type"] = string_to_type(return_match.group(1))
                    except Exception:
                        pass

                    result["output_params"].append(return_param)
                    last_param = return_param
                elif last_param:
                    last_param["description"] = (
                        last_param["description"] + " " + line
                        if "description" in last_param
                        else line
                    )
            elif section == "Raises":
                raise_match = re.match(r"(\w+):(.+)", line + " ")
                if raise_match:
                    last_exception = raise_match.group(1)
                    result["exceptions"][last_exception] = (
                        raise_match.group(2).strip()
                    ).strip()

                elif last_exception:
                    result["exceptions"][last_exception] += " " + line

    return _unify_parser_results(result, docstring)


def parse_numpy_docstring(docstring: str) -> DocstringParserResult:
    sections = {}
    res = DocstringParserResult(
        summary="",
    )
    # Regular expressions to identify sections
    section_regex = re.compile(r"^\n\s*([^\n]*)\s*\n\s*[-]+\s*\n", re.MULTILINE)

    # Find all section starts
    section_starts = [
        (match.start(), match.group(1)) for match in section_regex.finditer(docstring)
    ]
    if len(section_starts) > 0:
        first_section_start = min(section_starts, key=lambda x: x[0])
        res["summary"] = docstring[: first_section_start[0]].strip()

    # Add end of string as the final section start
    section_starts.append((len(docstring), None))

    # Extract sections
    for i in range(len(section_starts) - 1):
        start, section_name = section_starts[i]
        end, _ = section_starts[i + 1]
        section_content = docstring[start:end].strip()

        # Remove the section header
        if section_name:
            header_end = section_content.find("\n")
            section_content = section_content[header_end:].strip()

        sections[section_name] = section_content.strip().strip("-").strip()

    # Process Parameters section
    if "Parameters" in sections:
        params = []
        current_param = None
        current_param_intendation = 0
        current_intendation = 0
        for line in sections["Parameters"].split("\n"):
            param_match = re.match(r"\s*([\w,\s\*\`\"\']+)\s*:\s*(.+)", line)
            if (
                param_match
                and param_match.group(1).strip()
                and " " not in param_match.group(1).replace(", ", ",").strip()
                and (len(line) - len(line.lstrip()) <= current_intendation)
            ):
                if current_param:
                    # Add the current parameter to the list
                    if len(current_param["name"].split(",")) > 1:
                        for n in current_param["name"].split(","):
                            params.append({**current_param, "name": n.strip()})
                    else:
                        params.append(current_param)
                stype = param_match.group(2)
                try:
                    stype = string_to_type(stype)
                except Exception:
                    pass
                current_param = FunctionInputParam(
                    name=param_match.group(1)
                    .replace("`", "")
                    .replace("'", "'")
                    .replace('"', "")
                    .strip(),
                    type=stype,
                    description="",
                    positional="optional" not in param_match.group(2),
                    optional="optional" in param_match.group(2),
                )
                current_param_intendation = len(line) - len(line.lstrip())
                current_intendation = current_param_intendation
            elif current_param:
                # Continuation of a parameter description
                current_param["description"] += line.strip() + " "
                current_intendation = len(line) - len(line.lstrip())
        if current_param:
            # Add the current parameter to the list
            if len(current_param["name"].split(",")) > 1:
                for n in current_param["name"].split(","):
                    params.append({**current_param, "name": n.strip()})
            else:
                params.append(current_param)
        sections["Parameters"] = params
        res["input_params"] = sections["Parameters"]

    # Process Returns section
    if "Returns" in sections:
        params = []
        current_param = None
        current_intendation = 0
        for line in sections["Returns"].split("\n"):
            param_match = re.match(r"\s*([\w,\s\-\_]+)\s*:\s*(.+)", line)
            if (
                param_match
                and param_match.group(1).strip()
                and " " not in param_match.group(1).replace(", ", ",").strip()
                and (len(line) - len(line.lstrip()) <= current_intendation)
            ):
                if current_param:
                    # Add the current parameter to the list
                    if len(current_param["name"].split(",")) > 1:
                        for n in current_param["name"].split(","):
                            params.append({**current_param, "name": n.strip()})
                    else:
                        params.append(current_param)
                stype = param_match.group(2)
                try:
                    stype = string_to_type(stype)
                except Exception:
                    pass
                current_param = FunctionOutputParam(
                    name=param_match.group(1).strip(),
                    type=stype,
                    description="",
                )
                current_param_intendation = len(line) - len(line.lstrip())
                current_intendation = current_param_intendation
            elif current_param:
                # Continuation of a parameter description
                current_param["description"] += line.strip() + " "
                current_intendation = len(line) - len(line.lstrip())
        if current_param:
            # Add the current parameter to the list
            if len(current_param["name"].split(",")) > 1:
                for n in current_param["name"].split(","):
                    params.append({**current_param, "name": n.strip()})
            else:
                params.append(current_param)
        sections["Returns"] = params

        res["output_params"] = sections["Returns"]

    for k, v in sections.items():
        if k not in [
            "Parameters",
            "Returns",
        ]:
            res["summary"] += f"\n\n{k}\n----------\n{v}"

    # Examples section is kept as is, or you could split it into individual examples

    return _unify_parser_results(res, docstring=docstring)


def select_extraction_function(docstring: str) -> Callable:
    """
    Determines the appropriate extraction function for a given docstring.

    Args:
        docstring (str): The docstring for which an extraction function is needed.

    Returns:
        Callable: The selected extraction function.
    """
    # Check for reStructuredText indicators
    if ":param" in docstring or ":raises" in docstring or ":return" in docstring:
        return parse_restructured_docstring

    # Check for NumPy style indicators
    # NumPy docstrings have sections like Parameters, Returns, and Examples followed by a newline and dashes
    numpy_section_patterns = [
        r"^\s*Parameters\s*\n\s*[-]+\s*\n",
        r"^\s*Returns\s*\n\s*[-]+\s*\n",
        r"^\s*Examples\s*\n\s*[-]+\s*\n",
    ]
    if any(
        re.search(pattern, docstring, re.MULTILINE)
        for pattern in numpy_section_patterns
    ):
        return parse_numpy_docstring

    # Check for Google style indicators
    # (Note: Google style is more general and may overlap with other styles,
    # so we check it last)
    param_pattern_google_with_types = (
        r"^\s*([a-zA-Z_]\w*)\s?\(.*\):"  # match "param_name (param_type):"
    )
    param_pattern_google_no_types = r"^\s*([a-zA-Z_]\w*):"  # match "param_name:"
    if re.search(param_pattern_google_with_types, docstring, re.MULTILINE):
        return parse_google_docstring
    if re.search(param_pattern_google_no_types, docstring, re.MULTILINE):
        return parse_google_docstring

    # If none match, return None or you could return a default function
    return None


def parse_docstring(docstring: str) -> DocstringParserResult:
    """
    Extracts the parameter descriptions from a docstring.

    Args:
        docstring (str): The docstring from which the parameter descriptions are extracted.

    Returns:
        dict: A dictionary of parameter names to their descriptions.
    """
    extraction_function = select_extraction_function(docstring)
    if extraction_function is None:
        return _unify_parser_results({"summary": docstring}, docstring=docstring)
    return _unify_parser_results(extraction_function(docstring), docstring=docstring)
