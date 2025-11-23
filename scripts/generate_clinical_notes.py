#!/usr/bin/env python3
"""
Generate realistic clinical notes (progress notes, SOAP notes, H&P, consultation notes).
These are the most common text-heavy medical documents.
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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


class ClinicalNotesGenerator:
    """Generate realistic clinical progress notes and SOAP notes."""

    def __init__(self):
        self.faker = Faker()
        Faker.seed(42)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Custom styles for clinical notes."""
        self.header_style = ParagraphStyle(
            'Header', parent=self.styles['Heading1'],
            fontSize=14, textColor=colors.HexColor('#003366'),
            alignment=TA_CENTER, spaceAfter=8, fontName='Helvetica-Bold'
        )

        self.facility_style = ParagraphStyle(
            'Facility', parent=self.styles['Normal'],
            fontSize=11, alignment=TA_CENTER, spaceAfter=4, fontName='Helvetica-Bold'
        )

        self.section_style = ParagraphStyle(
            'Section', parent=self.styles['Heading2'],
            fontSize=10, textColor=colors.HexColor('#004080'),
            spaceBefore=8, spaceAfter=4, fontName='Helvetica-Bold'
        )

        self.body_style = ParagraphStyle(
            'Body', parent=self.styles['Normal'],
            fontSize=9, leading=12, alignment=TA_JUSTIFY
        )

        self.small_style = ParagraphStyle(
            'Small', parent=self.styles['Normal'],
            fontSize=8, textColor=colors.grey
        )

    def create_progress_note(self, patient_data, output_path):
        """Create a realistic progress/clinical note."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                                topMargin=0.4*inch, bottomMargin=0.4*inch)
        story = []
        annotations = []

        # Facility header
        facility_name = f"{self.faker.company()} Medical Center"
        facility_address = self.faker.address().replace('\n', ', ')

        story.append(Paragraph(facility_name, self.facility_style))
        story.append(Paragraph(facility_address, self.small_style))
        story.append(Spacer(1, 0.15*inch))

        # Document header
        story.append(Paragraph("PROGRESS NOTE", self.header_style))
        story.append(Spacer(1, 0.1*inch))

        # Patient info bar
        note_date = datetime.now()
        visit_date = note_date - timedelta(hours=random.randint(1, 8))

        patient_bar = [
            ['Patient:', patient_data['name'], 'DOB:', patient_data['birth_date'], 'MRN:', patient_data['mrn']],
            ['Date of Visit:', visit_date.strftime('%m/%d/%Y %H:%M'), 'Provider:', f"Dr. {self.faker.last_name()}", 'Location:', f"{random.choice(['Clinic 1A', 'Clinic 2B', 'Suite 305', 'Room 412'])}"],
        ]

        annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': visit_date.strftime('%Y-%m-%d'), 'page': 1, 'context': 'visit'},
        ])

        info_table = Table(patient_bar, colWidths=[0.7*inch, 1.8*inch, 0.5*inch, 1.2*inch, 0.6*inch, 1.2*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTNAME', (4, 0), (4, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f0f0f0')),
            ('BACKGROUND', (4, 0), (4, -1), colors.HexColor('#f0f0f0')),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.15*inch))

        # Chief Complaint
        story.append(Paragraph("CHIEF COMPLAINT:", self.section_style))
        complaints = [
            "Follow-up for hypertension and diabetes",
            "Chest pain and shortness of breath",
            "Persistent cough for 2 weeks",
            "Annual physical examination",
            "Medication refills and lab review",
            "Joint pain and swelling",
            "Headaches and dizziness",
        ]
        cc_text = random.choice(complaints)
        story.append(Paragraph(cc_text, self.body_style))
        story.append(Spacer(1, 0.1*inch))

        # History of Present Illness
        story.append(Paragraph("HISTORY OF PRESENT ILLNESS:", self.section_style))

        age = datetime.now().year - datetime.strptime(patient_data['birth_date'], '%Y-%m-%d').year
        hpi_text = f"""
        {patient_data['name']} is a {age}-year-old patient who presents today for {cc_text.lower()}.
        Patient reports symptoms started approximately {random.randint(2, 14)} days ago.
        The patient denies fever, chills, or night sweats. No recent travel history.
        Last seen in this office on {(note_date - timedelta(days=random.randint(30, 180))).strftime('%m/%d/%Y')}.
        Patient has been compliant with current medications and reports no adverse effects.
        {random.choice([
            'Blood pressure at home has been well-controlled.',
            'Patient reports occasional palpitations.',
            'Some difficulty sleeping noted.',
            'Exercise tolerance remains good.',
            'No changes in weight reported.'
        ])}
        """
        story.append(Paragraph(hpi_text, self.body_style))
        story.append(Spacer(1, 0.1*inch))

        # Review of Systems
        story.append(Paragraph("REVIEW OF SYSTEMS:", self.section_style))
        ros_text = """
        <b>Constitutional:</b> No fever, no weight changes<br/>
        <b>HEENT:</b> No vision changes, no hearing loss, no sore throat<br/>
        <b>Cardiovascular:</b> No chest pain, no palpitations, no edema<br/>
        <b>Respiratory:</b> No shortness of breath, no wheezing, no cough<br/>
        <b>GI:</b> No nausea, no vomiting, no diarrhea, no constipation<br/>
        <b>GU:</b> No dysuria, no hematuria, no urgency<br/>
        <b>Musculoskeletal:</b> No joint pain, no muscle weakness<br/>
        <b>Neurological:</b> No headaches, no dizziness, no numbness<br/>
        <b>Psychiatric:</b> No depression, no anxiety
        """
        story.append(Paragraph(ros_text, self.body_style))
        story.append(Spacer(1, 0.1*inch))

        # Past Medical History
        story.append(Paragraph("PAST MEDICAL HISTORY:", self.section_style))
        pmh_conditions = patient_data.get('medications', [])
        pmh_text = "Hypertension, Type 2 Diabetes Mellitus, Hyperlipidemia, Osteoarthritis" if not pmh_conditions else ", ".join([m['name'].split()[0] for m in pmh_conditions[:4]])
        story.append(Paragraph(pmh_text, self.body_style))
        story.append(Spacer(1, 0.1*inch))

        # Medications
        story.append(Paragraph("CURRENT MEDICATIONS:", self.section_style))
        for i, med in enumerate(patient_data['medications'][:5], 1):
            med_text = f"{i}. {med['name']} - {med['dosage']}"
            story.append(Paragraph(med_text, self.body_style))
        story.append(Spacer(1, 0.1*inch))

        # Allergies
        story.append(Paragraph("ALLERGIES:", self.section_style))
        story.append(Paragraph(random.choice(['NKDA (No Known Drug Allergies)', 'Penicillin - rash', 'Sulfa - hives']), self.body_style))
        story.append(Spacer(1, 0.1*inch))

        # Social History
        story.append(Paragraph("SOCIAL HISTORY:", self.section_style))
        living_with = random.choice(['spouse', 'family', 'alone', 'partner'])
        smoking = random.choice(['Non-smoker.', 'Former smoker, quit 5 years ago.', 'Smoker, 1 PPD.'])
        alcohol = random.choice(['Denies alcohol use.', 'Occasional alcohol use.', 'Social drinker.'])
        occupation = random.choice(['Retired', 'Office worker', 'Teacher', 'Healthcare worker', 'Manual laborer'])

        social_text = f"""
        Patient lives with {living_with} at {patient_data['address']}.
        Contact phone: {patient_data['phone']}.
        {smoking}
        {alcohol}
        Occupation: {occupation}.
        """
        story.append(Paragraph(social_text, self.body_style))

        annotations.extend([
            {'type': 'address', 'value': patient_data['address'], 'page': 1, 'context': 'social_history'},
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1, 'context': 'contact'},
        ])
        story.append(Spacer(1, 0.1*inch))

        # Physical Examination
        story.append(Paragraph("PHYSICAL EXAMINATION:", self.section_style))
        vitals_data = [
            ['Vital Signs:', f"BP {random.randint(110, 140)}/{random.randint(70, 90)}", f"HR {random.randint(60, 90)}", f"RR {random.randint(12, 20)}", f"Temp {round(random.uniform(97.0, 99.5), 1)}°F", f"SpO2 {random.randint(95, 100)}%"],
        ]
        vitals_table = Table(vitals_data, colWidths=[1.2*inch, 1*inch, 0.8*inch, 0.8*inch, 1*inch, 0.8*inch])
        vitals_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(vitals_table)
        story.append(Spacer(1, 0.05*inch))

        pe_text = """
        <b>General:</b> Alert and oriented x3, no acute distress, well-appearing<br/>
        <b>HEENT:</b> Normocephalic, atraumatic. PERRLA. EOMI. TMs clear bilaterally.<br/>
        <b>Neck:</b> Supple, no JVD, no lymphadenopathy, no thyromegaly<br/>
        <b>Cardiovascular:</b> Regular rate and rhythm. No murmurs, rubs, or gallops. No edema.<br/>
        <b>Respiratory:</b> Clear to auscultation bilaterally. No wheezes, rales, or rhonchi.<br/>
        <b>Abdomen:</b> Soft, non-tender, non-distended. Normal bowel sounds. No organomegaly.<br/>
        <b>Extremities:</b> Full range of motion. No cyanosis, clubbing, or edema. Pulses 2+ bilaterally.<br/>
        <b>Neurological:</b> Cranial nerves II-XII intact. Strength 5/5 throughout. Sensation intact.
        """
        story.append(Paragraph(pe_text, self.body_style))
        story.append(Spacer(1, 0.1*inch))

        # Assessment and Plan
        story.append(Paragraph("ASSESSMENT AND PLAN:", self.section_style))

        assessment_text = f"""
        <b>1. {random.choice(['Hypertension', 'Type 2 Diabetes', 'Hyperlipidemia'])} - Stable</b><br/>
        &nbsp;&nbsp;&nbsp;- Continue current medications<br/>
        &nbsp;&nbsp;&nbsp;- Recheck labs in 3 months<br/>
        &nbsp;&nbsp;&nbsp;- Follow up in {random.randint(3, 6)} months<br/><br/>

        <b>2. {random.choice(['Preventive care', 'Health maintenance'])}</b><br/>
        &nbsp;&nbsp;&nbsp;- Mammogram due (schedule)<br/>
        &nbsp;&nbsp;&nbsp;- Colonoscopy at age 50<br/>
        &nbsp;&nbsp;&nbsp;- Annual flu vaccine recommended<br/><br/>

        <b>3. Patient education</b><br/>
        &nbsp;&nbsp;&nbsp;- Discussed lifestyle modifications<br/>
        &nbsp;&nbsp;&nbsp;- Importance of medication compliance<br/>
        &nbsp;&nbsp;&nbsp;- Diet and exercise counseling provided
        """
        story.append(Paragraph(assessment_text, self.body_style))
        story.append(Spacer(1, 0.15*inch))

        # Orders
        story.append(Paragraph("ORDERS:", self.section_style))
        orders_text = f"""
        • Labs: CBC, CMP, HbA1c, Lipid Panel - drawn today<br/>
        • Referral to {random.choice(['Cardiology', 'Endocrinology', 'Physical Therapy'])}<br/>
        • Prescription refills as noted above<br/>
        • Return to clinic in {random.randint(3, 6)} months or PRN
        """
        story.append(Paragraph(orders_text, self.body_style))
        story.append(Spacer(1, 0.2*inch))

        # Signature
        provider_name = f"Dr. {self.faker.name()}"
        signature_date = note_date.strftime('%m/%d/%Y %H:%M')

        annotations.extend([
            {'type': 'name', 'value': provider_name, 'page': 1, 'context': 'provider'},
            {'type': 'date', 'value': note_date.strftime('%Y-%m-%d'), 'page': 1, 'context': 'signature'},
        ])

        signature_text = f"""
        <b>Electronically signed by:</b><br/>
        {provider_name}, MD<br/>
        Internal Medicine<br/>
        NPI: {self.faker.random_number(digits=10, fix_len=True)}<br/>
        Date/Time: {signature_date}<br/>
        <br/>
        <i>This document has been electronically signed and is legally binding.</i>
        """
        story.append(Paragraph(signature_text, self.body_style))

        doc.build(story)
        return annotations

    def create_soap_note(self, patient_data, output_path):
        """Create a SOAP (Subjective, Objective, Assessment, Plan) note."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                                topMargin=0.4*inch, bottomMargin=0.4*inch)
        story = []
        annotations = []

        # Header
        facility_name = f"{self.faker.company()} Clinic"
        story.append(Paragraph(facility_name, self.facility_style))
        story.append(Paragraph("SOAP NOTE", self.header_style))
        story.append(Spacer(1, 0.1*inch))

        # Patient info
        note_date = datetime.now()

        patient_info = [
            ['Patient:', patient_data['name'], 'DOB:', patient_data['birth_date']],
            ['MRN:', patient_data['mrn'], 'Date:', note_date.strftime('%m/%d/%Y')],
        ]

        annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': note_date.strftime('%Y-%m-%d'), 'page': 1},
        ])

        info_table = Table(patient_info, colWidths=[0.8*inch, 2.5*inch, 0.6*inch, 1.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.15*inch))

        # SUBJECTIVE
        story.append(Paragraph("S - SUBJECTIVE:", self.section_style))
        subjective_text = f"""
        Patient presents with chief complaint of {random.choice(['follow-up visit', 'medication refill', 'new onset symptoms'])}.
        Reports feeling {random.choice(['well overall', 'somewhat fatigued', 'having good days and bad days'])}.
        {random.choice([
            'No new concerns since last visit.',
            'Some questions about current medications.',
            'Interested in discussing preventive care options.'
        ])}
        Pain level: {random.randint(0, 3)}/10.
        Sleep: {random.choice(['Good', 'Fair', 'Poor with occasional insomnia'])}.
        Appetite: {random.choice(['Normal', 'Increased', 'Decreased'])}.
        Contact info verified: {patient_data['phone']}, {patient_data['email']}.
        """
        story.append(Paragraph(subjective_text, self.body_style))

        annotations.extend([
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1},
            {'type': 'email', 'value': patient_data['email'], 'page': 1},
        ])
        story.append(Spacer(1, 0.1*inch))

        # OBJECTIVE
        story.append(Paragraph("O - OBJECTIVE:", self.section_style))
        objective_text = f"""
        <b>Vitals:</b> BP {random.randint(110, 135)}/{random.randint(70, 88)}, HR {random.randint(62, 88)},
        Temp {round(random.uniform(97.5, 98.8), 1)}°F, RR {random.randint(14, 18)}, SpO2 {random.randint(96, 100)}%<br/>
        <b>Weight:</b> {random.randint(120, 220)} lbs<br/>
        <b>Exam:</b> Alert, oriented. Heart RRR. Lungs CTAB. Abdomen soft, NT/ND. Extremities no edema.<br/>
        <b>Recent Labs ({(note_date - timedelta(days=random.randint(7, 30))).strftime('%m/%d/%Y')}):</b><br/>
        &nbsp;&nbsp;Glucose: {random.randint(85, 120)} mg/dL<br/>
        &nbsp;&nbsp;HbA1c: {round(random.uniform(5.0, 7.0), 1)}%<br/>
        &nbsp;&nbsp;LDL: {random.randint(70, 140)} mg/dL<br/>
        &nbsp;&nbsp;Cr: {round(random.uniform(0.8, 1.2), 1)} mg/dL
        """
        story.append(Paragraph(objective_text, self.body_style))
        story.append(Spacer(1, 0.1*inch))

        # ASSESSMENT
        story.append(Paragraph("A - ASSESSMENT:", self.section_style))
        assessment_text = f"""
        1. {random.choice(['Hypertension', 'Type 2 Diabetes Mellitus', 'Hyperlipidemia'])} - well-controlled<br/>
        2. {random.choice(['Preventive health maintenance', 'Chronic disease management'])}<br/>
        3. No acute issues at this time
        """
        story.append(Paragraph(assessment_text, self.body_style))
        story.append(Spacer(1, 0.1*inch))

        # PLAN
        story.append(Paragraph("P - PLAN:", self.section_style))
        plan_text = f"""
        • Continue current medication regimen<br/>
        • Recheck labs in {random.randint(3, 6)} months<br/>
        • Scheduled follow-up {(note_date + timedelta(days=random.randint(60, 180))).strftime('%m/%d/%Y')}<br/>
        • Patient education provided regarding {random.choice(['medication compliance', 'lifestyle modifications', 'diet and exercise'])}<br/>
        • Emergency contact: {random.choice([patient_data['phone'], self.faker.phone_number()])}<br/>
        • Patient questions answered, agrees with plan
        """
        story.append(Paragraph(plan_text, self.body_style))
        story.append(Spacer(1, 0.2*inch))

        # Signature
        provider_name = f"Dr. {self.faker.name()}"
        annotations.append({'type': 'name', 'value': provider_name, 'page': 1, 'context': 'provider'})

        signature = f"""
        <b>Provider:</b> {provider_name}, MD<br/>
        <b>Signed:</b> {note_date.strftime('%m/%d/%Y %H:%M')}<br/>
        <b>Cosigned:</b> {random.choice(['N/A', f'Dr. {self.faker.last_name()}, Attending Physician'])}
        """
        story.append(Paragraph(signature, self.body_style))

        doc.build(story)
        return annotations


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Generate realistic clinical notes')
    parser.add_argument('--num-patients', type=int, default=100, help='Number of patients')
    parser.add_argument('--num-documents', type=int, default=500, help='Number of notes')
    parser.add_argument('--output-dir', type=str, default='./data/pdfs', help='Output directory')
    parser.add_argument('--annotations-dir', type=str, default='./data/annotations', help='Annotations directory')

    args = parser.parse_args()

    print("="*70)
    print("Generating Realistic Clinical Notes")
    print("="*70)
    print(f"Patients: {args.num_patients}")
    print(f"Notes: {args.num_documents}")
    print()

    # Generate patient data
    faker = Faker()
    Faker.seed(43)  # Different seed for variety

    patients = []
    for i in range(args.num_patients):
        patient = {
            'name': faker.name(),
            'birth_date': faker.date_of_birth(minimum_age=18, maximum_age=85).strftime('%Y-%m-%d'),
            'ssn': faker.ssn(),
            'phone': faker.phone_number(),
            'email': faker.email(),
            'address': faker.address().replace('\n', ', '),
            'mrn': f"MRN-{faker.random_number(digits=8, fix_len=True)}",
            'medications': [
                {'name': random.choice([
                    'Lisinopril 10mg', 'Metformin 500mg', 'Atorvastatin 20mg',
                    'Amlodipine 5mg', 'Omeprazole 20mg', 'Levothyroxine 50mcg',
                    'Aspirin 81mg', 'Gabapentin 300mg'
                ]),
                 'dosage': f'{random.choice(["Take 1", "Take 2"])} {random.choice(["daily", "twice daily", "as needed"])}'}
                for _ in range(random.randint(2, 5))
            ],
        }
        patients.append(patient)

    print(f"✓ Generated {len(patients)} synthetic patients")

    # Create generator
    generator = ClinicalNotesGenerator()

    output_dir = Path(args.output_dir)
    annotations_dir = Path(args.annotations_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    annotations_dir.mkdir(parents=True, exist_ok=True)

    note_types = [
        ('progress_note', generator.create_progress_note),
        ('soap_note', generator.create_soap_note),
    ]

    print(f"\nGenerating {args.num_documents} clinical notes...")

    for i in range(args.num_documents):
        patient = random.choice(patients)
        note_type, create_func = random.choice(note_types)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_name = f"{note_type}_{i:04d}_{timestamp}.pdf"
        pdf_path = output_dir / pdf_name

        # Create note
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
            print(f"  Generated {i + 1}/{args.num_documents} notes...")

    print(f"\n✓ Generation complete!")
    print(f"\nGenerated files:")
    print(f"  {len(list(output_dir.glob('*_note_*.pdf')))} clinical notes")
    print(f"  Progress notes with full HPI, ROS, PE, A&P")
    print(f"  SOAP notes with narrative documentation")
    print("="*70)


if __name__ == "__main__":
    main()
