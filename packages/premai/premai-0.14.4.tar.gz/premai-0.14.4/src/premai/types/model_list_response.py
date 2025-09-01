# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ModelListResponse", "Data"]


class Data(BaseModel):
    id: str
    """The unique identifier of the model.

    This can be used to specify the model in API requests. For fine-tuned models,
    this may include a user-specific prefix.
    """

    created: int
    """Unix timestamp (in seconds) when this model was created or made available.

    For fine-tuned models, this represents when the fine-tuning was completed.
    """

    object: Literal["model"]
    """The type of object represented, which is always "model" for model objects.

    This helps distinguish model objects from other types of responses.
    """

    owned_by: str
    """Identifies the owner or provider of the model.

    Can be "premai" for base models, a user ID for fine-tuned models, or other
    providers like "openai" or "anthropic".
    """


class ModelListResponse(BaseModel):
    data: List[Data]
    """An array containing the available models.

    Each element is a complete model object with all its properties.
    """

    object: Literal["list"]
    """The type of object returned, always "list" for model listing responses.

    Helps identify this as a collection of models.
    """
