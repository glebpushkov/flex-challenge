import enum
from datetime import date, datetime
from dataclasses import dataclass

ID_MAX_LEN = 255


class Direction(enum.Enum):
    buy = "buy"
    sell = "sell"


@dataclass
class Trade:
    created_at: datetime

    id: str
    price: int
    quantity: int
    direction: Direction
    delivery_day: date
    delivery_hour: int
    trader_id: str
    execution_time: datetime

# todo: we should be not able to create invalid Trade until all domain validation for each field passed
