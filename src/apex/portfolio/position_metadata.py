import json
from datetime import datetime, timezone
from pathlib import Path

from apex.core.logger import get_logger

log = get_logger()

METADATA_PATH = Path("data/position_metadata.json")


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def load_position_metadata():
    if not METADATA_PATH.exists():
        return {}

    try:
        with METADATA_PATH.open("r") as file:
            return json.load(file)
    except Exception as e:
        log.warning(f"Could not load position metadata: {e}")
        return {}


def save_position_metadata(metadata):
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    with METADATA_PATH.open("w") as file:
        json.dump(metadata, file, indent=2, sort_keys=True)


def reconcile_position_metadata(positions, source="UNKNOWN"):
    metadata = load_position_metadata()
    live_symbols = set()

    for position in positions:
        symbol = position.symbol
        live_symbols.add(symbol)

        current_price = float(position.current_price)
        entry_price = float(position.avg_entry_price)

        if symbol not in metadata:
            metadata[symbol] = {
                "symbol": symbol,
                "source": source,
                "strategy": "legacy" if source != "APEX" else "momentum",
                "intent": "Imported from live broker position",
                "entry_date": utc_now(),
                "entry_price": entry_price,
                "entry_score": None,
                "confidence_score": None,
                "entry_regime": None,
                "initial_stop": None,
                "target_price": None,
                "max_hold_days": 20,
                "last_validated": utc_now(),
                "high_watermark": current_price,
                "status": "OPEN",
            }

            log.info(f"Position metadata created for {symbol}")

        else:
            existing_high = float(metadata[symbol].get("high_watermark", current_price))

            metadata[symbol]["last_validated"] = utc_now()
            metadata[symbol]["status"] = "OPEN"
            metadata[symbol]["high_watermark"] = max(existing_high, current_price)

    for symbol, record in metadata.items():
        if symbol not in live_symbols and record.get("status") == "OPEN":
            record["status"] = "CLOSED"
            record["last_validated"] = utc_now()
            log.info(f"Position metadata marked closed for {symbol}")

    save_position_metadata(metadata)
    return metadata


def record_apex_entry(
    symbol,
    entry_price,
    entry_score,
    initial_stop,
    target_price=None,
    confidence_score=8,
    entry_regime=None,
):
    metadata = load_position_metadata()

    metadata[symbol] = {
        "symbol": symbol,
        "source": "APEX",
        "strategy": "momentum",
        "intent": "Persistent momentum entry approved by Apex governance",
        "entry_date": utc_now(),
        "entry_price": float(entry_price),
        "entry_score": entry_score,
        "confidence_score": confidence_score,
        "entry_regime": entry_regime,
        "initial_stop": float(initial_stop) if initial_stop is not None else None,
        "target_price": target_price,
        "max_hold_days": 20,
        "last_validated": utc_now(),
        "high_watermark": float(entry_price),
        "status": "OPEN",
    }

    save_position_metadata(metadata)
    log.info(f"Apex entry metadata recorded for {symbol}")


def show_position_metadata_summary():
    metadata = load_position_metadata()

    log.info("===== POSITION METADATA SUMMARY =====")

    if not metadata:
        log.info("No position metadata found.")
        log.info("=====================================")
        return metadata

    for symbol, record in metadata.items():
        log.info(
            f"{symbol} | "
            f"Source: {record.get('source')} | "
            f"Strategy: {record.get('strategy')} | "
            f"Status: {record.get('status')} | "
            f"High Watermark: {record.get('high_watermark')}"
        )

    log.info("=====================================")
    return metadata
