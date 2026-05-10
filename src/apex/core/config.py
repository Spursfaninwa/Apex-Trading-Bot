from pathlib import Path
import os
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class TradingConfig(BaseModel):
    mode: str = "paper"
    max_positions: int = 5
    risk_per_trade: float = 0.01
    max_daily_drawdown: float = 0.03

class BrokerConfig(BaseModel):
    provider: str = "alpaca"

class StrategyConfig(BaseModel):
    momentum: bool = True
    mean_reversion: bool = True
    volatility_expansion: bool = True
    relative_strength: bool = True

class RegimeConfig(BaseModel):
    enabled: bool = True


class ExecutionConfig(BaseModel):
    mode: str = "scan_only"

class AppConfig(BaseModel):
    trading: TradingConfig
    broker: BrokerConfig
    strategies: StrategyConfig
    regime: RegimeConfig
    execution: ExecutionConfig

def load_config(path: str = "config/settings.yaml") -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(config_path, "r") as file:
        raw = yaml.safe_load(file)

    return AppConfig(**raw)

def get_env(name: str, required: bool = True) -> str | None:
    value = os.getenv(name)
    if required and not value:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value
