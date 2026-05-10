from apex.data.market_data import get_stock_bars
from apex.core.logger import get_logger
from apex.core.config import load_config
from apex.strategies.signal_scoring import score_momentum_candidate
from apex.analytics.rejection_analytics import RejectionAnalytics
from apex.monitoring.signal_memory import log_signal_candidates

log = get_logger()

WATCHLIST = [
    "SPY",
    "QQQ",
    "NVDA",
    "META",
    "AAPL",
    "MSFT",
    "AMZN",
    "GOOGL",
    "TSLA",
    "AMD",
]


def scan_momentum_candidates():
    config = load_config()
    approved_symbols = config["scanner"]["approved_symbols"]

    rejection_analytics = RejectionAnalytics()
    candidates = []
    research_candidates = []

    for symbol in WATCHLIST:
        approved_for_trade = symbol in approved_symbols

        if not approved_for_trade:
            log.info(
                f"{symbol} research-only scan "
                f"(not approved for trading)."
            )

        try:
            df = get_stock_bars(symbol, days=120)
            closes = df["close"]

            current_price = closes.iloc[-1]
            sma_20 = closes.rolling(20).mean().iloc[-1]
            sma_50 = closes.rolling(50).mean().iloc[-1]

            momentum_30d = ((current_price / closes.iloc[-30]) - 1) * 100
            volatility = closes.pct_change().std() * 100
            trend_strength = ((sma_20 / sma_50) - 1) * 100

            if current_price <= sma_20:
                rejection_analytics.record(symbol, "below_sma20")
                continue

            if sma_20 <= sma_50:
                rejection_analytics.record(symbol, "sma20_below_sma50")
                continue

            candidate = {
                "symbol": symbol,
                "price": round(current_price, 2),
                "momentum_30d": round(momentum_30d, 2),
                "volatility": round(volatility, 2),
                "trend_strength": round(trend_strength, 2),
                "approved_for_trade": approved_for_trade,
            }

            candidate["score"] = score_momentum_candidate(candidate)

            if candidate["score"] < 40:
                rejection_analytics.record(symbol, "score_below_40")
                continue

            research_candidates.append(candidate)

            if approved_for_trade:
                candidates.append(candidate)
                log.info(
                    f"{symbol} approved bullish momentum "
                    f"({momentum_30d:.2f}%)"
                )
            else:
                log.info(
                    f"{symbol} research-only bullish momentum "
                    f"({momentum_30d:.2f}%)"
                )

        except Exception as e:
            log.error(f"{symbol} scan failed: {e}")
            rejection_analytics.record(symbol, "scan_error")

    candidates = sorted(
        candidates,
        key=lambda x: x["score"],
        reverse=True,
    )

    research_candidates = sorted(
        research_candidates,
        key=lambda x: x["score"],
        reverse=True,
    )

    log.info("===== RESEARCH MODE CANDIDATES =====")

    for candidate in research_candidates[:10]:
        status = (
            "TRADE_APPROVED"
            if candidate["approved_for_trade"]
            else "RESEARCH_ONLY"
        )

        log.info(
            f"{candidate['symbol']} | "
            f"{status} | "
            f"Price: ${candidate['price']} | "
            f"Momentum: {candidate['momentum_30d']}% | "
            f"Score: {candidate['score']}"
        )

    log.info("====================================")

    log_signal_candidates(research_candidates)

    rejection_analytics.report()

    return candidates
