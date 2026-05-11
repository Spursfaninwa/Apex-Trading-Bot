from apex.core.logger import get_logger

log = get_logger()


VALID_EXECUTION_MODES = {
    "scan_only",
    "paper_trade",
    "live_trade",
}


def get_execution_mode(config) -> str:
    if isinstance(config, dict):
        mode = config.get("execution", {}).get("mode", "scan_only")
    else:
        mode = getattr(
            getattr(config, "execution", None),
            "mode",
            "scan_only",
        )

    if mode not in VALID_EXECUTION_MODES:
        log.warning(
            f"Invalid execution mode '{mode}'. Defaulting to scan_only."
        )
        return "scan_only"

    return mode


def can_place_orders(config) -> bool:
    mode = get_execution_mode(config)

    if mode == "scan_only":
        log.info("Execution mode is scan_only. No orders will be placed.")
        return False

    if mode == "paper_trade":
        log.info("Execution mode is paper_trade. Paper orders are allowed.")
        return True

    if mode == "live_trade":
        log.warning("Execution mode is live_trade.")
        return True

    return False


def execution_allowed(config) -> bool:
    return can_place_orders(config)
