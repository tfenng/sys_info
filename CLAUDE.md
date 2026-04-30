# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python system information utility using `psutil` to display:
- Overview, load, disk, network, interfaces, users, and processes information

## Commands

```bash
# Install dependencies
uv sync

# Run the main script
uv run python main.py

# Run individual modules directly
uv run python overview.py
uv run python load.py
uv run python disk.py
uv run python network.py
uv run python interfaces.py
uv run python processes.py
uv run python users.py
```

## Architecture

- `main.py` - Entry point for interactive mode and subcommands
- `overview.py` - Overview and sensor information
- `load.py` - Load details and process top lists
- `disk.py` - Disk usage and disk I/O details
- `network.py` - Network I/O, connections, and listening ports
- `interfaces.py` - UP network interface details
- `users.py` - Lists currently online users via `psutil.users()`
- `processes.py` - Lists running processes with PID, username, and name

Modules use `psutil` for cross-platform system calls.
