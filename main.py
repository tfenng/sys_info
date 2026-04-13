from __future__ import annotations

import argparse
import time

import psutil

from common import clear_screen, format_duration, format_timestamp, print_separator
from disk import get_root_disk_summary, render_disk_details
from load import format_loadavg, get_cpu_summary, render_load_details
from net import get_network_summary, render_network_details
from processes import main as run_process_list
from up_interfaces import render_network_interfaces
from users import get_online_user_summary, render_user_details


def get_process_summary() -> str:
    return f"{len(psutil.pids())} running"


def render_overview(clear: bool = True, show_menu: bool = True) -> None:
    if clear:
        clear_screen()

    print("System Info")
    print_separator("=")
    print(
        "CPU      : "
        f"{psutil.cpu_count(logical=False) or 0} cores / {psutil.cpu_count() or 0} threads"
    )
    print(f"CPU Freq : {get_cpu_summary()}")
    print(f"CPU Use  : {psutil.cpu_percent(interval=0.2):.1f}%")
    print(f"Load Avg : {format_loadavg()}")
    print_separator()

    memory = psutil.virtual_memory()
    print(
        "Memory   : "
        f"{memory.used / (1024 ** 3):.2f} GiB / {memory.total / (1024 ** 3):.2f} GiB "
        f"({memory.percent:.1f}%)"
    )
    print(f"Disk     : {get_root_disk_summary()}")
    print(f"Network  : {get_network_summary()}")
    print(f"Users    : {get_online_user_summary()}")
    print(f"Processes: {get_process_summary()}")
    print_separator()

    boot_time = psutil.boot_time()
    print(f"Boot Time: {format_timestamp(boot_time)}")
    print(f"Uptime   : {format_duration(time.time() - boot_time)}")

    if show_menu:
        print_separator("=")
        print("[1] Users details     [2] Load details   [3] Disk details   [4] Network details")
        print("[5] Network interfaces (UP)")
        print("[R] Refresh           [Q] Quit")


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
