from __future__ import annotations

import time

import psutil

from common import clear_screen, format_duration, format_timestamp, print_separator
from disk import get_root_disk_summary
from load import format_loadavg, get_cpu_summary
from network import get_network_summary
from users import get_online_user_summary


def get_process_summary() -> str:
    return f"{len(psutil.pids())} running"


def render_sensor_summary() -> None:
    temperatures = {}
    battery = None

    try:
        temperatures = psutil.sensors_temperatures()
    except (AttributeError, NotImplementedError):
        temperatures = {}

    try:
        battery = psutil.sensors_battery()
    except (AttributeError, NotImplementedError):
        battery = None

    if not temperatures:
        print("Temp     : N/A")
    else:
        values = []
        for sensor_name, entries in sorted(temperatures.items()):
            for entry in entries:
                label = entry.label or sensor_name
                values.append(f"{label} {entry.current:.1f}C")
        print(f"Temp     : {'; '.join(values)}")

    if battery is None:
        print("Battery  : N/A")
        return

    status = "charging" if battery.power_plugged else "discharging"
    if battery.percent is None:
        print(f"Battery  : {status}")
        return

    secsleft = getattr(battery, "secsleft", None)
    if secsleft is None or secsleft in {
        getattr(psutil, "POWER_TIME_UNKNOWN", object()),
        getattr(psutil, "POWER_TIME_UNLIMITED", object()),
    }:
        eta = "n/a"
    else:
        eta = format_duration(secsleft)
    print(f"Battery  : {battery.percent:.1f}% {status}, eta {eta}")


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
    render_sensor_summary()

    if show_menu:
        print_separator("=")
        print("[1] Users details     [2] Load details   [3] Disk details   [4] Network details")
        print("[5] Network interfaces (UP)")
        print("[R] Refresh           [Q] Quit")


def main() -> None:
    render_overview(clear=False, show_menu=False)


if __name__ == "__main__":
    main()
