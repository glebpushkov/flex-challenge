from base64 import b64encode
from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.entities import Direction
from app.database import models
from app.database.session import Base
from app.main import app, settings
from app.api.handlers import get_session


TEST_DB_URL = "sqlite://"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(session):
    token = b64encode(f"{settings.basic_auth_username}:{settings.basic_auth_password}".encode('utf-8')).decode("ascii")
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app, headers={"Authorization": f"Basic {token}"})
    yield client


@pytest.fixture()
def trade_generator():
    counter = 0

    def gen(trader_id: str, day: date) -> models.TradeDB:
        nonlocal counter
        trade_db = models.TradeDB(
            id=str(counter),
            price=1,
            quantity=1,
            direction=Direction.buy,
            delivery_day=day,
            delivery_hour=1,
            trader_id=trader_id,
            execution_time=datetime.now(),
        )
        counter += 1
        return trade_db

    return gen
