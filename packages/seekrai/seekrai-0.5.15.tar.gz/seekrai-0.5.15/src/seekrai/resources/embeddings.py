from __future__ import annotations

from typing import List

from seekrai.abstract import api_requestor
from seekrai.resources.resource_base import ResourceBase
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import (
    EmbeddingRequest,
    EmbeddingResponse,
    SeekrFlowRequest,
)


class Embeddings(ResourceBase):
    def create(
        self,
        *,
        input: str | List[str],
        model: str,
    ) -> EmbeddingResponse:
        """
        Method to generate completions based on a given prompt using a specified model.

        Args:
            input (str | List[str]): A string or list of strings to embed
            model (str): The name of the model to query.

        Returns:
            EmbeddingResponse: Object containing embeddings
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = EmbeddingRequest(
            input=input,
            model=model,
        ).model_dump()

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="inference/embeddings",
                params=parameter_payload,
                headers={"content-type": "application/json"},
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return EmbeddingResponse(**response.data)


class AsyncEmbeddings(ResourceBase):
    async def create(
        self,
        *,
        input: str | List[str],
        model: str,
    ) -> EmbeddingResponse:
        """
        Async method to generate completions based on a given prompt using a specified model.

        Args:
            input (str | List[str]): A string or list of strings to embed
            model (str): The name of the model to query.

        Returns:
            EmbeddingResponse: Object containing embeddings
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = EmbeddingRequest(
            input=input,
            model=model,
        ).model_dump()

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="inference/embeddings",
                params=parameter_payload,
                headers={"content-type": "application/json"},
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return EmbeddingResponse(**response.data)
