from datetime import date

import pytest

from YMLEditor.structured_text import parse_text, to_text, DEFAULT_FALLBACKS

# Parameters and IDs for positive test cases
positive_test_cases = [  # (text, target_type, test_object)
    ("123", int, 123),  # 1
    ("-23", int, -23),  # 2
    ("3.1415", float, 3.1415),  # 3
    ("True", bool, True),  # 4
    ("False", bool, False),  # 5
    ("New Orleans", str, "New Orleans"),  # 6
    ("{'key7': '42', 'nested': {'bool': 'false', 'list': ['1', 2.5]}}", dict,
     {'key7': '42', 'nested': {'bool': 'false', 'list': ['1', 2.5]}}),  # 7
    ("[85, 'hello', 3.14, True]", list, [85, 'hello', 3.14, True]),  # 8
    ("'2024-09-23'", date, date(2024, 9, 23)),  # 9
    ("0", int, 0),  # 10
    ("3", float, 3),  # 11
    ("-3.1415", float, -3.1415),  # 12

    # Nested structures with mixed types
    ("{'int': 10, 'float': 1.1, 'list': [1, 2, '3']}", dict,
     {'int': 10, 'float': 1.1, 'list': [1, 2, '3']}),  # 13
    ("[{'a': 11}, {'b': 2}]", list, [{'a': 11}, {'b': 2}]),  # 14
    ("{'a': '12'}", dict, {'a': '12'}),  # 15
    # Additional deeply nested structures
    ("{'level1': {'level2': {'level3': 'deep'}}}", dict,
     {'level1': {'level2': {'level3': 'deep'}}}), # 16
    ("[{'nested_dict': {'key': [1, 2, 3]}}, {'another_list': [4.5, 'text']}]", list,
     [{'nested_dict': {'key': [1, 2, 3]}}, {'another_list': [4.5, 'text']}]),  # 17
    ("{'key': [1, {'inner_key': 'value'}, [True, False, '']]}", dict,
     {'key': [1, {'inner_key': 'value'}, [True, False, '']]}),  # 18
    ("[{'a': {'b': {'c': [1, 2, {'d': 3}]}}}, 'end']", list,
     [{'a': {'b': {'c': [1, 2, {'d': 3}]}}}, 'end']),  # 19
    ("{'a': [1, {'b': [2, {'c': '3'}]}]}", dict, {'a': [1, {'b': [2, {'c': '3'}]}]}),  # 20

    # Switches
    ("-s 21", str, "-s 21"),  # 21
]

positive_test_ids = ["1 int:positive", "2 int:negative", "3 float:pi", "4 bool:true",
                     "5 bool:false", "6 str:New_Orleans", "7 dict:nested_structure", "8 list:mixed",
                     "9 date:valid", "10 int:zero", "11 float:no_decimal", "12 float:negative",
                     "13 dict:mixed_types", "14 list:dict_elements", "15 dict:simple",
                     "16 dict:deep_nested_levels", "17 list:deep_nested_mixed",
                     "18 dict:complex_list_structure", "19 list:multiple_nested_dicts",
                     "20 dict:nested_lists_and_dicts", "21 str:Switches"]


# Positive cases
@pytest.mark.parametrize(
    "text, target_type, test_object", positive_test_cases, ids=positive_test_ids, )
def test_to_text(text, target_type, test_object):
    """
    Test to_text for positive cases, including nested and mixed structures.
    """
    print(f"\n\nto_text({test_object},target_type={target_type.__name__})")
    result = to_text(test_object)
    print(f" Expected=: <<{text}>>\n       Got: <<{result}>>")
    assert result == text, f"Failed result: Expected={text}, Got={result}"


# Positive cases
@pytest.mark.parametrize(
    "text, target_type, test_object", positive_test_cases, ids=positive_test_ids, )
def test_parse_text(text, target_type, test_object):
    """
    Test parse_text for positive cases, including nested and mixed structures.
    """
    print(f"\nRunning: text={text}, target_type={target_type}")
    error, result = parse_text(text, target_type)
    print("Result:", result)
    assert result == test_object, f"Failed result: Expected={test_object}, Got={result}"
    assert type(
        result
    ) == target_type, (f"Failed type: Expected={target_type.__name__}, Got="
                       f"{type(result).__name__}")
    assert error == False, f"Failed error_flag: Expected=False, Got={error}"


# Test roundtrip conversion for valid inputs
# Positive cases
@pytest.mark.parametrize(
    "text, target_type, test_object", positive_test_cases, ids=positive_test_ids, )
def test_roundtrip(text, target_type, test_object):
    """
    Test roundtrip: to_text and parse_text back to obj for valid inputs.
    """
    txt = to_text(test_object)
    print(f"\nto_text result: {txt}")
    error_flag, parsed_obj = parse_text(txt, type(test_object))
    assert not error_flag, f"Parsing failed for: {txt}"
    assert parsed_obj == test_object, f"Roundtrip failed: Expected={test_object}, Got={parsed_obj}"


# Test parse_text for negative cases
@pytest.mark.parametrize(
    "text, target_type,  expected_result", [  # Invalid and malformed data
        ("not_a_number1", int, -9999), ("'string2'", int, -9999), ("33.6", int, -9999),
        ("'hello4'", float, -9999.9), ("'2024-05-99'", date, date(1900, 1, 1)),  # 5 Invalid date
        ("{'key6': aaa", dict, None),  # 6 Malformed dict
        ("[7, 2, aaa", list, None),  # 7 Malformed list
        ("3a", int, -9999),  # 8
        ("3b", float, -9999.9),  # 9
    ],
    ids=["1 int:invalid_string", "2 int:from_string", "3 int:float", "4 float:non-numeric_string",
         "5 date:invalid_format", "6 dict:malformed", "7 list:malformed", "8 int:malformed",
         "9 float:malformed", ], )

def test_parse_text_neg(text, target_type, expected_result):
    """
    Test parse_text for negative cases with invalid or malformed inputs.
    """
    print(f"\nRunning: text={text}, target_type={target_type}")
    error, result = parse_text(text, target_type)
    print("Result:", result)
    assert error == True, f"Failed error_flag: Expected=True, Got={error}"
    assert result == expected_result, f"Failed result: Expected={expected_result}, Got={result}"

# Test to_text for unsupported types
@pytest.mark.parametrize(
    "obj, expected_exception", [({1, 2, 3}, TypeError),  # Set is unsupported
                                (complex(1, 2), TypeError),  # Complex numbers are unsupported
                                ], ids=["unsupported:set", "unsupported:complex", ], )
def test_to_text_invalid_types(obj, expected_exception):
    """
    Test to_text for unsupported types.
    """
    with pytest.raises(expected_exception):
        to_text(obj)


@pytest.mark.parametrize(
    "text, target_type, expected_result",
    [("{'empty_list': [], 'empty_dict': {}}", dict, {'empty_list': [], 'empty_dict': {}}), (
            "{'nested': {'level1': {'level2': {'key': 'value'}}}}", dict,
            {'nested': {'level1': {'level2': {'key': 'value'}}}}), ("[]", list, []),
     ("{}", dict, {}), ],
    ids=["dict:empty_structures", "dict:deep_nested", "list:empty", "dict:empty", ], )

def test_parse_text_positive_edge_cases(text, target_type, expected_result):
    """
    Test parse_text for edge cases such as empty and deeply nested structures.
    """
    error, result = parse_text(text, target_type)
    assert result == expected_result, f"Expected={expected_result}, Got={result}"
    assert error == False, f"Expected error flag=False, Got={error}"


@pytest.mark.parametrize(
    "text, target_type, rgx, expected_error_flag, expected_result", [
        ("42", str, r"^\d{2}$", False, "42"),  #  1 two-digit:valid
        ("123", str, r"^\d{2}$", True, "123"), # 2 two_digits:invalid
        ("{'key': 'value', 'number': 42}", dict, r"^\{.*\}$|^\[.*\]$", False,
         {'key': 'value', 'number': 42}),  # 3 dict:valid
        ("[1, 2, 3, 'four']", list, r"^\{.*\}$|^\[.*\]$", False, [1, 2, 3, 'four']),  # 4 list:valid
        ("Not a dict or list", str, r"^\{.*\}$|^\[.*\]$", True, "Not a dict or list"),
        # 5 dict_or_list:invalid
        ("-z 123", str, r"^-z\s+\d+(\s+)?$", False, "-z 123"),  # 6 command_switch:valid
        ("--z 123", str, r"^-z\s+\d+(\s+)?$", True, "--z 123"),# 7 command_switch:invalid_dash
        ("-z", str, r"^-z\s+\d+(\s+)?$", True, "-z"),  # 8 command_switch:missing_value
    ],
    ids=["1 two_digits:valid", "2 two_digits:invalid", "3 dict:valid", "4 list:valid",
            "5 dict_or_list:invalid", "6 command_switch:valid", "7 command_switch:invalid_dash",
            "8 command_switch:missing_value", ]
)

def test_parse_text_with_regex(text, target_type, rgx, expected_error_flag, expected_result):
    """
    Test `parse_text` with regex validation for various cases.
    """
    error_flag, result = parse_text(text, target_type, rgx=rgx)

    # Assertions
    assert error_flag == expected_error_flag, (
        f"Error flag mismatch for text='{text}', rgx='{rgx}'. "
        f"Expected: {expected_error_flag}, Got: {error_flag}")
    assert result == expected_result, (f"Result mismatch for text='{text}', rgx='{rgx}'. "
                                       f"Expected: {expected_result}, Got: {result}")
