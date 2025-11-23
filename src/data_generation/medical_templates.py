"""
Medical document templates for generating diverse PHI-containing PDFs.
These templates simulate various real-world medical forms and documents.
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
import random

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, KeepTogether, Frame
)
from faker import Faker


class MedicalTemplates:
    """Collection of medical document templates."""

    def __init__(self):
        self.faker = Faker()
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Set up custom paragraph styles for medical documents."""
        # Header styles
        self.header_style = ParagraphStyle(
            'MedicalHeader',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#003366'),
            alignment=1,  # Center
            spaceAfter=12,
        )

        # Subheader styles
        self.subheader_style = ParagraphStyle(
            'MedicalSubheader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#004080'),
            spaceBefore=12,
            spaceAfter=6,
        )

        # Body text styles
        self.body_style = ParagraphStyle(
            'MedicalBody',
            parent=self.styles['Normal'],
            fontSize=10,
            leading=12,
        )

        # Small print styles
        self.small_style = ParagraphStyle(
            'SmallPrint',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
        )

    def discharge_summary_template(self, patient_info: Dict) -> List:
        """Generate a discharge summary template."""
        story = []
        phi_annotations = []

        # Hospital header
        hospital_name = f"{self.faker.company()} Medical Center"
        story.append(Paragraph(hospital_name, self.header_style))
        story.append(Paragraph("DISCHARGE SUMMARY", self.header_style))
        story.append(Spacer(1, 0.2 * inch))

        # Admission/Discharge info
        admission_date = datetime.now() - timedelta(days=random.randint(3, 14))
        discharge_date = datetime.now()

        admission_data = [
            ['Patient Name:', patient_info['name']],
            ['MRN:', patient_info['mrn']],
            ['DOB:', patient_info['birth_date']],
            ['Admission Date:', admission_date.strftime('%Y-%m-%d')],
            ['Discharge Date:', discharge_date.strftime('%Y-%m-%d')],
            ['Length of Stay:', f"{(discharge_date - admission_date).days} days"],
            ['Attending Physician:', f"Dr. {self.faker.name()}"],
        ]

        # Track PHI
        phi_annotations.extend([
            {'type': 'name', 'value': patient_info['name']},
            {'type': 'mrn', 'value': patient_info['mrn']},
            {'type': 'date', 'value': patient_info['birth_date']},
            {'type': 'date', 'value': admission_date.strftime('%Y-%m-%d')},
            {'type': 'date', 'value': discharge_date.strftime('%Y-%m-%d')},
        ])

        admission_table = Table(admission_data, colWidths=[2 * inch, 4 * inch])
        admission_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(admission_table)
        story.append(Spacer(1, 0.3 * inch))

        # Principal Diagnosis
        story.append(Paragraph("PRINCIPAL DIAGNOSIS", self.subheader_style))
        if patient_info.get('conditions'):
            diagnosis = patient_info['conditions'][0]['code']
        else:
            diagnosis = "Pneumonia, unspecified organism"
        story.append(Paragraph(diagnosis, self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # Hospital Course
        story.append(Paragraph("HOSPITAL COURSE", self.subheader_style))
        course_text = f"""
        The patient is a {self._calculate_age(patient_info['birth_date'])}-year-old
        who presented with {diagnosis.lower()}. The patient was admitted for
        observation and treatment. Initial vital signs were stable. Laboratory
        studies revealed no significant abnormalities. The patient responded well
        to treatment and showed steady improvement throughout the hospitalization.
        """
        story.append(Paragraph(course_text, self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # Medications on Discharge
        story.append(Paragraph("DISCHARGE MEDICATIONS", self.subheader_style))
        if patient_info.get('medications'):
            for med in patient_info['medications'][:5]:
                story.append(Paragraph(f"• {med['name']} - {med['dosage']}", self.body_style))
        else:
            meds = [
                "• Amoxicillin 500mg - Take 1 tablet by mouth three times daily",
                "• Acetaminophen 500mg - Take 1-2 tablets every 6 hours as needed",
                "• Omeprazole 20mg - Take 1 capsule daily",
            ]
            for med in meds:
                story.append(Paragraph(med, self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # Discharge Instructions
        story.append(Paragraph("DISCHARGE INSTRUCTIONS", self.subheader_style))
        instructions = """
        1. Take medications as prescribed
        2. Follow up with primary care physician in 1-2 weeks
        3. Return to emergency department if symptoms worsen
        4. Get plenty of rest and maintain hydration
        5. Avoid strenuous activities for 1 week
        """
        story.append(Paragraph(instructions, self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # Follow-up Appointments
        story.append(Paragraph("FOLLOW-UP APPOINTMENTS", self.subheader_style))
        followup_date = discharge_date + timedelta(days=random.randint(7, 14))
        followup_text = f"""
        Primary Care: Dr. {self.faker.name()}<br/>
        Date: {followup_date.strftime('%Y-%m-%d')}<br/>
        Time: {random.choice(['9:00 AM', '10:30 AM', '2:00 PM', '3:30 PM'])}<br/>
        Location: {self.faker.company()} Medical Group<br/>
        Phone: {self.faker.phone_number()}
        """
        story.append(Paragraph(followup_text, self.body_style))
        phi_annotations.append({'type': 'date', 'value': followup_date.strftime('%Y-%m-%d')})

        return story, phi_annotations

    def referral_letter_template(self, patient_info: Dict) -> Tuple[List, List]:
        """Generate a medical referral letter template."""
        story = []
        phi_annotations = []

        # Letter header
        referring_dr = f"Dr. {self.faker.name()}"
        referring_practice = f"{self.faker.company()} Family Medicine"
        referring_address = self.faker.address().replace('\n', ', ')
        referring_phone = self.faker.phone_number()
        referring_fax = self.faker.phone_number()

        story.append(Paragraph(referring_practice, self.header_style))
        story.append(Paragraph(referring_address, self.small_style))
        story.append(Paragraph(f"Tel: {referring_phone} | Fax: {referring_fax}", self.small_style))
        story.append(Spacer(1, 0.3 * inch))

        # Date
        letter_date = datetime.now()
        story.append(Paragraph(letter_date.strftime('%B %d, %Y'), self.body_style))
        story.append(Spacer(1, 0.2 * inch))
        phi_annotations.append({'type': 'date', 'value': letter_date.strftime('%Y-%m-%d')})

        # Recipient
        specialist_dr = f"Dr. {self.faker.name()}"
        specialist_practice = f"{self.faker.company()} Specialists"
        specialist_address = self.faker.address().replace('\n', ', ')

        recipient_text = f"""
        {specialist_dr}<br/>
        {specialist_practice}<br/>
        {specialist_address}
        """
        story.append(Paragraph(recipient_text, self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # RE: line
        story.append(Paragraph(f"<b>RE: {patient_info['name']} (DOB: {patient_info['birth_date']})</b>", self.body_style))
        story.append(Spacer(1, 0.2 * inch))
        phi_annotations.extend([
            {'type': 'name', 'value': patient_info['name']},
            {'type': 'date', 'value': patient_info['birth_date']},
        ])

        # Salutation
        story.append(Paragraph(f"Dear Dr. {specialist_dr.split()[-1]}:", self.body_style))
        story.append(Spacer(1, 0.1 * inch))

        # Referral reason
        referral_text = f"""
        I am referring {patient_info['name']}, a {self._calculate_age(patient_info['birth_date'])}-year-old
        patient of mine, for evaluation and management of
        {patient_info['conditions'][0]['code'] if patient_info.get('conditions') else 'chronic symptoms'}.
        """
        story.append(Paragraph(referral_text, self.body_style))
        story.append(Spacer(1, 0.1 * inch))

        # Medical history
        story.append(Paragraph("<b>Medical History:</b>", self.body_style))
        history_text = """
        The patient has been under my care since 2020. Past medical history is significant for
        hypertension, type 2 diabetes mellitus, and hyperlipidemia. The patient is compliant
        with medications and follow-up appointments.
        """
        story.append(Paragraph(history_text, self.body_style))
        story.append(Spacer(1, 0.1 * inch))

        # Current medications
        story.append(Paragraph("<b>Current Medications:</b>", self.body_style))
        if patient_info.get('medications'):
            for med in patient_info['medications'][:5]:
                story.append(Paragraph(f"• {med['name']}", self.body_style))
        story.append(Spacer(1, 0.1 * inch))

        # Allergies
        story.append(Paragraph("<b>Allergies:</b>", self.body_style))
        if patient_info.get('allergies'):
            for allergy in patient_info['allergies']:
                story.append(Paragraph(f"• {allergy['substance']} ({allergy['severity']})", self.body_style))
        else:
            story.append(Paragraph("No known drug allergies", self.body_style))
        story.append(Spacer(1, 0.1 * inch))

        # Closing
        closing_text = """
        I would appreciate your evaluation and recommendations for this patient.
        Please send your consultation report to my office at your earliest convenience.
        <br/><br/>
        Thank you for seeing this patient.
        <br/><br/>
        Sincerely,<br/><br/><br/>
        """
        story.append(Paragraph(closing_text, self.body_style))

        story.append(Paragraph(f"{referring_dr}, MD", self.body_style))
        story.append(Paragraph(f"License #: {self.faker.random_number(digits=8, fix_len=True)}", self.small_style))

        return story, phi_annotations

    def radiology_report_template(self, patient_info: Dict) -> Tuple[List, List]:
        """Generate a radiology report template."""
        story = []
        phi_annotations = []

        # Header
        story.append(Paragraph("RADIOLOGY REPORT", self.header_style))
        story.append(Spacer(1, 0.2 * inch))

        # Report details
        exam_date = datetime.now() - timedelta(days=random.randint(0, 3))
        accession = f"RAD-{self.faker.random_number(digits=10, fix_len=True)}"

        report_data = [
            ['Patient Name:', patient_info['name']],
            ['MRN:', patient_info['mrn']],
            ['DOB:', patient_info['birth_date']],
            ['Exam Date:', exam_date.strftime('%Y-%m-%d %H:%M')],
            ['Accession #:', accession],
            ['Exam Type:', random.choice(['Chest X-Ray PA/LAT', 'CT Abdomen w/contrast', 'MRI Brain w/o contrast'])],
            ['Ordering Physician:', f"Dr. {self.faker.name()}"],
            ['Radiologist:', f"Dr. {self.faker.name()}"],
        ]

        # Track PHI
        phi_annotations.extend([
            {'type': 'name', 'value': patient_info['name']},
            {'type': 'mrn', 'value': patient_info['mrn']},
            {'type': 'date', 'value': patient_info['birth_date']},
            {'type': 'date', 'value': exam_date.strftime('%Y-%m-%d')},
        ])

        report_table = Table(report_data, colWidths=[2 * inch, 4 * inch])
        report_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(report_table)
        story.append(Spacer(1, 0.3 * inch))

        # Clinical History
        story.append(Paragraph("CLINICAL HISTORY", self.subheader_style))
        history = f"{self._calculate_age(patient_info['birth_date'])}-year-old with chest pain and shortness of breath."
        story.append(Paragraph(history, self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # Technique
        story.append(Paragraph("TECHNIQUE", self.subheader_style))
        technique = "PA and lateral views of the chest were obtained."
        story.append(Paragraph(technique, self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # Findings
        story.append(Paragraph("FINDINGS", self.subheader_style))
        findings = """
        Lungs: The lungs are clear bilaterally. No focal consolidation, pleural effusion, or pneumothorax.
        <br/><br/>
        Heart: Heart size is normal. Mediastinal contours are unremarkable.
        <br/><br/>
        Bones: No acute osseous abnormality.
        <br/><br/>
        Soft tissues: Unremarkable.
        """
        story.append(Paragraph(findings, self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # Impression
        story.append(Paragraph("IMPRESSION", self.subheader_style))
        impression = "No acute cardiopulmonary process."
        story.append(Paragraph(impression, self.body_style))

        return story, phi_annotations

    def consultation_note_template(self, patient_info: Dict) -> Tuple[List, List]:
        """Generate a medical consultation note template."""
        story = []
        phi_annotations = []

        # Header
        story.append(Paragraph("CONSULTATION NOTE", self.header_style))
        consultant_name = f"Dr. {self.faker.name()}"
        specialty = random.choice(['Cardiology', 'Pulmonology', 'Gastroenterology', 'Neurology'])
        story.append(Paragraph(f"{consultant_name}, MD - {specialty}", self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # Consultation details
        consult_date = datetime.now()
        consult_data = [
            ['Patient:', patient_info['name']],
            ['MRN:', patient_info['mrn']],
            ['DOB:', patient_info['birth_date']],
            ['Consultation Date:', consult_date.strftime('%Y-%m-%d')],
            ['Referring Physician:', f"Dr. {self.faker.name()}"],
            ['Reason for Consult:', 'Evaluation and management recommendations'],
        ]

        phi_annotations.extend([
            {'type': 'name', 'value': patient_info['name']},
            {'type': 'mrn', 'value': patient_info['mrn']},
            {'type': 'date', 'value': patient_info['birth_date']},
            {'type': 'date', 'value': consult_date.strftime('%Y-%m-%d')},
        ])

        consult_table = Table(consult_data, colWidths=[2 * inch, 4 * inch])
        consult_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(consult_table)
        story.append(Spacer(1, 0.3 * inch))

        # Chief Complaint
        story.append(Paragraph("CHIEF COMPLAINT", self.subheader_style))
        story.append(Paragraph("Chest pain and palpitations", self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # History of Present Illness
        story.append(Paragraph("HISTORY OF PRESENT ILLNESS", self.subheader_style))
        hpi_text = f"""
        {patient_info['name']} is a {self._calculate_age(patient_info['birth_date'])}-year-old
        who presents with a 2-week history of intermittent chest pain and palpitations.
        The chest pain is described as sharp, non-radiating, and lasting 5-10 minutes.
        It is not associated with exertion. The patient denies shortness of breath,
        dizziness, or syncope.
        """
        story.append(Paragraph(hpi_text, self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # Physical Examination
        story.append(Paragraph("PHYSICAL EXAMINATION", self.subheader_style))
        pe_text = """
        Vital Signs: BP 128/78, HR 72 regular, RR 16, Temp 98.6°F, SpO2 98% on room air<br/>
        General: Alert and oriented, no acute distress<br/>
        Cardiovascular: Regular rate and rhythm, no murmurs/rubs/gallops<br/>
        Pulmonary: Clear to auscultation bilaterally<br/>
        Abdomen: Soft, non-tender, non-distended<br/>
        Extremities: No edema, pulses 2+ bilaterally
        """
        story.append(Paragraph(pe_text, self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # Assessment and Plan
        story.append(Paragraph("ASSESSMENT AND PLAN", self.subheader_style))
        ap_text = """
        1. Chest pain - likely non-cardiac given characteristics. Will obtain EKG and troponin.
        2. Palpitations - consider Holter monitor for further evaluation.
        3. Continue current medications.
        4. Follow up in 2 weeks with test results.
        """
        story.append(Paragraph(ap_text, self.body_style))

        return story, phi_annotations

    def _calculate_age(self, birth_date_str: str) -> int:
        """Calculate age from birth date string."""
        try:
            birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d')
            today = datetime.now()
            age = today.year - birth_date.year
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1
            return age
        except:
            return random.randint(25, 85)

    def emergency_room_note_template(self, patient_info: Dict) -> Tuple[List, List]:
        """Generate an emergency room visit note."""
        story = []
        phi_annotations = []

        # Header
        story.append(Paragraph("EMERGENCY DEPARTMENT NOTE", self.header_style))
        story.append(Spacer(1, 0.2 * inch))

        # Visit information
        visit_date = datetime.now()
        arrival_time = (visit_date - timedelta(hours=random.randint(1, 6))).strftime('%H:%M')

        visit_data = [
            ['Patient Name:', patient_info['name']],
            ['MRN:', patient_info['mrn']],
            ['DOB/Age:', f"{patient_info['birth_date']} ({self._calculate_age(patient_info['birth_date'])} yo)"],
            ['Visit Date:', visit_date.strftime('%Y-%m-%d')],
            ['Arrival Time:', arrival_time],
            ['Triage Level:', random.choice(['1 - Resuscitation', '2 - Emergent', '3 - Urgent', '4 - Less Urgent'])],
        ]

        phi_annotations.extend([
            {'type': 'name', 'value': patient_info['name']},
            {'type': 'mrn', 'value': patient_info['mrn']},
            {'type': 'date', 'value': patient_info['birth_date']},
            {'type': 'date', 'value': visit_date.strftime('%Y-%m-%d')},
        ])

        visit_table = Table(visit_data, colWidths=[2 * inch, 4 * inch])
        visit_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(visit_table)
        story.append(Spacer(1, 0.3 * inch))

        # Chief Complaint
        story.append(Paragraph("CHIEF COMPLAINT", self.subheader_style))
        chief_complaints = [
            "Chest pain x 2 hours",
            "Shortness of breath",
            "Abdominal pain",
            "Head injury after fall",
            "Fever and cough",
        ]
        story.append(Paragraph(random.choice(chief_complaints), self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # Vital Signs
        story.append(Paragraph("VITAL SIGNS", self.subheader_style))
        vitals = f"""
        Temperature: {round(random.uniform(97.0, 101.0), 1)}°F<br/>
        Blood Pressure: {random.randint(110, 140)}/{random.randint(60, 90)} mmHg<br/>
        Heart Rate: {random.randint(60, 110)} bpm<br/>
        Respiratory Rate: {random.randint(12, 24)} breaths/min<br/>
        Oxygen Saturation: {random.randint(94, 100)}% on room air<br/>
        Pain Score: {random.randint(0, 10)}/10
        """
        story.append(Paragraph(vitals, self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        # Emergency Contact
        story.append(Paragraph("EMERGENCY CONTACT", self.subheader_style))
        contact_name = self.faker.name()
        contact_phone = self.faker.phone_number()
        contact_text = f"""
        Name: {contact_name}<br/>
        Relationship: {random.choice(['Spouse', 'Parent', 'Child', 'Sibling'])}<br/>
        Phone: {contact_phone}
        """
        story.append(Paragraph(contact_text, self.body_style))
        phi_annotations.extend([
            {'type': 'name', 'value': contact_name},
            {'type': 'phone', 'value': contact_phone},
        ])

        return story, phi_annotations


def create_medical_form_templates():
    """Create and save various medical form templates as JSON configs."""
    import json

    templates = {
        "prescription": {
            "name": "Prescription Form",
            "fields": [
                {"name": "patient_name", "type": "text", "phi": True, "category": "name"},
                {"name": "dob", "type": "date", "phi": True, "category": "date"},
                {"name": "mrn", "type": "text", "phi": True, "category": "mrn"},
                {"name": "address", "type": "text", "phi": True, "category": "address"},
                {"name": "phone", "type": "text", "phi": True, "category": "phone"},
                {"name": "medication", "type": "text", "phi": False},
                {"name": "dosage", "type": "text", "phi": False},
                {"name": "prescriber", "type": "text", "phi": True, "category": "name"},
                {"name": "dea_number", "type": "text", "phi": True, "category": "license"},
                {"name": "date_prescribed", "type": "date", "phi": True, "category": "date"},
            ]
        },
        "lab_report": {
            "name": "Laboratory Report",
            "fields": [
                {"name": "patient_name", "type": "text", "phi": True, "category": "name"},
                {"name": "dob", "type": "date", "phi": True, "category": "date"},
                {"name": "ssn", "type": "text", "phi": True, "category": "ssn"},
                {"name": "mrn", "type": "text", "phi": True, "category": "mrn"},
                {"name": "collection_date", "type": "datetime", "phi": True, "category": "date"},
                {"name": "specimen_id", "type": "text", "phi": False},
                {"name": "test_results", "type": "table", "phi": False},
                {"name": "pathologist", "type": "text", "phi": True, "category": "name"},
            ]
        },
        "insurance_claim": {
            "name": "Insurance Claim Form",
            "fields": [
                {"name": "patient_name", "type": "text", "phi": True, "category": "name"},
                {"name": "dob", "type": "date", "phi": True, "category": "date"},
                {"name": "ssn", "type": "text", "phi": True, "category": "ssn"},
                {"name": "address", "type": "text", "phi": True, "category": "address"},
                {"name": "phone", "type": "text", "phi": True, "category": "phone"},
                {"name": "email", "type": "text", "phi": True, "category": "email"},
                {"name": "policy_number", "type": "text", "phi": True, "category": "insurance_id"},
                {"name": "group_number", "type": "text", "phi": False},
                {"name": "provider_name", "type": "text", "phi": True, "category": "name"},
                {"name": "provider_npi", "type": "text", "phi": True, "category": "unique_id"},
                {"name": "service_date", "type": "date", "phi": True, "category": "date"},
                {"name": "diagnosis_codes", "type": "list", "phi": False},
                {"name": "procedure_codes", "type": "list", "phi": False},
            ]
        },
        "discharge_summary": {
            "name": "Discharge Summary",
            "fields": [
                {"name": "patient_name", "type": "text", "phi": True, "category": "name"},
                {"name": "mrn", "type": "text", "phi": True, "category": "mrn"},
                {"name": "dob", "type": "date", "phi": True, "category": "date"},
                {"name": "admission_date", "type": "date", "phi": True, "category": "date"},
                {"name": "discharge_date", "type": "date", "phi": True, "category": "date"},
                {"name": "attending_physician", "type": "text", "phi": True, "category": "name"},
                {"name": "diagnosis", "type": "text", "phi": False},
                {"name": "procedures", "type": "list", "phi": False},
                {"name": "medications", "type": "list", "phi": False},
                {"name": "followup_date", "type": "date", "phi": True, "category": "date"},
                {"name": "followup_provider", "type": "text", "phi": True, "category": "name"},
            ]
        },
        "patient_registration": {
            "name": "Patient Registration Form",
            "fields": [
                {"name": "full_name", "type": "text", "phi": True, "category": "name"},
                {"name": "dob", "type": "date", "phi": True, "category": "date"},
                {"name": "ssn", "type": "text", "phi": True, "category": "ssn"},
                {"name": "drivers_license", "type": "text", "phi": True, "category": "license"},
                {"name": "address", "type": "text", "phi": True, "category": "address"},
                {"name": "city", "type": "text", "phi": True, "category": "geo_small"},
                {"name": "state", "type": "text", "phi": False},
                {"name": "zip", "type": "text", "phi": True, "category": "geo_small"},
                {"name": "phone", "type": "text", "phi": True, "category": "phone"},
                {"name": "email", "type": "text", "phi": True, "category": "email"},
                {"name": "emergency_contact", "type": "text", "phi": True, "category": "name"},
                {"name": "emergency_phone", "type": "text", "phi": True, "category": "phone"},
                {"name": "insurance_provider", "type": "text", "phi": False},
                {"name": "policy_number", "type": "text", "phi": True, "category": "insurance_id"},
                {"name": "group_number", "type": "text", "phi": False},
            ]
        }
    }

    # Save templates to JSON file
    output_path = "config/medical_templates.json"
    with open(output_path, 'w') as f:
        json.dump(templates, f, indent=2)

    print(f"Medical form templates saved to {output_path}")
    return templates


if __name__ == "__main__":
    # Create and save template configurations
    templates = create_medical_form_templates()
    print(f"Created {len(templates)} medical form templates")