from collections import Counter

from apex.core.logger import get_logger

log = get_logger()


class RejectionAnalytics:
    def __init__(self):
        self.rejections = []

    def record(self, symbol: str, reason: str):
        self.rejections.append(
            {
                "symbol": symbol,
                "reason": reason,
            }
        )

    def report(self):
        if not self.rejections:
            log.info("No signal rejections recorded.")
            return

        reasons = Counter(
            r["reason"] for r in self.rejections
        )

        symbols = Counter(
            r["symbol"] for r in self.rejections
        )

        log.info("===== SIGNAL REJECTION ANALYTICS =====")

        log.info("Rejections by reason:")
        for reason, count in reasons.items():
            log.info(f"{reason}: {count}")

        log.info("Rejections by symbol:")
        for symbol, count in symbols.items():
            log.info(f"{symbol}: {count}")

        log.info("=====================================")
