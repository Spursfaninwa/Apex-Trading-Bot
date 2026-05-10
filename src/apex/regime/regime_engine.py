import pandas as pd

from apex.data.market_data import get_stock_bars
from apex.core.logger import get_logger

log = get_logger()

def classify_market_regime():
    df = get_stock_bars("SPY", days=250)

    closes = df["close"]

    sma_50 = closes.rolling(50).mean().iloc[-1]
    sma_200 = closes.rolling(200).mean().iloc[-1]

    current_price = closes.iloc[-1]

    log.info(f"SPY Current Price: {current_price:.2f}")
    log.info(f"SPY 50 SMA: {sma_50:.2f}")
    log.info(f"SPY 200 SMA: {sma_200:.2f}")

    if current_price > sma_50 > sma_200:
        regime = "BULL"

    elif current_price < sma_50 < sma_200:
        regime = "RISK_OFF"

    else:
        regime = "NEUTRAL"

    log.info(f"Current Market Regime: {regime}")

    return regime
