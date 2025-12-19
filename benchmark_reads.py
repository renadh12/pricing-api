
#!/usr/bin/env python3
"""
API Read Benchmark - Tests low-latency reads
Measures P50, P95, P99 latency at various loads
"""

import requests
import time
import statistics
import random
import concurrent.futures

SYMBOLS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT',
           'BAC', 'JNJ', 'PG', 'DIS', 'NFLX', 'INTC', 'CSCO', 'VZ', 'PFE', 'KO']

API_BASE_URL = 'http://localhost:8080/api/v1/prices'

def measure_single_request():
    """Measure latency of single price lookup"""
    symbol = random.choice(SYMBOLS)
    
    start = time.time()
    try:
        response = requests.get(f"{API_BASE_URL}/{symbol}", timeout=5)
        end = time.time()
        
        latency_ms = (end - start) * 1000
        success = response.status_code == 200
        
        return {
            'latency_ms': latency_ms,
            'success': success,
            'status_code': response.status_code
        }
    except Exception as e:
        end = time.time()
        return {
            'latency_ms': (end - start) * 1000,
            'success': False,
            'error': str(e)
        }

def measure_batch_request():
    """Measure latency of batch price lookup"""
    symbols = random.sample(SYMBOLS, 5)
    params = {'symbols': ','.join(symbols)}
    
    start = time.time()
    try:
        response = requests.get(f"{API_BASE_URL}/batch", params=params, timeout=5)
        end = time.time()
        
        latency_ms = (end - start) * 1000
        success = response.status_code == 200
        
        return {
            'latency_ms': latency_ms,
            'success': success,
            'status_code': response.status_code
        }
    except Exception as e:
        end = time.time()
        return {
            'latency_ms': (end - start) * 1000,
            'success': False,
            'error': str(e)
        }

def benchmark_reads(rate_per_sec=1000, duration_sec=60, workers=10):
    """Benchmark API reads at specified rate"""
    print("=" * 60)
    print("BENCHMARK #2: LOW-LATENCY READS")
    print("=" * 60)
    print(f"Target Rate:     {rate_per_sec:,} req/sec")
    print(f"Duration:        {duration_sec} seconds")
    print(f"Workers:         {workers}")
    print(f"Expected Total:  {rate_per_sec * duration_sec:,} requests")
    print("=" * 60)
    print()
    
    latencies = []
    successes = 0
    failures = 0
    
    start_time = time.time()
    end_time = start_time + duration_sec
    last_report = start_time
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        
        try:
            while time.time() < end_time:
                batch_start = time.time()
                
                requests_per_batch = rate_per_sec // 10
                for _ in range(requests_per_batch):
                    if random.random() < 0.8:
                        future = executor.submit(measure_single_request)
                    else:
                        future = executor.submit(measure_batch_request)
                    futures.append(future)
                
                completed = []
                for future in futures[:]:
                    if future.done():
                        result = future.result()
                        latencies.append(result['latency_ms'])
                        if result['success']:
                            successes += 1
                        else:
                            failures += 1
                        completed.append(future)
                
                for future in completed:
                    futures.remove(future)
                
                current_time = time.time()
                if current_time - last_report >= 1.0:
                    elapsed = current_time - start_time
                    total_requests = successes + failures
                    actual_rate = total_requests / elapsed if elapsed > 0 else 0
                    progress = (elapsed / duration_sec) * 100
                    
                    if latencies:
                        p50 = statistics.median(latencies)
                        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) > 20 else max(latencies)
                        p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) > 100 else max(latencies)
                    else:
                        p50 = p95 = p99 = 0
                    
                    print(f"[{progress:5.1f}%] Requests: {total_requests:,} | "
                          f"Rate: {actual_rate:,.0f} req/sec | "
                          f"P50: {p50:.2f}ms | P95: {p95:.2f}ms | P99: {p99:.2f}ms")
                    last_report = current_time
                
                elapsed_batch = time.time() - batch_start
                sleep_time = max(0, 0.1 - elapsed_batch)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n\nStopping benchmark...")
        
        print("\nWaiting for pending requests...")
        for future in futures:
            try:
                result = future.result(timeout=5)
                latencies.append(result['latency_ms'])
                if result['success']:
                    successes += 1
                else:
                    failures += 1
            except:
                failures += 1
    
    total_time = time.time() - start_time
    total_requests = successes + failures
    actual_rate = total_requests / total_time if total_time > 0 else 0
    
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
    print("BENCHMARK #2 RESULTS")
    print("=" * 60)
    print(f"Duration:           {total_time:.2f} seconds")
    print(f"Total Requests:     {total_requests:,}")
    print(f"Successful:         {successes:,}")
    print(f"Failed:             {failures}")
    print(f"Success Rate:       {(successes/total_requests)*100:.2f}%")
    print(f"Actual Rate:        {actual_rate:,.2f} req/sec")
    print(f"Target Rate:        {rate_per_sec:,} req/sec")
    print(f"Achievement:        {(actual_rate/rate_per_sec)*100:.1f}%")
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
        print("⚠️  P99 latency above 10ms target")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='API Read Benchmark')
    parser.add_argument('--rate', type=int, default=1000,
                        help='Requests per second (default: 1000)')
    parser.add_argument('--duration', type=int, default=60,
                        help='Duration in seconds (default: 60)')
    parser.add_argument('--workers', type=int, default=10,
                        help='Concurrent workers (default: 10)')
    
    args = parser.parse_args()
    
    print("Checking if API is ready...")
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ API is ready\n")
                break
        except:
            pass
        print(f"Waiting for API... ({i+1}/{max_retries})")
        time.sleep(2)
    else:
        print("❌ API not reachable. Make sure it's running on port 8080")
        exit(1)
    
    benchmark_reads(args.rate, args.duration, args.workers)
