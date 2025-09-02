"""Salesforce Agent Configuration Schema"""

from pydantic import Field, BaseModel, model_validator


class SalesforceAgentConfig(BaseModel):
    """
    Salesforce Agent Config
    """

    client_key: str = Field(
        default="",
        description="The environment variable containing the Salesforce Client key.",
    )
    client_secret: str = Field(
        default="",
        description="The environment variable containing the Salesforce Client Secret.",
    )
    domain: str = Field(
        default="",
        description="The orgfarm domain URL of the Salesforce account.",
    )
    agent_id: str = Field(
        default="",
        description="The Salesforce agent ID.",
    )

    @model_validator(mode="after")
    def check_connection_params_non_empty(self):
        """
        Checking if required connection parameters are populated in the config
        """
        client_key = self.client_key
        client_secret = self.client_secret
        domain = self.domain
        agent_id = self.agent_id

        if client_key == "":
            raise ValueError(
                "Missing 'client_key' in utility_config for SalesforceExecutor."
            )

        if client_secret == "":
            raise ValueError(
                "Missing 'client_secret' in utility_config for SalesforceExecutor."
            )

        if domain == "":
            raise ValueError(
                "Missing 'domain' in utility_config for SalesforceExecutor."
            )

        if agent_id == "":
            raise ValueError(
                "Missing 'agent_id' in utility_config for SalesforceExecutor."
            )

        return self
