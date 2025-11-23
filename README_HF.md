---
license: mit
tags:
- privacy
- phi-detection
- medical-documents
- vision-language-models
- negative-result
- deepseek-ocr
- hipaa
pipeline_tag: image-to-text
---

# Vision Token Masking for PHI Protection: A Negative Result

**Research Code & Evaluation Framework**

🚨 **Key Finding**: Vision-level token masking achieves only **42.9% PHI reduction** - insufficient for HIPAA compliance

## Overview

This repository contains the systematic evaluation code from our paper **"Vision Token Masking Alone Cannot Prevent PHI Leakage in Medical Document OCR"**.

**Author**: Richard J. Young
**Affiliation**: DeepNeuro.AI | University of Nevada, Las Vegas
**Status**: Paper Under Review

## The Negative Result

We evaluated **seven masking strategies** (V3-V9) across different architectural layers of DeepSeek-OCR using 100 synthetic medical billing statements from a corpus of 38,517 annotated documents.

### What We Found

| PHI Type | Reduction Rate |
|----------|----------------|
| **Patient Names** | ✅ 100% |
| **Dates of Birth** | ✅ 100% |
| **Physical Addresses** | ✅ 100% |
| **SSN** | ❌ 0% |
| **Medical Record Numbers** | ❌ 0% |
| **Email Addresses** | ❌ 0% |
| **Account Numbers** | ❌ 0% |
| **Overall** | ⚠️ 42.9% |

### Why It Matters

- **All strategies converged** to 42.9% regardless of architectural layer (V3-V9)
- **Spatial expansion didn't help** - mask radius r=1,2,3 showed no improvement
- **Root cause identified** - language model contextual inference reconstructs masked short identifiers from document context
- **Hybrid approach needed** - simulation shows 88.6% reduction when combining vision masking + NLP post-processing

## What's Included

✅ **Synthetic Data Pipeline**: Generates 38,517+ annotated medical PDFs using Synthea
✅ **PHI Annotation Tools**: Ground-truth labeling for all 18 HIPAA categories
✅ **Seven Masking Strategies**: V3-V9 implementations targeting different DeepSeek-OCR layers
✅ **Evaluation Framework**: Code for measuring PHI reduction by category
✅ **Configuration Files**: DeepSeek-OCR integration settings

## Quick Start

### Installation

```bash
git clone https://github.com/ricyoung/Justitia-Selective_Vision_Token_Masking_for_PHI-Compliant_OCR.git
cd Justitia-Selective_Vision_Token_Masking_for_PHI-Compliant_OCR

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Generate Synthetic Data

```bash
# Setup Synthea
bash scripts/setup_synthea.sh

# Generate patient data
bash scripts/generate_synthea_data.sh

# Create annotated PDFs
python scripts/generate_clinical_notes.py --output-dir data/pdfs --num-documents 1000
```

### Explore the Code

```bash
# View masking strategies
cat src/training/lora_phi_detector.py

# Check PHI annotation pipeline
cat src/preprocessing/phi_annotator.py
```

## Research Contributions

1. **First systematic evaluation** of vision-level token masking for PHI protection in VLMs
2. **Establishes boundaries** - identifies which PHI types work with vision masking vs requiring language-level redaction
3. **Negative result** - proves vision-only approaches are insufficient for HIPAA compliance
4. **Redirects future work** - toward hybrid architectures and decoder-level fine-tuning

## Architecture

```
Input PDF → Vision Encoder → PHI Detection → Vision Token Masking → DeepSeek Decoder → Text Output
            (SAM + CLIP)    (Ground Truth)   (V3-V9 Strategies)      (3B-MoE)
                                                    ↓
                                              42.9% Reduction
                                              (Insufficient!)
```

### Seven Masking Strategies

- **V3-V5**: SAM encoder blocks at different depths
- **V6**: Compression layer (4096→1024 tokens)
- **V7**: Dual vision encoders (SAM + CLIP)
- **V8**: Post-compression stage
- **V9**: Projector fusion layer

**Result**: All strategies converged to identical 42.9% reduction

## Implications

⚠️ **Vision-only masking is insufficient for HIPAA compliance** (requires 99%+ PHI reduction)

✅ **Hybrid architectures are necessary** - combine vision masking with NLP post-processing

🔮 **Future directions** - decoder-level fine-tuning, defense-in-depth approaches

## Use Cases

This code is useful for:

- Researchers exploring privacy-preserving VLMs
- Healthcare AI teams evaluating PHI protection strategies
- Benchmarking alternative redaction approaches
- Understanding VLM architectural limitations for sensitive data

## Citation

```bibtex
@article{young2025visionmasking,
  title={Vision Token Masking Alone Cannot Prevent PHI Leakage in Medical Document OCR: A Systematic Evaluation},
  author={Young, Richard J.},
  institution={DeepNeuro.AI; University of Nevada, Las Vegas},
  journal={Under Review},
  year={2025},
  url={https://huggingface.co/richardyoung/vision-token-masking-phi}
}
```

## License

MIT License - See [LICENSE](LICENSE) for details

## Contact

**Richard J. Young**
🌐 [deepneuro.ai/richard](https://deepneuro.ai/richard)
🤗 [@richardyoung](https://huggingface.co/richardyoung)
💻 [GitHub](https://github.com/ricyoung/Justitia-Selective_Vision_Token_Masking_for_PHI-Compliant_OCR)

## Disclaimer

⚠️ Research project only - **NOT for production use with real PHI**. Always consult legal and compliance teams before deploying PHI-related systems.

---

**Note**: This negative result establishes important boundaries for vision-level privacy interventions in VLMs and redirects the field toward more effective hybrid approaches.
