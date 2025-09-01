from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, String, Integer, Float, DateTime, UniqueConstraint
from .base import BinanceKline


# ✅ Pydantic Model
class BinanceFuturesCOINMKline(BaseModel):
    symbol: str
    interval: str
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float                  # COIN-M → contract volume
    close_time: datetime
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float
    ignore: Optional[float] = None


# ✅ ORM Table (SQLAlchemy v1.4 style)
class BinanceFuturesCOINMKlineTable(BinanceKline):
    __tablename__ = "binance_futures_coinm_kline"

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
    taker_buy_base_asset_volume = Column(Float)
    taker_buy_quote_asset_volume = Column(Float)
    ignore = Column(Float, nullable=True)

    # ✅ enforce uniqueness for safe upserts
    __table_args__ = (
        UniqueConstraint("symbol", "interval", "open_time", name="uq_futures_coinm_kline"),
    )


# ✅ Mapper
class BinanceFuturesCOINMKlineMapper:
    @staticmethod
    def from_raw(symbol: str, interval: str, raw: list) -> BinanceFuturesCOINMKline:
        return BinanceFuturesCOINMKline(
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
    def to_table(event: BinanceFuturesCOINMKline) -> BinanceFuturesCOINMKlineTable:
        return BinanceFuturesCOINMKlineTable(**event.dict())
