from apex.core.logger import get_logger

log = get_logger()


def show_account_snapshot(client):
    log.info("===== ACCOUNT SNAPSHOT =====")

    try:
        account = client.get_account()

        log.info(f"Portfolio Value: ${float(account.portfolio_value):.2f}")
        log.info(f"Cash: ${float(account.cash):.2f}")
        log.info(f"Buying Power: ${float(account.buying_power):.2f}")
        log.info(f"Equity: ${float(account.equity):.2f}")

    except Exception as e:
        log.warning(f"Failed to retrieve account snapshot: {e}")

    try:
        positions = client.get_all_positions()

        log.info(f"Open Positions: {len(positions)}")

        if not positions:
            log.info("No open positions.")

        for position in positions:
            log.info(
                f"POSITION | "
                f"{position.symbol} | "
                f"Qty: {position.qty} | "
                f"Market Value: ${float(position.market_value):.2f} | "
                f"Unrealized P/L: ${float(position.unrealized_pl):.2f}"
            )

    except Exception as e:
        log.warning(f"Failed to retrieve positions: {e}")

    try:
        orders = client.get_orders()

        log.info(f"Open Orders: {len(orders)}")

        if not orders:
            log.info("No open orders.")

        for order in orders:
            log.info(
                f"ORDER | "
                f"{order.symbol} | "
                f"{order.side} | "
                f"Qty: {order.qty} | "
                f"Status: {order.status}"
            )

    except Exception as e:
        log.warning(f"Failed to retrieve orders: {e}")

    log.info("============================")