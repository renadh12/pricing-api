#!/bin/bash
set -e

echo "========================================="
echo "  Pricing API - Complete Setup"
echo "========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "❌ Docker required but not installed. Aborting." >&2; exit 1; }
command -v mvn >/dev/null 2>&1 || { echo "❌ Maven required but not installed. Aborting." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python3 required but not installed. Aborting." >&2; exit 1; }

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install kafka-python redis requests python-snappy -q

# Start infrastructure
echo ""
echo "Starting Kafka, Redis, and Consumer..."
docker-compose down -v 2>/dev/null
docker-compose up -d

# Wait for Kafka
echo ""
echo "Waiting for Kafka to start (45 seconds)..."
sleep 45

# Create Kafka topic
echo ""
echo "Creating Kafka topic..."
docker exec kafka kafka-topics --create \
  --bootstrap-server localhost:9092 \
  --topic price-updates \
  --partitions 10 \
  --replication-factor 1 \
  --if-not-exists 2>/dev/null || true

# Build Spring Boot app
echo ""
echo "Building Pricing API..."
mvn clean install -q -DskipTests

echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "  1. Start API (in new terminal):"
echo "     mvn spring-boot:run"
echo ""
echo "  2. Run Benchmark #1 - High-Frequency Writes:"
echo "     python3 producer.py --rate 1000 --duration 180"
echo ""
echo "  3. Run Benchmark #2 - Low-Latency Reads:"
echo "     python3 benchmark_reads.py --rate 500 --duration 180"
echo ""