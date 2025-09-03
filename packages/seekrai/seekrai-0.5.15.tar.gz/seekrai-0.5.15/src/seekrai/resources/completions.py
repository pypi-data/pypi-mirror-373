from __future__ import annotations

from typing import AsyncGenerator, Iterator, List

from seekrai.abstract import api_requestor
from seekrai.resources.resource_base import ResourceBase
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import (
    CompletionChunk,
    CompletionRequest,
    CompletionResponse,
    SeekrFlowRequest,
)


class Completions(ResourceBase):
    def create(
        self,
        *,
        prompt: str,
        model: str,
        max_tokens: int | None = 512,
        stop: List[str] | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        repetition_penalty: float | None = None,
        stream: bool = False,
        logprobs: int | None = None,
        echo: bool | None = None,
        n: int | None = None,
        safety_model: str | None = None,
    ) -> CompletionResponse | Iterator[CompletionChunk]:
        """
        Method to generate completions based on a given prompt using a specified model.

        Args:
            prompt (str): A string providing context for the model to complete.
            model (str): The name of the model to query.
            max_tokens (int, optional): The maximum number of tokens to generate.
                Defaults to 512.
            stop (List[str], optional): List of strings at which to stop generation.
                Defaults to None.
            temperature (float, optional): A decimal number that determines the degree of randomness in the response.
                Defaults to None.
            top_p (float, optional): The top_p (nucleus) parameter is used to dynamically adjust the number
                    of choices for each predicted token based on the cumulative probabilities.
                Defaults to None.
            top_k (int, optional): The top_k parameter is used to limit the number of choices for the
                    next predicted word or token.
                Defaults to None.
            repetition_penalty (float, optional): A number that controls the diversity of generated text
                    by reducing the likelihood of repeated sequences. Higher values decrease repetition.
                Defaults to None.
            stream (bool, optional): Flag indicating whether to stream the generated completions.
                Defaults to False.
            logprobs (int, optional): Number of top-k logprobs to return
                Defaults to None.
            echo (bool, optional): Echo prompt in output. Can be used with logprobs to return prompt logprobs.
                Defaults to None.
            n (int, optional): Number of completions to generate. Setting to None will return a single generation.
                Defaults to None.
            safety_model (str, optional): A moderation model to validate tokens. Choice between available moderation
                    models found [here](https://docs.seekrflow.ai/docs/inference-models#moderation-models).
                Defaults to None.

        Returns:
            CompletionResponse | Iterator[CompletionChunk]: Object containing the completions
            or an iterator over completion chunks.
        """
        raise NotImplementedError("function not yet implemented")
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = CompletionRequest(
            model=model,
            prompt=prompt,
            top_p=top_p,
            top_k=top_k,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            repetition_penalty=repetition_penalty,
            stream=stream,
            logprobs=logprobs,
            echo=echo,
            n=n,
            safety_model=safety_model,
        ).model_dump()

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="inference/completions",
                params=parameter_payload,
            ),
            stream=stream,
        )

        if stream:
            # must be an iterator
            assert not isinstance(response, SeekrFlowResponse)
            return (CompletionChunk(**line.data) for line in response)
        assert isinstance(response, SeekrFlowResponse)
        return CompletionResponse(**response.data)


class AsyncCompletions(ResourceBase):
    async def create(
        self,
        *,
        prompt: str,
        model: str,
        max_tokens: int | None = 512,
        stop: List[str] | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        repetition_penalty: float | None = None,
        stream: bool = False,
        logprobs: int | None = None,
        echo: bool | None = None,
        n: int | None = None,
        safety_model: str | None = None,
    ) -> AsyncGenerator[CompletionChunk, None] | CompletionResponse:
        """
        Async method to generate completions based on a given prompt using a specified model.

        Args:
            prompt (str): A string providing context for the model to complete.
            model (str): The name of the model to query.
            max_tokens (int, optional): The maximum number of tokens to generate.
                Defaults to 512.
            stop (List[str], optional): List of strings at which to stop generation.
                Defaults to None.
            temperature (float, optional): A decimal number that determines the degree of randomness in the response.
                Defaults to None.
            top_p (float, optional): The top_p (nucleus) parameter is used to dynamically adjust the number
                    of choices for each predicted token based on the cumulative probabilities.
                Defaults to None.
            top_k (int, optional): The top_k parameter is used to limit the number of choices for the
                    next predicted word or token.
                Defaults to None.
            repetition_penalty (float, optional): A number that controls the diversity of generated text
                    by reducing the likelihood of repeated sequences. Higher values decrease repetition.
                Defaults to None.
            stream (bool, optional): Flag indicating whether to stream the generated completions.
                Defaults to False.
            logprobs (int, optional): Number of top-k logprobs to return
                Defaults to None.
            echo (bool, optional): Echo prompt in output. Can be used with logprobs to return prompt logprobs.
                Defaults to None.
            n (int, optional): Number of completions to generate. Setting to None will return a single generation.
                Defaults to None.
            safety_model (str, optional): A moderation model to validate tokens. Choice between available moderation
                    models found [here](https://docs.seekrflow.ai/docs/inference-models#moderation-models).
                Defaults to None.

        Returns:
            AsyncGenerator[CompletionChunk, None] | CompletionResponse: Object containing the completions
            or an iterator over completion chunks.
        """
        raise NotImplementedError("function not yet implemented")
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = CompletionRequest(
            model=model,
            prompt=prompt,
            top_p=top_p,
            top_k=top_k,
            temperature=temperature,
            max_tokens=max_tokens,
            stop=stop,
            repetition_penalty=repetition_penalty,
            stream=stream,
            logprobs=logprobs,
            echo=echo,
            n=n,
            safety_model=safety_model,
        ).model_dump()

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="inference/completions",
                params=parameter_payload,
            ),
            stream=stream,
        )

        if stream:
            # must be an iterator
            assert not isinstance(response, SeekrFlowResponse)
            return (CompletionChunk(**line.data) async for line in response)
        assert isinstance(response, SeekrFlowResponse)
        return CompletionResponse(**response.data)
