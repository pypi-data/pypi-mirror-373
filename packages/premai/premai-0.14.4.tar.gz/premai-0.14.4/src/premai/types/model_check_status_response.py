# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from .._models import BaseModel

__all__ = ["ModelCheckStatusResponse"]


class ModelCheckStatusResponse(BaseModel):
    status: bool
    """Whether the model is running."""
