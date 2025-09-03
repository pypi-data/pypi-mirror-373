import asyncio
import logging
import os
from datetime import datetime
from typing import Optional, List, Dict
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"anthropic_mcp_client_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        #logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MCPClient:
    """
    MCP Client class that handles communication with the server and Claude API.
    Manages message history and tool execution.
    """
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        self.messages: List[Dict[str, str]] = []
        self.max_messages = 20  # Maximum number of messages to keep in history
        self.max_tokens = 8000  # Maximum token count (using half of Claude 3.5 Sonnet's 16k context window)
        logger.debug("MCPClient initialized")

    def _estimate_tokens(self, text: str) -> int:
        """
        Roughly estimate the number of tokens in a text.
        Uses a simple approximation of 4 characters per token.
        """
        return len(text) // 4

    def _trim_messages_history(self):
        """
        Clean up message history to ensure it doesn't exceed limits.
        Removes oldest messages first when exceeding count or token limits.
        """
        initial_count = len(self.messages)
        
        # Remove messages if count exceeds limit
        while len(self.messages) > self.max_messages:
            removed_msg = self.messages.pop(0)
            logger.debug(f"Removed message due to count limit: {removed_msg['role']}")
        
        # Calculate and trim based on token count
        total_tokens = sum(self._estimate_tokens(msg["content"]) for msg in self.messages)
        while total_tokens > self.max_tokens and self.messages:
            removed_msg = self.messages.pop(0)
            removed_tokens = self._estimate_tokens(removed_msg["content"])
            total_tokens -= removed_tokens
            logger.debug(f"Removed message due to token limit: {removed_msg['role']}, tokens: {removed_tokens}")
        
        if initial_count != len(self.messages):
            logger.debug(f"Trimmed messages from {initial_count} to {len(self.messages)}")

    def add_message(self, role: str, content: str):
        """
        Add a new message to the history and trim if necessary.
        """
        self.messages.append({"role": role, "content": content})
        logger.debug(f"Added message - Role: {role}, Content length: {len(content)}")
        self._trim_messages_history()

    async def connect_to_server(self, server_script_path: str):
        """
        Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        logger.debug(f"Connecting to server with script: {server_script_path}")
        
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            logger.error("Invalid server script type")
            raise ValueError("Server script must be a .py or .js file")
            
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        tools_list = [tool.name for tool in tools]
        logger.debug(f"Connected to server with tools: {tools_list}")
        print("\nConnected to server with tools:", tools_list)

    async def process_query(self, query: str) -> str:
        """
        Process a query using Claude and available tools
        """
        logger.debug(f"Processing new query: {query}")
        self.add_message("user", query)

        response = await self.session.list_tools()
        available_tools = [{ 
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]
        logger.debug(f"Available tools: {[tool['name'] for tool in available_tools]}")

        # Initial Claude API call
        response = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=self.messages,
            tools=available_tools
        )

        tool_results = []
        final_text = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
                self.add_message("assistant", content.text)
                logger.debug("Added assistant text response")
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                logger.debug(f"Executing tool call - Tool: {tool_name}, Args: {tool_args}")
                result = await self.session.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                logger.debug(f"Tool execution result: {result.content}")

                if hasattr(content, 'text') and content.text:
                    self.add_message("assistant", content.text)
                self.add_message("user", result.content)

                response = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=self.messages,
                )

                final_text.append(response.content[0].text)
                self.add_message("assistant", response.content[0].text)
                logger.debug("Added follow-up assistant response")

        return "\n".join(final_text)

    async def chat_loop(self):
        """
        Run an interactive chat loop
        """
        logger.info("Starting chat loop")
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        print("Type 'clear' to clear conversation history.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    logger.info("Chat loop terminated by user")
                    break
                elif query.lower() == 'clear':
                    self.messages = []
                    logger.debug("Conversation history cleared")
                    print("\nConversation history cleared.")
                    continue
                    
                response = await self.process_query(query)
                print("\n" + response)
                    
            except Exception as e:
                logger.error(f"Error in chat loop: {str(e)}", exc_info=True)
                print(f"\nError: {str(e)}")
    
    async def cleanup(self):
        """
        Clean up resources
        """
        logger.debug("Cleaning up resources")
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        logger.error("Missing server script path argument")
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
        
    client = MCPClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    logger.info("Starting Anthropic MCP Client application")
    asyncio.run(main())