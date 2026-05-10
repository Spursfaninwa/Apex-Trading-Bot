from apex.core.logger import get_logger

log = get_logger()


def can_place_orders(config) -> bool:
    mode = getattr(config, "execution", None)

    if mode is None:
        log.warning("Execution config missing. Defaulting to scan_only.")
        return False

    execution_mode = getattr(mode, "mode", "scan_only")

    if execution_mode == "scan_only":
        log.info("Execution mode is scan_only. No orders will be placed.")
        return False

    if execution_mode == "paper_trade":
        log.info("Execution mode is paper_trade. Paper orders allowed.")
        return True

    if execution_mode == "live_trade":
        log.warning("Execution mode is live_trade. Live orders allowed.")
        return True

    log.warning(f"Unknown execution mode: {execution_mode}. Blocking orders.")
    return False
