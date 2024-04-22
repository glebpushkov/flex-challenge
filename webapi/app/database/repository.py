from typing import List

from sqlalchemy.orm import Session
from datetime import date

from app.database import models
from app.core.entities import Trade


class TradesRepo:
    def __init__(self, session: Session):
        self._db = session

    def get_trades(self, trader_id: str = None, delivery_day: date = None) -> List[Trade]:
        query = self._db.query(models.TradeDB)
        if trader_id:
            query = query.filter(models.TradeDB.trader_id == trader_id)
        if delivery_day:
            query = query.filter(models.TradeDB.delivery_day == delivery_day)
        return [to_domain(trade_db) for trade_db in query.all()]

    def create_trade(self, trade: Trade):
        trade_db = models.TradeDB(
            id=trade.id,
            price=trade.price,
            quantity=trade.quantity,
            direction=trade.direction,
            delivery_day=trade.delivery_day,
            delivery_hour=trade.delivery_hour,
            trader_id=trade.trader_id,
            execution_time=trade.execution_time,
        )
        self._db.add(trade_db)
        self._db.commit()


def to_domain(trade_db: models.TradeDB) -> Trade:
    return Trade(
        created_at=trade_db.created_at,
        id=trade_db.id,
        price=trade_db.price,
        quantity=trade_db.quantity,
        direction=trade_db.direction,
        delivery_day=trade_db.delivery_day,
        delivery_hour=trade_db.delivery_hour,
        trader_id=trade_db.trader_id,
        execution_time=trade_db.execution_time,
    )

#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
#
#
# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()
#
# // trader_id
