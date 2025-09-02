from collections.abc import MutableSequence

import pytest
from ipranges import IP4Range

from ransack.exceptions import OperatorNotFoundError
from ransack.operator import _comp_ip_ip, binary_operation


def test_comp_ip_ip():
    """
    Test the private function _comp_ip_ip for comparing IP range objects.

    The function is tested directly to achieve full coverage, as invalid operators
    are filtered out by `binary_operation` and cannot reach this function indirectly.
    This ensures that `_comp_ip_ip` handles valid and invalid cases as expected.

    Valid cases include comparison operators ('<', '>', '<=', '>='), while invalid
    cases (e.g., '==') raise an OperatorNotFoundError.
    """
    # Create sample IP ranges
    ip1 = IP4Range("192.168.1.0-192.168.1.255")
    ip2 = IP4Range("192.168.2.0-192.168.2.255")
    ip3 = IP4Range("192.168.1.0-192.168.3.255")  # Overlaps with both ip1 and ip2

    # Test valid comparisons
    assert _comp_ip_ip("<", ip1, ip2) is True
    assert _comp_ip_ip(">", ip2, ip1) is True
    assert _comp_ip_ip(">=", ip3, ip2) is True
    assert _comp_ip_ip("<=", ip1, ip3) is True
    assert _comp_ip_ip("=", ip1, ip1) is True
    assert _comp_ip_ip("=", ip3, ip1) is True

    # Test invalid operator (this branch cannot be reached indirectly)
    with pytest.raises(OperatorNotFoundError) as exc_info:
        _comp_ip_ip("==", ip1, ip2)

    assert "Operator '==' not found for types ('ip', 'ip')" in str(exc_info.value)


def test_binary_operation_operator_not_found():
    """
    Test binary_operation for scenarios where the operator is not supported.

    This ensures that the OperatorNotFoundError is raised with an appropriate
    error message when unsupported operators or operand types are used.

    Raises:
        AssertionError: If any of the assertions fail.
    """
    # Define test cases where OperatorNotFoundError is expected
    test_cases = [
        ("^", 5, 3),  # Unsupported operator
        ("+", "string", 3),  # Unsupported type for "+"
        ("-", {"key": "value"}, [1, 2, 3]),  # Unsupported types for "-"
        ("/", 1.5, "string"),  # Unsupported type for "/"
        ("%", None, 42),  # Unsupported type for "%"
    ]

    for operator, left, right in test_cases:
        with pytest.raises(OperatorNotFoundError) as exc_info:
            binary_operation(operator, left, right)

        # Validate the exception message
        exc_message = str(exc_info.value)

        # Special handling for numbers (int and float are resolved to Number)
        left_type = "Number" if isinstance(left, (int, float)) else str(type(left))
        right_type = "Number" if isinstance(right, (int, float)) else str(type(right))

        # Special handling for lists (list is resolved to MutableSequence
        if isinstance(right, MutableSequence):
            right_type = str(MutableSequence)

        # Check if the exception message contains the correct operator and types
        assert f"Operator '{operator}' not found" in exc_message
        assert left_type in exc_message
        assert right_type in exc_message

        # Validate values
        assert str(left) in exc_message
        assert str(right) in exc_message
