from alpaca.trading.client import TradingClient
from apex.core.config import get_env
from apex.core.logger import get_logger

log = get_logger()

def create_trading_client():
    api_key = get_env("ALPACA_API_KEY")
    secret_key = get_env("ALPACA_SECRET_KEY")

    client = TradingClient(
        api_key=api_key,
        secret_key=secret_key,
        paper=True
    )

    account = client.get_account()

    log.info(f"Connected to Alpaca paper account.")
    log.info(f"Portfolio value: ${account.portfolio_value}")

    return client
