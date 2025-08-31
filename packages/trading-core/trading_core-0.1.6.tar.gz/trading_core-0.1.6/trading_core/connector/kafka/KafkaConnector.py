from kafka import KafkaProducer, KafkaConsumer
import json
import logging
import asyncio 

logger = logging.getLogger(__name__)

class KafkaConnector:
    _instances = {}

    def __new__(cls, brokers, client_id="trading_core"):
        config_key = (brokers, client_id)

        if config_key not in cls._instances:
            instance = super(KafkaConnector, cls).__new__(cls)
            cls._instances[config_key] = instance
            instance.__init__(brokers, client_id)
        
        return cls._instances[config_key]

    def __init__(self, brokers, client_id="trading_core"):
        self.brokers = brokers if isinstance(brokers, list) else [brokers]
        self.client_id = client_id
        self.producer = None
        self.consumer = None

    def connect_producer(self):
        if self.producer:
            logger.info("Reusing existing Kafka Producer")
            return self.producer

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.brokers,
                client_id=self.client_id,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
                key_serializer=lambda k: None if k is None else str(k).encode("utf-8"),
                acks="all",
                retries=3
            )
            logger.info("Kafka Producer connected")
            return self.producer
        except Exception as e:
            logger.error(f"Kafka Producer connection failed: {e}")
            raise

    def connect_consumer(self, topic, group_id="trading_core_group", auto_offset_reset="earliest"):
        try:
            self.consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.brokers,
                client_id=self.client_id,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            )
            logger.info(f"Kafka Consumer connected to topic {topic}")
            return self.consumer
        except Exception as e:
            logger.error(f"Kafka Consumer connection failed: {e}")
            raise
        
    async def async_send_message(self, topic: str, key: str, value: dict):
        producer = self.connect_producer()
        fut = producer.send(topic, key=key, value=value)
        md = await asyncio.to_thread(fut.get, timeout=10)
        return md
    
    def send_message(self, topic, key, value):
        if not self.producer:
            self.connect_producer()
        future = self.producer.send(topic, key=key, value=value)
        result = future.get(timeout=10)
        logger.info(f"Message sent to {result.topic} partition {result.partition} offset {result.offset}")

    def consume_messages(self, callback, timeout_ms=1000):
        if not self.consumer:
            raise RuntimeError("Consumer is not connected. Call connect_consumer() first.")
        for message in self.consumer.poll(timeout_ms=timeout_ms).values():
            for record in message:
                callback(record.key, record.value)

    def close(self):
        if self.producer:
            self.producer.close()
            logger.info("Kafka Producer closed")
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka Consumer closed")

    def __enter__(self):
        self.connect_producer()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
