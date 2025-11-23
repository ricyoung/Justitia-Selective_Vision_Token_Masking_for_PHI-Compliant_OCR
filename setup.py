"""
Setup script for Justitia: Selective Vision Token Masking for PHI-Compliant OCR
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f
                if line.strip() and not line.startswith('#') and not line.startswith('flash-attn')]

# Base requirements
install_requires = read_requirements('requirements.txt')

# Development requirements
dev_requires = [
    'jupyter>=1.0.0',
    'black>=23.0.0',
    'flake8>=6.0.0',
    'pytest>=7.4.0',
    'pytest-cov>=4.1.0',
    'ipywidgets>=8.0.0',
]

setup(
    name="justitia-phi-ocr",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Selective Vision Token Masking for PHI-Compliant OCR using DeepSeek-OCR and LoRA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Justitia-PHI-OCR",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        "flash-attn": ["flash-attn>=2.7.3"],
    },
    entry_points={
        "console_scripts": [
            "justitia-train=training.train_lora:main",
            "justitia-infer=inference.process_documents:main",
            "justitia-generate=data_generation.synthea_to_pdf:main",
            "justitia-download=scripts.download_model:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json", "*.txt", "*.md"],
    },
)

print("\n" + "="*60)
print("Justitia PHI-OCR Setup Complete!")
print("="*60)
print("\nIMPORTANT: Flash Attention must be installed separately:")
print("  pip install flash-attn==2.7.3 --no-build-isolation")
print("\nFor development installation:")
print("  pip install -e .[dev]")
print("\nTo download DeepSeek-OCR model:")
print("  python scripts/download_model.py")
print("="*60)