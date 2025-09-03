# in flexi_agent/agent.py
from .models import LanguageModel
from .tools import Tool
from .schemas import Message, GenerationResult, ToolCall 
from typing import List, Optional, Dict, Any, Type, Union
from .history import InMemoryHistoryStore
from pydantic import BaseModel, Field
import json
import asyncio



class TenxAgent:
    def __init__(
        self,
        llm: LanguageModel,
        tools: List[Tool],
        system_prompt: str = None,
        max_llm_calls: int = 10, # RENAMED for clarity
        max_tokens: int = 4096,
        # history_store removed - agent manages its own internal history
        output_model: Optional[Type[BaseModel]] = None,
    ):
        self.llm = llm
        self.tools = {tool.name: tool for tool in tools}
        self.user_system_prompt = system_prompt
        self.max_llm_calls = max_llm_calls
        self.max_tokens = max_tokens
        self._internal_history = InMemoryHistoryStore()
        self.output_model = output_model

    def _get_system_prompt(self) -> str:
        """Get the system prompt from the LLM model, which handles tool calling instructions."""
        tools_list = list(self.tools.values()) if self.tools else None
        
        # Get base prompt from LLM
        base_prompt = self.llm.get_tool_calling_system_prompt(tools=tools_list, user_prompt=self.user_system_prompt)
        
        # Add structured output instructions if output model is specified
        if self.output_model:
            # Get field descriptions and create clear instructions
            field_descriptions = []
            for field_name, field_info in self.output_model.model_fields.items():
                field_type = field_info.annotation
                description = field_info.description or "No description provided"
                
                # Get a clean type description
                type_desc = self._get_type_description(field_type)
                field_descriptions.append(f"  - {field_name}: {type_desc}. {description}")
            
            # Create a realistic example by using the model's schema
            try:
                sample_instance = self.output_model()
                sample_json = sample_instance.model_dump()
                
                # Enhance the example with more realistic values
                sample_json = self._enhance_example_values(sample_json)
                
            except Exception:
                sample_json = {"error": "Could not create example"}
            
            output_instructions = f"""

            CRITICAL: You must respond with ONLY valid JSON in this exact format:

            Required fields:
            {chr(10).join(field_descriptions)}

            Example response:
            {json.dumps(sample_json, indent=2)}

            RULES:
            1. Response must be valid JSON only - no extra text, explanations, or markdown
            2. All required fields must be present
            3. Use exact enum values as specified 
            4. Follow the field descriptions carefully
            5. Start your response with {{ and end with }}"""
            
            return base_prompt + output_instructions
        
        return base_prompt

    def _get_type_description(self, field_type) -> str:
        """Get a clean, descriptive type description for structured output instructions."""
        import typing
        
        # Handle None type
        if field_type is type(None):
            return "null"
        
        # Handle basic types
        if field_type in (str, int, float, bool):
            return field_type.__name__
        
        # Handle enums
        if hasattr(field_type, '__members__'):
            enum_values = list(field_type.__members__.keys())
            return f"Must be one of {enum_values}"
        
        # Handle Optional types (Union[X, None])
        if hasattr(field_type, '__origin__'):
            origin = field_type.__origin__
            args = getattr(field_type, '__args__', ())
            
            # Optional[X] is Union[X, NoneType]
            if origin is typing.Union and len(args) == 2 and type(None) in args:
                non_none_type = args[0] if args[1] is type(None) else args[1]
                return f"Optional {self._get_type_description(non_none_type)}"
            
            # List[X]
            if origin is list:
                if args:
                    item_type = self._get_type_description(args[0])
                    return f"Array of {item_type}"
                return "Array"
            
            # Dict[X, Y]
            if origin is dict:
                if len(args) >= 2:
                    key_type = self._get_type_description(args[0])
                    value_type = self._get_type_description(args[1])
                    return f"Object with {key_type} keys and {value_type} values"
                return "Object"
            
            # Union types
            if origin is typing.Union:
                type_descriptions = [self._get_type_description(arg) for arg in args]
                return f"One of: {' | '.join(type_descriptions)}"
        
        # Handle Pydantic models
        if hasattr(field_type, 'model_fields'):
            return f"Object ({field_type.__name__})"
        
        # Fallback
        return str(field_type).replace('<class ', '').replace('>', '').replace("'", "")

    def _enhance_example_values(self, sample_json: dict) -> dict:
        """Enhance example JSON with more realistic values based on field names and types."""
        enhanced = sample_json.copy()
        
        for field_name, field_info in self.output_model.model_fields.items():
            if field_name in enhanced:
                field_type = field_info.annotation
                current_value = enhanced[field_name]
                
                # Enhance based on field name patterns
                if 'message' in field_name.lower() and isinstance(current_value, str):
                    enhanced[field_name] = "This is an example response message"
                elif 'description' in field_name.lower() and isinstance(current_value, str):
                    enhanced[field_name] = "Example description text"
                elif 'title' in field_name.lower() and isinstance(current_value, str):
                    enhanced[field_name] = "Example Title"
                elif 'name' in field_name.lower() and isinstance(current_value, str):
                    enhanced[field_name] = "example_name"
                elif 'id' in field_name.lower() and isinstance(current_value, str):
                    enhanced[field_name] = "example_id_123"
                elif 'count' in field_name.lower() and isinstance(current_value, int):
                    enhanced[field_name] = 42
                elif 'tokens' in field_name.lower() and isinstance(current_value, int):
                    enhanced[field_name] = 150
                
                # Enhance enum values
                if hasattr(field_type, '__members__') and current_value in field_type.__members__:
                    # Use the first enum value if current is default
                    enum_values = list(field_type.__members__.keys())
                    if enum_values:
                        enhanced[field_name] = enum_values[0]
                
                # Handle Optional enum types
                if hasattr(field_type, '__origin__') and hasattr(field_type, '__args__'):
                    args = field_type.__args__
                    if len(args) == 2 and type(None) in args:
                        non_none_type = args[0] if args[1] is type(None) else args[1]
                        if hasattr(non_none_type, '__members__'):
                            enum_values = list(non_none_type.__members__.keys())
                            if enum_values:
                                enhanced[field_name] = enum_values[0]
        
        return enhanced

    def _populate_token_fields(self, response_data: dict, metadata: Dict[str, Any]) -> dict:
        """Populate token fields in response data if they exist in the output model."""
        if not self.output_model:
            return response_data
            
        token_usage = metadata.get('token_usage', {})
        
        # Check for common token field names and populate them
        token_field_mappings = {
            'total_tokens': ['total_tokens', 'tokens_used', 'token_count'],
            'prompt_tokens': ['prompt_tokens', 'input_tokens'], 
            'completion_tokens': ['completion_tokens', 'output_tokens', 'response_tokens']
        }
        
        for usage_key, field_names in token_field_mappings.items():
            for field_name in field_names:
                if field_name in self.output_model.model_fields:
                    response_data[field_name] = token_usage.get(usage_key, 0)
                    break  # Only set the first matching field
        
        return response_data

    async def _execute_tool(self, tool_call: ToolCall, metadata: Dict[str, Any]) -> Message:
        """Helper to execute a single tool call and return a tool message."""
        tool = self.tools.get(tool_call.name)
        if not tool:
            result_content = f"Error: Tool '{tool_call.name}' not found."
        else:
            try:
                validated_args = tool.args_schema(**tool_call.arguments)
                result_content = await asyncio.to_thread(tool.execute, metadata=metadata, **validated_args.model_dump())
            except Exception as e:
                result_content = f"Error executing tool '{tool_call.name}': {e}"
        
        return Message(role="tool", content=result_content, tool_call_id=tool_call.id) # Assumes ToolCall has an ID

    async def run(self, user_input: str, session_id: str = "default", metadata: Optional[Dict[str, Any]] = None, history: Optional[List[Message]] = None) -> Union[str, BaseModel]:
        metadata = metadata or {}
        llm_calls_count = 0
        total_tokens_used = 0
        
        # Initialize token tracking in metadata if not present
        if 'token_usage' not in metadata:
            metadata['token_usage'] = {
                'total_tokens': 0,
                'prompt_tokens': 0,
                'completion_tokens': 0
            }
        
        # Use provided history or get from internal store
        if history is not None:
            # Use provided history - don't store anything, just use as-is
            messages = history.copy()
            user_message = Message(role="user", content=user_input)
            messages.append(user_message)
        else:
            # Use internal history store
            messages = await self._internal_history.get_messages(session_id)
            user_message = Message(role="user", content=user_input)
            await self._internal_history.add_message(session_id, user_message)
            messages.append(user_message)
        
        if not any(msg.role == "system" for msg in messages):
            messages.insert(0, Message(role="system", content=self._get_system_prompt()))

        while True:
            if llm_calls_count >= self.max_llm_calls:
                return "Error: Maximum number of LLM calls reached."
            
            llm_calls_count += 1
            
            # Pass tools to the LLM (it will handle the conversion to its own format)
            tools_list = list(self.tools.values()) if self.tools else None
            generation_result = await self.llm.generate(messages, tools=tools_list, metadata=metadata)
            
            # Update token tracking
            call_tokens = generation_result.input_tokens + generation_result.output_tokens
            total_tokens_used += call_tokens
            metadata['token_usage']['total_tokens'] += call_tokens
            metadata['token_usage']['prompt_tokens'] += generation_result.input_tokens
            metadata['token_usage']['completion_tokens'] += generation_result.output_tokens
            
            if total_tokens_used >= self.max_tokens:
                return "Error: Token limit reached."
            
            response_message = generation_result.message
            
            # Store assistant message only if using internal history
            if history is None:
                await self._internal_history.add_message(session_id, response_message)
            
            messages.append(response_message)
            
            # --- NEW: PARALLEL TOOL CALL LOGIC ---
            if getattr(response_message, 'tool_calls', None):
                # 1. Create a task for each tool call requested by the LLM
                execution_tasks = [
                    self._execute_tool(tool_call, metadata) for tool_call in response_message.tool_calls or []
                ]
                
                # 2. Run all tool calls concurrently
                tool_result_messages = await asyncio.gather(*execution_tasks)
                
                # 3. Add all results to history and continue the loop
                for msg in tool_result_messages:
                    # Store tool message only if using internal history
                    if history is None:
                        await self._internal_history.add_message(session_id, msg)
                    
                    messages.append(msg)
                
                continue # Go back to the LLM with the tool results
            
            # If there are no tool calls, we have our final answer
            final_content = response_message.content or "The agent finished without a final message."
            
            # If output model is specified, validate and parse the response
            if self.output_model:
                try:
                    # Try to parse as JSON first
                    if final_content.strip().startswith('{') and final_content.strip().endswith('}'):
                        import json
                        parsed_json = json.loads(final_content)
                        # Populate token fields if they exist in the model
                        parsed_json = self._populate_token_fields(parsed_json, metadata)
                        validated_output = self.output_model(**parsed_json)
                        return validated_output  # Return the Pydantic model instance
                    else:
                        # Content might have extra text, try to extract JSON
                        import re
                        json_match = re.search(r'\{.*\}', final_content, re.DOTALL)
                        if json_match:
                            parsed_json = json.loads(json_match.group())
                            # Populate token fields if they exist in the model
                            parsed_json = self._populate_token_fields(parsed_json, metadata)
                            validated_output = self.output_model(**parsed_json)
                            return validated_output  # Return the Pydantic model instance
                        else:
                            print(final_content)
                            return f"Error: Response does not match required output format. Expected JSON matching {self.output_model.__name__} schema."
                except json.JSONDecodeError as e:
                    print(final_content)
                    return f"Error: Invalid JSON in response: {str(e)}"
                except Exception as e:
                    print(final_content)
                    return f"Error: Response validation failed: {str(e)}"
            
            return final_content

class AgentToolInput(BaseModel):
    task: str = Field(description="The specific task for the agent to perform.")

def create_tenx_agent_tool(agent: TenxAgent, name: str, description: str) -> Tool:
    """Wraps an Agent to be used as a Tool by another Agent."""
    
    class AgentAsTool(Tool):
        def __init__(self, agent_instance, tool_name, tool_description):
            self.name = tool_name
            self.description = tool_description
            self.args_schema = AgentToolInput
            self.agent = agent_instance

        def execute(self, task: str, metadata: dict = None) -> str:
            import asyncio
            import uuid
            
            # Generate a unique session ID for this tool execution
            session_id = f"agent_tool_{uuid.uuid4().hex[:8]}"
            
            # Prepare metadata for the nested agent, preserving token tracking
            nested_metadata = metadata.copy() if metadata else {}
            
            # Simple approach: just run the async function
            try:
                result = asyncio.run(self.agent.run(task, session_id=session_id, metadata=nested_metadata))
                
                # Propagate token usage back to parent metadata
                if metadata and 'token_usage' in nested_metadata and 'token_usage' in metadata:
                    nested_usage = nested_metadata['token_usage']
                    metadata['token_usage']['total_tokens'] += nested_usage['total_tokens']
                    metadata['token_usage']['prompt_tokens'] += nested_usage['prompt_tokens'] 
                    metadata['token_usage']['completion_tokens'] += nested_usage['completion_tokens']
                
                return str(result)  # Ensure string return for tool interface
            except RuntimeError as e:
                if "cannot be called from a running event loop" in str(e):
                    # We're in an async context, use a thread
                    import threading
                    import queue
                    
                    result_queue = queue.Queue()
                    
                    def run_in_thread():
                        try:
                            result = asyncio.run(self.agent.run(task, session_id=session_id, metadata=nested_metadata))
                            result_queue.put(('success', result, nested_metadata))
                        except Exception as e:
                            result_queue.put(('error', e, nested_metadata))
                    
                    thread = threading.Thread(target=run_in_thread)
                    thread.start()
                    thread.join()
                    
                    status, result, returned_metadata = result_queue.get()
                    
                    # Propagate token usage back to parent metadata
                    if metadata and 'token_usage' in returned_metadata and 'token_usage' in metadata:
                        nested_usage = returned_metadata['token_usage']
                        metadata['token_usage']['total_tokens'] += nested_usage['total_tokens']
                        metadata['token_usage']['prompt_tokens'] += nested_usage['prompt_tokens']
                        metadata['token_usage']['completion_tokens'] += nested_usage['completion_tokens']
                    
                    if status == 'error':
                        raise result
                    return str(result)  # Ensure string return for tool interface
                else:
                    raise e
            
    return AgentAsTool(agent, name, description)