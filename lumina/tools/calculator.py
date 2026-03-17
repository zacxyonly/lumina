"""Calculator tool for mathematical operations."""

from typing import Dict, Any
from lumina.tools.base import Tool, ToolParameter


class CalculatorTool(Tool):
    """Tool for performing mathematical calculations."""
    
    name = "calculator"
    description = "Perform basic mathematical operations (add, subtract, multiply, divide)"
    parameters = [
        ToolParameter(
            name="operation",
            type="string",
            description="Operation to perform: add, subtract, multiply, divide",
            required=True,
            enum=["add", "subtract", "multiply", "divide"]
        ),
        ToolParameter(
            name="a",
            type="number",
            description="First number",
            required=True
        ),
        ToolParameter(
            name="b",
            type="number",
            description="Second number",
            required=True
        ),
    ]
    
    async def execute(
        self,
        operation: str,
        a: float,
        b: float,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute mathematical operation.
        
        Args:
            operation: Type of operation (add, subtract, multiply, divide)
            a: First operand
            b: Second operand
        
        Returns:
            Dictionary with status and result
        """
        try:
            operations = {
                "add": lambda x, y: x + y,
                "subtract": lambda x, y: x - y,
                "multiply": lambda x, y: x * y,
                "divide": lambda x, y: x / y if y != 0 else None,
            }
            
            if operation not in operations:
                return {
                    "status": "error",
                    "error": f"Unknown operation: {operation}"
                }
            
            result = operations[operation](a, b)
            
            if result is None:
                return {
                    "status": "error",
                    "error": "Division by zero"
                }
            
            return {
                "status": "success",
                "result": {
                    "operation": operation,
                    "a": a,
                    "b": b,
                    "answer": result
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def demo():
        calc = CalculatorTool()
        
        # Test operations
        tests = [
            ("add", 5, 3),
            ("subtract", 10, 4),
            ("multiply", 6, 7),
            ("divide", 20, 4),
            ("divide", 10, 0),  # Error case
        ]
        
        for op, a, b in tests:
            result = await calc.run(operation=op, a=a, b=b)
            print(f"{op}({a}, {b}) = {result}")
    
    asyncio.run(demo())
