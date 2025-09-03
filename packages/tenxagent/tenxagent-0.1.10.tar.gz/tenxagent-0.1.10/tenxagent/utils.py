# in tenxagent/utils.py
import ast
import operator as op
from typing import Union

# A dictionary mapping allowed AST nodes to their corresponding operator functions
_SUPPORTED_OPERATORS = {
    ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
    ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg
}

def _recursive_eval(node: ast.AST) -> Union[int, float]:
    """
    Recursively traverses the AST and evaluates it safely.
    Raises a TypeError for any unsupported operation.
    """
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        if type(node.op) in _SUPPORTED_OPERATORS:
            return _SUPPORTED_OPERATORS[type(node.op)](_recursive_eval(node.left), _recursive_eval(node.right))
    elif isinstance(node, ast.UnaryOp):
        if type(node.op) in _SUPPORTED_OPERATORS:
            return _SUPPORTED_OPERATORS[type(node.op)](_recursive_eval(node.operand))
    
    raise TypeError(f"Unsupported node type: {type(node).__name__}")

def safe_evaluate(expression: str) -> str:
    """
    Safely evaluates a mathematical string expression using an Abstract Syntax Tree (AST).

    Args:
        expression: The mathematical string to evaluate.

    Returns:
        The result as a string, or a descriptive error message.
    """
    try:
        # Parse the expression into an AST, which is a safe representation of the code
        parsed_ast = ast.parse(expression, mode='eval').body
        result = _recursive_eval(parsed_ast)
        return str(result)
    except (TypeError, SyntaxError, KeyError, ZeroDivisionError):
        return "Error: Invalid or unsupported mathematical expression."
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"