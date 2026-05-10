from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from apex.execution.execution_guard import can_place_orders
from apex.portfolio.position_manager import already_holding_symbol
from apex.core.logger import get_logger

log = get_logger()


def submit_paper_order(client, config, trade_plan):
    if not can_place_orders(config):
        log.info("Order blocked by execution guard.")
        return None

    if not trade_plan.approved:
        log.info("Order blocked: trade plan not approved.")
        return None

    if already_holding_symbol(client, trade_plan.symbol):
        log.info(
            f"Order blocked: already holding {trade_plan.symbol}"
        )
        return None

    order = MarketOrderRequest(
        symbol=trade_plan.symbol,
        qty=trade_plan.shares,
        side=OrderSide.BUY,
        time_in_force=TimeInForce.DAY,
    )

    submitted = client.submit_order(order)

    log.info(f"Paper order submitted: {submitted.id}")
    log.info(f"{trade_plan.symbol} | Qty: {trade_plan.shares}")

    return submitted
