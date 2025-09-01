from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, String, Boolean, Integer, JSON
from .base import ExchangeInfoSymbol


# ✅ Pydantic Model
class BinanceSpotExchangeInfoSymbol(BaseModel):
    symbol: str
    status: str
    baseAsset: str
    baseAssetPrecision: int
    quoteAsset: str
    quotePrecision: int
    quoteAssetPrecision: int
    baseCommissionPrecision: int
    quoteCommissionPrecision: int
    orderTypes: List[str]
    icebergAllowed: bool
    ocoAllowed: bool
    otoAllowed: bool
    quoteOrderQtyMarketAllowed: bool
    allowTrailingStop: bool
    cancelReplaceAllowed: bool
    amendAllowed: bool
    pegInstructionsAllowed: bool
    isSpotTradingAllowed: bool
    isMarginTradingAllowed: bool
    filters: Optional[List[dict]] = []
    permissions: Optional[List[str]] = []
    permissionSets: Optional[List[List[str]]] = []
    defaultSelfTradePreventionMode: Optional[str]
    allowedSelfTradePreventionModes: Optional[List[str]] = []


# ✅ ORM Table
class BinanceSpotExchangeInfoSymbolTable(ExchangeInfoSymbol):
    __tablename__ = "binance_spot_exchange_info_symbols"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True, unique=True)
    status = Column(String)
    baseAsset = Column(String)
    baseAssetPrecision = Column(Integer)
    quoteAsset = Column(String)
    quotePrecision = Column(Integer)
    quoteAssetPrecision = Column(Integer)
    baseCommissionPrecision = Column(Integer)
    quoteCommissionPrecision = Column(Integer)
    orderTypes = Column(JSON)
    icebergAllowed = Column(Boolean)
    ocoAllowed = Column(Boolean)
    otoAllowed = Column(Boolean)
    quoteOrderQtyMarketAllowed = Column(Boolean)
    allowTrailingStop = Column(Boolean)
    cancelReplaceAllowed = Column(Boolean)
    amendAllowed = Column(Boolean)
    pegInstructionsAllowed = Column(Boolean)
    isSpotTradingAllowed = Column(Boolean)
    isMarginTradingAllowed = Column(Boolean)
    filters = Column(JSON)
    permissions = Column(JSON)
    permissionSets = Column(JSON)
    defaultSelfTradePreventionMode = Column(String)
    allowedSelfTradePreventionModes = Column(JSON)


# ✅ Mapper
class BinanceSpotExchangeInfoSymbolMapper:
    @staticmethod
    def from_raw(raw: dict) -> BinanceSpotExchangeInfoSymbol:
        """Convert raw Binance JSON → Pydantic model"""
        return BinanceSpotExchangeInfoSymbol(
            symbol=raw["symbol"],
            status=raw["status"],
            baseAsset=raw["baseAsset"],
            baseAssetPrecision=raw["baseAssetPrecision"],
            quoteAsset=raw["quoteAsset"],
            quotePrecision=raw.get("quotePrecision", 0),
            quoteAssetPrecision=raw["quoteAssetPrecision"],
            baseCommissionPrecision=raw["baseCommissionPrecision"],
            quoteCommissionPrecision=raw["quoteCommissionPrecision"],
            orderTypes=raw.get("orderTypes", []),
            icebergAllowed=raw.get("icebergAllowed", False),
            ocoAllowed=raw.get("ocoAllowed", False),
            otoAllowed=raw.get("otoAllowed", False),
            quoteOrderQtyMarketAllowed=raw.get("quoteOrderQtyMarketAllowed", False),
            allowTrailingStop=raw.get("allowTrailingStop", False),
            cancelReplaceAllowed=raw.get("cancelReplaceAllowed", False),
            amendAllowed=raw.get("amendAllowed", False),
            pegInstructionsAllowed=raw.get("pegInstructionsAllowed", False),
            isSpotTradingAllowed=raw.get("isSpotTradingAllowed", False),
            isMarginTradingAllowed=raw.get("isMarginTradingAllowed", False),
            filters=raw.get("filters", []),
            permissions=raw.get("permissions", []),
            permissionSets=raw.get("permissionSets", []),
            defaultSelfTradePreventionMode=raw.get("defaultSelfTradePreventionMode"),
            allowedSelfTradePreventionModes=raw.get("allowedSelfTradePreventionModes", []),
        )

    @staticmethod
    def to_table(event: BinanceSpotExchangeInfoSymbol) -> BinanceSpotExchangeInfoSymbolTable:
        """Convert Pydantic model → ORM row"""
        return BinanceSpotExchangeInfoSymbolTable(
            symbol=event.symbol,
            status=event.status,
            baseAsset=event.baseAsset,
            baseAssetPrecision=event.baseAssetPrecision,
            quoteAsset=event.quoteAsset,
            quotePrecision=event.quotePrecision,
            quoteAssetPrecision=event.quoteAssetPrecision,
            baseCommissionPrecision=event.baseCommissionPrecision,
            quoteCommissionPrecision=event.quoteCommissionPrecision,
            orderTypes=event.orderTypes,
            icebergAllowed=event.icebergAllowed,
            ocoAllowed=event.ocoAllowed,
            otoAllowed=event.otoAllowed,
            quoteOrderQtyMarketAllowed=event.quoteOrderQtyMarketAllowed,
            allowTrailingStop=event.allowTrailingStop,
            cancelReplaceAllowed=event.cancelReplaceAllowed,
            amendAllowed=event.amendAllowed,
            pegInstructionsAllowed=event.pegInstructionsAllowed,
            isSpotTradingAllowed=event.isSpotTradingAllowed,
            isMarginTradingAllowed=event.isMarginTradingAllowed,
            filters=event.filters,
            permissions=event.permissions,
            permissionSets=event.permissionSets,
            defaultSelfTradePreventionMode=event.defaultSelfTradePreventionMode,
            allowedSelfTradePreventionModes=event.allowedSelfTradePreventionModes,
        )
