from apex.core.logger import get_logger
from apex.core.config import load_config
from apex.execution.alpaca_client import create_trading_client
from apex.regime.regime_engine import classify_market_regime
from apex.risk.risk_engine import RiskEngine
from apex.strategies.momentum_scanner import scan_momentum_candidates
from apex.portfolio.trade_planner import create_trade_plan
from apex.execution.order_executor import submit_paper_order
from apex.monitoring.trade_journal import log_trade_plan
from apex.portfolio.cooldown_manager import symbol_on_cooldown

log = get_logger()


def main():
    log.info("Apex Trading Bot starting...")

    config = load_config()
    log.info(f"Execution mode: {config.execution.mode}")

    client = create_trading_client()

    regime = classify_market_regime()

    risk_engine = RiskEngine(
        strategy_capital=1000,
        risk_per_trade=0.01,
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

    if candidates and regime != "RISK_OFF":
        top_candidate = candidates[0]

        if symbol_on_cooldown(top_candidate["symbol"]):

            log.info(
                f"{top_candidate['symbol']} skipped due to cooldown."
            )

        else:

            trade_plan = create_trade_plan(
                top_candidate,
                risk_engine,
            )

            log_trade_plan(trade_plan)

            submit_paper_order(
                client,
                config,
                trade_plan,
            )
    else:
        log.info("No trade plan created.")

    log.info(f"Active regime: {regime}")
    log.info("System initialized successfully.")


if __name__ == "__main__":
    main()
