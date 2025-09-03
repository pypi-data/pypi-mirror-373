# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EntityListSiblingsParams"]


class EntityListSiblingsParams(TypedDict, total=False):
    include_old_revisions: Annotated[Literal["true", "false"], PropertyInfo(alias="include-old-revisions")]
    """A case insensitive string.

    Any value besides true will have no effect. If the string is 'true', datasets
    that are have newer revisions will be included, otherwise by default they are
    not included.
    """

    property_key: Literal["uuid"]
    """A case insensitive string.

    Any value besides 'uuid' will raise an error. If property_key=uuid is provided,
    rather than entire dictionary representations of each node, only the list of
    matching uuid's will be returned
    """

    status: Literal["New", "QA", "Published"]
    """A case insensitive string.

    Any value besides 'New', 'Qa', and 'Published' will raise an error. If a valid
    status is provided, only results matching that status (if they are datasets)
    will be returned
    """
