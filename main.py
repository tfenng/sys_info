from __future__ import annotations

from collections import Counter
from datetime import datetime
import socket
import time

import psutil


def clear_screen() -> None:
    print("\033[2J\033[H", end="")


def print_separator(char: str = "-") -> None:
    print(char * 80)


def format_bytes(num: float) -> str:
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    value = float(num)
    for unit in units:
        if abs(value) < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{value:.2f} PiB"


def format_timestamp(ts: float) -> str:
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


def format_duration(seconds: float) -> str:
    remaining = int(seconds)
    days, remaining = divmod(remaining, 86400)
    hours, remaining = divmod(remaining, 3600)
    minutes, seconds = divmod(remaining, 60)
    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if seconds or not parts:
        parts.append(f"{seconds}s")
    return " ".join(parts)


def truncate_text(value: object, width: int) -> str:
    text = str(value)
    if len(text) <= width:
        return text
    return text[: max(0, width - 3)] + "..."


def format_loadavg() -> str:
    try:
        load1, load5, load15 = psutil.getloadavg()
    except (AttributeError, OSError):
        return "N/A"
    return f"{load1:.2f} / {load5:.2f} / {load15:.2f}"


def get_cpu_summary() -> str:
    freq = psutil.cpu_freq()
    if freq is None:
        return "freq N/A"
    return f"{freq.current:.2f} GHz (min {freq.min:.2f} / max {freq.max:.2f})"


def get_root_disk_summary() -> str:
    usage = psutil.disk_usage("/")
    return f"{format_bytes(usage.used)} / {format_bytes(usage.total)} ({usage.percent:.1f}%)"


def get_network_summary() -> str:
    counters = psutil.net_io_counters()
    return f"recv {format_bytes(counters.bytes_recv)} / send {format_bytes(counters.bytes_sent)}"


def get_online_user_summary() -> str:
    active_users = psutil.users()
    if not active_users:
        return "0 online"
    unique_names = sorted({user.name for user in active_users})
    return f"{len(active_users)} sessions ({', '.join(unique_names)})"


def get_process_summary() -> str:
    return f"{len(psutil.pids())} running"


def render_overview() -> None:
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
        f"{format_bytes(memory.used)} / {format_bytes(memory.total)} ({memory.percent:.1f}%)"
    )
    print(f"Disk     : {get_root_disk_summary()}")
    print(f"Network  : {get_network_summary()}")
    print(f"Users    : {get_online_user_summary()}")
    print(f"Processes: {get_process_summary()}")
    print_separator()
    boot_time = psutil.boot_time()
    print(f"Boot Time: {format_timestamp(boot_time)}")
    print(f"Uptime   : {format_duration(time.time() - boot_time)}")
    print_separator("=")
    print("[1] Users details     [2] Load details   [3] Disk details   [4] Network details")
    print("[5] Network interfaces (UP)")
    print("[R] Refresh           [Q] Quit")


def render_detail_header(title: str) -> None:
    clear_screen()
    print(title)
    print_separator("=")


def render_network_details() -> None:
    render_detail_header("Network Details")
    totals = psutil.net_io_counters()
    print(
        "Total I/O : "
        f"recv {format_bytes(totals.bytes_recv)} / send {format_bytes(totals.bytes_sent)}"
    )
    print(
        "Packets   : "
        f"recv {totals.packets_recv} / send {totals.packets_sent} / "
        f"err {totals.errin + totals.errout} / drop {totals.dropin + totals.dropout}"
    )

    print_separator()
    print("Per Interface Traffic")
    per_nic = psutil.net_io_counters(pernic=True)
    for nic_name in sorted(per_nic):
        counters = per_nic[nic_name]
        print(
            f"{nic_name:<12} recv {format_bytes(counters.bytes_recv):>12}  "
            f"send {format_bytes(counters.bytes_sent):>12}"
        )

    print_separator()
    print("Connection State Summary")
    try:
        connections = psutil.net_connections(kind="inet")
        state_counts = Counter(conn.status or "UNKNOWN" for conn in connections)
        for state, count in sorted(state_counts.items(), key=lambda item: (-item[1], item[0])):
            print(f"{state:<13} {count}")

        listeners = sorted(
            {
                f"{conn.laddr.ip}:{conn.laddr.port}"
                for conn in connections
                if conn.status == psutil.CONN_LISTEN and conn.laddr
            }
        )
        if listeners:
            print_separator()
            print("Listening Endpoints")
            for endpoint in listeners[:15]:
                print(endpoint)
            if len(listeners) > 15:
                print(f"... {len(listeners) - 15} more")
    except (psutil.AccessDenied, psutil.Error) as exc:
        print(f"Unable to read connection details without elevated privileges: {exc}")


def render_network_interfaces() -> None:
    render_detail_header("Network Interfaces")
    nic_addresses = psutil.net_if_addrs()
    nic_stats = psutil.net_if_stats()
    per_nic = psutil.net_io_counters(pernic=True)

    for nic_name in sorted(set(nic_addresses) | set(nic_stats) | set(per_nic)):
        stats = nic_stats.get(nic_name)
        counters = per_nic.get(nic_name)
        if stats is None or not stats.isup:
            continue

        speed = f"{stats.speed}Mb" if stats.speed > 0 else "n/a"
        print(f"{nic_name}: up, speed {speed}, mtu {stats.mtu}")

        if counters is not None:
            print(
                f"  traffic recv {format_bytes(counters.bytes_recv)} / "
                f"send {format_bytes(counters.bytes_sent)}"
            )

        for address in nic_addresses.get(nic_name, []):
            family = str(address.family)
            if address.family == socket.AF_INET:
                family = "IPv4"
            elif address.family == socket.AF_INET6:
                family = "IPv6"
            elif getattr(psutil, "AF_LINK", None) == address.family:
                family = "MAC"
            print(f"  {family:<7} {address.address}")
        print_separator()


def render_user_details() -> None:
    render_detail_header("Users Details")
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


def render_disk_details() -> None:
    render_detail_header("Disk Details")
    print("Mount Usage")
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            continue
        print(
            f"{partition.mountpoint:<24} "
            f"{format_bytes(usage.used):>10} / {format_bytes(usage.total):>10} "
            f"({usage.percent:>5.1f}%)  {partition.fstype or 'n/a'}"
        )

    print_separator()
    print("Disk I/O Counters")
    disk_io = psutil.disk_io_counters(perdisk=True)
    sorted_items = sorted(
        disk_io.items(),
        key=lambda item: item[1].read_bytes + item[1].write_bytes,
        reverse=True,
    )
    for disk_name, io_stats in sorted_items:
        busy_time = getattr(io_stats, "busy_time", None)
        busy_text = f"{busy_time} ms" if busy_time is not None else "n/a"
        print(
            f"{disk_name:<12} read {format_bytes(io_stats.read_bytes):>10}  "
            f"write {format_bytes(io_stats.write_bytes):>10}  "
            f"ops {io_stats.read_count + io_stats.write_count:<10} busy {busy_text}"
        )


def collect_process_snapshot(attr: str, needs_cpu_sample: bool = False) -> list[dict[str, object]]:
    processes = list(psutil.process_iter(["pid", "name", "username"]))
    if needs_cpu_sample:
        for proc in processes:
            try:
                proc.cpu_percent(None)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        time.sleep(0.2)

    records: list[dict[str, object]] = []
    for proc in processes:
        try:
            cpu_percent = proc.cpu_percent(None) if needs_cpu_sample else None
            memory_percent = proc.memory_percent()
            record = {
                "pid": proc.pid,
                "name": proc.info.get("name") or "-",
                "user": proc.info.get("username") or "-",
                "cpu_percent": cpu_percent if cpu_percent is not None else 0.0,
                "memory_percent": memory_percent,
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        records.append(record)

    return sorted(records, key=lambda item: float(item[attr]), reverse=True)[:10]


def render_process_table(title: str, rows: list[dict[str, object]], metric: str) -> None:
    print(title)
    if not rows:
        print("No process data available")
        return
    for row in rows:
        metric_value = float(row[metric])
        print(
            f"{int(row['pid']):>6}  "
            f"{metric_value:>6.1f}%  "
            f"{truncate_text(row['user'], 14):<14}  "
            f"{truncate_text(row['name'], 30)}"
        )


def render_load_details() -> None:
    render_detail_header("Load Details")
    boot_time = psutil.boot_time()
    print(f"Boot Time : {format_timestamp(boot_time)}")
    print(f"Uptime    : {format_duration(time.time() - boot_time)}")
    print(f"Load Avg  : {format_loadavg()}")

    print_separator()
    print(f"CPU Overall: {psutil.cpu_percent(interval=0.2):.1f}%")
    per_core = psutil.cpu_percent(interval=0.2, percpu=True)
    print("Per Core   : " + "  ".join(f"CPU{i}:{value:>5.1f}%" for i, value in enumerate(per_core)))

    cpu_time_breakdown = psutil.cpu_times_percent(interval=0.2)
    parts = [
        f"user {getattr(cpu_time_breakdown, 'user', 0.0):.1f}%",
        f"system {getattr(cpu_time_breakdown, 'system', 0.0):.1f}%",
        f"idle {getattr(cpu_time_breakdown, 'idle', 0.0):.1f}%",
    ]
    if hasattr(cpu_time_breakdown, "iowait"):
        parts.append(f"iowait {getattr(cpu_time_breakdown, 'iowait', 0.0):.1f}%")
    print("CPU Times  : " + "  ".join(parts))

    print_separator()
    render_process_table(
        "Top 10 By CPU",
        collect_process_snapshot("cpu_percent", needs_cpu_sample=True),
        "cpu_percent",
    )
    print_separator()
    render_process_table(
        "Top 10 By Memory",
        collect_process_snapshot("memory_percent"),
        "memory_percent",
    )


def show_detail_page(renderer) -> str:
    while True:
        renderer()
        print_separator("=")
        print("[B] Back   [R] Refresh   [Q] Quit")
        choice = input("> ").strip().lower()
        if choice == "b":
            return "back"
        if choice == "q":
            return "quit"
        if choice in {"", "r"}:
            continue


def main() -> None:
    while True:
        render_overview()
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


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBye")
