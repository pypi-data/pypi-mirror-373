from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime
from datetime import datetime, timezone
from .base import ExchangeInfoSymbol

# ✅ Pydantic Model
class BinanceFutureUSDTExchangeInfoSymbol(BaseModel):
    symbol: str
    pair: str
    contractType: str
    deliveryDate: Optional[datetime]
    onboardDate: Optional[datetime]
    status: str
    baseAsset: str
    quoteAsset: str
    marginAsset: str
    pricePrecision: int
    quantityPrecision: int
    baseAssetPrecision: int
    quotePrecision: int
    underlyingType: str
    underlyingSubType: List[str]
    settlePlan: int
    triggerProtect: str
    filters: List[dict]
    OrderType: List[str]
    timeInForce: List[str]
    liquidationFee: str
    marketTakeBound: str


# ✅ ORM Table
class BinanceFutureUSDTExchangeInfoSymbolTable(ExchangeInfoSymbol):
    __tablename__ = "binance_future_usdt_exchange_info_symbols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True, unique=True)
    pair = Column(String, index=True)
    contractType = Column(String)
    deliveryDate = Column(DateTime(timezone=True)) 
    onboardDate = Column(DateTime(timezone=True)) 
    status = Column(String)
    baseAsset = Column(String)
    quoteAsset = Column(String)
    marginAsset = Column(String)
    pricePrecision = Column(Integer)
    quantityPrecision = Column(Integer)
    baseAssetPrecision = Column(Integer)
    quotePrecision = Column(Integer)
    underlyingType = Column(String)
    underlyingSubType = Column(JSON)
    settlePlan = Column(Integer)
    triggerProtect = Column(String)
    filters = Column(JSON)
    OrderType = Column(JSON)
    timeInForce = Column(JSON)
    liquidationFee = Column(String)
    marketTakeBound = Column(String)

class BinanceFutureUSDTExchangeInfoSymbolMapper:
    @staticmethod
    def from_raw(raw: dict) -> BinanceFutureUSDTExchangeInfoSymbol:
        return BinanceFutureUSDTExchangeInfoSymbol(
            symbol=raw["symbol"],
            pair=raw["pair"],
            contractType=raw["contractType"],
            deliveryDate=datetime.fromtimestamp(raw["deliveryDate"]/1000, tz=timezone.utc)
                          if raw.get("deliveryDate") else None,
            onboardDate=datetime.fromtimestamp(raw["onboardDate"]/1000, tz=timezone.utc)
                         if raw.get("onboardDate") else None,
            status=raw["status"],
            baseAsset=raw["baseAsset"],
            quoteAsset=raw["quoteAsset"],
            marginAsset=raw["marginAsset"],
            pricePrecision=raw["pricePrecision"],
            quantityPrecision=raw["quantityPrecision"],
            baseAssetPrecision=raw["baseAssetPrecision"],
            quotePrecision=raw["quotePrecision"],
            underlyingType=raw["underlyingType"],
            underlyingSubType=raw.get("underlyingSubType", []),
            settlePlan=raw.get("settlePlan", 0),
            triggerProtect=raw.get("triggerProtect", "0"),
            filters=raw.get("filters", []),
            OrderType=raw.get("OrderType", []),
            timeInForce=raw.get("timeInForce", []),
            liquidationFee=raw.get("liquidationFee", "0"),
            marketTakeBound=raw.get("marketTakeBound", "0"),
        )

    @staticmethod
    def to_table(event: BinanceFutureUSDTExchangeInfoSymbol) -> BinanceFutureUSDTExchangeInfoSymbolTable:
        return BinanceFutureUSDTExchangeInfoSymbolTable(
            symbol=event.symbol,
            pair=event.pair,
            contractType=event.contractType,
            deliveryDate=event.deliveryDate,
            onboardDate=event.onboardDate,
            status=event.status,
            baseAsset=event.baseAsset,
            quoteAsset=event.quoteAsset,
            marginAsset=event.marginAsset,
            pricePrecision=event.pricePrecision,
            quantityPrecision=event.quantityPrecision,
            baseAssetPrecision=event.baseAssetPrecision,
            quotePrecision=event.quotePrecision,
            underlyingType=event.underlyingType,
            underlyingSubType=event.underlyingSubType,
            settlePlan=event.settlePlan,
            triggerProtect=event.triggerProtect,
            filters=event.filters,
            OrderType=event.OrderType,
            timeInForce=event.timeInForce,
            liquidationFee=event.liquidationFee,
            marketTakeBound=event.marketTakeBound,
        )
