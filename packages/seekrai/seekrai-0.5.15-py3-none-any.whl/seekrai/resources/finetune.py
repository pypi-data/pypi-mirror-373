from __future__ import annotations

from pathlib import Path

from seekrai.abstract import api_requestor
from seekrai.resources.resource_base import ResourceBase
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import (
    FinetuneDownloadResult,
    FinetuneList,
    FinetuneListEvents,
    FinetuneRequest,
    FinetuneResponse,
    InfrastructureConfig,
    SeekrFlowRequest,
    TrainingConfig,
)


class FineTuning(ResourceBase):
    def create(
        self,
        *,
        project_id: int,
        training_config: TrainingConfig,
        infrastructure_config: InfrastructureConfig,
        # wandb_api_key: str | None = None,
    ) -> FinetuneResponse:
        """
        Method to initiate a fine-tuning job

        Args:

        Returns:
            FinetuneResponse: Object containing information about fine-tuning job.
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = FinetuneRequest(
            project_id=project_id,
            training_config=training_config,
            infrastructure_config=infrastructure_config,
        ).model_dump()

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/fine-tune",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FinetuneResponse(**response.data)

    def list(self) -> FinetuneList:
        """
        Lists fine-tune job history

        Returns:
            FinetuneList: Object containing a list of fine-tune jobs
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/fine-tunes",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FinetuneList(**response.data)

    def retrieve(self, id: str) -> FinetuneResponse:
        """
        Retrieves fine-tune job details

        Args:
            id (str): Fine-tune ID to retrieve. A string that starts with `ft-`.

        Returns:
            FinetuneResponse: Object containing information about fine-tuning job.
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/fine-tunes/{id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FinetuneResponse(**response.data)

    def cancel(self, id: str) -> FinetuneResponse:
        """
        Method to cancel a running fine-tuning job

        Args:
            id (str): Fine-tune ID to cancel. A string that starts with `ft-`.

        Returns:
            FinetuneResponse: Object containing information about cancelled fine-tuning job.
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/fine-tunes/{id}/cancel",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FinetuneResponse(**response.data)

    def list_events(self, id: str) -> FinetuneListEvents:
        """
        Lists events of a fine-tune job

        Args:
            id (str): Fine-tune ID to list events for. A string that starts with `ft-`.

        Returns:
            FinetuneListEvents: Object containing list of fine-tune events
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/fine-tunes/{id}/events",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FinetuneListEvents(**response.data)

    def download(
        self, id: str, *, output: Path | str | None = None, checkpoint_step: int = -1
    ) -> FinetuneDownloadResult:
        """
        Downloads compressed fine-tuned model or checkpoint to local disk.

        Defaults file location to `$PWD/{model_name}.{extension}`

        Args:
            id (str): Fine-tune ID to download. A string that starts with `ft-`.
            output (pathlib.Path | str, optional): Specifies output file name for downloaded model.
                Defaults to None.
            checkpoint_step (int, optional): Specifies step number for checkpoint to download.
                Defaults to -1 (download the final model)

        Returns:
            FinetuneDownloadResult: Object containing downloaded model metadata
        """
        raise NotImplementedError("Function not yet implemented")
        # url = f"finetune/download?ft_id={id}"
        #
        # if checkpoint_step > 0:
        #     url += f"&checkpoint_step={checkpoint_step}"
        #
        # remote_name = self.retrieve(id).output_name
        #
        # download_manager = DownloadManager(self._client)
        #
        # if isinstance(output, str):
        #     output = Path(output)
        #
        # downloaded_filename, file_size = download_manager.download(
        #     url, output, normalize_key(remote_name or id), fetch_metadata=True
        # )
        #
        # return FinetuneDownloadResult(
        #     object="local",
        #     id=id,
        #     checkpoint_step=checkpoint_step,
        #     filename=downloaded_filename,
        #     size=file_size,
        # )

    def promote(self, id: str) -> FinetuneListEvents:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/fine-tunes/{id}/promote-model",
                params={"fine_tune_id": id},
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FinetuneListEvents(**response.data)

    def demote(self, id: str) -> FinetuneListEvents:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/fine-tunes/{id}/demote-model",
                params={"fine_tune_id": id},
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FinetuneListEvents(**response.data)


class AsyncFineTuning(ResourceBase):
    async def create(
        self,
        *,
        project_id: int,
        training_config: TrainingConfig,
        infrastructure_config: InfrastructureConfig,
    ) -> FinetuneResponse:
        """
        Async method to initiate a fine-tuning job

        Args:
        Returns:
            FinetuneResponse: Object containing information about fine-tuning job.
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = FinetuneRequest(
            project_id=project_id,
            training_config=training_config,
            infrastructure_config=infrastructure_config,
        ).model_dump()

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/fine-tunes",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FinetuneResponse(**response.data)

    async def list(self) -> FinetuneList:
        """
        Async method to list fine-tune job history

        Returns:
            FinetuneList: Object containing a list of fine-tune jobs
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/fine-tunes",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FinetuneList(**response.data)

    async def retrieve(self, id: str) -> FinetuneResponse:
        """
        Async method to retrieve fine-tune job details

        Args:
            id (str): Fine-tune ID to retrieve. A string that starts with `ft-`.

        Returns:
            FinetuneResponse: Object containing information about fine-tuning job.
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/fine-tunes/{id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FinetuneResponse(**response.data)

    async def cancel(self, id: str) -> FinetuneResponse:
        """
        Async method to cancel a running fine-tuning job

        Args:
            id (str): Fine-tune ID to cancel. A string that starts with `ft-`.

        Returns:
            FinetuneResponse: Object containing information about cancelled fine-tuning job.
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url=f"flow/fine-tunes/{id}/cancel",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FinetuneResponse(**response.data)

    async def list_events(self, id: str) -> FinetuneListEvents:
        """
        Async method to lists events of a fine-tune job

        Args:
            id (str): Fine-tune ID to list events for. A string that starts with `ft-`.

        Returns:
            FinetuneListEvents: Object containing list of fine-tune events
        """

        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/fine-tunes/{id}/events",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)

        return FinetuneListEvents(**response.data)

    async def download(
        self, id: str, *, output: str | None = None, checkpoint_step: int = -1
    ) -> str:
        """
        TODO: Implement async download method
        """

        raise NotImplementedError(
            "AsyncFineTuning.download not implemented. "
            "Please use FineTuning.download function instead."
        )
