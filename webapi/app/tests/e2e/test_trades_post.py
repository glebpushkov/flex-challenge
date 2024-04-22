from copy import copy
from datetime import date, datetime
from http import HTTPStatus

from app.core.entities import Direction
from app.database.models import TradeDB


def test_create_trade_success(session, client):
    expected = {
        'id': "123",
        'price': 123,
        'quantity': 123,
        'direction': Direction.buy,
        'delivery_day': date(2024, 1,1),
        'delivery_hour': 12,
        'trader_id': 'bot1',
        'execution_time':  datetime(2024, 1, 1, 0, 1),
    }
    expected_json = copy(expected)
    expected_json['direction'] = 'buy'
    expected_json['delivery_day'] = '2024-01-01'
    expected_json['execution_time'] = '2024-01-01T00:01'

    response = client.post('/trades', json=expected_json)

    assert response.status_code == HTTPStatus.OK, response.json()
    trades = session.query(TradeDB).all()
    assert len(trades) == 1
    trade = trades[0]
    for k, v in expected.items():
        assert getattr(trade, k) == v


def test_create_trade_duplicate_error(session, client):
    trade = {
        'id': "123",
        'price': 123,
        'quantity': 123,
        'direction': 'buy',
        'delivery_day': '2024-01-01',
        'delivery_hour': 12,
        'trader_id': 'bot1',
        'execution_time':  '2024-01-01T00:01',
    }

    response = client.post('/trades', json=trade)
    assert response.status_code == HTTPStatus.OK, response.json()
    response = client.post('/trades', json=trade)
    assert response.status_code == HTTPStatus.BAD_REQUEST, response.json()
    session.rollback()  # restore session after integrity error
    trades = session.query(TradeDB).all()
    assert len(trades) == 1


def test_create_trade_all_blank(client):
    response = client.post('/trades', json={})

    assert response.status_code == HTTPStatus.BAD_REQUEST
    error = response.json()
    assert error['status_code'] == HTTPStatus.BAD_REQUEST
    assert 'missing' in error['message']


def test_create_trade_all_fields_are_blank(client):
    response = client.post(
        '/trades',
        json={
            'id': None,
            'price': None,
            'quantity': None,
            'direction': None,
            'delivery_day': None,
            'delivery_hour': None,
            'trader_id': None,
            'execution_time': None,
        }
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    error = response.json()
    assert error['status_code'] == HTTPStatus.BAD_REQUEST
    # <it's a very bad test>
    fields = ['id', 'price', 'quantity', 'direction', 'delivery_day', 'delivery_hour', 'trader_id', 'execution_time']
    for fname in fields:
        assert fname in error['message']


# todo: more validation tests
