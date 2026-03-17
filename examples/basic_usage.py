"""Example usage of Lumina agent."""

import asyncio
from lumina import Lumina
from lumina.utils.config import LuminaConfig


async def basic_example():
    """Basic usage example."""
    print("=== Basic Example ===\n")
    
    # Create agent with default config
    agent = Lumina()
    
    # Run a simple task
    result = await agent.run("List all Python files in the current directory")
    print(result)
    print("\n" + "="*50 + "\n")


async def custom_config_example():
    """Example with custom configuration."""
    print("=== Custom Config Example ===\n")
    
    # Create custom config
    config = LuminaConfig(
        provider="openai",
        model="gpt-4-turbo-preview",
        temperature=0.5,
        max_iterations=5,
        verbose=True
    )
    
    agent = Lumina(config=config)
    
    result = await agent.run("What files are in this directory? Summarize them.")
    print(result)
    print("\n" + "="*50 + "\n")


async def chat_example():
    """Example of chat mode (no tools)."""
    print("=== Chat Example ===\n")
    
    agent = Lumina()
    
    # Chat without tools
    response1 = await agent.chat("Hello! What's your name?")
    print(f"Assistant: {response1}\n")
    
    response2 = await agent.chat("What can you help me with?")
    print(f"Assistant: {response2}\n")
    
    print("="*50 + "\n")


async def multi_step_example():
    """Example of multi-step task."""
    print("=== Multi-Step Example ===\n")
    
    agent = Lumina()
    
    task = """
    Please do the following:
    1. Create a file called test.txt with the content "Hello, Lumina!"
    2. Read the file back to verify it was created
    3. List all .txt files in the current directory
    """
    
    result = await agent.run(task)
    print(result)
    print("\n" + "="*50 + "\n")


async def custom_tool_example():
    """Example with custom tool."""
    print("=== Custom Tool Example ===\n")
    
    from lumina.tools.base import Tool, ToolParameter
    
    class GreetingTool(Tool):
        """Custom greeting tool."""
        name = "greet"
        description = "Greet someone by name"
        parameters = [
            ToolParameter(
                name="name",
                type="string",
                description="Name of the person to greet",
                required=True
            )
        ]
        
        async def execute(self, name: str, **kwargs):
            return {
                "status": "success",
                "result": f"Hello, {name}! Welcome to Lumina! 🌟"
            }
    
    # Create agent with custom tool
    agent = Lumina(tools=[GreetingTool()])
    
    result = await agent.run("Please greet me. My name is Alex.")
    print(result)
    print("\n" + "="*50 + "\n")


async def memory_example():
    """Example demonstrating memory."""
    print("=== Memory Example ===\n")
    
    agent = Lumina(enable_memory=True)
    
    # First interaction
    await agent.run("My favorite programming language is Python")
    
    # Reset to start new task
    agent.reset()
    
    # Memory should remember the preference
    result = await agent.run("What is my favorite programming language?")
    print(result)
    print("\n" + "="*50 + "\n")


async def main():
    """Run all examples."""
    examples = [
        ("Basic Example", basic_example),
        ("Custom Config", custom_config_example),
        ("Chat Mode", chat_example),
        ("Multi-Step Task", multi_step_example),
        ("Custom Tool", custom_tool_example),
        ("Memory System", memory_example),
    ]
    
    print("\n" + "="*50)
    print("      LUMINA EXAMPLES")
    print("="*50 + "\n")
    
    for name, func in examples:
        try:
            await func()
        except Exception as e:
            print(f"Error in {name}: {e}\n")
            continue


if __name__ == "__main__":
    asyncio.run(main())
