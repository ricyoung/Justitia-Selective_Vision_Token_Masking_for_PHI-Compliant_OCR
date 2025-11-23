#!/bin/bash

# Script to generate synthetic patient data using Synthea

PATIENTS=${1:-100}
STATE=${2:-Massachusetts}
OUTPUT_DIR=${3:-./data/synthetic/synthea}

echo "Generating $PATIENTS synthetic patients from $STATE..."

# Ensure output directory exists
mkdir -p "$OUTPUT_DIR"

# Run Synthea
cd external/synthea
./run_synthea -p "$PATIENTS" -s "$STATE" --exporter.baseDirectory="../../$OUTPUT_DIR"

echo "Generation complete. Output saved to $OUTPUT_DIR"

# Count generated files
echo "Generated files:"
find "../../$OUTPUT_DIR" -type f -name "*.json" | wc -l | xargs echo "  FHIR bundles:"
find "../../$OUTPUT_DIR" -type f -name "*.xml" | wc -l | xargs echo "  C-CDA documents:"
find "../../$OUTPUT_DIR" -type f -name "*.csv" | wc -l | xargs echo "  CSV files:"

echo "Done!"
