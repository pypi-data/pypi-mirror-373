import os
import sys
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from trading_core.utilities.LoadJsonConfig import LoadJsonConfig
from .config_schema import BinanceStreamConfig, BinanceConfig
from trading_core.connector.kafka.KafkaConnector import KafkaConnector
from trading_core.connector.postgres.PostgresqlDBConnector import PostgresqlDBConnector
from streams.binance_stream import BinanceStream

async def test_connections(kafka, postgres, binance_cfg):
    """
    Run simple health checks before starting the stream
    """
    # ✅ Test Kafka
    try:
        kafka.send_message(   # <--- no await
            topic="__healthcheck__",
            key="ping",
            value={"status": "ok"}
        )
        print("✅ Kafka connection OK")
    except Exception as e:
        print(f"❌ Kafka connection failed: {e}")
        raise

    # ✅ Test Postgres
    try:
        postgres.execute_query("SELECT 1;")
        print("✅ PostgreSQL connection OK")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        raise

    # ✅ Test Binance WS URL
    print(f"✅ Binance WS URL: {binance_cfg.build_url()}")
    
    
def binance_stream(config):
    # ✅ Create Kafka connection
    kafka_connection = KafkaConnector(
        brokers=config.kafka.url
    )

    # ✅ Create Postgres connection
    postgresql_connection = PostgresqlDBConnector(
        db_name=config.postgres.dbname,
        db_port=config.postgres.port,
        db_host=config.postgres.host,
        db_user=config.postgres.user,
        db_password=config.postgres.password,
    )

    # ✅ Binance stream config
    binance_stream_config = BinanceStreamConfig(
        binance=BinanceConfig(
            market=config.binance.market,
            kline_interval=config.binance.kline_interval,
            event_type=config.binance.event_type,
            symbols=config.binance.symbols or ["btcusdt"],
        ),
        postgres=postgresql_connection,
        kafka=kafka_connection,
        kafka_topic=config.kafka.topic
    )

    # ✅ Start stream
    stream = BinanceStream(binance_stream_config)
    try:
        asyncio.run(test_connections(kafka_connection, postgresql_connection, binance_stream_config.binance))
        asyncio.run(stream.run())
    except KeyboardInterrupt:
        print("⏹️ Binance stream stopped by user")


# if __name__ == "__main__":
#     # ✅ Load validated config.json
#     config_path = os.getenv("CONFIG_PATH", "config.json")
#     config = LoadJsonConfig(config_path)

#     # ✅ Create Kafka connection
#     kafka_connection = KafkaConnector(
#         brokers=config.kafka.url
#     )

#     # ✅ Create Postgres connection
#     postgresql_connection = PostgresqlDBConnector(
#         db_name=config.postgres.dbname,
#         db_port=config.postgres.port,
#         db_host=config.postgres.host,
#         db_user=config.postgres.user,
#         db_password=config.postgres.password,
#     )

#     # ✅ Binance stream config
#     binance_stream_config = BinanceStreamConfig(
#         binance=BinanceConfig(
#             market=config.binance.market,
#             kline_interval=config.binance.kline_interval,
#             event_type=config.binance.event_type,
#             symbols=["btcusdt"], 
#         ),
#         postgres=postgresql_connection,
#         kafka=kafka_connection,
#         kafka_topic=config.kafka.topic
#     )

#     # ✅ Start stream
#     stream = BinanceStream(binance_stream_config)
#     try:
#         asyncio.run(test_connections(kafka_connection, postgresql_connection, binance_stream_config.binance))
#         asyncio.run(stream.run())
#     except KeyboardInterrupt:
#         print("⏹️ Binance stream stopped by user")
