"""
PHI Annotation System for PDF documents.
This module provides tools to detect, annotate, and track PHI in medical PDFs.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
from PIL import Image, ImageDraw
import pdf2image
import cv2


@dataclass
class PHIAnnotation:
    """Represents a single PHI annotation in a document."""
    category: str  # PHI category (name, date, ssn, etc.)
    value: str  # The actual PHI value
    page: int  # Page number (1-indexed)
    bbox: Optional[Tuple[int, int, int, int]] = None  # Bounding box (x1, y1, x2, y2)
    confidence: float = 1.0  # Confidence score
    masked_value: Optional[str] = None  # Value after masking


@dataclass
class DocumentAnnotations:
    """Contains all PHI annotations for a document."""
    document_path: str
    annotations: List[PHIAnnotation]
    total_pages: int
    timestamp: str
    metadata: Dict[str, Any]


class PHIAnnotator:
    """Annotate PHI in medical documents."""

    # HIPAA PHI Categories
    PHI_CATEGORIES = {
        'name': 'Names (patients, physicians, family)',
        'date': 'Dates (except year alone)',
        'address': 'Geographic subdivisions smaller than state',
        'phone': 'Phone and fax numbers',
        'email': 'Email addresses',
        'ssn': 'Social Security Numbers',
        'mrn': 'Medical Record Numbers',
        'insurance_id': 'Health plan beneficiary numbers',
        'account': 'Account numbers',
        'license': 'Certificate/license numbers',
        'vehicle': 'Vehicle identifiers and license plates',
        'device_id': 'Device identifiers and serial numbers',
        'url': 'Web URLs',
        'ip': 'IP addresses',
        'biometric': 'Biometric identifiers',
        'unique_id': 'Any unique identifying number',
        'geo_small': 'Geographic subdivisions < state',
        'institution': 'Healthcare facility names',
    }

    # Regular expressions for PHI detection
    PHI_PATTERNS = {
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'mrn': r'\b(?:MRN|Medical Record Number)[:\s]?[\w\d-]+\b',
        'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
        'url': r'https?://[^\s]+',
        'ip': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
        'insurance_id': r'\b(?:INS|Policy|Member ID)[:\s]?[\w\d-]+\b',
        'license': r'\b(?:License|DEA|NPI)[:\s]?[\w\d-]+\b',
    }

    def __init__(self, confidence_threshold: float = 0.85):
        """
        Initialize PHI Annotator.

        Args:
            confidence_threshold: Minimum confidence for PHI detection
        """
        self.confidence_threshold = confidence_threshold

    def annotate_pdf(self, pdf_path: Path, dpi: int = 150) -> DocumentAnnotations:
        """
        Annotate PHI in a PDF document.

        Args:
            pdf_path: Path to PDF file
            dpi: DPI for PDF to image conversion

        Returns:
            DocumentAnnotations object
        """
        # Convert PDF to images
        images = pdf2image.convert_from_path(pdf_path, dpi=dpi)

        annotations = []
        for page_num, image in enumerate(images, 1):
            # Convert PIL Image to numpy array
            img_array = np.array(image)

            # Detect text regions using OCR
            text_regions = self._detect_text_regions(img_array)

            # Analyze each region for PHI
            for region in text_regions:
                phi_results = self._analyze_region_for_phi(region, page_num)
                annotations.extend(phi_results)

        # Create DocumentAnnotations object
        doc_annotations = DocumentAnnotations(
            document_path=str(pdf_path),
            annotations=annotations,
            total_pages=len(images),
            timestamp=datetime.now().isoformat(),
            metadata={
                'dpi': dpi,
                'confidence_threshold': self.confidence_threshold,
            }
        )

        return doc_annotations

    def _detect_text_regions(self, image: np.ndarray) -> List[Dict]:
        """
        Detect text regions in an image using computer vision.

        Args:
            image: Image array

        Returns:
            List of text regions with bounding boxes
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # Filter out very small regions
            if w > 20 and h > 10:
                regions.append({
                    'bbox': (x, y, x + w, y + h),
                    'area': w * h,
                })

        return regions

    def _analyze_region_for_phi(self, region: Dict, page_num: int) -> List[PHIAnnotation]:
        """
        Analyze a text region for PHI.

        Args:
            region: Text region dictionary
            page_num: Page number

        Returns:
            List of PHI annotations found
        """
        annotations = []

        # This is a placeholder - in reality, you would run OCR on the region
        # and then analyze the text for PHI patterns

        # For now, we'll simulate PHI detection
        # In production, this would use actual OCR results
        simulated_phi = self._simulate_phi_detection(region['bbox'])

        for phi_item in simulated_phi:
            annotation = PHIAnnotation(
                category=phi_item['category'],
                value=phi_item['value'],
                page=page_num,
                bbox=region['bbox'],
                confidence=phi_item['confidence'],
            )
            annotations.append(annotation)

        return annotations

    def _simulate_phi_detection(self, bbox: Tuple) -> List[Dict]:
        """
        Simulate PHI detection for testing.
        In production, this would be replaced with actual OCR and pattern matching.
        """
        import random

        # Randomly simulate finding PHI
        if random.random() < 0.3:  # 30% chance of finding PHI
            category = random.choice(list(self.PHI_CATEGORIES.keys()))
            return [{
                'category': category,
                'value': f"SIMULATED_{category.upper()}_VALUE",
                'confidence': random.uniform(0.85, 1.0),
            }]
        return []

    def apply_pattern_matching(self, text: str) -> List[Dict]:
        """
        Apply regex patterns to detect PHI in text.

        Args:
            text: Text to analyze

        Returns:
            List of detected PHI items
        """
        detections = []

        for category, pattern in self.PHI_PATTERNS.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detections.append({
                    'category': category,
                    'value': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.9,  # Pattern matching confidence
                })

        return detections

    def create_masked_image(
        self,
        image: Image.Image,
        annotations: List[PHIAnnotation],
        mask_type: str = 'black_box'
    ) -> Image.Image:
        """
        Create a masked version of the image with PHI redacted.

        Args:
            image: Original image
            annotations: PHI annotations
            mask_type: Type of masking ('black_box', 'blur', 'pixelate')

        Returns:
            Masked image
        """
        # Create a copy of the image
        masked_image = image.copy()
        draw = ImageDraw.Draw(masked_image)

        for annotation in annotations:
            if annotation.bbox:
                x1, y1, x2, y2 = annotation.bbox

                if mask_type == 'black_box':
                    # Draw black rectangle
                    draw.rectangle([x1, y1, x2, y2], fill='black')
                elif mask_type == 'blur':
                    # Apply blur to region
                    region = image.crop((x1, y1, x2, y2))
                    blurred = region.filter(ImageFilter.GaussianBlur(radius=10))
                    masked_image.paste(blurred, (x1, y1))
                elif mask_type == 'pixelate':
                    # Pixelate region
                    region = image.crop((x1, y1, x2, y2))
                    small = region.resize((10, 10), Image.NEAREST)
                    pixelated = small.resize(region.size, Image.NEAREST)
                    masked_image.paste(pixelated, (x1, y1))

        return masked_image

    def save_annotations(self, annotations: DocumentAnnotations, output_path: Path):
        """
        Save annotations to JSON file.

        Args:
            annotations: Document annotations
            output_path: Path to save JSON file
        """
        # Convert dataclass to dictionary
        data = {
            'document_path': annotations.document_path,
            'total_pages': annotations.total_pages,
            'timestamp': annotations.timestamp,
            'metadata': annotations.metadata,
            'annotations': [asdict(ann) for ann in annotations.annotations],
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    def load_annotations(self, json_path: Path) -> DocumentAnnotations:
        """
        Load annotations from JSON file.

        Args:
            json_path: Path to JSON file

        Returns:
            DocumentAnnotations object
        """
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Convert dictionaries back to PHIAnnotation objects
        annotations = [
            PHIAnnotation(**ann_dict)
            for ann_dict in data['annotations']
        ]

        return DocumentAnnotations(
            document_path=data['document_path'],
            annotations=annotations,
            total_pages=data['total_pages'],
            timestamp=data['timestamp'],
            metadata=data['metadata'],
        )

    def calculate_statistics(self, annotations: DocumentAnnotations) -> Dict:
        """
        Calculate statistics about PHI in the document.

        Args:
            annotations: Document annotations

        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_phi_items': len(annotations.annotations),
            'pages_with_phi': len(set(ann.page for ann in annotations.annotations)),
            'phi_by_category': {},
            'average_confidence': 0.0,
        }

        # Count by category
        for ann in annotations.annotations:
            if ann.category not in stats['phi_by_category']:
                stats['phi_by_category'][ann.category] = 0
            stats['phi_by_category'][ann.category] += 1

        # Calculate average confidence
        if annotations.annotations:
            confidences = [ann.confidence for ann in annotations.annotations]
            stats['average_confidence'] = sum(confidences) / len(confidences)

        return stats

    def create_annotation_report(
        self,
        annotations: DocumentAnnotations,
        output_path: Path
    ):
        """
        Create a human-readable report of PHI annotations.

        Args:
            annotations: Document annotations
            output_path: Path to save report
        """
        stats = self.calculate_statistics(annotations)

        report = []
        report.append("=" * 60)
        report.append("PHI ANNOTATION REPORT")
        report.append("=" * 60)
        report.append(f"Document: {annotations.document_path}")
        report.append(f"Timestamp: {annotations.timestamp}")
        report.append(f"Total Pages: {annotations.total_pages}")
        report.append("")
        report.append("STATISTICS")
        report.append("-" * 40)
        report.append(f"Total PHI Items: {stats['total_phi_items']}")
        report.append(f"Pages with PHI: {stats['pages_with_phi']}/{annotations.total_pages}")
        report.append(f"Average Confidence: {stats['average_confidence']:.2%}")
        report.append("")
        report.append("PHI BY CATEGORY")
        report.append("-" * 40)

        for category, count in sorted(stats['phi_by_category'].items()):
            description = self.PHI_CATEGORIES.get(category, 'Unknown')
            report.append(f"{category:15} {count:3} items - {description}")

        report.append("")
        report.append("DETAILED ANNOTATIONS")
        report.append("-" * 40)

        for i, ann in enumerate(annotations.annotations, 1):
            report.append(f"\n{i}. Category: {ann.category}")
            report.append(f"   Value: {ann.value[:30]}..." if len(ann.value) > 30 else f"   Value: {ann.value}")
            report.append(f"   Page: {ann.page}")
            report.append(f"   Confidence: {ann.confidence:.2%}")
            if ann.bbox:
                report.append(f"   Location: {ann.bbox}")

        report.append("")
        report.append("=" * 60)
        report.append("END OF REPORT")
        report.append("=" * 60)

        # Save report
        with open(output_path, 'w') as f:
            f.write('\n'.join(report))


def main():
    """Example usage of PHI Annotator."""
    import argparse

    parser = argparse.ArgumentParser(description='Annotate PHI in PDF documents')
    parser.add_argument('--pdf', type=str, required=True, help='Path to PDF file')
    parser.add_argument('--output', type=str, help='Output directory for annotations')
    parser.add_argument('--report', action='store_true', help='Generate annotation report')
    parser.add_argument('--mask', action='store_true', help='Create masked version of PDF')

    args = parser.parse_args()

    # Create annotator
    annotator = PHIAnnotator()

    # Annotate PDF
    pdf_path = Path(args.pdf)
    print(f"Annotating PHI in {pdf_path}...")
    annotations = annotator.annotate_pdf(pdf_path)

    # Save annotations
    output_dir = Path(args.output) if args.output else pdf_path.parent
    output_dir.mkdir(exist_ok=True)

    json_path = output_dir / f"{pdf_path.stem}_annotations.json"
    annotator.save_annotations(annotations, json_path)
    print(f"Annotations saved to {json_path}")

    # Generate report if requested
    if args.report:
        report_path = output_dir / f"{pdf_path.stem}_report.txt"
        annotator.create_annotation_report(annotations, report_path)
        print(f"Report saved to {report_path}")

    # Print statistics
    stats = annotator.calculate_statistics(annotations)
    print(f"\nPHI Statistics:")
    print(f"  Total PHI items: {stats['total_phi_items']}")
    print(f"  Pages with PHI: {stats['pages_with_phi']}")
    print(f"  Categories found: {', '.join(stats['phi_by_category'].keys())}")


if __name__ == "__main__":
    main()