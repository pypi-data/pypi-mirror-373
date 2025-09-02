from pydantic import Field, BaseModel, model_validator
import warnings


class PublicAgentCardConfig(BaseModel):
    """
    Public agent card details.
    Two fields, at least one required, not allowed concurrently empty.
    """

    public_agent_card_path: str = Field(
        default="", description="Path to the public agent card."
    )
    rpc_url: str = Field(default="", description="RPC URL for the agent.")

    @model_validator(mode="after")
    def check_public_agent_card_fields(self):
        public_path = self.public_agent_card_path
        rpc = self.rpc_url

        if public_path == "" and rpc == "":
            raise ValueError(
                "Either 'public_agent_card_path' or 'rpc_url' must be provided (cannot both be empty)."
            )
        return self


class PrivateAgentCardConfig(BaseModel):
    """
    Private agent card details.
    Two fields, both optional.
    """

    extended_agent_card_path: str = Field(
        default="/agent/authenticatedExtendedCard",
        description="Path to the extended agent card.",
    )
    authentication_token: str = Field(description="Authentication token for the agent.")


class AgentCardConfig(BaseModel):
    """
    Dictionary containing public or private agent card information.
    Two fields, public required.
    """

    public: PublicAgentCardConfig = Field(
        default=PublicAgentCardConfig(public_agent_card_path="dummy_path"),
        description="Public agent card details.",
    )
    private: PrivateAgentCardConfig | None = Field(
        default=None, description="Private agent card details."
    )

    @model_validator(mode="after")
    def check_public_agent_card_non_empty(self):
        public = self.public

        if not public:
            raise ValueError("Public agent card details must be provided.")
        return self


class ResponsePrefsConfig(BaseModel):
    """
    Dictionary containing the preferences for how to handle the agent's response.
    Two fields, both optional, not allowed concurrently True - second ignored if first True.
    """

    tracing: bool | None = Field(
        default=False, description="Enable tracing of intermediate agent responses."
    )
    streaming: bool | None = Field(
        default=False, description="Enable streaming of agent responses."
    )

    @model_validator(mode="after")
    def check_conflicting_repsonse_prefs(self):
        tracing = self.tracing
        streaming = self.streaming

        if tracing and streaming:
            warnings.warn(
                "Both Tracing and Streaming are enabled. Streaming is ignored."
            )
        return self


class A2AClientAgentConfig(BaseModel):
    """
    A2A Client Agent Config
    - base_url: Required, must be non-empty
    - agent_card: Required, dictionary or instance of AgentCardConfig.
    - response_prefs: Optional, dictionary or instance of ResponsePrefsConfig.
    - wait_time: Optional, integer.
    - contexts: Optional, list
    """

    base_url: str = Field(
        default="", description="The base URL where the agents are located."
    )
    agent_card: AgentCardConfig = Field(
        default_factory=AgentCardConfig,
        description="Dictionary containing public (agent card path or RPC URL) or "
        "private (extended agent card and authentication token) of the agent.",
    )
    response_prefs: ResponsePrefsConfig = Field(
        default_factory=ResponsePrefsConfig,
        description="Configure tracing of intermediate agent responses "
        "and streaming of response chunks.",
    )
    wait_time: int = Field(
        default=300,
        description="Time in seconds to wait for a response from the "
        "A2A agent before timing out.",
    )
    contexts: list = Field(
        default_factory=list,
        description="List of additional contexts to be passed to the agent.",
    )

    @model_validator(mode="after")
    def check_empty_base_url(self):
        base_url = self.base_url

        if base_url == "":
            raise ValueError("Missing 'base_url' in utility_config for A2AExecutor.")
        return self
