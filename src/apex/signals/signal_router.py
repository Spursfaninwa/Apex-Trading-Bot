from apex.core.logger import get_logger

log = get_logger()


class SignalRouter:
    def __init__(self):
        self.signals = []

    def add_signal(self, signal):
        self.signals.append(signal)

    def get_ranked_signals(self):
        ranked = sorted(
            self.signals,
            key=lambda s: s.score,
            reverse=True,
        )

        log.info(
            f"Ranked {len(ranked)} signals."
        )

        return ranked
