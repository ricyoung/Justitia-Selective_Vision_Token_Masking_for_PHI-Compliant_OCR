#!/bin/bash

# Convert Synthea output to medical PDFs with PHI annotations

SYNTHEA_DIR=${1:-./data/synthetic/patients}
PDF_DIR=${2:-./data/pdfs}
ANNOTATION_DIR=${3:-./data/annotations}
NUM_DOCS=${4:-500}

echo "Converting Synthea data to medical PDFs..."
echo "Synthea output: $SYNTHEA_DIR"
echo "PDF output: $PDF_DIR"
echo "Annotations: $ANNOTATION_DIR"
echo "Documents to generate: $NUM_DOCS"
echo ""

# Create output directories
mkdir -p "$PDF_DIR"
mkdir -p "$ANNOTATION_DIR"

# Run the PDF generator
python src/data_generation/synthea_to_pdf.py \
    --synthea-output "$SYNTHEA_DIR" \
    --pdf-output "$PDF_DIR" \
    --annotations-output "$ANNOTATION_DIR" \
    --num-documents "$NUM_DOCS"

echo ""
echo "✓ PDF generation complete!"
echo ""
echo "Generated files:"
find "$PDF_DIR" -name "*.pdf" | wc -l | xargs echo "  PDFs:"
find "$ANNOTATION_DIR" -name "*.json" | wc -l | xargs echo "  Annotations:"
echo ""
echo "Next steps:"
echo "  1. Review PDFs: ls $PDF_DIR"
echo "  2. Check annotations: ls $ANNOTATION_DIR"
echo "  3. Start training: python src/training/train_lora.py"
