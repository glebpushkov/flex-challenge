from app.core.entities import Direction, ID_MAX_LEN
from app.database.session import Base
from sqlalchemy import Column, Integer, String, Enum, Date, DateTime, UUID, func


class BaseDBModel(Base):
    """
    A base model which adds basic common fields to all db tables, and can override common methods (like __repr__ or so)
    For now, it's only one field, potentially here could be 'uuid' and 'updated_at'
    """
    __abstract__ = True

    created_at = time_created = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TradeDB(BaseDBModel):
    __tablename__ = 'trades'

    id = Column(
        String(ID_MAX_LEN), primary_key=True, nullable=False, doc='Unique id of the trade as defined by the exchange'
    )
    price = Column(Integer, nullable=False, doc='Price in eurocent/MWh.')
    quantity = Column(Integer, nullable=False, doc='Quantity in MW.')
    direction = Column(
        Enum(Direction), nullable=False, doc='Direction of the trade from the perspective of flew-power, buy or sell'
    )
    delivery_day = Column(Date, nullable=False, doc='Day on which the energy has to be delivered in local time.')
    delivery_hour = Column(
        Integer, nullable=False, doc='Hour during which the energy has to be delivered in local time.'
    )
    trader_id = Column(String(ID_MAX_LEN), nullable=False, doc='Unique id of a trader (bot or team member).')
    execution_time = Column(DateTime, nullable=False, doc='UTC datetime at which the trade occured on the exchange.')
