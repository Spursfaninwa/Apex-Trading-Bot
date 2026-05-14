import json
from datetime import datetime, timezone
from pathlib import Path

from apex.core.logger import get_logger
from apex.monitoring.slack_notifier import send_slack_message

log = get_logger()

SUPPRESSION_PATH = Path("data/suppression_log.json")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_suppression_log():
    if not SUPPRESSION_PATH.exists():
        return {}

    try:
        with SUPPRESSION_PATH.open("r") as file:
            return json.load(file)
    except Exception as e:
        log.warning(f"Could not load suppression log: {e}")
        return {}


def save_suppression_log(records):
    SUPPRESSION_PATH.parent.mkdir(parents=True, exist_ok=True)

    with SUPPRESSION_PATH.open("w") as file:
        json.dump(records, file, indent=2, sort_keys=True)


def severity_for_count(count):
    if count >= 5:
        return "OPERATIONAL_BLINDNESS_RISK"

    if count >= 3:
        return "SLACK_WARNING"

    if count >= 2:
        return "LOG"

    return "OBSERVE"


def record_suppression(source, symbol, signal_type, reason):
    records = load_suppression_log()
    key = f"{source}:{symbol}:{signal_type}"

    if key not in records:
        records[key] = {
            "source": source,
            "symbol": symbol,
            "signal_type": signal_type,
            "first_seen": utc_now(),
            "last_seen": utc_now(),
            "count": 1,
            "last_reason": reason,
            "severity": "OBSERVE",
            "status": "SUPPRESSED",
        }
    else:
        records[key]["count"] += 1
        records[key]["last_seen"] = utc_now()
        records[key]["last_reason"] = reason

    count = records[key]["count"]
    severity = severity_for_count(count)
    records[key]["severity"] = severity

    save_suppression_log(records)

    log.info(
        f"Suppression recorded | {key} | "
        f"Count: {count} | Severity: {severity}"
    )

    if count == 3:
        send_slack_message(
            ":warning: *[APEX] Repeated Signal Suppression*\n"
            f"Source: {source}\n"
            f"Symbol: {symbol}\n"
            f"Signal: {signal_type}\n"
            f"Count: {count}\n"
            f"Reason: {reason}"
        )

    if count == 5:
        send_slack_message(
            ":rotating_light: *[APEX] Operational Blindness Risk*\n"
            f"Source: {source}\n"
            f"Symbol: {symbol}\n"
            f"Signal: {signal_type}\n"
            f"Count: {count}\n"
            f"Repeated invalid signal may be masking useful alerts.\n"
            f"Reason: {reason}"
        )

    return records[key]


def resolve_suppression(source, symbol, signal_type):
    records = load_suppression_log()
    key = f"{source}:{symbol}:{signal_type}"

    if key in records:
        records[key]["status"] = "RESOLVED"
        records[key]["last_seen"] = utc_now()
        save_suppression_log(records)
        log.info(f"Suppression resolved | {key}")

    return records.get(key)


def show_suppression_summary():
    records = load_suppression_log()

    log.info("===== SUPPRESSION SUMMARY =====")

    if not records:
        log.info("No suppressed signals recorded.")
        log.info("===============================")
        return records

    for key, record in records.items():
        log.info(
            f"{key} | "
            f"Count: {record.get('count')} | "
            f"Severity: {record.get('severity')} | "
            f"Status: {record.get('status')} | "
            f"Reason: {record.get('last_reason')}"
        )

    log.info("===============================")
    return records
