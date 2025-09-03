# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing
from typing import Union

from pydivkit.core import BaseDiv, Expr, Field

from . import content_text, content_url


DivActionCopyToClipboardContent = Union[
    content_text.ContentText,
    content_url.ContentUrl,
]
