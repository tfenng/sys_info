from __future__ import annotations

import time
from collections.abc import Callable

import psutil

from common import format_duration, format_timestamp, print_separator, render_detail_header, truncate_text

TOP_N = 10
PROCESS_NAME_WIDTH = 40
DUAL_COLUMN_WIDTH = 57


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
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

        records.append(
            {
                "pid": proc.pid,
                "name": proc.info.get("name") or "-",
                "user": proc.info.get("username") or "-",
                "cpu_percent": cpu_percent if cpu_percent is not None else 0.0,
                "memory_percent": memory_percent,
            }
        )

    return sorted(records, key=lambda item: float(item[attr]), reverse=True)[:TOP_N]


def collect_process_metric(
    metric_name: str,
    getter: Callable[[psutil.Process], float],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for proc in psutil.process_iter(["pid", "name", "username"]):
        try:
            metric_value = getter(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError):
            continue

        rows.append(
            {
                "pid": proc.pid,
                "name": proc.info.get("name") or "-",
                "user": proc.info.get("username") or "-",
                metric_name: float(metric_value),
            }
        )

    rows.sort(key=lambda item: float(item[metric_name]), reverse=True)
    return rows[:TOP_N]


def format_process_row(
    row: dict[str, object],
    metric: str,
    suffix: str = "%",
    decimals: int = 1,
    name_width: int = PROCESS_NAME_WIDTH,
) -> str:
    metric_value = float(row[metric])
    metric_text = f"{metric_value:>{6}.{decimals}f}{suffix}"
    return (
        f"{int(row['pid']):>6} "
        f"{metric_text:>7} "
        f"{truncate_text(row['name'], name_width):<{name_width}}"
    )


def render_process_table(
    title: str,
    rows: list[dict[str, object]],
    metric: str,
    suffix: str = "%",
    decimals: int = 1,
) -> None:
    print(title)
    if not rows:
        print("No process data available")
        return

    for row in rows:
        print(
            f"{int(row['pid']):>6}  "
            f"{f'{float(row[metric]):>{6}.{decimals}f}{suffix}':>7}  "
            f"{truncate_text(row['user'], 14):<14}  "
            f"{truncate_text(row['name'], PROCESS_NAME_WIDTH)}"
        )


def render_dual_process_tables(
    left_title: str,
    left_rows: list[dict[str, object]],
    left_metric: str,
    right_title: str,
    right_rows: list[dict[str, object]],
    right_metric: str,
    left_suffix: str = "%",
    left_decimals: int = 1,
    right_suffix: str = "%",
    right_decimals: int = 1,
) -> None:
    column_width = DUAL_COLUMN_WIDTH
    print(f"{left_title:<{column_width}} {right_title}")
    total_rows = max(len(left_rows), len(right_rows))

    for index in range(total_rows):
        left_text = ""
        right_text = ""
        if index < len(left_rows):
            left_text = format_process_row(
                left_rows[index],
                left_metric,
                suffix=left_suffix,
                decimals=left_decimals,
                name_width=PROCESS_NAME_WIDTH,
            )
        if index < len(right_rows):
            right_text = format_process_row(
                right_rows[index],
                right_metric,
                suffix=right_suffix,
                decimals=right_decimals,
                name_width=PROCESS_NAME_WIDTH,
            )
        print(f"{left_text:<{column_width}} {right_text}")


def get_open_file_count(proc: psutil.Process) -> float:
    return float(len(proc.open_files()))


def get_thread_count(proc: psutil.Process) -> float:
    return float(proc.num_threads())


def render_load_details(clear: bool = True) -> None:
    render_detail_header("Load Details", clear=clear)
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
    render_dual_process_tables(
        f"Top {TOP_N} By CPU",
        collect_process_snapshot("cpu_percent", needs_cpu_sample=True),
        "cpu_percent",
        f"Top {TOP_N} By Memory",
        collect_process_snapshot("memory_percent"),
        "memory_percent",
    )
    print_separator()
    render_dual_process_tables(
        f"Top {TOP_N} By Threads",
        collect_process_metric("thread_count", get_thread_count),
        "thread_count",
        f"Top {TOP_N} By Open Files",
        collect_process_metric("open_file_count", get_open_file_count),
        "open_file_count",
        left_suffix="",
        left_decimals=0,
        right_suffix="",
        right_decimals=0,
    )


def main() -> None:
    render_load_details(clear=False)


if __name__ == "__main__":
    main()
