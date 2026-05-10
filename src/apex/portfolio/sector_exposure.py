from apex.core.logger import get_logger

log = get_logger()


SYMBOL_SECTORS = {
    "AAPL": "technology",
    "MSFT": "technology",
    "GOOGL": "communication_services",
    "META": "communication_services",
    "AMZN": "consumer_discretionary",
    "NVDA": "semiconductors",
    "AMD": "semiconductors",
    "TSLA": "consumer_discretionary",
    "QQQ": "technology_etf",
    "SPY": "broad_market",
}


def get_symbol_sector(symbol: str) -> str:
    return SYMBOL_SECTORS.get(symbol, "unknown")


def sector_exposure_blocked(
    symbol: str,
    open_symbols: list[str],
    max_same_sector_positions: int = 1,
) -> bool:
    sector = get_symbol_sector(symbol)

    if sector == "unknown":
        return False

    same_sector_count = 0

    for open_symbol in open_symbols:
        if get_symbol_sector(open_symbol) == sector:
            same_sector_count += 1

    log.info(
        f"{symbol} sector: {sector} | "
        f"existing sector positions: {same_sector_count}"
    )

    if same_sector_count >= max_same_sector_positions:
        log.info(
            f"Sector exposure block: {symbol} exceeds "
            f"{sector} limit"
        )
        return True

    return False
