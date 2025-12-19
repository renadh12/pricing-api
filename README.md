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
# 1. Run automated setup
./setup.sh

# 2. Start API (new terminal)
cd pricing-api && mvn spring-boot:run
```

Wait for: `Started PricingApiApplication`

### Benchmark
```bash
# Benchmark #1: High-Frequency Writes (30 sec)
python3 producer.py --rate 1000 --duration 30

# Benchmark #2: Low-Latency Reads (60 sec)
python3 benchmark_reads.py --rate 500 --duration 60
```

### Test API Manually
```bash
# Single price
curl http://localhost:8080/api/v1/prices/AAPL

# Batch prices
curl "http://localhost:8080/api/v1/prices/batch?symbols=AAPL,GOOGL,MSFT"

# Health check
curl http://localhost:8080/api/v1/prices/health
```
