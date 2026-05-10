from apex.core.logger import get_logger
from apex.core.config import load_config

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

from apex.monitoring.trade_journal import log_trade_plan
from apex.analytics.performance_dashboard import show_performance_dashboard

log = get_logger()


def main():
    log.info("Apex Trading Bot starting...")

    config = load_config()
    log.info(f"Execution mode: {config['execution']['mode']}")

    client = create_trading_client()

    regime = classify_market_regime()
    regime_signal = build_regime_signal(regime)

    log.info(f"Regime risk multiplier: {regime_signal.risk_multiplier}")
    log.info(f"Regime max positions: {regime_signal.max_positions}")
    log.info(f"Regime allows new positions: {regime_signal.allow_new_positions}")

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

    if not regime_signal.allow_new_positions:
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

            submit_paper_order(
                client,
                config,
                trade_plan,
            )

    else:
        log.info("No candidates available or market is risk off.")

    log.info(f"Active regime: {regime}")

    show_performance_dashboard()

    log.info("System initialized successfully.")


if __name__ == "__main__":
    main()
