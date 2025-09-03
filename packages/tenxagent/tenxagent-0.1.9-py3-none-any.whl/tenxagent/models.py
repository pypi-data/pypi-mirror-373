# in flexi_agent/models.py
from abc import ABC, abstractmethod
from typing import List, Optional
import os
from dotenv import load_dotenv
from .schemas import Message, GenerationResult # MODIFIED
import json

# Load environment variables from .env file
load_dotenv()

class LanguageModel(ABC):
    @abstractmethod
    async def generate(self, messages: List[Message], tools: Optional[List['Tool']] = None, metadata: Optional[dict] = None) -> GenerationResult: # MODIFIED
        """Takes a list of messages and returns the LLM's response and token usage."""
        pass
    
    @abstractmethod
    def supports_native_tool_calling(self) -> bool:
        """Returns True if this model supports native tool calling, False if it needs manual prompting."""
        pass
    
    def convert_tools_to_model_format(self, tools: Optional[List['Tool']]) -> Optional[List[dict]]:
        """Override this method to convert tools to the specific format needed by your model."""
        return None
    
    def get_tool_calling_system_prompt(self, tools: Optional[List['Tool']] = None, user_prompt: Optional[str] = None) -> str:
        """Override this method to provide model-specific tool calling instructions."""
        prompt_parts = [
            "You are a helpful and intelligent AI assistant.",
            "You have access to various tools that can help you answer questions and perform tasks.",
        ]
        
        if user_prompt:
            prompt_parts.extend(["\n--- Additional Instructions ---", user_prompt])
        
        return "\n".join(prompt_parts)

# --- Example Implementation ---
class OpenAIModel(LanguageModel):
    def __init__(self, 
                 model: str = "gpt-4o-mini", 
                 max_tokens: int = 1000, 
                 temperature: float = 1, 
                 top_p: float = 1, 
                 frequency_penalty: float = 0, 
                 presence_penalty: float = 0,
                 api_key: Optional[str] = None,
                 organization: Optional[str] = None,
                 base_url: Optional[str] = None):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        
        # Load API credentials from environment variables or use provided values
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.organization = organization or os.getenv("OPENAI_ORG_ID")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
    
    def supports_native_tool_calling(self) -> bool:
        """OpenAI supports native function calling."""
        return True
    
    def convert_tools_to_model_format(self, tools: Optional[List['Tool']]) -> Optional[List[dict]]:
        """Convert tools to OpenAI function calling format."""
        if not tools:
            return None
            
        openai_tools = []
        for tool in tools:
            schema = tool.args_schema.model_json_schema()
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": schema
                }
            }
            openai_tools.append(openai_tool)
        return openai_tools
    
    async def generate(self, messages: List[Message], tools: Optional[List['Tool']] = None, metadata: Optional[dict] = None) -> GenerationResult: 
        import openai
        import json
        
        # Initialize OpenAI client with loaded credentials
        client = openai.AsyncOpenAI(
            api_key=self.api_key,
            organization=self.organization,
            base_url=self.base_url
        )
        
        # Convert messages to OpenAI format
        openai_messages = []
        for msg in messages:
            if msg.role == "tool":
                # Tool response messages need special formatting
                openai_messages.append({
                    "role": "tool",
                    "content": msg.content or "",
                    "tool_call_id": msg.tool_call_id
                })
            elif msg.role == "assistant" and getattr(msg, 'tool_calls', None):
                # Assistant messages with tool calls
                openai_msg = {
                    "role": "assistant",
                    "tool_calls": []
                }
                
                # Only add content if it's not None/empty
                if msg.content:
                    openai_msg["content"] = msg.content
                
                # Convert tool calls to OpenAI format
                for tc in msg.tool_calls or []:
                    # Handle arguments - if it's already a string, use as-is, otherwise JSON encode
                    args = tc.arguments if isinstance(tc.arguments, str) else json.dumps(tc.arguments)
                    openai_msg["tool_calls"].append({
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.name,
                            "arguments": args
                        }
                    })
                openai_messages.append(openai_msg)
            else:
                # Regular messages
                message_dict = {"role": msg.role}
                if msg.content is not None:
                    message_dict["content"] = msg.content
                openai_messages.append(message_dict)
        
        # Prepare API call parameters
        api_params = {
            "model": self.model,
            "messages": openai_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty
        }
        
        # Add metadata parameters if provided (for OpenAI-specific features)
        if metadata:
            # OpenAI-specific metadata handling
            if "user" in metadata:
                api_params["user"] = metadata["user"]
            if "seed" in metadata:
                api_params["seed"] = metadata["seed"]
            if "response_format" in metadata:
                api_params["response_format"] = metadata["response_format"]
            if "stream" in metadata:
                api_params["stream"] = metadata["stream"]
            # Add any other OpenAI-specific parameters from metadata
        
        # Add tools if provided (convert them to OpenAI format)
        openai_tools = self.convert_tools_to_model_format(tools)
        if openai_tools:
            api_params["tools"] = openai_tools
            api_params["tool_choice"] = "auto"
        
        # Call OpenAI API
        response = await client.chat.completions.create(**api_params) 

        # Extract message and token usage from the API response
        openai_message = response.choices[0].message
        message_content = openai_message.content
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        # Convert OpenAI tool calls to our ToolCall format
        tool_calls = None
        if getattr(openai_message, 'tool_calls', None):
            from .schemas import ToolCall
            import json
            tool_calls = []
            for tc in openai_message.tool_calls or []:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments)
                ))
        
        return GenerationResult(
            message=Message(
                role="assistant", 
                content=message_content,
                tool_calls=tool_calls
            ),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )

# --- Example: Manual Tool Calling Model ---
class ManualToolCallingModel(LanguageModel):
    """
    Example model that doesn't support native tool calling.
    Instead, it uses manual prompting to request tool calls in JSON format.
    """
    
    def __init__(self, base_model: LanguageModel):
        """Wrap another model to add manual tool calling capability."""
        self.base_model = base_model
    
    def supports_native_tool_calling(self) -> bool:
        """This model uses manual prompting, not native tool calling."""
        return False
    
    def get_tool_calling_system_prompt(self, tools: Optional[List['Tool']] = None, user_prompt: Optional[str] = None) -> str:
        """Generate system prompt with manual tool calling instructions."""
        if user_prompt:
            prompt_parts = [
                user_prompt
            ]
        else:
            prompt_parts = [
                "You are a helpful and intelligent AI assistant.",
            ]
        
        if tools:
            prompt_parts.extend([
                "You have access to the following tools. When you need to use a tool, respond with ONLY a JSON object in this exact format:",
                '{"tool_calls": [{"name": "tool_name", "arguments": {"arg1": "value1", "arg2": "value2"}}]}',
                "Do not include any other text or explanation when making tool calls.",
                "",
                "Available tools:"
            ])
            
            for tool in tools:
                schema = tool.args_schema.model_json_schema()
                arguments_schema = schema.get("properties", {})
                tool_def = f"""- {tool.name}: {tool.description}
                Parameters: {json.dumps(arguments_schema, indent=2)}"""
                prompt_parts.append(tool_def)
            
            prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    async def generate(self, messages: List[Message], tools: Optional[List['Tool']] = None, metadata: Optional[dict] = None) -> GenerationResult:
        """Generate response using the base model (no tool conversion needed)."""
        # For manual tool calling, we don't convert tools - the system prompt handles it
        result = await self.base_model.generate(messages, tools=None, metadata=metadata)
        
        # Check if the response looks like a tool call request
        content = result.message.content
        if content and content.strip().startswith('{"tool_calls"'):
            try:
                import json
                from .schemas import ToolCall
                
                # Parse the JSON tool call request
                tool_call_data = json.loads(content.strip())
                tool_calls = []
                
                for i, tc in enumerate(tool_call_data.get("tool_calls", [])):
                    tool_calls.append(ToolCall(
                        id=f"manual_call_{i}",
                        name=tc["name"], 
                        arguments=tc["arguments"]
                    ))
                
                # Return a message with parsed tool calls
                return GenerationResult(
                    message=Message(
                        role="assistant",
                        content=None,  # No content when making tool calls
                        tool_calls=tool_calls
                    ),
                    input_tokens=result.input_tokens,
                    output_tokens=result.output_tokens
                )
            except (json.JSONDecodeError, KeyError):
                # If parsing fails, return the original response
                pass
        
        return result