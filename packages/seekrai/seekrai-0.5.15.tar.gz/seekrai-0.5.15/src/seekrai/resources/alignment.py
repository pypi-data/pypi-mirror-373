from typing import List

from seekrai.abstract import api_requestor
from seekrai.resources.resource_base import ResourceBase
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import (
    AlignmentEstimationRequest,
    AlignmentEstimationResponse,
    AlignmentList,
    AlignmentRequest,
    AlignmentResponse,
    AlignmentType,
    SeekrFlowRequest,
)


class Alignment(ResourceBase):
    def generate(
        self,
        instructions: str,
        files: List[str],
        type: AlignmentType = AlignmentType.PRINCIPLE,
    ) -> AlignmentResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = AlignmentRequest(
            instructions=instructions, files=files, type=type
        ).model_dump()

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/alignment/generate",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return AlignmentResponse(**response.data)

    def list(self) -> AlignmentList:
        """
        Lists alignment job history

        Returns:
            AlignmentList: Object containing a list of alignment jobs
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/alignment",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return AlignmentList(**response.data)

    def retrieve(self, id: str) -> AlignmentResponse:
        """
        Retrieves alignment job details

        Args:
            id (str): Alignment job ID to retrieve.

        Returns:
            AlignmentResponse: Object containing information about alignment job.
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/alignment/{id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return AlignmentResponse(**response.data)

    def estimate(self, files: List[str]) -> AlignmentEstimationResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = AlignmentEstimationRequest(
            files=files,
        ).model_dump()

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/alignment/estimate",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return AlignmentEstimationResponse(**response.data)


class AsyncAlignment(ResourceBase):
    async def generate(
        self,
        instructions: str,
        files: List[str],
        type: AlignmentType = AlignmentType.PRINCIPLE,
    ) -> AlignmentResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = AlignmentRequest(
            instructions=instructions, files=files, type=type
        ).model_dump()

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/alignment/generate",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return AlignmentResponse(**response.data)

    async def list(self) -> AlignmentList:
        """
        Lists alignment job history

        Returns:
            AlignmentList: Object containing a list of alignment jobs
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/alignment",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return AlignmentList(**response.data)

    async def retrieve(self, id: str) -> AlignmentResponse:
        """
        Retrieves alignment job details

        Args:
            id (str): Alignment job ID to retrieve.

        Returns:
            AlignmentResponse: Object containing information about alignment job.
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/alignment/{id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return AlignmentResponse(**response.data)

    async def estimate(self, files: List[str]) -> AlignmentEstimationResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = AlignmentEstimationRequest(
            files=files,
        ).model_dump()

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/alignment/estimate",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return AlignmentEstimationResponse(**response.data)
