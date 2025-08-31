# in tests/test_agent.py

import pytest
import asyncio
from tenxagent.agent import TenxAgent
from tenxagent.tools import Tool
from tenxagent.models import LanguageModel
from tenxagent.schemas import Message, GenerationResult
from pydantic import BaseModel, Field

# --- 1. Mock Objects and Test Fixtures ---
# Create a fake LanguageModel for testing.
class MockLanguageModel(LanguageModel):
    def __init__(self):
        # We can configure this to return different things for different tests
        self.responses = []
        self.call_count = 0

    def set_responses(self, responses: list):
        """Set a sequence of responses for the mock LLM to return."""
        self.responses = responses
        self.call_count = 0

    def supports_native_tool_calling(self) -> bool:
        """Mock model supports native tool calling for testing."""
        return True

    async def generate(self, messages: list, tools=None, metadata=None) -> GenerationResult:
        if not self.responses:
            raise Exception("MockLanguageModel has no responses configured!")
        
        # Return the next response in the queue
        response = self.responses[self.call_count % len(self.responses)]
        self.call_count += 1
        return response

# Create a simple tool for testing.
class AdderInput(BaseModel):
    a: int = Field(description="First number")
    b: int = Field(description="Second number")

class AdderTool(Tool):
    name = "adder"
    description = "Adds two numbers together."
    args_schema = AdderInput

    def execute(self, a: int, b: int, metadata: dict = None) -> str:
        return str(a + b)

# Use pytest fixtures to create reusable components for our tests
@pytest.fixture
def mock_llm():
    return MockLanguageModel()

@pytest.fixture
def adder_tool():
    return AdderTool()

# --- 2. The Tests ---

@pytest.mark.asyncio
async def test_agent_run_simple_response(mock_llm, adder_tool):
    """Tests that the agent can return a simple response without calling a tool."""
    # Arrange: Configure the mock LLM's response
    mock_llm.set_responses([
        GenerationResult(message=Message(role="assistant", content="The answer is 42."), input_tokens=10, output_tokens=5)
    ])
    agent = TenxAgent(llm=mock_llm, tools=[adder_tool])

    # Act: Run the agent
    result = await agent.run("What is the meaning of life?", session_id="test_session")

    # Assert: Check the result
    assert result == "The answer is 42."
    assert mock_llm.call_count == 1

@pytest.mark.asyncio
async def test_agent_run_with_single_tool_call(mock_llm, adder_tool):
    """Tests a full agent cycle: LLM asks for a tool, agent executes it, LLM gives final answer."""
    # Arrange: Configure a sequence of responses for the LLM
    from tenxagent.schemas import ToolCall
    mock_llm.set_responses([
        # First, the LLM asks to use the 'adder' tool
        GenerationResult(
            message=Message(
                role="assistant", 
                content="", 
                # Updated to use the new tool_calls format
                tool_calls=[ToolCall(id="call_1", name="adder", arguments={"a": 5, "b": 7})]
            ),
            input_tokens=50,
            output_tokens=20
        ),
        # Second, after getting the tool result, the LLM gives the final answer
        GenerationResult(
            message=Message(role="assistant", content="5 plus 7 is 12."),
            input_tokens=80, # Includes the tool result message
            output_tokens=10
        )
    ])
    agent = TenxAgent(llm=mock_llm, tools=[adder_tool])

    # Act
    result = await agent.run("What is 5 plus 7?", session_id="test_session")

    # Assert
    assert result == "5 plus 7 is 12."
    assert mock_llm.call_count == 2 # The LLM was called twice

@pytest.mark.asyncio
async def test_agent_stops_at_max_llm_calls(mock_llm, adder_tool):
    """Tests that the agent correctly enforces the max_llm_calls limit."""
    # Arrange: Configure the LLM to always call a tool, forcing a loop
    from tenxagent.schemas import ToolCall
    tool_call_response = GenerationResult(
        message=Message(role="assistant", content="", tool_calls=[ToolCall(id="call_1", name="adder", arguments={"a": 1, "b": 1})]),
        input_tokens=50, output_tokens=20
    )
    mock_llm.set_responses([tool_call_response]) # It will return this over and over
    
    # Create an agent with a low limit (renamed parameter)
    agent = TenxAgent(llm=mock_llm, tools=[adder_tool], max_llm_calls=3)

    # Act
    result = await agent.run("Add 1+1 repeatedly", session_id="test_session")

    # Assert
    assert result == "Error: Maximum number of LLM calls reached."
    assert mock_llm.call_count == 3

@pytest.mark.asyncio
async def test_agent_stops_at_max_tokens(mock_llm, adder_tool):
    """Tests that the agent correctly enforces the max_tokens limit."""
    # Arrange: Configure a response with a high token count
    high_token_response = GenerationResult(
        message=Message(role="assistant", content="Final answer."),
        input_tokens=1000, output_tokens=500
    )
    mock_llm.set_responses([high_token_response])
    
    agent = TenxAgent(llm=mock_llm, tools=[adder_tool], max_tokens=1200)

    # Act
    result = await agent.run("This is a query.", session_id="test_session")

    # Assert
    assert result == "Error: Token limit reached."