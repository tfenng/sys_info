# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python system information utility using `psutil` to display:
- CPU count and frequency
- Memory usage
- Disk partitions and usage
- Network I/O statistics
- Online users
- System uptime

## Commands

```bash
# Install dependencies
poetry install

# Run the main script
python main.py

# Run individual modules directly
python net_io.py
python process_list.py
python uptime.py
python users.py
```

## Architecture

- `main.py` - Aggregator script that prints all system info sections
- `uptime.py` - Calculates and displays system boot time and uptime duration
- `users.py` - Lists currently online users via `psutil.users()`
- `net_io.py` - Standalone network I/O and connection stats
- `process_list.py` - Lists running processes with PID, username, and name

Modules use `psutil` for cross-platform system calls and `datetime` for time calculations.
