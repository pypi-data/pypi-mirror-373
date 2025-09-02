"""Google Vertex Agent Configuration Schema"""

from pydantic import Field, BaseModel, model_validator


class GoogleAgentConfig(BaseModel):
    """
    Google Vertex Agent Config
    """

    resource_name: str = Field(
        default="",
        description="The resource name to identify the Google Vertex agent.",
    )

    @model_validator(mode="after")
    def check_connection_params_non_empty(self):
        """
        Checking if required connection parameters are populated in the config
        """
        resource_name = self.resource_name

        if resource_name == "":
            raise ValueError(
                "Missing 'resource_name' in utility_config for GoogleExecutor."
            )

        return self
