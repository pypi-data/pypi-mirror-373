import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, os

# เพิ่ม path ให้เจอ trading_core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from trading_kiwcomp_models.models.binance.data.BinanceFutureUSDTExchangeInfoSymbol import (
    BinanceFutureUSDTExchangeInfoSymbol,
    BinanceFutureUSDTExchangeInfoSymbolTable,
    BinanceFutureUSDTExchangeInfoSymbolMapper,
)

from trading_kiwcomp_models.models.binance.data import ExchangeInfoSymbol

# ✅ ตัวอย่าง raw message จาก Binance Futures USDT
RAW_SAMPLE = {
    "symbol": "BTCUSDT",
    "pair": "BTCUSDT",
    "contractType": "PERPETUAL",
    "deliveryDate": 4133865600000,  # ไกล ๆ ไปเลย
    "onboardDate": 1569398400000,
    "status": "TRADING",
    "baseAsset": "BTC",
    "quoteAsset": "USDT",
    "marginAsset": "USDT",
    "pricePrecision": 2,
    "quantityPrecision": 3,
    "baseAssetPrecision": 8,
    "quotePrecision": 8,
    "underlyingType": "USDⓈ",
    "underlyingSubType": ["DeFi"],
    "settlePlan": 0,
    "triggerProtect": "0.0500",
    "filters": [
        {"filterType": "PRICE_FILTER", "maxPrice": "100000", "minPrice": "0.1", "tickSize": "0.1"},
        {"filterType": "LOT_SIZE", "maxQty": "10000", "minQty": "0.001", "stepSize": "0.001"},
    ],
    "OrderType": ["LIMIT", "MARKET"],
    "timeInForce": ["GTC", "IOC", "FOK"],
    "liquidationFee": "0.020000",
    "marketTakeBound": "0.30",
}


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    ExchangeInfoSymbol.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_from_raw_to_model():
    event = BinanceFutureUSDTExchangeInfoSymbolMapper.from_raw(RAW_SAMPLE)
    assert isinstance(event, BinanceFutureUSDTExchangeInfoSymbol)
    assert event.symbol == "BTCUSDT"
    assert event.pair == "BTCUSDT"
    assert event.contractType == "PERPETUAL"
    assert event.status == "TRADING"
    assert event.baseAsset == "BTC"
    assert event.quoteAsset == "USDT"
    assert event.marginAsset == "USDT"
    assert event.pricePrecision == 2
    assert event.quantityPrecision == 3
    assert event.liquidationFee == "0.020000"
    assert "PRICE_FILTER" in [f["filterType"] for f in event.filters]


def test_model_to_table_object():
    event = BinanceFutureUSDTExchangeInfoSymbolMapper.from_raw(RAW_SAMPLE)
    row = BinanceFutureUSDTExchangeInfoSymbolMapper.to_table(event)
    assert isinstance(row, BinanceFutureUSDTExchangeInfoSymbolTable)
    assert row.symbol == "BTCUSDT"
    assert row.pair == "BTCUSDT"
    assert row.status == "TRADING"
    assert row.pricePrecision == 2
    assert row.liquidationFee == "0.020000"


def test_insert_into_db(db_session):
    event = BinanceFutureUSDTExchangeInfoSymbolMapper.from_raw(RAW_SAMPLE)
    row = BinanceFutureUSDTExchangeInfoSymbolMapper.to_table(event)
    db_session.add(row)
    db_session.commit()

    result = db_session.query(BinanceFutureUSDTExchangeInfoSymbolTable).first()
    assert result.symbol == "BTCUSDT"
    assert result.pair == "BTCUSDT"
    assert result.status == "TRADING"
    assert result.baseAsset == "BTC"
    assert result.quoteAsset == "USDT"
    assert result.liquidationFee == "0.020000"
