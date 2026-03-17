"""Main Lumina AI Agent."""

import json
import uuid
from typing import List, Dict, Any, Optional
from lumina.core.llm import LLMProvider, Message, create_provider
from lumina.core.memory import Memory
from lumina.tools.base import ToolRegistry, Tool
from lumina.tools.file import get_file_tools
from lumina.utils.config import get_config, LuminaConfig
from lumina.utils.logger import get_logger


class Lumina:
    """Lumina AI Agent - autonomous task executor."""
    
    def __init__(
        self,
        config: Optional[LuminaConfig] = None,
        tools: Optional[List[Tool]] = None,
        enable_memory: bool = True,
    ):
        """Initialize Lumina agent.
        
        Args:
            config: Configuration object (uses global config if None)
            tools: List of custom tools to register
            enable_memory: Whether to enable memory system
        """
        self.config = config or get_config()
        self.config.validate()
        
        self.logger = get_logger(
            level=20 if not self.config.debug else 10,
            log_file=self.config.log_dir / "lumina.log"
        )
        
        # Initialize LLM provider
        api_key = self.config.get_api_key()
        self.llm = create_provider(
            provider=self.config.provider,
            api_key=api_key,
            model=self.config.model
        )
        
        # Initialize tool registry
        self.tools = ToolRegistry()
        
        # Register default file tools
        for tool in get_file_tools():
            self.tools.register(tool)
        
        # Register custom tools
        if tools:
            for tool in tools:
                self.tools.register(tool)
        
        # Initialize memory
        self.memory = None
        if enable_memory and self.config.enable_memory:
            self.memory = Memory(self.config.memory_dir)
        
        # Session state
        self.session_id = str(uuid.uuid4())
        self.messages: List[Message] = []
        self.iteration_count = 0
        
        self.logger.success("Lumina initialized successfully")
        self.logger.info(f"Provider: {self.config.provider} | Model: {self.config.model}")
        self.logger.info(f"Tools: {', '.join(self.tools.list_tools())}")
    
    async def run(
        self,
        task: str,
        context: Optional[str] = None,
        max_iterations: Optional[int] = None,
    ) -> str:
        """Run agent on a task.
        
        Args:
            task: Task description
            context: Additional context
            max_iterations: Maximum iterations (uses config default if None)
        
        Returns:
            Final response string
        """
        self.iteration_count = 0
        max_iter = max_iterations or self.config.max_iterations
        
        self.logger.agent_action("Starting task", task[:100])
        
        # Build initial message
        system_prompt = self._build_system_prompt()
        self.messages = [Message(role="system", content=system_prompt)]
        
        # Add context if provided
        if context:
            user_content = f"Context: {context}\n\nTask: {task}"
        else:
            user_content = task
        
        self.messages.append(Message(role="user", content=user_content))
        
        # Add to memory
        if self.memory:
            self.memory.add_short_term(task, type="conversation", role="user")
        
        # Main agent loop
        while self.iteration_count < max_iter:
            self.iteration_count += 1
            self.logger.thinking(f"Iteration {self.iteration_count}/{max_iter}")
            
            # Get LLM response
            tool_format = "anthropic" if self.config.provider == "anthropic" else "openai"
            tool_specs = self.tools.get_specs(format=tool_format)
            
            response = await self.llm.chat(
                messages=self.messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                tools=tool_specs if tool_specs else None
            )
            
            # Add assistant message
            self.messages.append(Message(
                role="assistant",
                content=response.content,
                tool_calls=response.tool_calls
            ))
            
            if self.memory:
                self.memory.add_short_term(
                    response.content,
                    type="conversation",
                    role="assistant"
                )
            
            # If no tool calls, we're done
            if not response.tool_calls:
                self.logger.success("Task completed")
                if self.memory:
                    self.memory.save_conversation(self.messages, self.session_id)
                return response.content
            
            # Execute tool calls
            for tool_call in response.tool_calls:
                func_name = tool_call["function"]["name"]
                func_args = json.loads(tool_call["function"]["arguments"])
                
                self.logger.tool_call(func_name, str(func_args)[:50])
                
                # Execute tool
                result = await self.tools.execute(func_name, **func_args)
                
                # Add tool result to messages
                tool_result_content = json.dumps(result, indent=2)
                
                if self.config.provider == "anthropic":
                    # Anthropic format
                    self.messages.append(Message(
                        role="user",
                        content=f"Tool result for {func_name}:\n{tool_result_content}"
                    ))
                else:
                    # OpenAI format
                    self.messages.append(Message(
                        role="tool",
                        content=tool_result_content,
                        name=func_name,
                        tool_call_id=tool_call.get("id", "")
                    ))
                
                if self.memory:
                    self.memory.add_working(
                        f"Used tool {func_name}",
                        tool=func_name,
                        result=result
                    )
        
        # Max iterations reached
        self.logger.warning(f"Max iterations ({max_iter}) reached")
        final_response = "I've reached the maximum number of iterations. Here's what I've accomplished so far:\n\n"
        
        # Get last assistant message
        for msg in reversed(self.messages):
            if msg.role == "assistant" and msg.content:
                final_response += msg.content
                break
        
        if self.memory:
            self.memory.save_conversation(self.messages, self.session_id)
        
        return final_response
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for agent."""
        prompt = """You are Lumina, an autonomous AI agent designed to help users accomplish tasks.

You have access to various tools that you can use to complete tasks. Think step by step:

1. Analyze the task and break it down if needed
2. Use the appropriate tools to gather information or perform actions
3. Synthesize results and provide clear, helpful responses
4. If a task requires multiple steps, work through them systematically

Available tools:
"""
        
        for tool_name in self.tools.list_tools():
            tool = self.tools.get(tool_name)
            prompt += f"\n- {tool.name}: {tool.description}"
        
        prompt += """

Guidelines:
- Be thorough but concise
- Use tools when they would be helpful
- Explain your reasoning
- If you're unsure, ask for clarification
- Focus on delivering practical, actionable results
"""
        
        # Add memory context if available
        if self.memory:
            facts = self.memory.long_term_data.get("facts", [])
            if facts:
                prompt += "\n\nRelevant facts from memory:\n"
                for fact in facts[-5:]:  # Last 5 facts
                    prompt += f"- {fact['fact']}\n"
        
        return prompt
    
    async def chat(self, message: str) -> str:
        """Simple chat interface (no tools, just conversation).
        
        Args:
            message: User message
        
        Returns:
            Assistant response
        """
        self.messages.append(Message(role="user", content=message))
        
        if self.memory:
            self.memory.add_short_term(message, type="conversation", role="user")
        
        response = await self.llm.chat(
            messages=self.messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens
        )
        
        self.messages.append(Message(role="assistant", content=response.content))
        
        if self.memory:
            self.memory.add_short_term(
                response.content,
                type="conversation",
                role="assistant"
            )
        
        return response.content
    
    def reset(self) -> None:
        """Reset agent state."""
        self.messages = []
        self.iteration_count = 0
        self.session_id = str(uuid.uuid4())
        if self.memory:
            self.memory.clear_working()
        self.logger.info("Agent state reset")
