from typing import List, Optional

from seekrai.abstract import api_requestor
from seekrai.resources.resource_base import ResourceBase
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import (
    SeekrFlowRequest,
)
from seekrai.types.vectordb import (
    VectorDatabaseCreate,
    VectorDatabaseFileList,
    VectorDatabaseIngestionList,
    VectorDatabaseIngestionRequest,
    VectorDatabaseIngestionResponse,
    VectorDatabaseList,
    VectorDatabaseResponse,
)


class VectorDatabase(ResourceBase):
    def create(
        self,
        name: str,
        model: str,
        description: Optional[str] = None,
    ) -> VectorDatabaseResponse:
        """
        Create a new vector database.

        Args:
            name (str): Name of the vector database.
            model (str): Model used to generate the vectors.
            dimension (int): Dimension of the vectors.
            description (Optional[str], optional): Optional description. Defaults to None.

        Returns:
            VectorDatabaseResponse: Object containing information about the created vector database.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = VectorDatabaseCreate(
            name=name, model=model, description=description
        ).model_dump()

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/vectordb",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseResponse(**response.data)

    def list(self) -> VectorDatabaseList:
        """
        Lists all vector databases for the user.

        Returns:
            VectorDatabaseList: Object containing a list of vector databases.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/vectordb",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseList(**response.data)

    def retrieve(self, database_id: str) -> VectorDatabaseResponse:
        """
        Retrieves vector database details.

        Args:
            database_id (str): Vector database ID to retrieve.

        Returns:
            VectorDatabaseResponse: Object containing information about the vector database.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/vectordb/{database_id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseResponse(**response.data)

    def create_ingestion_job(
        self,
        database_id: str,
        files: List[str],
        method: str,
        token_count: int = 800,
        overlap_tokens: int = 100,
    ) -> VectorDatabaseIngestionResponse:
        """
        Start an ingestion job for the specified files.

        Args:
            database_id (str): ID of the vector database to ingest into.
            files (List[str]): List of file IDs to ingest.
            method (str): Method to use for ingestion.

        Returns:
            VectorDatabaseIngestionResponse: Object containing information about the created ingestion job.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = VectorDatabaseIngestionRequest(
            file_ids=files,
            method=method,
            token_count=token_count,
            overlap_tokens=overlap_tokens,
        ).model_dump()

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url=f"flow/vectordb/{database_id}/ingestion",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseIngestionResponse(**response.data)

    def list_ingestion_jobs(self, database_id: str) -> VectorDatabaseIngestionList:
        """
        Lists ingestion job history for a specific vector database.

        Args:
            database_id (str): ID of the vector database.

        Returns:
            VectorDatabaseIngestionList: Object containing a list of ingestion jobs.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/vectordb/{database_id}/ingestion",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseIngestionList(**response.data)

    def retrieve_ingestion_job(
        self, database_id: str, job_id: str
    ) -> VectorDatabaseIngestionResponse:
        """
        Retrieves ingestion job details.

        Args:
            database_id (str): ID of the vector database.
            job_id (str): Ingestion job ID to retrieve.

        Returns:
            VectorDatabaseIngestionResponse: Object containing information about the ingestion job.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/vectordb/{database_id}/ingestion/{job_id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseIngestionResponse(**response.data)

    def list_files(self, database_id: str) -> VectorDatabaseFileList:
        """
        Lists all files in a vector database.

        Args:
            database_id (str): ID of the vector database.

        Returns:
            VectorDatabaseFileList: Object containing a list of files in the vector database.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/vectordb/{database_id}/files",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseFileList(**response.data)

    def delete(self, database_id: str) -> None:
        """
        Delete a vector database.

        Args:
            database_id (str): ID of the vector database to delete.

        Returns:
            None
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="DELETE",
                url=f"flow/vectordb/{database_id}",
            ),
            stream=False,
        )

        # The endpoint returns 204 No Content
        return None


class AsyncVectorDatabase(ResourceBase):
    async def create(
        self,
        name: str,
        model: str,
        description: Optional[str] = None,
    ) -> VectorDatabaseResponse:
        """
        Create a new vector database asynchronously.

        Args:
            name (str): Name of the vector database.
            model (str): Model used to generate the vectors.
            description (Optional[str], optional): Optional description. Defaults to None.

        Returns:
            VectorDatabaseResponse: Object containing information about the created vector database.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = VectorDatabaseCreate(
            name=name, model=model, description=description
        ).model_dump()

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/vectordb",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseResponse(**response.data)

    async def list(self) -> VectorDatabaseList:
        """
        Lists all vector databases for the user asynchronously.

        Returns:
            VectorDatabaseList: Object containing a list of vector databases.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/vectordb",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseList(**response.data)

    async def retrieve(self, database_id: str) -> VectorDatabaseResponse:
        """
        Retrieves vector database details asynchronously.

        Args:
            database_id (str): Vector database ID to retrieve.

        Returns:
            VectorDatabaseResponse: Object containing information about the vector database.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/vectordb/{database_id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseResponse(**response.data)

    async def create_ingestion_job(
        self,
        database_id: str,
        files: List[str],
        method: str,
        token_count: int = 800,
        overlap_tokens: int = 100,
    ) -> VectorDatabaseIngestionResponse:
        """
        Start an ingestion job for the specified files asynchronously.

        Args:
            database_id (str): ID of the vector database to ingest into.
            files (List[str]): List of file IDs to ingest.
            method (str): Method to use for ingestion.

        Returns:
            VectorDatabaseIngestionResponse: Object containing information about the created ingestion job.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = VectorDatabaseIngestionRequest(
            file_ids=files,
            method=method,
            token_count=token_count,
            overlap_tokens=overlap_tokens,
        ).model_dump()

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url=f"flow/vectordb/{database_id}/ingestion",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseIngestionResponse(**response.data)

    async def list_ingestion_jobs(
        self, database_id: str
    ) -> VectorDatabaseIngestionList:
        """
        Lists ingestion job history for a specific vector database asynchronously.

        Args:
            database_id (str): ID of the vector database.

        Returns:
            VectorDatabaseIngestionList: Object containing a list of ingestion jobs.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/vectordb/{database_id}/ingestion",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseIngestionList(**response.data)

    async def retrieve_ingestion_job(
        self, database_id: str, job_id: str
    ) -> VectorDatabaseIngestionResponse:
        """
        Retrieves ingestion job details asynchronously.

        Args:
            database_id (str): ID of the vector database.
            job_id (str): Ingestion job ID to retrieve.

        Returns:
            VectorDatabaseIngestionResponse: Object containing information about the ingestion job.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/vectordb/{database_id}/ingestion/{job_id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseIngestionResponse(**response.data)

    async def list_files(self, database_id: str) -> VectorDatabaseFileList:
        """
        Lists all files in a vector database asynchronously.

        Args:
            database_id (str): ID of the vector database.

        Returns:
            VectorDatabaseFileList: Object containing a list of files in the vector database.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/vectordb/{database_id}/files",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return VectorDatabaseFileList(**response.data)

    async def delete(self, database_id: str) -> None:
        """
        Delete a vector database asynchronously.

        Args:
            database_id (str): ID of the vector database to delete.

        Returns:
            None
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="DELETE",
                url=f"flow/vectordb/{database_id}",
            ),
            stream=False,
        )

        # The endpoint returns 204 No Content
        return None
