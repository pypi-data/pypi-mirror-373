import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from trading_kiwcomp_models.models.binance.stream.BinanceStreamFuturesUSDTKline import (
    BinanceStreamFuturesUSDTKline,
    BinanceStreamFuturesUSDTKlineTable,
    BinanceStreamFuturesUSDTKlineMapper,
)

from trading_kiwcomp_models.models.binance.stream import StreamKline


# ✅ Example raw message from Binance Futures USDT kline
RAW_SAMPLE = {
    "data": {
        "e": "kline",
        "E": 1638747660000,
        "s": "BTCUSDT",
        "k": {
            "t": 1638747660000,
            "T": 1638747719999,
            "s": "BTCUSDT",
            "i": "1m",
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
    event = BinanceStreamFuturesUSDTKlineMapper.from_raw(RAW_SAMPLE)
    assert isinstance(event, BinanceStreamFuturesUSDTKline)
    assert event.symbol == "BTCUSDT"
    assert event.interval == "1m"
    assert event.is_closed is True
    assert event.close == 0.0020
    assert event.volume == 1000.0


def test_model_to_table_object():
    event = BinanceStreamFuturesUSDTKlineMapper.from_raw(RAW_SAMPLE)
    row = BinanceStreamFuturesUSDTKlineMapper.to_table(event)
    assert isinstance(row, BinanceStreamFuturesUSDTKlineTable)
    assert row.symbol == "BTCUSDT"
    assert row.close == 0.0020


def test_insert_into_db(db_session):
    event = BinanceStreamFuturesUSDTKlineMapper.from_raw(RAW_SAMPLE)
    row = BinanceStreamFuturesUSDTKlineMapper.to_table(event)
    db_session.add(row)
    db_session.commit()

    result = db_session.query(BinanceStreamFuturesUSDTKlineTable).first()
    assert result.symbol == "BTCUSDT"
    assert result.interval == "1m"
