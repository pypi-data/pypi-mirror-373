"""
This provides routines for formatting data structures as text for user editing and then parsing
the edited text back into a data structure.

- Converts data structures to text for display or editing (`to_text`).
- Parses text back into structured data (`parse_text`).
- Supports simple dict, list, and scalar (int, float, bool, etc.)

"""
#   Copyright (c) 2024.
#   Permission is hereby granted, free of charge, to any person obtaining a
#   copy of this software and associated documentation files (the “Software”), to deal in the
#   Software without restriction,
#   including without limitation the rights to use, copy, modify, merge, publish, distribute,
#   sublicense, and/or sell copies
#   of the Software, and to permit persons to whom the Software is furnished to do so, subject to
#   the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all copies or
#   substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
#   BUT NOT LIMITED TO THE
#   WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO
#   EVENT SHALL THE AUTHORS OR
#   COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
#   CONTRACT, TORT OR
#   OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#   DEALINGS IN THE SOFTWARE.
#
#   This uses QT for some components which has the primary open-source license is the GNU Lesser
#   General Public License v. 3 (“LGPL”).
#   With the LGPL license option, you can use the essential libraries and some add-on libraries
#   of Qt.
#   See https://www.qt.io/licensing/open-source-lgpl-obligations for QT details.

import ast
from datetime import date, datetime
import re


def to_text(item, normalize=False):
    """
    Converts a Python object into a string representation that is compatible with
    `ast.literal_eval`.
    This function handles common Python types including nested hierarchies and ensures proper
    formatting for compatibility with evaluation and representation needs.

    Args:
        item: The data structure to format. Supported types include:
            - `dict`: Converted into a string with properly formatted key-value pairs.
            - `list`: Converted into a string representation of a list.
            - `str`: Encased in single quotes, ensuring compatibility with evaluators.
            - `int` or `float`: Directly converted into their string representations.
            - `bool`: Represented as `True` or `False` in the string.
            - `None`: Represented as the string ``.
            - `date`: Converted to an ISO-formatted string enclosed in single quotes.

        normalize (bool): If `True`, applies normalization rules to standardize strings for
        certain cases.  Ensures proper escaping of characters in strings using `repr` when
        normalizing.

    Returns:
        str: A string representation of the object, formatted to be compatible with
        `ast.literal_eval`.

    Raises:
        TypeError: If the input object is of an unsupported type.

    Notes:
        - Nested structures (e.g., lists within dictionaries) are handled recursively.
        - The `normalize` flag affects how strings are represented, enabling additional
        standardization when needed.
    """
    # Handle dictionaries by converting each key-value pair into a formatted string
    if isinstance(item, dict):
        formatted_pairs = [f"'{key}': {to_text(val if val is not None and val != '' else '', True)}"
            for key, val in item.items()]
        result = "{" + ", ".join(formatted_pairs) + "}"
        return result

    # Handle lists by converting each element into its formatted string representation
    elif isinstance(item, list):
        formatted_elements = [to_text(element, True) for element in item]
        return "[" + ", ".join(formatted_elements) + "]"

    # Handle booleans by mapping them to their Python string equivalents
    elif isinstance(item, bool):
        return "True" if item else "False"

    # Handle numbers (int and float) by converting directly to their string representation
    elif isinstance(item, (int, float)):
        return str(item)

    # Handle strings, optionally normalizing if the flag is set
    elif isinstance(item, str):
        if normalize:
            # Use `repr` to ensure proper quoting and escaping of special characters, e.g., '\n',
            # '\t'
            return repr(item)
        # Default behavior, return as-is
        return f"{item}"

    # Handle NoneType as the string ""
    elif item is None:
        return "''"

    # Handle date objects by formatting them into ISO 8601 strings wrapped in single quotes
    elif isinstance(item, date):
        return f"'{item.isoformat()}'"

    # Handle tuples
    elif isinstance(item, tuple):
        formatted_elements = [to_text(element, True) for element in item]
        return "(" + ", ".join(formatted_elements) + ("," if len(item) == 1 else "") + ")"
    # Raise an error for unsupported types
    else:
        raise TypeError(f"Unsupported type: {type(item).__name__}")


DEFAULT_FALLBACKS = {
    int: -9999,  # Default fallback for integers
    float: -9999.9,  # Default fallback for floats
    bool: False,  # Default fallback for booleans
    str: "ERROR",  # Default fallback for strings
    date: date(1900, 1, 1),  # Default fallback for dates
    dict: None,  # Default fallback for dictionaries
    list: None,  # Default fallback for lists
    tuple: None,
}

def get_default_fallbacks():
    """
    Retrieve the DEFAULT_FALLBACKS dictionary.
    DEFAULT_FALLBACKS is a dictionary that provides default fallback values for
    various data types (e.g., int, float, str) when text cannot be parsed correctly.

    Defaults:
        - `int`: -9999
        - `float`: -9999.9
        - `bool`: False
        - `str`: "ERROR"
        - `date`: datetime.date(1900, 1, 1)
        - `dict`, `list`, `tuple`: None

    Returns:
        dict: Dictionary of fallback values for parsing failures.
    """
    return DEFAULT_FALLBACKS


def parse_text(text, target_type, rgx=None, fallbacks=None):
    """
    Parse a string into a Python object (e.g., dictionary, list, scalar, or nested structure).
    The input string must be in a format compatible with Python's `ast.literal_eval`.

    Args:
        text (str): The input string to parse.
        target_type (type): The desired type of the output (e.g., int, float, str, bool, date,
        etc.).
        rgx: Optional parameter for additional handling.
        fallbacks: Override default fallbacks.

    Returns:
        tuple: (error_flag, result)
            - error_flag (bool): Indicates if parsing errors or type mismatches occurred.
            - result: The parsed object if successful, or a fallback value if parsing fails.
    Raises:
        None: Any exceptions during parsing are handled internally and result in a fallback value.

    Fallback Handling:
        If parsing fails or the result does not match the desired target type:
        - The function assigns a default fallback value from `DEFAULT_FALLBACKS` based on the
          specified `target_type`.
        - If `target_type` is not in `DEFAULT_FALLBACKS`, `None` is returned as the fallback value.
        - The DEFAULT_FALLBACKS can be overridden with `fallbacks`.

    Notes:
        - Parsing is performed using `ast.literal_eval` for security and compatibility.
        - Nested structures (e.g., lists or dictionaries) are handled recursively.
        - Scalar values are converted to the `target_type` if specified.
    """
    # Use the provided fallbacks or default to `DEFAULT_FALLBACKS` if not provided
    fallbacks = fallbacks or DEFAULT_FALLBACKS

    # Validate against rgx
    if rgx:
        info(f"check regex: val={text} rgx={rgx}")
        valid = validate_text(text, rgx)
        if not valid:
            info(f"regex validation failed for '{text}'")
            if target_type is str:
                # Strings are always returned as-is
                return True, text

            # Assign fallback value based on the target type
            value = fallbacks.get(target_type, None)
            return True, value

    info(f"parse text: {text} target_type={target_type}")

    if target_type is str:
        # Strings are always returned as-is
        return False, text

    # Attempt parsing and initial type matching
    error_flag, value = _parse_text(text, target_type, rgx)

    # If parsing fails or the result does not match the target type
    if error_flag or (target_type and not isinstance(value, target_type)):
        # Assign fallback value based on the target type
        value = fallbacks.get(target_type, None)
        error_flag = True

    return error_flag, value


def _parse_text(text, target_type=None, rgx=None):
    """
    Internal recursive function to parse a string into a Python object (e.g., dictionary, list,
    or scalar).

    Args:
        text (str): The input string to parse.
        target_type (type, optional): Desired data type for the result.
        rgx: Optional parameter for additional handling (not implemented in this version).

    Returns:
        tuple: (error_flag, result)
            - error_flag (bool): True if parsing errors or mismatches occurred, False otherwise.
            - result: The parsed object, or None if parsing fails.

    Notes:
        - Handles dictionaries and lists recursively.
        - Uses `_convert_value` to ensure scalar values match the desired target type.
    """
    try:
        # Attempt parsing the string with `ast.literal_eval`
        info(f"parsing <{text}>")
        result = ast.literal_eval(text)

        # Handle dictionaries by recursively parsing keys and values
        if isinstance(result, dict):
            parsed_dict = {}
            error_flag = False
            for key, value in result.items():
                sub_error, sub_result = _parse_text(repr(value), None, rgx)
                error_flag |= sub_error
                parsed_dict[key] = sub_result
                if error_flag:
                    info(f"parsing error1 for '{key}' value '{value}'")
            return error_flag, parsed_dict

        # Handle lists by recursively parsing each element
        elif isinstance(result, list):
            parsed_list = []
            error_flag = False
            for item in result:
                sub_error, sub_result = _parse_text(repr(item), None, rgx)
                error_flag |= sub_error
                parsed_list.append(sub_result)
                if error_flag:
                    info(f"parsing error2 for value '{item}'")
            return error_flag, parsed_list

        # Handle tuples
        elif isinstance(result, tuple):
            parsed_tuple = []
            error_flag = False
            for item in result:
                sub_error, sub_result = _parse_text(repr(item), None, rgx)
                error_flag |= sub_error
                parsed_tuple.append(sub_result)
            if error_flag:
                info(f"parsing error3 for '{tuple}'")
            return error_flag, tuple(parsed_tuple)

        # Scalar values: Convert to target type if specified
        if target_type:
            type_error, converted = _convert_value(result, target_type)
            if type_error:
                info(f"convert error for '{result}'")
            return type_error, converted

        # Return the scalar value as-is if no target type is specified
        return False, result

    except (ValueError, SyntaxError, TypeError) as e:
        # Handle parsing errors by returning an error flag and None
        info(f"parsing error4 for '{text}'")
        return True, None


def _ast_dictionary(txt):
    """
    Create an AST formatted dictionary string, ensuring proper formatting with quoted keys and values.

    Args:
        txt (str): The input string containing key-value pairs in simplified dictionary-like format.
                   Example: "key1: value1, key2: value2"

    Returns:
        str: An AST formatted dictionary string with single quotes around keys and values.
             Example: "{'key1': 'value1', 'key2': 'value2'}"

    Notes:
        - Ensures the input text is enclosed in curly braces `{}`.
        - Utilizes `format_key_value_pairs` to process individual key-value pairs.
    """
    # Add enclosing braces if not present and content is non-empty
    if txt and (not txt.startswith("{") or not txt.endswith("}")):
        txt = f"{{{txt}}}"

    # Process the content inside the braces and build an AST dictionary string
    text_content = txt.strip("{}")  # Remove braces for processing
    return f"{{{_ast_key_value_pairs(text_content)}}}"


def _ast_key_value_pairs(text):
    """
    Convert a simple string of key-value pairs into an AST-style formatted string.

    This function takes a string containing key-value pairs separated by commas
    (e.g., "key1: value1, key2: value2") and returns a formatted string where
    both the keys and values are enclosed in single quotes
    (e.g., "'key1': 'value1', 'key2': 'value2'").

    Args:
        text (str): A string of key-value pairs, where each pair is separated
                    by a comma and each key and value is separated by a colon.
                    Example: "key1: value1, key2: value2"

    Returns:
        str: A formatted string with keys and values wrapped in single quotes.
             Example: "'key1': 'value1', 'key2': 'value2'"

    Raises:
        ValueError: If a key-value pair does not contain exactly one colon.

    Notes:
        - Leading and trailing whitespace or quotes around keys and values are removed.
        - If a value is empty, it is explicitly set to an empty string (`''`).
        - Each key-value pair is processed independently, and the formatted pairs
          are joined into a single output string.
    """
    formatted_pairs = []  # List to hold formatted key-value pairs
    pairs = text.split(",")  # Split input string into individual key-value pairs

    for pair in pairs:
        key_value = pair.split(":")  # Split each pair into key and value
        if len(key_value) == 2:
            key, value = key_value

            # Clean up the key and value by removing whitespace and surrounding quotes
            key = key.strip().strip("'").strip('"')
            value = value.strip().strip("'").strip('"')

            # Enclose the cleaned key in single quotes
            key = f"'{key}'"

            # Enclose the value in single quotes or set it to an empty string if blank
            value = f"'{value}'" if value else "''"

            # Append the formatted key-value pair to the list
            formatted_pairs.append(f"{key}: {value}")
        else:
            # Raise an error if the pair does not have exactly one colon
            raise ValueError(f"Invalid key-value pair: {pair.strip()}")

    # Combine the formatted pairs into a single string separated by commas
    return ", ".join(formatted_pairs)



def validate_text(text, regex):
    """
    Validates if a string fully matches a specified regex pattern.

    Parameters:
        text (str): The string to validate.
        regex (str): The regex pattern to match.

    Returns:
        bool: True if the string matches the regex or regex is None, False otherwise.
    """
    return bool(re.fullmatch(regex, text)) if text and regex else True


def _convert_value(value, target_type):
    """
    Convert a scalar value to the specified target type.

    Args:
        value: The input scalar value to convert.
        target_type (type): The desired type of the output.

    Returns:
        tuple: (error_flag, result)
            - error_flag (bool): True if conversion fails, False otherwise.
            - result: The converted value, or None if conversion fails.

    Notes:
        - Includes specific logic for converting to `int`, `float`, `bool`, `str`, and `date`.
    """
    try:
        # Convert to integer if possible
        if target_type == int:
            if isinstance(value, int):
                return False, value
            if isinstance(value, str) and value.strip().lstrip('-').isdigit():
                return False, int(value.strip())
            return True, None

        # Convert to float if possible
        elif target_type == float:
            if isinstance(value, (int, float)):
                return False, float(value)
            if isinstance(value, str):
                return False, float(value.strip())
            return True, None

        # Convert to boolean if possible
        elif target_type == bool:
            if isinstance(value, bool):
                return False, value
            if isinstance(value, (int, str)):
                return False, bool(int(value))
            return True, None

        # Convert to string
        elif target_type == str:
            return False, str(value)

        # Convert to date
        elif target_type == date:
            if isinstance(value, str):
                return False, datetime.strptime(value.strip(), "%Y-%m-%d").date()
            return True, None

        # Unsupported target types
        else:
            return True, None

    except (ValueError, TypeError):
        # Handle conversion errors
        return True, None


def data_type(item):
    """
    Identifies the item's data type (List, Dict, int, float, bool, str).

    Parameters:
        item: The item to categorize.

    Returns:
        The identified data type.
    """
    return type(item)


def warn(text):
    pass


def info(text):
    pass
