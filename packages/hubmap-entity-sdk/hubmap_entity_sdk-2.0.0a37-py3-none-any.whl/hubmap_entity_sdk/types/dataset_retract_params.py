# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DatasetRetractParams"]


class DatasetRetractParams(TypedDict, total=False):
    retraction_reason: str
    """Free text describing why the dataset was retracted"""
