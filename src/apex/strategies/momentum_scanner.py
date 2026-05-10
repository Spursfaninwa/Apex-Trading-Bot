from apex.data.market_data import get_stock_bars
from apex.strategies.signal_scoring import score_stock
from apex.core.logger import logger
from apex.strategies.approved_symbols import APPROVED_SYMBOLS

log = logger()

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


def scan_momentum_candidates(client):

    candidates = []

    for symbol in WATCHLIST:

        if symbol not in APPROVED_SYMBOLS:

            log.info(
                f"{symbol} skipped (not approved)."
            )

            continue

        bars = get_stock_bars(
            client,
            symbol,
            limit=82,
        )

        if bars.empty:
            continue

        score = score_stock(bars)

        latest_close = bars["close"].iloc[-1]
        first_close = bars["close"].iloc[0]

        momentum_pct = (
            (latest_close - first_close)
            / first_close
        ) * 100

        log.info(
            f"{symbol} scored {score}"
        )

        log.info(
            f"{symbol} bullish momentum "
            f"({momentum_pct:.2f}%)"
        )

        candidates.append(
            {
                "symbol": symbol,
                "score": score,
                "price": latest_close,
                "momentum_pct": momentum_pct,
            }
        )

    candidates = sorted(
        candidates,
        key=lambda x: x["score"],
        reverse=True,
    )

    log.info("Top Momentum Candidates:")

    for candidate in candidates[:5]:

        log.info(
            f"{candidate['symbol']} | "
            f"Price: ${candidate['price']:.2f} | "
            f"Momentum: "
            f"{candidate['momentum_pct']:.2f}% | "
            f"Score: {candidate['score']}"
        )

    return candidates
