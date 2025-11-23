# Justitia PHI-OCR Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Synthea Setup](#synthea-setup)
4. [Model Download](#model-download)
5. [Data Generation](#data-generation)
6. [Training Setup](#training-setup)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **Python**: 3.12 or newer
- **RAM**: 16GB minimum (32GB recommended)
- **Storage**: 50GB+ free space
- **GPU**: NVIDIA GPU with 8GB+ VRAM (optional but recommended)
  - CUDA 11.8 or newer
  - cuDNN 8.6 or newer

### Software Requirements
- Git
- Java JDK 11+ (for Synthea)
- Python virtual environment tool (venv, conda, etc.)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Justitia-PHI-OCR.git
cd Justitia-Selective_Vision_Token_Masking_for_PHI-Compliant_OCR
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n justitia python=3.12
conda activate justitia
```

### 3. Install Python Dependencies

```bash
# Install base requirements
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Install Flash Attention (optional but recommended for speed)
pip install flash-attn==2.7.3 --no-build-isolation
```

### 4. Verify Installation

```bash
python -c "import torch; print(f'PyTorch: {torch.__version__}')"
python -c "import transformers; print(f'Transformers: {transformers.__version__}')"
python -c "import peft; print(f'PEFT: {peft.__version__}')"
```

If CUDA is available:
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

## Synthea Setup

Synthea generates synthetic patient data with realistic PHI for training.

### Automatic Setup

```bash
# Run the setup script
./scripts/setup_synthea.sh
```

### Manual Setup

If the automatic setup fails:

```bash
# 1. Create external directory
mkdir -p external
cd external

# 2. Clone Synthea
git clone https://github.com/synthetichealth/synthea.git
cd synthea

# 3. Build Synthea
./gradlew build -x test

# 4. Test generation
./run_synthea -p 5

cd ../..
```

### Generate Synthetic Patients

```bash
# Generate 1000 patients from Massachusetts
./scripts/generate_synthea_data.sh 1000 Massachusetts ./data/synthetic/patients

# Generate from different states for diversity
./scripts/generate_synthea_data.sh 500 California ./data/synthetic/ca_patients
./scripts/generate_synthea_data.sh 500 Texas ./data/synthetic/tx_patients
```

## Model Download

### Download DeepSeek-OCR

```bash
# Download the model
python scripts/download_model.py

# Verify download
python scripts/download_model.py --test-only
```

### Alternative: Manual Download

If automatic download fails:

```bash
# Using Hugging Face CLI
pip install huggingface-hub
huggingface-cli download deepseek-ai/DeepSeek-OCR --local-dir ./models/deepseek_ocr
```

## Data Generation

### 1. Generate Synthetic Medical PDFs

```bash
# Convert Synthea data to PDFs with PHI
python src/data_generation/synthea_to_pdf.py \
    --synthea-output data/synthetic/patients \
    --pdf-output data/pdfs \
    --annotations-output data/annotations \
    --num-documents 5000
```

### 2. Create Training/Validation Split

```bash
# Split data into train/val/test sets
python scripts/split_data.py \
    --input-dir data/pdfs \
    --output-dir data/split \
    --train-ratio 0.8 \
    --val-ratio 0.1 \
    --test-ratio 0.1
```

## Training Setup

### 1. Configure Training Parameters

Edit `config/training_config.yaml` to adjust:
- Batch size (based on your GPU memory)
- Learning rate
- Number of epochs
- LoRA rank

### 2. Start Training

```bash
# Train the LoRA adapter
python src/training/train_lora.py \
    --config config/training_config.yaml \
    --data-dir data/split \
    --output-dir models/lora_adapters/experiment_1
```

### 3. Monitor Training

```bash
# If using Weights & Biases
wandb login  # First time only

# If using TensorBoard
tensorboard --logdir logs/tensorboard
```

### 4. Distributed Training (Multiple GPUs)

```bash
# Using accelerate
accelerate config  # Configure multi-GPU setup
accelerate launch src/training/train_lora.py --config config/training_config.yaml
```

## Quick Start Script

For a complete setup from scratch:

```bash
#!/bin/bash
# save as quick_setup.sh

echo "Setting up Justitia PHI-OCR..."

# 1. Create virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt
pip install -e .

# 3. Setup Synthea
./scripts/setup_synthea.sh

# 4. Download model
python scripts/download_model.py

# 5. Generate test data
./scripts/generate_synthea_data.sh 100
python src/data_generation/synthea_to_pdf.py --num-documents 100

echo "Setup complete! You can now start training."
```

## Troubleshooting

### Common Issues

#### 1. CUDA Out of Memory

Reduce batch size in `config/training_config.yaml`:
```yaml
training:
  batch_size: 4  # Reduce from 8
  gradient_accumulation_steps: 8  # Increase to maintain effective batch size
```

#### 2. Flash Attention Installation Failed

Flash Attention is optional. If installation fails:
```bash
# Edit config/model_config.yaml
optimization:
  use_flash_attention: false
```

#### 3. Synthea Build Failed

Ensure Java is installed:
```bash
java -version  # Should show Java 11 or newer

# On Ubuntu/Debian
sudo apt-get install openjdk-11-jdk

# On macOS
brew install openjdk@11
```

#### 4. Model Download Timeout

Try alternative sources:
```bash
python scripts/download_model.py --model-name unsloth/DeepSeek-OCR
```

#### 5. ImportError for Custom Modules

Ensure the package is installed in development mode:
```bash
pip install -e .
```

### GPU Memory Requirements

| Configuration | VRAM Required | Batch Size | Notes |
|--------------|---------------|------------|-------|
| Full Training | 40GB+ | 8-16 | A100 recommended |
| LoRA Training | 16-24GB | 4-8 | RTX 3090/4090 |
| LoRA Training (8-bit) | 8-12GB | 2-4 | RTX 3070/3080 |
| CPU Training | System RAM | 1-2 | Very slow |

### Performance Optimization

1. **Enable Mixed Precision**:
```yaml
training:
  mixed_precision:
    enabled: true
    dtype: "fp16"  # or "bf16" for newer GPUs
```

2. **Use Gradient Checkpointing**:
```yaml
training:
  gradient_checkpointing: true
```

3. **Enable Compiled Model** (PyTorch 2.0+):
```yaml
optimization:
  compile_model: true
```

## Next Steps

After setup:

1. **Generate Training Data**: Create at least 5,000 synthetic PDFs
2. **Train Initial Model**: Start with a small dataset to verify pipeline
3. **Evaluate Performance**: Test PHI detection accuracy
4. **Fine-tune**: Adjust hyperparameters based on results
5. **Deploy**: Set up inference pipeline for production use

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/yourusername/Justitia-PHI-OCR/issues)
- **Documentation**: See `/docs` directory
- **Community**: Join our Discord/Slack (if applicable)

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Citation

If you use this project in research, please cite:
```bibtex
@software{justitia2025,
  title={Justitia: Selective Vision Token Masking for PHI-Compliant OCR},
  year={2025},
  url={https://github.com/yourusername/Justitia-PHI-OCR}
}
```