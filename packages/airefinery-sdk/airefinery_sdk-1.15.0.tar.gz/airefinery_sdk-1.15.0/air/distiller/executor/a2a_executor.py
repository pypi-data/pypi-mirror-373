"""Module containing the A2AExecutor for the integration of agents exposed over A2A."""

# pylint: disable=no-member

import asyncio
import logging
from uuid import uuid4
from typing import Any, Callable, Dict
import httpx

from air.distiller.executor.executor import Executor
from air.types.distiller.executor.a2a_config import A2AClientAgentConfig

logger = logging.getLogger(__name__)

try:
    from a2a.client import A2ACardResolver, A2AClient
    from a2a.types import (
        AgentCard,
        MessageSendParams,
        SendMessageRequest,
        SendStreamingMessageRequest,
    )

except ImportError as exc:
    logger.error(
        "[Installation Failed] Missing A2A SDK dependencies. "
        "Install with: pip install '.[tah-a2a]'"
    )
    raise


class A2AExecutor(Executor):
    """
    Executor class for the A2A Client Agent.
    """

    agent_class: str = "A2AClientAgent"

    def __init__(
        self,
        func: Dict[str, Callable],
        send_queue: asyncio.Queue,
        account: str,
        project: str,
        uuid: str,
        role: str,
        utility_config: Dict[str, Any],
        return_string: bool = True,
    ):
        """
        Initializes the A2AExecutor.
        """
        logger.debug(
            "Initializing A2AExecutor with role=%r, account=%r, project=%r, uuid=%r",
            role,
            account,
            project,
            uuid,
        )

        # Casting utility config to class-specific pydantic BaseModel
        a2a_agent_config = A2AClientAgentConfig(**utility_config)

        # Retrieve config fields
        self._base_url = a2a_agent_config.base_url

        agent_card = a2a_agent_config.agent_card
        self._public_agent_card_path = (
            a2a_agent_config.agent_card.public.public_agent_card_path
        )
        self._rpc_url = a2a_agent_config.agent_card.public.rpc_url

        # Retrieve optional extended agent card details if they have been configgured
        if agent_card.private:
            self._extended_agent_card_path = agent_card.private.extended_agent_card_path
            self._authentication_token = agent_card.private.authentication_token

        # Retrieve repsonse preferences
        response_prefs = a2a_agent_config.response_prefs
        self._response_tracing = response_prefs.tracing
        self._response_streaming = response_prefs.streaming

        # Initialize long-lived attributes: httpx_client, AgentCard, A2AClient
        # Will populate with async methods later
        self._httpx_client: httpx.AsyncClient | None = None

        self._final_agent_card: AgentCard | None = None
        self._client: A2AClient | None = None

        # Initialize the base Executor with our specialized execution method.
        super().__init__(
            func=self._execute_agent,
            send_queue=send_queue,
            account=account,
            project=project,
            uuid=uuid,
            role=role,
            return_string=return_string,
        )

    async def _get_httpx_client(self) -> httpx.AsyncClient:
        """
        Ensures a single httpx.AsyncClient instance is created and reused.
        We require a long-lived httpx client to support multi-turn conversations.
        If a client is not initialized, a new one is returned.
        Otherwise the running client is returned.

        Returns : self._httpx_client
        """
        if self._httpx_client is None:
            self._httpx_client = httpx.AsyncClient()
        return self._httpx_client

    async def _close_httpx_client(self):
        """
        Closes the httpx.AsyncClient explicitly.
        We need to ensure that the client is closed explicitly after the agent execution.
        If not closed explicitly and cleaned up, the async cycle of the agent conflicts
        with the base executor's event loop.
        """
        if self._httpx_client is not None and not self._httpx_client.is_closed:
            await self._httpx_client.aclose()
            self._httpx_client = None
            self._client = None
            logger.info("httpx.AsyncClient explicitly closed.")

    async def aclose(self):
        """
        Asynchronously closes the A2AExecutor, including the underlying httpx client.
        """
        logger.debug("Closing A2AExecutor...")
        await self._close_httpx_client()
        logger.debug("A2AExecutor closed.")

    async def collect_agent_card(self) -> AgentCard:
        """
        Retrieves the A2A AgentCard.
        Uses the httpx client to instantiate an Agent Card Resolver (ACR).
        Then uses the ACR to sequentially attempt to:
            - collect the public agent card (required)
            - use the self._authentication_token to collect the private
              agent card from self._extended_agent_card_path (optional)

        Returns: final_agent_card_to_use (fetched public or extended agent card)
        Raises:
            - RuntimeError : When failing to fetch a public agent card.
            - RuntimeError : When no agent card was fetched.
        """
        # Use the persistent client
        httpx_client = await self._get_httpx_client()

        # Initialize A2ACardResolver with the persistent client
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=self._base_url,
        )

        # Fetch Public Agent Card and Initialize Client
        final_agent_card_to_use: AgentCard | None = None

        try:
            logger.info(
                f"Attempting to fetch public agent card from: {self._base_url}{self._public_agent_card_path}"
            )
            _public_card = (
                await resolver.get_agent_card()
            )  # Fetches from default public path
            logger.info("Successfully fetched public agent card:")
            logger.info(_public_card.model_dump_json(indent=2, exclude_none=True))
            final_agent_card_to_use = _public_card
            logger.info(
                "\nUsing PUBLIC agent card for client initialization (default)."
            )

            if _public_card.supportsAuthenticatedExtendedCard:
                try:
                    logger.info(
                        "\nPublic card supports authenticated extended card. "
                        "Attempting to fetch from: "
                        f"{self._base_url}{self._extended_agent_card_path}"
                    )
                    auth_headers_dict = {
                        "Authorization": f"Bearer {self._authentication_token}"
                    }
                    _extended_card = await resolver.get_agent_card(
                        relative_card_path=self._extended_agent_card_path,
                        http_kwargs={"headers": auth_headers_dict},
                    )
                    logger.info(
                        "Successfully fetched authenticated extended agent card:"
                    )
                    logger.info(
                        _extended_card.model_dump_json(indent=2, exclude_none=True)
                    )
                    final_agent_card_to_use = (
                        _extended_card  # Update to use the extended card
                    )
                    logger.info(
                        "\nUsing AUTHENTICATED EXTENDED agent card for client "
                        "initialization."
                    )
                except Exception as e_extended:
                    logger.warning(
                        "Failed to fetch extended agent card: %s."
                        " Will proceed with public card.",
                        e_extended,
                        exc_info=True,
                    )
            elif _public_card:  # supportsAuthenticatedExtendedCard is False or None
                logger.info(
                    "\nPublic card does not indicate support "
                    "for an extended card. Using public card."
                )

        except Exception as e:
            logger.error(
                "Critical error fetching public agent card: %s", e, exc_info=True
            )
            raise RuntimeError(
                "Failed to fetch the public agent card. Cannot continue."
            ) from e

        if final_agent_card_to_use is None:
            raise RuntimeError("No agent card was successfully retrieved.")
        return final_agent_card_to_use

    async def initialize_A2A_client(self):
        """
        Initialize an A2A client for the agent.

        We require a long-lived client for multi-turn conversations, so the method
        initializes a new client only if one hasn't been initialized yet.

        The A2A client is initialized using either the fetched agent card (public
        or private), or the agent's self._rpc_url

        """
        if self._client is None:
            # Exlusive logic for initializing client: either agent card or rpc_url
            # Prioritize agent card. If not present, try rpc_url
            if self._final_agent_card is None and self._rpc_url == "":
                self._final_agent_card = await self.collect_agent_card()
                self._client = A2AClient(
                    httpx_client=await self._get_httpx_client(),
                    agent_card=self._final_agent_card,
                )
                logger.info("A2AClient initialized with agent card.")
            elif self._final_agent_card is None and self._rpc_url != "":
                self._client = A2AClient(
                    httpx_client=await self._get_httpx_client(),
                    url=self._rpc_url,
                )
                logger.info("A2AClient initialized with rpc url.")
        else:
            logger.debug("A2AClient already initialized. Reusing existing client.")

    async def send_message(self, prompt):
        """
        Post message to the agent over A2A and poll response

        The method assembles the message payload and wraps it in a SendMessageRequest.
        It then uses the A2A client to send the message to the server.

        Then, it awaits for the server's response.
        Depending on the response preferences
        (a2a_agent_config.response_prefs -> self._response_tracing),
        the method attempts to:
            - either extract only the final answer of the agent
              (self._response_tracing = False)
            - also extract intermediate messages of the agent and then the final
              response (self._response_tracing = True)

        Returns: text_response (extracted text from the agent's response)
        Raises:
            - Exception : When failing to post message to A2A agent
            - Exception : When failing to extract content from agent's response
        """
        # Ensure the client is initialized before sending a message
        await self.initialize_A2A_client()

        if self._client is None:
            raise RuntimeError("A2A client was not initialized successfully.")

        send_message_payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": prompt}],
                "messageId": uuid4().hex,
            },
        }
        request = SendMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )
        try:
            response = await self._client.send_message(request)

        except Exception:
            logger.exception("Failed to post message to A2A agent.")
            raise

        text_response = ""
        try:
            if not self._response_tracing:
                versioned_response = response.model_dump(
                    mode="json", exclude_none=True
                )["result"]
                if (
                    "artifacts" in versioned_response
                ):  # Older structure of the response dict
                    text_response = response.model_dump(mode="json", exclude_none=True)[
                        "result"
                    ]["artifacts"][0]["parts"][0]["text"]
                else:  # Newer structure of the response dict
                    text_response = response.model_dump(mode="json", exclude_none=True)[
                        "result"
                    ]["parts"][0]["text"]

            else:
                response = response.model_dump(mode="json", exclude_none=True)
                # Collect intermediate message traces
                agent_trace_texts = []
                if "history" in response["result"] and isinstance(
                    response["result"]["history"], list
                ):
                    # Collect all intermediate response traces
                    for message_entry in response["result"]["history"]:
                        # Check if the message is from the 'agent' role
                        if message_entry.get("role") == "agent":
                            # Check if 'parts' exist and contain text
                            if (
                                "parts" in message_entry
                                and isinstance(message_entry["parts"], list)
                                and len(message_entry["parts"]) > 0
                                and "text" in message_entry["parts"][0]
                            ):
                                agent_trace_texts.append(
                                    message_entry["parts"][0]["text"]
                                )
                    # Add the final response
                    agent_trace_texts.append(
                        response["result"]["artifacts"][0]["parts"][0]["text"]
                    )
                    text_response = f"{'\n'.join(agent_trace_texts)}"
        except Exception:
            logger.exception("Failed to retrieve messages from A2A agent.")
            raise

        return text_response

    async def send_streaming_message(self, prompt):
        """
        Post streaming request to the agent over A2A and poll response

        The method assembles the message payload and wraps it in a SendStreamingMessageRequest.
        It then uses the A2A client to send a streaming request to the server.

        Then, it awaits for the server's response and attempts to extract the chunks
        from the agent's response. It prints intermediate responses and returns the final response

        Returns: final_response (extracted final answer)
        Raises:
            - Exception : When failing to post streaming request to A2A agent
            - Exception : When failing to extract retrieve streaming chunks from A2A agent
        """
        # Ensure the client is initialized before sending a message
        await self.initialize_A2A_client()

        if self._client is None:
            raise RuntimeError("A2A client was not initialized successfully.")

        send_message_payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": prompt}],
                "messageId": uuid4().hex,
            },
        }

        streaming_request = SendStreamingMessageRequest(
            id=str(uuid4()), params=MessageSendParams(**send_message_payload)
        )

        try:
            stream_response = self._client.send_message_streaming(streaming_request)
        except Exception:
            logger.exception("Failed to post streaming request to A2A agent.")
            raise

        final_response = ""

        try:
            async for chunk in stream_response:
                chunk_json = chunk.model_dump(mode="json", exclude_none=True)
                # Print streaming chunks
                if (
                    chunk_json["result"]["kind"] == "status-update"
                    and not chunk_json["result"]["final"]
                ):
                    # Identify intermediate messages with content
                    interm_response = chunk_json["result"]["status"]["message"][
                        "parts"
                    ][0]["text"]
                    print(interm_response)
                elif chunk_json["result"]["kind"] == "artifact-update":
                    # Identify final message with content
                    final_response = chunk_json["result"]["artifact"]["parts"][0][
                        "text"
                    ]
                elif (
                    chunk_json["result"]["kind"] == "status-update"
                    and chunk_json["result"]["final"]
                ):
                    # Identify end-of-message signal
                    pass

        except Exception:
            logger.exception("Failed to retrieve streaming chunks from A2A agent.")
            raise

        return final_response

    async def _execute_agent(self, **kwargs) -> str:
        """
        Executes the A2A Client agent using a prompt.
        """
        prompt = kwargs.get("prompt")
        if not prompt:
            raise ValueError(
                "Missing 'prompt' parameter in A2AExecutor._execute_agent."
            )

        logger.debug("Running A2A Client agent with prompt=%r", prompt)
        # Execute the asynchronous agent run in a synchronous context.
        return await self._process_agent_request(prompt)

    async def _process_agent_request(self, prompt: str) -> str:
        """Processes the agent request asynchronously."""

        if not self._response_streaming:
            response = await self.send_message(prompt)
        else:
            response = await self.send_streaming_message(prompt)

        await self.aclose()

        return response
