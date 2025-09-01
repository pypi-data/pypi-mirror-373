from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, String, Integer, Float, DateTime
from .base import BinanceKline


# ✅ Pydantic Model
class BinanceSpotKline(BaseModel):
    symbol: str
    interval: str
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: datetime
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float
    ignore: Optional[float] = None


# ✅ ORM Table (SQLAlchemy v1.4 style)
class BinanceSpotKlineTable(BinanceKline):
    __tablename__ = "binance_spot_kline"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    interval = Column(String)
    open_time = Column(DateTime(timezone=True), index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    close_time = Column(DateTime(timezone=True))
    quote_asset_volume = Column(Float)
    number_of_trades = Column(Integer)
    taker_buy_base_asset_volume = Column(Float)   # ✅ fixed
    taker_buy_quote_asset_volume = Column(Float)  # ✅ fixed
    ignore = Column(Float, nullable=True)


# ✅ Mapper
class BinanceSpotKlineMapper:
    @staticmethod
    def from_raw(symbol: str, interval: str, raw: list) -> BinanceSpotKline:
        return BinanceSpotKline(
            symbol=symbol,
            interval=interval,
            open_time=datetime.fromtimestamp(raw[0] / 1000, tz=timezone.utc),
            open=float(raw[1]),
            high=float(raw[2]),
            low=float(raw[3]),
            close=float(raw[4]),
            volume=float(raw[5]),
            close_time=datetime.fromtimestamp(raw[6] / 1000, tz=timezone.utc),
            quote_asset_volume=float(raw[7]),
            number_of_trades=int(raw[8]),
            taker_buy_base_asset_volume=float(raw[9]),
            taker_buy_quote_asset_volume=float(raw[10]),
            ignore=float(raw[11]) if len(raw) > 11 else None,
        )

    @staticmethod
    def to_table(event: BinanceSpotKline) -> BinanceSpotKlineTable:
        """Convert Pydantic model → SQLAlchemy ORM row"""
        return BinanceSpotKlineTable(**event.dict())
