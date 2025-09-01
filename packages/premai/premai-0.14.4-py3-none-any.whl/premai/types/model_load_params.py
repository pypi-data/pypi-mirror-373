# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ModelLoadParams"]


class ModelLoadParams(TypedDict, total=False):
    model: Required[str]
    """The ID or alias of the model to load up."""
