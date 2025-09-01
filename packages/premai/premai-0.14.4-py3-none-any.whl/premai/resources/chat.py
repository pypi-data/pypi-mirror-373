# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Iterable, Optional
from typing_extensions import Literal

import httpx

from ..types import chat_completions_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.chat_completions_response import ChatCompletionsResponse

__all__ = ["ChatResource", "AsyncChatResource"]


class ChatResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ChatResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#accessing-raw-response-data-eg-headers
        """
        return ChatResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChatResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#with_streaming_response
        """
        return ChatResourceWithStreamingResponse(self)

    def completions(
        self,
        *,
        messages: Iterable[chat_completions_params.Message],
        model: str,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        response_format: chat_completions_params.ResponseFormat | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: Union[str, List[str]] | NotGiven = NOT_GIVEN,
        stream: bool | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Union[Literal["none", "auto"], object] | NotGiven = NOT_GIVEN,
        tools: Iterable[object] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatCompletionsResponse:
        """
        Create a chat completion (OpenAI compatible).

        Args:
          messages: An array of messages comprising the conversation so far. Must contain at least
              one message. System messages are only allowed as the first message.

          model: The identifier of the model to use for generating completions. This can be a
              model ID or an alias.

          frequency_penalty: A value between -2.0 and 2.0 that penalizes new tokens based on their frequency
              in the text so far. Higher values decrease the likelihood of the model repeating
              the same tokens.

          max_completion_tokens: The maximum number of tokens to generate in the completion. If null, will use
              the model's maximum context length. This is the maximum number of tokens that
              will be generated.

          presence_penalty: A value between -2.0 and 2.0 that penalizes new tokens based on whether they
              appear in the text so far. Higher values increase the likelihood of the model
              talking about new topics.

          response_format: Specifies the format of the model's output. Use "json_schema" to constrain
              responses to valid JSON matching the provided schema.

          seed: A seed value for deterministic sampling. Using the same seed with the same
              parameters will generate the same completion.

          stop: One or more sequences where the API will stop generating further tokens. Can be
              a single string or an array of strings.

          stream: If true, partial message deltas will be sent as server-sent events. Useful for
              showing progressive generation in real-time.

          temperature: Controls randomness in the model's output. Values between 0 and 2. Lower values
              make the output more focused and deterministic, higher values make it more
              random and creative.

          tool_choice: Controls how the model uses tools. "none" disables tools, "auto" lets the model
              decide, or specify a particular tool configuration.

          tools: A list of tools the model may call. Each tool has a specific function the model
              can use to achieve specific tasks.

          top_p: An alternative to temperature for controlling randomness. Controls the
              cumulative probability of tokens to consider. Lower values make output more
              focused.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/v1/chat/completions",
            body=maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "frequency_penalty": frequency_penalty,
                    "max_completion_tokens": max_completion_tokens,
                    "presence_penalty": presence_penalty,
                    "response_format": response_format,
                    "seed": seed,
                    "stop": stop,
                    "stream": stream,
                    "temperature": temperature,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_p": top_p,
                },
                chat_completions_params.ChatCompletionsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChatCompletionsResponse,
        )


class AsyncChatResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncChatResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncChatResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChatResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/premAI-io/prem-py-sdk#with_streaming_response
        """
        return AsyncChatResourceWithStreamingResponse(self)

    async def completions(
        self,
        *,
        messages: Iterable[chat_completions_params.Message],
        model: str,
        frequency_penalty: float | NotGiven = NOT_GIVEN,
        max_completion_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        presence_penalty: float | NotGiven = NOT_GIVEN,
        response_format: chat_completions_params.ResponseFormat | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        stop: Union[str, List[str]] | NotGiven = NOT_GIVEN,
        stream: bool | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tool_choice: Union[Literal["none", "auto"], object] | NotGiven = NOT_GIVEN,
        tools: Iterable[object] | NotGiven = NOT_GIVEN,
        top_p: Optional[float] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatCompletionsResponse:
        """
        Create a chat completion (OpenAI compatible).

        Args:
          messages: An array of messages comprising the conversation so far. Must contain at least
              one message. System messages are only allowed as the first message.

          model: The identifier of the model to use for generating completions. This can be a
              model ID or an alias.

          frequency_penalty: A value between -2.0 and 2.0 that penalizes new tokens based on their frequency
              in the text so far. Higher values decrease the likelihood of the model repeating
              the same tokens.

          max_completion_tokens: The maximum number of tokens to generate in the completion. If null, will use
              the model's maximum context length. This is the maximum number of tokens that
              will be generated.

          presence_penalty: A value between -2.0 and 2.0 that penalizes new tokens based on whether they
              appear in the text so far. Higher values increase the likelihood of the model
              talking about new topics.

          response_format: Specifies the format of the model's output. Use "json_schema" to constrain
              responses to valid JSON matching the provided schema.

          seed: A seed value for deterministic sampling. Using the same seed with the same
              parameters will generate the same completion.

          stop: One or more sequences where the API will stop generating further tokens. Can be
              a single string or an array of strings.

          stream: If true, partial message deltas will be sent as server-sent events. Useful for
              showing progressive generation in real-time.

          temperature: Controls randomness in the model's output. Values between 0 and 2. Lower values
              make the output more focused and deterministic, higher values make it more
              random and creative.

          tool_choice: Controls how the model uses tools. "none" disables tools, "auto" lets the model
              decide, or specify a particular tool configuration.

          tools: A list of tools the model may call. Each tool has a specific function the model
              can use to achieve specific tasks.

          top_p: An alternative to temperature for controlling randomness. Controls the
              cumulative probability of tokens to consider. Lower values make output more
              focused.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/v1/chat/completions",
            body=await async_maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "frequency_penalty": frequency_penalty,
                    "max_completion_tokens": max_completion_tokens,
                    "presence_penalty": presence_penalty,
                    "response_format": response_format,
                    "seed": seed,
                    "stop": stop,
                    "stream": stream,
                    "temperature": temperature,
                    "tool_choice": tool_choice,
                    "tools": tools,
                    "top_p": top_p,
                },
                chat_completions_params.ChatCompletionsParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChatCompletionsResponse,
        )


class ChatResourceWithRawResponse:
    def __init__(self, chat: ChatResource) -> None:
        self._chat = chat

        self.completions = to_raw_response_wrapper(
            chat.completions,
        )


class AsyncChatResourceWithRawResponse:
    def __init__(self, chat: AsyncChatResource) -> None:
        self._chat = chat

        self.completions = async_to_raw_response_wrapper(
            chat.completions,
        )


class ChatResourceWithStreamingResponse:
    def __init__(self, chat: ChatResource) -> None:
        self._chat = chat

        self.completions = to_streamed_response_wrapper(
            chat.completions,
        )


class AsyncChatResourceWithStreamingResponse:
    def __init__(self, chat: AsyncChatResource) -> None:
        self._chat = chat

        self.completions = async_to_streamed_response_wrapper(
            chat.completions,
        )
