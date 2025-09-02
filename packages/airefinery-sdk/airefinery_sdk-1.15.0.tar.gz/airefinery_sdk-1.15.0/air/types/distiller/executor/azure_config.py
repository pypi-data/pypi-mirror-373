"""Azure Agent Configuration Schema"""

from pydantic import Field, BaseModel, model_validator


class AzureAgentConfig(BaseModel):
    """
    Azure Agent Config
    """

    connection_string: str = Field(
        default="",
        description="The environment variable containing the Azure connection string.",
    )
    agent_id: str = Field(
        default="",
        description="The environment variable containing the Azure agent ID.",
    )

    @model_validator(mode="after")
    def check_connection_params_non_empty(self):
        """
        Checking if required connection parameters are populated in the config
        """
        connection_string = self.connection_string
        agent_id = self.agent_id

        if connection_string == "":
            raise ValueError(
                "Missing 'connection_string' in utility_config for AzureExecutor."
            )

        if agent_id == "":
            raise ValueError("Missing 'agent_id' in utility_config for AzureExecutor.")

        return self
