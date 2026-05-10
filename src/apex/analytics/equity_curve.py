from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path("reports")
OUTPUT_DIR.mkdir(exist_ok=True)


def save_equity_curve(symbol: str, equity_curve: list[float]):
    path = OUTPUT_DIR / f"{symbol}_equity_curve.csv"

    df = pd.DataFrame(
        {
            "bar": list(range(len(equity_curve))),
            "equity": equity_curve,
        }
    )

    df.to_csv(path, index=False)

    return path
