# Apex Trading Bot

Cloud-native systematic trading framework for risk-controlled momentum trading.

## Current Features

- Alpaca paper trading connection
- Market regime detection
- Momentum scanner
- Signal scoring
- ATR-based stops
- Risk-based position sizing
- Fractional share planning
- Execution guard: scan_only / paper_trade / live_trade
- Cooldown protection
- Daily trade limits
- Trade journal CSV
- Performance dashboard

## Run

```bash
pip install -e .
python -m apex.main
```

## Safety

Default mode is:

```yaml
execution:
  mode: scan_only
```

No orders are placed unless intentionally enabled.

## Disclaimer

For research and educational purposes only. Trading involves risk.