"""Unit tests for Lumina core components."""

import pytest
from pathlib import Path
from lumina.utils.config import LuminaConfig
from lumina.core.llm import Message
from lumina.tools.base import Tool, ToolParameter, ToolRegistry


class TestConfig:
    """Test configuration management."""
    
    def test_config_creation(self):
        """Test creating config with defaults."""
        config = LuminaConfig()
        assert config.provider == "openai"
        assert config.temperature == 0.7
        assert config.max_iterations == 10
    
    def test_config_validation(self):
        """Test config validation requires API key."""
        config = LuminaConfig(openai_api_key=None)
        with pytest.raises(ValueError, match="API key not found"):
            config.validate()
    
    def test_get_api_key(self):
        """Test getting API key for provider."""
        config = LuminaConfig(
            openai_api_key="test-key-1",
            anthropic_api_key="test-key-2"
        )
        assert config.get_api_key("openai") == "test-key-1"
        assert config.get_api_key("anthropic") == "test-key-2"


class TestMessage:
    """Test message structure."""
    
    def test_message_creation(self):
        """Test creating message."""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name is None


class TestToolSystem:
    """Test tool system."""
    
    def test_tool_parameter(self):
        """Test tool parameter creation."""
        param = ToolParameter(
            name="test",
            type="string",
            description="A test parameter",
            required=True
        )
        assert param.name == "test"
        assert param.type == "string"
        assert param.required is True
    
    def test_tool_registry(self):
        """Test tool registration."""
        registry = ToolRegistry()
        
        class TestTool(Tool):
            name = "test_tool"
            description = "A test tool"
            
            async def execute(self, **kwargs):
                return {"status": "success"}
        
        tool = TestTool()
        registry.register(tool)
        
        assert "test_tool" in registry.list_tools()
        assert registry.get("test_tool") is not None
    
    def test_tool_unregister(self):
        """Test tool unregistration."""
        registry = ToolRegistry()
        
        class TestTool(Tool):
            name = "test_tool"
            description = "A test tool"
            
            async def execute(self, **kwargs):
                return {"status": "success"}
        
        tool = TestTool()
        registry.register(tool)
        registry.unregister("test_tool")
        
        assert "test_tool" not in registry.list_tools()
    
    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test executing a tool."""
        class CalculatorTool(Tool):
            name = "calculator"
            description = "Simple calculator"
            parameters = [
                ToolParameter("a", "number", "First number", True),
                ToolParameter("b", "number", "Second number", True),
            ]
            
            async def execute(self, a: int, b: int, **kwargs):
                return {"status": "success", "result": a + b}
        
        tool = CalculatorTool()
        result = await tool.run(a=5, b=3)
        
        assert result["status"] == "success"
        assert result["result"] == 8
    
    @pytest.mark.asyncio
    async def test_tool_validation(self):
        """Test tool parameter validation."""
        class TestTool(Tool):
            name = "test"
            description = "Test"
            parameters = [
                ToolParameter("required_param", "string", "Required", True)
            ]
            
            async def execute(self, **kwargs):
                return {"status": "success"}
        
        tool = TestTool()
        
        with pytest.raises(ValueError, match="Missing required parameter"):
            await tool.run()


class TestMemory:
    """Test memory system."""
    
    def test_memory_creation(self, tmp_path):
        """Test creating memory system."""
        from lumina.core.memory import Memory
        
        memory = Memory(tmp_path, max_short_term=5)
        assert memory.memory_dir == tmp_path
        assert len(memory.short_term) == 0
    
    def test_add_short_term(self, tmp_path):
        """Test adding to short-term memory."""
        from lumina.core.memory import Memory
        
        memory = Memory(tmp_path, max_short_term=5)
        memory.add_short_term("Test memory")
        
        assert len(memory.short_term) == 1
        assert memory.short_term[0].content == "Test memory"
    
    def test_add_fact(self, tmp_path):
        """Test adding fact to long-term memory."""
        from lumina.core.memory import Memory
        
        memory = Memory(tmp_path)
        memory.add_fact("Python is awesome", category="programming")
        
        assert len(memory.long_term_data["facts"]) == 1
        assert memory.long_term_data["facts"][0]["fact"] == "Python is awesome"
    
    def test_preferences(self, tmp_path):
        """Test user preferences."""
        from lumina.core.memory import Memory
        
        memory = Memory(tmp_path)
        memory.set_preference("language", "python")
        
        assert memory.get_preference("language") == "python"
        assert memory.get_preference("nonexistent", "default") == "default"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
