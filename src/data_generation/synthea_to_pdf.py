"""
Convert Synthea synthetic patient data to realistic medical PDFs with PHI.
This module generates various medical document types from Synthea JSON/CSV output.
"""

import json
import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from faker import Faker


class MedicalPDFGenerator:
    """Generate realistic medical PDFs from Synthea data with full PHI."""

    def __init__(self, synthea_dir: str, output_dir: str, annotations_dir: str):
        """
        Initialize the PDF generator.

        Args:
            synthea_dir: Directory containing Synthea output
            output_dir: Directory to save generated PDFs
            annotations_dir: Directory to save PHI annotations
        """
        self.synthea_dir = Path(synthea_dir)
        self.output_dir = Path(output_dir)
        self.annotations_dir = Path(annotations_dir)

        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.annotations_dir.mkdir(parents=True, exist_ok=True)

        # Initialize faker for additional realistic data
        self.faker = Faker()
        Faker.seed(42)

        # PHI tracking for annotations
        self.phi_annotations = []

        # Document templates
        self.document_types = [
            'prescription',
            'lab_report',
            'discharge_summary',
            'insurance_claim',
            'medical_record',
            'referral_letter',
            'consultation_note',
            'radiology_report',
        ]

    def load_synthea_patient(self, patient_file: Path) -> Dict:
        """Load a Synthea patient from FHIR JSON."""
        with open(patient_file, 'r') as f:
            return json.load(f)

    def extract_patient_info(self, bundle: Dict) -> Dict[str, Any]:
        """Extract relevant patient information from FHIR bundle."""
        patient_info = {
            'name': '',
            'birth_date': '',
            'ssn': '',
            'phone': '',
            'email': '',
            'address': '',
            'mrn': '',
            'insurance_id': '',
            'conditions': [],
            'medications': [],
            'procedures': [],
            'encounters': [],
            'allergies': [],
            'immunizations': [],
            'observations': [],
        }

        for entry in bundle.get('entry', []):
            resource = entry.get('resource', {})
            resource_type = resource.get('resourceType', '')

            if resource_type == 'Patient':
                # Extract patient demographics
                name_data = resource.get('name', [{}])[0]
                patient_info['name'] = f"{name_data.get('given', [''])[0]} {name_data.get('family', '')}"
                patient_info['birth_date'] = resource.get('birthDate', '')

                # Extract SSN from identifier
                for identifier in resource.get('identifier', []):
                    if identifier.get('system') == 'http://hl7.org/fhir/sid/us-ssn':
                        patient_info['ssn'] = identifier.get('value', self.faker.ssn())

                # Extract contact information
                telecom = resource.get('telecom', [])
                for contact in telecom:
                    if contact.get('system') == 'phone':
                        patient_info['phone'] = contact.get('value', self.faker.phone_number())
                    elif contact.get('system') == 'email':
                        patient_info['email'] = contact.get('value', self.faker.email())

                # Extract address
                address_data = resource.get('address', [{}])[0]
                patient_info['address'] = self._format_address(address_data)

                # Generate MRN
                patient_info['mrn'] = f"MRN-{self.faker.random_number(digits=8, fix_len=True)}"

            elif resource_type == 'Condition':
                condition = {
                    'code': resource.get('code', {}).get('text', ''),
                    'onset': resource.get('onsetDateTime', ''),
                    'status': resource.get('clinicalStatus', {}).get('text', ''),
                }
                patient_info['conditions'].append(condition)

            elif resource_type == 'MedicationRequest':
                medication = {
                    'name': resource.get('medicationCodeableConcept', {}).get('text', ''),
                    'dosage': self._extract_dosage(resource.get('dosageInstruction', [])),
                    'prescriber': self._extract_prescriber(resource),
                }
                patient_info['medications'].append(medication)

            elif resource_type == 'Procedure':
                procedure = {
                    'name': resource.get('code', {}).get('text', ''),
                    'date': resource.get('performedDateTime', resource.get('performedPeriod', {}).get('start', '')),
                    'performer': self._extract_performer(resource),
                }
                patient_info['procedures'].append(procedure)

            elif resource_type == 'Encounter':
                encounter = {
                    'type': resource.get('class', {}).get('display', ''),
                    'period': resource.get('period', {}),
                    'reason': self._extract_reason(resource),
                }
                patient_info['encounters'].append(encounter)

            elif resource_type == 'AllergyIntolerance':
                allergy = {
                    'substance': resource.get('code', {}).get('text', ''),
                    'severity': resource.get('criticality', ''),
                }
                patient_info['allergies'].append(allergy)

        # Generate insurance ID
        patient_info['insurance_id'] = f"INS-{self.faker.random_number(digits=10, fix_len=True)}"

        return patient_info

    def _format_address(self, address_data: Dict) -> str:
        """Format address from FHIR address structure."""
        lines = address_data.get('line', [])
        city = address_data.get('city', self.faker.city())
        state = address_data.get('state', self.faker.state_abbr())
        postal = address_data.get('postalCode', self.faker.postcode())

        if not lines:
            lines = [self.faker.street_address()]

        return f"{', '.join(lines)}, {city}, {state} {postal}"

    def _extract_dosage(self, dosage_instructions: List) -> str:
        """Extract dosage information."""
        if not dosage_instructions:
            return "Take as directed"

        dosage = dosage_instructions[0]
        text = dosage.get('text', '')
        if text:
            return text

        # Build dosage string from components
        timing = dosage.get('timing', {}).get('repeat', {})
        frequency = timing.get('frequency', 1)
        period = timing.get('period', 1)
        period_unit = timing.get('periodUnit', 'day')

        return f"{frequency} time(s) per {period} {period_unit}"

    def _extract_prescriber(self, resource: Dict) -> str:
        """Extract prescriber name."""
        requester = resource.get('requester', {})
        display = requester.get('display', '')
        if display:
            return display
        return f"Dr. {self.faker.last_name()}"

    def _extract_performer(self, resource: Dict) -> str:
        """Extract performer name."""
        performers = resource.get('performer', [])
        if performers:
            return performers[0].get('actor', {}).get('display', f"Dr. {self.faker.last_name()}")
        return f"Dr. {self.faker.last_name()}"

    def _extract_reason(self, resource: Dict) -> str:
        """Extract encounter reason."""
        reasons = resource.get('reasonCode', [])
        if reasons:
            return reasons[0].get('text', 'Routine checkup')
        return 'Routine checkup'

    def create_prescription(self, patient_info: Dict, output_path: Path) -> List[Dict]:
        """Create a prescription PDF."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        phi_annotations = []

        # Header
        header_style = ParagraphStyle(
            'CustomHeader',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#003366'),
            alignment=1,  # Center
        )

        story.append(Paragraph("PRESCRIPTION", header_style))
        story.append(Spacer(1, 0.2 * inch))

        # Clinic information
        clinic_name = f"{self.faker.company()} Medical Center"
        clinic_address = self.faker.address().replace('\n', ', ')
        clinic_phone = self.faker.phone_number()
        dea_number = f"DEA: B{self.faker.random_number(digits=7, fix_len=True)}"
        npi_number = f"NPI: {self.faker.random_number(digits=10, fix_len=True)}"

        clinic_info = f"""
        <para align=center>
        <b>{clinic_name}</b><br/>
        {clinic_address}<br/>
        Phone: {clinic_phone}<br/>
        {dea_number} | {npi_number}
        </para>
        """
        story.append(Paragraph(clinic_info, styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Patient information (PHI)
        patient_data = [
            ['Patient Name:', patient_info['name']],  # PHI: Name
            ['Date of Birth:', patient_info['birth_date']],  # PHI: Date
            ['MRN:', patient_info['mrn']],  # PHI: MRN
            ['Address:', patient_info['address']],  # PHI: Address
            ['Phone:', patient_info['phone']],  # PHI: Phone
            ['Date:', datetime.now().strftime('%Y-%m-%d')],  # PHI: Date
        ]

        # Track PHI locations for annotations
        phi_annotations.append({'type': 'name', 'value': patient_info['name'], 'page': 1})
        phi_annotations.append({'type': 'date', 'value': patient_info['birth_date'], 'page': 1})
        phi_annotations.append({'type': 'mrn', 'value': patient_info['mrn'], 'page': 1})
        phi_annotations.append({'type': 'address', 'value': patient_info['address'], 'page': 1})
        phi_annotations.append({'type': 'phone', 'value': patient_info['phone'], 'page': 1})

        patient_table = Table(patient_data, colWidths=[2 * inch, 4 * inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.3 * inch))

        # Prescription details
        story.append(Paragraph("℞", ParagraphStyle('Rx', fontSize=20, alignment=0)))
        story.append(Spacer(1, 0.1 * inch))

        # Add medications
        if patient_info['medications']:
            for i, med in enumerate(patient_info['medications'][:3]):  # Limit to 3 medications
                med_text = f"""
                <para leftIndent=20>
                <b>{med['name']}</b><br/>
                Sig: {med['dosage']}<br/>
                Quantity: {random.randint(30, 90)}<br/>
                Refills: {random.randint(0, 3)}
                </para>
                """
                story.append(Paragraph(med_text, styles['Normal']))
                story.append(Spacer(1, 0.2 * inch))
        else:
            # Generate synthetic medication if none available
            med_name = self.faker.word().capitalize() + "mycin 500mg"
            med_text = f"""
            <para leftIndent=20>
            <b>{med_name}</b><br/>
            Sig: Take 1 tablet by mouth twice daily<br/>
            Quantity: 60<br/>
            Refills: 2
            </para>
            """
            story.append(Paragraph(med_text, styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))

        # Prescriber signature
        prescriber_name = f"Dr. {self.faker.name()}"
        license_number = f"License: {self.faker.random_number(digits=8, fix_len=True)}"

        phi_annotations.append({'type': 'name', 'value': prescriber_name, 'page': 1})

        signature_text = f"""
        <para>
        <br/><br/>
        _________________________________<br/>
        {prescriber_name}, MD<br/>
        {license_number}
        </para>
        """
        story.append(Paragraph(signature_text, styles['Normal']))

        # Build PDF
        doc.build(story)

        return phi_annotations

    def create_lab_report(self, patient_info: Dict, output_path: Path) -> List[Dict]:
        """Create a laboratory report PDF."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        phi_annotations = []

        # Header
        header_style = ParagraphStyle(
            'LabHeader',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#800020'),
            alignment=1,
        )

        story.append(Paragraph("LABORATORY REPORT", header_style))
        story.append(Spacer(1, 0.2 * inch))

        # Lab information
        lab_name = f"{self.faker.company()} Diagnostics"
        lab_address = self.faker.address().replace('\n', ', ')
        lab_phone = self.faker.phone_number()
        clia_number = f"CLIA: {self.faker.random_number(digits=10, fix_len=True)}"

        lab_info = f"""
        <para align=center>
        <b>{lab_name}</b><br/>
        {lab_address}<br/>
        Phone: {lab_phone} | {clia_number}
        </para>
        """
        story.append(Paragraph(lab_info, styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Patient and specimen information
        specimen_id = f"SPEC-{self.faker.random_number(digits=10, fix_len=True)}"
        accession_number = f"ACC-{self.faker.random_number(digits=8, fix_len=True)}"
        collection_date = datetime.now() - timedelta(days=random.randint(1, 7))
        report_date = datetime.now()

        patient_data = [
            ['Patient Name:', patient_info['name']],  # PHI
            ['Date of Birth:', patient_info['birth_date']],  # PHI
            ['SSN:', patient_info['ssn']],  # PHI
            ['MRN:', patient_info['mrn']],  # PHI
            ['Collection Date:', collection_date.strftime('%Y-%m-%d %H:%M')],  # PHI
            ['Report Date:', report_date.strftime('%Y-%m-%d %H:%M')],  # PHI
            ['Specimen ID:', specimen_id],
            ['Accession #:', accession_number],
        ]

        # Track PHI
        phi_annotations.extend([
            {'type': 'name', 'value': patient_info['name'], 'page': 1},
            {'type': 'date', 'value': patient_info['birth_date'], 'page': 1},
            {'type': 'ssn', 'value': patient_info['ssn'], 'page': 1},
            {'type': 'mrn', 'value': patient_info['mrn'], 'page': 1},
            {'type': 'date', 'value': collection_date.strftime('%Y-%m-%d'), 'page': 1},
            {'type': 'date', 'value': report_date.strftime('%Y-%m-%d'), 'page': 1},
        ])

        info_table = Table(patient_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.3 * inch))

        # Test results
        story.append(Paragraph("TEST RESULTS", styles['Heading2']))
        story.append(Spacer(1, 0.1 * inch))

        # Create test results table
        test_data = [
            ['Test Name', 'Result', 'Units', 'Reference Range', 'Flag'],
        ]

        # Generate realistic lab values
        tests = [
            ('Glucose', random.randint(70, 120), 'mg/dL', '70-99', ''),
            ('Creatinine', round(random.uniform(0.6, 1.2), 1), 'mg/dL', '0.7-1.3', ''),
            ('BUN', random.randint(7, 25), 'mg/dL', '7-20', ''),
            ('Sodium', random.randint(135, 145), 'mEq/L', '136-144', ''),
            ('Potassium', round(random.uniform(3.5, 5.0), 1), 'mEq/L', '3.5-5.0', ''),
            ('Chloride', random.randint(96, 106), 'mEq/L', '96-106', ''),
            ('CO2', random.randint(22, 28), 'mEq/L', '22-28', ''),
            ('Hemoglobin', round(random.uniform(12.0, 17.0), 1), 'g/dL', '12.0-16.0', ''),
            ('Hematocrit', round(random.uniform(36.0, 48.0), 1), '%', '36.0-46.0', ''),
            ('WBC Count', round(random.uniform(4.5, 11.0), 1), 'K/uL', '4.5-11.0', ''),
        ]

        for test_name, value, units, ref_range, flag in tests:
            # Randomly flag some abnormal values
            if random.random() < 0.2:
                if random.choice([True, False]):
                    flag = 'H'  # High
                else:
                    flag = 'L'  # Low

            test_data.append([test_name, str(value), units, ref_range, flag])

        test_table = Table(test_data, colWidths=[2 * inch, 1 * inch, 1 * inch, 1.5 * inch, 0.5 * inch])
        test_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            # Highlight abnormal flags
            ('TEXTCOLOR', (4, 1), (4, -1), colors.red),
            ('FONTNAME', (4, 1), (4, -1), 'Helvetica-Bold'),
        ]))
        story.append(test_table)
        story.append(Spacer(1, 0.3 * inch))

        # Pathologist signature
        pathologist_name = f"Dr. {self.faker.name()}"
        pathologist_title = "Clinical Pathologist"
        license_number = f"License: {self.faker.random_number(digits=8, fix_len=True)}"

        phi_annotations.append({'type': 'name', 'value': pathologist_name, 'page': 1})

        signature_text = f"""
        <para>
        Reviewed and Approved by:<br/><br/>
        _________________________________<br/>
        {pathologist_name}, MD<br/>
        {pathologist_title}<br/>
        {license_number}
        </para>
        """
        story.append(Paragraph(signature_text, styles['Normal']))

        # Build PDF
        doc.build(story)

        return phi_annotations

    def create_insurance_claim(self, patient_info: Dict, output_path: Path) -> List[Dict]:
        """Create an insurance claim form PDF."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        phi_annotations = []

        # Header
        header_style = ParagraphStyle(
            'ClaimHeader',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#000080'),
            alignment=1,
        )

        story.append(Paragraph("HEALTH INSURANCE CLAIM FORM", header_style))
        story.append(Paragraph("CMS-1500 (02-12)", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Insurance information
        insurance_company = f"{self.faker.company()} Health Insurance"
        policy_number = patient_info['insurance_id']
        group_number = f"GRP-{self.faker.random_number(digits=6, fix_len=True)}"

        # Patient information section
        story.append(Paragraph("<b>PATIENT INFORMATION</b>", styles['Heading3']))

        patient_data = [
            ['1. Patient Name:', patient_info['name']],  # PHI
            ['2. Date of Birth:', patient_info['birth_date']],  # PHI
            ['3. SSN:', patient_info['ssn']],  # PHI
            ['4. Patient Address:', patient_info['address']],  # PHI
            ['5. Phone:', patient_info['phone']],  # PHI
            ['6. Email:', patient_info['email']],  # PHI
            ['7. Policy Number:', policy_number],  # PHI
            ['8. Group Number:', group_number],
        ]

        # Track PHI
        phi_annotations.extend([
            {'type': 'name', 'value': patient_info['name'], 'page': 1},
            {'type': 'date', 'value': patient_info['birth_date'], 'page': 1},
            {'type': 'ssn', 'value': patient_info['ssn'], 'page': 1},
            {'type': 'address', 'value': patient_info['address'], 'page': 1},
            {'type': 'phone', 'value': patient_info['phone'], 'page': 1},
            {'type': 'email', 'value': patient_info['email'], 'page': 1},
            {'type': 'insurance_id', 'value': policy_number, 'page': 1},
        ])

        patient_table = Table(patient_data, colWidths=[2 * inch, 4 * inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.2 * inch))

        # Provider information
        story.append(Paragraph("<b>PROVIDER INFORMATION</b>", styles['Heading3']))

        provider_name = f"Dr. {self.faker.name()}"
        provider_npi = f"{self.faker.random_number(digits=10, fix_len=True)}"
        provider_tax_id = f"{self.faker.random_number(digits=2, fix_len=True)}-{self.faker.random_number(digits=7, fix_len=True)}"
        facility_name = f"{self.faker.company()} Medical Center"
        facility_address = self.faker.address().replace('\n', ', ')

        provider_data = [
            ['Provider Name:', provider_name],  # PHI
            ['NPI:', provider_npi],
            ['Tax ID:', provider_tax_id],
            ['Facility:', facility_name],
            ['Facility Address:', facility_address],  # PHI
        ]

        phi_annotations.extend([
            {'type': 'name', 'value': provider_name, 'page': 1},
            {'type': 'address', 'value': facility_address, 'page': 1},
        ])

        provider_table = Table(provider_data, colWidths=[2 * inch, 4 * inch])
        provider_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(provider_table)
        story.append(Spacer(1, 0.2 * inch))

        # Diagnosis and procedures
        story.append(Paragraph("<b>DIAGNOSIS AND TREATMENT</b>", styles['Heading3']))

        # Add diagnosis codes
        diagnosis_data = [
            ['ICD-10 Code', 'Description'],
        ]

        # Use actual conditions or generate synthetic ones
        if patient_info['conditions']:
            for condition in patient_info['conditions'][:4]:
                icd_code = f"{chr(random.randint(65, 90))}{random.randint(10, 99)}.{random.randint(0, 9)}"
                diagnosis_data.append([icd_code, condition['code']])
        else:
            diagnosis_data.extend([
                ['J06.9', 'Acute upper respiratory infection'],
                ['R50.9', 'Fever, unspecified'],
            ])

        diagnosis_table = Table(diagnosis_data, colWidths=[1.5 * inch, 4.5 * inch])
        diagnosis_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        story.append(diagnosis_table)
        story.append(Spacer(1, 0.2 * inch))

        # Service lines
        story.append(Paragraph("<b>SERVICES PROVIDED</b>", styles['Heading3']))

        service_data = [
            ['Date', 'CPT Code', 'Description', 'Units', 'Charge'],
        ]

        # Generate service lines
        service_date = datetime.now() - timedelta(days=random.randint(1, 30))
        services = [
            ('99213', 'Office visit, established patient', 1, 150.00),
            ('80053', 'Comprehensive metabolic panel', 1, 85.00),
            ('85025', 'Complete blood count', 1, 45.00),
        ]

        total_charges = 0
        for cpt, desc, units, charge in services:
            service_data.append([
                service_date.strftime('%m/%d/%Y'),  # PHI: Date
                cpt,
                desc,
                str(units),
                f"${charge:.2f}",
            ])
            total_charges += charge
            phi_annotations.append({'type': 'date', 'value': service_date.strftime('%Y-%m-%d'), 'page': 1})

        service_data.append(['', '', '', 'TOTAL:', f"${total_charges:.2f}"])

        service_table = Table(service_data, colWidths=[1 * inch, 1 * inch, 2.5 * inch, 0.75 * inch, 0.75 * inch])
        service_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -2), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ]))
        story.append(service_table)
        story.append(Spacer(1, 0.3 * inch))

        # Signature section
        signature_date = datetime.now().strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': signature_date, 'page': 1})

        signature_text = f"""
        <para>
        I authorize payment of medical benefits to the provider.<br/><br/>
        Patient Signature: _______________________________ Date: {signature_date}<br/><br/>
        Provider Signature: ______________________________ Date: {signature_date}
        </para>
        """
        story.append(Paragraph(signature_text, styles['Normal']))

        # Build PDF
        doc.build(story)

        return phi_annotations

    def add_realistic_noise(self, pdf_path: Path) -> None:
        """Add realistic scanning artifacts to make PDFs look more authentic."""
        # This would add noise, slight rotation, blur, etc.
        # For now, we'll keep the PDFs clean for better initial training
        pass

    def save_annotations(self, pdf_name: str, annotations: List[Dict]) -> None:
        """Save PHI annotations for a PDF."""
        annotation_file = self.annotations_dir / f"{pdf_name}.json"

        with open(annotation_file, 'w') as f:
            json.dump({
                'document': pdf_name,
                'annotations': annotations,
                'timestamp': datetime.now().isoformat(),
            }, f, indent=2)

    def generate_pdfs_from_synthea(self, num_documents: int = 100) -> None:
        """Generate multiple PDFs from Synthea data."""
        print(f"Generating {num_documents} medical PDFs with PHI...")

        # Find Synthea FHIR bundles
        fhir_dir = self.synthea_dir / 'fhir'
        if not fhir_dir.exists():
            print(f"Error: FHIR directory not found at {fhir_dir}")
            print("Please run Synthea first to generate patient data.")
            return

        patient_files = list(fhir_dir.glob('*.json'))
        if not patient_files:
            print(f"No patient files found in {fhir_dir}")
            return

        print(f"Found {len(patient_files)} patient files")

        # Generate PDFs
        for i in range(min(num_documents, len(patient_files) * len(self.document_types))):
            patient_file = random.choice(patient_files)
            doc_type = random.choice(self.document_types)

            try:
                # Load patient data
                bundle = self.load_synthea_patient(patient_file)
                patient_info = self.extract_patient_info(bundle)

                # Generate filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                pdf_name = f"{doc_type}_{i:04d}_{timestamp}.pdf"
                pdf_path = self.output_dir / pdf_name

                # Generate PDF based on type
                if doc_type == 'prescription':
                    annotations = self.create_prescription(patient_info, pdf_path)
                elif doc_type == 'lab_report':
                    annotations = self.create_lab_report(patient_info, pdf_path)
                elif doc_type == 'insurance_claim':
                    annotations = self.create_insurance_claim(patient_info, pdf_path)
                else:
                    # For other types, use a default template
                    annotations = self.create_prescription(patient_info, pdf_path)

                # Save annotations
                self.save_annotations(pdf_name, annotations)

                print(f"✓ Generated {pdf_name} with {len(annotations)} PHI annotations")

            except Exception as e:
                print(f"✗ Error generating PDF {i}: {e}")
                continue

        print(f"\nGeneration complete!")
        print(f"PDFs saved to: {self.output_dir}")
        print(f"Annotations saved to: {self.annotations_dir}")


def main():
    """Main function to run PDF generation."""
    import argparse

    parser = argparse.ArgumentParser(description='Generate medical PDFs from Synthea data')
    parser.add_argument('--synthea-output', type=str, default='./data/synthetic/synthea',
                        help='Path to Synthea output directory')
    parser.add_argument('--pdf-output', type=str, default='./data/pdfs',
                        help='Directory to save generated PDFs')
    parser.add_argument('--annotations-output', type=str, default='./data/annotations',
                        help='Directory to save PHI annotations')
    parser.add_argument('--num-documents', type=int, default=100,
                        help='Number of PDFs to generate')

    args = parser.parse_args()

    # Create generator
    generator = MedicalPDFGenerator(
        synthea_dir=args.synthea_output,
        output_dir=args.pdf_output,
        annotations_dir=args.annotations_output
    )

    # Generate PDFs
    generator.generate_pdfs_from_synthea(args.num_documents)


if __name__ == '__main__':
    main()