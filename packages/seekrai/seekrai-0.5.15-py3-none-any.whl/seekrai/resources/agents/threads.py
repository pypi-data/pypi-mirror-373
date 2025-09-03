from typing import Any, Optional

from seekrai.abstract import api_requestor
from seekrai.seekrflow_response import SeekrFlowResponse
from seekrai.types import (
    MessageUpdateRequest,
    SeekrFlowRequest,
    Thread,
    ThreadCreateRequest,
    ThreadMessage,
    ThreadMessageContentType,
)


class AgentThreads:
    def __init__(self, client: Any) -> None:
        self._client = client
        self._requestor = api_requestor.APIRequestor(client=self._client)

    def create_message(
        self,
        thread_id: str,
        role: str,
        content: ThreadMessageContentType,
        **meta_data: Any,
    ) -> ThreadMessage:
        """Creates a new message within a Thread.

        Args:
            thread_id: Identifier for the Thread to append to.
            role: The name of the message writer.
            content: The contents of the newly written message.
            meta_data: Additional information attached to the new message.

        Returns:
            A ThreadMessage that matches the provided arguments.
        """
        payload = ThreadMessage(
            thread_id=thread_id,
            role=role,
            content=content,
            meta_data=meta_data,
        ).model_dump()

        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url=f"threads/{thread_id}/messages",
                params=payload,
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return ThreadMessage(**response.data)

    def retrieve_message(self, thread_id: str, message_id: str) -> ThreadMessage:
        """Retrieves a referenced ThreadMessage.

        Args:
            thread_id: Identifier for the Thread the message belongs to.
            message_id: Identifier for the ThreadMessage to retrieve.

        Returns:
            The ThreadMessage whose identity matches the arguments.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"threads/{thread_id}/messages/{message_id}",
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return ThreadMessage(**response.data)

    def list_messages(
        self, thread_id: str, limit: int = 20, order: str = "desc"
    ) -> list[ThreadMessage]:
        """Retrieves a list of messages from a referenced Thread.

        Args:
            thread_id: Identifier of the Thread.
            limit: The max number of ThreadMessages to retrieve.
            order: The order in which ThreadMessages are retrieved. Either 'desc' or 'asc'.

        Returns:
            A list of ThreadMessages, all from the Thread whose id matches thread_id.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"threads/{thread_id}/messages",
                params={"limit": limit, "order": order},
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return [ThreadMessage(**message) for message in response.data]  # type: ignore

    def update_message(
        self,
        thread_id: str,
        message_id: str,
        content: Optional[str] = None,
        **meta_data: Any,
    ) -> ThreadMessage:
        """Updates a ThreadMessage to have new attributes.

        Args:
            thread_id: Identifier of the Thread that contains the message to update.
            message_id: Identifier of the ThreadMessage to be updated.
            content: The new content of the message.
            meta_data: Any other attributes to be updated on the ThreadMessage.

        Returns:
            The referenced ThreadMessage, but with updated attributes.
        """
        payload = MessageUpdateRequest(
            content=content,
            meta_data=meta_data,
        ).model_dump()

        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="PATCH",
                url=f"threads/{thread_id}/messages/{message_id}",
                params=payload,
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return ThreadMessage(**response.data)

    def delete_message(self, thread_id: str, message_id: str) -> dict[str, Any]:
        """Deletes a referenced ThreadMessage.

        Args:
            thread_id: Identifier of the Thread from which a message should be deleted.
            message_id: Identifier of the ThreadMessage to delete.

        Returns:
            {"deleted": True} on success.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="DELETE",
                url=f"threads/{thread_id}/messages/{message_id}",
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return response.data

    def create(self, **meta_data: Any) -> Thread:
        """Creates a new Thread.

        Args:
            meta_data: Any special attributes to be attached to the new Thread.

        Returns:
            A newly created Thread with the specified attributes.
        """
        payload = ThreadCreateRequest(meta_data=meta_data).model_dump()

        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="POST",
                url="threads/",
                params=payload,
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return Thread(**response.data)

    def retrieve(self, thread_id: str) -> Thread:
        """Retrieves a referenced Thread.

        Args:
            thread_id: Identifier of the Thread to retrieve.

        Returns:
            A Thread whose id matches thread_id.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url=f"threads/{thread_id}",
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return Thread(**response.data)

    def list(self, limit: int = 20, order: str = "desc") -> list[Thread]:
        """Retrieve a list of Threads.

        Args:
            limit: The maximum number of Threads to retrieve.
            order: The order in which retrieved Threads are listed. Either 'desc' or 'asc'.

        Returns:
            A list of known Threads.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="GET",
                url="threads/",
                params={"limit": limit, "order": order},
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return [Thread(**thread) for thread in response.data]  # type: ignore

    def delete(self, thread_id: str) -> dict[str, Any]:
        """Deletes a Thread.

        Args:
            thread_id: Identifier of the Thread to be deleted.

        Returns:
            {"deleted": True} on success.
        """
        response, _, _ = self._requestor.request(
            options=SeekrFlowRequest(
                method="DELETE",
                url=f"threads/{thread_id}",
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return response.data


class AsyncAgentThreads:
    def __init__(self, client: Any) -> None:
        self._client = client
        self._requestor = api_requestor.APIRequestor(client=self._client)

    async def create_message(
        self,
        thread_id: str,
        role: str,
        content: ThreadMessageContentType,
        **meta_data: Any,
    ) -> ThreadMessage:
        """Creates a new message within a Thread.

        Args:
            thread_id: Identifier for the Thread to append to.
            role: The name of the message writer.
            content: The contents of the newly written message.
            meta_data: Additional information attached to the new message.

        Returns:
            A ThreadMessage that matches the provided arguments.
        """
        payload = ThreadMessage(
            thread_id=thread_id,
            role=role,
            content=content,
            meta_data=meta_data,
        ).model_dump()

        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url=f"threads/{thread_id}/messages",
                params=payload,
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return ThreadMessage(**response.data)

    async def retrieve_message(self, thread_id: str, message_id: str) -> ThreadMessage:
        """Retrieves a referenced ThreadMessage.

        Args:
            thread_id: Identifier for the Thread the message belongs to.
            message_id: Identifier for the ThreadMessage to retrieve.

        Returns:
            The ThreadMessage whose identity matches the arguments.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"threads/{thread_id}/messages/{message_id}",
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return ThreadMessage(**response.data)

    async def list_messages(
        self, thread_id: str, limit: int = 20, order: str = "desc"
    ) -> list[ThreadMessage]:
        """Retrieves a list of messages from a referenced Thread.

        Args:
            thread_id: Identifier of the Thread.
            limit: The max number of ThreadMessages to retrieve.
            order: The order in which ThreadMessages are retrieved. Either 'desc' or 'asc'.

        Returns:
            A list of ThreadMessages, all from the Thread whose id matches thread_id.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"threads/{thread_id}/messages",
                params={"limit": limit, "order": order},
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return [ThreadMessage(**message) for message in response.data]  # type: ignore

    async def update_message(
        self,
        thread_id: str,
        message_id: str,
        content: Optional[str] = None,
        **meta_data: Any,
    ) -> ThreadMessage:
        """Updates a ThreadMessage to have new attributes.

        Args:
            thread_id: Identifier of the Thread that contains the message to update.
            message_id: Identifier of the ThreadMessage to be updated.
            content: The new content of the message.
            meta_data: Any other attributes to be updated on the ThreadMessage.

        Returns:
            The referenced ThreadMessage, but with updated attributes.
        """
        payload = MessageUpdateRequest(
            content=content,
            meta_data=meta_data,
        ).model_dump()

        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="PATCH",
                url=f"threads/{thread_id}/messages/{message_id}",
                params=payload,
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return ThreadMessage(**response.data)

    async def delete_message(self, thread_id: str, message_id: str) -> dict[str, Any]:
        """Deletes a referenced ThreadMessage.

        Args:
            thread_id: Identifier of the Thread from which a message should be deleted.
            message_id: Identifier of the ThreadMessage to delete.

        Returns:
            {"deleted": True} on success.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="DELETE",
                url=f"threads/{thread_id}/messages/{message_id}",
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return response.data

    async def create(self, **meta_data: Any) -> Thread:
        """Creates a new Thread.

        Args:
            meta_data: Any special attributes to be attached to the new Thread.

        Returns:
            A newly created Thread with the specified attributes.
        """
        payload = ThreadCreateRequest(meta_data=meta_data).model_dump()

        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="POST",
                url="threads/",
                params=payload,
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return Thread(**response.data)

    async def retrieve(self, thread_id: str) -> Thread:
        """Retrieves a referenced Thread.

        Args:
            thread_id: Identifier of the Thread to retrieve.

        Returns:
            A Thread whose id matches thread_id.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url=f"threads/{thread_id}",
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return Thread(**response.data)

    async def list(self, limit: int = 20, order: str = "desc") -> list[Thread]:
        """Retrieve a list of Threads.

        Args:
            limit: The maximum number of Threads to retrieve.
            order: The order in which retrieved Threads are listed. Either 'desc' or 'asc'.

        Returns:
            A list of known Threads.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="GET",
                url="threads/",
                params={"limit": limit, "order": order},
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return [Thread(**thread) for thread in response.data]  # type: ignore

    async def delete(self, thread_id: str) -> dict[str, Any]:
        """Deletes a Thread.

        Args:
            thread_id: Identifier of the Thread to be deleted.

        Returns:
            {"deleted": True} on success.
        """
        response, _, _ = await self._requestor.arequest(
            options=SeekrFlowRequest(
                method="DELETE",
                url=f"threads/{thread_id}",
            )
        )

        assert isinstance(response, SeekrFlowResponse)
        return response.data
