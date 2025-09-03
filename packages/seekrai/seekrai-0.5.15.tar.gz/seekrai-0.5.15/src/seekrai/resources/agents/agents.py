from seekrai.abstract import api_requestor
from seekrai.resources.agents.agent_inference import AgentInference, AsyncAgentInference
from seekrai.resources.agents.python_functions import (
    AsyncCustomFunctions,
    CustomFunctions,
)
from seekrai.resources.agents.threads import AgentThreads, AsyncAgentThreads
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import SeekrFlowClient, SeekrFlowRequest
from seekrai.types.agents.agent import (
    Agent,
    AgentDeleteResponse,
    CreateAgentRequest,
    UpdateAgentRequest,
)


class Agents:
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client
        self._requestor = api_requestor.APIRequestor(
            client=self._client,
        )
        self.runs = AgentInference(client)
        self.threads = AgentThreads(client)
        self.custom_functions = CustomFunctions(client)

    def retrieve(self, agent_id: str) -> Agent:
        """
        Retrieve an agent by its ID.

        Args:
            agent_id: The ID of the Agent to retrieve.

        Returns: An agent.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/agents/{agent_id}",
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return Agent(**response.data)

    def create(self, request: CreateAgentRequest) -> Agent:
        """
        Create an agent based on a set of instructions and tooling.

        Args:
            request: The request object containing all the agent config (instructions, tooling, etc.)

        Returns:
            The newly created agent.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="POST", url="flow/agents/create", params=request.model_dump()
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return Agent(**response.data)

    def list_agents(self) -> list[Agent]:
        """
        Retrieve an entire list of agents for the user.

        Args:
            None.

        Returns: A list of agents.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/agents/",
            ),
        )
        assert isinstance(response, SeekrFlowResponse)

        agents = [Agent(**agent) for agent in response.data["data"]]

        return agents

    def promote(self, agent_id: str) -> Agent:
        """
        Re-deploy an existing agent.

        Args:
            agent_id: The ID of the existing agent to re-deploy

        Returns:
            The agent that was re-deployed.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/agents/{agent_id}/promote",
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return Agent(**response.data)

    def demote(self, agent_id: str) -> Agent:
        """
        Scale down an Agent deployment.

        Args:
            agent_id: The ID of the agent to demote.

        Returns:
            The agent whose corresponding deployment was scaled down.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/agents/{agent_id}/demote",
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return Agent(**response.data)

    def delete(self, agent_id: str) -> AgentDeleteResponse:
        """
        Demote an agent (if it's currently active/deployed) and subsequently delete the agent from the DB.

        DESTRUCTIVE OPERATION - cannot recover deleted agents.

        Args:
            agent_id: The ID of the agent to delete.

        Returns:
            A response indicating whether the delete operation was successful.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="DELETE",
                url=f"flow/agents/{agent_id}",
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return AgentDeleteResponse(**response.data)

    def update(self, agent_id: str, request: UpdateAgentRequest) -> Agent:
        """
        Update an existing agent's configuration.

        Args:
            agent_id: The ID of the agent to update.
            request: The request object containing updated agent config.

        Returns:
            The updated agent.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/agents/{agent_id}/update",
                params=request.model_dump(),
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return Agent(**response.data)


class AsyncAgents:
    def __init__(self, client: SeekrFlowClient) -> None:
        self._client = client
        self._requestor = api_requestor.APIRequestor(
            client=self._client,
        )
        self.runs = AsyncAgentInference(client)
        self.threads = AsyncAgentThreads(client)
        self.custom_functions = AsyncCustomFunctions(client)

    async def retrieve(self, agent_id: str) -> Agent:
        """
        Retrieve an agent by its ID.

        Args:
            agent_id: The ID of the Agent to retrieve.

        Returns: An agent.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"flow/agents/{agent_id}",
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return Agent(**response.data)

    async def create(self, request: CreateAgentRequest) -> Agent:
        """
        Create an agent based on a set of instructions and tooling.

        Args:
            request: The request object containing all the agent config (instructions, tooling, etc.)

        Returns:
            The newly created agent.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="POST", url="flow/agents/create", params=request.model_dump()
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return Agent(**response.data)

    async def list_agents(self) -> list[Agent]:
        """
        Retrieve an entire list of agents for the user.

        Args:
            None.

        Returns: A list of agents.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url="flow/agents/",
            ),
        )
        assert isinstance(response, SeekrFlowResponse)

        agents = [Agent(**agent) for agent in response.data["data"]]

        return agents

    async def promote(self, agent_id: str) -> Agent:
        """
        Re-deploy an existing agent.

        Args:
            agent_id: The ID of the existing agent to re-deploy

        Returns:
            The agent that was re-deployed.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/agents/{agent_id}/promote",
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return Agent(**response.data)

    async def demote(self, agent_id: str) -> Agent:
        """
        Scale down an Agent deployment.

        Args:
            agent_id: The ID of the agent to demote.

        Returns:
            The agent whose corresponding deployment was scaled down.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/agents/{agent_id}/demote",
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return Agent(**response.data)

    async def delete(self, agent_id: str) -> AgentDeleteResponse:
        """
        Demote an agent (if it's currently active/deployed) and subsequently delete the agent from the DB.

        DESTRUCTIVE OPERATION - cannot recover deleted agents.

        Args:
            agent_id: The ID of the agent to delete.

        Returns:
            A response indicating whether the delete operation was successful.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="DELETE",
                url=f"flow/agents/{agent_id}",
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return AgentDeleteResponse(**response.data)

    async def update(self, agent_id: str, request: UpdateAgentRequest) -> Agent:
        """
        Update an existing agent's configuration.

        Args:
            agent_id: The ID of the agent to update.
            request: The request object containing updated agent config.

        Returns:
            The updated agent.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="PUT",
                url=f"flow/agents/{agent_id}/update",
                params=request.model_dump(),
            ),
        )

        assert isinstance(response, SeekrFlowResponse)
        return Agent(**response.data)
