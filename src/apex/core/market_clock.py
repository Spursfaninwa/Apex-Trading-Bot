from datetime import datetime, time
from zoneinfo import ZoneInfo


MARKET_TIMEZONE = ZoneInfo("America/New_York")

MARKET_OPEN = time(9, 30)
MARKET_CLOSE = time(16, 0)


def now_eastern():
    return datetime.now(MARKET_TIMEZONE)


def is_market_open():
    current = now_eastern()

    if current.weekday() >= 5:
        return False

    current_time = current.time()

    return MARKET_OPEN <= current_time < MARKET_CLOSE


def get_market_clock_summary():
    current = now_eastern()

    status = "OPEN" if is_market_open() else "CLOSED"

    return (
        f"Market clock: {status} | "
        f"Eastern time: {current.strftime('%Y-%m-%d %I:%M:%S %p %Z')}"
    )
