from typing import Optional, List
from contextlib import AsyncExitStack
import traceback
# from utils.logger import logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from datetime import datetime
from utils.logger import logger
import json
import os

from anthropic import Anthropic
from anthropic.types import Message
from openai import OpenAI


system_prompt = """
You are CryptoTradeGPT, a specialized Trader for cryptocurrency trading, portfolio optimization, and risk management. Your responses must be precise, actionable, and data-driven. For every user query, follow these steps:
With 7 years of experience in trading and 5 years of experience in portfolio optimization and risk management.

1. Analyze the latest market data for all mentioned cryptocurrencies.
2. For each new cryptocurrency symbol identified:
   - Extract the current price, liquidity, volatility, and recent trend (bullish/bearish/sideways).
   - Determine a logical entry point, a realistic target price, and a well-placed stop loss using technical analysis (supply/demand) , price action, sentiment, news, and cross-market correlations .
   - For each symbol, provide the following in your response:
     - **Entry Point**: An actionable price or price zone for entering a trade.
     - **Target Price**: A realistic and data-driven price level for taking profit.
     - **Stop Loss**: A prudent stop price to limit downside risk.
   - Obtain a screenshot of the most relevant chart (e.g., TradingView) and capture contextual data from its chart URL, ensuring the screenshot and context represent up-to-date and meaningful information.
   - Do Multi-Time Frame Analysis and provide the analysis in your response.
   - If the user provides a chart URL, use it. Otherwise, construct the URL based on the symbol and take a screenshot.
3. Assess overall market conditions, including sentiment, major news, and cross-market correlations that may influence trades.
4. Summarize trading opportunities and risks, clearly stating the rationale behind each suggestion, and highlight both short- and long-term considerations.
5. Communicate in clear, concise, and professional language suitable for all levels of experience. Use bullet points and tables for clarity where helpful.
6. Verify the accuracy and recency of all extracted data. If any information is missing, specify what’s missing and suggest how to obtain it.
7. Remain alert to market volatility, sudden news, or breaking events, and note if trading plans should be adjusted as a result.
8. When tool execution is requested, always confirm user intent, display the resulting data or screenshot, and provide a brief, insightful interpretation of the chart and its context.
9. End every response with a succinct summary and, when relevant, provide a checklist of next steps for the user.

Your goal is to maximize clarity, reliability, and practical value in every interaction, ensuring every new cryptocurrency discussed includes a clear entry point, target price, stop loss, screenshot, and contextual data from its relevant chart URL.
"""




class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = Anthropic()
        self.tools = []
        self.system_prompt = system_prompt
        self.messages = []  # Initialize messages as an empty list
        self.logger = logger

    # connect to the MCP server
    async def connect_to_server(self, server_script_path: str):
        try:
            is_python = server_script_path.endswith(".py")
            is_js = server_script_path.endswith(".js")
            if not (is_python or is_js):
                raise ValueError("Server script must be a .py or .js file")

            command = "python3" if is_python else "node"
            server_params = StdioServerParameters(
                command=command, args=[server_script_path], env=None
            )

            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            await self.session.initialize()

            self.logger.info("Connected to MCP server")

            mcp_tools = await self.get_mcp_tools()
            self.tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in mcp_tools
            ]

            self.logger.info(
                f"Available tools: {[tool['name'] for tool in self.tools]}"
            )

            return True

        except Exception as e:
            self.logger.error(f"Error connecting to MCP server: {e}")
            traceback.print_exc()
            raise

    # get mcp tool list
    async def get_mcp_tools(self):
        try:
            response = await self.session.list_tools()
            return response.tools
        except Exception as e:
            self.logger.error(f"Error getting MCP tools: {e}")
            raise

    # process query
    async def process_query(self, query: str, chat_history: list = []):
        try:
            self.logger.info(f"Processing query: {query}")
            user_message = {"role": "user", "content": query}
            
            # Initialize messages with chat history if provided, otherwise start fresh
            if chat_history and len(chat_history) > 0:
                self.messages = chat_history
                # Add the latest query if it's not already in chat history
                if self.messages[-1]["role"] != "user" or self.messages[-1]["content"] != query:
                    self.messages.append({"role": "user", "content": query})
            else:
                self.messages = [
                    {"role": "user", "content": query},
                ]

            while True:
                response = await self.call_llm()

                # the response is a text message
                if response.content[0].type == "text" and len(response.content) == 1:
                    assistant_message = {
                        "role": "assistant",
                        "content": response.content[0].text,
                    }
                    self.messages.append(assistant_message)
                    await self.log_conversation()
                    break

                # the response is a tool call
                assistant_message = {
                    "role": "assistant",
                    "content": response.to_dict()["content"],
                }
                self.messages.append(assistant_message)
                await self.log_conversation()

                for content in response.content:
                    if content.type == "tool_use":
                        tool_name = content.name
                        tool_args = content.input
                        tool_use_id = content.id
                        self.logger.info(
                            f"Calling tool {tool_name} with args {tool_args}"
                        )
                        try:
                            result = await self.session.call_tool(tool_name, tool_args)
                            self.logger.info(f"Tool {tool_name} result: {result}...")
                            self.messages.append(
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "tool_result",
                                            "tool_use_id": tool_use_id,
                                            "content": result.content,
                                        }
                                    ],
                                }
                            )
                            await self.log_conversation()
                        except Exception as e:
                            self.logger.error(f"Error calling tool {tool_name}: {e}")
                            raise

            return self.messages

        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            raise

    # call llm
    def sanitize_messages(self, messages):
        """Sanitize messages to ensure compatibility with Anthropic API"""
        sanitized_messages = []
        
        for message in messages:
            sanitized_message = {"role": message["role"]}
            
            # Handle different content types
            if isinstance(message["content"], str):
                sanitized_message["content"] = message["content"]
            elif isinstance(message["content"], list):
                sanitized_content = []
                
                for item in message["content"]:
                    if isinstance(item, dict):
                        # Handle tool results
                        if item.get("type") == "tool_result":
                            sanitized_item = {"type": "tool_result", "tool_use_id": item.get("tool_use_id")}
                            
                            # Sanitize the content of the tool result
                            if "content" in item:
                                if isinstance(item["content"], list):
                                    sanitized_content_list = []
                                    for content_item in item["content"]:
                                        if isinstance(content_item, dict) and "text" in content_item:
                                            # Remove annotations
                                            text_content = {"type": "text", "text": content_item["text"]}
                                            if "annotations" in text_content:
                                                del text_content["annotations"]
                                            sanitized_content_list.append(text_content)
                                        else:
                                            sanitized_content_list.append(content_item)
                                    sanitized_item["content"] = sanitized_content_list
                                else:
                                    sanitized_item["content"] = item["content"]
                            
                            sanitized_content.append(sanitized_item)
                        else:
                            # For other types of dict content
                            sanitized_content.append(item)
                    else:
                        # For non-dict content
                        sanitized_content.append(item)
                
                sanitized_message["content"] = sanitized_content
            else:
                # For other types of content (shouldn't happen, but just in case)
                sanitized_message["content"] = str(message["content"])
            
            sanitized_messages.append(sanitized_message)
        
        return sanitized_messages

    async def call_llm(self):
        try:
            self.logger.info("Calling LLM")
            
            # Sanitize messages before sending to LLM
            sanitized_messages = self.sanitize_messages(self.messages)
            
            return self.llm.messages.create(
                model="claude-3-5-sonnet-latest",
                system=self.system_prompt,  # Pass system prompt here
                messages=sanitized_messages,
                tools=self.tools,
                max_tokens=1000,
            )
        except Exception as e:
            self.logger.error(f"Error calling LLM: {e}")
            raise

    # cleanup
    async def cleanup(self):
        try:
            await self.exit_stack.aclose()
            self.logger.info("Disconnected from MCP server")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            traceback.print_exc()
            raise

    async def log_conversation(self):
        os.makedirs("conversations", exist_ok=True)

        serializable_conversation = []

        for message in self.messages:
            try:
                serializable_message = {"role": message["role"], "content": []}

                # Handle both string and list content
                if isinstance(message["content"], str):
                    serializable_message["content"] = message["content"]
                elif isinstance(message["content"], list):
                    for content_item in message["content"]:
                        if hasattr(content_item, "to_dict"):
                            serializable_message["content"].append(
                                content_item.to_dict()
                            )
                        elif hasattr(content_item, "dict"):
                            serializable_message["content"].append(content_item.dict())
                        elif hasattr(content_item, "model_dump"):
                            serializable_message["content"].append(
                                content_item.model_dump()
                            )
                        else:
                            serializable_message["content"].append(content_item)

                serializable_conversation.append(serializable_message)
            except Exception as e:
                self.logger.error(f"Error processing message: {str(e)}")
                self.logger.debug(f"Message content: {message}")
                raise

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join("conversations", f"conversation_{timestamp}.json")

        try:
            with open(filepath, "w") as f:
                json.dump(serializable_conversation, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error writing conversation to file: {str(e)}")
            self.logger.debug(f"Serializable conversation: {serializable_conversation}")
            raise
