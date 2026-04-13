from __future__ import annotations

import psutil

from common import format_bytes, print_separator, render_detail_header


def get_root_disk_summary() -> str:
    usage = psutil.disk_usage("/")
    return f"{format_bytes(usage.used)} / {format_bytes(usage.total)} ({usage.percent:.1f}%)"


def render_disk_details(clear: bool = True) -> None:
    render_detail_header("Disk Details", clear=clear)
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
    disk_stats = psutil.disk_io_counters(perdisk=True)
    sorted_items = sorted(
        disk_stats.items(),
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


def main() -> None:
    render_disk_details(clear=False)


if __name__ == "__main__":
    main()
