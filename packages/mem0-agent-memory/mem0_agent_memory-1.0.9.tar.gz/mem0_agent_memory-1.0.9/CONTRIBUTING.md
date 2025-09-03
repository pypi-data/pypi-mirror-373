# Contributing to Mem0 Agent Memory

Thank you for your interest in contributing to Mem0 Agent Memory! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/mem0-agent-memory.git`
3. Create a virtual environment: `uv sync`
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

```bash
# Clone the repository
git clone https://github.com/arunkse/mem0-agent-memory.git
cd mem0-agent-memory

# Install dependencies
uv sync

# Run the server
uv run python mem0_agent_memory.py
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Keep functions focused and well-documented
- Add docstrings for all public functions

## Testing

Before submitting a pull request:
1. Test the MCP server with a client
2. Verify all tools work correctly
3. Test with different backends (FAISS, OpenSearch, Mem0 Platform)

## Submitting Changes

1. Create a descriptive commit message
2. Push to your fork
3. Create a pull request with:
   - Clear description of changes
   - Any relevant issue numbers
   - Testing performed

## Reporting Issues

When reporting issues, please include:
- Python version
- Operating system
- Error messages and stack traces
- Steps to reproduce
- Expected vs actual behavior

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
