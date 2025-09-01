import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from trading_kiwcomp_models.models.binance.stream.BinanceStreamSpotKline import (
    BinanceStreamSpotKline,
    BinanceStreamSpotKlineTable,
    BinanceStreamSpotKlineMapper,
)

from trading_kiwcomp_models.models.binance.stream import StreamKline

# ✅ ตัวอย่าง raw message จาก Binance Spot
RAW_SAMPLE = {
    "data": {
        "e": "kline",
        "E": 1672515782136,
        "s": "BNBBTC",
        "k": {
            "t": 1672515780000,
            "T": 1672515839999,
            "s": "BNBBTC",
            "i": "1m",
            "f": 100,
            "L": 200,
            "o": "0.0010",
            "c": "0.0020",
            "h": "0.0025",
            "l": "0.0015",
            "v": "1000",
            "n": 100,
            "x": True,
            "q": "1.0000",
            "V": "500",
            "Q": "0.500",
            "B": "123456"
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
    event = BinanceStreamSpotKlineMapper.from_raw(RAW_SAMPLE)
    assert isinstance(event, BinanceStreamSpotKline)
    assert event.symbol == "BNBBTC"
    assert event.interval == "1m"
    assert event.is_closed is True
    assert event.close == 0.0020

def test_model_to_table_object():
    event = BinanceStreamSpotKlineMapper.from_raw(RAW_SAMPLE)
    row = BinanceStreamSpotKlineMapper.to_table(event)
    assert isinstance(row, BinanceStreamSpotKlineTable)
    assert row.symbol == "BNBBTC"
    assert float(row.close) == 0.0020

def test_insert_into_db(db_session):
    # map raw -> model -> table -> insert
    event = BinanceStreamSpotKlineMapper.from_raw(RAW_SAMPLE)
    row = BinanceStreamSpotKlineMapper.to_table(event)
    db_session.add(row)
    db_session.commit()

    result = db_session.query(BinanceStreamSpotKlineTable).first()
    assert result.symbol == "BNBBTC"
    assert result.interval == "1m"
    assert float(result.close) == 0.0020

