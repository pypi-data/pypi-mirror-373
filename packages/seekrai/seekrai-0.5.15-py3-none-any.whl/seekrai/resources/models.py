from __future__ import annotations

from seekrai.abstract import api_requestor
from seekrai.resources.resource_base import ResourceBase
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import ModelList, ModelResponse, SeekrFlowRequest
from seekrai.types.common import ObjectType


class Models(ResourceBase):
    def list(
        self,
    ) -> ModelList:
        """
        Method to return list of models on the API

        Returns:
            ModelList: List of model objects
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/models",
            ),
            stream=False,
        )
        assert isinstance(response, SeekrFlowResponse)

        model_responses = [
            ModelResponse(
                id=str(model["id"]),
                object=ObjectType.Model,
                name=model["name"],
                bytes=model["size"],
                model_type=model["model_type"],
            )
            for model in response.data["data"]
        ]

        return ModelList(data=model_responses)


class AsyncModels(ResourceBase):
    async def list(
        self,
    ) -> ModelList:
        """
        Async method to return list of models on API

        Returns:
            ModelList: List of model objects
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/models",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        assert isinstance(response.data, list)

        model_responses = [
            ModelResponse(
                id=str(model["id"]),
                object=ObjectType.Model,
                name=model["name"],
                bytes=model["size"],
                model_type=model["model_type"],
            )
            for model in response.data["data"]
        ]

        return ModelList(data=model_responses)
