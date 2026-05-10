from apex.core.logger import get_logger

log = get_logger()


HIGH_CORRELATION_GROUPS = {
    "mega_cap_tech": {
        "AAPL",
        "MSFT",
        "GOOGL",
        "META",
        "AMZN",
        "NVDA",
        "QQQ",
    },
    "semiconductors": {
        "AMD",
        "NVDA",
    },
}


def get_symbol_group(symbol: str):
    for group_name, symbols in HIGH_CORRELATION_GROUPS.items():
        if symbol in symbols:
            return group_name

    return None


def correlation_blocked(symbol: str, open_symbols: list[str]) -> bool:
    symbol_group = get_symbol_group(symbol)

    if symbol_group is None:
        return False

    for open_symbol in open_symbols:
        if get_symbol_group(open_symbol) == symbol_group:
            log.info(
                f"Correlation block: {symbol} conflicts with "
                f"existing {open_symbol} in {symbol_group}"
            )
            return True

    return False
