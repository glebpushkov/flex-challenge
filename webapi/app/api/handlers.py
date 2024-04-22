from datetime import date
from http import HTTPStatus
from typing import List, Optional, Union, Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import RequestValidationError
from pydantic.v1.error_wrappers import ErrorWrapper
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.schemas_gen import Trade, Error
from app.core.entities import ID_MAX_LEN
from app.core.services import TradesManager
from app.database.repository import TradesRepo
from app.database.session import SessionLocal

router = APIRouter()


def get_session() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_trades_manager(db: Session = Depends(get_session)):
    repo = TradesRepo(db)
    return TradesManager(repo)


@router.get('/trades', response_model=List[Trade], responses={'400': {'model': Error}})
def get_trades(
    trader_id: Annotated[str | None, Query(max_length=ID_MAX_LEN)] = None,
    delivery_day: Optional[date] = None,
    trades_manager: TradesManager = Depends(get_trades_manager)
) -> Union[List[Trade], Error]:
    return trades_manager.get_trades(trader_id, delivery_day)


@router.post('/trades', response_model=None, responses={'400': {'model': Error}})
def post_trades(
    trade: Trade,
    trades_manager: TradesManager = Depends(get_trades_manager)

) -> Union[None, Error]:
    try:
        trades_manager.create_trade(trade)
    except IntegrityError as e:
        if 'UNIQUE' in str(e):  # dirty way, but seems like there is no other way around
            # mimic validation error
            msg = 'Trade with such ID already exists'
            raise RequestValidationError(errors=[
                ErrorWrapper(ValueError(msg), loc=('body', 'id')),
            ], body=msg)
        raise e
    return
