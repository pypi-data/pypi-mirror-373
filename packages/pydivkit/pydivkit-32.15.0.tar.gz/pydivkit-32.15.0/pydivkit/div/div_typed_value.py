# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing
from typing import Union

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    array_value, boolean_value, color_value, dict_value, integer_value,
    number_value, string_value, url_value,
)


DivTypedValue = Union[
    string_value.StringValue,
    integer_value.IntegerValue,
    number_value.NumberValue,
    color_value.ColorValue,
    boolean_value.BooleanValue,
    url_value.UrlValue,
    dict_value.DictValue,
    array_value.ArrayValue,
]
