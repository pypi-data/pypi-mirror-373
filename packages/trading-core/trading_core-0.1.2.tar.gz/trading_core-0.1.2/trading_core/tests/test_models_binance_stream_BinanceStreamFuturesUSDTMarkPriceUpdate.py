import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone

from trading_core.models.binance.stream.BinanceStreamFuturesUSDTMarkPriceUpdate import (
    BinanceStreamFuturesUSDTMarkPriceUpdate,
    BinanceStreamFuturesUSDTMarkPriceUpdateTable,
    BinanceStreamFuturesUSDTMarkPriceUpdateMapper,
)

from trading_core.models.binance.stream import MarkPriceUpdate


# ✅ Sample raw message (from Binance docs)
RAW_SAMPLE = {
    "data": {
        "e": "markPriceUpdate",
        "E": 1562305380000,
        "s": "BTCUSDT",
        "p": "11794.15000000",
        "i": "11784.62659091",
        "P": "11784.25641265",
        "r": "0.00038167",
        "T": 1562306400000
    }
}

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    MarkPriceUpdate.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_from_raw_to_model():
    event = BinanceStreamFuturesUSDTMarkPriceUpdateMapper.from_raw(RAW_SAMPLE)
    assert isinstance(event, BinanceStreamFuturesUSDTMarkPriceUpdate)
    assert event.symbol == "BTCUSDT"
    assert event.mark_price == pytest.approx(11794.15)
    assert event.index_price == pytest.approx(11784.62659091)
    assert event.estimated_settle_price == pytest.approx(11784.25641265)
    assert event.funding_rate == pytest.approx(0.00038167)
    assert isinstance(event.event_time, datetime)
    assert isinstance(event.next_funding_time, datetime)
    assert event.event_time.tzinfo == timezone.utc

def test_model_to_table_object():
    event = BinanceStreamFuturesUSDTMarkPriceUpdateMapper.from_raw(RAW_SAMPLE)
    row = BinanceStreamFuturesUSDTMarkPriceUpdateMapper.to_table(event)
    assert isinstance(row, BinanceStreamFuturesUSDTMarkPriceUpdateTable)
    assert row.symbol == "BTCUSDT"
    assert row.mark_price == pytest.approx(11794.15)
    assert row.index_price == pytest.approx(11784.62659091)

def test_insert_into_db(db_session):
    event = BinanceStreamFuturesUSDTMarkPriceUpdateMapper.from_raw(RAW_SAMPLE)
    row = BinanceStreamFuturesUSDTMarkPriceUpdateMapper.to_table(event)
    db_session.add(row)
    db_session.commit()

    result = db_session.query(BinanceStreamFuturesUSDTMarkPriceUpdateTable).first()
    assert result.symbol == "BTCUSDT"
    assert float(result.mark_price) == 11794.15
    assert float(result.index_price) == 11784.62659091

def test_from_raw_with_empty_funding_rate():
    raw = {
        "e": "markPriceUpdate",
        "E": 1562305380000,
        "s": "BTCUSDT",
        "p": "11794.15000000",
        "i": "11784.62659091",
        "P": "11784.25641265",
        "r": "",  # simulate delivery contract (no funding rate)
        "T": 0    # next funding time is 0
    }

    event = BinanceStreamFuturesUSDTMarkPriceUpdateMapper.from_raw(raw)
    assert isinstance(event, BinanceStreamFuturesUSDTMarkPriceUpdate)
    assert event.funding_rate == 0.0  # ✅ empty string should map to 0.0
    assert event.next_funding_time is None  # ✅ 0 → None
