from collections.abc import Callable, MutableSequence
from datetime import datetime, timedelta, timezone
from functools import partial
from numbers import Number
from operator import add, eq, ge, gt, le, lt, mod, mul, sub, truediv
from typing import Any

from ipranges import IP4, IP6, IP4Net, IP4Range, IP6Net, IP6Range

from .exceptions import OperatorNotFoundError

IP = IP4 | IP4Net | IP4Range | IP6 | IP6Net | IP6Range
Operand = type | str

commutative_operators = {"+", "*"}


def _op_scalar_range(op: str, scalar, _range: tuple) -> tuple:
    """
    Perform a binary operation between a scalar and a range (tuple).

    Args:
        op: The operator to apply.
        scalar: The scalar operand.
        _range: The range operand as a tuple of two values.

    Returns:
        A tuple containing the result of the operation applied to
        each end of the range.
    """
    start, end = _range
    return (binary_operation(op, scalar, start), binary_operation(op, scalar, end))


def _op_range_scalar(op: str, _range: tuple, scalar) -> tuple:
    """
    Perform a binary operation between a range (tuple) and a scalar.

    Args:
        op: The operator to apply.
        _range: The range operand as a tuple of two values.
        scalar: The scalar operand.

    Returns:
        A tuple containing the result of the operation applied to
        each end of the range.
    """
    start, end = _range
    return (binary_operation(op, start, scalar), binary_operation(op, end, scalar))


def _op_scalar_list(op: str, scalar, t: MutableSequence) -> list:
    """
    Perform a binary operation between a scalar and each element in a list.

    Args:
        op: The operator to apply.
        scalar: The scalar operand.
        t: The list of operands.

    Returns:
        A list of results from the operation.
    """
    return [binary_operation(op, scalar, elem) for elem in t]


def _op_list_scalar(op: str, t: MutableSequence, scalar: Any) -> list:
    """
    Perform a binary operation between each element in a list and a scalar.

    Args:
        op: The operator to apply.
        t: The list of operands.
        scalar: The scalar operand.

    Returns:
        A list of results from the operation.
    """
    return [binary_operation(op, elem, scalar) for elem in t]


def _comp_scalar_range(op: str, scalar, _range: tuple) -> bool:
    """
    Compare a scalar with a range (tuple) using the specified operator.

    Args:
        op: The comparison operator.
        scalar: The scalar operand.
        _range: The range operand as a tuple of two values.

    Returns:
        The result of the comparison.
    """
    if op == "=":
        return _in_scalar_range(scalar, _range)
    start, end = _range
    return binary_operation(op, scalar, start) or binary_operation(op, scalar, end)


def _comp_range_scalar(op: str, _range: tuple, scalar) -> bool:
    """
    Compare a range (tuple) with a scalar using the specified operator.

    Args:
        op: The comparison operator.
        _range: The range operand as a tuple of two values.
        scalar: The scalar operand.

    Returns:
        The result of the comparison.
    """
    if op == "=":
        return _in_scalar_range(scalar, _range)
    start, end = _range
    return binary_operation(op, start, scalar) or binary_operation(op, end, scalar)


def _comp_scalar_list(op: str, scalar: Any, t: MutableSequence) -> bool:
    """
    Compare a scalar with a list using the specified operator.

    Args:
        op: The comparison operator.
        scalar: The scalar operand.
        t: The list of operands.

    Returns:
        True if the comparison is satisfied for any element in the list,
        otherwise False.
    """
    return any(map(partial(binary_operation, op, scalar), t))


def _comp_list_scalar(op: str, t: MutableSequence, scalar: Any) -> bool:
    """
    Compare each element of a list with a scalar using the specified operator.

    Args:
        op: The comparison operator.
        t: The list of operands.
        scalar: The scalar operand.

    Returns:
        True if the comparison is satisfied for any element in the list,
        otherwise False.
    """
    return any(binary_operation(op, x, scalar) for x in t)


def _comp_list_list(op: str, t1: MutableSequence, t2: MutableSequence) -> bool:
    """
    Compare two lists using the specified operator.

    Args:
        op: The comparison operator.
        t1: The first list of operands.
        t2: The second list of operands.

    Returns:
        True if the comparison is satisfied for any pair of elements,
        otherwise False.
    """
    return any(_comp_scalar_list(op, elem, t2) for elem in t1)


def _comp_ip_ip(op: str, ip1: IP, ip2: IP) -> bool:
    """
    Compare two ipranges objects using the specified operator.

    Args:
        op: The comparison operator.
        ip1: The first IP object.
        ip2: The second IP object.

    Returns:
        The result of the comparison.

    Raises:
        OperatorNotFoundError: If the operator is not recognized for ipranges types.
    """
    match op:
        case "<":
            return ip1.low() < ip2.high()
        case ">":
            return ip1.high() > ip2.low()
        case ">=":
            return ip1.high() >= ip2.low()
        case "<=":
            return ip1.low() <= ip2.high()
        case "=":
            return ip1 in ip2 or ip2 in ip1
        case _:
            raise OperatorNotFoundError(op, ("ip", "ip"), (ip1, ip2))


def _concat(a, b) -> str | MutableSequence:
    """
    Concatenate two objects, either strings or lists.

    Args:
        a: The first object, either a string or a list.
        b: The second object, either a string or a list.

    Returns:
        The concatenated result.
    """
    return a + b


def _in_scalar_list(left, right: MutableSequence) -> bool:
    """
    Check if a scalar value is contained within a list or iterable.

    Args:
        left: The scalar value to check for membership.
        right: The list or iterable to search within.

    Returns:
        True if the scalar value is found in the list or iterable,
        otherwise False.

    Notes:
        - For each element in `right`, if it belongs to specific iterable
          types (`list`, `tuple`, `IP4Net`, `IP4Range`, `IP6Range`, `IP6Net`),
          the membership check is performed using the `binary_operation("in")`.
        - For other types, the comparison is done using equality (`==`).
    """
    iterable = (MutableSequence, tuple, IP4Net, IP4Range, IP6Range, IP6Net)
    return any(
        binary_operation("in", left, x) if isinstance(x, iterable) else left == x
        for x in right
    )


def _in_scalar_range(scalar, _range: tuple) -> bool:
    """
    Check if a scalar is within a range.

    Args:
        scalar: The scalar value to check.
        _range: A tuple representing the range (start, end).

    Returns:
        True if the scalar is within the range, otherwise False.
    """
    start, end = _range
    start, end = min(start, end), max(start, end)
    return binary_operation(">=", scalar, start) and binary_operation("<=", scalar, end)


def _in_list_tuple(t: MutableSequence, _range: tuple) -> bool:
    """
    Check if any element from the list is within a range.

    Args:
        t: The list of values to check.
        _range: A tuple representing the range (start, end).

    Returns:
        True if any element of the list is within the range, otherwise False.
    """
    return any(_in_scalar_range(elem, _range) for elem in t)


def _in_list_list(left: MutableSequence, right: MutableSequence) -> bool:
    """
    Check if any element of one list is in another list.

    Args:
        left: The first list of elements.
        right: The second list to search in.

    Returns:
        True if any element of `left` is in `right`, otherwise False.
    """
    return any(_in_scalar_list(elem, right) for elem in left)


def _set_zero_timezone_if_none(
    left: datetime, right: datetime
) -> tuple[datetime, datetime]:
    """
    Set UTC timezone to datetime objects if they are offset-naive.

    Args:
        left: The first datetime object.
        right: The second datetime object.

    Returns:
        A tuple of datetime objects with UTC timezone set if they were naive.
    """
    if left.tzinfo is None:
        left = left.replace(tzinfo=timezone.utc)
    if right.tzinfo is None:
        right = right.replace(tzinfo=timezone.utc)
    return left, right


def _comp_datetime_datetime(comp: Callable, left: datetime, right: datetime) -> bool:
    """
    Compare two datetime objects with a given comparison function,
    ensuring both are timezone-aware.

    Args:
        comp: A callable comparison function (e.g., operator.lt).
        left: The first datetime object.
        right: The second datetime object.

    Returns:
        The result of the comparison.
    """
    left, right = _set_zero_timezone_if_none(left, right)
    return comp(left, right)


def _sub_datetime_datetime(left: datetime, right: datetime) -> timedelta:
    """
    Subtract two datetime objects, ensuring both are timezone-aware.

    Args:
        left: The first datetime object.
        right: The second datetime object.

    Returns:
        The time difference as a timedelta object.
    """
    left, right = _set_zero_timezone_if_none(left, right)
    return left - right


def _get_comp_dict(op: str, comp: Callable) -> dict[tuple[Operand, Operand], Callable]:
    """
    Generate a comparison dictionary for the given operator.

    Args:
        op: The comparison operator.
        comp: The comparison function.

    Returns:
        A dictionary mapping operand type pairs to comparison functions.
    """
    return {
        (Number, Number): comp,
        (datetime, datetime): partial(_comp_datetime_datetime, comp),
        (timedelta, timedelta): comp,
        ("ip", "ip"): partial(_comp_ip_ip, op),
        (Number, tuple): partial(_comp_scalar_range, op),
        (datetime, tuple): partial(_comp_scalar_range, op),
        (tuple, Number): partial(_comp_range_scalar, op),
        (tuple, datetime): partial(_comp_range_scalar, op),
        (str, MutableSequence): partial(_comp_scalar_list, op),
        ("ip", MutableSequence): partial(_comp_scalar_list, op),
        (Number, MutableSequence): partial(_comp_scalar_list, op),
        (datetime, MutableSequence): partial(_comp_scalar_list, op),
        (timedelta, MutableSequence): partial(_comp_scalar_list, op),
        (MutableSequence, str): partial(_comp_list_scalar, op),
        (MutableSequence, "ip"): partial(_comp_list_scalar, op),
        (MutableSequence, Number): partial(_comp_list_scalar, op),
        (MutableSequence, datetime): partial(_comp_list_scalar, op),
        (MutableSequence, timedelta): partial(_comp_list_scalar, op),
        (MutableSequence, MutableSequence): partial(_comp_list_list, op),
    }


# Define the operator map
_operator_map: dict[str, dict[tuple[Operand, Operand], Callable]] = {
    "+": {
        (Number, Number): add,
        (datetime, timedelta): add,
        (timedelta, timedelta): add,
        (Number, tuple): partial(_op_scalar_range, "+"),
        (timedelta, tuple): partial(_op_scalar_range, "+"),
        (Number, MutableSequence): partial(_op_scalar_list, "+"),
        (datetime, MutableSequence): partial(_op_scalar_list, "+"),
        (timedelta, MutableSequence): partial(_op_scalar_list, "+"),
    },
    "-": {
        (Number, Number): sub,
        (datetime, timedelta): sub,
        (timedelta, timedelta): sub,
        (datetime, datetime): _sub_datetime_datetime,
        # x - tuple[x]
        (Number, tuple): partial(_op_scalar_range, "-"),
        (timedelta, tuple): partial(_op_scalar_range, "-"),
        (datetime, tuple): partial(_op_scalar_range, "-"),
        # tuple[x] - x
        (tuple, Number): partial(_op_range_scalar, "-"),
        (tuple, timedelta): partial(_op_range_scalar, "-"),
        (tuple, datetime): partial(_op_range_scalar, "-"),
        # x - list[x]
        (Number, MutableSequence): partial(_op_scalar_list, "-"),
        (datetime, MutableSequence): partial(_op_scalar_list, "-"),
        (timedelta, MutableSequence): partial(_op_scalar_list, "-"),
        # list[x] - x
        (MutableSequence, Number): partial(_op_list_scalar, "-"),
        (MutableSequence, datetime): partial(_op_list_scalar, "-"),
        (MutableSequence, timedelta): partial(_op_list_scalar, "-"),
    },
    "*": {
        (timedelta, Number): mul,
        (Number, Number): mul,
        (timedelta, MutableSequence): partial(_op_scalar_list, "*"),
        (Number, MutableSequence): partial(_op_scalar_list, "*"),
    },
    "/": {
        (timedelta, timedelta): truediv,
        (Number, Number): truediv,
        (timedelta, MutableSequence): partial(_op_scalar_list, "/"),
        (Number, MutableSequence): partial(_op_scalar_list, "/"),
        (MutableSequence, timedelta): partial(_op_list_scalar, "/"),
        (MutableSequence, Number): partial(_op_list_scalar, "/"),
    },
    "%": {
        (timedelta, timedelta): mod,
        (Number, Number): mod,
        (timedelta, MutableSequence): partial(_op_scalar_list, "%"),
        (Number, MutableSequence): partial(_op_scalar_list, "%"),
        (MutableSequence, timedelta): partial(_op_list_scalar, "%"),
        (MutableSequence, Number): partial(_op_list_scalar, "%"),
    },
    ">": _get_comp_dict(">", gt),
    ">=": _get_comp_dict(">=", ge),
    "<=": _get_comp_dict("<=", le),
    "<": _get_comp_dict("<", lt),
    "=": _get_comp_dict("=", eq) | {(str, str): eq},
    ".": {
        (str, str): _concat,
        (MutableSequence, MutableSequence): _concat,
    },
    "contains": {
        (str, str): lambda value, pattern: pattern in value,
        (MutableSequence, str): lambda t, x: any(x in elem for elem in t),
    },
    "in": {
        ("ip", "ip"): lambda left, right: left in right,
        (str, MutableSequence): _in_scalar_list,
        (Number, MutableSequence): _in_scalar_list,
        (timedelta, MutableSequence): _in_scalar_list,
        (datetime, MutableSequence): _in_scalar_list,
        ("ip", MutableSequence): _in_scalar_list,
        ("ip", tuple): _in_scalar_range,
        (Number, tuple): _in_scalar_range,
        (datetime, tuple): _in_scalar_range,
        (MutableSequence, tuple): _in_list_tuple,
        (MutableSequence, MutableSequence): _in_list_list,
        (MutableSequence, "ip"): lambda left, right: any(
            binary_operation("in", x, right) for x in left
        ),
    },
}


def _resolve_type(value: Any) -> type | str:
    """
    Resolve the type of a value for use in operator mapping.

    Args:
        value: The value to resolve.

    Returns:
        The resolved type or a custom type string.
    """
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return Number
    if isinstance(value, (IP4, IP4Range, IP4Net, IP6, IP6Net, IP6Range)):
        return "ip"
    if isinstance(value, MutableSequence):
        return MutableSequence
    return type(value)


def binary_operation(operator: str, left: Any, right: Any) -> Any:
    """
    Perform a binary operation using the specified operator and operands.

    Args:
        operator: The operator to apply.
        left: The left operand.
        right: The right operand.

    Returns:
        The result of the operation.

    Raises:
        OperatorNotFoundError: If the operator is not found for the operand types.
    """
    t1 = _resolve_type(left)
    t2 = _resolve_type(right)
    try:
        # Try to find and apply the operator for the (t1, t2) combination
        return _operator_map[operator][(t1, t2)](left, right)
    except KeyError:
        # If not found, check if the operator is commutative and try the reverse order
        if operator in commutative_operators:
            try:
                return _operator_map[operator][(t2, t1)](right, left)
            except KeyError:
                pass
        # Raise an error if the operator is not found in either order
        raise OperatorNotFoundError(operator, (t1, t2), (left, right)) from None
