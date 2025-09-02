"""Amazon Bedrock Agent Configuration Schema"""

from pydantic import Field, BaseModel, model_validator


class AmazonBedrockAgentConfig(BaseModel):
    """
    AmazonBedrock Agent Config
    """

    client_key: str = Field(
        default="",
        description="The environment variable containing the AmazonBedrock Client key.",
    )
    client_secret: str = Field(
        default="",
        description="The environment variable containing the AmazonBedrock Client Secret.",
    )
    deployment_region: str = Field(
        default="",
        description="The deployment region of the AmazonBedrock account.",
    )
    agent_id: str = Field(
        default="",
        description="The AmazonBedrock agent ID.",
    )
    alias_id: str = Field(
        default="",
        description="The AmazonBedrock agent's alias ID.",
    )
    session_id: str = Field(
        default="",
        description="The session ID to identify a conversation with a certain agent.",
    )

    @model_validator(mode="after")
    def check_connection_params_non_empty(self):
        """
        Checking if required connection parameters are populated in the config
        """
        client_key = self.client_key
        client_secret = self.client_secret
        deployment_region = self.deployment_region
        agent_id = self.agent_id
        alias_id = self.alias_id

        if client_key == "":
            raise ValueError(
                "Missing 'client_key' in utility_config for AmazonBedrockExecutor."
            )

        if client_secret == "":
            raise ValueError(
                "Missing 'client_secret' in utility_config for AmazonBedrockExecutor."
            )

        if deployment_region == "":
            raise ValueError(
                "Missing 'deployment_region' in utility_config for AmazonBedrockExecutor."
            )

        if agent_id == "":
            raise ValueError(
                "Missing 'agent_id' in utility_config for AmazonBedrockExecutor."
            )

        if alias_id == "":
            raise ValueError(
                "Missing 'alias_id' in utility_config for AmazonBedrockExecutor."
            )

        return self
