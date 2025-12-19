#!/usr/bin/env python3
"""
WebSocket Benchmark - Tests low-latency WebSocket reads
"""

import asyncio
import json
import random
import time
import statistics
from websocket import create_connection
import websocket

SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT']

def measure_websocket_request():
    """Measure single WebSocket request latency"""
    symbol = random.choice(SYMBOLS)
    
    try:
        ws = create_connection("ws://localhost:8080/ws/prices")
        
        # Send subscription
        subscribe_msg = {
            "destination": f"/app/price/{symbol}",
            "headers": {}
        }
        
        start = time.time()
        ws.send(json.dumps(subscribe_msg))
        result = ws.recv()
        end = time.time()
        
        ws.close()
        
        latency_ms = (end - start) * 1000
        return {
            'latency_ms': latency_ms,
            'success': True
        }
    except Exception as e:
        return {
            'latency_ms': 0,
            'success': False,
            'error': str(e)
        }

def benchmark_websocket(num_requests=1000):
    """Benchmark WebSocket requests"""
    print("=" * 60)
    print("WEBSOCKET BENCHMARK")
    print("=" * 60)
    print(f"Requests: {num_requests}")
    print("=" * 60)
    print()
    
    latencies = []
    successes = 0
    failures = 0
    
    for i in range(num_requests):
        result = measure_websocket_request()
        
        if result['success']:
            latencies.append(result['latency_ms'])
            successes += 1
        else:
            failures += 1
        
        if (i + 1) % 100 == 0:
            print(f"Progress: {i+1}/{num_requests}")
    
    if latencies:
        latencies.sort()
        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else max(latencies)
        p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else max(latencies)
        min_lat = min(latencies)
        max_lat = max(latencies)
        avg_lat = statistics.mean(latencies)
    else:
        p50 = p95 = p99 = min_lat = max_lat = avg_lat = 0
    
    print("\n" + "=" * 60)
    print("WEBSOCKET RESULTS")
    print("=" * 60)
    print(f"Total Requests:     {num_requests}")
    print(f"Successful:         {successes}")
    print(f"Failed:             {failures}")
    print(f"Success Rate:       {(successes/num_requests)*100:.2f}%")
    print()
    print("LATENCY STATISTICS:")
    print(f"  Min:              {min_lat:.2f} ms")
    print(f"  Average:          {avg_lat:.2f} ms")
    print(f"  P50 (Median):     {p50:.2f} ms")
    print(f"  P95:              {p95:.2f} ms")
    print(f"  P99:              {p99:.2f} ms")
    print(f"  Max:              {max_lat:.2f} ms")
    print("=" * 60)
    
    print()
    if p99 < 10:
        print("✅ LOW-LATENCY REQUIREMENT MET: P99 < 10ms")
    else:
        print(f"⚠️  P99 latency: {p99:.2f}ms (target: <10ms)")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='WebSocket Benchmark')
    parser.add_argument('--requests', type=int, default=1000,
                        help='Number of requests (default: 1000)')
    
    args = parser.parse_args()
    
    benchmark_websocket(args.requests)
