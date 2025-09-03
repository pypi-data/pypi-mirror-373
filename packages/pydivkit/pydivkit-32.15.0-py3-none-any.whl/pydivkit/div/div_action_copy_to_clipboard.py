# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div_action_copy_to_clipboard_content


# Copies data to the clipboard.
class DivActionCopyToClipboard(BaseDiv):

    def __init__(
        self, *,
        type: str = "copy_to_clipboard",
        content: typing.Optional[div_action_copy_to_clipboard_content.DivActionCopyToClipboardContent] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            type=type,
            content=content,
            **kwargs,
        )

    type: str = Field(default="copy_to_clipboard")
    content: div_action_copy_to_clipboard_content.DivActionCopyToClipboardContent = Field(
    )


DivActionCopyToClipboard.update_forward_refs()
