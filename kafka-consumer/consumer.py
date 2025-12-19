#!/usr/bin/env python3
"""
Kafka Consumer - Moves price updates from Kafka to Redis
"""

import json
import os
import redis
from kafka import KafkaConsumer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

def create_consumer():
    return KafkaConsumer(
        'price-updates',
        bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest',
        enable_auto_commit=True,
        max_poll_records=500,
        group_id='redis-consumer-group'
    )

def create_redis_client():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True
    )

def main():
    logger.info("Starting Kafka → Redis consumer")
    logger.info(f"Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
    logger.info(f"Redis: {REDIS_HOST}:{REDIS_PORT}")
    
    consumer = create_consumer()
    redis_client = create_redis_client()
    
    message_count = 0
    
    try:
        for message in consumer:
            price_update = message.value
            symbol = price_update['symbol']
            
            key = f"price:{symbol}"
            redis_client.set(key, json.dumps(price_update))
            
            message_count += 1
            
            if message_count % 1000 == 0:
                logger.info(f"Processed {message_count} messages")
    
    except KeyboardInterrupt:
        logger.info("Shutting down consumer")
    finally:
        consumer.close()
        logger.info(f"Total messages processed: {message_count}")

if __name__ == '__main__':
    main()
