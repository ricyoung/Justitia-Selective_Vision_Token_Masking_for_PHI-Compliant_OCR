# Vision Token Masking Cannot Prevent PHI Leakage: A Negative Result

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Paper](https://img.shields.io/badge/paper-under%20review-red.svg)](https://deepneuro.ai/richard)

> **Author**: Richard J. Young
> **Affiliation**: Founding AI Scientist, [DeepNeuro.AI](https://deepneuro.ai/richard) | University of Nevada, Las Vegas, Department of Neuroscience
> **Links**: [HuggingFace](https://huggingface.co/richardyoung) | [DeepNeuro.AI](https://deepneuro.ai/richard)

## Overview

This repository contains the systematic evaluation code and data generation pipeline for our paper **"Vision Token Masking Alone Cannot Prevent PHI Leakage in Medical Document OCR"**.

**Key Finding**: Vision-level token masking in VLMs achieves only **42.9% PHI reduction** regardless of masking strategy, successfully suppressing long-form identifiers (names, addresses) at 100% effectiveness while completely failing on short structured identifiers (SSN, medical record numbers) at 0% effectiveness.

### The Negative Result

We evaluated **seven masking strategies** (V3-V9) across different architectural layers of DeepSeek-OCR using 100 synthetic medical billing statements (from a corpus of 38,517 annotated documents):

- **What Worked**: 100% reduction of patient names, dates of birth, physical addresses (spatially-distributed long-form PHI)
- **What Failed**: 0% reduction of SSN, medical record numbers, email addresses, account numbers (short structured identifiers)
- **The Ceiling**: All strategies converged to 42.9% total PHI reduction
- **Why**: Language model contextual inference—not insufficient visual masking—drives structured identifier leakage

This establishes **fundamental boundaries** for vision-only privacy interventions in VLMs and redirects future research toward decoder-level fine-tuning and hybrid defense-in-depth architectures.

## Architecture

```
Input PDF → Vision Encoder → PHI Detection → Vision Token Masking → DeepSeek Decoder → Text Output
              (SAM + CLIP)    (Ground Truth)   (V3-V9 Strategies)      (3B-MoE)
```

### Experimental Approach

1. **Base Model**: DeepSeek-OCR
   - Vision Encoder: SAM-base + CLIP-large blocks
   - Text Decoder: DeepSeek-3B-MoE
   - Processes 1024×1024 images to 256 vision tokens

2. **PHI Detection**: Ground-truth annotations from synthetic data generation
   - Perfect bounding box annotations for all 18 HIPAA PHI categories
   - No learned detection model - direct annotation-based masking

3. **Seven Masking Strategies (V3-V9)**:
   - **V3-V5**: SAM encoder blocks at different depths
   - **V6**: Compression layer (4096→1024 tokens)
   - **V7**: Dual vision encoders (SAM + CLIP)
   - **V8**: Post-compression stage
   - **V9**: Projector fusion layer

## Research Contributions

### What This Work Provides

1. **First Systematic Evaluation** of vision-level token masking for PHI protection in VLMs
2. **Negative Result**: Establishes that vision masking alone is insufficient for HIPAA compliance
3. **Boundary Conditions**: Identifies which PHI types are amenable to vision-level vs language-level redaction
4. **38,517 Annotated Documents**: Massive synthetic medical document corpus with ground-truth PHI annotations
5. **Seven Masking Strategies**: V3-V9 targeting SAM encoders, compression layers, dual vision encoders, and projector fusion
6. **Ablation Studies**: Mask expansion radius variations (r=1,2,3) demonstrating spatial coverage limitations
7. **Hybrid Architecture Simulation**: Shows 88.6% reduction when combining vision masking with NLP post-processing

### What's in This Repository

- **Synthetic Data Pipeline**: Fully functional Synthea-based pipeline generating 38,517+ annotated medical PDFs
- **PHI Annotation Tools**: Ground-truth annotation pipeline for all 18 HIPAA identifier categories
- **Evaluation Framework**: Code for measuring PHI reduction across masking strategies
- **Configuration Files**: DeepSeek-OCR integration and experimental parameters

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

DeepSeek-OCR compresses a 1024×1024 image through multiple stages:
1. **SAM-base block**: Windowed attention for local detail (4096 tokens)
2. **CLIP-large block**: Global attention for layout understanding (1024 tokens)
3. **Convolution layer**: 16x token reduction to 256 tokens
4. **Projector fusion**: Maps vision tokens to language model space

Each vision token represents a ~64×64 pixel region with semantic and spatial information.

### Masking Implementation

Vision tokens corresponding to PHI bounding boxes are zeroed at different architectural layers (V3-V9). Ablation studies tested mask expansion radius r=1,2,3 to determine if spatial coverage affects reduction rates.

## Experimental Results

### Main Findings

| Masking Strategy | Layer Target | PHI Reduction | Names | DOB | SSN | MRN | Addresses |
|-----------------|--------------|---------------|-------|-----|-----|-----|-----------|
| **V3-V9 (all)** | Various | **42.9%** | 100% | 100% | 0% | 0% | 100% |
| Baseline | None | 0% | 0% | 0% | 0% | 0% | 0% |
| Hybrid (sim) | Vision + NLP | **88.6%** | 100% | 100% | 80% | 80% | 100% |

### Key Insights

1. **Convergence**: All seven masking strategies (V3-V9) achieved identical 42.9% reduction regardless of architectural layer
2. **Spatial Invariance**: Mask expansion radius (r=1,2,3) did not improve reduction beyond this ceiling
3. **Type-Dependent Success**:
   - ✅ Long-form spatially-distributed PHI: 100% reduction
   - ❌ Short structured identifiers: 0% reduction
4. **Root Cause**: Language model contextual inference reconstructs masked structured identifiers from document context

### Implications for Privacy-Preserving VLMs

- Vision-only masking is **insufficient for HIPAA compliance** (requires 99%+ reduction)
- Hybrid architectures combining vision masking with NLP post-processing are necessary
- Future work should focus on decoder-level fine-tuning or defense-in-depth approaches

## Paper

A paper describing this work has been submitted for peer review. The paper, experimental results, and additional materials are available in the `not_uploaded/` directory (not included in this public repository).

## Citation

If you use this work in your research, please cite:

```bibtex
@article{young2025visionmasking,
  title={Vision Token Masking Alone Cannot Prevent PHI Leakage in Medical Document OCR: A Systematic Evaluation},
  author={Young, Richard J.},
  institution={DeepNeuro.AI; University of Nevada, Las Vegas},
  journal={Under Review},
  year={2025},
  note={Code available at: https://github.com/ricyoung/Justitia-Selective_Vision_Token_Masking_for_PHI-Compliant_OCR}
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

**Richard J. Young**
- Founding AI Scientist, DeepNeuro.AI
- University of Nevada, Las Vegas, Department of Neuroscience
- Website: [deepneuro.ai/richard](https://deepneuro.ai/richard)
- HuggingFace: [@richardyoung](https://huggingface.co/richardyoung)
- GitHub: Open an issue on this repository

---

**Note**: The `not_uploaded/` directory contains paper drafts, experimental results, and other materials not included in the public repository.
