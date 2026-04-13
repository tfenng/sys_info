from __future__ import annotations

import psutil

from common import format_timestamp, print_separator, render_detail_header


def get_online_user_summary() -> str:
    active_users = psutil.users()
    if not active_users:
        return "0 online"
    unique_names = sorted({user.name for user in active_users})
    return f"{len(active_users)} sessions ({', '.join(unique_names)})"


def render_user_details(clear: bool = True) -> None:
    render_detail_header("Users Details", clear=clear)
    active_users = psutil.users()
    if not active_users:
        print("No active user sessions")
        return

    print(f"Active Sessions: {len(active_users)}")
    print_separator()
    for user in active_users:
        terminal = user.terminal or "-"
        host = user.host or "local"
        pid = user.pid if user.pid is not None else "-"
        started = format_timestamp(user.started) if user.started else "-"
        print(
            f"user {user.name:<14} terminal {terminal:<10} host {host:<15} "
            f"pid {pid:<8} started {started}"
        )


def main() -> None:
    render_user_details(clear=False)


if __name__ == "__main__":
    main()
