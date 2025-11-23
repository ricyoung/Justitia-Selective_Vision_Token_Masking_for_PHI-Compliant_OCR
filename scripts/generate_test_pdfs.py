#!/usr/bin/env python3
"""
Generate test medical PDFs without Synthea dependency.
This creates synthetic medical documents for initial testing.
"""

import sys
import os
from pathlib import Path
from faker import Faker
import random
import json

def generate_fake_patient_data(faker, num_patients=100):
    """Generate fake patient data without Synthea."""
    patients = []

    for i in range(num_patients):
        patient = {
            'name': faker.name(),
            'birth_date': faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
            'ssn': faker.ssn(),
            'phone': faker.phone_number(),
            'email': faker.email(),
            'address': faker.address().replace('\n', ', '),
            'mrn': f"MRN-{faker.random_number(digits=8, fix_len=True)}",
            'insurance_id': f"INS-{faker.random_number(digits=10, fix_len=True)}",

            # Medical data
            'conditions': [
                {'code': faker.random_element(['Hypertension', 'Diabetes Type 2', 'Asthma', 'COPD', 'CAD']),
                 'onset': faker.date_between(start_date='-10y', end_date='today').strftime('%Y-%m-%d'),
                 'status': 'active'}
                for _ in range(random.randint(1, 3))
            ],

            'medications': [
                {'name': faker.random_element(['Lisinopril 10mg', 'Metformin 500mg', 'Atorvastatin 20mg', 'Omeprazole 20mg']),
                 'dosage': f'Take {random.randint(1, 3)} tablet(s) {random.choice(["daily", "twice daily", "three times daily"])}',
                 'prescriber': f'Dr. {faker.last_name()}'}
                for _ in range(random.randint(1, 4))
            ],

            'allergies': [
                {'substance': faker.random_element(['Penicillin', 'Sulfa drugs', 'Aspirin', 'Latex']),
                 'severity': faker.random_element(['mild', 'moderate', 'severe'])}
                for _ in range(random.randint(0, 2))
            ],

            'procedures': [],
            'encounters': [],
            'immunizations': [],
            'observations': []
        }

        patients.append(patient)

    return patients


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate test medical PDFs')
    parser.add_argument('--num-patients', type=int, default=100, help='Number of patients')
    parser.add_argument('--num-documents', type=int, default=500, help='Number of PDFs to generate')
    parser.add_argument('--output-dir', type=str, default='./data/pdfs', help='Output directory')
    parser.add_argument('--annotations-dir', type=str, default='./data/annotations', help='Annotations directory')

    args = parser.parse_args()

    print("="*60)
    print("Generating Test Medical PDFs (without Synthea)")
    print("="*60)
    print(f"Patients: {args.num_patients}")
    print(f"Documents: {args.num_documents}")
    print(f"Output: {args.output_dir}")
    print()

    # Initialize Faker
    faker = Faker()
    Faker.seed(42)

    # Generate fake patient data
    print("Generating synthetic patient data...")
    patients = generate_fake_patient_data(faker, args.num_patients)
    print(f"✓ Generated {len(patients)} patients")

    # Create PDF generator
    # Note: We need to adapt since it expects Synthea output
    # Let's create PDFs directly

    from datetime import datetime
    import random as rand
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch

    output_dir = Path(args.output_dir)
    annotations_dir = Path(args.annotations_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    annotations_dir.mkdir(parents=True, exist_ok=True)

    document_types = ['prescription', 'lab_report', 'insurance_claim']

    print(f"\nGenerating {args.num_documents} PDFs...")

    for i in range(args.num_documents):
        patient = rand.choice(patients)
        doc_type = rand.choice(document_types)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_name = f"{doc_type}_{i:04d}_{timestamp}.pdf"
        pdf_path = output_dir / pdf_name

        # Create simple PDF
        doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Header
        story.append(Paragraph(f"<b>{doc_type.upper().replace('_', ' ')}</b>", styles['Heading1']))
        story.append(Spacer(1, 0.2 * inch))

        # Patient info
        patient_data = [
            ['Patient Name:', patient['name']],
            ['Date of Birth:', patient['birth_date']],
            ['MRN:', patient['mrn']],
            ['Phone:', patient['phone']],
            ['Date:', datetime.now().strftime('%Y-%m-%d')],
        ]

        patient_table = Table(patient_data, colWidths=[2 * inch, 4 * inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(patient_table)

        doc.build(story)

        # Create annotation
        annotations = [
            {'type': 'name', 'value': patient['name'], 'page': 1},
            {'type': 'date', 'value': patient['birth_date'], 'page': 1},
            {'type': 'mrn', 'value': patient['mrn'], 'page': 1},
            {'type': 'phone', 'value': patient['phone'], 'page': 1},
        ]

        annotation_file = annotations_dir / f"{pdf_name}.json"
        with open(annotation_file, 'w') as f:
            json.dump({
                'document': pdf_name,
                'annotations': annotations,
                'timestamp': datetime.now().isoformat(),
            }, f, indent=2)

        if (i + 1) % 100 == 0:
            print(f"  Generated {i + 1}/{args.num_documents} PDFs...")

    print(f"\n✓ Generation complete!")
    print(f"  PDFs: {output_dir}")
    print(f"  Annotations: {annotations_dir}")
    print(f"\nGenerated files:")
    print(f"  {len(list(output_dir.glob('*.pdf')))} PDFs")
    print(f"  {len(list(annotations_dir.glob('*.json')))} annotations")

    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("1. Review PDFs: ls data/pdfs")
    print("2. Download model: python scripts/download_model.py")
    print("3. Train LoRA: python src/training/train_lora.py")
    print("="*60)


if __name__ == "__main__":
    main()
