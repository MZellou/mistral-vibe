# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mistral Vibe is an open-source CLI coding assistant powered by Mistral's models. It provides a conversational interface for exploring, modifying, and interacting with codebases through natural language.

## Development Commands

All commands use `uv` (never bare `python` or `pip`):

```bash
# Install dependencies
uv sync --all-extras

# Run the CLI from this repo
uv run vibe

# Run tests
uv run pytest
uv run pytest tests/test_agent_tool_call.py  # specific file
uv run pytest --ignore tests/snapshots       # skip snapshot tests

# Linting and formatting
uv run ruff check .           # lint
uv run ruff check --fix .     # auto-fix
uv run ruff format .          # format
uv run pyright                # type check

# Pre-commit (all checks)
uv run pre-commit run --all-files
```

## Architecture

### Entry Points
- `vibe.cli.entrypoint:main` - Interactive Textual-based TUI
- `vibe.acp.entrypoint:main` - Agent Client Protocol server for IDE integration

### Core Components
- **`vibe/core/agent.py`** - Main agent loop: user prompt → LLM call → tool execution → repeat
- **`vibe/core/config.py`** - TOML-based configuration, provider/model definitions
- **`vibe/core/llm/backend/`** - LLM backends: `mistral.py` (Mistral API), `generic.py` (OpenAI-compatible/vLLM)
- **`vibe/core/tools/`** - Tool system with `manager.py` orchestrating built-in tools (bash, read_file, write_file, search_replace, grep, todo)
- **`vibe/core/middleware.py`** - Context compaction, turn limits, price limits

### CLI/UI (`vibe/cli/`)
- **`textual_ui/`** - Textual TUI with widgets, handlers, renderers
- **`commands.py`** - Slash commands (`/clear`, `/config`, `/set-model`)
- **`autocompletion/`** - `@` for files, `/` for commands

### Configuration
- User config: `~/.vibe/config.toml`
- Project config: `.vibe/config.toml` (overrides user)
- API keys: `~/.vibe/.env`
- Custom prompts: `~/.vibe/prompts/`
- Custom agents: `~/.vibe/agents/`

## Code Style (from AGENTS.md)

- Python 3.12+ with modern type hints (`list`, `dict`, `|` instead of `Optional`/`Union`)
- Match-case over if/elif chains
- "Never nester" - use early returns and guard clauses
- Pathlib for file operations
- Pydantic v2 for validation
- No inline `# type: ignore` or `# noqa` - fix at source
- Strong static typing compatible with Pyright
