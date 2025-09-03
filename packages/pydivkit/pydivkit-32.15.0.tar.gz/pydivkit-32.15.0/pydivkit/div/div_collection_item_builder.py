# Generated code. Do not modify.
# flake8: noqa: F401, F405, F811

from __future__ import annotations

import enum
import typing

from pydivkit.core import BaseDiv, Expr, Field

from . import div


class DivCollectionItemBuilder(BaseDiv):

    def __init__(
        self, *,
        data: typing.Optional[typing.Sequence[typing.Any]] = None,
        data_element_name: typing.Optional[typing.Union[Expr, str]] = None,
        prototypes: typing.Optional[typing.Sequence[DivCollectionItemBuilderPrototype]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            data=data,
            data_element_name=data_element_name,
            prototypes=prototypes,
            **kwargs,
        )

    data: typing.Sequence[typing.Any] = Field(
        description="Data that will be used to create collection elements.",
    )
    data_element_name: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "Name for accessing the next `data` element in the "
            "prototype. Working with thiselement is the same as with "
            "dictionaries."
        ),
    )
    prototypes: typing.Sequence[DivCollectionItemBuilderPrototype] = Field(
        min_items=1, 
        description=(
            "Array of `div` elements from which the collection elements "
            "will be created."
        ),
    )


class DivCollectionItemBuilderPrototype(BaseDiv):

    def __init__(
        self, *,
        div: typing.Optional[div.Div] = None,
        id: typing.Optional[typing.Union[Expr, str]] = None,
        selector: typing.Optional[typing.Union[Expr, bool]] = None,
        **kwargs: typing.Any,
    ):
        super().__init__(
            div=div,
            id=id,
            selector=selector,
            **kwargs,
        )

    div: div.Div = Field(
        description=(
            "`Div` from which the collection elements will be created. "
            "In `Div`, you can useexpressions using data from `data`. To "
            "access the next `data` element, you needto use the same "
            "prefix as in `data_element_prefix`."
        ),
    )
    id: typing.Optional[typing.Union[Expr, str]] = Field(
        description=(
            "`id` of the element to be created from the prototype. "
            "Unlike the `div-base.id`field, may contain expressions. Has "
            "a higher priority than `div-base.id`."
        ),
    )
    selector: typing.Optional[typing.Union[Expr, bool]] = Field(
        description=(
            "A condition that is used to select the prototype for the "
            "next element in thecollection. If there is more than 1 true "
            "condition, the earlier prototype isselected. If none of the "
            "conditions are met, the element from `data` is skipped."
        ),
    )


DivCollectionItemBuilderPrototype.update_forward_refs()


DivCollectionItemBuilder.update_forward_refs()
