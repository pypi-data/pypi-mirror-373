# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, TypedDict

__all__ = ["DatasetRetrieveProvInfoParams"]


class DatasetRetrieveProvInfoParams(TypedDict, total=False):
    format: Literal["json", "tsv"]
    """A case insensitive string.

    Any value besides 'json' will have no effect. If the string is 'json',
    provenance info will be returned as a json. Otherwise, it will be returned as a
    tsv file
    """
