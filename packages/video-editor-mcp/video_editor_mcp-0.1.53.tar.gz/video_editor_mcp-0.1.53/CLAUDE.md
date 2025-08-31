# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands
- Build: `uv build`
- Lint: `ruff --fix .`
- Format: `ruff format .`
- Run: `uv run video-editor-mcp YOURAPIKEY`
- With Photos access: `LOAD_PHOTOS_DB=1 uv run video-editor-mcp YOURAPIKEY`
- Debug logs: `tail -n 90 -f app.log`
- Debug with inspector: `npx @modelcontextprotocol/inspector uv run --directory /path/to/repo video-editor-mcp YOURAPIKEY`

## Style Guide
- Python version: 3.11+
- Formatting: Ruff formatter
- Imports: Group standard library, third-party, and local imports
- Types: Use typing annotations for function parameters and return values
- Error handling: Use specific exceptions with descriptive messages
- Naming: Snake case for functions/variables, PascalCase for classes
- Comments: Use docstrings for functions describing args, returns, and raises