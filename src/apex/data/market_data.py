from datetime import datetime, timedelta, timezone

from alpaca.data.enums import DataFeed
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from apex.core.config import get_env
from apex.core.logger import get_logger

log = get_logger()


def get_stock_bars(symbol: str, days: int = 250):
    client = StockHistoricalDataClient(
        api_key=get_env("ALPACA_API_KEY"),
        secret_key=get_env("ALPACA_SECRET_KEY"),
    )

    end = datetime.now(timezone.utc) - timedelta(minutes=20)
    start = end - timedelta(days=days)

    request = StockBarsRequest(
        symbol_or_symbols=symbol,
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        feed=DataFeed.IEX,
    )

    bars = client.get_stock_bars(request)
    df = bars.df

    if df.empty:
        raise ValueError(f"No data returned for {symbol}")

    if "symbol" in df.index.names:
        df = df.loc[symbol]

    log.info(f"Retrieved {len(df)} IEX bars for {symbol}")
    return df
