import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from trading_core.models.binance.stream.BinanceStreamFuturesCOINMKline import (
    BinanceStreamFuturesCOINMKline,
    BinanceStreamFuturesCOINMKlineTable,
    BinanceStreamFuturesCOINMKlineMapper,
)

from trading_core.models.binance.stream import StreamKline

# ✅ ตัวอย่าง raw message จาก Binance
RAW_SAMPLE = {
    "data": {
        "e": "kline",
        "E": 1672515782136,
        "s": "BTCUSD_PERP",
        "k": {
            "t": 1672515780000,
            "T": 1672515839999,
            "s": "BTCUSD_PERP",
            "i": "1m",
            "o": "43500.00",
            "c": "43600.00",
            "h": "43650.00",
            "l": "43450.00",
            "v": "12.345",
            "n": 123,
            "x": True,
            "q": "543210.99",
            "V": "6.789",
            "Q": "300000.22"
        }
    }
}

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    StreamKline.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_from_raw_to_model():
    event = BinanceStreamFuturesCOINMKlineMapper.from_raw(RAW_SAMPLE)
    assert isinstance(event, BinanceStreamFuturesCOINMKline)
    assert event.symbol == "BTCUSD_PERP"
    assert event.interval == "1m"
    assert event.is_closed is True
    assert event.close == 43600.00

def test_model_to_table_object():
    event = BinanceStreamFuturesCOINMKlineMapper.from_raw(RAW_SAMPLE)
    row = BinanceStreamFuturesCOINMKlineMapper.to_table(event)
    assert isinstance(row, BinanceStreamFuturesCOINMKlineTable)
    assert row.symbol == "BTCUSD_PERP"
    assert row.close == 43600.00

def test_insert_into_db(db_session):
    # map raw -> model -> table -> insert
    event = BinanceStreamFuturesCOINMKlineMapper.from_raw(RAW_SAMPLE)
    row = BinanceStreamFuturesCOINMKlineMapper.to_table(event)
    db_session.add(row)
    db_session.commit()

    result = db_session.query(BinanceStreamFuturesCOINMKlineTable).first()
    assert result.symbol == "BTCUSD_PERP"
    assert result.interval == "1m"
    assert float(result.close) == 43600.00
