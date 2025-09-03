from typing import Any, AsyncGenerator, Iterator, Optional, Union

from seekrai.abstract import api_requestor
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import ModelSettings, Run, RunRequest, RunResponse, SeekrFlowRequest
from seekrai.types.agents.runs import ResponseFormat


class AgentInference:
    def __init__(self, client: Any) -> None:
        self._client = client
        self._requestor = api_requestor.APIRequestor(client=self._client)

    def run(
        self,
        agent_id: str,
        thread_id: str,
        *,
        stream: bool = False,
        model_settings: ModelSettings = ModelSettings(),
        response_format: Optional[Any] = None,
        group: Optional[str] = None,
    ) -> Union[RunResponse, Iterator[Any]]:
        """
        Run an inference call on a deployed agent.

        Args:
            agent_id (str): The unique identifier of the deployed agent.
            thread_id (str): A thread identifier.
            stream (bool, optional): Whether to stream the response. Defaults to False.
            model_settings (optional): Additional parameters (such as temperature, max_tokens, etc).
            response_format: Optional structured output specification. If provided, the LLM will be constrained to return JSON matching this schema.
            group (str, optional): Label used to associate a group of runs. Defaults to None.

        Returns:
            A dictionary with the response (if non-streaming) or an iterator over response chunks.
        """
        payload = RunRequest(
            agent_id=agent_id,
            model_settings=model_settings,
            response_format=ResponseFormat.from_value(response_format)
            if response_format
            else None,
            group=group,
        ).model_dump()
        endpoint = f"threads/{thread_id}/runs"
        if stream:
            endpoint += "/stream"

        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url=endpoint,
                params=payload,
            ),
            stream=stream,
        )

        if stream:
            assert not isinstance(response, SeekrFlowResponse)
            return (chunk.data for chunk in response)
        else:
            assert isinstance(response, SeekrFlowResponse)
            return RunResponse(**response.data)

    def cancel(self, agent_id: str, run_id: str, thread_id: str) -> dict[str, Any]:
        """Cancels a Run that is in progress.

        Args:
            agent_id: Identifier for the agent performing the run.
            run_id: Identifier for the run to be cancelled.
            thread_id: Identifier for the thread used by the run.

        Returns:
            {'status': 'canceled', 'run_id': run_id} on success.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url=f"threads/{thread_id}/runs/{run_id}/cancel",
                params=RunRequest(agent_id=agent_id).model_dump(),
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return response.data

    def attach(self, run_id: str, thread_id: str) -> Iterator[Any]:
        """Returns a stream of output from a Run.

        Args:
            run_id: Identifier for the Run.
            thread_id: Identifier for the Thread used by the Run.

        Returns:
            An Iterator of streamed output from the Run.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"threads/{thread_id}/runs/{run_id}/attach",
            ),
            stream=True,
        )

        assert not isinstance(response, SeekrFlowResponse)
        return (chunk.data for chunk in response)

    def retrieve(self, run_id: str, thread_id: str) -> Run:
        """Retrieves a Run.

        Args:
            run_id: Identifier for the Run.
            thread_id: Identifier for the Thread used by the Run.

        Returns:
            The Run whose id matches run_id.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"threads/{thread_id}/runs/{run_id}",
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return Run(**response.data)

    def list(self, thread_id: str) -> list[Run]:
        """Retrieves a list of Runs relevant to a referenced Thread.

        Args:
            thread_id: Identifier for a Thread.

        Returns:
            A list of Runs that have leveraged the referenced Thread.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"threads/{thread_id}/runs",
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return [Run(**run) for run in response.data]  # type: ignore


class AsyncAgentInference:
    def __init__(self, client: Any) -> None:
        self._client = client
        self._requestor = api_requestor.APIRequestor(client=self._client)

    async def run(
        self,
        agent_id: str,
        thread_id: str,
        *,
        stream: bool = False,
        model_settings: ModelSettings = ModelSettings(),
        response_format: Optional[Any] = None,
        group: Optional[str] = None,
    ) -> Union[RunResponse, AsyncGenerator[Any, None]]:
        """
        Run an inference call on a deployed agent.

        Args:
            agent_id (str): The unique identifier of the deployed agent.
            thread_id (str): A thread identifier.
            stream (bool, optional): Whether to stream the response. Defaults to False.
            model_settings (optional): Additional parameters (such as temperature, max_tokens, etc).
            response_format: Optional structured output specification. If provided, the LLM will be constrained to return JSON matching this schema.
            group (str, optional): Label used to associate a group of runs. Defaults to None.

        Returns:
            A dictionary with the response (if non-streaming) or an iterator over response chunks.
        """
        payload = RunRequest(
            agent_id=agent_id,
            model_settings=model_settings,
            response_format=ResponseFormat.from_value(response_format)
            if response_format
            else None,
            group=group,
        ).model_dump()
        endpoint = f"threads/{thread_id}/runs"
        if stream:
            endpoint += "/stream"

        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url=endpoint,
                params=payload,
            ),
            stream=stream,
        )

        if stream:
            assert not isinstance(response, SeekrFlowResponse)

            async def output() -> AsyncGenerator[Any, None]:
                async for chunk in response:
                    yield chunk.data

            return output()
        else:
            assert isinstance(response, SeekrFlowResponse)
            return RunResponse(**response.data)

    async def cancel(
        self, agent_id: str, run_id: str, thread_id: str
    ) -> dict[str, Any]:
        """Cancels a Run that is in progress.

        Args:
            agent_id: Identifier for the agent performing the run.
            run_id: Identifier for the run to be cancelled.
            thread_id: Identifier for the thread used by the run.

        Returns:
            {'status': 'canceled', 'run_id': run_id} on success.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url=f"threads/{thread_id}/runs/{run_id}/cancel",
                params=RunRequest(agent_id=agent_id).model_dump(),
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return response.data

    async def attach(self, run_id: str, thread_id: str) -> AsyncGenerator[Any, None]:
        """Returns a stream of output from a Run.

        Args:
            run_id: Identifier for the Run.
            thread_id: Identifier for the Thread used by the Run.

        Returns:
            An Iterator of streamed output from the Run.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"threads/{thread_id}/runs/{run_id}/attach",
            ),
            stream=True,
        )

        assert not isinstance(response, SeekrFlowResponse)

        async def output() -> AsyncGenerator[Any, None]:
            async for chunk in response:
                yield chunk.data

        return output()

    async def retrieve(self, run_id: str, thread_id: str) -> Run:
        """Retrieves a Run.

        Args:
            run_id: Identifier for the Run.
            thread_id: Identifier for the Thread used by the Run.

        Returns:
            The Run whose id matches run_id.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"threads/{thread_id}/runs/{run_id}",
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return Run(**response.data)

    async def list(self, thread_id: str) -> list[Run]:
        """Retrieves a list of Runs relevant to a referenced Thread.

        Args:
            thread_id: Identifier for a Thread.

        Returns:
            A list of Runs that have leveraged the referenced Thread.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"threads/{thread_id}/runs",
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return [Run(**run) for run in response.data]  # type: ignore
