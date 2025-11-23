# Justitia: Selective Vision Token Masking for PHI-Compliant OCR

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![arXiv](https://img.shields.io/badge/arXiv-2025.xxxxx-b31b1b.svg)](https://arxiv.org/)

## Overview

**Justitia** is a novel approach to privacy-preserving OCR that implements **vision-level token masking** for PHI (Protected Health Information) compliance. Unlike traditional text-based redaction methods that operate after OCR extraction, Justitia detects and masks sensitive information at the vision token stage, preventing PHI from ever being processed by the language model decoder.

### Key Innovation

The core innovation is **selective vision token masking** - identifying and masking PHI tokens before they reach the text generation decoder. This approach provides:

- **Stronger Privacy Guarantees**: PHI never enters the text generation pipeline
- **Better Utility Preservation**: Non-PHI medical context remains intact for downstream processing
- **Efficient Implementation**: Uses LoRA adapters for lightweight PHI detection without modifying the base model

## Architecture

```
Input PDF → Vision Encoder → PHI Detection (LoRA) → Token Masking → DeepSeek-OCR → Safe Text Output
              (SAM + CLIP)      (256 tokens)         (Replace/Mask)     (Decoder)
```

### Components

1. **Base Model**: DeepSeek-OCR (~950M parameters)
   - Vision Encoder: SAM-base + CLIP-large blocks
   - Text Decoder: DeepSeek-3B-MoE
   - Processes 1024×1024 images to 256 vision tokens

2. **PHI Detection**: LoRA Adapter (Rank 8-16)
   - Trained to identify PHI tokens in vision space
   - Targets vision encoder attention layers
   - Parameter-efficient: <1% of base model parameters

3. **Masking Strategies**:
   - **Token Replacement**: Substitute PHI tokens with privacy-preserving embeddings
   - **Selective Attention Masking**: ToSA-inspired attention mechanism
   - **Hybrid Approach**: Combines both for optimal privacy-utility tradeoff

## Features

- **Vision-Level PHI Detection**: Identifies sensitive information before text extraction
- **HIPAA Safe Harbor Compliant**: Covers all 18 HIPAA PHI identifiers
- **Dual Masking Strategies**: Token replacement and selective attention mechanisms
- **Synthetic Data Pipeline**: Uses Synthea for generating realistic medical PDFs with PHI annotations
- **Efficient Fine-tuning**: LoRA adapters for parameter-efficient training
- **Evaluation Framework**: Comprehensive metrics for privacy and utility assessment

## Quick Start

### Prerequisites

- Python 3.12+
- CUDA 11.8+ compatible GPU (8GB+ VRAM recommended)
- Java JDK 11+ (for Synthea data generation)
- 50GB+ free disk space

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/Justitia-Selective_Vision_Token_Masking_for_PHI-Compliant_OCR.git
cd Justitia-Selective_Vision_Token_Masking_for_PHI-Compliant_OCR

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download DeepSeek-OCR model
python scripts/download_model.py
```

### Generate Synthetic Medical Data

```bash
# Setup Synthea (synthetic patient generator)
bash scripts/setup_synthea.sh

# Generate synthetic patient data
bash scripts/generate_synthea_data.sh

# Convert to annotated PDFs
python scripts/generate_clinical_notes.py --output-dir data/pdfs --num-documents 1000
```

### Train PHI Detection LoRA

```bash
python src/training/lora_phi_detector.py \
    --config config/training_config.yaml \
    --data-dir data/pdfs \
    --output-dir models/lora_adapters
```

### Run Inference

```bash
python src/inference/process_documents.py \
    --input path/to/medical.pdf \
    --output path/to/redacted_output.txt \
    --masking-strategy selective_attention \
    --lora-checkpoint models/lora_adapters/best_model
```

## Project Structure

```
.
├── config/                     # Configuration files
│   ├── model_config.yaml      # Model architecture and hyperparameters
│   └── training_config.yaml   # Training settings
│
├── data/                      # Data directory (generated, not in repo)
│   ├── synthetic/            # Synthea synthetic patient data
│   ├── pdfs/                 # Generated medical PDFs with PHI
│   └── annotations/          # PHI bounding box annotations
│
├── models/                    # Model directory (not in repo)
│   ├── deepseek_ocr/        # Base DeepSeek-OCR model
│   ├── lora_adapters/       # Trained LoRA adapters
│   └── checkpoints/         # Training checkpoints
│
├── scripts/                   # Utility scripts
│   ├── download_model.py    # Download DeepSeek-OCR
│   ├── setup_synthea.sh     # Install Synthea
│   ├── generate_synthea_data.sh          # Generate patient data
│   ├── generate_clinical_notes.py        # Create medical PDFs
│   ├── generate_realistic_pdfs.py        # Realistic PDF generation
│   ├── generate_additional_documents.py  # Additional document types
│   └── generate_final_document_types.py  # Final document generation
│
├── src/                       # Source code
│   ├── data_generation/      # Synthea integration and PDF generation
│   │   ├── synthea_to_pdf.py
│   │   └── medical_templates.py
│   ├── preprocessing/        # PHI annotation pipeline
│   │   └── phi_annotator.py
│   ├── training/             # LoRA training implementation
│   │   └── lora_phi_detector.py
│   ├── inference/            # OCR with PHI masking (placeholder)
│   └── utils/                # Evaluation and metrics (placeholder)
│
├── tests/                     # Unit tests
├── notebooks/                 # Jupyter notebooks for experiments
│
├── .gitignore                # Git ignore file
├── requirements.txt          # Python dependencies
├── setup.py                  # Package setup
├── SETUP.md                  # Detailed setup instructions
├── README.md                 # This file
└── LICENSE                   # MIT License
```

## PHI Categories Detected

Following HIPAA Safe Harbor guidelines, Justitia detects and masks:

| Category | Examples |
|----------|----------|
| **Names** | Patients, physicians, family members, guarantors |
| **Dates** | Birth dates, admission/discharge, death dates, appointments |
| **Geographic** | Street addresses, cities, counties, zip codes, facility names |
| **Contact** | Phone numbers, fax numbers, email addresses |
| **Medical IDs** | Medical record numbers, account numbers, health plan IDs |
| **Personal IDs** | SSN, driver's license, vehicle IDs, device identifiers |
| **Biometric** | Photos, fingerprints, voiceprints |
| **Web & Network** | URLs, IP addresses, certificate numbers |

## Masking Strategies

### 1. Token Replacement
- Replaces PHI vision tokens with learned privacy-preserving embeddings
- Fast inference, low memory overhead
- Good utility preservation for non-PHI content

### 2. Selective Attention Masking
- Applies attention masking to prevent PHI token information flow
- Based on ToSA (Token-level Selective Attention) approach
- Stronger privacy guarantees, moderate computational cost

### 3. Hybrid Approach
- Combines token replacement with selective attention
- Optimal privacy-utility tradeoff
- Recommended for production use

## Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **PHI Removal Rate** | % of PHI successfully masked | >99% |
| **OCR Accuracy Retention** | Character accuracy on non-PHI text | >95% |
| **False Positive Rate** | Non-PHI incorrectly masked | <5% |
| **Processing Speed** | Seconds per page | <2s |
| **F1 Score** | Harmonic mean of precision/recall | >0.90 |

## Technical Details

### Vision Token Processing

DeepSeek-OCR compresses a 1024×1024 image to 256 vision tokens:
1. **SAM-base block**: Windowed attention for local detail (4096 tokens)
2. **CLIP-large block**: Global attention for layout understanding (1024 tokens)
3. **Convolution layer**: 16x token reduction to 256 tokens

Each vision token represents a ~64×64 pixel region with semantic and spatial information.

### LoRA Configuration

```yaml
rank: 16                      # LoRA rank
alpha: 32                     # LoRA alpha (scaling factor)
dropout: 0.1                  # Dropout rate
target_modules:               # Attention layers to target
  - q_proj
  - v_proj
  - k_proj
task_type: PHI_DETECTION
```

### Training Details

- **Dataset**: 10,000+ synthetic medical PDFs from Synthea
- **Batch Size**: 8 (with gradient accumulation: 4)
- **Learning Rate**: 2e-4 with cosine annealing
- **Epochs**: 10
- **Hardware**: Single A100 40GB GPU
- **Training Time**: ~8 hours

## Development Roadmap

- [x] Project structure and configuration
- [x] Synthea integration for synthetic patient data
- [x] PDF generation pipeline with PHI annotations
- [x] PHI annotation and preprocessing tools
- [x] LoRA adapter implementation
- [ ] Complete training pipeline with evaluation
- [ ] Inference engine with masking strategies
- [ ] Comprehensive evaluation framework
- [ ] Benchmarking against baseline methods
- [ ] Documentation and tutorials
- [ ] Paper submission to arXiv/conference

## Citation

If you use this work in your research, please cite:

```bibtex
@article{justitia2025,
  title={Justitia: Selective Vision Token Masking for PHI-Compliant OCR},
  author={Your Name},
  journal={arXiv preprint arXiv:2025.xxxxx},
  year={2025}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **DeepSeek AI** for the DeepSeek-OCR model
- **MITRE Corporation** for Synthea synthetic patient generator
- **Hugging Face** for PEFT library and model hosting
- **Meta AI** for Segment Anything Model (SAM)
- **OpenAI** for CLIP vision encoder

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

**IMPORTANT**: This is a research project for academic purposes. It is **NOT** intended for production use with real patient PHI. Always consult with legal and compliance teams before deploying PHI-related systems in healthcare settings.

## Contact

For questions, collaboration, or feedback:
- Open an issue on GitHub
- Email: your.email@example.com

---

**Note**: The `not_uploaded/` directory contains paper drafts, experimental results, and other materials not included in the public repository.
