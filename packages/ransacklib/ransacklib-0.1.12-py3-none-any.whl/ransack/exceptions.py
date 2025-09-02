"""Custom exceptions for Ransack query parsing, evaluation, and shape validation."""

from typing import Any


class RansackError(Exception):
    """Base exception for all query-related errors."""


class PositionInfoMixin:
    """Mixin class that adds source position metadata to exceptions."""

    def __init__(
        self,
        line: int,
        column: int,
        context: str | None = None,
        start_pos: int | None = None,
        end_pos: int | None = None,
        end_line: int | None = None,
        end_column: int | None = None,
        *args,
        **kwargs,
    ):
        self.line = line
        self.column = column
        self.context = context
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.end_line = end_line
        self.end_column = end_column
        super().__init__(*args, **kwargs)


class ParseError(PositionInfoMixin, RansackError):
    """Raised when the input query cannot be parsed."""

    def __str__(self):
        return (
            f"Syntax error at line {self.line}, column {self.column}.\n\n{self.context}"
        )


class ShapeError(PositionInfoMixin, RansackError):
    """Raised when a query has an invalid shape or structure."""

    def __init__(self, msg: str, **kwargs):
        self.msg = msg
        super().__init__(**kwargs)

    def __str__(self):
        return f"Error at line {self.line}, column {self.column}.\n\n{self.msg}\n\n{self.context}"  # noqa


class EvaluationError(PositionInfoMixin, RansackError):
    """Raised when a query fails during evaluation."""

    def __init__(self, msg: str, **kwargs):
        self.msg = msg
        super().__init__(**kwargs)

    def __str__(self):
        return f"Error at line {self.line}, column {self.column}.\n\n{self.msg}"


class OperatorNotFoundError(RansackError):
    """Exception raised when an operator is not found for the provided types."""

    def __init__(
        self,
        operator: str,
        types: tuple[type | str, type | str],
        values: tuple[Any, Any] | None = None,
    ):
        """
        Initialize the exception with operator, operand types, and optional values.

        Args:
            operator: The operator that was attempted.
            types: The types of the operands.
            values: The values of the operands. Defaults to None.
        """
        self.operator = operator
        self.types = types
        self.values = values
        message = f"Operator '{operator}' not found for types {types}"
        if values:
            message += f" with values {values}"
        super().__init__(message)


def add_caret_to_context(
    context: str, line: int, column: int, original_data: str, context_start_pos: int
) -> str:
    """
    Inserts a caret (^) under the character at (line, column) relative
    to the full input. `context` is a slice of the full input string.
    `line` and `column` are from the parser (1-based).
    """
    # Recalculate absolute position
    lines_up_to_error = original_data.splitlines()[0 : line - 1]
    absolute_error_pos = (
        sum(len(lines) + 1 for lines in lines_up_to_error) + column - 1
    )  # +1 for newline

    caret_pos_in_context = absolute_error_pos - context_start_pos

    # Sanity check
    if caret_pos_in_context < 0 or caret_pos_in_context > len(context):
        return context  # fallback, avoid crashing

    # Find line offset in context
    line_start = context.rfind("\n", 0, caret_pos_in_context) + 1
    line_end = context.find("\n", caret_pos_in_context)
    if line_end == -1:
        line_end = len(context)

    caret_line = " " * (caret_pos_in_context - line_start) + "^"

    return context[:line_end] + "\n" + caret_line + context[line_end:]
