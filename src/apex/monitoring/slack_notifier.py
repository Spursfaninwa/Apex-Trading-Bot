import json
import os
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

from apex.core.logger import get_logger

log = get_logger()


def eastern_now():
    return datetime.now(
        ZoneInfo("America/New_York")
    ).strftime("%Y-%m-%d %I:%M %p ET")


def send_slack_message(message: str):
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")

    if not webhook_url:
        log.warning("SLACK_WEBHOOK_URL not set. Slack message skipped.")
        return False

    payload = {
        "text": message,
    }

    try:
        data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            webhook_url,
            data=data,
            headers={
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            if response.status == 200:
                log.info("Slack notification sent.")
                return True

            log.warning(f"Slack returned status: {response.status}")
            return False

    except Exception as e:
        log.warning(f"Slack notification failed: {e}")
        return False


def notify_apex_test():
    return send_slack_message(
        f":white_check_mark: *[APEX]* Slack test successful | {eastern_now()}"
    )


def notify_account_snapshot(account, positions, open_orders):
    lines = [
        f":bar_chart: *[APEX] Account Snapshot* | {eastern_now()}",
        f"Portfolio: *${float(account.portfolio_value):,.2f}*",
        f"Cash: ${float(account.cash):,.2f}",
        f"Buying Power: ${float(account.buying_power):,.2f}",
        f"Open Positions: {len(positions)}",
        f"Open Orders: {len(open_orders)}",
    ]

    for position in positions:
        unrealized_pl = float(position.unrealized_pl)
        emoji = (
            ":chart_with_upwards_trend:"
            if unrealized_pl >= 0
            else ":chart_with_downwards_trend:"
        )

        lines.append(
            f"{emoji} {position.symbol} | "
            f"Qty: {position.qty} | "
            f"Value: ${float(position.market_value):,.2f} | "
            f"P/L: ${unrealized_pl:+,.2f}"
        )

    return send_slack_message("\n".join(lines))


def notify_market_closed():
    return send_slack_message(
        f":crescent_moon: *[APEX]* Market closed | {eastern_now()} | No orders placed."
    )
