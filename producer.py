#!/usr/bin/env python3
"""
High-Frequency Producer - Benchmark Edition
Produces price updates to Kafka at configurable rate
"""

import json
import random
import time
import sys
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Stock symbols
SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT',
           'BAC', 'JNJ', 'PG', 'DIS', 'NFLX', 'INTC', 'CSCO', 'VZ', 'PFE', 'KO']

# Initial prices
PRICES = {symbol: random.uniform(100, 500) for symbol in SYMBOLS}

def create_producer():
    """Create high-performance Kafka producer"""
    return KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None,
        acks=1,
        # compression_type='snappy',
        batch_size=16384,
        linger_ms=10,
        buffer_memory=33554432
    )

def generate_price_update(symbol):
    """Generate realistic price update"""
    current_price = PRICES[symbol]
    change_percent = random.uniform(-0.005, 0.005)
    new_price = round(current_price * (1 + change_percent), 2)
    PRICES[symbol] = new_price
    
    return {
        'symbol': symbol,
        'price': new_price,
        'bidPrice': round(new_price * 0.999, 2),
        'askPrice': round(new_price * 1.001, 2),
        'volume': random.randint(1000, 100000),
        'timestamp': int(time.time() * 1000),
        'receivedAt': int(time.time() * 1000)
    }

def benchmark_producer(rate_per_sec=1000, duration_sec=60):
    """
    Produce messages at specified rate
    """
    producer = create_producer()
    
    total_sent = 0
    total_errors = 0
    interval = 1.0 / rate_per_sec
    
    print("=" * 60)
    print("BENCHMARK #1: HIGH-FREQUENCY WRITES")
    print("=" * 60)
    print(f"Target Rate: {rate_per_sec:,} msg/sec")
    print(f"Duration: {duration_sec} seconds")
    print(f"Expected Total: {rate_per_sec * duration_sec:,} messages")
    print("=" * 60)
    print()
    
    start_time = time.time()
    end_time = start_time + duration_sec
    last_report = start_time
    
    try:
        while time.time() < end_time:
            batch_start = time.time()
            
            symbol = random.choice(SYMBOLS)
            price_update = generate_price_update(symbol)
            
            try:
                producer.send('price-updates', key=symbol, value=price_update)
                total_sent += 1
            except KafkaError as e:
                total_errors += 1
                print(f"Error sending message: {e}")
            
            current_time = time.time()
            if current_time - last_report >= 1.0:
                elapsed = current_time - start_time
                actual_rate = total_sent / elapsed if elapsed > 0 else 0
                progress = (elapsed / duration_sec) * 100
                
                print(f"[{progress:5.1f}%] Sent: {total_sent:,} | "
                      f"Rate: {actual_rate:,.0f} msg/sec | "
                      f"Errors: {total_errors}")
                last_report = current_time
            
            elapsed_batch = time.time() - batch_start
            sleep_time = max(0, interval - elapsed_batch)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    except KeyboardInterrupt:
        print("\n\nStopping producer...")
    
    finally:
        producer.flush()
        producer.close()
        
        total_time = time.time() - start_time
        actual_rate = total_sent / total_time if total_time > 0 else 0
        
        print("\n" + "=" * 60)
        print("BENCHMARK #1 RESULTS")
        print("=" * 60)
        print(f"Duration:        {total_time:.2f} seconds")
        print(f"Messages Sent:   {total_sent:,}")
        print(f"Errors:          {total_errors}")
        print(f"Actual Rate:     {actual_rate:,.2f} msg/sec")
        print(f"Target Rate:     {rate_per_sec:,} msg/sec")
        print(f"Achievement:     {(actual_rate/rate_per_sec)*100:.1f}%")
        print("=" * 60)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='High-Frequency Price Producer')
    parser.add_argument('--rate', type=int, default=1000, 
                        help='Messages per second (default: 1000)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Duration in seconds (default: 60)')
    
    args = parser.parse_args()
    
    benchmark_producer(args.rate, args.duration)
