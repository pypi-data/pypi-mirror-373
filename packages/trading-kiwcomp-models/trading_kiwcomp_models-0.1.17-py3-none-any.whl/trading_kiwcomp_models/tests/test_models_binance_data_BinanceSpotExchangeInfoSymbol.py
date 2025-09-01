import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from trading_kiwcomp_models.models.binance.data.BinanceSpotExchangeInfoSymbol import (
    BinanceSpotExchangeInfoSymbol,
    BinanceSpotExchangeInfoSymbolTable,
    BinanceSpotExchangeInfoSymbolMapper,
)

from trading_kiwcomp_models.models.binance.data import ExchangeInfoSymbol

RAW_SAMPLE = {
    "symbol": "BTCUSDT",
    "status": "TRADING",
    "baseAsset": "BTC",
    "baseAssetPrecision": 8,
    "quoteAsset": "USDT",
    "quotePrecision": 8,
    "quoteAssetPrecision": 8,
    "baseCommissionPrecision": 2,
    "quoteCommissionPrecision": 2,
    "orderTypes": ["LIMIT", "MARKET", "STOP_LOSS", "TAKE_PROFIT"],
    "icebergAllowed": True,
    "ocoAllowed": True,
    "otoAllowed": False,
    "quoteOrderQtyMarketAllowed": True,
    "allowTrailingStop": True,
    "cancelReplaceAllowed": True,
    "amendAllowed": False,
    "pegInstructionsAllowed": False,
    "isSpotTradingAllowed": True,
    "isMarginTradingAllowed": False,
    "filters": [
        {"filterType": "PRICE_FILTER", "minPrice": "0.01", "maxPrice": "1000000", "tickSize": "0.01"},
        {"filterType": "LOT_SIZE", "minQty": "0.0001", "maxQty": "1000", "stepSize": "0.0001"},
    ],
    "permissions": ["SPOT"],
    "permissionSets": [["SPOT"]],
    "defaultSelfTradePreventionMode": "NONE",
    "allowedSelfTradePreventionModes": ["NONE", "EXPIRE_TAKER"],
}


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    ExchangeInfoSymbol.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_from_raw_to_model():
    event = BinanceSpotExchangeInfoSymbolMapper.from_raw(RAW_SAMPLE)
    assert isinstance(event, BinanceSpotExchangeInfoSymbol)
    assert event.symbol == "BTCUSDT"
    assert event.status == "TRADING"
    assert event.baseAsset == "BTC"
    assert event.quoteAsset == "USDT"
    assert event.baseAssetPrecision == 8
    assert event.quoteAssetPrecision == 8
    assert event.icebergAllowed is True
    assert "PRICE_FILTER" in [f["filterType"] for f in event.filters]


def test_model_to_table_object():
    event = BinanceSpotExchangeInfoSymbolMapper.from_raw(RAW_SAMPLE)
    row = BinanceSpotExchangeInfoSymbolMapper.to_table(event)
    assert isinstance(row, BinanceSpotExchangeInfoSymbolTable)
    assert row.symbol == "BTCUSDT"
    assert row.status == "TRADING"
    assert row.baseAsset == "BTC"
    assert row.quoteAsset == "USDT"
    assert row.isSpotTradingAllowed is True
    assert row.isMarginTradingAllowed is False


def test_insert_into_db(db_session):
    event = BinanceSpotExchangeInfoSymbolMapper.from_raw(RAW_SAMPLE)
    row = BinanceSpotExchangeInfoSymbolMapper.to_table(event)
    db_session.add(row)
    db_session.commit()

    result = db_session.query(BinanceSpotExchangeInfoSymbolTable).first()
    assert result.symbol == "BTCUSDT"
    assert result.status == "TRADING"
    assert result.baseAsset == "BTC"
    assert result.quoteAsset == "USDT"
    assert result.icebergAllowed is True
    assert result.isSpotTradingAllowed is True
