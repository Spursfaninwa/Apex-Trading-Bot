from apex.core.logger import get_logger

log = get_logger()


def get_open_positions(client):

    try:

        positions = client.get_all_positions()

        symbols = [p.symbol for p in positions]

        log.info(f"Open positions: {symbols}")

        return symbols

    except Exception as e:

        log.error(f"Failed to retrieve positions: {e}")

        return []


def already_holding_symbol(client, symbol: str) -> bool:

    positions = get_open_positions(client)

    return symbol in positions
