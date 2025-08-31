import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from trading_core.models.binance.stream.BinanceStreamFuturesCOINMMarkPriceUpdate import (
    BinanceStreamFuturesCOINMMarkPriceUpdate,
    BinanceStreamFuturesCOINMMarkPriceUpdateTable,
    BinanceStreamFuturesCOINMMarkPriceUpdateMapper,
)

from trading_core.models.binance.stream import MarkPriceUpdate


# ✅ ตัวอย่าง raw message จาก Binance
RAW_SAMPLE = {
    "data": {
        "e": "markPriceUpdate",
        "E": 1596095725000,
        "s": "BTCUSD_201225",
        "p": "10934.62615417",   # Mark Price
        "P": "10962.17178236",   # Estimated Settle Price
        "i": "10933.62615417",   # Index Price
        "r": "0.00038167",       # Funding rate
        "T": 1596100000000       # Next funding time
    }
}

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    MarkPriceUpdate.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_from_raw_to_model():
    event = BinanceStreamFuturesCOINMMarkPriceUpdateMapper.from_raw(RAW_SAMPLE)
    assert isinstance(event, BinanceStreamFuturesCOINMMarkPriceUpdate)
    assert event.symbol == "BTCUSD_201225"
    assert float(event.mark_price) == 10934.62615417
    assert float(event.index_price) == 10933.62615417
    assert float(event.estimated_settle_price) == 10962.17178236
    assert float(event.funding_rate) == 0.00038167

def test_model_to_table_object():
    event = BinanceStreamFuturesCOINMMarkPriceUpdateMapper.from_raw(RAW_SAMPLE)
    row = BinanceStreamFuturesCOINMMarkPriceUpdateMapper.to_table(event)
    assert isinstance(row, BinanceStreamFuturesCOINMMarkPriceUpdateTable)
    assert row.symbol == "BTCUSD_201225"
    assert float(row.mark_price) == 10934.62615417
    assert float(row.index_price) == 10933.62615417

def test_insert_into_db(db_session):
    # map raw -> model -> table -> insert
    event = BinanceStreamFuturesCOINMMarkPriceUpdateMapper.from_raw(RAW_SAMPLE)
    row = BinanceStreamFuturesCOINMMarkPriceUpdateMapper.to_table(event)
    db_session.add(row)
    db_session.commit()

    result = db_session.query(BinanceStreamFuturesCOINMMarkPriceUpdateTable).first()
    assert result.symbol == "BTCUSD_201225"
    assert float(result.mark_price) == 10934.62615417
    assert float(result.funding_rate) == 0.00038167
