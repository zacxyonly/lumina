"""Configuration management for Lumina."""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class LuminaConfig:
    """Lumina configuration settings."""
    
    # LLM Provider settings
    provider: str = "openai"
    model: str = "gpt-4-turbo-preview"
    temperature: float = 0.7
    max_tokens: int = 4000
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    
    # Agent settings
    max_iterations: int = 10
    verbose: bool = True
    debug: bool = False
    
    # Paths
    project_root: Path = field(default_factory=lambda: Path.cwd())
    log_dir: Path = field(default_factory=lambda: Path.cwd() / "logs")
    memory_dir: Path = field(default_factory=lambda: Path.cwd() / "memory")
    
    # Memory settings
    enable_memory: bool = True
    memory_retention_days: int = 30
    
    # Security
    allow_code_execution: bool = True
    sandbox_code: bool = True
    max_file_size_mb: int = 10
    
    @classmethod
    def from_env(cls) -> "LuminaConfig":
        """Load configuration from environment variables."""
        return cls(
            provider=os.getenv("LUMINA_PROVIDER", "openai"),
            model=os.getenv("LUMINA_MODEL", "gpt-4-turbo-preview"),
            temperature=float(os.getenv("LUMINA_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LUMINA_MAX_TOKENS", "4000")),
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            groq_api_key=os.getenv("GROQ_API_KEY"),
            max_iterations=int(os.getenv("LUMINA_MAX_ITERATIONS", "10")),
            verbose=os.getenv("LUMINA_VERBOSE", "true").lower() == "true",
            debug=os.getenv("LUMINA_DEBUG", "false").lower() == "true",
            enable_memory=os.getenv("LUMINA_ENABLE_MEMORY", "true").lower() == "true",
            allow_code_execution=os.getenv("LUMINA_ALLOW_CODE_EXEC", "true").lower() == "true",
        )
    
    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """Get API key for the specified provider."""
        provider = provider or self.provider
        key_map = {
            "openai": self.openai_api_key,
            "anthropic": self.anthropic_api_key,
            "google": self.google_api_key,
            "groq": self.groq_api_key,
        }
        return key_map.get(provider.lower())
    
    def validate(self) -> bool:
        """Validate configuration."""
        api_key = self.get_api_key()
        if not api_key:
            raise ValueError(f"API key not found for provider: {self.provider}")
        
        # Create required directories
        self.log_dir.mkdir(parents=True, exist_ok=True)
        if self.enable_memory:
            self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        return True


# Global config instance
_config: Optional[LuminaConfig] = None


def get_config() -> LuminaConfig:
    """Get or create global config instance."""
    global _config
    if _config is None:
        _config = LuminaConfig.from_env()
    return _config


def set_config(config: LuminaConfig) -> None:
    """Set global config instance."""
    global _config
    _config = config
