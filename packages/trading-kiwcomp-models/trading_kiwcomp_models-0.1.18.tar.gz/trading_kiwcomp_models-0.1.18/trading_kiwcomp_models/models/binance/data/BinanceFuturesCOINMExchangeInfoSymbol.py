from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime
from datetime import datetime, timezone
from .base import ExchangeInfoSymbol


# ✅ Pydantic Model (ยังใช้ได้ปกติ)
class BinanceFuturesCOINMExchangeInfoSymbol(BaseModel):
    symbol: str
    pair: str
    contractType: str
    deliveryDate: Optional[datetime]
    onboardDate: Optional[datetime]
    contractStatus: str
    contractSize: int
    quoteAsset: str
    baseAsset: str
    marginAsset: str
    pricePrecision: int
    quantityPrecision: int
    baseAssetPrecision: int
    quotePrecision: int
    triggerProtect: str
    underlyingType: str
    underlyingSubType: List[str]
    filters: List[dict]
    OrderType: List[str]
    timeInForce: List[str]
    liquidationFee: str
    marketTakeBound: str


# ✅ ORM Table (SQLAlchemy v1.4 compatible)
class BinanceFuturesCOINMExchangeInfoSymbolTable(ExchangeInfoSymbol):
    __tablename__ = "binance_futures_coinm_exchange_info_symbols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True, unique=True)
    pair = Column(String, index=True)
    contractType = Column(String)
    deliveryDate = Column(DateTime(timezone=True))
    onboardDate = Column(DateTime(timezone=True))
    contractStatus = Column(String)
    contractSize = Column(Integer)
    quoteAsset = Column(String)
    baseAsset = Column(String)
    marginAsset = Column(String)
    pricePrecision = Column(Integer)
    quantityPrecision = Column(Integer)
    baseAssetPrecision = Column(Integer)
    quotePrecision = Column(Integer)
    triggerProtect = Column(String)
    underlyingType = Column(String)
    underlyingSubType = Column(JSON)  # ✅ JSON รองรับใน 1.4
    filters = Column(JSON)
    OrderType = Column(JSON)
    timeInForce = Column(JSON)
    liquidationFee = Column(String)
    marketTakeBound = Column(String)


# ✅ Mapper
class BinanceFuturesCOINMExchangeInfoSymbolMapper:
    @staticmethod
    def from_raw(raw: dict) -> BinanceFuturesCOINMExchangeInfoSymbol:
        """Convert raw Binance JSON → Pydantic model"""
        return BinanceFuturesCOINMExchangeInfoSymbol(
            symbol=raw["symbol"],
            pair=raw["pair"],
            contractType=raw["contractType"],
            deliveryDate=datetime.fromtimestamp(raw["deliveryDate"] / 1000, tz=timezone.utc)
            if raw.get("deliveryDate") else None,
            onboardDate=datetime.fromtimestamp(raw["onboardDate"] / 1000, tz=timezone.utc)
            if raw.get("onboardDate") else None,
            contractStatus=raw["contractStatus"],
            contractSize=raw["contractSize"],
            quoteAsset=raw["quoteAsset"],
            baseAsset=raw["baseAsset"],
            marginAsset=raw["marginAsset"],
            pricePrecision=raw["pricePrecision"],
            quantityPrecision=raw["quantityPrecision"],
            baseAssetPrecision=raw["baseAssetPrecision"],
            quotePrecision=raw["quotePrecision"],
            triggerProtect=raw.get("triggerProtect", "0"),
            underlyingType=raw["underlyingType"],
            underlyingSubType=raw.get("underlyingSubType", []),
            filters=raw.get("filters", []),
            OrderType=raw.get("OrderType", []),
            timeInForce=raw.get("timeInForce", []),
            liquidationFee=raw.get("liquidationFee", "0"),
            marketTakeBound=raw.get("marketTakeBound", "0"),
        )

    @staticmethod
    def to_table(event: BinanceFuturesCOINMExchangeInfoSymbol) -> BinanceFuturesCOINMExchangeInfoSymbolTable:
        """Convert Pydantic model → ORM row"""
        return BinanceFuturesCOINMExchangeInfoSymbolTable(
            symbol=event.symbol,
            pair=event.pair,
            contractType=event.contractType,
            deliveryDate=event.deliveryDate,
            onboardDate=event.onboardDate,
            contractStatus=event.contractStatus,
            contractSize=event.contractSize,
            quoteAsset=event.quoteAsset,
            baseAsset=event.baseAsset,
            marginAsset=event.marginAsset,
            pricePrecision=event.pricePrecision,
            quantityPrecision=event.quantityPrecision,
            baseAssetPrecision=event.baseAssetPrecision,
            quotePrecision=event.quotePrecision,
            triggerProtect=event.triggerProtect,
            underlyingType=event.underlyingType,
            underlyingSubType=event.underlyingSubType,
            filters=event.filters,
            OrderType=event.OrderType,
            timeInForce=event.timeInForce,
            liquidationFee=event.liquidationFee,
            marketTakeBound=event.marketTakeBound,
        )
