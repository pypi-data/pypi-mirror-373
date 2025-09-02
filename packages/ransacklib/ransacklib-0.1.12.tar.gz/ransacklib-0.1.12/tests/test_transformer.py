from datetime import datetime, timedelta

import pytest
from ipranges import IP4, IP6, IP4Net, IP4Range, IP6Net, IP6Range
from lark import Token

from ransack.exceptions import RansackError, ShapeError
from ransack.parser import Parser
from ransack.transformer import ExpressionTransformer, Filter, TokenWrapper, get_values


@pytest.fixture
def token():
    return Token("RULE", "value")


@pytest.fixture
def parser():
    return Parser()


@pytest.fixture
def expr_transformer():
    return ExpressionTransformer()


sample_data = {
    "Category": ["Intrusion.UserCompromise"],
    "ConnCount": 1,
    "Description": "Successful login using credentials",
    "Credentials": [{"Password": "P4ssw0rd123", "Username": "root"}],
    "NullKey": None,
    "Source": [
        {"IP4": ["1.2.3.235"], "Proto": ["tcp", "smtp"]},
        {"IP4": ["1.2.3.236"], "Proto": ["tcp", "smtp"]},
    ],
    "_Mentat": {
        "SourceResolvedASN": [111111],
        "SourceResolvedCountry": ["CZ"],
        "StorageTime": "2023-12-12",
        "NestedNullKey": None,
        "_private": 123,
    },
}


@pytest.fixture
def filter_():
    return Filter()


def test_token_wrapper_initialization(token):
    wrapper = TokenWrapper(token, "real_value")

    # Check the token and real_value attributes
    assert wrapper.token == token
    assert wrapper.real_value == "real_value"


def test_token_wrapper_getattr(token):
    wrapper = TokenWrapper(token, "real_value")

    # Access attributes of the wrapped token
    assert wrapper.type == "RULE"
    assert wrapper.value == "value"


def test_token_wrapper_real_value_property(token):
    wrapper = TokenWrapper(token, "initial_real_value")

    # Check the initial real_value
    assert wrapper.real_value == "initial_real_value"

    # Update the _real_value directly
    wrapper._real_value = "updated_real_value"
    assert wrapper.real_value == "updated_real_value"


class TestGetValues:
    def test_single_value(self):
        data = {"a": {"b": 42}}
        assert get_values(data, "a.b") == [42]

    def test_missing_key(self):
        data = {"a": {"b": 42}}
        assert get_values(data, "a.c") == []

    def test_empty_path(self):
        data = {"a": 1}
        assert get_values(data, "") == [data]

    def test_nested_list_aggregation(self):
        data = {"items": [{"value": 1}, {"value": 2}, {"value": 3}]}
        assert get_values(data, "items.value") == [1, 2, 3]

    def test_list_inside_list(self):
        data = {"group": [{"nums": [1, 2]}, {"nums": [3, 4]}]}
        assert get_values(data, "group.nums") == [1, 2, 3, 4]

    def test_nonexistent_path_in_list(self):
        data = {"group": [{"nums": [1, 2]}, {"other": 123}]}
        assert get_values(data, "group.nums") == [1, 2]

    def test_non_mapping_non_sequence(self):
        data = 123
        assert get_values(data, "any.path") == []


class TestExpressionTransformer:
    def parse_and_assert(
        self, parser, expr_transformer, expression, expected_type, expected_value
    ):
        """Parse the expression and assert the type and value of the result."""
        result = (
            expr_transformer.transform(parser.parse_only(expression))
            .children[0]
            .real_value
        )
        assert isinstance(result, expected_type)
        assert str(result) == expected_value

    def parse_and_expect_error(self, parser, expr_transformer, expression):
        """Parse the expression and expect an exception to be raised."""
        with pytest.raises(ShapeError):
            expr_transformer.transform(parser.parse(expression))

    @pytest.mark.parametrize(
        ("expression", "expected_type", "expected_value"),
        [
            ("192.168.0.1", IP4, "192.168.0.1"),
            ("192.168.0.0/24", IP4Net, "192.168.0.0/24"),
            ("192.0.0.1-192.0.0.255", IP4Range, "192.0.0.1-192.0.0.255"),
            (
                "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
                IP6,
                "2001:db8:85a3::8a2e:370:7334",
            ),
            ("2001:db8::/32", IP6Net, "2001:db8::/32"),
            ("2001:db8::-2001:db8::2", IP6Range, "2001:db8::-2001:db8::2"),
            (
                "2001:0db8::0370:7334-2001:0db8::0370:7335",
                IP6Range,
                "2001:db8::370:7334-2001:db8::370:7335",
            ),
            ("2024-01-01T12:00:00Z", datetime, "2024-01-01 12:00:00+00:00"),
            ("2024-01-01 12:00:00-02:00", datetime, "2024-01-01 12:00:00-02:00"),
            ("2024-01-01T12:00:00", datetime, "2024-01-01 12:00:00+00:00"),
            ("01:00:00", timedelta, "1:00:00"),
            ("1d01:00:00", timedelta, "1 day, 1:00:00"),
            ("'constant1'", str, "constant1"),
            ('"constant2"', str, "constant2"),
            ("42", int, "42"),
            ("0.5", float, "0.5"),
            ("0", int, "0"),
            ("3.14", float, "3.14"),
        ],
    )
    def test_transformations(
        self, parser, expr_transformer, expression, expected_type, expected_value
    ):
        self.parse_and_assert(
            parser, expr_transformer, expression, expected_type, expected_value
        )

    @pytest.mark.parametrize(
        "expression",
        [
            "400.168.0.1",  # Invalid IPv4
            "192.168.0.0/44",  # Invalid CIDR
            "2001:8a2e:370:733",  # Invalid IPv6
            "2001:db8::/982",  # Invalid CIDR
            "2024-10-32",  # Invalid date
            "10D100:00:00",  # Invalid timedelta
        ],
    )
    def test_invalid_cases(self, parser, expr_transformer, expression):
        self.parse_and_expect_error(parser, expr_transformer, expression)

    def test_timedelta_invalid(self, expr_transformer):
        with pytest.raises(ValueError, match="Invalid duration format: invalid"):
            expr_transformer.timedelta("invalid")

    def test_variable(self, parser):
        """
        Tests variable transformation to ensure proper resolution from context
        or as a data-driven variable.
        """
        # Context setup for testing constant variable resolution
        context = {"my_var": "example_value"}
        expr_transformer = ExpressionTransformer(context)

        # Test variable from context
        result_context = expr_transformer.transform(parser.parse_only("my_var"))
        assert result_context.children[0] == "example_value"

        # Test data-driven variable
        result_data = expr_transformer.transform(parser.parse_only("external_var"))
        assert result_data.children[0].real_value == "external_var"

        # Test data-driven variable (prefixed with '.')
        result_data = expr_transformer.transform(parser.parse_only(".my_var"))
        assert result_data.children[0].real_value == "my_var"


class TestFilter:
    def parse_filter(self, parser, filter_, expression):
        """Helper to parse, evaluate atoms to Python object, then evaluate."""
        tree = parser.parse(expression)
        return filter_.eval(tree, sample_data)

    def parse_filter_and_expect_error(self, parser, filter_, expression):
        """Parse the expression and expect an exception to be raised."""
        tree = parser.parse(expression)
        with pytest.raises(RansackError):
            filter_.eval(tree, sample_data)

    @pytest.mark.parametrize(
        ("expression", "expected"),
        [
            # Test Arithmetic Operations
            ("5 - 3", 2),
            ("2.5 + 3.5", 6.0),
            ("4 * 3", 12),
            ("10 / 2", 5),
            ("7 % 2", 1),
            ("-2.5", -2.5),
            ("(4 + 5 * 2 - 6 / 3) % 5", 2),
            (
                "2024-01-01 - 1D00:00:00",
                datetime.fromisoformat("2023-12-31T00:00:00+00:00"),
            ),
            (
                "2023-11-28 15:30:00 + 0D10:00:00",
                datetime.fromisoformat("2023-11-29T01:30:00+00:00"),
            ),
            ("3D00:00:00 + 0D05:00:00", timedelta(days=3, hours=5)),
            ("0D10:00:00 + 0D00:20:00", timedelta(hours=10, minutes=20)),
            # Scalar and range
            ("5 + 1..2", (6, 7)),
            ("10 - 5 .. 7", (5, 3)),
            ("1..2 + 5", (6, 7)),
            ("12..10 - 4", (8, 6)),
            (
                "1D00:00:00 + 2024-02-28..2025-02-28",
                (
                    datetime.fromisoformat("2024-02-29T00:00:00+00:00"),
                    datetime.fromisoformat("2025-03-01T00:00:00+00:00"),
                ),
            ),
            (
                "2024-01-01 .. 2024-12-31 - 1D00:00:00",
                (
                    datetime.fromisoformat("2023-12-31T00:00:00+00:00"),
                    datetime.fromisoformat("2024-12-30T00:00:00+00:00"),
                ),
            ),
            # Scalar and list
            ("5 + [1, 2, 3]", [6, 7, 8]),
            ("10 - [5, 6, 7]", [5, 4, 3]),
            ("3 * [1, 2, 3]", [3, 6, 9]),
            ("29 % [12, 23, 2]", [5, 6, 1]),
            ("60 / [12, 10, 4]", [5.0, 6.0, 15]),
            ("[1, 2, 3] + 5", [6, 7, 8]),
            ("[5, 6, 7] - 3", [2, 3, 4]),
            ("[1, 2, 3] * 3", [3, 6, 9]),
            ("[12, 23, 2] % 5", [2, 3, 2]),
            ("[12, 10, 4] / 4", [3.0, 2.5, 1.0]),
            (
                "5D00:00:00 + [1D00:00:00, 2D00:00:00]",
                [timedelta(days=6), timedelta(days=7)],
            ),
            (
                "0D02:00:00 - [0D00:30:00, 0D00:45:00]",
                [timedelta(hours=1, minutes=30), timedelta(hours=1, minutes=15)],
            ),
            (
                "[0D00:30:00, 0D00:45:00] - 0D02:00:00",
                [-timedelta(hours=1, minutes=30), -timedelta(hours=1, minutes=15)],
            ),
            (
                "2023-11-28 + [1D00:00:00, 2D00:00:00]",
                [
                    datetime.fromisoformat("2023-11-29T00:00:00+00:00"),
                    datetime.fromisoformat("2023-11-30T00:00:00+00:00"),
                ],
            ),
            # Test Comparisons
            ("2 >= 2 and 4 <= 12.89 or 4 == 4", True),
            ("not (2 > 1 and 3 > 2) or (1 < 2 and 2 < 3)", True),  # not True or True
            ("3 > 2 or 2 < 1 and 1 > 2", True),  # True or False and False
            ("2 < 3 and 3 > 1 or 1 < 0", True),  # True and True or False
            ("not (4 > 2) or 1 > 2", False),  # not True or False
            ("not (5 > 3 or 2 < 1)", False),  # not (True or False)
            ("3 > 2 and not 2 < 1", True),  # True and not False
            # Test short-circuit evaluation
            ("1 > 0 or .not_in_data == 1", True),
            ("1 < 0 and .not_in_data == 1", False),
            # Numeric comparisons
            ("5 > 3", True),
            ("5 < 3", False),
            ("5 >= 5", True),
            ("5 <= 3", False),
            ("5 = 5", True),
            ("5 == 5", True),
            ("5 == 3", False),
            # Datetime comparisons
            ("2023-11-28 > 2023-11-25", True),
            ("2023-11-28 < 2023-11-25", False),
            ("2023-11-28 >= 2023-11-28", True),
            ("2023-11-28 <= 2023-11-25", False),
            ("2023-11-28 == 2023-11-28", True),
            # Timedelta comparisons
            ("5D00:00:00 > 3D00:00:00", True),
            ("5D00:00:00 < 3D00:00:00", False),
            ("5D00:00:00 >= 5D00:00:00", True),
            ("5D00:00:00 <= 3D00:00:00", False),
            ("5D00:00:00 == 5D00:00:00", True),
            # IP comparisons
            ("192.168.1.1 > 192.168.1.0", True),
            ("192.168.1.1 < 192.168.1.2", True),
            ("192.168.1.1 >= 192.168.1.1", True),
            ("192.168.1.1 <= 192.168.1.0", False),
            ("192.168.1.1 == 192.168.1.1", True),
            # IP and list
            ("192.168.1.1 > [192.168.1.0, 192.168.1.2]", True),
            ("192.168.1.1 < [192.168.1.0, 192.168.1.1]", False),
            ("192.168.1.1 == [192.168.1.0, 192.168.1.1]", False),
            ("192.168.1.1 = [192.168.1.0, 192.168.1.1]", True),
            # IP = range
            ("192.168.0.4 = 192.168.0.1..192.168.0.10", True),
            ("192.168.0.1-192.168.0.10 = 192.168.0.4", True),
            ("192.168.0.1-192.168.0.10 = 192.168.0.11", False),
            ("192.168.0.11 = 192.168.0.1..192.168.0.10", False),
            # Numeric comparisons with tuples
            ("5 > 5..7", False),
            ("5 < 3 .. 6", True),
            ("5 >= 5..6", True),
            ("5 <= 7 .. -4", True),
            ("5 == 5..12", False),
            ("5..7 > 5", True),
            ("3..6 < 5", True),
            ("5..6 >= 5", True),
            ("7..-4 <= -5", False),
            ("5..12 = 7", True),
            ("8 = 13..5", True),
            ("5..12 == 5", False),
            # Datetime comparisons with tuples
            ("2023-11-28 > 2023-11-25 .. 2023-11-30", True),
            ("2023-11-28 < 2023-11-25..2023-11-30", True),
            ("2023-11-28 == 2023-11-28 .. 2023-11-29", False),
            # Numeric comparisons with lists
            ("5 > [3, 6, 4]", True),
            ("5 < [2, 3, 4]", False),
            ("5 >= [5, 6, 6]", True),
            ("5 <= [3, 5, 7]", True),
            ("5 = [5, 3, 6]", True),
            ("5 == [5, 3, 6]", False),
            ("[2, 3, 4] < 5", True),
            # Datetime comparisons with lists
            ("2023-11-28 > [2023-11-25, 2023-11-30]", True),
            ("2023-11-28 < [2023-11-24, 2023-11-28]", False),
            ("2023-11-28 == [2023-11-28, 2023-11-29]", False),
            # Timedelta comparisons with lists
            ("5D00:00:00 > [3D00:00:00, 6D00:00:00]", True),
            ("5D00:00:00 < [5D00:00:00, 4D00:00:00]", False),
            ("5D00:00:00 >= [5D00:00:00, 4D00:00:00]", True),
            ("5D00:00:00 <= [5D00:00:01, 4D23:59:59]", True),
            ("5D00:00:00 = [5D00:00:00]", True),
            ("5D00:00:00 == [5D00:00:00]", False),
            # List-to-list comparisons
            ("[0, 2, 3] > [0, 2, 4]", True),
            ("[4, 5, 6] < [0, 2, 4]", False),
            ("[1, 2, 3] >= [1, 1, 3]", True),
            ("[1, 2, 3] <= [0, 2, 4]", True),
            ("[1, 2, 3] = [0, 2]", True),
            ("[2, 4] = [1, 3, 5, 6]", False),
            ("[1, 2, 3] == [1, 2, 3]", True),
            # List-to-IP comparisons
            ("[192.168.1.1, 192.168.1.3] > 192.168.1.2", True),
            ("192.168.1.2 < [192.168.1.1, 192.168.0.1]", False),
            ("192.168.1.1/32 == 192.168.1.1", True),
            # Test in operator
            ("192.168.0.1 in 192.168.0.0/16", True),
            ("not 192.168.0.1-192.168.0.10 in 192.168.0.8-192.168.0.12", True),
            ("192.168.0.0/24 in 192.168.0.0/16", True),
            ("13 in [1, 3, 13] and (not 12 in [1, 2])", True),
            ("2024-12-12 in [2024-11-11]", False),
            ("4D12:13:14 in [13D13:24:24, 12D23:23:23, 4D12:13:14]", True),
            ("192.168.0.1 in [192.168.0.2, 192.168.0.2]", False),
            ("[192.168.0.2] in [192.168.0.2, 192.168.0.0/16]", True),
            ("[192.168.0.2] in 192.168.0.0/16", True),
            ("[192.168.0.2] in 192.169.0.0/16", False),
            ("192.168.0.2-192.168.0.5 in 192.168.0.0/16", True),
            ("[2, 3, 4] in [5, 6, 7, 8, 3]", True),
            ("'tcp' in Source.Proto", True),
            # Test in range
            ("192.168.0.12 in 192.168.0.0 .. 192.168.0.255", True),
            ("not 2023-12-12 in 2023-12-13..2023-12-31", True),
            ("1 in 1..10", True),
            ("8 in 19..-13", True),
            ("_Mentat.SourceResolvedASN in 1 .. 200000", True),
            # Test in nested data
            ("13 in [1, [3, 13]]", True),
            ("192.168.0.1 in [192.168.0.0/16]", True),
            ("192.168.0.1 in [(192.168.0.0..192.168.0.2)]", True),
            ("2024::10 in [2024::0-2024::10]", True),
            ("2024-12-12 in [(2024-12-01..2024-12-31)]", True),
            # Test string equality
            ("'abc' == 'abc'", True),
            ("'abc' = 'abc'", True),
            ("'abc' = '_abc_'", False),
            ("'abc' = ['def', 'abc']", True),
            ("'abc' = ['a', 'b', 'c']", False),
            ("['a', 'b', 'c'] = 'b'", True),
            # Test contains operator
            ("'abcdefghi' contains 'def'", True),
            ("not 'abc' contains 'def'", True),
            ("['abc', 'abcdefghi','ghi'] contains 'def'", True),
            ("['abc', 'def','ghi'] contains 'abcd'", False),
            # Test concat operator on lists
            ("[1, 3, 13] . [1, 2]", [1, 3, 13, 1, 2]),
            # Test concat operator on strings
            ("'abc'.'def'", "abcdef"),
            # Test integer range
            ("1..1024", (1, 1024)),
            # Test float range
            ("1.0..-2.0", (1.0, -2.0)),
            # Test mixed number range
            ("0..12.0", (0, 12.0)),
            # Test alternate IP range
            ("192.0.0.1..192.0.0.255", IP4Range("192.0.0.1-192.0.0.255")),
            ("12D3::0 .. 12D3::1", IP6Range("12D3::-12D3::1")),
            # Test range on variables
            ("(ConnCount - 5) .. ConnCount", (-4, 1)),
            # Test nested data
            ("ConnCount", 1),
            ("_Mentat.SourceResolvedCountry", ["CZ"]),
            ("Source.IP4", ["1.2.3.235", "1.2.3.236"]),
            ("Credentials.Username", ["root"]),
            ("_Mentat.StorageTime", "2023-12-12"),
            ("_Mentat._private", 123),
            # Test None is returned
            ("NullKey", None),
            ("_Mentat.NestedNullKey", None),
            # Test exists
            ("NullKey??", True),
            ("_Mentat.NestedNullKey??", True),
            ("Category??", True),
            ("Credentials.Password??", True),
            ("Source.Foo??", False),
            ("Foo??", False),
            # Test exists with default
            ("NullKey??12", None),
            ("_Mentat.NestedNullKey??Source.IP4", None),
            ("Category??Category", ["Intrusion.UserCompromise"]),
            ("Credentials.Password ?? ConnCount", ["P4ssw0rd123"]),
            ("Source.Foo??ConnCount", 1),
            ("Foo??('abc'.'def')", "abcdef"),
            # Test predefined functions
            ("len([1, 2, 3]) == 3", True),
            ("length([])", 0),
            ("now() > now() - 1D00:00:00", True),
            ("len(not_in_dict??[])", 0),
            ("len([1].[2].[3])", 3),
            # Test that function call returns the same value
            # when used multipe times in one query
            ("now() == now()", True),
        ],
    )
    def test_filters(self, parser, filter_, expression, expected):
        result = self.parse_filter(parser, filter_, expression)
        assert result == expected

    @pytest.mark.parametrize(
        "expression",
        [
            "1D00:00:00 - 2024-01-01",
            "[1, 3, 13] in 13 and (not [1, 2] in 12)",
            "[2024-11-11] in 2024-12-12",
            "[13D13:24:24, 12D23:23:23, 4D12:13:14] in 4D12:13:14",
            "[192.168.0.2, 192.168.0.0/16] in 192.168",
            ".not_in_dict",  # Test unknown variable
            "unknown_function([1, 2])",  # Test undefined function
            "len(12)",  # Test wrong type
        ],
    )
    def test_invalid_cases(self, parser, filter_, expression):
        self.parse_filter_and_expect_error(
            parser,
            filter_,
            expression,
        )

    def test_variable(self, parser, filter_):
        # Context setup for testing constant variable resolution
        context = {"my_var": 14}
        expr_transformer = ExpressionTransformer(context)

        # Test variable from context
        exp_tree = expr_transformer.transform(parser.parse_only("my_var == 14"))
        res = filter_.transform(exp_tree)
        assert res
