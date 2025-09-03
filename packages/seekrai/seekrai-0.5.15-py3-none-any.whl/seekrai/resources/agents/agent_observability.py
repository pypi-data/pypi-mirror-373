from datetime import datetime
from typing import Any, Optional

from seekrai.abstract import api_requestor
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import SeekrFlowRequest
from seekrai.types.agents.observability import (
    ObservabilitySpansRequest,
    ObservabilitySpansResponse,
)


BASE_OBSERVABILITY_ENDPOINT = "observability/spans"


class AgentObservability:
    def __init__(self, client: Any):
        self._client = client
        self._requestor = api_requestor.APIRequestor(client=self._client)

    def query_spans(
        self,
        min_start_time: Optional[datetime] = None,
        max_start_time: Optional[datetime] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        group: Optional[str] = None,
        limit: int = 100,
        order: str = "desc",
        offset: int = 0,
    ) -> ObservabilitySpansResponse:
        """
        Retrieve spans for a given run or group of runs given a set of facets.
        """
        payload = ObservabilitySpansRequest(
            min_start_datetime=min_start_time,
            max_start_datetime=max_start_time,
            agent_id=agent_id,
            run_id=run_id,
            trace_id=trace_id,
            thread_id=thread_id,
            group=group,
            limit=limit,
            order=order,
            offset=offset,
        ).model_dump()

        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="POST", url=BASE_OBSERVABILITY_ENDPOINT, params=payload
            )
        )

        assert isinstance(response, SeekrFlowResponse)

        return ObservabilitySpansResponse(spans=response.data)

    def retrieve_span(self, span_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieve a specific span given a span_id.
        """
        endpoint = f"{BASE_OBSERVABILITY_ENDPOINT}/{span_id}"

        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(method="GET", url=endpoint)
        )

        assert isinstance(response, SeekrFlowResponse)

        return response.data


class AsyncAgentObservability:
    def __init__(self, client: Any) -> None:
        self._client = client
        self._requestor = api_requestor.APIRequestor(client=self._client)

    async def query_spans(
        self,
        min_start_time: Optional[datetime] = None,
        max_start_time: Optional[datetime] = None,
        agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        thread_id: Optional[str] = None,
        group: Optional[str] = None,
        limit: int = 100,
        order: str = "desc",
        offset: int = 0,
    ) -> ObservabilitySpansResponse:
        """
        Retrieve spans for a given run or group of runs given a set of facets.
        """
        payload = ObservabilitySpansRequest(
            min_start_datetime=min_start_time,
            max_start_datetime=max_start_time,
            agent_id=agent_id,
            run_id=run_id,
            trace_id=trace_id,
            thread_id=thread_id,
            group=group,
            limit=limit,
            order=order,
            offset=offset,
        ).model_dump()

        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="POST", url=BASE_OBSERVABILITY_ENDPOINT, params=payload
            )
        )

        assert isinstance(response, SeekrFlowResponse)

        return ObservabilitySpansResponse(spans=response.data)

    async def retrieve_span(self, span_id: str) -> Optional[dict[str, Any]]:
        """
        Retrieve a specific span given a span_id.
        """
        endpoint = f"{BASE_OBSERVABILITY_ENDPOINT}/{span_id}"

        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(method="GET", url=endpoint)
        )

        assert isinstance(response, SeekrFlowResponse)

        return response.data
