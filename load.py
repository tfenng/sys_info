from __future__ import annotations

import time

import psutil

from common import format_duration, format_timestamp, print_separator, render_detail_header, truncate_text


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


def main() -> None:
    render_load_details(clear=False)


if __name__ == "__main__":
    main()
