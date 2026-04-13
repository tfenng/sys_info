from datetime import datetime
import time

import psutil


def boot_time() -> datetime:
    return datetime.fromtimestamp(psutil.boot_time())


def format_duration(seconds: float) -> str:
    remaining = int(seconds)
    days, remaining = divmod(remaining, 86400)
    hours, remaining = divmod(remaining, 3600)
    minutes, seconds = divmod(remaining, 60)

    parts: list[str] = []
    if days:
        parts.append(f"{days} days")
    if hours:
        parts.append(f"{hours} hours")
    if minutes:
        parts.append(f"{minutes} minutes")
    if seconds or not parts:
        parts.append(f"{seconds} seconds")
    return " ".join(parts)


def uptime_value() -> str:
    return format_duration(time.time() - psutil.boot_time())


def show() -> None:
    print(f"{boot_time().strftime('%Y-%m-%d %H:%M:%S')} up {uptime_value()}")


if __name__ == "__main__":
    show()
