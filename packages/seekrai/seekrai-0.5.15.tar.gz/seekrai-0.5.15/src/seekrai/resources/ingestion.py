from typing import List

from seekrai.abstract import api_requestor
from seekrai.resources.resource_base import ResourceBase
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import (
    SeekrFlowRequest,
)
from seekrai.types.ingestion import IngestionList, IngestionRequest, IngestionResponse


class Ingestion(ResourceBase):
    def ingest(
        self,
        files: List[str],
    ) -> IngestionResponse:
        """
        Start an ingestion job for the specified files.

        Args:
            files (List[str]): List of file IDs to ingest.

        Returns:
            IngestionResponse: Object containing information about the created ingestion job.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = IngestionRequest(
            files=files,
        ).model_dump()

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/alignment/ingestion",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return IngestionResponse(**response.data)

    def list(self) -> IngestionList:
        """
        Lists ingestion job history

        Returns:
            IngestionList: Object containing a list of ingestion jobs
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/alignment/ingestion",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return IngestionList(**response.data)

    def retrieve(self, id: str) -> IngestionResponse:
        """
        Retrieves ingestion job details

        Args:
            id (str): Ingestion job ID to retrieve.

        Returns:
            IngestionResponse: Object containing information about ingestion job.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/alignment/ingestion/{id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return IngestionResponse(**response.data)


class AsyncIngestion(ResourceBase):
    async def ingest(
        self,
        files: List[str],
    ) -> IngestionResponse:
        """
        Start an ingestion job for the specified files asynchronously.

        Args:
            files (List[str]): List of file IDs to ingest.

        Returns:
            IngestionResponse: Object containing information about the created ingestion job.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = IngestionRequest(
            files=files,
        ).model_dump()

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/alignment/ingestion",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return IngestionResponse(**response.data)

    async def list(self) -> IngestionList:
        """
        Lists ingestion job history asynchronously

        Returns:
            IngestionList: Object containing a list of ingestion jobs
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/alignment/ingestion",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return IngestionList(**response.data)

    async def retrieve(self, id: str) -> IngestionResponse:
        """
        Retrieves ingestion job details asynchronously

        Args:
            id (str): Ingestion job ID to retrieve.

        Returns:
            IngestionResponse: Object containing information about ingestion job.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/alignment/ingestion/{id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return IngestionResponse(**response.data)
