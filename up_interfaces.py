from __future__ import annotations

import socket

import psutil

from common import format_bytes, print_separator, render_detail_header


def render_network_interfaces(clear: bool = True) -> None:
    render_detail_header("Network Interfaces", clear=clear)
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


def main() -> None:
    render_network_interfaces(clear=False)


if __name__ == "__main__":
    main()
