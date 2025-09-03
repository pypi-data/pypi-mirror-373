from __future__ import annotations

import os
import shutil
import stat
import tempfile
import uuid
from pathlib import Path
from typing import Tuple

import httpx
import requests
from requests.structures import CaseInsensitiveDict
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

import seekrai.utils
from seekrai.abstract import api_requestor
from seekrai.constants import DISABLE_TQDM
from seekrai.error import (
    APIError,
    AuthenticationError,
    DownloadError,
    FileTypeError,
)
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import (
    FilePurpose,
    FileResponse,
    FileType,
    SeekrFlowClient,
    SeekrFlowRequest,
)


def chmod_and_replace(src: Path, dst: Path) -> None:
    """Set correct permission before moving a blob from tmp directory to cache dir.

    Do not take into account the `umask` from the process as there is no convenient way
    to get it that is thread-safe.
    """

    # Get umask by creating a temporary file in the cache folder.
    tmp_file = dst.parent / f"tmp_{uuid.uuid4()}"

    # try:
    tmp_file.touch()

    cache_dir_mode = Path(tmp_file).stat().st_mode

    os.chmod(src.as_posix(), stat.S_IMODE(cache_dir_mode))

    # finally:
    #     tmp_file.unlink()

    shutil.move(src.as_posix(), dst.as_posix())


def _get_file_size(
    headers: CaseInsensitiveDict[str],
) -> int:
    """
    Extracts file size from header
    """
    total_size_in_bytes = 0

    parts = headers.get("Content-Range", "").split(" ")

    if len(parts) == 2:
        range_parts = parts[1].split("/")

        if len(range_parts) == 2:
            total_size_in_bytes = int(range_parts[1])

    assert total_size_in_bytes != 0, "Unable to retrieve remote file."

    return total_size_in_bytes


def _prepare_output(
    headers: CaseInsensitiveDict[str],
    step: int = -1,
    output: Path | None = None,
    remote_name: str | None = None,
) -> Path:
    """
    Generates output file name from remote name and headers
    """
    if output:
        return output

    content_type = str(headers.get("content-type"))

    assert remote_name, (
        "No model name found in fine_tune object. Please specify an `output` file name."
    )

    if step > 0:
        remote_name += f"-checkpoint-{step}"

    if "x-tar" in content_type.lower():
        remote_name += ".tar.gz"

    elif "zstd" in content_type.lower() or step != -1:
        remote_name += ".tar.zst"

    else:
        raise FileTypeError(
            f"Unknown file type {content_type} found. Aborting download."
        )

    return Path(remote_name)


class DownloadManager:
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client

    def get_file_metadata(
        self,
        url: str,
        output: Path | None = None,
        remote_name: str | None = None,
        fetch_metadata: bool = False,
    ) -> Tuple[Path, int]:
        """
        gets remote file head and parses out file name and file size
        """

        if not fetch_metadata:
            if isinstance(output, Path):
                file_path = output
            else:
                assert isinstance(remote_name, str)
                file_path = Path(remote_name)

            return file_path, 0

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response = requestor.request_raw(
            options=SeekrFlowRequest(
                method="GET",
                url=url,
                headers={"Range": "bytes=0-1"},
            ),
            stream=False,
        )

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise APIError(
                "Error fetching file metadata", http_status=response.status_code
            ) from e

        headers = response.headers

        assert isinstance(headers, CaseInsensitiveDict)

        file_path = _prepare_output(
            headers=headers,
            output=output,
            remote_name=remote_name,
        )

        file_size = _get_file_size(headers)

        return file_path, file_size

    def download(
        self,
        url: str,
        output: Path | None = None,
        remote_name: str | None = None,
        fetch_metadata: bool = False,
    ) -> Tuple[str, int]:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        # pre-fetch remote file name and file size
        file_path, file_size = self.get_file_metadata(
            url, output, remote_name, fetch_metadata
        )

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            response = requestor.request_raw(
                options=SeekrFlowRequest(
                    method="GET",
                    url=url,
                ),
                stream=False,
            )

            try:
                response.raise_for_status()
            except Exception as e:
                raise APIError(
                    "Error downloading file", http_status=response.status_code
                ) from e

            if not fetch_metadata:
                file_size = int(response.headers.get("content-length", 0))

            assert file_size != 0, "Unable to retrieve remote file."

            with tqdm(
                total=file_size,
                unit="B",
                unit_scale=True,
                desc=f"Downloading file {file_path.name}",
                disable=bool(DISABLE_TQDM),
            ) as pbar:
                num_bytes_downloaded = response.num_bytes_downloaded
                for chunk in response.iter_bytes():
                    temp_file.write(chunk)
                    pbar.update(response.num_bytes_downloaded - num_bytes_downloaded)
                    num_bytes_downloaded = response.num_bytes_downloaded

            # Raise exception if remote file size does not match downloaded file size
            temp_file_size = os.stat(temp_file.name).st_size
            if temp_file_size != file_size:
                DownloadError(
                    f"Downloaded file size `{temp_file_size}` bytes does not match "
                    f"remote file size `{file_size}` bytes."
                )

            # Moves temp file to output file path
            chmod_and_replace(Path(temp_file.name), file_path)

        return str(file_path.resolve()), file_size


class UploadManager:
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client

    @classmethod
    def _redirect_error_handler(
        cls, requestor: api_requestor.APIRequestor, response: httpx.Response
    ) -> None:
        if response.status_code == 401:
            raise AuthenticationError(
                "This job would exceed your free trial credits. "
                "Please upgrade to a paid account through "
                "Settings -> Billing on api.seekrai.ai to continue.",
            )
        elif response.status_code != 302:
            raise APIError(
                f"Unexpected error raised by endpoint: {response.content.decode()}, headers: {response.headers}",
                http_status=response.status_code,
            )

    def get_upload_url(
        self,
        url: str,
        file: Path,
        purpose: FilePurpose,
        filetype: FileType,
    ) -> Tuple[str, str]:
        data = {
            "purpose": purpose.value,
            "file_name": file.name,
            "file_type": filetype.value,
        }

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        method = "POST"

        headers = seekrai.utils.get_headers(method, requestor.api_key)

        response = requestor.request_raw(
            options=SeekrFlowRequest(
                method=method,
                url=url,
                params=data,
                allow_redirects=False,
                override_headers=True,
                headers=headers,
            ),
        )

        self._redirect_error_handler(requestor, response)

        redirect_url = response.headers["Location"]
        file_id = response.headers["X-SeekrFlow-File-Id"]

        return redirect_url, file_id

    def callback(self, url: str) -> SeekrFlowResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url=url,
            ),
        )

        return response

    def upload(
        self,
        url: str,
        file: Path,
        purpose: FilePurpose,
        redirect: bool = False,
    ) -> FileResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        file_size = os.stat(file.as_posix()).st_size

        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            desc=f"Uploading file {file.name}",
            disable=bool(DISABLE_TQDM),
        ) as t:
            with file.open("rb") as f:
                reader_wrapper = CallbackIOWrapper(t.update, f, "read")
                response, _, _ = requestor.request(
                    options=SeekrFlowRequest(
                        method="PUT",
                        url=url,
                        files={"files": reader_wrapper, "filename": file.name},
                        params={"purpose": purpose.value},
                    ),
                )

        assert isinstance(response, SeekrFlowResponse)

        return FileResponse(**response.data)

    def bulk_upload(
        self,
        url: str,
        files: list[Path],
        *,
        purpose: FilePurpose,
        redirect: bool = False,
    ) -> list[FileResponse]:
        """
        Upload multiple files in a bulk request.

        Args:
            url: API endpoint to upload to
            files: List of file paths to upload
            purpose: The purpose of the files
            redirect: Whether to redirect after upload

        Returns:
            List of FileResponse objects for each uploaded file
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        # Prepare files for multipart form upload
        # Format needs to be a list of tuples: [('files', (filename, file_stream)), ...]
        files_tuples = []
        file_streams = []
        progress_bars = []

        try:
            for file_path in files:
                file_size = os.stat(file_path.as_posix()).st_size

                # Create progress bar
                progress_bar = tqdm(
                    total=file_size,
                    unit="B",
                    unit_scale=True,
                    desc=f"Uploading file {file_path.name}",
                    disable=bool(DISABLE_TQDM),
                )
                progress_bars.append(progress_bar)

                # Open file and track for cleanup
                file_stream = file_path.open("rb")
                file_streams.append(file_stream)

                # Create wrapper for progress tracking
                reader_wrapper = CallbackIOWrapper(
                    progress_bar.update, file_stream, "read"
                )

                # Add to files list as a tuple
                files_tuples.append(("files", (file_path.name, reader_wrapper)))

            # Make the request
            response, _, _ = requestor.request(
                options=SeekrFlowRequest(
                    method="PUT",
                    url=url,
                    files=files_tuples,  # Pass as a list of tuples (field_name, (filename, file_stream))
                    params={"purpose": purpose.value},
                    allow_redirects=redirect,
                ),
                stream=False,
            )

            assert isinstance(response, SeekrFlowResponse)

            # Parse the response
            if isinstance(response.data, list):
                file_responses = [
                    FileResponse(**file_data) for file_data in response.data
                ]
            else:
                # Handle case where response might be a single object
                file_responses = [FileResponse(**response.data)]

            return file_responses

        finally:
            # Clean up resources
            for file_stream in file_streams:
                file_stream.close()

            for progress_bar in progress_bars:
                progress_bar.close()

    async def bulk_upload_async(
        self,
        url: str,
        files: list[Path],
        *,
        purpose: FilePurpose,
        redirect: bool = False,
    ) -> list[FileResponse]:
        """
        Upload multiple files in a bulk request.

        Args:
            url: API endpoint to upload to
            files: List of file paths to upload
            purpose: The purpose of the files
            redirect: Whether to redirect after upload

        Returns:
            List of FileResponse objects for each uploaded file
        """
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        # Prepare files for multipart form upload
        # Format needs to be a list of tuples: [('files', (filename, file_stream)), ...]
        files_tuples = []
        file_streams = []
        progress_bars = []

        try:
            for file_path in files:
                file_size = os.stat(file_path.as_posix()).st_size

                # Create progress bar
                progress_bar = tqdm(
                    total=file_size,
                    unit="B",
                    unit_scale=True,
                    desc=f"Uploading file {file_path.name}",
                    disable=bool(DISABLE_TQDM),
                )
                progress_bars.append(progress_bar)

                # Open file and track for cleanup
                file_stream = file_path.open("rb")
                file_streams.append(file_stream)

                # Create wrapper for progress tracking
                reader_wrapper = CallbackIOWrapper(
                    progress_bar.update, file_stream, "read"
                )

                # Add to files list as a tuple
                files_tuples.append(("files", (file_path.name, reader_wrapper)))

            # Make the request
            response, _, _ = await requestor.arequest(
                options=SeekrFlowRequest(
                    method="PUT",
                    url=url,
                    files=files_tuples,  # Pass as a list of tuples (field_name, (filename, file_stream))
                    params={"purpose": purpose.value},
                    allow_redirects=redirect,
                ),
                stream=False,
            )

            assert isinstance(response, SeekrFlowResponse)

            # Parse the response
            if isinstance(response.data, list):
                file_responses = [
                    FileResponse(**file_data) for file_data in response.data
                ]
            else:
                # Handle case where response might be a single object
                file_responses = [FileResponse(**response.data)]

            return file_responses

        finally:
            # Clean up resources
            for file_stream in file_streams:
                file_stream.close()

            for progress_bar in progress_bars:
                progress_bar.close()
