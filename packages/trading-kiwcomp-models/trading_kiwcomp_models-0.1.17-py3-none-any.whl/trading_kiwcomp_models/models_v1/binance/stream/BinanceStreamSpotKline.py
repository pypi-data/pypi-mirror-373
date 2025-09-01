from pydantic import BaseModel
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime
from .base import StreamKline

class BinanceStreamSpotKline(BaseModel):
    source: str = "binance"
    type: str = "kline"
    market: str = "spot"
    symbol: str
    interval: str
    event_time: datetime
    open_time: datetime
    close_time: datetime
    is_closed: bool
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_volume: float
    trades: int
    taker_buy_base: float
    taker_buy_quote: float

class BinanceStreamSpotKlineTable(StreamKline):
    __tablename__ = "binance_stream_spot_kline"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    interval = Column(String)
    event_time = Column(DateTime, index=True)
    open_time = Column(DateTime)
    close_time = Column(DateTime)
    is_closed = Column(Boolean)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    quote_volume = Column(Float)
    trades = Column(Integer)
    taker_buy_base = Column(Float)
    taker_buy_quote = Column(Float)

def ms_to_dt(ms: int) -> datetime:
    return datetime.fromtimestamp(ms/1000, tz=timezone.utc)

class BinanceStreamSpotKlineMapper:
    @staticmethod
    def from_raw(raw: dict) -> BinanceStreamSpotKline:
        d = raw.get("data") or raw
        k = d.get("k") or {}

        return BinanceStreamSpotKline(
            symbol=d["s"],
            interval=k["i"],
            event_time=ms_to_dt(d["E"]),
            open_time=ms_to_dt(k["t"]),
            close_time=ms_to_dt(k["T"]),
            is_closed=k["x"],
            open=float(k["o"]),
            high=float(k["h"]),
            low=float(k["l"]),
            close=float(k["c"]),
            volume=float(k["v"]),
            quote_volume=float(k["q"]),
            trades=int(k["n"]),
            taker_buy_base=float(k["V"]),
            taker_buy_quote=float(k["Q"]),
        )

    @staticmethod
    def to_table(event: BinanceStreamSpotKline) -> BinanceStreamSpotKlineTable:
        return BinanceStreamSpotKlineTable(
            symbol=event.symbol,
            interval=event.interval,
            event_time=event.event_time,
            open_time=event.open_time,
            close_time=event.close_time,
            is_closed=event.is_closed,
            open=event.open,
            high=event.high,
            low=event.low,
            close=event.close,
            volume=event.volume,
            quote_volume=event.quote_volume,
            trades=event.trades,
            taker_buy_base=event.taker_buy_base,
            taker_buy_quote=event.taker_buy_quote,
        )
