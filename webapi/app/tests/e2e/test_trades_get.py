from datetime import date
from http import HTTPStatus
from urllib.parse import urlencode

import pytest

from app.core.entities import ID_MAX_LEN


@pytest.mark.parametrize(
    'trader,date_str,expected',
    [
        (None, None, 3),
        (None, '2024-04-20', 2),
        (None, '2024-04-19', 0),
        ('trader 1', None, 1),
        ('trader not existing', None, 0),
        ('trader 1', '2024-04-20', 1),
        ('trader 3', '2024-04-20', 0),
    ],
    ids=['no-filters', 'by-date', 'by-date-none', 'by-trader', 'by-trader-none', 'by-trader-and-date', 'by-trader-and-date-none']
)
def test_get_trades_success(trader, date_str, expected, session, client, trade_generator):
    today = date(2024, 4, 20)
    tomorrow = date(2024, 4, 21)
    session.add(trade_generator('trader 1', today))
    session.add(trade_generator('trader 2', today))
    session.add(trade_generator('trader 3', tomorrow))
    session.commit()
    params = {
        'trader_id': trader,
        'delivery_day': date_str,
    }

    response = client.get('/trades?' + urlencode({k: v for k, v in params.items() if v}))

    assert response.status_code == HTTPStatus.OK, response.text
    trades = response.json()
    assert len(trades) == expected


@pytest.mark.parametrize(
    'trader,date_str,expected',
    [
        ("1" * (ID_MAX_LEN + 1), None, 'string_too_long'),
        (None, 'december', 'date_from_datetime_parsing'),
    ],
    ids=['id-too-long', 'not-a-date']
)
def test_get_trades_validation_errors(trader, date_str, expected, session, client, trade_generator):
    session.add(trade_generator('trader 1', date.today()))
    session.commit()
    params = {
        'trader_id': trader,
        'delivery_day': date_str,
    }

    response = client.get('/trades?' + urlencode({k: v for k, v in params.items() if v}))

    assert response.status_code == HTTPStatus.BAD_REQUEST
    error = response.json()
    assert error['status_code'] == HTTPStatus.BAD_REQUEST
    assert expected in error['message']
