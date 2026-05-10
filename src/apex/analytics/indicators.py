def calculate_atr(df, period: int = 14):
    high = df["high"]
    low = df["low"]
    close = df["close"]

    prev_close = close.shift(1)

    tr = (high - low).to_frame("hl")
    tr["hc"] = (high - prev_close).abs()
    tr["lc"] = (low - prev_close).abs()

    true_range = tr.max(axis=1)
    atr = true_range.rolling(period).mean()

    return atr.iloc[-1]
