"""Databricks Agent Configuration Schema"""

from pydantic import Field, BaseModel, model_validator


class DatabricksAgentConfig(BaseModel):
    """
    Databricks Agent Config
    """

    client_id: str = Field(
        default="",
        description="The environment variable containing the Databricks Client ID.",
    )
    client_secret: str = Field(
        default="",
        description="The environment variable containing the Databricks Client Secret.",
    )
    host_url: str = Field(
        default="",
        description="The environment variable containing the Databricks account URL.",
    )
    genie_space_id: str = Field(
        default="",
        description="The environment variable containing the Databricks Genie Space ID.",
    )
    contexts: list = Field(
        default_factory=list, description="List of contexts provided to the agent."
    )

    @model_validator(mode="after")
    def check_connection_params_non_empty(self):
        """
        Checking if required connection parameters are populated in the config
        """
        client_id = self.client_id
        client_secret = self.client_secret
        host_url = self.host_url
        genie_space_id = self.genie_space_id

        if client_id == "":
            raise ValueError(
                "Missing 'client_id' in utility_config for DatabricksExecutor."
            )

        if client_secret == "":
            raise ValueError(
                "Missing 'client_secret' in utility_config for DatabricksExecutor."
            )

        if host_url == "":
            raise ValueError(
                "Missing 'host_url' in utility_config for DatabricksExecutor."
            )

        if genie_space_id == "":
            raise ValueError(
                "Missing 'genie_space_id' in utility_config for DatabricksExecutor."
            )

        return self
