import pytest

from ransack.exceptions import ParseError
from ransack.parser import Parser


@pytest.fixture
def parser():
    return Parser()  # Create a fresh instance of the parser for each test


# Test valid input: arithmetic expression
def test_valid_expression(parser):
    valid_input = "3 + 5 * (10 - 2)"
    tree = parser.parse_only(valid_input)
    assert tree is not None, "Parsing failed for valid input"
    assert "add" in tree.pretty(), "Addition rule was not applied"
    assert "mul" in tree.pretty(), "Multiplication rule was not applied"


# Test another valid expression
def test_valid_expression_2(parser):
    valid_input = "-5 * (2 + 3)"
    tree = parser.parse_only(valid_input)
    assert tree is not None, "Parsing failed for valid input"
    assert "neg" in tree.pretty(), "Negation rule was not applied"


# Test invalid input: Malformed arithmetic expression
def test_invalid_expression(parser):
    invalid_input = "3 + * 5"  # Malformed
    with pytest.raises(ParseError):
        parser.parse_only(invalid_input)


# Test another invalid input: Unmatched parentheses
def test_invalid_expression_2(parser):
    invalid_input = "(3 + 5 * 2"
    with pytest.raises(ParseError):
        parser.parse_only(invalid_input)


# Test handling of unknown symbols
def test_invalid_symbols(parser):
    invalid_input = "3 + 5 ^ 2"  # "^" is not a valid symbol in the grammar
    with pytest.raises(ParseError):
        parser.parse_only(invalid_input)


# Test for modulo operation
def test_modulo(parser):
    tree = parser.parse_only("10 % 3")
    assert tree is not None
    assert "mod" in tree.pretty()


# Test for logical `or` operation
def test_logical_or(parser):
    tree = parser.parse_only("a or b")
    assert tree is not None
    assert "or_op" in tree.pretty()
    tree = parser.parse_only("a || b")
    assert tree is not None
    assert "or_op" in tree.pretty()


# Test for logical `and` operation
def test_logical_and(parser):
    tree = parser.parse_only("a and b")
    assert tree is not None
    assert "and_op" in tree.pretty()
    tree = parser.parse_only("a && b")
    assert tree is not None
    assert "and_op" in tree.pretty()


# Test for logical `not` operation
def test_logical_not(parser):
    tree = parser.parse_only("not a")
    assert tree is not None
    assert "not_op" in tree.pretty()
    tree = parser.parse_only("!a")
    assert tree is not None
    assert "not_op" in tree.pretty()


# Test for comparison `>` operator
def test_comparison_gt(parser):
    tree = parser.parse_only("5 > 3")
    assert tree is not None
    assert "gt" in tree.pretty()


# Test for comparison `>=` operator
def test_comparison_gte(parser):
    tree = parser.parse_only("5 >= 5")
    assert tree is not None
    assert "gte" in tree.pretty()


# Test for comparison `<` operator
def test_comparison_lt(parser):
    tree = parser.parse_only("3 < 5")
    assert tree is not None
    assert "lt" in tree.pretty()


# Test for comparison `<=` operator
def test_comparison_lte(parser):
    tree = parser.parse_only("5 <= 5")
    assert tree is not None
    assert "lte" in tree.pretty()


# Test for comparison `==` operator
def test_comparison_eq(parser):
    tree = parser.parse_only("5 == 5")
    assert tree is not None
    assert "eq" in tree.pretty()


# Test combination of arithmetic, logical, and comparison expressions
def test_arithmetic_logic_comparison_combined(parser):
    tree = parser.parse_only("(3 + 5) > 2 and a")
    assert tree is not None
    assert "and_op" in tree.pretty()
    assert "gt" in tree.pretty()


# Test for nested logical and comparison expressions
def test_nested_logical_comparison_expressions(parser):
    tree = parser.parse_only("not (a and b) or (1 + 1 == 2)")
    assert tree is not None
    assert "or_op" in tree.pretty()
    assert "not_op" in tree.pretty()
    assert "and_op" in tree.pretty()
    assert "eq" in tree.pretty()


# Test for invalid logical expressions
def test_invalid_logical_expression(parser):
    with pytest.raises(ParseError):
        parser.parse_only("a or or b")  # Invalid expression


# Test for IN operator with a valid list
def test_in_operator(parser):
    tree = parser.parse_only("Source.Port IN [22, 80, 443]")
    assert tree is not None
    assert "in_op" in tree.pretty()


# Test for IN operator with a list of strings
def test_in_operator_with_strings(parser):
    tree = parser.parse_only('Service.Name in ["http", "https"]')
    assert tree is not None
    assert "in_op" in tree.pretty()


# Test for IN operator case insensitivity
def test_in_operator_case_insensitive(parser):
    tree = parser.parse_only("Source.Port in [21, 22, 443]")
    assert tree is not None
    assert "in_op" in tree.pretty()


# Test for CONTAINS operator
def test_contains_operator(parser):
    tree = parser.parse_only("'abcdefghi' CONTAINS 'def'")
    assert tree is not None
    assert "contains_op" in tree.pretty()


# Test for CONTAINS operator case insensitivity
def test_contains_operator_case_insensitive(parser):
    tree = parser.parse_only("description contains 'login'")
    assert tree is not None
    assert "contains_op" in tree.pretty()


# Test numbers with a exponent in a list
def test_floats_in_list(parser):
    tree = parser.parse_only("[24E10, 10e12, 0.4E+112, 21e-20]")
    assert tree is not None
    for x in "24E10", "10e12", "0.4E+112", "21e-20":
        assert x in tree.pretty()


# Test for invalid syntax that should raise an error
def test_invalid_in_syntax(parser):
    with pytest.raises(ParseError):
        parser.parse_only("Source.Port IN 22, 80, 443")


# Test concat on strings
def test_concat_strings(parser):
    tree = parser.parse_only("'abc' . 'def'")
    assert tree is not None
    assert "concat_op" in tree.pretty()


# Test concat no whitespace
def test_concat_strings_no_whitespace(parser):
    tree = parser.parse_only("'abc'.'def'")
    assert tree is not None
    assert "concat_op" in tree.pretty()


# Test concat on lists
def test_concat_lists(parser):
    tree = parser.parse_only("[123, 132] . [32, 424, 42]")
    assert tree is not None
    assert "concat_op" in tree.pretty()


# Test for IPv4
def test_ipv4(parser):
    # Test basic IPv4 address
    tree = parser.parse_only("192.168.0.0")
    assert tree is not None
    assert "ipv4" in tree.pretty()
    assert "ipv4_single" in tree.pretty()

    # Test IPv4 address with CIDR notation
    tree = parser.parse_only("192.168.0.1/24")
    assert tree is not None
    assert "ipv4" in tree.pretty()
    assert "ipv4_cidr" in tree.pretty()


# Test for IPv6
def test_ipv6(parser):
    # Test basic IPv6 address
    tree = parser.parse_only("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
    assert tree is not None
    assert "ipv6" in tree.pretty()
    assert "ipv6_single" in tree.pretty()

    # Test IPv6 address with CIDR notation
    tree = parser.parse_only("2001:0db8:85a3:0000:0000:8a2e:0370:7334/64")
    assert tree is not None
    assert "ipv6" in tree.pretty()
    assert "ipv6_cidr" in tree.pretty()


def test_datetime(parser):
    dtimes = [
        "2024-01-01T12:00:00Z",
        "2024-01-01T12:00:00z",
        "2024-01-01T12:00:00.123Z",
        "2024-01-01T12:00:00.123z",
        "2024-01-01T12:00:00+02:00",
        "2024-01-01T12:00:00-02:00",
        "2024-01-01T12:00:00.123+02:00",
        "2024-01-01T12:00:00.123-02:00",
        "2024-01-01 12:00:00Z",
        "2024-01-01 12:00:00z",
        "2024-01-01 12:00:00.123Z",
        "2024-01-01 12:00:00.123z",
        "2024-01-01 12:00:00+02:00",
        "2024-01-01 12:00:00-02:00",
        "2024-01-01 12:00:00.123+02:00",
        "2024-01-01 12:00:00.123-02:00",
        "2024-01-01 12:00:00",
        "2024-01-01 12:00:00.123",
        "2024-10-14",
    ]

    for dtime in dtimes:
        tree = parser.parse_only(dtime)
        assert tree is not None
        assert "datetime" in tree.pretty()


def test_datetime_invalid(parser):
    dtimes = ["2024-01-01T12:00", "2024-01-01T12:00:00+02:00:00"]

    for dtime in dtimes:
        with pytest.raises(ParseError):
            parser.parse_only(dtime)


def test_timedelta(parser):
    timedeltas = [
        "01:00:00",  # Basic time format (hours, minutes, seconds)
        "1d01:00:00",  # Days included
        "10D23:59:59",  # Days, uppercase 'D'
        "00:00:00",  # Zero time
        "99:59:59",  # Large hour value
        "5d00:00:00",  # Multiple days
    ]

    for tdelta in timedeltas:
        tree = parser.parse_only(tdelta)
        assert tree is not None
        assert "timedelta" in tree.pretty()


# Test invalid timedelta input - only day, no time
def test_timedelta_only_day(parser):
    with pytest.raises(ParseError):
        parser.parse_only("1D")


# Test for strings enclosed in double quotes
def test_string_double_quotes(parser):
    tree = parser.parse_only('"hello world"')
    assert tree is not None
    assert "string" in tree.pretty()
    assert "hello world" in tree.pretty()


# Test for strings enclosed in single quotes
def test_string_single_quotes(parser):
    tree = parser.parse_only("'hello world'")
    assert tree is not None
    assert "string" in tree.pretty()
    assert "hello world" in tree.pretty()


# Test for strings with special characters inside
def test_string_with_special_chars(parser):
    special_input = '"special!@#$%^&*()_+-={}|[]:;<>,.?"'
    tree = parser.parse_only(special_input)
    assert tree is not None
    assert "string" in tree.pretty()
    assert special_input in tree.pretty()

# Test empty strings
def test_string_empty(parser):
    tree = parser.parse_only('""')
    assert tree is not None
    assert "string" in tree.pretty()
    tree = parser.parse_only("''")
    assert tree is not None
    assert "string" in tree.pretty()

# Test for strings in a larger expression (within arithmetic expression)
def test_string_in_expression(parser):
    tree = parser.parse_only('"hello" + "world"')
    assert tree is not None
    assert "add" in tree.pretty()
    assert "string" in tree.pretty()
    assert "hello" in tree.pretty()
    assert "world" in tree.pretty()


# Test for strings with array indexing
def test_string_with_index(parser):
    tree = parser.parse_only('"list[0]"')
    assert tree is not None
    assert "string" in tree.pretty()
    assert "[0]" in tree.pretty()


# Test a simple single-letter variable
def test_single_variable(parser):
    tree = parser.parse_only("S")
    assert "variable" in tree.pretty()
    assert "S" in tree.pretty()


# Test a simple variable with one dot notation
def test_variable_with_dot(parser):
    tree = parser.parse_only("S.N")
    assert "variable" in tree.pretty()
    assert "S.N" in tree.pretty()


# Test a longer variable with multiple dot notations
def test_variable_long_with_dot(parser):
    tree = parser.parse_only("Source.Node")
    assert "variable" in tree.pretty()
    assert "Source.Node" in tree.pretty()


# Test a variable with indices
def test_variable_with_indices(parser):
    with pytest.raises(ParseError):
        parser.parse_only("Source[1].Node[2]")


# Test a combination of variables and strings
def test_variable_with_string(parser):
    tree = parser.parse_only('Source.Node + "string"')
    assert "variable" in tree.pretty()
    assert "Source.Node" in tree.pretty()
    assert "string" in tree.pretty()


# Test a variable with dot prefix
def test_variable_dot(parser):
    tree = parser.parse_only(".count > target_count")
    assert "variable" in tree.pretty()
    assert ".count" in tree.pretty()
    assert "target_count" in tree.pretty()


# Test parsing a function with arguments
def test_function_with_arguments():
    parser = Parser()
    tree = parser.parse_only("addition(13, 43)")
    assert "function" in tree.pretty()
    assert "args" in tree.pretty()
    assert "number" in tree.pretty()


# Test parsing a function with a single argument
def test_function_with_single_argument():
    parser = Parser()
    tree = parser.parse_only("single_argument(-42.24)")
    assert "function" in tree.pretty()
    assert "args" in tree.pretty()
    assert "number" in tree.pretty()


# Test parsing a function with no arguments
def test_function_with_no_arguments():
    parser = Parser()
    tree = parser.parse_only("_emptyFunction()")
    assert "function" in tree.pretty()
    assert "None" in tree.pretty()


# Test function with a single character name
def test_function_with_short_name(parser):
    tree = parser.parse_only("f()")
    assert tree is not None
    assert "function" in tree.pretty()


def test_function_in_list():
    parser = Parser()
    tree = parser.parse_only("[addition(13, 43), subtraction(22, 10)]")
    assert (
        tree.pretty()
        == """\
list
  function
    addition(
    args
      number	13
      number	43
  function
    subtraction(
    args
      number	22
      number	10
"""
    )


# Test function call from within a function
def test_nested_function_calls():
    parser = Parser()
    tree = parser.parse_only("outer(inner(10), 20)")
    assert (
        tree.pretty()
        == """\
function
  outer(
  args
    function
      inner(
      args
        number	10
    number	20
"""
    )


def test_function_with_strings():
    parser = Parser()
    tree = parser.parse_only('print("Hello, World!")')
    assert "function" in tree.pretty()
    assert "string" in tree.pretty()


def test_function_with_variable():
    parser = Parser()
    tree = parser.parse_only("processData(data)")
    assert "function" in tree.pretty()
    assert "variable" in tree.pretty()


def test_function_with_ipv4():
    parser = Parser()
    tree = parser.parse_only("validateIp(192.168.0.1)")
    assert "function" in tree.pretty()
    assert "ipv4" in tree.pretty()


def test_function_with_mixed_arguments():
    parser = Parser()
    tree = parser.parse_only('doSomething(13, "text", myVar)')
    assert "function" in tree.pretty()
    assert "number" in tree.pretty()
    assert "string" in tree.pretty()
    assert "variable" in tree.pretty()


# Test parsing a list of numbers
def test_list_of_numbers(parser):
    tree = parser.parse_only("[1, 2, 3, 4, 5]")
    assert tree is not None
    assert "list" in tree.pretty()
    assert "number" in tree.pretty()


# Test parsing a list without whitespace
def test_list_no_whitespace(parser):
    tree = parser.parse_only("[1,2,3,4,5]")
    assert tree is not None
    assert (
        tree.pretty()
        == """\
list
  number	1
  number	2
  number	3
  number	4
  number	5
"""
    )


# Test parsing a list of mixed types (numbers, IPv4, IPv6)
def test_list_of_mixed_types(parser):
    tree = parser.parse_only("[123, 3.14, 192.168.0.1, 2001:0db8:85a3::7334]")
    assert tree is not None
    assert "list" in tree.pretty()
    assert "number" in tree.pretty()
    assert "ipv4" in tree.pretty()
    assert "ipv6" in tree.pretty()


# Test parsing a list of IPv4 addresses
def test_list_of_ipv4(parser):
    tree = parser.parse_only("[192.168.1.1, 10.0.0.1, 172.16.0.1]")
    assert tree is not None
    assert "list" in tree.pretty()
    assert "ipv4" in tree.pretty()


# Test parsing a list of IPv6 addresses
def test_list_of_ipv6(parser):
    tree = parser.parse_only("[fe80::1, 2001:0db8:85a3::8a2e:0370:7334]")
    assert tree is not None
    assert "list" in tree.pretty()
    assert "ipv6" in tree.pretty()


# Test parsing a list of strings
def test_list_of_strings(parser):
    tree = parser.parse_only('["constant1", "constant2", "constant3"]')
    assert tree is not None
    assert "list" in tree.pretty()
    assert "string" in tree.pretty()


# Test parsing an empty list
def test_empty_list(parser):
    tree = parser.parse_only("[]")
    assert tree is not None
    assert "list" in tree.pretty()


# Test parsing a single element list
def test_single_element_list(parser):
    tree = parser.parse_only("[42]")
    assert tree is not None
    assert "list" in tree.pretty()
    assert "number" in tree.pretty()


# Test parsing a list with missing commas (invalid list)
def test_invalid_list_missing_commas(parser):
    invalid_input = "[1 2 3]"
    with pytest.raises(ParseError):
        parser.parse_only(invalid_input)


# Test parsing a list with missing closing bracket (invalid list)
def test_invalid_list_missing_closing_bracket(parser):
    invalid_input = "[1, 2, 3"
    with pytest.raises(ParseError):
        parser.parse_only(invalid_input)


# Test parsing a list with invalid elements
def test_invalid_list_elements(parser):
    invalid_input = "[1, &]"
    with pytest.raises(ParseError):
        parser.parse_only(invalid_input)


# Test parsing a nested list
def test_nested_list(parser):
    tree = parser.parse_only("[[1, 2], [3, 4], [5]]")
    assert tree is not None
    assert "list" in tree.pretty()


# Test for number range with integer bounds
def test_integer_range(parser):
    tree = parser.parse_only("port in 1..1024")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test for number range with float bounds
def test_float_range(parser):
    tree = parser.parse_only("x in 1.5..10.75")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test for number range with a negative lower bound and positive upper bound
def test_negative_to_positive_range(parser):
    tree = parser.parse_only("temperature in -10..50")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test for number range with negative integer bounds
def test_negative_integer_range(parser):
    tree = parser.parse_only("x in -100..-1")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test for number range with a negative float lower bound and positive float upper bound
def test_negative_float_to_positive_float_range(parser):
    tree = parser.parse_only("temperature in -5.5..25.75")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test for number range with both negative float bounds
def test_negative_float_range(parser):
    tree = parser.parse_only("x in -10.5..-1.25")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test for number range with zero as a boundary
def test_zero_to_positive_range(parser):
    tree = parser.parse_only("x in 0..100")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test for number range with zero as the lower bound and a negative upper bound
def test_zero_to_negative_range(parser):
    tree = parser.parse_only("x in 0..-50")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test number range without IN operator
def test_only_number_range(parser):
    tree = parser.parse_only("10..123")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test number range with whitespace
def test_number_range_with_whitespace(parser):
    tree = parser.parse_only("10   ..		123")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test for a range with an invalid range operator (e.g., `...` instead of `..`)
def test_invalid_range_operator(parser):
    with pytest.raises(ParseError):
        parser.parse_only("x in 5...10")


# Test for IPv4 range with dash (-)
def test_ipv4_range_dash(parser):
    tree = parser.parse_only("192.168.0.1-192.168.0.255")
    assert tree is not None
    assert "ipv4_range" in tree.pretty()


# Test for IPv4 range with double dots (..)
def test_ipv4_range_double_dot(parser):
    tree = parser.parse_only("192.168.0.1..192.168.0.255")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test for IPv6 range with dash (-)
def test_ipv6_range_dash(parser):
    tree = parser.parse_only("2001:0db8::0370:7334-2001:0db8::0370:7335")
    assert tree is not None
    assert "ipv6_range" in tree.pretty()


# Test for IPv6 range with double dots (..)
def test_ipv6_range_double_dot(parser):
    tree = parser.parse_only("2001:0db8::0370:7334..2001:0db8::0370:7335")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test for datetime range
def test_datetime_range(parser):
    tree = parser.parse_only("2024-01-01T12:00:00Z..2024-01-02T12:00:00Z")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test for a range with a variable
def test_range_with_variable(parser):
    tree = parser.parse_only("12 .. max(port)")
    assert tree is not None
    assert "range_op" in tree.pretty()


# Test invalid number range
def test_invalid_number_range(parser):
    invalid_input = "10.."
    with pytest.raises(ParseError):
        parser.parse_only(invalid_input)


# Test invalid IPv4 range
def test_invalid_ipv4_range(parser):
    invalid_input = "192.168.0.1.."
    with pytest.raises(ParseError):
        parser.parse_only(invalid_input)


# Test invalid IPv6 range
def test_invalid_ipv6_range(parser):
    invalid_input = "2001:0db8::0370:7334.."
    with pytest.raises(ParseError):
        parser.parse_only(invalid_input)


# Test invalid datetime range
def test_invalid_datetime_range(parser):
    invalid_input = "2024-01-01T12:00:00Z.."
    with pytest.raises(ParseError):
        parser.parse_only(invalid_input)


def test_exists(parser):
    tree = parser.parse_only("DetectTime??")
    assert tree is not None
    assert "exists_op" in tree.pretty()


def test_invalid_exists(parser):
    invalid_input = "14??"
    with pytest.raises(ParseError):
        parser.parse_only(invalid_input)


def test_exists_with_default_variable(parser):
    tree = parser.parse_only("DetectTime??CeaseTime")
    assert tree is not None
    assert "exists_with_default" in tree.pretty()


def test_exists_with_default_value(parser):
    tree = parser.parse_only("DetectTime??2024-12-12")
    assert tree is not None
    assert "exists_with_default" in tree.pretty()


def test_exists_with_default_value_2(parser):
    tree = parser.parse_only("Port ?? 1024")
    assert tree is not None
    assert "exists_with_default" in tree.pretty()


def test_function_and_logical_expression(parser):
    expression = (
        "FunctionA(Source.IP4) and "
        + "(Source.Port > 1024 or "
        + "Target.IP4 in ['192.168.1.1', '10.0.0.1'])"
    )
    tree = parser.parse_only(expression)
    assert tree.data == "and_op"
    assert tree.children[0].data == "function"
    assert tree.children[1].data == "or_op"


def test_negation_with_and(parser):
    expression = "not (Source.IP4 in ['10.0.0.1', '10.0.0.2'] and Target.Port == 443)"
    tree = parser.parse_only(expression)
    assert tree.data == "not_op"
    assert tree.children[0].data == "and_op"


def test_ip_range_with_and_or(parser):
    expression = (
        "Source.IP4 >= 192.168.0.0 and "
        + "Source.IP4 <= 192.168.255.255 or "
        + "Target.IP4 == 10.0.0.1"
    )
    tree = parser.parse_only(expression)
    assert tree.data == "or_op"
    assert tree.children[0].data == "and_op"
    assert tree.children[1].data == "eq"


def test_nested_lists_and_types(parser):
    expression = (
        "Category in ['Attack', 'Exploit'] and "
        + "Source.Port in [22, 80, 443] and "
        + "Target.Proto in ['http', 'https', 'ftp']"
    )
    tree = parser.parse_only(expression)
    assert (
        tree.pretty()
        == """\
and_op
  and_op
    in_op
      variable	Category
      list
        string	'Attack'
        string	'Exploit'
    in_op
      variable	Source.Port
      list
        number	22
        number	80
        number	443
  in_op
    variable	Target.Proto
    list
      string	'http'
      string	'https'
      string	'ftp'
"""
    )


def test_ignoring_of_newline(parser):
    tree = parser.parse_only("12\n + 15\n\n")
    assert tree is not None
    assert (
        tree.pretty()
        == """\
add
  number	12
  number	15
"""
    )


def test_complex_expression(parser):
    expression = (
        "Category in ['Attempt.Exploit'] and "
        + "(Target.Port in [80, 443] or "
        + "Source.Proto in ['http', 'https', 'http-alt'] or "
        + "Target.Proto in ['http', 'https', 'http-alt'])"
    )
    tree = parser.parse_only(expression)
    assert (
        tree.pretty()
        == """\
and_op
  in_op
    variable	Category
    list
      string	'Attempt.Exploit'
  or_op
    or_op
      in_op
        variable	Target.Port
        list
          number	80
          number	443
      in_op
        variable	Source.Proto
        list
          string	'http'
          string	'https'
          string	'http-alt'
    in_op
      variable	Target.Proto
      list
        string	'http'
        string	'https'
        string	'http-alt'
"""
    )
