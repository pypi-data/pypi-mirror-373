import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, os
from datetime import datetime, timezone

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from trading_kiwcomp_models.models.binance.data.BinanceSpotKlineDaily import (
    BinanceSpotKlineDaily,
    BinanceSpotKlineDailyTable,
    BinanceSpotKlineDailyMapper,
)
from trading_kiwcomp_models.models.binance.data.base import SpotKlineDaily

# ✅ Sample RAW from Binance Klines API
RAW_SAMPLE = [
    1722470400000,       # open_time
    "64628.01000000",    # open
    "65659.78000000",    # high
    "62302.00000000",    # low
    "65354.02000000",    # close
    "35542.26854000",    # volume
    1722556799999,       # close_time
    "2270877792.65867990", # quote_asset_volume
    2397257,             # number_of_trades
    "16886.93292000",    # taker_buy_base_asset_volume
    "1079221072.75802780", # taker_buy_quote_asset_volume
    "0"                  # ignore
]

SYMBOL = "BTCUSDT"
INTERVAL = "1d"


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    SpotKlineDaily.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_from_raw_to_model():
    event = BinanceSpotKlineDailyMapper.from_raw(SYMBOL, INTERVAL, RAW_SAMPLE)
    assert isinstance(event, BinanceSpotKlineDaily)
    assert event.open_time == datetime.fromtimestamp(RAW_SAMPLE[0] / 1000, tz=timezone.utc)
    assert event.close_time == datetime.fromtimestamp(RAW_SAMPLE[6] / 1000, tz=timezone.utc)
    assert event.high == float(RAW_SAMPLE[2])
    assert event.low == float(RAW_SAMPLE[3])
    assert event.close == float(RAW_SAMPLE[4])
    assert event.volume == float(RAW_SAMPLE[5])
    assert event.number_of_trades == RAW_SAMPLE[8]


def test_model_to_table_object():
    event = BinanceSpotKlineDailyMapper.from_raw(SYMBOL, INTERVAL, RAW_SAMPLE)
    row = BinanceSpotKlineDailyMapper.to_table(SYMBOL, INTERVAL, event)
    assert isinstance(row, BinanceSpotKlineDailyTable)
    assert row.symbol == SYMBOL
    assert row.interval == INTERVAL
    assert row.open_time == datetime.fromtimestamp(RAW_SAMPLE[0] / 1000, tz=timezone.utc)
    assert row.close_time == datetime.fromtimestamp(RAW_SAMPLE[6] / 1000, tz=timezone.utc)
    assert row.open == float(RAW_SAMPLE[1])
    assert row.close == float(RAW_SAMPLE[4])
    assert row.number_of_trades == RAW_SAMPLE[8]


def test_insert_into_db(db_session):
    event = BinanceSpotKlineDailyMapper.from_raw(SYMBOL, INTERVAL, RAW_SAMPLE)
    row = BinanceSpotKlineDailyMapper.to_table(SYMBOL, INTERVAL, event)
    db_session.add(row)
    db_session.commit()

    result = db_session.query(BinanceSpotKlineDailyTable).first()
    assert result.symbol == SYMBOL
    assert result.interval == INTERVAL
    assert result.open == float(RAW_SAMPLE[1])
    assert result.close == float(RAW_SAMPLE[4])
    assert result.volume == float(RAW_SAMPLE[5])
    assert result.number_of_trades == RAW_SAMPLE[8]
    assert result.taker_buy_base_asset_volume == float(RAW_SAMPLE[9])
    assert result.taker_buy_quote_asset_volume == float(RAW_SAMPLE[10])
