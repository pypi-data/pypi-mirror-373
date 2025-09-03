# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing
from typing import Union

from pydivkit.core import BaseDiv, Expr, Field

from . import div_text_range_mask_particles, div_text_range_mask_solid


DivTextRangeMask = Union[
    div_text_range_mask_particles.DivTextRangeMaskParticles,
    div_text_range_mask_solid.DivTextRangeMaskSolid,
]
