# Changelog

All notable changes to Lumina will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-03-17

### Added
- Initial release of Lumina framework
- Core agent system with autonomous task execution
- LLM provider abstraction (OpenAI, Anthropic)
- Tool system with extensible plugin architecture
- Memory management system (short-term, working, long-term)
- File operation tools (read, write, list, search)
- Rich CLI interface with interactive mode
- Configuration management via environment variables
- Structured logging with Rich formatting
- Comprehensive documentation
- Example usage scripts
- Unit test suite

### Features
- **Agent System**: Autonomous task planning and execution
- **Multi-Provider Support**: OpenAI and Anthropic Claude
- **Tool Registry**: Easy registration and management of custom tools
- **Memory System**: Context-aware conversations with persistence
- **CLI Interface**: Both interactive and single-command modes
- **Type Safety**: Full type hints throughout codebase
- **Async Architecture**: High-performance async/await patterns

### Tools Included
- `read_file`: Read file contents
- `write_file`: Write or append to files
- `list_directory`: List directory contents (recursive option)
- `search_files`: Search files by glob pattern

### Documentation
- Comprehensive README with examples
- API documentation in docstrings
- Configuration guide
- Example scripts
- MIT License

## [1.1.0] - 2026-03-17

### Added
- Interactive setup wizard (`python -m lumina.wizard`)
- Multi-LLM support via LiteLLM provider
- Support for OpenAI, Anthropic, Google, Groq, and 100+ other providers
- Enhanced CLI with `--setup` and `--wizard` flags
- Improved error messages with actionable guidance
- Configuration validation and testing in wizard

### Changed
- Updated QUICKSTART.md to recommend setup wizard
- Enhanced error messages in config validation
- Better provider detection and handling

### Fixed
- API key validation now provides helpful error messages
- Missing environment variable handling with suggestions

## [Unreleased]

### Planned for v1.1.0
- GUI interface (web-based)
- Additional tools (web browsing, calculator, code execution)
- Streaming responses in CLI
- Enhanced memory retrieval with semantic search
- Tool usage analytics

### Planned for v1.2.0
- Multi-agent collaboration
- Agent workflows and pipelines
- Custom agent personas
- Voice interface support

### Planned for v2.0.0
- Plugin marketplace
- Cloud deployment options
- Agent templates library
- Advanced observability and monitoring
