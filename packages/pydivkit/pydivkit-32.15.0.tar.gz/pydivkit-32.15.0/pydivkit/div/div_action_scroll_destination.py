# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing
from typing import Union

from pydivkit.core import BaseDiv, Expr, Field

from . import (
    end_destination, index_destination, offset_destination, start_destination,
)


DivActionScrollDestination = Union[
    offset_destination.OffsetDestination,
    index_destination.IndexDestination,
    start_destination.StartDestination,
    end_destination.EndDestination,
]
