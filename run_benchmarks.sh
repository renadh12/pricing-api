#!/bin/bash

echo "========================================="
echo "  AUTOMATED BENCHMARK DEMO"
echo "========================================="
echo ""
echo "This will run both benchmarks automatically."
echo "Make sure you have:"
echo "  1. Started infrastructure: ./setup.sh"
echo "  2. Started API: mvn spring-boot:run (in pricing-api/)"
echo "  3. Installed deps: pip install -r requirements.txt"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

echo "========================================="
echo "Starting Benchmark #1: High-Frequency Writes"
echo "========================================="
python producer.py --rate 1000 --duration 30
echo ""
echo "Waiting 5 seconds before Benchmark #2..."
sleep 5
echo ""

echo "========================================="
echo "Starting Benchmark #2: Low-Latency Reads"
echo "========================================="
python benchmark_reads.py --rate 1000 --duration 30

echo ""
echo "========================================="
echo "  BENCHMARKS COMPLETE"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✅ Benchmark #1: High-frequency writes to Kafka"
echo "  ✅ Benchmark #2: Low-latency reads from API"
echo ""
echo "Check results above for detailed metrics."
echo ""
