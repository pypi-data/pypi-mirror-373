import asyncio
import json
import websockets
from trading_core.models.binance.stream import (
    BinanceStreamFuturesUSDTKlineMapper,
    BinanceStreamFuturesUSDTMarkPriceUpdateMapper,
)

class BinanceStream:
    def __init__(self, stream_cfg):
        """
        stream_cfg: BinanceStreamConfig (binance + kafka + postgres)
        """
        self.stream_cfg = stream_cfg
        self.binance_cfg = stream_cfg.binance
        self.kafka = stream_cfg.kafka
        self.kafka_topic = stream_cfg.kafka_topic
        self.postgres = stream_cfg.postgres

    def map_event(self, data: dict):
        """Map raw WS event -> (event, payload)"""
        etype = self.binance_cfg.event_type

        if etype == "markpriceupdate":
            if data.get("e") != "markPriceUpdate":
                return None, None
            event = BinanceStreamFuturesUSDTMarkPriceUpdateMapper.from_raw(data)
            return event, event.dict()

        elif etype == "kline":
            if data.get("e") != "kline":
                return None, None
            event = BinanceStreamFuturesUSDTKlineMapper.from_raw(data)
            if self.binance_cfg.final_only and not event.is_closed:
                return None, None
            return event, {"candle_stick": [event.dict()]}

        else:
            raise ValueError(f"Unsupported event_type: {etype}")

    async def run(self):
        url = self.binance_cfg.build_url()
        print(f"[binance_stream] subscribing to {url}")

        backoff = 1
        while True:
            try:
                async with websockets.connect(
                    url, ping_interval=20, ping_timeout=60,
                    open_timeout=20, close_timeout=5
                ) as ws:
                    backoff = 1
                    async for msg in ws:
                        obj = json.loads(msg)
                        data = obj.get("data") or {}
                        print(f"[raw] {json.dumps(obj, indent=2)}")


                        try:
                            event, payload = self.map_event(data)
                            if not event:
                                continue

                            # ---- Send to Kafka ----
                            await self.kafka.send_message(
                                topic=self.kafka_topic,
                                key=event.symbol,
                                value=payload
                            )
                            print(f"[kafka] sent -> {event.symbol} {self.binance_cfg.event_type}")

                            # ---- Optional: Insert to Postgres ----
                            # if self.postgres:
                            #     self.postgres.insert_event(event)

                        except ValueError as e:
                            print(f"[error] {e}")
                            break

            except Exception as e:
                print(f"[reconnect] {type(e).__name__}: {e}")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)
