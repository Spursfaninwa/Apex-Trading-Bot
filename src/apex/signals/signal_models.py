from dataclasses import dataclass


@dataclass
class TradeSignal:
    symbol: str
    strategy: str
    score: float
    entry_price: float
    stop_price: float
    volatility: float
    regime: str
