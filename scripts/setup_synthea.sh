#!/bin/bash

# Setup script for Synthea synthetic patient generator
# This script downloads and configures Synthea for generating synthetic medical records

set -e  # Exit on error

echo "=========================================="
echo "Setting up Synthea for Justitia PHI-OCR"
echo "=========================================="

# Check Java installation
echo "Checking Java installation..."
if ! command -v java &> /dev/null; then
    echo "Error: Java is not installed. Please install Java JDK 11 or newer."
    echo "Visit: https://www.oracle.com/java/technologies/downloads/"
    exit 1
fi

JAVA_VERSION=$(java -version 2>&1 | head -n 1 | cut -d'"' -f2)
echo "Found Java version: $JAVA_VERSION"

# Create external directory if it doesn't exist
EXTERNAL_DIR="external"
if [ ! -d "$EXTERNAL_DIR" ]; then
    echo "Creating external directory..."
    mkdir -p "$EXTERNAL_DIR"
fi

cd "$EXTERNAL_DIR"

# Clone Synthea if not already present
if [ ! -d "synthea" ]; then
    echo "Cloning Synthea repository..."
    git clone https://github.com/synthetichealth/synthea.git
    cd synthea
else
    echo "Synthea directory already exists. Updating..."
    cd synthea
    git pull
fi

# Build Synthea
echo "Building Synthea (this may take a few minutes)..."
./gradlew build -x test

# Create custom configuration for PHI-heavy output
echo "Creating custom Synthea configuration..."
cat > src/main/resources/synthea_phi_config.properties << 'EOF'
# Custom Synthea configuration for PHI detection training

# Generate complete patient information
generate.demographics = true
generate.vital_signs = true
generate.medications = true
generate.conditions = true
generate.allergies = true
generate.procedures = true
generate.immunizations = true
generate.encounters = true
generate.imaging_studies = true
generate.devices = true
generate.supplies = true

# Export formats (we want multiple formats for diverse training)
exporter.ccda.export = true
exporter.fhir.export = true
exporter.csv.export = true
exporter.text.export = true
exporter.pdf.export = false  # We'll generate our own PDFs

# Include all PHI fields
exporter.csv.included_files = patients,encounters,conditions,medications,procedures,immunizations,allergies,devices,supplies
exporter.csv.append_mode = false

# Generate diverse demographics
generate.demographics.socioeconomic.weights.income = 1,1,1,1,1
generate.demographics.socioeconomic.weights.education = 1,1,1,1,1

# Location settings (generate diverse addresses)
generate.geography.country = United States
generate.geography.state = Massachusetts  # Can be changed

# Age distribution
generate.demographics.min_age = 0
generate.demographics.max_age = 100

# Keep all history
generate.log_patients = true
generate.keep_patients = true
EOF

# Create a generation script
echo "Creating generation script..."
cd ../..
cat > scripts/generate_synthea_data.sh << 'EOF'
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
EOF

chmod +x scripts/generate_synthea_data.sh

# Test Synthea with a small generation
echo "Testing Synthea with 5 patients..."
cd external/synthea
./run_synthea -p 5 -s Massachusetts --exporter.baseDirectory="../../data/synthetic/test"

# Check if test was successful
if [ -d "../../data/synthetic/test" ]; then
    echo "✓ Synthea test successful!"
    echo "  Generated test files in data/synthetic/test/"
else
    echo "✗ Synthea test failed. Please check the output above for errors."
    exit 1
fi

cd ../..

echo ""
echo "=========================================="
echo "Synthea Setup Complete!"
echo "=========================================="
echo ""
echo "To generate synthetic patients, run:"
echo "  ./scripts/generate_synthea_data.sh [num_patients] [state] [output_dir]"
echo ""
echo "Example:"
echo "  ./scripts/generate_synthea_data.sh 1000 California ./data/synthetic/patients"
echo ""
echo "Next steps:"
echo "1. Generate synthetic patient data"
echo "2. Run the PDF generation script to convert to PDFs with PHI"
echo "3. Use the PDFs for training the LoRA adapter"
echo ""