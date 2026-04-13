from __future__ import annotations

from collections import Counter

import psutil

from common import format_bytes, print_separator, render_detail_header


def get_network_summary() -> str:
    counters = psutil.net_io_counters()
    return f"recv {format_bytes(counters.bytes_recv)} / send {format_bytes(counters.bytes_sent)}"


def render_network_details(clear: bool = True) -> None:
    render_detail_header("Network Details", clear=clear)
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
    for nic_name, counters in sorted(psutil.net_io_counters(pernic=True).items()):
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


def main() -> None:
    render_network_details(clear=False)


if __name__ == "__main__":
    main()
