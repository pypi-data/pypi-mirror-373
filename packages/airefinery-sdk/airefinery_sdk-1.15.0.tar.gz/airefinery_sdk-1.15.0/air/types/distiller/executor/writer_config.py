"""WriterAI Agent Configuration Schema"""

from pydantic import Field, BaseModel, model_validator


class WriterAIAgentConfig(BaseModel):
    """
    WriterAI Agent Config
    """

    api_key_env_var: str = Field(
        default="",
        description="The environment variable containing the WriterAI API key.",
    )
    application_id: str = Field(
        default="",
        description="The application ID used to identify the WriterAI agent.",
    )
    wait_time: int = Field(
        default=300,
        description="The time in seconds to wait for the WriterAI agent's response.",
    )

    @model_validator(mode="after")
    def check_connection_params_non_empty(self):
        """
        Checking if required connection parameters are populated in the config
        """
        api_key_env_var = self.api_key_env_var
        application_id = self.application_id

        if api_key_env_var == "":
            raise ValueError(
                "Missing 'api_key_env_var' in utility_config for WriterAIExecutor."
            )

        if application_id == "":
            raise ValueError(
                "Missing 'application_id' in utility_config for WriterAIExecutor."
            )

        return self
