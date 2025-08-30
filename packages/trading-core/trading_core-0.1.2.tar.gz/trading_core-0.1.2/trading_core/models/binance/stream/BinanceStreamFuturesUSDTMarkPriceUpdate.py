from pydantic import BaseModel
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime
from typing import Optional
from .base import MarkPriceUpdate

class BinanceStreamFuturesUSDTMarkPriceUpdate(BaseModel):
    source: str = "binance"
    type: str = "markPriceUpdate"
    market: str = "futures_usdt"
    symbol: str
    event_time: datetime
    mark_price: float
    index_price: float
    estimated_settle_price: float
    funding_rate: float
    next_funding_time: Optional[datetime] = None

class BinanceStreamFuturesUSDTMarkPriceUpdateTable(MarkPriceUpdate):
    __tablename__ = "binance_futures_usdt_mark_price_update"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    event_time = Column(DateTime, index=True)
    mark_price = Column(Float)
    index_price = Column(Float)
    estimated_settle_price = Column(Float)
    funding_rate = Column(Float)
    next_funding_time = Column(DateTime)

def ms_to_dt(ms: int) -> datetime:
    if not ms:
        return None
    return datetime.fromtimestamp(ms/1000, tz=timezone.utc)

class BinanceStreamFuturesUSDTMarkPriceUpdateMapper:
    @staticmethod
    def from_raw(raw: dict) -> BinanceStreamFuturesUSDTMarkPriceUpdate:
        d = raw.get("data") or raw

        return BinanceStreamFuturesUSDTMarkPriceUpdate(
            symbol=d["s"],
            event_time=ms_to_dt(d["E"]),
            mark_price=float(d["p"]),
            index_price=float(d["i"]),
            estimated_settle_price=float(d["P"]),
            funding_rate=float(d["r"]) if d.get("r") not in ("", None) else 0.0,
            next_funding_time=ms_to_dt(d["T"]),
        )

    @staticmethod
    def to_table(event: BinanceStreamFuturesUSDTMarkPriceUpdate) -> BinanceStreamFuturesUSDTMarkPriceUpdateTable:
        return BinanceStreamFuturesUSDTMarkPriceUpdateTable(
            symbol=event.symbol,
            event_time=event.event_time,
            mark_price=event.mark_price,
            index_price=event.index_price,
            estimated_settle_price=event.estimated_settle_price,
            funding_rate=event.funding_rate,
            next_funding_time=event.next_funding_time,
        )
