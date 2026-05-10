from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

REPORTS_DIR = Path("reports")


def plot_equity_curves():
    csv_files = sorted(REPORTS_DIR.glob("*_equity_curve.csv"))

    if not csv_files:
        print("No equity curve files found.")
        return

    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        symbol = csv_file.stem.replace("_equity_curve", "")

        plt.figure()
        plt.plot(df["bar"], df["equity"])
        plt.title(f"{symbol} Equity Curve")
        plt.xlabel("Bar")
        plt.ylabel("Equity ($)")
        plt.tight_layout()

        output_path = REPORTS_DIR / f"{symbol}_equity_curve.png"
        plt.savefig(output_path)
        plt.close()

        print(f"Saved {output_path}")


if __name__ == "__main__":
    plot_equity_curves()
