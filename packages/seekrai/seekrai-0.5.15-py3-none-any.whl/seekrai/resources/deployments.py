from seekrai.abstract import api_requestor
from seekrai.resources.resource_base import ResourceBase
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import SeekrFlowRequest
from seekrai.types.deployments import Deployment as DeploymentSchema
from seekrai.types.deployments import GetDeploymentsResponse


class Deployments(ResourceBase):
    def list(self) -> GetDeploymentsResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/deployments",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return GetDeploymentsResponse(**response.data)

    def retrieve(self, deployment_id: str) -> DeploymentSchema:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/deployments/{deployment_id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return DeploymentSchema(**response.data)

    def create(
        self,
        name: str,
        description: str,
        model_type: str,
        model_id: str,
        n_instances: int,
    ) -> DeploymentSchema:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/deployments",
                params={
                    "name": name,
                    "description": description,
                    "model_type": model_type,
                    "model_id": model_id,
                    "n_instances": n_instances,
                },
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return DeploymentSchema(**response.data)

    def promote(self, deployment_id: str) -> DeploymentSchema:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/deployments/{deployment_id}/promote",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return DeploymentSchema(**response.data)

    def demote(self, deployment_id: str) -> DeploymentSchema:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/deployments/{deployment_id}/demote",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return DeploymentSchema(**response.data)


class AsyncDeployments(ResourceBase):
    async def list(self) -> GetDeploymentsResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/deployments",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return GetDeploymentsResponse(**response.data)

    async def retrieve(self, deployment_id: str) -> DeploymentSchema:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/deployments/{deployment_id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return DeploymentSchema(**response.data)

    async def create(
        self,
        name: str,
        description: str,
        model_type: str,
        model_id: str,
        n_instances: int,
    ) -> DeploymentSchema:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/deployments",
                params={
                    "name": name,
                    "description": description,
                    "model_type": model_type,
                    "model_id": model_id,
                    "n_instances": n_instances,
                },
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return DeploymentSchema(**response.data)

    async def promote(self, deployment_id: str) -> DeploymentSchema:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/deployments/{deployment_id}/promote",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return DeploymentSchema(**response.data)

    async def demote(self, deployment_id: str) -> DeploymentSchema:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/deployments/{deployment_id}/demote",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return DeploymentSchema(**response.data)
