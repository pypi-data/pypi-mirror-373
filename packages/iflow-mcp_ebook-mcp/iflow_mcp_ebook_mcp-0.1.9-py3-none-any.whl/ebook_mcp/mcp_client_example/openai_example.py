import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import json
import tiktoken
import logging
import os
from datetime import datetime

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# Setup logging
def setup_logging():
    """Configure logging settings"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Generate log filename with timestamp
    log_filename = f'logs/openai_mcp_client_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            #logging.StreamHandler()  # Also output to console
        ]
    )
    return logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.client = AsyncOpenAI()
        self.conversation_history = []
        self.model = "gpt-4-turbo-preview"
        self.max_tokens = 4000
        self.encoding = tiktoken.encoding_for_model(self.model)
        self.logger = setup_logging()

    def count_tokens(self, messages):
        """Calculate token count for message history"""
        num_tokens = 0
        for message in messages:
            num_tokens += 4
            for key, value in message.items():
                if key == "tool_calls" and value:
                    for tool_call in value:
                        if isinstance(tool_call, dict):
                            function_name = tool_call.get("function", {}).get("name", "")
                            function_args = tool_call.get("function", {}).get("arguments", "")
                        else:
                            function_name = tool_call.function.name
                            function_args = tool_call.function.arguments
                        num_tokens += len(self.encoding.encode(function_name))
                        num_tokens += len(self.encoding.encode(str(function_args)))
                elif isinstance(value, str):
                    num_tokens += len(self.encoding.encode(value))
        num_tokens += 2
        return num_tokens

    def trim_conversation_history(self):
        """Trim conversation history to ensure it doesn't exceed maximum token limit"""
        while self.conversation_history and self.count_tokens(self.conversation_history) > self.max_tokens:
            removed_message = self.conversation_history.pop(1)
            self.logger.debug(f"Trimmed message from history: {removed_message}")

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server"""
        self.logger.info(f"Connecting to server: {server_script_path}")
        
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
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
        
        response = await self.session.list_tools()
        tools = response.tools
        self.logger.info(f"Connected to server with tools: {[tool.name for tool in tools]}")
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using OpenAI and available tools"""
        self.logger.debug(f"Processing user query: {query}")
        
        if query.lower() == 'clear':
            self.logger.debug("Clearing conversation history")
            self.conversation_history = []
            return "Conversation history cleared."

        self.conversation_history.append({
            "role": "user",
            "content": query
        })
        self.logger.debug("Added user message to history")

        self.trim_conversation_history()

        response = await self.session.list_tools()
        available_tools = [{ 
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema
            }
        } for tool in response.tools]

        final_text = []
        while True:
            self.logger.debug(f"Sending request to OpenAI with {len(self.conversation_history)} messages in history")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=self.conversation_history,
                tools=available_tools,
                tool_choice="auto"
            )

            message = response.choices[0].message
            assistant_message = {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    } for tool_call in (message.tool_calls or [])
                ] if message.tool_calls else None
            }
            self.conversation_history.append(assistant_message)
            self.logger.debug(f"Added assistant message to history: {message.content}")
            final_text.append(message.content or "")

            if not message.tool_calls:
                break

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                self.logger.debug(f"Calling tool: {tool_name}")
                self.logger.debug(f"Tool arguments: {tool_args}")
                
                result = await self.session.call_tool(tool_name, tool_args)
                self.logger.debug(f"Tool result: {result.content}")
                
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result.content
                }
                self.conversation_history.append(tool_message)
                self.logger.debug("Added tool result to history")

            self.trim_conversation_history()

        self.logger.debug("Final conversation history:")
        for msg in self.conversation_history:
            self.logger.debug(f"Message: {msg}")

        return "\n".join(filter(None, final_text))

    async def chat_loop(self):
        """Run an interactive chat loop"""
        self.logger.info("Starting chat loop")
        print("\nMCP Client Started!")
        print("Type your queries, 'clear' to clear history, or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    self.logger.info("User requested to quit")
                    break
                    
                response = await self.process_query(query)
                print("\n" + response)
                    
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                self.logger.error(error_msg, exc_info=True)
                print("\n" + error_msg)
    
    async def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up resources")
        await self.exit_stack.aclose()

async def main():
    if len(sys.argv) < 2:
        print("Usage: python client.py <path_to_server_script>")
        sys.exit(1)
        
    client = MCPClient()
    client.logger.info("Starting OpenAI MCP Client application")
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())