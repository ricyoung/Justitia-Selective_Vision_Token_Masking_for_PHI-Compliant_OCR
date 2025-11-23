#!/usr/bin/env python3
"""
Generate REALISTIC medical PDFs that match real-world documents.
Includes proper formatting, layouts, medical terminology, and varied PHI.
"""

import sys
import os
from pathlib import Path
from faker import Faker
import random
import json
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, Image as RLImage, Frame, PageTemplate
)
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class RealisticMedicalPDFGenerator:
    """Generate highly realistic medical documents."""

    def __init__(self):
        self.faker = Faker()
        Faker.seed(42)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Create custom styles for medical documents."""
        # Header style
        self.header_style = ParagraphStyle(
            'MedicalHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            alignment=TA_CENTER,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )

        # Facility name
        self.facility_style = ParagraphStyle(
            'Facility',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#004080'),
            alignment=TA_CENTER,
            spaceAfter=3,
            fontName='Helvetica-Bold'
        )

        # Small text
        self.small_style = ParagraphStyle(
            'Small',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        )

        # Body text
        self.body_style = ParagraphStyle(
            'Body',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=14,
        )

        # Section header
        self.section_style = ParagraphStyle(
            'Section',
            parent=self.styles['Heading2'],
            fontSize=11,
            textColor=colors.HexColor('#004080'),
            spaceBefore=8,
            spaceAfter=4,
            fontName='Helvetica-Bold'
        )

    def create_prescription(self, patient_data, output_path):
        """Create a realistic prescription."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                                topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        annotations = []

        # Facility header
        clinic_name = f"{self.faker.company()} Medical Group"
        clinic_address = self.faker.address().replace('\n', ', ')
        clinic_phone = self.faker.phone_number()
        clinic_fax = clinic_phone  # Reuse for simplicity

        story.append(Paragraph(clinic_name, self.facility_style))
        story.append(Paragraph(clinic_address, self.small_style))
        story.append(Paragraph(f"Phone: {clinic_phone} | Fax: {clinic_fax}", self.small_style))
        story.append(Spacer(1, 0.2*inch))

        # Prescription header with RX symbol
        story.append(Paragraph("PRESCRIPTION", self.header_style))
        story.append(Spacer(1, 0.15*inch))

        # Patient information box
        rx_date = datetime.now()
        patient_info = [
            ['Patient Name:', patient_data['name']],
            ['Date of Birth:', patient_data['birth_date']],
            ['Address:', patient_data['address']],
            ['Phone:', patient_data['phone']],
            ['Date:', rx_date.strftime('%m/%d/%Y')],
        ]

        annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'address', 'value': patient_data['address'], 'page': 1},
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1},
            {'type': 'date', 'value': rx_date.strftime('%Y-%m-%d'), 'page': 1, 'context': 'rx_date'},
        ])

        patient_table = Table(patient_info, colWidths=[1.5*inch, 5*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))

        # RX symbol
        story.append(Paragraph("℞", ParagraphStyle('Rx', fontSize=24, textColor=colors.HexColor('#003366'))))
        story.append(Spacer(1, 0.1*inch))

        # Medications
        for i, med in enumerate(patient_data['medications'][:3], 1):
            med_text = f"""
            <b>{i}. {med['name']}</b><br/>
            <b>Sig:</b> {med['dosage']}<br/>
            <b>Disp:</b> #{random.randint(30, 90)} ({random.choice(['thirty', 'sixty', 'ninety'])})<br/>
            <b>Refills:</b> {random.randint(0, 5)}<br/>
            <b>Generic OK:</b> {random.choice(['Yes', 'No - Brand Medically Necessary'])}
            """
            story.append(Paragraph(med_text, self.body_style))
            story.append(Spacer(1, 0.15*inch))

        # Prescriber info
        prescriber = f"Dr. {self.faker.name()}"
        dea = f"DEA: {random.choice(['A', 'B', 'F'])}{self.faker.random_number(digits=7, fix_len=True)}"
        npi = f"NPI: {self.faker.random_number(digits=10, fix_len=True)}"
        license = f"License: {self.faker.random_number(digits=8, fix_len=True)}"

        annotations.append({'type': 'name', 'value': prescriber, 'page': 1, 'context': 'prescriber'})
        annotations.append({'type': 'license', 'value': dea, 'page': 1, 'context': 'dea'})
        annotations.append({'type': 'unique_id', 'value': npi, 'page': 1, 'context': 'npi'})
        annotations.append({'type': 'license', 'value': license, 'page': 1, 'context': 'state_license'})

        story.append(Spacer(1, 0.3*inch))
        prescriber_text = f"""
        <b>Prescriber:</b> {prescriber}, MD<br/>
        {dea} | {npi} | {license}<br/>
        <b>Signature:</b> _____________________________ <b>Date:</b> {rx_date.strftime('%m/%d/%Y')}
        """
        story.append(Paragraph(prescriber_text, self.body_style))

        # Footer
        story.append(Spacer(1, 0.2*inch))
        footer = "This prescription is valid for one year from the date written unless otherwise specified."
        story.append(Paragraph(footer, self.small_style))

        doc.build(story)
        return annotations

    def create_lab_report(self, patient_data, output_path):
        """Create a realistic laboratory report."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                                topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        annotations = []

        # Lab header
        lab_name = f"{self.faker.company()} Clinical Laboratory"
        lab_address = self.faker.address().replace('\n', ', ')
        clia = f"CLIA #: {self.faker.random_number(digits=10, fix_len=True)}"

        story.append(Paragraph(lab_name, self.facility_style))
        story.append(Paragraph(lab_address, self.small_style))
        story.append(Paragraph(f"{clia} | CAP Accredited", self.small_style))
        story.append(Spacer(1, 0.2*inch))

        story.append(Paragraph("LABORATORY REPORT", self.header_style))
        story.append(Spacer(1, 0.15*inch))

        # Patient and specimen info
        collection_date = datetime.now() - timedelta(days=random.randint(1, 7))
        report_date = datetime.now()
        specimen_id = f"SPEC-{self.faker.random_number(digits=10, fix_len=True)}"
        accession = f"ACC-{self.faker.random_number(digits=8, fix_len=True)}"

        patient_info = [
            ['Patient Name:', patient_data['name'], 'Ordering Physician:', f"Dr. {self.faker.last_name()}"],
            ['DOB:', patient_data['birth_date'], 'Collected:', collection_date.strftime('%m/%d/%Y %H:%M')],
            ['MRN:', patient_data['mrn'], 'Received:', collection_date.strftime('%m/%d/%Y %H:%M')],
            ['SSN:', patient_data['ssn'], 'Reported:', report_date.strftime('%m/%d/%Y %H:%M')],
            ['Phone:', patient_data['phone'], 'Specimen ID:', specimen_id],
            ['', '', 'Accession:', accession],
        ]

        annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'ssn', 'value': patient_data['ssn'], 'page': 1},
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1},
            {'type': 'date', 'value': collection_date.strftime('%Y-%m-%d'), 'page': 1},
            {'type': 'date', 'value': report_date.strftime('%Y-%m-%d'), 'page': 1},
        ])

        info_table = Table(patient_info, colWidths=[1.3*inch, 2.2*inch, 1.3*inch, 2.2*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f0f0')),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.25*inch))

        # Test results
        story.append(Paragraph("COMPREHENSIVE METABOLIC PANEL", self.section_style))

        test_data = [
            ['Test Name', 'Result', 'Units', 'Reference Range', 'Flag'],
            ['Glucose', str(random.randint(70, 130)), 'mg/dL', '70-99', random.choice(['', '', 'H'])],
            ['BUN', str(random.randint(7, 25)), 'mg/dL', '7-20', ''],
            ['Creatinine', str(round(random.uniform(0.6, 1.3), 1)), 'mg/dL', '0.7-1.3', ''],
            ['eGFR', str(random.randint(60, 120)), 'mL/min', '>60', ''],
            ['Sodium', str(random.randint(135, 145)), 'mEq/L', '136-144', ''],
            ['Potassium', str(round(random.uniform(3.5, 5.1), 1)), 'mEq/L', '3.5-5.0', random.choice(['', 'H'])],
            ['Chloride', str(random.randint(96, 106)), 'mEq/L', '96-106', ''],
            ['CO2', str(random.randint(22, 29)), 'mEq/L', '22-28', ''],
            ['Calcium', str(round(random.uniform(8.5, 10.5), 1)), 'mg/dL', '8.5-10.5', ''],
            ['Total Protein', str(round(random.uniform(6.0, 8.3), 1)), 'g/dL', '6.0-8.3', ''],
            ['Albumin', str(round(random.uniform(3.5, 5.0), 1)), 'g/dL', '3.5-5.0', ''],
            ['Bilirubin, Total', str(round(random.uniform(0.1, 1.2), 1)), 'mg/dL', '0.1-1.2', ''],
            ['Alk Phos', str(random.randint(30, 120)), 'IU/L', '30-120', ''],
            ['AST (SGOT)', str(random.randint(10, 40)), 'IU/L', '10-40', ''],
            ['ALT (SGPT)', str(random.randint(7, 56)), 'IU/L', '7-56', ''],
        ]

        test_table = Table(test_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 1.5*inch, 0.6*inch])
        test_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004080')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Highlight abnormal values
            ('TEXTCOLOR', (4, 1), (4, -1), colors.red),
            ('FONTNAME', (4, 1), (4, -1), 'Helvetica-Bold'),
        ]))
        story.append(test_table)
        story.append(Spacer(1, 0.2*inch))

        # CBC
        story.append(Paragraph("COMPLETE BLOOD COUNT", self.section_style))

        cbc_data = [
            ['Test Name', 'Result', 'Units', 'Reference Range', 'Flag'],
            ['WBC', str(round(random.uniform(4.0, 11.0), 1)), 'K/uL', '4.0-11.0', ''],
            ['RBC', str(round(random.uniform(4.2, 5.9), 2)), 'M/uL', '4.2-5.9', ''],
            ['Hemoglobin', str(round(random.uniform(12.0, 17.0), 1)), 'g/dL', '12.0-16.0', random.choice(['', 'H'])],
            ['Hematocrit', str(round(random.uniform(36.0, 48.0), 1)), '%', '36.0-46.0', ''],
            ['MCV', str(random.randint(80, 100)), 'fL', '80-100', ''],
            ['MCH', str(round(random.uniform(27.0, 34.0), 1)), 'pg', '27.0-34.0', ''],
            ['MCHC', str(round(random.uniform(32.0, 36.0), 1)), 'g/dL', '32.0-36.0', ''],
            ['Platelets', str(random.randint(150, 400)), 'K/uL', '150-400', ''],
        ]

        cbc_table = Table(cbc_data, colWidths=[2*inch, 0.8*inch, 0.8*inch, 1.5*inch, 0.6*inch])
        cbc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#004080')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TEXTCOLOR', (4, 1), (4, -1), colors.red),
            ('FONTNAME', (4, 1), (4, -1), 'Helvetica-Bold'),
        ]))
        story.append(cbc_table)
        story.append(Spacer(1, 0.2*inch))

        # Pathologist signature
        pathologist = f"Dr. {self.faker.name()}"
        annotations.append({'type': 'name', 'value': pathologist, 'page': 1, 'context': 'pathologist'})

        signature = f"""
        <b>Electronically signed by:</b> {pathologist}, MD<br/>
        <b>Board Certified Clinical Pathologist</b><br/>
        {report_date.strftime('%m/%d/%Y %H:%M')}
        """
        story.append(Paragraph(signature, self.body_style))

        # Footer
        story.append(Spacer(1, 0.15*inch))
        footer = "This report has been electronically signed. No signature required for legal validity."
        story.append(Paragraph(footer, self.small_style))

        doc.build(story)
        return annotations

    def create_insurance_claim(self, patient_data, output_path):
        """Create realistic CMS-1500 insurance claim form."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                                topMargin=0.3*inch, bottomMargin=0.3*inch)
        story = []
        annotations = []

        # Form header
        story.append(Paragraph("HEALTH INSURANCE CLAIM FORM", self.header_style))
        story.append(Paragraph("(CMS-1500 - 02/12)", self.small_style))
        story.append(Spacer(1, 0.15*inch))

        # Insurance carrier info
        carrier = f"{self.faker.company()} Health Insurance"
        carrier_address = self.faker.address().replace('\n', ', ')

        carrier_box = [
            ['CARRIER', carrier],
            ['Address', carrier_address],
        ]
        carrier_table = Table(carrier_box, colWidths=[1*inch, 5.5*inch])
        carrier_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(carrier_table)
        story.append(Spacer(1, 0.15*inch))

        # Patient information
        story.append(Paragraph("1-8. PATIENT INFORMATION", self.section_style))

        patient_info = [
            ['1. Patient Name (Last, First, MI)', patient_data['name']],
            ['2. Patient Date of Birth', patient_data['birth_date']],
            ['3. Patient Sex', random.choice(['M', 'F'])],
            ['4. Insured Name', patient_data['name']],
            ['5. Patient Address', patient_data['address']],
            ['6. Patient City, State, ZIP', f"{self.faker.city()}, {self.faker.state_abbr()} {self.faker.postcode()}"],
            ['7. Patient Phone', patient_data['phone']],
            ['8. Patient Status', 'Single'],
        ]

        annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1},
            {'type': 'address', 'value': patient_data['address'], 'page': 1},
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1},
        ])

        patient_table = Table(patient_info, colWidths=[2.5*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.15*inch))

        # Insurance information
        story.append(Paragraph("9-13. INSURANCE INFORMATION", self.section_style))

        insurance_info = [
            ['9. Insured ID Number', patient_data['insurance_id']],
            ['10. Patient Relationship to Insured', 'Self'],
            ['11. Insured Group Number', f"GRP-{self.faker.random_number(digits=6, fix_len=True)}"],
            ['12. Insured Date of Birth', patient_data['birth_date']],
            ['13. Insured SSN', patient_data['ssn']],
        ]

        annotations.extend([
            {'type': 'insurance_id', 'value': patient_data['insurance_id'], 'page': 1},
            {'type': 'ssn', 'value': patient_data['ssn'], 'page': 1},
        ])

        insurance_table = Table(insurance_info, colWidths=[2.5*inch, 4*inch])
        insurance_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        story.append(insurance_table)
        story.append(Spacer(1, 0.15*inch))

        # Provider information
        story.append(Paragraph("14-23. PROVIDER INFORMATION", self.section_style))

        provider_name = f"Dr. {self.faker.name()}"
        provider_npi = f"{self.faker.random_number(digits=10, fix_len=True)}"
        provider_tax_id = f"{self.faker.random_number(digits=2, fix_len=True)}-{self.faker.random_number(digits=7, fix_len=True)}"
        facility_name = f"{self.faker.company()} Medical Center"
        facility_address = self.faker.address().replace('\n', ', ')

        annotations.extend([
            {'type': 'name', 'value': provider_name, 'page': 1, 'context': 'provider'},
            {'type': 'unique_id', 'value': provider_npi, 'page': 1, 'context': 'npi'},
            {'type': 'institution', 'value': facility_name, 'page': 1},
            {'type': 'address', 'value': facility_address, 'page': 1, 'context': 'facility'},
        ])

        provider_info = [
            ['Rendering Provider', provider_name],
            ['NPI', provider_npi],
            ['Tax ID', provider_tax_id],
            ['Facility Name', facility_name],
            ['Facility Address', facility_address],
        ]

        provider_table = Table(provider_info, colWidths=[2.5*inch, 4*inch])
        provider_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        story.append(provider_table)
        story.append(Spacer(1, 0.15*inch))

        # Service details
        story.append(Paragraph("24. SERVICE DETAILS", self.section_style))

        service_date = datetime.now() - timedelta(days=random.randint(1, 30))
        annotations.append({'type': 'date', 'value': service_date.strftime('%Y-%m-%d'), 'page': 1, 'context': 'service'})

        # Diagnosis codes
        dx_codes = [
            ('J06.9', 'Acute upper respiratory infection'),
            ('R50.9', 'Fever, unspecified'),
            ('M25.511', 'Pain in right shoulder'),
        ]

        # Service lines
        service_data = [
            ['Date', 'CPT/HCPCS', 'Description', 'Units', 'Charge'],
            [service_date.strftime('%m/%d/%Y'), '99213', 'Office Visit - Established', '1', '$150.00'],
            [service_date.strftime('%m/%d/%Y'), '85025', 'Complete Blood Count', '1', '$45.00'],
            [service_date.strftime('%m/%d/%Y'), '80053', 'Comprehensive Metabolic Panel', '1', '$85.00'],
            ['', '', '', 'TOTAL:', '$280.00'],
        ]

        service_table = Table(service_data, colWidths=[1.2*inch, 1*inch, 2.5*inch, 0.7*inch, 1*inch])
        service_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -2), 0.25, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ]))
        story.append(service_table)
        story.append(Spacer(1, 0.2*inch))

        # Signature
        sig_date = datetime.now().strftime('%m/%d/%Y')
        annotations.append({'type': 'date', 'value': datetime.now().strftime('%Y-%m-%d'), 'page': 1, 'context': 'signature'})

        signature = f"""
        I certify that the statements on this form are true and accurate.<br/>
        <b>Patient/Authorized Person Signature:</b> _____________________ <b>Date:</b> {sig_date}<br/>
        <b>Provider Signature:</b> _____________________ <b>Date:</b> {sig_date}
        """
        story.append(Paragraph(signature, self.body_style))

        doc.build(story)
        return annotations


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate REALISTIC medical PDFs')
    parser.add_argument('--num-patients', type=int, default=100, help='Number of patients')
    parser.add_argument('--num-documents', type=int, default=500, help='Number of PDFs')
    parser.add_argument('--output-dir', type=str, default='./data/pdfs', help='Output directory')
    parser.add_argument('--annotations-dir', type=str, default='./data/annotations', help='Annotations directory')

    args = parser.parse_args()

    print("="*70)
    print("Generating REALISTIC Medical PDFs")
    print("="*70)
    print(f"Patients: {args.num_patients}")
    print(f"Documents: {args.num_documents}")
    print()

    # Generate patient data
    faker = Faker()
    Faker.seed(42)

    patients = []
    for i in range(args.num_patients):
        patient = {
            'name': faker.name(),
            'birth_date': faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
            'ssn': faker.ssn(),
            'phone': faker.phone_number(),
            'email': faker.email(),
            'address': faker.address().replace('\n', ', '),
            'mrn': f"MRN-{faker.random_number(digits=8, fix_len=True)}",
            'insurance_id': f"{random.choice(['ABC', 'XYZ', 'DEF'])}{faker.random_number(digits=9, fix_len=True)}",
            'medications': [
                {'name': random.choice([
                    'Lisinopril 10mg Tablet',
                    'Metformin 500mg Tablet',
                    'Atorvastatin 20mg Tablet',
                    'Amlodipine 5mg Tablet',
                    'Omeprazole 20mg Capsule',
                    'Levothyroxine 50mcg Tablet',
                    'Albuterol 90mcg Inhaler',
                    'Gabapentin 300mg Capsule',
                ]),
                 'dosage': f'Take {random.randint(1, 2)} tablet(s) {random.choice(["once daily", "twice daily", "three times daily", "as needed"])}'}
                for _ in range(random.randint(2, 5))
            ],
        }
        patients.append(patient)

    print(f"✓ Generated {len(patients)} synthetic patients")

    # Create generator
    generator = RealisticMedicalPDFGenerator()

    output_dir = Path(args.output_dir)
    annotations_dir = Path(args.annotations_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    annotations_dir.mkdir(parents=True, exist_ok=True)

    document_types = [
        ('prescription', generator.create_prescription),
        ('lab_report', generator.create_lab_report),
        ('insurance_claim', generator.create_insurance_claim),
    ]

    print(f"\nGenerating {args.num_documents} realistic medical PDFs...")

    for i in range(args.num_documents):
        patient = random.choice(patients)
        doc_type, create_func = random.choice(document_types)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_name = f"{doc_type}_{i:04d}_{timestamp}.pdf"
        pdf_path = output_dir / pdf_name

        # Create PDF
        annotations = create_func(patient, pdf_path)

        # Save annotations
        annotation_file = annotations_dir / f"{pdf_name}.json"
        with open(annotation_file, 'w') as f:
            json.dump({
                'document': pdf_name,
                'annotations': annotations,
                'timestamp': datetime.now().isoformat(),
                'num_phi_items': len(annotations),
                'phi_categories': list(set(a['type'] for a in annotations)),
            }, f, indent=2)

        if (i + 1) % 50 == 0:
            print(f"  Generated {i + 1}/{args.num_documents} PDFs...")

    print(f"\n✓ Generation complete!")
    print(f"\nGenerated files:")
    print(f"  {len(list(output_dir.glob('*.pdf')))} realistic medical PDFs")
    print(f"  {len(list(annotations_dir.glob('*.json')))} PHI annotation files")
    print(f"\nFeatures:")
    print(f"  • Realistic medical formatting and layouts")
    print(f"  • Proper medical terminology and codes")
    print(f"  • Multiple PHI categories (names, dates, MRN, SSN, etc.)")
    print(f"  • Tables with lab results and service details")
    print(f"  • Professional headers, footers, and signatures")
    print("="*70)


if __name__ == "__main__":
    main()
