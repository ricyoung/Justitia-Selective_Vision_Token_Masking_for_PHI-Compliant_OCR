#!/usr/bin/env python3
"""
Generate final 5 document types to reach 20 total document types.
Creates: consent forms, MAR, billing statements, test requisitions, therapy notes.
"""

import sys
import os
from pathlib import Path
from faker import Faker
import random
import json
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY


class FinalDocumentTypesGenerator:
    """Generate the final 5 document types."""

    def __init__(self):
        self.faker = Faker()
        Faker.seed(42)
        self.styles = getSampleStyleSheet()

        # Add custom styles
        self.styles.add(ParagraphStyle(
            name='CenterBold',
            parent=self.styles['Normal'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            fontSize=14
        ))

        self.styles.add(ParagraphStyle(
            name='SmallJustify',
            parent=self.styles['Normal'],
            alignment=TA_JUSTIFY,
            fontSize=8
        ))

    def create_consent_form(self, patient_data, output_path):
        """Create surgical/procedure consent form."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Hospital header
        facility = random.choice([
            "Massachusetts General Hospital",
            "University Medical Center",
            "St. Mary's Surgical Center"
        ])

        story.append(Paragraph(f"<b>{facility}</b>", self.styles['CenterBold']))
        story.append(Paragraph("INFORMED CONSENT FOR PROCEDURE", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.append({'type': 'institution', 'value': facility, 'page': 1, 'context': 'facility'})

        # Patient info
        consent_date = datetime.now().strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': consent_date, 'page': 1, 'context': 'consent'})

        patient_info = [
            ['Patient Name:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['Date of Birth:', patient_data['birth_date'], 'Date:', consent_date],
            ['Address:', patient_data['address'], '', ''],
            ['Phone:', patient_data['phone'], 'Email:', patient_data.get('email', self.faker.email())],
        ]

        email = patient_info[3][3]

        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'address', 'value': patient_data['address'], 'page': 1},
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1},
            {'type': 'email', 'value': email, 'page': 1}
        ])

        info_table = Table(patient_info, colWidths=[1.5*inch, 2.5*inch, 1*inch, 1.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('SPAN', (1, 2), (3, 2)),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # Procedure info
        procedure = random.choice([
            "Laparoscopic Cholecystectomy",
            "Total Knee Arthroplasty",
            "Coronary Artery Bypass Graft",
            "Appendectomy",
            "Hernia Repair"
        ])

        surgeon = f"Dr. {self.faker.last_name()}, MD"
        phi_annotations.append({'type': 'name', 'value': surgeon, 'page': 1, 'context': 'surgeon'})

        story.append(Paragraph(f"<b>PROCEDURE:</b> {procedure}", self.styles['Normal']))
        story.append(Paragraph(f"<b>SURGEON:</b> {surgeon}", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Consent text
        story.append(Paragraph("<b>CONSENT TO TREATMENT</b>", self.styles['Normal']))
        consent_text = f"""
        I, {patient_data['name']}, hereby authorize {surgeon} and such assistants as may be selected to perform
        the following procedure: <b>{procedure}</b>. The procedure has been explained to me by {surgeon},
        and I understand the nature of the procedure, the risks involved, and the expected benefits.
        <br/><br/>
        I understand that the practice of medicine is not an exact science and I acknowledge that no guarantees have been
        made to me concerning the results of the procedure. I have been given the opportunity to ask questions and all my
        questions have been answered to my satisfaction.
        <br/><br/>
        I understand the risks include but are not limited to: bleeding, infection, adverse reactions to anesthesia,
        blood clots, nerve damage, and in rare cases, death. Alternative treatments have been explained to me including
        the option of no treatment.
        """
        story.append(Paragraph(consent_text, self.styles['SmallJustify']))
        story.append(Spacer(1, 0.2 * inch))

        # Witness info
        witness_name = self.faker.name()
        witness_title = random.choice(['RN', 'PA', 'Medical Assistant', 'Nurse Practitioner'])

        phi_annotations.append({'type': 'name', 'value': witness_name, 'page': 1, 'context': 'witness'})

        # Signature section
        story.append(Paragraph("<b>SIGNATURES</b>", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        sig_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        phi_annotations.append({'type': 'date', 'value': sig_date.split()[0], 'page': 1, 'context': 'signature'})

        sig_data = [
            ['Patient Signature:', '_' * 40, 'Date/Time:', sig_date],
            ['', '', '', ''],
            ['Witness Signature:', '_' * 40, 'Title:', witness_title],
            ['Witness Name (Print):', witness_name, 'Date/Time:', sig_date],
        ]

        sig_table = Table(sig_data, colWidths=[1.5*inch, 3*inch, 1*inch, 1.5*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(sig_table)

        doc.build(story)
        return phi_annotations

    def create_mar(self, patient_data, output_path):
        """Create Medication Administration Record."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Header
        facility = random.choice([
            "Massachusetts General Hospital - 5 West",
            "University Medical Center - ICU",
            "St. Mary's Hospital - Med-Surg"
        ])

        story.append(Paragraph(f"<b>{facility}</b>", self.styles['CenterBold']))
        story.append(Paragraph("MEDICATION ADMINISTRATION RECORD", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.append({'type': 'institution', 'value': facility, 'page': 1, 'context': 'unit'})

        # Date range
        mar_date = datetime.now().strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': mar_date, 'page': 1, 'context': 'mar'})

        # Patient info
        patient_info = [
            ['Patient:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['DOB:', patient_data['birth_date'], 'Room:', f"{random.randint(100, 999)}-{random.choice(['A', 'B'])}"],
            ['Allergies:', random.choice(['NKDA', 'Penicillin', 'Sulfa drugs']), 'Date:', mar_date],
        ]

        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'}
        ])

        info_table = Table(patient_info, colWidths=[1*inch, 2.5*inch, 1*inch, 1.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # MAR entries
        story.append(Paragraph("<b>SCHEDULED MEDICATIONS</b>", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Create medication schedule
        medications = [
            {'drug': 'Metoprolol 25mg PO', 'times': ['0800', '2000']},
            {'drug': 'Lisinopril 10mg PO', 'times': ['0800']},
            {'drug': 'Insulin Glargine 20 units SC', 'times': ['2100']},
            {'drug': 'Aspirin 81mg PO', 'times': ['0800']},
        ]

        # Generate administration times with nurse initials
        nurses = [
            {'name': self.faker.name(), 'initials': f"{self.faker.first_name()[0]}{self.faker.last_name()[0]}"},
            {'name': self.faker.name(), 'initials': f"{self.faker.first_name()[0]}{self.faker.last_name()[0]}"},
        ]

        for nurse in nurses:
            phi_annotations.append({'type': 'name', 'value': nurse['name'], 'page': 1, 'context': 'nurse'})

        mar_data = [['Medication', '0800', '1200', '1600', '2000', '2100']]

        for med in medications:
            row = [med['drug']]
            for time in ['0800', '1200', '1600', '2000', '2100']:
                if time in med['times']:
                    nurse = random.choice(nurses)
                    row.append(nurse['initials'])
                else:
                    row.append('')
            mar_data.append(row)

        mar_table = Table(mar_data, colWidths=[2.5*inch, 0.75*inch, 0.75*inch, 0.75*inch, 0.75*inch, 0.75*inch])
        mar_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(mar_table)
        story.append(Spacer(1, 0.2 * inch))

        # Signature legend
        story.append(Paragraph("<b>SIGNATURE LEGEND</b>", self.styles['Normal']))
        sig_legend = [[nurses[0]['initials'], nurses[0]['name'], nurses[1]['initials'], nurses[1]['name']]]

        legend_table = Table(sig_legend, colWidths=[0.5*inch, 2.5*inch, 0.5*inch, 2.5*inch])
        legend_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(legend_table)

        doc.build(story)
        return phi_annotations

    def create_billing_statement(self, patient_data, output_path):
        """Create medical billing statement."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Billing header
        provider = random.choice([
            "Massachusetts Medical Billing Services",
            "University Health System Revenue Cycle",
            "Commonwealth Healthcare Billing"
        ])

        billing_address = self.faker.address().replace('\n', ', ')
        billing_phone = self.faker.phone_number()

        story.append(Paragraph(f"<b>{provider}</b>", self.styles['Normal']))
        story.append(Paragraph(billing_address, self.styles['Normal']))
        story.append(Paragraph(f"Phone: {billing_phone}", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.extend([
            {'type': 'institution', 'value': provider, 'page': 1, 'context': 'billing'},
            {'type': 'address', 'value': billing_address, 'page': 1, 'context': 'billing_address'},
            {'type': 'phone', 'value': billing_phone, 'page': 1, 'context': 'billing_phone'}
        ])

        # Statement info
        story.append(Paragraph("<b>STATEMENT</b>", self.styles['CenterBold']))
        story.append(Spacer(1, 0.1 * inch))

        statement_date = datetime.now().strftime('%Y-%m-%d')
        account_number = f"ACCT-{self.faker.random_number(digits=10, fix_len=True)}"
        statement_number = f"STMT-{self.faker.random_number(digits=8, fix_len=True)}"

        phi_annotations.extend([
            {'type': 'date', 'value': statement_date, 'page': 1, 'context': 'statement'},
            {'type': 'account', 'value': account_number, 'page': 1},
            {'type': 'unique_id', 'value': statement_number, 'page': 1, 'context': 'statement_number'}
        ])

        statement_info = [
            ['Statement Date:', statement_date, 'Account Number:', account_number],
            ['Statement Number:', statement_number, 'Due Date:', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')],
        ]

        due_date = statement_info[1][3]
        phi_annotations.append({'type': 'date', 'value': due_date, 'page': 1, 'context': 'due'})

        info_table = Table(statement_info, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # Patient/Guarantor info
        story.append(Paragraph("<b>PATIENT INFORMATION</b>", self.styles['Normal']))
        patient_billing = [
            ['Patient Name:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['Date of Birth:', patient_data['birth_date'], 'SSN:', patient_data['ssn']],
            ['Address:', patient_data['address'], '', ''],
            ['Phone:', patient_data['phone'], 'Email:', patient_data.get('email', self.faker.email())],
        ]

        email = patient_billing[3][3]

        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'ssn', 'value': patient_data['ssn'], 'page': 1},
            {'type': 'address', 'value': patient_data['address'], 'page': 1},
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1},
            {'type': 'email', 'value': email, 'page': 1}
        ])

        patient_table = Table(patient_billing, colWidths=[1.5*inch, 2.5*inch, 1*inch, 1.5*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('SPAN', (1, 2), (3, 2)),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.2 * inch))

        # Service details
        story.append(Paragraph("<b>STATEMENT OF SERVICES</b>", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        service_date = self.faker.date_between(start_date='-60d', end_date='-30d').strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': service_date, 'page': 1, 'context': 'service'})

        services = [
            ['Date', 'Description', 'Charges', 'Insurance', 'Patient Resp.'],
            [service_date, 'Office Visit - Level 4 (99214)', '$275.00', '$220.00', '$55.00'],
            [service_date, 'Laboratory - CBC (85025)', '$125.00', '$100.00', '$25.00'],
            [service_date, 'Laboratory - CMP (80053)', '$150.00', '$120.00', '$30.00'],
        ]

        service_table = Table(services, colWidths=[1*inch, 2.5*inch, 1*inch, 1*inch, 1*inch])
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ]))
        story.append(service_table)
        story.append(Spacer(1, 0.1 * inch))

        # Summary
        summary_data = [
            ['Total Charges:', '$550.00'],
            ['Insurance Payments:', '$440.00'],
            ['Previous Balance:', '$0.00'],
            ['<b>Amount Due:</b>', '<b>$110.00</b>'],
        ]

        summary_table = Table(summary_data, colWidths=[5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
        ]))
        story.append(summary_table)

        doc.build(story)
        return phi_annotations

    def create_test_requisition(self, patient_data, output_path):
        """Create lab/imaging test requisition form."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Header
        test_type = random.choice(['LABORATORY', 'RADIOLOGY', 'PATHOLOGY'])
        facility = random.choice([
            f"Massachusetts {test_type.title()} Services",
            f"University Medical Center - {test_type.title()}",
            f"Regional {test_type.title()} Center"
        ])

        story.append(Paragraph(f"<b>{facility}</b>", self.styles['CenterBold']))
        story.append(Paragraph(f"{test_type} TEST REQUISITION", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.append({'type': 'institution', 'value': facility, 'page': 1, 'context': 'lab'})

        # Requisition info
        req_date = datetime.now().strftime('%Y-%m-%d')
        req_number = f"REQ-{self.faker.random_number(digits=10, fix_len=True)}"

        phi_annotations.extend([
            {'type': 'date', 'value': req_date, 'page': 1, 'context': 'requisition'},
            {'type': 'unique_id', 'value': req_number, 'page': 1, 'context': 'requisition_number'}
        ])

        story.append(Paragraph(f"<b>Requisition Number:</b> {req_number}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Date:</b> {req_date}", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Patient demographics
        story.append(Paragraph("<b>PATIENT INFORMATION</b>", self.styles['Normal']))
        patient_info = [
            ['Patient Name:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['Date of Birth:', patient_data['birth_date'], 'Age/Sex:', f"{datetime.now().year - int(patient_data['birth_date'][:4])}/M"],
            ['SSN:', patient_data['ssn'], 'Phone:', patient_data['phone']],
            ['Address:', patient_data['address'], '', ''],
        ]

        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'ssn', 'value': patient_data['ssn'], 'page': 1},
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1},
            {'type': 'address', 'value': patient_data['address'], 'page': 1}
        ])

        patient_table = Table(patient_info, colWidths=[1.5*inch, 2.5*inch, 1*inch, 1.5*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('SPAN', (1, 3), (3, 3)),
        ]))
        story.append(patient_table)
        story.append(Spacer(1, 0.2 * inch))

        # Ordering provider
        ordering_md = f"Dr. {self.faker.last_name()}, MD"
        npi = f"NPI: {self.faker.random_number(digits=10, fix_len=True)}"
        provider_phone = self.faker.phone_number()

        phi_annotations.extend([
            {'type': 'name', 'value': ordering_md, 'page': 1, 'context': 'ordering_physician'},
            {'type': 'unique_id', 'value': npi, 'page': 1, 'context': 'npi'},
            {'type': 'phone', 'value': provider_phone, 'page': 1, 'context': 'provider_phone'}
        ])

        story.append(Paragraph("<b>ORDERING PHYSICIAN</b>", self.styles['Normal']))
        provider_info = [
            ['Name:', ordering_md, 'NPI:', npi],
            ['Phone:', provider_phone, 'Fax:', self.faker.phone_number()],
        ]

        fax = provider_info[1][3]
        phi_annotations.append({'type': 'phone', 'value': fax, 'page': 1, 'context': 'fax'})

        provider_table = Table(provider_info, colWidths=[1*inch, 2.5*inch, 1*inch, 2*inch])
        provider_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(provider_table)
        story.append(Spacer(1, 0.2 * inch))

        # Tests ordered
        story.append(Paragraph("<b>TESTS ORDERED</b>", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        if test_type == 'LABORATORY':
            tests = [
                '☑ Complete Blood Count (CBC) - 85025',
                '☑ Comprehensive Metabolic Panel (CMP) - 80053',
                '☑ Lipid Panel - 80061',
                '☐ Thyroid Function Tests',
                '☐ Hemoglobin A1C',
            ]
        elif test_type == 'RADIOLOGY':
            tests = [
                '☑ Chest X-Ray PA and Lateral',
                '☐ CT Chest with Contrast',
                '☐ MRI Brain without Contrast',
                '☐ Ultrasound Abdomen',
            ]
        else:
            tests = [
                '☑ Tissue Biopsy - Breast',
                '☐ Cytology - Fine Needle Aspiration',
                '☐ Frozen Section',
            ]

        for test in tests:
            story.append(Paragraph(test, self.styles['Normal']))

        story.append(Spacer(1, 0.2 * inch))

        # Clinical indication
        story.append(Paragraph("<b>CLINICAL INDICATION:</b>", self.styles['Normal']))
        indication = random.choice([
            "Annual physical examination, screening labs",
            "Follow-up for known hypertension and diabetes",
            "Chest pain, rule out pneumonia",
            "Abnormal mammogram, further evaluation needed"
        ])
        story.append(Paragraph(indication, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Urgency
        urgency = random.choice(['ROUTINE', 'STAT', 'URGENT'])
        story.append(Paragraph(f"<b>PRIORITY:</b> {urgency}", self.styles['Normal']))

        doc.build(story)
        return phi_annotations

    def create_therapy_note(self, patient_data, output_path):
        """Create PT/OT/Speech therapy note."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Header
        therapy_type = random.choice(['Physical Therapy', 'Occupational Therapy', 'Speech-Language Pathology'])
        facility = f"Massachusetts {therapy_type} Services"

        story.append(Paragraph(f"<b>{facility}</b>", self.styles['CenterBold']))
        story.append(Paragraph(f"{therapy_type.upper()} EVALUATION NOTE", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.append({'type': 'institution', 'value': facility, 'page': 1, 'context': 'therapy'})

        # Visit info
        visit_date = datetime.now().strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': visit_date, 'page': 1, 'context': 'visit'})

        # Patient info
        therapist = f"{self.faker.name()}, {random.choice(['PT, DPT', 'OTR/L', 'CCC-SLP', 'PT', 'OT'])}"
        phi_annotations.append({'type': 'name', 'value': therapist, 'page': 1, 'context': 'therapist'})

        patient_info = [
            ['Patient:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['DOB:', patient_data['birth_date'], 'Date:', visit_date],
            ['Therapist:', therapist, 'Visit #:', str(random.randint(1, 12))],
        ]

        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'}
        ])

        info_table = Table(patient_info, colWidths=[1*inch, 2.5*inch, 1*inch, 1.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # Diagnosis
        story.append(Paragraph("<b>DIAGNOSIS:</b>", self.styles['Normal']))
        diagnosis = random.choice([
            "Status post total knee arthroplasty, right",
            "Cerebrovascular accident with left hemiparesis",
            "Chronic low back pain with functional limitations",
            "Developmental apraxia of speech"
        ])
        story.append(Paragraph(diagnosis, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Subjective
        story.append(Paragraph("<b>SUBJECTIVE:</b>", self.styles['Normal']))
        subjective = f"Patient reports {random.choice(['improvement', 'minimal change', 'some difficulty'])} since last visit. {random.choice(['Pain level 3/10.', 'Pain level 5/10.', 'Denies pain.'])} Patient motivated and engaged in therapy."
        story.append(Paragraph(subjective, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Objective - measurements
        story.append(Paragraph("<b>OBJECTIVE:</b>", self.styles['Normal']))

        if therapy_type == 'Physical Therapy':
            measures = [
                ['Measurement', 'Left', 'Right'],
                ['ROM - Knee Flexion', '110°', '95°'],
                ['ROM - Knee Extension', '0°', '5° lag'],
                ['Strength - Quadriceps', '4/5', '3+/5'],
                ['Gait Speed', '', '0.8 m/s'],
            ]
        elif therapy_type == 'Occupational Therapy':
            measures = [
                ['Assessment', 'Score'],
                ['Grip Strength - Right', '18 kg'],
                ['Fine Motor Coordination', 'Mod impaired'],
                ['ADL Independence', '75%'],
            ]
        else:
            measures = [
                ['Assessment', 'Result'],
                ['Intelligibility', '65%'],
                ['Articulation Accuracy', 'Mild deficit'],
                ['Voice Quality', 'WNL'],
            ]

        measure_table = Table(measures)
        measure_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(measure_table)
        story.append(Spacer(1, 0.1 * inch))

        # Assessment
        story.append(Paragraph("<b>ASSESSMENT:</b>", self.styles['Normal']))
        assessment = f"Patient demonstrates {random.choice(['good', 'fair', 'excellent'])} progress toward functional goals. {random.choice(['Continue current treatment plan.', 'Progressing exercises as tolerated.', 'Will advance to next phase of treatment.'])}"
        story.append(Paragraph(assessment, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Plan
        story.append(Paragraph("<b>PLAN:</b>", self.styles['Normal']))
        plan = f"""
        - Continue {therapy_type.lower()} 2-3x per week
        - Home exercise program reviewed and updated
        - Next visit scheduled for {(datetime.now() + timedelta(days=random.randint(3, 7))).strftime('%Y-%m-%d')}
        - Anticipated discharge in {random.randint(2, 6)} weeks
        """

        next_visit = (datetime.now() + timedelta(days=random.randint(3, 7))).strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': next_visit, 'page': 1, 'context': 'next_visit'})

        story.append(Paragraph(plan, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Signature
        sig_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        phi_annotations.append({'type': 'date', 'value': sig_time.split()[0], 'page': 1, 'context': 'signature'})

        story.append(Paragraph(f"<b>Electronically signed:</b> {therapist}", self.styles['Normal']))
        story.append(Paragraph(f"Date/Time: {sig_time}", self.styles['Normal']))

        doc.build(story)
        return phi_annotations


def generate_sample_patient():
    """Generate a single sample patient."""
    faker = Faker()
    return {
        'name': faker.name(),
        'birth_date': faker.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d'),
        'ssn': faker.ssn(),
        'phone': faker.phone_number(),
        'email': faker.email(),
        'address': faker.address().replace('\n', ', '),
        'mrn': f"MRN-{faker.random_number(digits=8, fix_len=True)}",
        'insurance_id': f"INS-{faker.random_number(digits=10, fix_len=True)}",
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate final 5 document types')
    parser.add_argument('--samples-only', action='store_true', help='Generate one sample of each type only')
    parser.add_argument('--num-each', type=int, default=2500, help='Number of each document type to generate')
    parser.add_argument('--output-dir', type=str, default='./data/pdfs', help='Output directory')
    parser.add_argument('--annotations-dir', type=str, default='./data/annotations', help='Annotations directory')

    args = parser.parse_args()

    print("="*60)
    print("Generating Final 5 Document Types (to reach 20 total)")
    print("="*60)

    output_dir = Path(args.output_dir)
    annotations_dir = Path(args.annotations_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    annotations_dir.mkdir(parents=True, exist_ok=True)

    generator = FinalDocumentTypesGenerator()

    document_types = [
        ('consent_form', generator.create_consent_form),
        ('mar', generator.create_mar),
        ('billing_statement', generator.create_billing_statement),
        ('test_requisition', generator.create_test_requisition),
        ('therapy_note', generator.create_therapy_note),
    ]

    if args.samples_only:
        print("\nGenerating one sample of each document type for review...\n")
        num_docs = 1
    else:
        print(f"\nGenerating {args.num_each} of each document type...\n")
        num_docs = args.num_each

    total_generated = 0

    for doc_type, create_func in document_types:
        print(f"Generating {num_docs} {doc_type.replace('_', ' ').title()}(s)...")

        for i in range(num_docs):
            patient = generate_sample_patient()

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_name = f"{doc_type}_{i:04d}_{timestamp}.pdf"
            pdf_path = output_dir / pdf_name

            # Generate document
            phi_annotations = create_func(patient, pdf_path)

            # Save annotations
            annotation_file = annotations_dir / f"{pdf_name}.json"
            phi_categories = list(set(ann['type'] for ann in phi_annotations))

            with open(annotation_file, 'w') as f:
                json.dump({
                    'document': pdf_name,
                    'annotations': phi_annotations,
                    'timestamp': datetime.now().isoformat(),
                    'num_phi_items': len(phi_annotations),
                    'phi_categories': phi_categories
                }, f, indent=2)

            total_generated += 1

        print(f"  ✓ Generated {num_docs} {doc_type.replace('_', ' ')}(s)")

    print(f"\n{'='*60}")
    print(f"✓ Generation complete!")
    print(f"  Total documents: {total_generated}")
    print(f"  PDFs: {output_dir}")
    print(f"  Annotations: {annotations_dir}")
    print(f"{'='*60}")

    if args.samples_only:
        print("\nSample documents generated. Please review before generating full dataset.")
        print("To generate full dataset, run:")
        print(f"  python {sys.argv[0]} --num-each 2500")


if __name__ == "__main__":
    main()
