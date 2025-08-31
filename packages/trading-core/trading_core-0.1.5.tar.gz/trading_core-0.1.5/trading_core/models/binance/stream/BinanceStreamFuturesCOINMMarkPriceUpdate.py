from pydantic import BaseModel
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime
from .base import MarkPriceUpdate

class BinanceStreamFuturesCOINMMarkPriceUpdate(BaseModel):
    source: str = "binance"
    type: str = "markPriceUpdate"
    market: str = "futures_coinm"
    symbol: str
    event_time: datetime
    mark_price: float
    estimated_settle_price: float | None = None   # ✅ add this
    index_price: float
    funding_rate: float | None = None
    next_funding_time: datetime | None = None

class BinanceStreamFuturesCOINMMarkPriceUpdateTable(MarkPriceUpdate):
    __tablename__ = "binance_futures_coinm_mark_price_update"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    event_time = Column(DateTime, index=True)
    mark_price = Column(Float)
    estimated_settle_price = Column(Float)   # ✅ add this
    index_price = Column(Float)
    funding_rate = Column(Float)
    next_funding_time = Column(DateTime)

def ms_to_dt(ms: int) -> datetime:
    return datetime.fromtimestamp(ms/1000, tz=timezone.utc)

class BinanceStreamFuturesCOINMMarkPriceUpdateMapper:
    @staticmethod
    def from_raw(raw: dict) -> BinanceStreamFuturesCOINMMarkPriceUpdate:
        d = raw.get("data") or raw
        return BinanceStreamFuturesCOINMMarkPriceUpdate(
            symbol=d["s"],
            event_time=ms_to_dt(d["E"]),
            mark_price=float(d["p"]),
            estimated_settle_price=float(d["P"]) if d.get("P") else None,  # ✅
            index_price=float(d["i"]),
            funding_rate=float(d["r"]) if d.get("r") not in ("", None) else None,
            next_funding_time=ms_to_dt(d["T"]) if d.get("T") else None
        )

    @staticmethod
    def to_table(event: BinanceStreamFuturesCOINMMarkPriceUpdate) -> BinanceStreamFuturesCOINMMarkPriceUpdateTable:
        return BinanceStreamFuturesCOINMMarkPriceUpdateTable(
            symbol=event.symbol,
            event_time=event.event_time,
            mark_price=event.mark_price,
            estimated_settle_price=event.estimated_settle_price,   # ✅
            index_price=event.index_price,
            funding_rate=event.funding_rate,
            next_funding_time=event.next_funding_time
        )
