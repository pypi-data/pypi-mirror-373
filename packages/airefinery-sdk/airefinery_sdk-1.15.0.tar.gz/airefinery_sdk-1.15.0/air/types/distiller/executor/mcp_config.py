"""MCP Client Agent Configuration Schema"""

from pydantic import Field, BaseModel, model_validator


class MCPClientAgentConfig(BaseModel):
    """
    MCPClient Agent Config
    """

    mcp_sse_url: str = Field(
        default="",
        description="The URL where the MCP server is hosted.",
    )
    enable_interpreter: bool = Field(
        default=False,
        description="The setting controlling the use of an interpreter that makes the response of the MCP server more user-friendly.",
    )
    tool_call_interval: int = Field(
        default=1,
        description="The time in seconds between consecutive tool calls.",
    )
    max_tool_calls: int = Field(
        default=5,
        description="The maximum number of tool calls.",
    )
    show_tool_progress: bool = Field(
        default=False,
        description="The setting controlling whether tool call progress will be shown.",
    )
    wait_time: int = Field(
        default=300,
        description="The time in seconds to wait for the MCP server's response.",
    )

    @model_validator(mode="after")
    def check_connection_params_non_empty(self):
        """
        Checking if required connection parameters are populated in the config
        """
        mcp_sse_url = self.mcp_sse_url

        if mcp_sse_url == "":
            raise ValueError(
                "Missing 'mcp_sse_url' in utility_config for MCPClientExecutor."
            )

        return self
