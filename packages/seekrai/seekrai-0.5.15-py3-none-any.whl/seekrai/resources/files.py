from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from seekrai.abstract import api_requestor
from seekrai.filemanager import DownloadManager, UploadManager
from seekrai.resources.resource_base import ResourceBase
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import (
    FileDeleteResponse,
    FileList,
    FileObject,
    FilePurpose,
    FileResponse,
    SeekrFlowRequest,
)
from seekrai.types.files import (
    AlignFileMetadataValidationReq,
    AlignFileMetadataValidationResp,
)
from seekrai.utils import normalize_key


def _get_local_file_metadata(file_path: Path) -> Dict[str, Any]:
    suffix = file_path.suffix.lstrip(".")
    size_bytes = int(file_path.stat().st_size)
    return {
        "suffix": suffix,
        "size_bytes": size_bytes,
        "filename": file_path.name,
    }


class Files(ResourceBase):
    def upload(
        self, file: Path | str, *, purpose: FilePurpose | str = FilePurpose.FineTune
    ) -> FileResponse:
        if isinstance(file, str):
            file = Path(file)

        if isinstance(purpose, str):
            purpose = FilePurpose(purpose)

        assert isinstance(purpose, FilePurpose)

        # Do the metadata validation (fail fast before uploading) for Alignment purpose
        if purpose == FilePurpose.Alignment:
            file_metadata = _get_local_file_metadata(file)
            suffix = file_metadata["suffix"]
            size = file_metadata["size_bytes"]
            metadata_validation = self.validate_align_file_metadata(
                purpose,
                suffix,
                size,
            )

            if not metadata_validation.is_valid:
                assert metadata_validation.errors is not None  # To appease linter
                raise ValueError(
                    f"Alignment file metadata validation failed: {metadata_validation.errors}"
                )

        # Upload the file to s3
        upload_manager = UploadManager(self._client)
        file_response = upload_manager.upload(
            "flow/files", file, purpose=purpose, redirect=True
        )

        return file_response

    def bulk_upload(
        self,
        files: list[Path | str],
        *,
        purpose: FilePurpose | str = FilePurpose.FineTune,
    ) -> list[FileResponse]:
        """
        Upload multiple files in bulk.

        Args:
            files: List of file paths to upload
            purpose: The purpose of the files (defaults to FineTune)

        Returns:
            List of FileResponse objects for each uploaded file
        """
        if isinstance(purpose, str):
            purpose = FilePurpose(purpose)

        assert isinstance(purpose, FilePurpose)

        # Convert string paths to Path objects
        file_paths = [Path(file) if isinstance(file, str) else file for file in files]

        # Validate all files before uploading (fail fast)
        if purpose == FilePurpose.Alignment:
            for file_path in file_paths:
                file_metadata = _get_local_file_metadata(file_path)
                suffix = file_metadata["suffix"]
                size = file_metadata["size_bytes"]
                metadata_validation = self.validate_align_file_metadata(
                    purpose,
                    suffix,
                    size,
                )

                if not metadata_validation.is_valid:
                    assert metadata_validation.errors is not None  # To appease linter
                    raise ValueError(
                        f"Alignment file metadata validation failed for {file_path.name}: {metadata_validation.errors}"
                    )

        # Upload the files to s3
        upload_manager = UploadManager(self._client)
        file_responses = upload_manager.bulk_upload(
            "flow/bulk_files", file_paths, purpose=purpose, redirect=True
        )

        return file_responses

    def retrieve(self, id: str) -> FileResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/files/{id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FileResponse(**response.data)

    def retrieve_content(
        self, id: str, *, output: Path | str | None = None
    ) -> FileObject:
        download_manager = DownloadManager(self._client)

        if isinstance(output, str):
            output = Path(output)

        downloaded_filename, file_size = download_manager.download(
            f"flow/files/{id}/content", output, normalize_key(id)
        )

        return FileObject(
            object="local",
            id=id,
            filename=downloaded_filename,
            size=file_size,
        )

    def delete(self, id: str) -> FileDeleteResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="DELETE",
                url=f"flow/files/{id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FileDeleteResponse(**response.data)

    def validate_align_file_metadata(
        self,
        purpose: FilePurpose,
        suffix: str,
        size: int,
    ) -> AlignFileMetadataValidationResp:
        requestor = api_requestor.APIRequestor(client=self._client)

        request_body = AlignFileMetadataValidationReq(
            purpose=purpose,
            suffix=suffix,
            size=size,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/files/validate_metadata",
                params=request_body.model_dump(),
            ),
            stream=False,
        )

        return AlignFileMetadataValidationResp(**response.data)

    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        purpose: Optional[Union[FilePurpose, str]] = None,
    ) -> FileList:
        """
        List files with pagination, sorting, and filtering options.

        All parameter defaults are handled by the API if not specified.

        Args:
            limit: Maximum number of files to return
            offset: Number of files to skip
            sort_by: Field to sort by ('created_at', 'filename', 'type', or 'size')
            sort_order: Sort order ('asc' or 'desc')
            purpose: Filter by file purpose (FilePurpose enum or string)

        Returns:
            A FileList object containing the list of files

        Raises:
            Exception: If the API request fails
        """
        # Build query parameters, only including non-None values
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort_by is not None:
            params["sort_by"] = sort_by
        if sort_order is not None:
            params["sort_order"] = sort_order

        # Add purpose filter if provided, converting from enum if needed
        if purpose is not None:
            params["purpose"] = (
                purpose.value if isinstance(purpose, FilePurpose) else purpose
            )

        # Create request and use the API requestor
        requestor = api_requestor.APIRequestor(client=self._client)

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/files",
                params=params,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FileList.parse_obj(response.data)

    def rename(self, id: str, new_filename: str) -> FileResponse:
        """
        Rename a file.

        Args:
            id (str): ID of the file to rename.
            new_filename (str): New filename for the file.

        Returns:
            FileResponse: Object containing information about the renamed file.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/files/{id}/rename",
                params={"new_filename": new_filename},
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FileResponse(**response.data)


class AsyncFiles(ResourceBase):
    async def validate_align_file_metadata(
        self,
        purpose: FilePurpose,
        suffix: str,
        size: int,
    ) -> AlignFileMetadataValidationResp:
        requestor = api_requestor.APIRequestor(client=self._client)

        request_body = AlignFileMetadataValidationReq(
            purpose=purpose,
            suffix=suffix,
            size=size,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/files/validate_metadata",
                params=request_body.model_dump(),
            ),
            stream=False,
        )

        return AlignFileMetadataValidationResp(**response.data)

    async def retrieve(self, id: str) -> FileResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/files/{id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FileResponse(**response.data)

    async def retrieve_content(
        self, id: str, *, output: Path | str | None = None
    ) -> FileObject:
        raise NotImplementedError()

    async def delete(self, id: str) -> FileDeleteResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="DELETE",
                url=f"flow/files/{id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FileDeleteResponse(**response.data)

    async def bulk_upload(
        self,
        files: list[Path | str],
        *,
        purpose: FilePurpose | str = FilePurpose.FineTune,
    ) -> list[FileResponse]:
        """
        Upload multiple files in bulk asynchronously.

        Args:
            files: List of file paths to upload
            purpose: The purpose of the files (defaults to FineTune)

        Returns:
            List of FileResponse objects for each uploaded file
        """
        if isinstance(purpose, str):
            purpose = FilePurpose(purpose)

        assert isinstance(purpose, FilePurpose)

        # Convert string paths to Path objects
        file_paths = [Path(file) if isinstance(file, str) else file for file in files]

        # Validate all files before uploading (fail fast)
        if purpose == FilePurpose.Alignment:
            for file_path in file_paths:
                file_metadata = _get_local_file_metadata(file_path)
                suffix = file_metadata["suffix"]
                size = file_metadata["size_bytes"]
                metadata_validation = await self.validate_align_file_metadata(
                    purpose,
                    suffix,
                    size,
                )

                if not metadata_validation.is_valid:
                    assert metadata_validation.errors is not None  # To appease linter
                    raise ValueError(
                        f"Alignment file metadata validation failed for {file_path.name}: {metadata_validation.errors}"
                    )

        # Upload the files to s3
        upload_manager = UploadManager(self._client)
        file_responses = await upload_manager.bulk_upload_async(
            "flow/bulk_files", file_paths, purpose=purpose, redirect=True
        )

        return file_responses

    async def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = None,
        purpose: Optional[Union[FilePurpose, str]] = None,
    ) -> FileList:
        """
        List files with pagination, sorting, and filtering options.

        All parameter defaults are handled by the API if not specified.

        Args:
            limit: Maximum number of files to return
            offset: Number of files to skip
            sort_by: Field to sort by ('created_at', 'filename', 'type', or 'size')
            sort_order: Sort order ('asc' or 'desc')
            purpose: Filter by file purpose (FilePurpose enum or string)

        Returns:
            A FileList object containing the list of files

        Raises:
            Exception: If the API request fails
        """
        # Build query parameters, only including non-None values
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if sort_by is not None:
            params["sort_by"] = sort_by
        if sort_order is not None:
            params["sort_order"] = sort_order

        # Add purpose filter if provided, converting from enum if needed
        if purpose is not None:
            params["purpose"] = (
                purpose.value if isinstance(purpose, FilePurpose) else purpose
            )

        # Create request and use the API requestor
        requestor = api_requestor.APIRequestor(client=self._client)

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/files",
                params=params,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FileList.parse_obj(response.data)

    async def rename(self, id: str, new_filename: str) -> FileResponse:
        """
        Rename a file asynchronously.

        Args:
            id (str): ID of the file to rename.
            new_filename (str): New filename for the file.

        Returns:
            FileResponse: Object containing information about the renamed file.
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/files/{id}/rename",
                params={"new_filename": new_filename},
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FileResponse(**response.data)
