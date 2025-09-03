# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["EntityListUploadsParams"]


class EntityListUploadsParams(TypedDict, total=False):
    property: Literal["uuid"]
    """A case insensitive string.

    Any value besides 'uuid' will raise an error. If property=uuid is provided,
    rather than entire dictionary representations of each node, only the list of
    matching uuid's will be returned
    """
