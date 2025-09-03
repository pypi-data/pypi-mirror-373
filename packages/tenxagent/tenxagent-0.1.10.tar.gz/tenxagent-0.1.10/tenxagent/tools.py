# in tenxagent/tools.py
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, Optional

class Tool(ABC):
    name: str
    description: str
    args_schema: Optional[Type[BaseModel]]

    @abstractmethod
    def execute(self, metadata: Dict[str, Any] = None, **kwargs) -> str:
        """Executes the tool with validated arguments and optional metadata."""
        pass

# --- Example Implementation ---
class CalculatorInput(BaseModel):
    expression: str = Field(description="The mathematical expression to evaluate.")

class CalculatorTool(Tool):
    name = "calculator"
    description = "Evaluates a mathematical expression."
    args_schema = CalculatorInput

    def execute(self, expression: str, metadata: Dict[str, Any] = None) -> str:
        try:
            return str(eval(expression))
        except Exception as e:
            return f"Error: {e}"