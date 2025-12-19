# Pricing API - High-Frequency System

Real-time pricing system demonstrating high-frequency writes and low-latency reads.

## Architecture

### Data Flow
```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   Producer      │      │      Kafka       │      │    Consumer     │
│   (Python)      │─────▶│  Message Broker  │─────▶│    (Python)     │
│  Simulates      │      │  10 Partitions   │      │    (Docker)     │
│  Market Data    │      │                  │      │                 │
└─────────────────┘      └──────────────────┘      └────────┬────────┘
   High-frequency                                            │
   Price Updates                                             ▼
                                                   ┌─────────────────┐
                                                   │      Redis      │
                                                   │  In-Memory Cache│
                                                   │                 │
                                                   └────────┬────────┘
                                                            │
                                                            ▼
                  ┌──────────────┐              ┌────────────────────┐
                  │   Clients    │              │   Pricing API      │
                  │  - AlgoTrade │◀─────────────│   (Spring Boot)    │
                  │  - Execution │     REST     │   Java 21          │
                  │  - Smart     ây) | Low-latency cache |
| **Pricing API** | Spring Boot 3.4 + Java 21 | REST endpoints for price lookups |

### API Endpoints

- `GET /api/v1/prices/{symbol}` - Single price lookup
- `GET /api/v1/prices/batch?symbols=A,B,C` - Batch lookup (optimized with Redis MGET)
- `GET /api/v1/prices/health` - Health check

### Key Features

- **Rate Limiting:** 10,000 req/sec capacity (Guava RateLimiter)
- **Connection Pooling:** Redis Lettuce pool (100 max connections)
- **Stateless API:** Horizontal scaling ready
- **Replay Capability:** Kafka persistent log

### Design Decisions

**Kafka over direct writes:** Replay capability, producer/consumer decoupling, persistent log  
**Python consumer:** Simpler than Kafka Connect, easy to understand and debug  
**REST API:** Adequate for requirements, simpler client integration  
**Blocking Redis:** Sufficient performance, cleaner code  

### Future Optimizations

1. **Reactive Redis:** Non-blocking I/O for lower latency
2. **WebSocket:** Real-time streaming for UI/AlgoTrading
3. **Redis Pipelining:** Batch operations for higher throughput

---

## Quick Start (5 Minutes)

### Prerequisites
- Docker Desktop
- Java 21
- Maven
- Python 3.x

### Setup
```bash
# Clone repository
git clone https://github.com/renadh12/pricing-api.git
cd pricing-api

# Run automated setup
./setup.sh

# Start API (new terminal)
mvn spring-boot:run
```

Wait for: `Started PricingApiApplication`

### Validate Setup
```bash
# Check Docker containers are running
docker ps

# Test API health
curl http://localhost:8080/api/v1/prices/health

# Test single price (after running producer)
curl http://localhost:8080/api/v1/prices/AAPL

# Test batch prices (after running producer)
curl "http://localhost:8080/api/v1/prices/batch?symbols=AAPL,GOOGL,MSFT"
```

### Benchmark
```bash
# Benchmark #1: High-Frequency Writes (3 min)
python3 producer.py --rate 1000 --duration 180

# Benchmark #2: Low-Latency Reads (3 min)
python3 benchmark_reads.py --rate 500 --duration 180
```

<details>
<summary>Sample Benchmark Results (Not Conclusive)</summary>

**Test Environment:** MacBook Pro, Local Docker, 2-minute runs

### Benchmark #1: High-Frequency Writes

| Metric | Value |
|--------|-------|
| Duration | 120 seconds |
| Messages Sent | 97,839 |
| Actual Rate | 815 msg/sec |
| Target Rate | 1,000 msg/sec |
| Achievement | 81.5% |
| Errors | 0 |

### Benchmark #2: Low-Latency Reads

| Metric | Value |
|--------|-------|
| Duration | 189 seconds |
| Total Requests | 57,800 |
| Success Rate | 100% |
| Actual Rate | 306 req/sec |
| Target Rate | 500 req/sec |
| Achievement | 61.2% |

**Latency:**
- P50: 25ms
- P95: 65ms
- P99: 94ms

**Note:** Results vary based on system resources. Run benchmarks on your machine for accurate metrics.

</details>