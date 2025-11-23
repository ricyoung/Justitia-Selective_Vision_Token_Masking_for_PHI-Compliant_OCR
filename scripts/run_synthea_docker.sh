#!/bin/bash

# Run Synthea using Docker (alternative to local Java installation)

PATIENTS=${1:-100}
STATE=${2:-Massachusetts}
OUTPUT_DIR=${3:-./data/synthetic/synthea}

echo "Running Synthea in Docker..."
echo "Patients: $PATIENTS"
echo "State: $STATE"
echo "Output: $OUTPUT_DIR"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Run Synthea in Docker container
docker run --rm \
    -v "$(pwd)/$OUTPUT_DIR:/output" \
    synthetichealth/synthea:latest \
    -p $PATIENTS \
    -s $STATE \
    --exporter.baseDirectory=/output

echo "✓ Generation complete!"
echo "Files saved to: $OUTPUT_DIR"
