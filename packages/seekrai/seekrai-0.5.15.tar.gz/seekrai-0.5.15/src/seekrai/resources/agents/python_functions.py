from pathlib import Path
from typing import Union

from seekrai.abstract import api_requestor
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import SeekrFlowClient, SeekrFlowRequest
from seekrai.types.agents.python_functions import (
    DeletePythonFunctionResponse,
    PythonFunctionResponse,
)


class CustomFunctions:
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client
        self._requestor = api_requestor.APIRequestor(
            client=self._client,
        )

    def create(
        self, file_path: Union[str, Path], description: Union[str, None] = None
    ) -> PythonFunctionResponse:
        """
        Upload a new Python function for the user.

        Args:
            file_path: Path to the Python function file to upload (can be relative or absolute).
            description: Optional description for the function.

        Returns:
            The newly created Python function.
        """
        # Convert string to Path if needed
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Read the file contents
        with file_path.open("rb") as f:
            file_content = f.read()

        # Prepare multipart form data
        files = {"file": (file_path.name, file_content, "text/plain")}
        params = {}
        if description:
            params["description"] = description

        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="functions/",
                files=files,
                params=params,
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return PythonFunctionResponse(**response.data)

    def retrieve(self, function_id: str) -> PythonFunctionResponse:
        """
        Retrieve a Python function by its ID.

        Args:
            function_id: The ID of the Python function to retrieve.

        Returns:
            The Python function.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"functions/{function_id}",
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return PythonFunctionResponse(**response.data)

    def list_functions(
        self, limit: int = 20, offset: int = 0, order: str = "desc"
    ) -> list[PythonFunctionResponse]:
        """
        List all Python functions for the user.

        Args:
            limit: Maximum number of functions to return (default: 20).
            offset: Number of functions to skip (default: 0).
            order: Sort order, 'asc' or 'desc' (default: 'desc').

        Returns:
            A list of Python functions.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url="functions/",
                params={"limit": limit, "offset": offset, "order": order},
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        functions = [PythonFunctionResponse(**func) for func in response.data]  # type: ignore
        return functions

    def update(
        self,
        function_id: str,
        file_path: Union[str, Path, None] = None,
        description: Union[str, None] = None,
    ) -> PythonFunctionResponse:
        """
        Update an existing Python function.

        Args:
            function_id: The ID of the Python function to update.
            file_path: Optional path to a new Python function file (can be relative or absolute).
            description: Optional new description for the function.

        Returns:
            The updated Python function.
        """
        files = None
        params = {}

        if file_path:
            # Convert string to Path if needed
            if isinstance(file_path, str):
                file_path = Path(file_path)

            # Read the file contents
            with file_path.open("rb") as f:
                file_content = f.read()

            # Prepare multipart form data
            files = {"file": (file_path.name, file_content, "text/plain")}

        if description:
            params["description"] = description

        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="PATCH",
                url=f"functions/{function_id}",
                files=files,
                params=params,
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return PythonFunctionResponse(**response.data)

    def delete(self, function_id: str) -> DeletePythonFunctionResponse:
        """
        Delete a Python function by its ID.

        Args:
            function_id: The ID of the Python function to delete.

        Returns:
            A response indicating whether the delete operation was successful.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="DELETE",
                url=f"functions/{function_id}",
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return DeletePythonFunctionResponse(**response.data)


class AsyncCustomFunctions:
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client
        self._requestor = api_requestor.APIRequestor(
            client=self._client,
        )

    async def create(
        self, file_path: Union[str, Path], description: Union[str, None] = None
    ) -> PythonFunctionResponse:
        """
        Upload a new Python function for the user.

        Args:
            file_path: Path to the Python function file to upload (can be relative or absolute).
            description: Optional description for the function.

        Returns:
            The newly created Python function.
        """
        # Convert string to Path if needed
        if isinstance(file_path, str):
            file_path = Path(file_path)

        # Read the file contents
        with file_path.open("rb") as f:
            file_content = f.read()

        # Prepare multipart form data
        files = {"file": (file_path.name, file_content, "text/plain")}
        params = {}
        if description:
            params["description"] = description

        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="functions/",
                files=files,
                params=params,
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return PythonFunctionResponse(**response.data)

    async def retrieve(self, function_id: str) -> PythonFunctionResponse:
        """
        Retrieve a Python function by its ID.

        Args:
            function_id: The ID of the Python function to retrieve.

        Returns:
            The Python function.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"functions/{function_id}",
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return PythonFunctionResponse(**response.data)

    async def list_functions(
        self, limit: int = 20, offset: int = 0, order: str = "desc"
    ) -> list[PythonFunctionResponse]:
        """
        List all Python functions for the user.

        Args:
            limit: Maximum number of functions to return (default: 20).
            offset: Number of functions to skip (default: 0).
            order: Sort order, 'asc' or 'desc' (default: 'desc').

        Returns:
            A list of Python functions.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url="functions/",
                params={"limit": limit, "offset": offset, "order": order},
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        functions = [PythonFunctionResponse(**func) for func in response.data]  # type: ignore
        return functions

    async def update(
        self,
        function_id: str,
        file_path: Union[str, Path, None] = None,
        description: Union[str, None] = None,
    ) -> PythonFunctionResponse:
        """
        Update an existing Python function.

        Args:
            function_id: The ID of the Python function to update.
            file_path: Optional path to a new Python function file (can be relative or absolute).
            description: Optional new description for the function.

        Returns:
            The updated Python function.
        """
        files = None
        params = {}

        if file_path:
            # Convert string to Path if needed
            if isinstance(file_path, str):
                file_path = Path(file_path)

            # Read the file contents
            with file_path.open("rb") as f:
                file_content = f.read()

            # Prepare multipart form data
            files = {"file": (file_path.name, file_content, "text/plain")}

        if description:
            params["description"] = description

        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="PATCH",
                url=f"functions/{function_id}",
                files=files,
                params=params,
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return PythonFunctionResponse(**response.data)

    async def delete(self, function_id: str) -> DeletePythonFunctionResponse:
        """
        Delete a Python function by its ID.

        Args:
            function_id: The ID of the Python function to delete.

        Returns:
            A response indicating whether the delete operation was successful.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="DELETE",
                url=f"functions/{function_id}",
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return DeletePythonFunctionResponse(**response.data)
