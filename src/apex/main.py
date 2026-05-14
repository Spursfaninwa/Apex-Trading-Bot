from apex.core.logger import get_logger
from apex.core.config import load_config
from apex.core.market_clock import (
    get_market_clock_summary,
    is_market_open,
)

from apex.execution.alpaca_client import create_trading_client
from apex.execution.order_executor import submit_paper_order

from apex.regime.regime_engine import classify_market_regime
from apex.signals.regime_signals import build_regime_signal
from apex.risk.risk_engine import RiskEngine

from apex.strategies.momentum_scanner import scan_momentum_candidates

from apex.portfolio.trade_planner import create_trade_plan
from apex.portfolio.daily_limits import daily_trade_limit_reached
from apex.portfolio.portfolio_risk_manager import PortfolioRiskManager
from apex.portfolio.portfolio_heat import portfolio_heat_limit_reached
from apex.portfolio.cooldown_manager import symbol_on_cooldown
from apex.portfolio.position_manager import get_open_positions
from apex.portfolio.correlation_filter import correlation_blocked
from apex.portfolio.sector_exposure import sector_exposure_blocked
from apex.portfolio.exit_manager import monitor_exit_signals
from apex.portfolio.position_metadata import (
    reconcile_position_metadata,
    show_position_metadata_summary,
)
from apex.portfolio.position_metadata import (
    reconcile_position_metadata,
    show_position_metadata_summary,
)

from apex.monitoring.trade_journal import log_trade_plan
from apex.monitoring.slack_notifier import (
    notify_account_snapshot,
    notify_market_closed,
    send_slack_message,
)

from apex.analytics.account_snapshot import show_account_snapshot
from apex.analytics.performance_dashboard import show_performance_dashboard
from apex.analytics.research_promotion import analyze_research_promotions

log = get_logger()


def notify_order_if_submitted(order, trade_plan):
    if not order:
        return

    send_slack_message(
        ":rocket: *[APEX] Paper Order Submitted*\n"
        f"Symbol: *{trade_plan.symbol}*\n"
        f"Qty: {trade_plan.shares:.4f}\n"
        f"Entry: ${trade_plan.entry_price:.2f}\n"
        f"Risk: ${trade_plan.dollar_risk:.2f}\n"
        f"Order ID: `{order.id}`"
    )


def notify_exit_signals(exit_signals):
    for signal in exit_signals:
        send_slack_message(
            ":warning: *[APEX] Exit Signal Detected — Monitor Only*\n"
            f"Symbol: *{signal.symbol}*\n"
            f"Reason: {signal.reason.value}\n"
            f"Qty: {signal.qty}\n"
            f"Entry: ${signal.entry_price:.2f}\n"
            f"Current: ${signal.current_price:.2f}\n"
            f"P/L: ${signal.unrealized_pl:.2f} "
            f"({signal.unrealized_plpc:.2%})"
        )


def main():
    log.info("Apex Trading Bot starting...")

    config = load_config()

    log.info(f"Execution mode: {config['execution']['mode']}")
    log.info(get_market_clock_summary())

    client = create_trading_client()

    show_account_snapshot(client)

    account = client.get_account()
    positions = client.get_all_positions()
    open_orders = client.get_orders()

    notify_account_snapshot(
        account,
        positions,
        open_orders,
    )

    reconcile_position_metadata(
        positions,
        source="BROKER_IMPORT",
    )

    show_position_metadata_summary()

    reconcile_position_metadata(
        positions,
        source="BROKER_IMPORT",
    )

    show_position_metadata_summary()

    regime = classify_market_regime()
    regime_signal = build_regime_signal(regime)

    exit_signals = monitor_exit_signals(
        positions=positions,
        regime=regime,
    )

    notify_exit_signals(exit_signals)

    log.info(f"Regime risk multiplier: {regime_signal.risk_multiplier}")
    log.info(f"Regime max positions: {regime_signal.max_positions}")
    log.info(
        f"Regime allows new positions: "
        f"{regime_signal.allow_new_positions}"
    )

    base_risk_per_trade = config["risk"]["risk_per_trade"]

    adjusted_risk_per_trade = (
        base_risk_per_trade * regime_signal.risk_multiplier
    )

    risk_engine = RiskEngine(
        strategy_capital=config["risk"]["strategy_capital"],
        risk_per_trade=adjusted_risk_per_trade,
    )

    portfolio_risk_manager = PortfolioRiskManager(
        max_open_positions=regime_signal.max_positions,
    )

    candidates = scan_momentum_candidates()

    log.info("Top Momentum Candidates:")

    for candidate in candidates[:5]:
        log.info(
            f"{candidate['symbol']} | "
            f"Price: ${candidate['price']} | "
            f"Momentum: {candidate['momentum_30d']}% | "
            f"Score: {candidate['score']}"
        )

    if not is_market_open():
        log.info("Market is closed by Eastern market clock.")
        log.info("No new paper orders will be placed.")
        notify_market_closed()

    elif not regime_signal.allow_new_positions:
        log.info("No new trades allowed by regime signal.")

    elif daily_trade_limit_reached():
        log.info("No new trades allowed today.")

    elif portfolio_heat_limit_reached(
        strategy_capital=config["risk"]["strategy_capital"],
        max_portfolio_risk_pct=config["risk"]["max_portfolio_risk_pct"],
    ):
        log.info("No new trades allowed due to portfolio heat limits.")

    elif not portfolio_risk_manager.can_add_new_position(client):
        log.info("No new trades allowed due to portfolio risk limits.")

    elif candidates and regime != "RISK_OFF":
        selected_candidate = None
        open_symbols = get_open_positions(client)

        for candidate in candidates:
            if symbol_on_cooldown(candidate["symbol"]):
                log.info(
                    f"{candidate['symbol']} skipped due to cooldown."
                )
                continue

            if correlation_blocked(candidate["symbol"], open_symbols):
                log.info(
                    f"{candidate['symbol']} skipped due to correlation."
                )
                continue

            if sector_exposure_blocked(candidate["symbol"], open_symbols):
                log.info(
                    f"{candidate['symbol']} skipped due to sector exposure."
                )
                continue

            selected_candidate = candidate
            log.info(f"{candidate['symbol']} selected.")
            break

        if selected_candidate is None:
            log.info("No eligible candidates available.")

        else:
            trade_plan = create_trade_plan(
                selected_candidate,
                risk_engine,
            )

            log_trade_plan(trade_plan)

            order = submit_paper_order(
                client,
                config,
                trade_plan,
            )

            notify_order_if_submitted(order, trade_plan)

    else:
        log.info("No candidates available or market is risk off.")

    log.info(f"Active regime: {regime}")

    show_performance_dashboard()

    analyze_research_promotions()

    log.info("System initialized successfully.")


if __name__ == "__main__":
    main()
