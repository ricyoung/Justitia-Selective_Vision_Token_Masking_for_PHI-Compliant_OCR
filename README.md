# Justitia: Selective Vision Token Masking for PHI-Compliant OCR

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![arXiv](https://img.shields.io/badge/arXiv-2025.xxxxx-b31b1b.svg)](https://arxiv.org/)

## Overview

**Justitia** is a research exploration of **vision-level token masking** for PHI (Protected Health Information) compliance in OCR systems. Unlike traditional text-based redaction methods that operate after OCR extraction, this approach investigates detecting and masking sensitive information at the vision token stage, attempting to prevent PHI from ever being processed by the language model decoder.

### Research Approach

The core idea is **selective vision token masking** - identifying and masking PHI tokens before they reach the text generation decoder. This approach theoretically could provide:

- **Stronger Privacy Guarantees**: PHI would never enter the text generation pipeline
- **Better Utility Preservation**: Non-PHI medical context could remain intact for downstream processing
- **Efficient Implementation**: LoRA adapters for lightweight PHI detection without modifying the base model

**Note**: This repository contains the implementation and data generation infrastructure. No actual model training was successfully completed. See [Project Status](#project-status) for details.

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

## What's Included

- **Synthetic Data Pipeline**: Fully functional pipeline using Synthea for generating realistic medical PDFs with PHI annotations
- **LoRA Architecture Code**: Implementation of LoRA adapters for vision token PHI detection (not trained)
- **PHI Annotation Tools**: Preprocessing pipeline for marking PHI in synthetic documents
- **Multiple Masking Strategies**: Code for token replacement and selective attention mechanisms (experimental)
- **HIPAA Safe Harbor Coverage**: Designed to handle all 18 HIPAA PHI identifier categories
- **Configuration Files**: Model and training configurations for DeepSeek-OCR integration

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

The primary working component is the data generation pipeline:

```bash
# Setup Synthea (synthetic patient generator)
bash scripts/setup_synthea.sh

# Generate synthetic patient data
bash scripts/generate_synthea_data.sh

# Convert to annotated PDFs
python scripts/generate_clinical_notes.py --output-dir data/pdfs --num-documents 1000
```

### Explore the Code

```bash
# View the LoRA adapter implementation
cat src/training/lora_phi_detector.py

# Check the PHI annotation tools
cat src/preprocessing/phi_annotator.py

# Review configuration files
cat config/training_config.yaml
```

**Note**: The training and inference pipelines are not functional. The code is provided for reference and future development.

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

## Project Status

**Current State**: Research prototype with functional data generation infrastructure. The LoRA-based vision token masking approach was implemented but not successfully trained.

### Completed
- [x] Project structure and configuration
- [x] Synthea integration for synthetic patient data
- [x] PDF generation pipeline with PHI annotations
- [x] PHI annotation and preprocessing tools
- [x] LoRA adapter architecture implementation (code only, not trained)

### Known Limitations
- No successful model training was completed
- The vision-level masking approach proved more challenging than anticipated
- Infrastructure and data generation are functional, but the core ML approach needs rethinking
- Alternative architectures or hybrid approaches may be required

### Future Directions
- Explore alternative masking strategies
- Investigate different vision encoder fine-tuning approaches
- Consider hybrid text-vision detection methods
- Benchmark against traditional OCR + NER pipelines

## Paper

A paper describing this work has been submitted for peer review. The paper, experimental results, and additional materials are available in the `not_uploaded/` directory (not included in this public repository).

## Citation

If you use this work in your research, please cite:

```bibtex
@article{justitia2025,
  title={Justitia: Selective Vision Token Masking for PHI-Compliant OCR},
  author={Your Name},
  journal={Under Review},
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
