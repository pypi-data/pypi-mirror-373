import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from trading_core.models.binance.data.BinanceFutureCOINMExchangeInfoSymbol import (
    BinanceFutureCOINMExchangeInfoSymbol,
    BinanceFutureCOINMExchangeInfoSymbolTable,
    BinanceFutureCOINMExchangeInfoSymbolMapper,
)
from trading_core.models.binance.data import ExchangeInfoSymbol

# ✅ ตัวอย่าง raw message จาก Binance Futures COIN-M
RAW_SAMPLE = {
    "symbol": "BTCUSD_200925",
    "pair": "BTCUSD",
    "contractType": "CURRENT_QUARTER",
    "deliveryDate": 1601020800000,
    "onboardDate": 1590739200000,
    "contractStatus": "TRADING",
    "contractSize": 100,
    "quoteAsset": "USD",
    "baseAsset": "BTC",
    "marginAsset": "BTC",
    "pricePrecision": 1,
    "quantityPrecision": 0,
    "baseAssetPrecision": 8,
    "quotePrecision": 8,
    "triggerProtect": "0.0500",
    "underlyingType": "COIN",
    "underlyingSubType": [],
    "filters": [
        {
            "filterType": "PRICE_FILTER",
            "maxPrice": "100000",
            "minPrice": "0.1",
            "tickSize": "0.1",
        },
        {
            "filterType": "LOT_SIZE",
            "maxQty": "100000",
            "minQty": "1",
            "stepSize": "1",
        },
    ],
    "OrderType": ["LIMIT", "MARKET", "STOP", "TAKE_PROFIT", "TRAILING_STOP_MARKET"],
    "timeInForce": ["GTC", "IOC", "FOK", "GTX"],
    "liquidationFee": "0.010000",
    "marketTakeBound": "0.30",
}


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    ExchangeInfoSymbol.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_from_raw_to_model():
    event = BinanceFutureCOINMExchangeInfoSymbolMapper.from_raw(RAW_SAMPLE)
    assert isinstance(event, BinanceFutureCOINMExchangeInfoSymbol)
    assert event.symbol == "BTCUSD_200925"
    assert event.pair == "BTCUSD"
    assert event.contractType == "CURRENT_QUARTER"
    assert event.quoteAsset == "USD"
    assert event.baseAsset == "BTC"
    assert event.marginAsset == "BTC"
    assert event.contractSize == 100
    assert event.pricePrecision == 1
    assert event.quantityPrecision == 0
    assert event.liquidationFee == "0.010000"
    assert event.marketTakeBound == "0.30"
    assert "PRICE_FILTER" in [f["filterType"] for f in event.filters]


def test_model_to_table_object():
    event = BinanceFutureCOINMExchangeInfoSymbolMapper.from_raw(RAW_SAMPLE)
    row = BinanceFutureCOINMExchangeInfoSymbolMapper.to_table(event)
    assert isinstance(row, BinanceFutureCOINMExchangeInfoSymbolTable)
    assert row.symbol == "BTCUSD_200925"
    assert row.pair == "BTCUSD"
    assert row.contractStatus == "TRADING"
    assert row.contractSize == 100
    assert row.liquidationFee == "0.010000"


def test_insert_into_db(db_session):
    # map raw -> model -> table -> insert
    event = BinanceFutureCOINMExchangeInfoSymbolMapper.from_raw(RAW_SAMPLE)
    row = BinanceFutureCOINMExchangeInfoSymbolMapper.to_table(event)
    db_session.add(row)
    db_session.commit()

    result = db_session.query(BinanceFutureCOINMExchangeInfoSymbolTable).first()
    assert result.symbol == "BTCUSD_200925"
    assert result.pair == "BTCUSD"
    assert result.contractSize == 100
    assert result.quoteAsset == "USD"
    assert result.baseAsset == "BTC"
    assert result.liquidationFee == "0.010000"
