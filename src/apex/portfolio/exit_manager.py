from dataclasses import dataclass
from enum import Enum

from apex.core.logger import get_logger
from apex.data.market_data import get_stock_bars

log = get_logger()


class ExitReason(str, Enum):
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    ATR_TRAILING_STOP = "ATR_TRAILING_STOP"
    REGIME_FORCED = "REGIME_FORCED"


@dataclass
class ExitSignal:
    symbol: str
    reason: ExitReason
    qty: float
    entry_price: float
    current_price: float
    unrealized_pl: float
    unrealized_plpc: float


def calculate_atr(symbol: str, period: int = 14):
    try:
        df = get_stock_bars(symbol, days=60)

        high = df["high"]
        low = df["low"]
        close = df["close"]
        prev_close = close.shift(1)

        tr = (
            (high - low)
            .to_frame("hl")
            .join((high - prev_close).abs().to_frame("hc"))
            .join((low - prev_close).abs().to_frame("lc"))
            .max(axis=1)
        )

        atr = tr.rolling(period).mean().iloc[-1]

        if atr != atr:
            return None

        return float(atr)

    except Exception as e:
        log.warning(f"ATR unavailable for {symbol}: {e}")
        return None


def evaluate_position_exit(
    position,
    regime,
    stop_loss_pct: float = 0.05,
    take_profit_pct: float = 0.20,
    atr_multiplier: float = 2.5,
):
    symbol = position.symbol
    qty = float(position.qty)
    entry_price = float(position.avg_entry_price)
    current_price = float(position.current_price)
    unrealized_pl = float(position.unrealized_pl)
    unrealized_plpc = float(position.unrealized_plpc)

    if regime == "RISK_OFF":
        return ExitSignal(
            symbol=symbol,
            reason=ExitReason.REGIME_FORCED,
            qty=qty,
            entry_price=entry_price,
            current_price=current_price,
            unrealized_pl=unrealized_pl,
            unrealized_plpc=unrealized_plpc,
        )

    if unrealized_plpc <= -stop_loss_pct:
        return ExitSignal(
            symbol=symbol,
            reason=ExitReason.STOP_LOSS,
            qty=qty,
            entry_price=entry_price,
            current_price=current_price,
            unrealized_pl=unrealized_pl,
            unrealized_plpc=unrealized_plpc,
        )

    if unrealized_plpc >= take_profit_pct:
        return ExitSignal(
            symbol=symbol,
            reason=ExitReason.TAKE_PROFIT,
            qty=qty,
            entry_price=entry_price,
            current_price=current_price,
            unrealized_pl=unrealized_pl,
            unrealized_plpc=unrealized_plpc,
        )

    atr = calculate_atr(symbol)

    if atr is not None:
        trailing_stop = current_price - (atr * atr_multiplier)

        log.info(
            f"Exit monitor {symbol} | "
            f"ATR: ${atr:.2f} | "
            f"Trailing stop reference: ${trailing_stop:.2f}"
        )

    return None


def monitor_exit_signals(positions, regime):
    log.info("===== EXIT MONITOR =====")

    signals = []

    for position in positions:
        signal = evaluate_position_exit(position, regime)

        if signal:
            signals.append(signal)
            log.warning(
                f"EXIT SIGNAL | {signal.symbol} | "
                f"Reason: {signal.reason.value} | "
                f"Qty: {signal.qty} | "
                f"Entry: ${signal.entry_price:.2f} | "
                f"Current: ${signal.current_price:.2f} | "
                f"P/L: ${signal.unrealized_pl:.2f} "
                f"({signal.unrealized_plpc:.2%})"
            )
        else:
            log.info(f"No exit signal for {position.symbol}")

    if not signals:
        log.info("No exit signals detected.")

    log.info("========================")

    return signals
