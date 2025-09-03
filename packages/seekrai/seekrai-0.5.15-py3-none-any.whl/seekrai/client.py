from __future__ import annotations

import os
from typing import Dict

from seekrai import resources
from seekrai.constants import BASE_URL, MAX_RETRIES, TIMEOUT_SECS
from seekrai.error import AuthenticationError
from seekrai.types import SeekrFlowClient
from seekrai.utils import enforce_trailing_slash


class SeekrFlow:
    completions: resources.Completions
    chat: resources.Chat
    embeddings: resources.Embeddings
    files: resources.Files
    images: resources.Images
    models: resources.Models
    fine_tuning: resources.FineTuning
    alignment: resources.Alignment
    ingestion: resources.Ingestion
    projects: resources.Projects
    deployments: resources.Deployments
    vector_database: resources.VectorDatabase
    agents: resources.Agents
    observability: resources.AgentObservability

    # client options
    client: SeekrFlowClient

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        supplied_headers: Dict[str, str] | None = None,
    ) -> None:
        """Construct a new synchronous seekrai client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `SEEKR_API_KEY`
        - `base_url` from `SEEKR_BASE_URL`
        """

        # get api key
        if not api_key:
            api_key = os.environ.get("SEEKR_API_KEY")

        if not api_key:
            raise AuthenticationError(
                "The api_key client option must be set either by passing api_key to the client or by setting the "
                "SEEKR_API_KEY environment variable"
            )

        # get base url
        if not base_url:
            base_url = os.environ.get("SEEKR_BASE_URL")

        if not base_url:
            base_url = BASE_URL

        if timeout is None:
            timeout = TIMEOUT_SECS

        if max_retries is None:
            max_retries = MAX_RETRIES

        # SeekrFlowClient object
        self.client = SeekrFlowClient(
            api_key=api_key,
            base_url=enforce_trailing_slash(base_url),  # type: ignore
            timeout=timeout,
            max_retries=max_retries,
            supplied_headers=supplied_headers,
        )

        self.completions = resources.Completions(self.client)
        self.chat = resources.Chat(self.client)
        self.embeddings = resources.Embeddings(self.client)
        self.files = resources.Files(self.client)
        self.images = resources.Images(self.client)
        self.models = resources.Models(self.client)
        self.fine_tuning = resources.FineTuning(self.client)
        self.alignment = resources.Alignment(self.client)
        self.ingestion = resources.Ingestion(self.client)
        self.projects = resources.Projects(self.client)
        self.deployments = resources.Deployments(self.client)
        self.vector_database = resources.VectorDatabase(self.client)
        self.agents = resources.Agents(self.client)
        self.observability = resources.AgentObservability(self.client)


class AsyncSeekrFlow:
    completions: resources.AsyncCompletions
    chat: resources.AsyncChat
    embeddings: resources.AsyncEmbeddings
    files: resources.AsyncFiles
    images: resources.AsyncImages
    models: resources.AsyncModels
    fine_tuning: resources.AsyncFineTuning
    alignment: resources.AsyncAlignment
    ingestion: resources.AsyncIngestion
    projects: resources.AsyncProjects
    deployments: resources.AsyncDeployments
    vector_database: resources.AsyncVectorDatabase
    agents: resources.AsyncAgents
    observability: resources.AsyncAgentObservability

    # client options
    client: SeekrFlowClient

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        supplied_headers: Dict[str, str] | None = None,
    ) -> None:
        """Construct a new async seekrai client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `SEEKR_API_KEY`
        - `base_url` from `SEEKR_BASE_URL`
        """

        # get api key
        if not api_key:
            api_key = os.environ.get("SEEKR_API_KEY")

        if not api_key:
            raise AuthenticationError(
                "The api_key client option must be set either by passing api_key to the client or by setting the "
                "SEEKR_API_KEY environment variable"
            )

        # get base url
        if not base_url:
            base_url = os.environ.get("SEEKR_BASE_URL")

        if not base_url:
            base_url = BASE_URL

        if timeout is None:
            timeout = TIMEOUT_SECS

        if max_retries is None:
            max_retries = MAX_RETRIES

        # SeekrFlowClient object
        self.client = SeekrFlowClient(
            api_key=api_key,
            base_url=enforce_trailing_slash(base_url),  # type: ignore
            timeout=timeout,
            max_retries=max_retries,
            supplied_headers=supplied_headers,
        )

        self.completions = resources.AsyncCompletions(self.client)
        self.chat = resources.AsyncChat(self.client)
        self.embeddings = resources.AsyncEmbeddings(self.client)
        self.files = resources.AsyncFiles(self.client)
        self.images = resources.AsyncImages(self.client)
        self.models = resources.AsyncModels(self.client)
        self.fine_tuning = resources.AsyncFineTuning(self.client)
        self.alignment = resources.AsyncAlignment(self.client)
        self.ingestion = resources.AsyncIngestion(self.client)
        self.projects = resources.AsyncProjects(self.client)
        self.deployments = resources.AsyncDeployments(self.client)
        self.vector_database = resources.AsyncVectorDatabase(self.client)
        self.agents = resources.AsyncAgents(self.client)
        self.observability = resources.AsyncAgentObservability(self.client)


Client = SeekrFlow

AsyncClient = AsyncSeekrFlow
