from typing import Optional, TypedDict
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

class TwolyOptions(TypedDict, total=False):
    """Options for configuring the 2ly MCP connection."""
    workspace: str
    nats_servers: str
    version: str

class TwolyMCP:
    """
    Provide a 2l MCP Server ready to use with Langchain.
    """

    def __init__(self, name: str, options: Optional[TwolyOptions] = None):
        self.name = name
        self.options = options
        if options is None:
            options = {}

        nats_servers = options.get("nats_servers", "nats://localhost:4222")
        version = options.get("version", "latest")

        env = {
            "RUNTIME_NAME": name,
            "NATS_SERVERS": nats_servers,
        }        
        
        if "workspace" in options:
            env["WORKSPACE_ID"] = options["workspace"]

        self.serverParams = StdioServerParameters(
            command="npx",
            args=["@2ly/runtime@" + version],
            env=env
        )

    async def tools(self):
        async with stdio_client(self.serverParams) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize(client_info={"name": "Langchain::twoly", "version": "0.0.1"})

                # Get tools
                tools = await load_mcp_tools(session)
                return tools
        