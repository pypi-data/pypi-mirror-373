"""
parser.py - Provides a `Parser` class for parsing input data using Lark.

This module defines a custom grammar for parsing various expressions such as
comparisons, arithmetic operations, logical operators, IP address parsing,
datetime formats, and strings. The `Parser` class utilizes the Lark parser
to build a parse tree for input expressions that conform to the grammar rules.

Classes:
    - Parser: Encapsulates the Lark parser with the defined grammar to parse
              input data into an abstract syntax tree (AST).
"""

import os
from pathlib import Path
from typing import Any, no_type_check

from lark import Lark, Token, Tree
from lark.exceptions import UnexpectedInput, VisitError

from .exceptions import ParseError, ShapeError, add_caret_to_context
from .transformer import ExpressionTransformer


class Parser:
    """
    Parser for query expressions based on a custom grammar using Lark.

    This class accepts an optional `context` dictionary at initialization. The context
    provides user-defined variables that can be referenced in expressions and take
    precedence over variables from the input data source.

    To avoid ambiguity, variables prefixed with a dot (e.g., `.foo`) are always
    resolved from the data, while unprefixed variables (e.g., `foo`) are resolved
    from the context if present.
    """

    grammar = r"""
        ?start: or_expr

        ?or_expr: and_expr
                | or_expr ("or"i | "||")  and_expr      -> or_op

        ?and_expr: not_expr
                 | and_expr ("and"i | "&&") not_expr    -> and_op

        ?not_expr: comparison
                 | ("not"i | "!") comparison            -> not_op

        ?comparison: sum
                   | sum ">" sum            -> gt
                   | sum ">=" sum           -> gte
                   | sum "<" sum            -> lt
                   | sum "<=" sum           -> lte
                   | sum "=" sum            -> any_eq
                   | sum "==" sum           -> eq
                   | sum "in"i sum          -> in_op
                   | sum "contains"i sum    -> contains_op

        ?sum: product
            | sum "+" product            -> add
            | sum "-" product            -> sub

        ?product: range
                | product "*" range      -> mul
                | product "/" range      -> div
                | product "%" range      -> mod

        ?range: exists
              | exists ".." exists       -> range_op
              | range "." exists         -> concat_op

        ?exists: atom
               | VARIABLE "??"           -> exists_op
               | VARIABLE "??" atom      -> exists_with_default

        ?atom: NUMBER                    -> number
             | "-" atom                  -> neg
             | "(" or_expr ")"
             | ipv4_atom
             | ipv6_atom
             | datetime
             | TIMEDELTA                 -> timedelta
             | STRING                    -> string
             | VARIABLE                  -> variable
             | function
             | list

        ?ipv4_atom: IPV4                         -> ipv4_single
                  | IPV4_RANGE                   -> ipv4_range
                  | IPV4_CIDR                    -> ipv4_cidr

        ?ipv6_atom: IPV6                         -> ipv6_single
                  | IPV6_RANGE                   -> ipv6_range
                  | IPV6_CIDR                    -> ipv6_cidr

        datetime: DATE "T"i? TIME    -> datetime_full
                | DATE               -> datetime_only_date

        function: FUNCTION [args] ")"
        args: or_expr ("," or_expr)*

        list: "[" [atom ("," atom)*] "]"

        NUMBER: /\d+(\.\d+)?([eE][+-]?\d+)?/
        IPV4.2: /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/
        IPV4_RANGE.2: /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}-\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/
        IPV4_CIDR.2: /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2}/
        IPV6.2: /[:a-fA-F0-9]+:[:a-fA-F0-9]*/
        IPV6_RANGE.2: /[:a-fA-F0-9]+:[:a-fA-F0-9]*-[:a-fA-F0-9]+:[:a-fA-F0-9]*/
        IPV6_CIDR.2: /[:a-fA-F0-9]+:[:a-fA-F0-9]*\/\d{1,3}/
        DATE.2: /[0-9]{4}-[0-9]{2}-[0-9]{2}/
        TIME.2: /[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:[Zz]|(?:[+-][0-9]{2}:[0-9]{2}))?/
        TIMEDELTA.2: /([0-9]+[D|d])?[0-9]{2}:[0-9]{2}:[0-9]{2}/
        STRING: /"([^"]*)"|\'([^\']*)\'/
        VARIABLE: /\.?[_a-zA-Z][-_a-zA-Z0-9]*(?:\.?[_a-zA-Z][-_a-zA-Z0-9]*)*/
        FUNCTION.2: /[_a-zA-Z][_a-zA-Z0-9]*\(/

        %import common.WS
        %ignore WS
        """  # noqa

    def __init__(self, context: dict[str, Any] | None = None) -> None:
        """
        Initialize the Parser.

        Args:
            context (dict[str, Any] | None): Optional dictionary of variables that can
            be referenced in queries. Context variables override data variables unless
            the data variable is explicitly accessed with a leading dot.
        """
        # Determine the cache file of the grammar. By default, it's in the home
        # directory. But when the environment variable is set, use the value
        # from that variable. This is useful for GitLab CI/CD.
        cache_path = os.getenv("RANSACK_CACHE_PATH")
        if not cache_path:
            cache_path = str(Path("~/.cache/ransack_grammar_cache").expanduser())

        self.parser = Lark(
            self.grammar,
            parser="lalr",
            propagate_positions=True,
            cache=cache_path,
        )
        self.shaper = ExpressionTransformer(context)

    @no_type_check
    def parse(self, data: str) -> Tree[Token]:
        try:
            parsed_tree = self.parser.parse(data)
            return self.shaper.transform(parsed_tree)
        except UnexpectedInput as e:
            raise ParseError(e.line, e.column, e.get_context(data)) from None
        except VisitError as e:
            first_token = e.obj.children[0]
            last_token = e.obj.children[-1]

            # Extract context - input before and after the problematic tokens
            context_start_pos = max(first_token.start_pos - 40, 0)
            context_end_pos = min(last_token.end_pos + 40, len(data))
            raw_context = data[context_start_pos:context_end_pos]

            # Add '^' add the start of the problematic token
            context_with_caret = add_caret_to_context(
                context=raw_context,
                line=first_token.line,
                column=first_token.column,
                original_data=data,
                context_start_pos=context_start_pos,
            )

            raise ShapeError(
                str(e.orig_exc),
                line=first_token.line,
                column=first_token.column,
                context=context_with_caret,
                start_pos=first_token.start_pos,
                end_pos=last_token.end_pos,
                end_line=last_token.end_line,
                end_column=last_token.end_column,
            ) from None

    def parse_only(self, data: str) -> Tree[Token]:
        try:
            return self.parser.parse(data)
        except UnexpectedInput as e:
            raise ParseError(e.line, e.column, e.get_context(data)) from None
