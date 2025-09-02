# pylint: disable=redefined-outer-name
"""Module containing the DatabricksExecutor for Databricks Genie integration."""

import asyncio
import logging
from typing import Any, Callable, Dict
import os
import json

from databricks.sdk import WorkspaceClient

from air.distiller.executor.executor import Executor
from air.types.distiller.executor.databricks_config import DatabricksAgentConfig

logger = logging.getLogger(__name__)


class DatabricksSessionManager:
    """
    Manages the Databricks agent session.
    """

    def __init__(
        self,
        client_id_env_var,
        client_secret_env_var,
        host_url_env_var,
        genie_space_id_env_var,
    ):
        """
        Initializes the DatabricksSessionManager.

        Args:
            genie_space_id: The Databricks Genie space ID.
        """
        self._client_id = os.getenv(client_id_env_var, "")

        self._client_secret = os.getenv(client_secret_env_var, "")

        self._host_url = os.getenv(host_url_env_var, "")

        self._genie_space_id = os.getenv(genie_space_id_env_var, "")

        self._conversation_id = None

    def get_workspace_client(self):
        """
        Initialize Databricks Workspace client
        """
        self.client = WorkspaceClient(
            host=self._host_url,
            client_id=self._client_id,
            client_secret=self._client_secret,
        )

    def run_query_attachments(self, response):
        query_result = self.client.genie.get_message_attachment_query_result(
            self._genie_space_id,
            response.conversation_id,
            response.id,
            response.attachments[0].attachment_id,
        )
        sr = query_result.statement_response
        if not sr or not sr.result or not sr.result.data_array:
            raise ValueError("statement_response or its nested attributes are None")
        return sr.result.data_array

    def start_genie_conversation(self, workspace_client, space_id, message):
        """
        Initiate new conversation with Genie agent
        """
        response = workspace_client.genie.start_conversation_and_wait(
            space_id=space_id,
            content=message,
        )
        return response

    def continue_genie_conversation(
        self, workspace_client, space_id, conversation_id, prompt
    ):
        """
        Continue previous conversation with Genie agent
        """
        response = workspace_client.genie.create_message_and_wait(
            space_id, conversation_id, prompt
        )
        return response

    def send_message(self, prompt):
        """
        Send message to Genie agent.
        If no conversation is active, initiate new one, otherwise post to existing.
        If the initial Genie response contains a SQL query, run it and return the results.

        Returns:
            - response (GenieMessage): struct with the raw genie response
            - sql_df (list of lists): dataframe with the result of running the
                                      SQL query attached in the original response struct
        """
        # If there is no active conversation
        if not self._conversation_id:
            # initiate new one.
            response = self.start_genie_conversation(
                self.client, self._genie_space_id, prompt
            )
            # Record the conversation_id to continue it if needed
            self._conversation_id = response.conversation_id
        else:
            # continue the existing conversation
            response = self.continue_genie_conversation(
                self.client, self._genie_space_id, self._conversation_id, prompt
            )

        # If genie response has a SQL query attachment
        sql_df = []
        if not response.attachments:
            raise ValueError("response has no attachments")
        if response.attachments[0].query:
            # run it and return the results
            sql_df = self.run_query_attachments(response)

        return response, sql_df


class DatabricksExecutor(Executor):
    """
    Executor class for Databricks Agent.
    """

    agent_class: str = "DatabricksAgent"

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
        Initializes the DatabricksExecutor.
        """
        logger.debug(
            "Initializing DatabricksExecutor with role=%r, account=%r, project=%r, uuid=%r",
            role,
            account,
            project,
            uuid,
        )

        db_agent_config = DatabricksAgentConfig(**utility_config)

        # Retrieve required fields from utility_config.
        self._client_id_env_var = db_agent_config.client_id
        self._client_secret_env_var = db_agent_config.client_secret
        self._host_url_env_var = db_agent_config.host_url
        self._genie_space_id_env_var = db_agent_config.genie_space_id

        try:
            # Initialize session manager
            self.session_manager = DatabricksSessionManager(
                self._client_id_env_var,
                self._client_secret_env_var,
                self._host_url_env_var,
                self._genie_space_id_env_var,
            )
            logger.info("Successfully initialized Databricks Session manager.")
        except Exception as e:
            logger.exception(
                "Failed to initialize Databricks Session manager: %s", str(e)
            )
            raise RuntimeError(f"Databricks initialization failed: {str(e)}") from e

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

    def _execute_agent(self, **kwargs) -> str:
        """
        Executes the Databricks agent using a prompt.
        """
        prompt = kwargs.get("prompt")
        if not prompt:
            raise ValueError(
                "Missing 'prompt' parameter in DatabricksExecutor._execute_agent."
            )

        logger.debug("Running Databricks agent with prompt=%r", prompt)
        # Execute the asynchronous agent run in a synchronous context.
        return asyncio.run(self._process_agent_request(prompt))

    async def _process_agent_request(self, prompt: str) -> str:
        """Processes the agent request asynchronously."""
        try:
            # Create a new Databricks Workspace Client.
            self.session_manager.get_workspace_client()
            logger.info("Successfully created new Databricks Workspace Client.")
        except Exception:
            logger.exception("Failed to create new Databricks Workspace Client.")
            raise

        try:
            # Post the user prompt as a message within the conversation session.
            response, sql_result_df = self.session_manager.send_message(prompt)
            logger.info("Succesfully posted message to Databricks agent.")
        except Exception:
            logger.exception("Failed to post message for Databricks agent.")
            raise

        try:
            # Retrieve agent response
            if len(sql_result_df) == 0:
                # If the agent response is a text message then return it as the response
                if (
                    response.attachments
                    and response.attachments[0].text
                    and response.attachments[0].text.content
                ):
                    message = response.attachments[0].text.content
                else:
                    raise ValueError(
                        "response attachments or their nested attributes are None"
                    )
            else:
                # If the agent response is a dataframe resulting from a SQL query execution,
                # return it a as joined string
                message = json.dumps([list(row) for row in sql_result_df], indent=2)
        except Exception:
            logger.exception("Failed to retrieve response from Databricks agent.")
            raise

        return message
