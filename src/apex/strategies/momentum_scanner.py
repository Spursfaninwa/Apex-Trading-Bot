from apex.data.market_data import get_stock_bars
from apex.core.logger import get_logger
from apex.core.config import load_config
from apex.strategies.signal_scoring import score_momentum_candidate
from apex.analytics.rejection_analytics import RejectionAnalytics

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

    for symbol in WATCHLIST:
        if symbol not in approved_symbols:
            log.info(f"{symbol} skipped (not approved).")
            rejection_analytics.record(symbol, "not_approved")
            continue

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
            }

            candidate["score"] = score_momentum_candidate(candidate)

            if candidate["score"] < 40:
                rejection_analytics.record(symbol, "score_below_40")
                continue

            candidates.append(candidate)

            log.info(
                f"{symbol} bullish momentum "
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

    rejection_analytics.report()

    return candidates
