#!/bin/bash
set -e

echo "========================================="
echo "  Pricing API Benchmark - Quick Setup"
echo "========================================="
echo ""

echo "1. Starting Kafka, Redis, and Consumer..."
docker-compose up -d

echo ""
echo "2. Waiting for services to start (30 seconds)..."
sleep 30

echo ""
echo "3. Creating Kafka topic..."
docker exec -it kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic price-updates \
  --partitions 10 \
  --replication-factor 1 \
  --if-not-exists || true

echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "Services running:"
echo "  - Kafka:          localhost:9092"
echo "  - Redis:          localhost:6379"
echo "  - Kafka Consumer: Running in Docker"
echo ""
echo "Next steps:"
echo "  1. Start Pricing API: cd pricing-api && mvn spring-boot:run"
echo "  2. Run Benchmark #1 (writes): python producer.py --rate 1000 --duration 60"
echo "  3. Run Benchmark #2 (reads):  python benchmark_reads.py --rate 1000 --duration 60"
echo ""
