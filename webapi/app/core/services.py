from datetime import date
from typing import Protocol, List

from app.core.entities import Trade


class TradesRepoAccessor(Protocol):
    def get_trades(self, trader_id: str = None, delivery_day: date = None) -> List[Trade]:
        pass

    def create_trade(self, trade: Trade):
        pass


class TradesManager:
    def __init__(self, repository: TradesRepoAccessor):
        self.repo = repository

    def get_trades(self, trader_id: str = None, delivery_day: date = None) -> List[Trade]:
        return self.repo.get_trades(trader_id, delivery_day)

    def create_trade(self, trade: Trade):
        self.repo.create_trade(trade)
