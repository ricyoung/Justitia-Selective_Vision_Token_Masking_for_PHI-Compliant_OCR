"""
LoRA Adapter Implementation for PHI Detection in Vision Tokens.
This module implements a LoRA adapter for DeepSeek-OCR to detect PHI at the vision token level.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from transformers import AutoModel, AutoTokenizer
import yaml
from pathlib import Path


@dataclass
class PHIDetectorConfig:
    """Configuration for PHI Detector LoRA."""
    # LoRA parameters
    lora_rank: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1
    target_modules: List[str] = None

    # PHI detection parameters
    num_phi_categories: int = 18  # Number of HIPAA PHI categories
    confidence_threshold: float = 0.85

    # Vision token parameters
    vision_hidden_size: int = 1024
    num_vision_tokens: int = 256  # After compression

    # Training parameters
    learning_rate: float = 2e-4
    warmup_steps: int = 500
    gradient_checkpointing: bool = True

    def __post_init__(self):
        if self.target_modules is None:
            self.target_modules = ["q_proj", "v_proj", "k_proj", "o_proj"]


class PHITokenClassifier(nn.Module):
    """Classification head for PHI detection on vision tokens."""

    def __init__(self, config: PHIDetectorConfig):
        super().__init__()
        self.config = config

        # Multi-layer classifier for PHI detection
        self.classifier = nn.Sequential(
            nn.Linear(config.vision_hidden_size, config.vision_hidden_size // 2),
            nn.LayerNorm(config.vision_hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(config.lora_dropout),
            nn.Linear(config.vision_hidden_size // 2, config.vision_hidden_size // 4),
            nn.LayerNorm(config.vision_hidden_size // 4),
            nn.ReLU(),
            nn.Dropout(config.lora_dropout),
            nn.Linear(config.vision_hidden_size // 4, config.num_phi_categories + 1)  # +1 for non-PHI
        )

        # Confidence predictor
        self.confidence_head = nn.Sequential(
            nn.Linear(config.vision_hidden_size, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

        # Token importance scorer for attention masking
        self.importance_scorer = nn.Sequential(
            nn.Linear(config.vision_hidden_size, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )

    def forward(
        self,
        vision_features: torch.Tensor,
        return_importance: bool = False
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass for PHI detection.

        Args:
            vision_features: Vision token features [batch_size, num_tokens, hidden_size]
            return_importance: Whether to return token importance scores

        Returns:
            Dictionary containing:
                - logits: PHI category logits [batch_size, num_tokens, num_categories + 1]
                - confidence: Confidence scores [batch_size, num_tokens, 1]
                - importance: Token importance scores (if requested)
        """
        # PHI classification
        logits = self.classifier(vision_features)

        # Confidence prediction
        confidence = self.confidence_head(vision_features)

        outputs = {
            'logits': logits,
            'confidence': confidence,
        }

        # Token importance (for selective attention)
        if return_importance:
            importance = self.importance_scorer(vision_features)
            outputs['importance'] = importance

        return outputs


class PHIDetectorLoRA(nn.Module):
    """LoRA adapter for PHI detection in DeepSeek-OCR."""

    def __init__(
        self,
        base_model: nn.Module,
        config: PHIDetectorConfig,
        device: str = 'cuda'
    ):
        super().__init__()
        self.config = config
        self.device = device

        # Configure LoRA
        lora_config = LoraConfig(
            r=config.lora_rank,
            lora_alpha=config.lora_alpha,
            lora_dropout=config.lora_dropout,
            target_modules=config.target_modules,
            task_type=TaskType.FEATURE_EXTRACTION,
        )

        # Apply LoRA to base model
        self.base_model = get_peft_model(base_model, lora_config)

        # PHI detection head
        self.phi_detector = PHITokenClassifier(config)

        # Vision token processor
        self.token_processor = VisionTokenProcessor(config)

        # Move to device
        self.to(device)

    def forward(
        self,
        images: torch.Tensor,
        return_masked: bool = True,
        masking_strategy: str = 'selective_attention'
    ) -> Dict[str, Any]:
        """
        Forward pass with PHI detection and optional masking.

        Args:
            images: Input images [batch_size, channels, height, width]
            return_masked: Whether to return masked vision tokens
            masking_strategy: Strategy for masking ('selective_attention' or 'token_replacement')

        Returns:
            Dictionary containing:
                - vision_features: Original vision features
                - phi_predictions: PHI detection results
                - masked_features: Masked vision features (if requested)
                - attention_mask: Attention mask for PHI tokens
        """
        # Extract vision features using base model
        with torch.no_grad() if not self.training else torch.enable_grad():
            vision_outputs = self.base_model.get_vision_features(images)

        vision_features = vision_outputs['last_hidden_state']

        # Detect PHI in vision tokens
        phi_predictions = self.phi_detector(vision_features, return_importance=True)

        outputs = {
            'vision_features': vision_features,
            'phi_predictions': phi_predictions,
        }

        # Apply masking if requested
        if return_masked:
            masked_features, attention_mask = self.token_processor.apply_masking(
                vision_features,
                phi_predictions,
                strategy=masking_strategy
            )
            outputs['masked_features'] = masked_features
            outputs['attention_mask'] = attention_mask

        return outputs

    def detect_phi(
        self,
        vision_features: torch.Tensor,
        threshold: Optional[float] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Detect PHI in vision features.

        Args:
            vision_features: Vision token features
            threshold: Confidence threshold (uses config default if None)

        Returns:
            Tuple of (phi_mask, phi_categories)
        """
        if threshold is None:
            threshold = self.config.confidence_threshold

        # Get PHI predictions
        predictions = self.phi_detector(vision_features)

        # Get predicted categories (excluding non-PHI class at index 0)
        phi_probs = F.softmax(predictions['logits'], dim=-1)
        phi_categories = torch.argmax(phi_probs, dim=-1)

        # Create mask based on confidence and category
        is_phi = phi_categories > 0  # Category 0 is non-PHI
        confident = predictions['confidence'].squeeze(-1) > threshold

        phi_mask = is_phi & confident

        return phi_mask, phi_categories

    def save_adapter(self, save_path: str):
        """Save LoRA adapter weights."""
        save_dir = Path(save_path)
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save LoRA weights
        self.base_model.save_pretrained(save_dir)

        # Save PHI detector weights
        torch.save(self.phi_detector.state_dict(), save_dir / 'phi_detector.pt')

        # Save config
        config_dict = {
            'lora_rank': self.config.lora_rank,
            'lora_alpha': self.config.lora_alpha,
            'lora_dropout': self.config.lora_dropout,
            'target_modules': self.config.target_modules,
            'num_phi_categories': self.config.num_phi_categories,
            'confidence_threshold': self.config.confidence_threshold,
            'vision_hidden_size': self.config.vision_hidden_size,
            'num_vision_tokens': self.config.num_vision_tokens,
        }

        with open(save_dir / 'config.yaml', 'w') as f:
            yaml.dump(config_dict, f)

        print(f"✓ Adapter saved to {save_dir}")

    @classmethod
    def load_adapter(cls, base_model: nn.Module, load_path: str, device: str = 'cuda'):
        """Load LoRA adapter from saved weights."""
        load_dir = Path(load_path)

        # Load config
        with open(load_dir / 'config.yaml', 'r') as f:
            config_dict = yaml.safe_load(f)

        config = PHIDetectorConfig(**config_dict)

        # Load LoRA model
        model = PeftModel.from_pretrained(base_model, load_dir)

        # Create PHI detector instance
        detector = cls(model, config, device)

        # Load PHI detector weights
        detector.phi_detector.load_state_dict(
            torch.load(load_dir / 'phi_detector.pt', map_location=device)
        )

        print(f"✓ Adapter loaded from {load_dir}")
        return detector


class VisionTokenProcessor:
    """Process and mask vision tokens based on PHI detection."""

    def __init__(self, config: PHIDetectorConfig):
        self.config = config

        # Learned privacy-preserving embeddings for each PHI category
        self.privacy_embeddings = nn.Parameter(
            torch.randn(config.num_phi_categories + 1, config.vision_hidden_size)
        )

    def apply_masking(
        self,
        vision_features: torch.Tensor,
        phi_predictions: Dict[str, torch.Tensor],
        strategy: str = 'selective_attention'
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Apply masking to vision features based on PHI predictions.

        Args:
            vision_features: Original vision features
            phi_predictions: PHI detection results
            strategy: Masking strategy

        Returns:
            Tuple of (masked_features, attention_mask)
        """
        batch_size, num_tokens, hidden_size = vision_features.shape

        # Get PHI mask
        phi_categories = torch.argmax(phi_predictions['logits'], dim=-1)
        is_phi = phi_categories > 0

        if strategy == 'token_replacement':
            # Replace PHI tokens with privacy-preserving embeddings
            masked_features = vision_features.clone()

            for b in range(batch_size):
                for t in range(num_tokens):
                    if is_phi[b, t]:
                        category = phi_categories[b, t]
                        masked_features[b, t] = self.privacy_embeddings[category]

            attention_mask = torch.ones_like(is_phi, dtype=torch.float32)

        elif strategy == 'selective_attention':
            # Create attention mask to ignore PHI tokens
            attention_mask = (~is_phi).float()

            # Keep original features but rely on attention masking
            masked_features = vision_features

            # Optionally reduce importance of PHI tokens
            if 'importance' in phi_predictions:
                importance = phi_predictions['importance'].squeeze(-1)
                attention_mask = attention_mask * importance

        elif strategy == 'hybrid':
            # Combination of both strategies
            masked_features = vision_features.clone()
            attention_mask = torch.ones_like(is_phi, dtype=torch.float32)

            # High-confidence PHI gets replaced
            high_confidence = phi_predictions['confidence'].squeeze(-1) > 0.95
            replace_mask = is_phi & high_confidence

            # Lower confidence PHI gets attention masking
            attention_mask_phi = is_phi & ~high_confidence
            attention_mask[attention_mask_phi] = 0.1  # Reduced attention weight

            # Replace high-confidence PHI tokens
            for b in range(batch_size):
                for t in range(num_tokens):
                    if replace_mask[b, t]:
                        category = phi_categories[b, t]
                        masked_features[b, t] = self.privacy_embeddings[category]

        else:
            raise ValueError(f"Unknown masking strategy: {strategy}")

        return masked_features, attention_mask


class PHILoss(nn.Module):
    """Custom loss function for PHI detection training."""

    def __init__(self, config: PHIDetectorConfig, class_weights: Optional[torch.Tensor] = None):
        super().__init__()
        self.config = config

        # Focal loss for handling class imbalance
        self.focal_alpha = 0.25
        self.focal_gamma = 2.0

        # Class weights for imbalanced PHI categories
        self.class_weights = class_weights

    def forward(
        self,
        predictions: Dict[str, torch.Tensor],
        targets: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """
        Calculate PHI detection losses.

        Args:
            predictions: Model predictions
            targets: Ground truth labels

        Returns:
            Dictionary of losses
        """
        losses = {}

        # Classification loss (focal loss)
        logits = predictions['logits']
        labels = targets['labels']

        ce_loss = F.cross_entropy(
            logits.view(-1, logits.size(-1)),
            labels.view(-1),
            weight=self.class_weights,
            reduction='none'
        )

        # Apply focal loss modification
        pt = torch.exp(-ce_loss)
        focal_loss = self.focal_alpha * (1 - pt) ** self.focal_gamma * ce_loss
        losses['classification'] = focal_loss.mean()

        # Confidence loss (MSE between predicted and true confidence)
        if 'confidence' in predictions and 'confidence_targets' in targets:
            confidence_loss = F.mse_loss(
                predictions['confidence'].squeeze(-1),
                targets['confidence_targets']
            )
            losses['confidence'] = confidence_loss

        # Consistency loss (encourage similar predictions for nearby tokens)
        if 'importance' in predictions:
            importance = predictions['importance'].squeeze(-1)

            # Calculate importance consistency
            importance_diff = torch.diff(importance, dim=1)
            consistency_loss = torch.mean(importance_diff ** 2)
            losses['consistency'] = consistency_loss * 0.1  # Weight the loss

        # Total loss
        losses['total'] = sum(losses.values())

        return losses


def create_phi_detector(
    model_name: str = "deepseek-ai/DeepSeek-OCR",
    config_path: Optional[str] = None,
    device: str = 'cuda'
) -> PHIDetectorLoRA:
    """
    Create a PHI detector with LoRA adapter.

    Args:
        model_name: Base model name
        config_path: Path to config file
        device: Device to use

    Returns:
        PHIDetectorLoRA instance
    """
    # Load config
    if config_path:
        with open(config_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        config = PHIDetectorConfig(**config_dict)
    else:
        config = PHIDetectorConfig()

    # Load base model
    base_model = AutoModel.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.float16 if device == 'cuda' else torch.float32,
    )

    # Create PHI detector
    detector = PHIDetectorLoRA(base_model, config, device)

    return detector


if __name__ == "__main__":
    # Example usage
    print("Creating PHI Detector with LoRA...")

    # Create detector
    config = PHIDetectorConfig()
    print(f"Config: {config}")

    # Note: This would require the actual model to be downloaded
    # detector = create_phi_detector()
    # print("✓ PHI Detector created successfully!")

    print("\nPHI Categories:")
    categories = [
        "Non-PHI", "Name", "Date", "Address", "Phone", "Email",
        "SSN", "MRN", "Insurance ID", "Account", "License",
        "Vehicle", "Device ID", "URL", "IP", "Biometric",
        "Unique ID", "Geo Small", "Institution"
    ]
    for i, cat in enumerate(categories):
        print(f"  {i:2d}: {cat}")