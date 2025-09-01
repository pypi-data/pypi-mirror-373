# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["ChatCompletionsParams", "Message", "MessageToolCall", "MessageToolCallFunction", "ResponseFormat"]


class ChatCompletionsParams(TypedDict, total=False):
    messages: Required[Iterable[Message]]
    """An array of messages comprising the conversation so far.

    Must contain at least one message. System messages are only allowed as the first
    message.
    """

    model: Required[str]
    """The identifier of the model to use for generating completions.

    This can be a model ID or an alias.
    """

    frequency_penalty: float
    """
    A value between -2.0 and 2.0 that penalizes new tokens based on their frequency
    in the text so far. Higher values decrease the likelihood of the model repeating
    the same tokens.
    """

    max_completion_tokens: Optional[int]
    """The maximum number of tokens to generate in the completion.

    If null, will use the model's maximum context length. This is the maximum number
    of tokens that will be generated.
    """

    presence_penalty: float
    """
    A value between -2.0 and 2.0 that penalizes new tokens based on whether they
    appear in the text so far. Higher values increase the likelihood of the model
    talking about new topics.
    """

    response_format: ResponseFormat
    """Specifies the format of the model's output.

    Use "json_schema" to constrain responses to valid JSON matching the provided
    schema.
    """

    seed: int
    """A seed value for deterministic sampling.

    Using the same seed with the same parameters will generate the same completion.
    """

    stop: Union[str, List[str]]
    """One or more sequences where the API will stop generating further tokens.

    Can be a single string or an array of strings.
    """

    stream: bool
    """If true, partial message deltas will be sent as server-sent events.

    Useful for showing progressive generation in real-time.
    """

    temperature: Optional[float]
    """Controls randomness in the model's output.

    Values between 0 and 2. Lower values make the output more focused and
    deterministic, higher values make it more random and creative.
    """

    tool_choice: Union[Literal["none", "auto"], object]
    """Controls how the model uses tools.

    "none" disables tools, "auto" lets the model decide, or specify a particular
    tool configuration.
    """

    tools: Iterable[object]
    """A list of tools the model may call.

    Each tool has a specific function the model can use to achieve specific tasks.
    """

    top_p: Optional[float]
    """An alternative to temperature for controlling randomness.

    Controls the cumulative probability of tokens to consider. Lower values make
    output more focused.
    """


class MessageToolCallFunction(TypedDict, total=False):
    arguments: Required[str]
    """The arguments to pass to the function as a JSON string"""

    name: Required[str]
    """The name of the function to call"""


class MessageToolCall(TypedDict, total=False):
    id: Required[str]
    """A unique identifier for this tool call"""

    function: Required[MessageToolCallFunction]

    type: Required[Literal["function"]]
    """The type of tool call"""


class Message(TypedDict, total=False):
    role: Required[Literal["system", "user", "assistant", "tool"]]
    """The role of the message sender.

    "system" is for system-level instructions, "user" represents the end user, and
    "assistant" represents the AI model's responses.
    """

    content: Optional[str]
    """The actual text content of the message.

    Note that this can be null in certain cases, such as when the message contains
    tool calls or when specific roles don't require content.
    """

    name: str
    """The name of the function to call, if any."""

    tool_call_id: str
    """
    The ID of the tool call that this message is a response to (only for tool role
    messages)
    """

    tool_calls: Iterable[MessageToolCall]
    """Tool calls to be made by the assistant"""


class ResponseFormat(TypedDict, total=False):
    json_schema: Required[Dict[str, object]]

    type: Required[Literal["text", "json_schema"]]
