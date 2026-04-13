from __future__ import annotations

import argparse

from disk import render_disk_details
from load import render_load_details
from net import render_network_details
from overview import render_overview
from processes import main as run_process_list
from up_interfaces import render_network_interfaces
from users import render_user_details


def show_detail_page(renderer) -> str:
    while True:
        renderer(clear=True)
        print_separator("=")
        print("[B] Back   [R] Refresh   [Q] Quit")
        choice = input("> ").strip().lower()
        if choice == "b":
            return "back"
        if choice == "q":
            return "quit"
        if choice in {"", "r"}:
            continue


def run_interactive() -> None:
    while True:
        render_overview(clear=True, show_menu=True)
        choice = input("> ").strip().lower()
        if choice in {"q", "quit"}:
            break
        if choice in {"", "r", "refresh"}:
            continue
        if choice == "1":
            result = show_detail_page(render_user_details)
            if result == "quit":
                break
        elif choice == "2":
            result = show_detail_page(render_load_details)
            if result == "quit":
                break
        elif choice == "3":
            result = show_detail_page(render_disk_details)
            if result == "quit":
                break
        elif choice == "4":
            result = show_detail_page(render_network_details)
            if result == "quit":
                break
        elif choice == "5":
            result = show_detail_page(render_network_interfaces)
            if result == "quit":
                break


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="System info CLI based on psutil")
    parser.add_argument(
        "command",
        nargs="?",
        choices=[
            "overview",
            "users",
            "load",
            "disk",
            "network",
            "interfaces",
            "processes",
        ],
        help="Run a specific report directly",
    )
    return parser


def run_command(command: str | None) -> None:
    if command is None:
        run_interactive()
        return

    handlers = {
        "overview": lambda: render_overview(clear=False, show_menu=False),
        "users": lambda: render_user_details(clear=False),
        "load": lambda: render_load_details(clear=False),
        "disk": lambda: render_disk_details(clear=False),
        "network": lambda: render_network_details(clear=False),
        "interfaces": lambda: render_network_interfaces(clear=False),
        "processes": run_process_list,
    }
    handlers[command]()


def main() -> None:
    args = build_parser().parse_args()
    run_command(args.command)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye")
