from apex.core.logger import get_logger
from apex.portfolio.position_manager import get_open_positions

log = get_logger()


class PortfolioRiskManager:
    def __init__(
        self,
        max_open_positions: int = 5,
    ):
        self.max_open_positions = max_open_positions

    def can_add_new_position(self, client) -> bool:
        open_positions = get_open_positions(client)

        position_count = len(open_positions)

        log.info(f"Open position count: {position_count}")
        log.info(f"Max open positions: {self.max_open_positions}")

        if position_count >= self.max_open_positions:
            log.info("Portfolio risk block: max positions reached.")
            return False

        return True
