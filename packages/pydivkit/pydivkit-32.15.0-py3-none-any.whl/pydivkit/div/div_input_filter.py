# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing
from typing import Union

from pydivkit.core import BaseDiv, Expr, Field

from . import div_input_filter_expression, div_input_filter_regex


DivInputFilter = Union[
    div_input_filter_regex.DivInputFilterRegex,
    div_input_filter_expression.DivInputFilterExpression,
]
