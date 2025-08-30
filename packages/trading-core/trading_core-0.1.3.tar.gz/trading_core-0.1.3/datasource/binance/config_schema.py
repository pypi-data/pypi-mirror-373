from pydantic import BaseModel, Field, validator,ConfigDict
from typing import List
from trading_core.connector.postgres.PostgresqlDBConnector import PostgresqlDBConnector
from trading_core.connector.kafka.KafkaConnector import KafkaConnector


class KafkaUserConfig(BaseModel):
    url: str
    topic: str


class PostgreSQLUserConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    dbname: str


class BinanceConfig(BaseModel):
    market: str = Field("futures_usdt", pattern="^(spot|futures_usdt|futures_coin)$")
    event_type: str = Field("kline", pattern="^(kline|markpriceupdate)$")
    kline_interval: str = Field("1m")
    symbols: List[str] = []
    final_only: bool = False

    @validator("kline_interval")
    def validate_interval(cls, v):
        allowed = {"1m", "3m", "5m", "15m", "1h", "4h", "1d"}
        if v not in allowed:
            raise ValueError(f"Invalid interval {v}, must be one of {allowed}")
        return v

    def ws_base_url(self) -> str:
        return {
            "spot": "wss://stream.binance.com:9443",
            "futures_usdt": "wss://fstream.binance.com",
            "futures_coin": "wss://dstream.binance.com",
        }[self.market]

    def build_url(self) -> str:
        if self.event_type == "markpriceupdate":
            streams = "/".join(f"{s}@markPrice" for s in self.symbols)
        elif self.event_type == "kline":
            streams = "/".join(f"{s}@kline_{self.kline_interval}" for s in self.symbols)
        else:
            raise ValueError(f"Unsupported event_type: {self.event_type}")
        return f"{self.ws_base_url()}/stream?streams={streams}"


class BinanceStreamConfig(BaseModel):
    binance: BinanceConfig
    postgres: PostgresqlDBConnector
    kafka: KafkaConnector
    kafka_topic: str

    model_config = ConfigDict(arbitrary_types_allowed=True)
