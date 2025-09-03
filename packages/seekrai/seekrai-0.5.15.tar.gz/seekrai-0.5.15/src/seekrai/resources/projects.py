from seekrai.abstract import api_requestor
from seekrai.resources.resource_base import ResourceBase
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import SeekrFlowRequest
from seekrai.types.projects import (
    GetProjectsResponse,
    PostProjectRequest,
)
from seekrai.types.projects import (
    Project as ProjectSchema,
)


class Projects(ResourceBase):
    def list(self, skip: int = 0, limit: int = 100) -> GetProjectsResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/projects",
                params={"skip": skip, "limit": limit},
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return GetProjectsResponse(**response.data)

    def retrieve(self, project_id: int) -> ProjectSchema:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/projects/{project_id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return ProjectSchema(**response.data)

    def create(self, name: str, description: str) -> ProjectSchema:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = PostProjectRequest(
            name=name,
            description=description,
        ).model_dump()

        response, _, _ = requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/projects",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return ProjectSchema(**response.data)


class AsyncProjects(ResourceBase):
    async def list(self, skip: int = 0, limit: int = 100) -> GetProjectsResponse:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/projects",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return GetProjectsResponse(**response.data)

    async def retrieve(self, project_id: int) -> ProjectSchema:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/projects/{project_id}",
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return ProjectSchema(**response.data)

    async def create(self, name: str, description: str) -> ProjectSchema:
        requestor = api_requestor.APIRequestor(
            client=self._client,
        )

        parameter_payload = PostProjectRequest(
            name=name,
            description=description,
        ).model_dump()

        response, _, _ = await requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="flow/projects",
                params=parameter_payload,
            ),
            stream=False,
        )

        assert isinstance(response, SeekrFlowResponse)
        return ProjectSchema(**response.data)
