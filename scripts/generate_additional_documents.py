#!/usr/bin/env python3
"""
Generate additional medical document types with realistic formatting.
Creates: discharge summaries, radiology reports, operative reports, pathology reports,
ED notes, consultation notes, H&P, referral letters, registration forms, immunization records.
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
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class AdditionalDocumentsGenerator:
    """Generate additional realistic medical documents."""

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
            name='SmallRight',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT,
            fontSize=8
        ))

    def create_discharge_summary(self, patient_data, output_path):
        """Create hospital discharge summary."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Hospital header
        facility_name = random.choice([
            "Massachusetts General Hospital",
            "University Medical Center",
            "St. Mary's Regional Hospital",
            "Metropolitan Healthcare System"
        ])

        story.append(Paragraph(f"<b>{facility_name}</b>", self.styles['CenterBold']))
        story.append(Paragraph("DISCHARGE SUMMARY", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        # Admission/Discharge dates
        admission_date = self.faker.date_between(start_date='-30d', end_date='-7d')
        discharge_date = admission_date + timedelta(days=random.randint(3, 14))
        discharge_date_str = discharge_date.strftime('%Y-%m-%d')
        admission_date_str = admission_date.strftime('%Y-%m-%d')

        phi_annotations.extend([
            {'type': 'institution', 'value': facility_name, 'page': 1, 'context': 'hospital'},
            {'type': 'date', 'value': admission_date_str, 'page': 1, 'context': 'admission'},
            {'type': 'date', 'value': discharge_date_str, 'page': 1, 'context': 'discharge'}
        ])

        # Patient demographics
        patient_info = [
            ['Patient Name:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['Date of Birth:', patient_data['birth_date'], 'Age:', str(datetime.now().year - int(patient_data['birth_date'][:4]))],
            ['Admission Date:', admission_date_str, 'Discharge Date:', discharge_date_str],
            ['Attending Physician:', f"Dr. {self.faker.last_name()}, MD", 'Service:', random.choice(['Internal Medicine', 'Surgery', 'Cardiology', 'Neurology'])],
        ]

        attending_name = patient_info[3][1]
        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'name', 'value': attending_name, 'page': 1, 'context': 'attending'}
        ])

        info_table = Table(patient_info, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # Chief Complaint
        story.append(Paragraph("<b>CHIEF COMPLAINT:</b>", self.styles['Normal']))
        chief_complaint = random.choice([
            "Chest pain and shortness of breath",
            "Abdominal pain with nausea and vomiting",
            "Altered mental status",
            "Fever and productive cough",
            "Syncope with fall"
        ])
        story.append(Paragraph(chief_complaint, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Hospital Course
        story.append(Paragraph("<b>HOSPITAL COURSE:</b>", self.styles['Normal']))
        course_text = f"""
        The patient was admitted to {facility_name} on {admission_date_str} with the above chief complaint.
        Initial evaluation in the Emergency Department revealed vital signs: BP 142/88, HR 92, RR 18, Temp 98.6°F, SpO2 96% on room air.
        Laboratory studies showed WBC 11.2, Hemoglobin 13.5, Platelets 245, BUN 18, Creatinine 1.1, and Glucose 105.
        <br/><br/>
        The patient was started on appropriate medical management and monitored closely. Imaging studies including
        {random.choice(['chest X-ray', 'CT scan', 'MRI', 'ultrasound'])} were obtained. Consultations were placed to
        {random.choice(['Cardiology', 'Gastroenterology', 'Neurology', 'Pulmonology', 'Infectious Disease'])}.
        <br/><br/>
        The patient's condition improved with treatment and they were deemed stable for discharge on {discharge_date_str}.
        """
        story.append(Paragraph(course_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Discharge Diagnoses
        story.append(Paragraph("<b>DISCHARGE DIAGNOSES:</b>", self.styles['Normal']))
        diagnoses = [
            f"1. {random.choice(['Acute myocardial infarction', 'Community-acquired pneumonia', 'Acute kidney injury', 'Congestive heart failure exacerbation', 'Sepsis'])}",
            f"2. {random.choice(['Hypertension', 'Diabetes mellitus type 2', 'Hyperlipidemia', 'Chronic kidney disease', 'Atrial fibrillation'])}",
            f"3. {random.choice(['Anemia', 'COPD', 'Coronary artery disease', 'Gastroesophageal reflux disease', 'Osteoarthritis'])}"
        ]
        for dx in diagnoses:
            story.append(Paragraph(dx, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Discharge Medications
        story.append(Paragraph("<b>DISCHARGE MEDICATIONS:</b>", self.styles['Normal']))
        medications = [
            "1. Lisinopril 10 mg PO daily",
            "2. Metoprolol tartrate 25 mg PO BID",
            "3. Atorvastatin 40 mg PO QHS",
            "4. Aspirin 81 mg PO daily",
            "5. Metformin 500 mg PO BID"
        ]
        for med in medications:
            story.append(Paragraph(med, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Follow-up
        followup_date = discharge_date + timedelta(days=random.randint(7, 21))
        followup_date_str = followup_date.strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': followup_date_str, 'page': 1, 'context': 'followup'})

        story.append(Paragraph("<b>FOLLOW-UP:</b>", self.styles['Normal']))
        followup_text = f"Follow-up appointment scheduled with Dr. {self.faker.last_name()} on {followup_date_str}. Patient instructed to call {patient_data['phone']} to confirm appointment."
        story.append(Paragraph(followup_text, self.styles['Normal']))

        followup_provider = f"Dr. {self.faker.last_name()}"
        phi_annotations.extend([
            {'type': 'name', 'value': followup_provider, 'page': 1, 'context': 'followup_provider'},
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1}
        ])

        # Signature
        story.append(Spacer(1, 0.3 * inch))
        sig_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        phi_annotations.append({'type': 'date', 'value': sig_time.split()[0], 'page': 1, 'context': 'signature'})

        story.append(Paragraph(f"<b>Electronically signed by:</b> {attending_name}", self.styles['Normal']))
        story.append(Paragraph(f"Date/Time: {sig_time}", self.styles['Normal']))

        doc.build(story)
        return phi_annotations

    def create_radiology_report(self, patient_data, output_path):
        """Create radiology imaging report."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Header
        facility = random.choice([
            "Advanced Imaging Center",
            "Radiology Associates of Massachusetts",
            "University Hospital Imaging Department"
        ])

        story.append(Paragraph(f"<b>{facility}</b>", self.styles['CenterBold']))
        story.append(Paragraph("RADIOLOGY REPORT", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.append({'type': 'institution', 'value': facility, 'page': 1, 'context': 'imaging_center'})

        # Exam info
        exam_date = datetime.now().strftime('%Y-%m-%d')
        exam_time = datetime.now().strftime('%H:%M:%S')

        exam_type = random.choice([
            'CT Chest with Contrast',
            'MRI Brain without Contrast',
            'X-Ray Chest PA and Lateral',
            'Ultrasound Abdomen Complete',
            'CT Abdomen/Pelvis with IV Contrast'
        ])

        exam_info = [
            ['Patient Name:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['Date of Birth:', patient_data['birth_date'], 'Age:', str(datetime.now().year - int(patient_data['birth_date'][:4]))],
            ['Exam Date:', exam_date, 'Exam Time:', exam_time],
            ['Exam Type:', exam_type, 'Accession #:', f"RAD{self.faker.random_number(digits=8, fix_len=True)}"],
        ]

        accession = exam_info[3][3]
        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'date', 'value': exam_date, 'page': 1, 'context': 'exam'},
            {'type': 'unique_id', 'value': accession, 'page': 1, 'context': 'accession'}
        ])

        info_table = Table(exam_info, colWidths=[1.5*inch, 2*inch, 1.2*inch, 1.8*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # Ordering physician
        ordering_physician = f"Dr. {self.faker.last_name()}, MD"
        phi_annotations.append({'type': 'name', 'value': ordering_physician, 'page': 1, 'context': 'ordering_physician'})

        story.append(Paragraph(f"<b>Ordering Physician:</b> {ordering_physician}", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Clinical indication
        story.append(Paragraph("<b>CLINICAL INDICATION:</b>", self.styles['Normal']))
        indication = random.choice([
            "Chest pain, rule out pulmonary embolism",
            "Headache and vision changes, evaluate for intracranial pathology",
            "Shortness of breath, evaluate for pneumonia",
            "Abdominal pain, right upper quadrant",
            "Follow-up of known mass"
        ])
        story.append(Paragraph(indication, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Technique
        story.append(Paragraph("<b>TECHNIQUE:</b>", self.styles['Normal']))
        technique_text = f"{exam_type} was performed according to standard protocol. Total radiation dose (DLP): {random.randint(200, 800)} mGy-cm."
        story.append(Paragraph(technique_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Comparison
        comparison_date = (datetime.now() - timedelta(days=random.randint(90, 365))).strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': comparison_date, 'page': 1, 'context': 'comparison'})

        story.append(Paragraph("<b>COMPARISON:</b>", self.styles['Normal']))
        story.append(Paragraph(f"Prior study dated {comparison_date} available for comparison.", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Findings
        story.append(Paragraph("<b>FINDINGS:</b>", self.styles['Normal']))
        findings_text = """
        <b>Lungs:</b> The lungs are clear without focal consolidation, pleural effusion, or pneumothorax.
        No suspicious pulmonary nodules identified.
        <br/><br/>
        <b>Heart:</b> Heart size is normal. No pericardial effusion.
        <br/><br/>
        <b>Mediastinum:</b> Mediastinal and hilar contours are unremarkable. No pathologically enlarged lymph nodes.
        <br/><br/>
        <b>Bones:</b> Visualized osseous structures demonstrate no acute abnormality.
        """
        story.append(Paragraph(findings_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Impression
        story.append(Paragraph("<b>IMPRESSION:</b>", self.styles['Normal']))
        impression = random.choice([
            "1. No acute cardiopulmonary abnormality.\n2. Comparison shows interval improvement.",
            "1. Small pleural effusion, likely reactive.\n2. Recommend clinical correlation and follow-up.",
            "1. Findings consistent with mild interstitial changes.\n2. Suggest follow-up imaging in 3 months.",
            "1. Normal study.\n2. No significant change from prior examination."
        ])
        story.append(Paragraph(impression.replace('\n', '<br/>'), self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Radiologist signature
        radiologist = f"Dr. {self.faker.last_name()}, MD"
        radiologist_npi = f"NPI: {self.faker.random_number(digits=10, fix_len=True)}"

        phi_annotations.extend([
            {'type': 'name', 'value': radiologist, 'page': 1, 'context': 'radiologist'},
            {'type': 'unique_id', 'value': radiologist_npi, 'page': 1, 'context': 'npi'}
        ])

        sig_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        phi_annotations.append({'type': 'date', 'value': sig_time.split()[0], 'page': 1, 'context': 'signature'})

        story.append(Paragraph(f"<b>Interpreted by:</b> {radiologist}", self.styles['Normal']))
        story.append(Paragraph(radiologist_npi, self.styles['Normal']))
        story.append(Paragraph(f"<b>Date/Time:</b> {sig_time}", self.styles['Normal']))

        doc.build(story)
        return phi_annotations

    def create_operative_report(self, patient_data, output_path):
        """Create surgical operative report."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Header
        hospital = random.choice([
            "University Surgical Center",
            "Massachusetts General Hospital - OR Suite",
            "St. Mary's Regional Hospital - Surgery Department"
        ])

        story.append(Paragraph(f"<b>{hospital}</b>", self.styles['CenterBold']))
        story.append(Paragraph("OPERATIVE REPORT", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.append({'type': 'institution', 'value': hospital, 'page': 1, 'context': 'hospital'})

        # Surgery date/time
        surgery_date = self.faker.date_between(start_date='-30d', end_date='today')
        surgery_date_str = surgery_date.strftime('%Y-%m-%d')
        start_time = f"{random.randint(7, 15):02d}:{random.randint(0, 59):02d}"
        end_time_hour = int(start_time.split(':')[0]) + random.randint(2, 5)
        end_time = f"{end_time_hour:02d}:{random.randint(0, 59):02d}"

        phi_annotations.extend([
            {'type': 'date', 'value': surgery_date_str, 'page': 1, 'context': 'surgery'}
        ])

        # Patient info
        patient_info = [
            ['Patient Name:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['Date of Birth:', patient_data['birth_date'], 'Age/Sex:', f"{datetime.now().year - int(patient_data['birth_date'][:4])}/M"],
            ['Date of Surgery:', surgery_date_str, 'Time:', f"{start_time} - {end_time}"],
        ]

        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'}
        ])

        info_table = Table(patient_info, colWidths=[1.5*inch, 2.5*inch, 1*inch, 1.5*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # Surgical team
        surgeon = f"Dr. {self.faker.last_name()}, MD"
        assistant = f"Dr. {self.faker.last_name()}, MD"
        anesthesiologist = f"Dr. {self.faker.last_name()}, MD"
        scrub_nurse = self.faker.name()

        phi_annotations.extend([
            {'type': 'name', 'value': surgeon, 'page': 1, 'context': 'surgeon'},
            {'type': 'name', 'value': assistant, 'page': 1, 'context': 'assistant'},
            {'type': 'name', 'value': anesthesiologist, 'page': 1, 'context': 'anesthesiologist'},
            {'type': 'name', 'value': scrub_nurse, 'page': 1, 'context': 'nurse'}
        ])

        story.append(Paragraph(f"<b>Surgeon:</b> {surgeon}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Assistant:</b> {assistant}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Anesthesiologist:</b> {anesthesiologist}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Scrub Nurse:</b> {scrub_nurse}", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Procedure
        procedure = random.choice([
            "Laparoscopic Cholecystectomy",
            "Open Appendectomy",
            "Total Knee Arthroplasty, Right",
            "Laparoscopic Inguinal Hernia Repair",
            "Coronary Artery Bypass Graft x3"
        ])

        story.append(Paragraph(f"<b>PROCEDURE PERFORMED:</b> {procedure}", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Pre/Post-op diagnosis
        diagnosis = random.choice([
            "Acute cholecystitis",
            "Acute appendicitis",
            "Severe osteoarthritis right knee",
            "Right inguinal hernia",
            "Triple vessel coronary artery disease"
        ])

        story.append(Paragraph(f"<b>PREOPERATIVE DIAGNOSIS:</b> {diagnosis}", self.styles['Normal']))
        story.append(Paragraph(f"<b>POSTOPERATIVE DIAGNOSIS:</b> Same", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Anesthesia
        anesthesia_type = random.choice(["General endotracheal", "Spinal", "General with LMA", "Epidural"])
        story.append(Paragraph(f"<b>ANESTHESIA:</b> {anesthesia_type}", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Indications
        story.append(Paragraph("<b>INDICATIONS:</b>", self.styles['Normal']))
        indications_text = f"This is a {datetime.now().year - int(patient_data['birth_date'][:4])}-year-old patient with {diagnosis}. "
        indications_text += "After discussion of risks, benefits, and alternatives, the patient provided informed consent for the procedure."
        story.append(Paragraph(indications_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Procedure description
        story.append(Paragraph("<b>PROCEDURE IN DETAIL:</b>", self.styles['Normal']))
        procedure_text = """
        The patient was brought to the operating room and placed in supine position on the operating table.
        After adequate general anesthesia was achieved, the patient was prepped and draped in the usual sterile fashion.
        A time-out was performed confirming correct patient, procedure, and site.
        <br/><br/>
        Standard surgical technique was employed. The procedure was performed without complications.
        Hemostasis was achieved. The surgical site was irrigated and closed in layers using absorbable sutures.
        Sterile dressing was applied.
        <br/><br/>
        The patient tolerated the procedure well and was transferred to the recovery room in stable condition.
        Estimated blood loss: 50 mL. No specimens sent to pathology.
        """
        story.append(Paragraph(procedure_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Signature
        sig_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        phi_annotations.append({'type': 'date', 'value': sig_time.split()[0], 'page': 1, 'context': 'signature'})

        story.append(Paragraph(f"<b>Electronically signed by:</b> {surgeon}", self.styles['Normal']))
        story.append(Paragraph(f"Date/Time: {sig_time}", self.styles['Normal']))

        doc.build(story)
        return phi_annotations

    def create_pathology_report(self, patient_data, output_path):
        """Create pathology/biopsy report."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Header
        lab_name = random.choice([
            "Massachusetts Pathology Laboratory",
            "University Hospital Department of Pathology",
            "Regional Diagnostic Pathology Services"
        ])

        story.append(Paragraph(f"<b>{lab_name}</b>", self.styles['CenterBold']))
        story.append(Paragraph("SURGICAL PATHOLOGY REPORT", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.append({'type': 'institution', 'value': lab_name, 'page': 1, 'context': 'pathology_lab'})

        # Accession info
        accession = f"S{datetime.now().strftime('%y')}-{self.faker.random_number(digits=6, fix_len=True)}"
        collection_date = self.faker.date_between(start_date='-14d', end_date='-7d').strftime('%Y-%m-%d')
        received_date = (datetime.strptime(collection_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        report_date = datetime.now().strftime('%Y-%m-%d')

        phi_annotations.extend([
            {'type': 'unique_id', 'value': accession, 'page': 1, 'context': 'accession'},
            {'type': 'date', 'value': collection_date, 'page': 1, 'context': 'collection'},
            {'type': 'date', 'value': received_date, 'page': 1, 'context': 'received'},
            {'type': 'date', 'value': report_date, 'page': 1, 'context': 'report'}
        ])

        # Patient info
        patient_info = [
            ['Patient Name:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['Date of Birth:', patient_data['birth_date'], 'Sex:', random.choice(['M', 'F'])],
            ['Accession #:', accession, 'Physician:', f"Dr. {self.faker.last_name()}"],
            ['Collection Date:', collection_date, 'Received:', received_date],
            ['Report Date:', report_date, 'Priority:', 'Routine'],
        ]

        physician_name = patient_info[2][3]
        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'name', 'value': physician_name, 'page': 1, 'context': 'physician'}
        ])

        info_table = Table(patient_info, colWidths=[1.5*inch, 2*inch, 1.2*inch, 1.8*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # Clinical history
        story.append(Paragraph("<b>CLINICAL HISTORY:</b>", self.styles['Normal']))
        clinical_history = random.choice([
            "45-year-old with abnormal mammogram, suspicious mass right breast.",
            "62-year-old with history of polyps, surveillance colonoscopy.",
            "55-year-old with abnormal Pap smear, cervical biopsy.",
            "68-year-old smoker with lung nodule on CT, bronchoscopy with biopsy.",
            "50-year-old with skin lesion, rule out melanoma."
        ])
        story.append(Paragraph(clinical_history, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Specimen
        story.append(Paragraph("<b>SPECIMEN:</b>", self.styles['Normal']))
        specimen = random.choice([
            "Core needle biopsy, right breast",
            "Colon polyp, descending colon",
            "Cervical biopsy",
            "Lung mass, right upper lobe",
            "Skin lesion, left shoulder"
        ])
        story.append(Paragraph(specimen, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Gross description
        story.append(Paragraph("<b>GROSS DESCRIPTION:</b>", self.styles['Normal']))
        gross_text = f"""
        Received fresh in formalin labeled with patient name {patient_data['name']} and "{specimen}" is a
        {random.choice(['core of tan-pink tissue', 'fragment of tan-brown tissue', 'portion of pink-tan tissue'])}
        measuring {random.uniform(0.3, 1.5):.1f} x {random.uniform(0.2, 0.8):.1f} x {random.uniform(0.1, 0.5):.1f} cm.
        The specimen is entirely submitted in cassette A1.
        """
        story.append(Paragraph(gross_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Microscopic description
        story.append(Paragraph("<b>MICROSCOPIC DESCRIPTION:</b>", self.styles['Normal']))
        micro_text = """
        Sections show tissue architecture within normal limits. No evidence of malignancy is identified.
        The specimen demonstrates benign histologic features. Focal inflammatory changes are noted.
        No dysplasia, atypia, or malignant transformation is observed.
        """
        story.append(Paragraph(micro_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Diagnosis
        story.append(Paragraph("<b>DIAGNOSIS:</b>", self.styles['Normal']))
        diagnosis = random.choice([
            "Benign breast tissue with fibrocystic changes",
            "Tubular adenoma, colon",
            "Chronic cervicitis with squamous metaplasia",
            "Benign lung parenchyma with anthracotic pigment",
            "Benign intradermal nevus"
        ])
        story.append(Paragraph(f"<b>{specimen.upper()}:</b> {diagnosis}", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Comment
        story.append(Paragraph("<b>COMMENT:</b>", self.styles['Normal']))
        comment = "No evidence of malignancy. Clinical correlation recommended."
        story.append(Paragraph(comment, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Pathologist signature
        pathologist = f"Dr. {self.faker.last_name()}, MD"
        board_cert = "Board Certified in Anatomic and Clinical Pathology"

        phi_annotations.append({'type': 'name', 'value': pathologist, 'page': 1, 'context': 'pathologist'})

        sig_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        phi_annotations.append({'type': 'date', 'value': sig_time.split()[0], 'page': 1, 'context': 'signature'})

        story.append(Paragraph(f"<b>Pathologist:</b> {pathologist}", self.styles['Normal']))
        story.append(Paragraph(board_cert, self.styles['Normal']))
        story.append(Paragraph(f"<b>Electronically signed:</b> {sig_time}", self.styles['Normal']))

        doc.build(story)
        return phi_annotations

    def create_ed_note(self, patient_data, output_path):
        """Create Emergency Department note."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Header
        ed_name = random.choice([
            "Massachusetts General Hospital Emergency Department",
            "St. Mary's Emergency Room",
            "University Medical Center - Emergency Services"
        ])

        story.append(Paragraph(f"<b>{ed_name}</b>", self.styles['CenterBold']))
        story.append(Paragraph("EMERGENCY DEPARTMENT NOTE", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.append({'type': 'institution', 'value': ed_name, 'page': 1, 'context': 'ed'})

        # Visit info
        arrival_time = datetime.now() - timedelta(hours=random.randint(1, 6))
        arrival_str = arrival_time.strftime('%Y-%m-%d %H:%M')

        phi_annotations.append({'type': 'date', 'value': arrival_str.split()[0], 'page': 1, 'context': 'arrival'})

        # Patient info
        patient_info = [
            ['Patient Name:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['Date of Birth:', patient_data['birth_date'], 'Age:', str(datetime.now().year - int(patient_data['birth_date'][:4]))],
            ['Arrival Time:', arrival_str, 'Acuity:', random.choice(['ESI 2', 'ESI 3', 'ESI 4'])],
            ['Provider:', f"Dr. {self.faker.last_name()}, MD", 'Contact:', patient_data['phone']],
        ]

        provider_name = patient_info[3][1]
        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'name', 'value': provider_name, 'page': 1, 'context': 'provider'},
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1}
        ])

        info_table = Table(patient_info, colWidths=[1.5*inch, 2*inch, 1*inch, 2*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # Chief Complaint
        story.append(Paragraph("<b>CHIEF COMPLAINT:</b>", self.styles['Normal']))
        chief_complaint = random.choice([
            "Chest pain",
            "Abdominal pain",
            "Shortness of breath",
            "Headache",
            "Fall with possible injury",
            "Laceration to hand"
        ])
        story.append(Paragraph(chief_complaint, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Triage Vitals
        story.append(Paragraph("<b>TRIAGE VITALS:</b>", self.styles['Normal']))
        vitals_data = [
            ['BP:', f"{random.randint(110, 160)}/{random.randint(60, 95)}", 'HR:', str(random.randint(60, 110))],
            ['RR:', str(random.randint(12, 24)), 'Temp:', f"{random.uniform(97.0, 99.5):.1f}°F"],
            ['SpO2:', f"{random.randint(94, 100)}%", 'Pain:', f"{random.randint(0, 10)}/10"],
        ]

        vitals_table = Table(vitals_data, colWidths=[1*inch, 1.5*inch, 1*inch, 1.5*inch])
        vitals_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(vitals_table)
        story.append(Spacer(1, 0.1 * inch))

        # HPI
        story.append(Paragraph("<b>HISTORY OF PRESENT ILLNESS:</b>", self.styles['Normal']))
        hpi_text = f"""
        Patient is a {datetime.now().year - int(patient_data['birth_date'][:4])}-year-old who presents to the ED with {chief_complaint}.
        Symptoms began approximately {random.randint(1, 48)} hours ago. {random.choice(['Denies', 'Reports'])} associated nausea, vomiting, or fever.
        {random.choice(['No', 'Some'])} relief with over-the-counter medications. {random.choice(['Denies', 'Reports'])} recent trauma.
        """
        story.append(Paragraph(hpi_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Physical Exam
        story.append(Paragraph("<b>PHYSICAL EXAMINATION:</b>", self.styles['Normal']))
        pe_text = """
        <b>General:</b> Alert and oriented x3, in no acute distress.
        <br/><b>HEENT:</b> Normocephalic, atraumatic. PERRLA. Moist mucous membranes.
        <br/><b>Cardiovascular:</b> Regular rate and rhythm. No murmurs, rubs, or gallops.
        <br/><b>Respiratory:</b> Clear to auscultation bilaterally. No wheezes, rales, or rhonchi.
        <br/><b>Abdomen:</b> Soft, non-tender, non-distended. Normal bowel sounds.
        <br/><b>Extremities:</b> No edema. Full range of motion.
        <br/><b>Neurological:</b> Cranial nerves II-XII intact. Motor 5/5 throughout.
        """
        story.append(Paragraph(pe_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # ED Course
        story.append(Paragraph("<b>ED COURSE:</b>", self.styles['Normal']))
        ed_course = f"""
        Patient received supportive care including IV hydration and pain management.
        Laboratory studies and imaging were obtained as clinically indicated.
        Patient's symptoms improved with treatment. Patient tolerated interventions well.
        """
        story.append(Paragraph(ed_course, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Disposition
        story.append(Paragraph("<b>DISPOSITION:</b>", self.styles['Normal']))
        disposition = random.choice([
            "Discharged home with instructions and prescriptions.",
            "Admitted to Internal Medicine service for further management.",
            "Transferred to observation unit for monitoring.",
            "Discharged with follow-up scheduled with PCP in 2-3 days."
        ])
        story.append(Paragraph(disposition, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Signature
        sig_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        phi_annotations.append({'type': 'date', 'value': sig_time.split()[0], 'page': 1, 'context': 'signature'})

        story.append(Paragraph(f"<b>Electronically signed by:</b> {provider_name}", self.styles['Normal']))
        story.append(Paragraph(f"Date/Time: {sig_time}", self.styles['Normal']))

        doc.build(story)
        return phi_annotations

    def create_consultation_note(self, patient_data, output_path):
        """Create specialist consultation note."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Header
        specialty = random.choice(['Cardiology', 'Neurology', 'Gastroenterology', 'Pulmonology', 'Endocrinology'])
        facility = f"{specialty} Associates of Massachusetts"

        story.append(Paragraph(f"<b>{facility}</b>", self.styles['CenterBold']))
        story.append(Paragraph("CONSULTATION NOTE", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.append({'type': 'institution', 'value': facility, 'page': 1, 'context': 'specialty_practice'})

        # Consult date
        consult_date = datetime.now().strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': consult_date, 'page': 1, 'context': 'consultation'})

        # Patient info
        referring_md = f"Dr. {self.faker.last_name()}, MD"
        consultant = f"Dr. {self.faker.last_name()}, MD"

        patient_info = [
            ['Patient Name:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['Date of Birth:', patient_data['birth_date'], 'Date:', consult_date],
            ['Referring MD:', referring_md, 'Consultant:', consultant],
        ]

        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'name', 'value': referring_md, 'page': 1, 'context': 'referring'},
            {'type': 'name', 'value': consultant, 'page': 1, 'context': 'consultant'}
        ])

        info_table = Table(patient_info, colWidths=[1.5*inch, 2.5*inch, 1*inch, 2*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # Reason for consultation
        story.append(Paragraph("<b>REASON FOR CONSULTATION:</b>", self.styles['Normal']))
        reason = random.choice([
            "Evaluation and management of refractory hypertension",
            "Assessment of recurrent headaches, rule out neurological etiology",
            "Evaluation of abnormal liver enzymes",
            "Management of poorly controlled diabetes mellitus",
            "Evaluation of dyspnea and chronic cough"
        ])
        story.append(Paragraph(reason, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # History
        story.append(Paragraph("<b>HISTORY:</b>", self.styles['Normal']))
        history_text = f"""
        Thank you for referring this {datetime.now().year - int(patient_data['birth_date'][:4])}-year-old patient for {specialty.lower()} evaluation.
        The patient has a history of {random.choice(['hypertension', 'diabetes', 'hyperlipidemia', 'COPD', 'CAD'])} and presents with the above complaint.
        Review of systems is significant for {random.choice(['fatigue', 'weight loss', 'dyspnea', 'chest discomfort', 'palpitations'])}.
        <br/><br/>
        Current medications include: {', '.join([random.choice(['Lisinopril', 'Metformin', 'Atorvastatin', 'Metoprolol', 'Aspirin']) for _ in range(3)])}.
        """
        story.append(Paragraph(history_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Physical examination
        story.append(Paragraph("<b>PHYSICAL EXAMINATION:</b>", self.styles['Normal']))
        pe_text = """
        Vitals: BP 138/82, HR 76, RR 16, Temp 98.4°F, SpO2 97% on RA
        <br/><b>General:</b> Well-appearing, no acute distress
        <br/><b>Cardiovascular:</b> Regular rhythm, normal S1/S2, no murmurs
        <br/><b>Respiratory:</b> Clear breath sounds bilaterally
        <br/><b>Abdomen:</b> Soft, non-tender, no organomegaly
        """
        story.append(Paragraph(pe_text, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Assessment
        story.append(Paragraph("<b>ASSESSMENT AND RECOMMENDATIONS:</b>", self.styles['Normal']))
        assessment_text = f"""
        1. {reason}
        <br/>   - Reviewed patient's history, physical exam, and available records
        <br/>   - Recommend initiating {random.choice(['ACE inhibitor', 'beta blocker', 'calcium channel blocker', 'statin therapy', 'lifestyle modifications'])}
        <br/>   - Obtain additional testing: {random.choice(['echocardiogram', 'stress test', 'MRI', 'CT scan', 'laboratory studies'])}
        <br/><br/>
        2. Continue current medical management with close monitoring
        <br/><br/>
        3. Follow-up in {random.choice([2, 4, 6, 8, 12])} weeks or sooner if symptoms worsen
        <br/><br/>
        Thank you for this interesting consultation. I will continue to follow the patient with you.
        """
        story.append(Paragraph(assessment_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Contact
        story.append(Paragraph(f"<b>Questions or concerns:</b> Contact {consultant} at {patient_data['phone']}", self.styles['Normal']))
        phi_annotations.append({'type': 'phone', 'value': patient_data['phone'], 'page': 1})

        story.append(Spacer(1, 0.2 * inch))

        # Signature
        sig_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        phi_annotations.append({'type': 'date', 'value': sig_time.split()[0], 'page': 1, 'context': 'signature'})

        story.append(Paragraph(f"<b>Electronically signed by:</b> {consultant}", self.styles['Normal']))
        story.append(Paragraph(f"{specialty} Specialist", self.styles['Normal']))
        story.append(Paragraph(f"Date/Time: {sig_time}", self.styles['Normal']))

        doc.build(story)
        return phi_annotations

    def create_history_physical(self, patient_data, output_path):
        """Create comprehensive History & Physical admission note."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Header
        hospital = random.choice([
            "Massachusetts General Hospital",
            "University Medical Center",
            "St. Mary's Regional Hospital"
        ])

        story.append(Paragraph(f"<b>{hospital}</b>", self.styles['CenterBold']))
        story.append(Paragraph("HISTORY AND PHYSICAL EXAMINATION", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.append({'type': 'institution', 'value': hospital, 'page': 1, 'context': 'hospital'})

        # Admission info
        admission_date = datetime.now().strftime('%Y-%m-%d')
        admission_time = datetime.now().strftime('%H:%M')

        phi_annotations.append({'type': 'date', 'value': admission_date, 'page': 1, 'context': 'admission'})

        # Patient info
        attending = f"Dr. {self.faker.last_name()}, MD"

        patient_info = [
            ['Patient Name:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['Date of Birth:', patient_data['birth_date'], 'Admission:', f"{admission_date} {admission_time}"],
            ['Attending:', attending, 'Service:', random.choice(['Internal Medicine', 'Surgery', 'Cardiology'])],
        ]

        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'name', 'value': attending, 'page': 1, 'context': 'attending'}
        ])

        info_table = Table(patient_info, colWidths=[1.5*inch, 2.5*inch, 1*inch, 2*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.2 * inch))

        # Chief Complaint
        story.append(Paragraph("<b>CHIEF COMPLAINT:</b>", self.styles['Normal']))
        cc = random.choice(["Chest pain", "Shortness of breath", "Abdominal pain", "Syncope", "Altered mental status"])
        story.append(Paragraph(cc, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # HPI
        story.append(Paragraph("<b>HISTORY OF PRESENT ILLNESS:</b>", self.styles['Normal']))
        hpi = f"""
        This is a {datetime.now().year - int(patient_data['birth_date'][:4])}-year-old patient with past medical history of
        {random.choice(['hypertension', 'diabetes', 'CAD', 'CHF', 'COPD'])} who presents with {cc.lower()}.
        Symptoms began {random.randint(1, 48)} hours prior to presentation. Associated symptoms include
        {random.choice(['nausea', 'diaphoresis', 'palpitations', 'lightheadedness'])}. Patient denies fever, chills.
        Arrived via {random.choice(['private vehicle', 'EMS', 'ambulance'])}. In the ED, vital signs notable for
        BP {random.randint(110, 180)}/{random.randint(60, 100)}, HR {random.randint(60, 120)}.
        """
        story.append(Paragraph(hpi, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Past Medical History
        story.append(Paragraph("<b>PAST MEDICAL HISTORY:</b>", self.styles['Normal']))
        pmh = "1. Hypertension\n2. Diabetes mellitus type 2\n3. Hyperlipidemia\n4. Coronary artery disease\n5. Chronic kidney disease stage 3"
        story.append(Paragraph(pmh.replace('\n', '<br/>'), self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Medications
        story.append(Paragraph("<b>MEDICATIONS:</b>", self.styles['Normal']))
        meds = "1. Lisinopril 20mg daily\n2. Metformin 1000mg BID\n3. Atorvastatin 40mg QHS\n4. Aspirin 81mg daily\n5. Metoprolol 50mg BID"
        story.append(Paragraph(meds.replace('\n', '<br/>'), self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Allergies
        story.append(Paragraph("<b>ALLERGIES:</b>", self.styles['Normal']))
        allergies = random.choice(["NKDA", "Penicillin (rash)", "Sulfa drugs (hives)"])
        story.append(Paragraph(allergies, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Social History
        story.append(Paragraph("<b>SOCIAL HISTORY:</b>", self.styles['Normal']))
        social = f"Patient lives at {patient_data['address']}. {random.choice(['Non-smoker', 'Former smoker', 'Current smoker 1 PPD'])}. {random.choice(['Denies alcohol', 'Social drinker', 'Occasional alcohol'])}. Denies illicit drug use."
        story.append(Paragraph(social, self.styles['Normal']))
        phi_annotations.append({'type': 'address', 'value': patient_data['address'], 'page': 1})
        story.append(Spacer(1, 0.1 * inch))

        # Family History
        story.append(Paragraph("<b>FAMILY HISTORY:</b>", self.styles['Normal']))
        fh = "Father: CAD, MI at age 65. Mother: Diabetes, HTN. No family history of cancer."
        story.append(Paragraph(fh, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Physical Examination
        story.append(Paragraph("<b>PHYSICAL EXAMINATION:</b>", self.styles['Normal']))
        pe = """
        <b>Vitals:</b> BP 142/88, HR 82, RR 18, Temp 98.6°F, SpO2 96% on RA
        <br/><b>General:</b> Alert, oriented x3, NAD
        <br/><b>HEENT:</b> Normocephalic, atraumatic, PERRLA, EOMI, MMM
        <br/><b>Neck:</b> Supple, no JVD, no lymphadenopathy
        <br/><b>Cardiovascular:</b> RRR, normal S1/S2, no m/r/g
        <br/><b>Respiratory:</b> CTAB, no wheezes/rales/rhonchi
        <br/><b>Abdomen:</b> Soft, NT/ND, +BS, no HSM
        <br/><b>Extremities:</b> No c/c/e, 2+ pulses, FROM
        <br/><b>Neurological:</b> CN II-XII intact, motor 5/5, sensation intact
        """
        story.append(Paragraph(pe, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        # Assessment and Plan
        story.append(Paragraph("<b>ASSESSMENT AND PLAN:</b>", self.styles['Normal']))
        ap = f"""
        1. {cc} - Rule out {random.choice(['ACS', 'PE', 'acute abdomen', 'stroke', 'infection'])}
        <br/>   - Serial troponins, EKG, imaging as indicated
        <br/>   - Continue medical management, monitor closely
        <br/><br/>
        2. Hypertension - Continue home medications
        <br/><br/>
        3. Diabetes - Hold metformin, sliding scale insulin
        <br/><br/>
        4. Disposition - Admit to {random.choice(['telemetry', 'medical floor', 'ICU'])} for further management
        """
        story.append(Paragraph(ap, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Signature
        sig_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        phi_annotations.append({'type': 'date', 'value': sig_time.split()[0], 'page': 1, 'context': 'signature'})

        story.append(Paragraph(f"<b>Electronically signed by:</b> {attending}", self.styles['Normal']))
        story.append(Paragraph(f"Date/Time: {sig_time}", self.styles['Normal']))

        doc.build(story)
        return phi_annotations

    def create_referral_letter(self, patient_data, output_path):
        """Create provider-to-provider referral letter."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Referring practice header
        referring_practice = random.choice([
            "Boston Primary Care Associates",
            "Massachusetts Family Medicine",
            "Commonwealth Internal Medicine Group"
        ])

        referring_address = self.faker.address().replace('\n', ', ')
        referring_phone = self.faker.phone_number()
        referring_fax = self.faker.phone_number()

        story.append(Paragraph(f"<b>{referring_practice}</b>", self.styles['Normal']))
        story.append(Paragraph(referring_address, self.styles['Normal']))
        story.append(Paragraph(f"Phone: {referring_phone} | Fax: {referring_fax}", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.extend([
            {'type': 'institution', 'value': referring_practice, 'page': 1, 'context': 'referring_practice'},
            {'type': 'address', 'value': referring_address, 'page': 1, 'context': 'practice_address'},
            {'type': 'phone', 'value': referring_phone, 'page': 1, 'context': 'practice_phone'},
            {'type': 'phone', 'value': referring_fax, 'page': 1, 'context': 'practice_fax'}
        ])

        # Date
        letter_date = datetime.now().strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': letter_date, 'page': 1, 'context': 'letter'})

        story.append(Paragraph(f"<b>Date:</b> {letter_date}", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # To
        specialist = random.choice(['Cardiology', 'Neurology', 'Gastroenterology', 'Orthopedics', 'Dermatology'])
        specialist_name = f"Dr. {self.faker.last_name()}, MD"
        specialist_practice = f"{specialist} Specialists of Massachusetts"

        story.append(Paragraph(f"<b>To:</b> {specialist_name}", self.styles['Normal']))
        story.append(Paragraph(specialist_practice, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        phi_annotations.extend([
            {'type': 'name', 'value': specialist_name, 'page': 1, 'context': 'specialist'},
            {'type': 'institution', 'value': specialist_practice, 'page': 1, 'context': 'specialist_practice'}
        ])

        # From
        referring_md = f"Dr. {self.faker.last_name()}, MD"
        story.append(Paragraph(f"<b>From:</b> {referring_md}", self.styles['Normal']))
        story.append(Paragraph(referring_practice, self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        phi_annotations.append({'type': 'name', 'value': referring_md, 'page': 1, 'context': 'referring_md'})

        # Re: Patient
        story.append(Paragraph(f"<b>Re:</b> {patient_data['name']}", self.styles['Normal']))
        story.append(Paragraph(f"DOB: {patient_data['birth_date']} | MRN: {patient_data['mrn']}", self.styles['Normal']))
        story.append(Paragraph(f"Phone: {patient_data['phone']}", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1}
        ])

        # Letter body
        story.append(Paragraph(f"Dear Dr. {specialist_name.split()[1]},", self.styles['Normal']))
        story.append(Spacer(1, 0.1 * inch))

        reason = random.choice([
            "persistent symptoms despite conservative management",
            "abnormal findings requiring specialist evaluation",
            "poorly controlled condition needing expert consultation",
            "complex medical issue requiring specialized care"
        ])

        letter_body = f"""
        I am writing to refer {patient_data['name']}, a {datetime.now().year - int(patient_data['birth_date'][:4])}-year-old patient,
        for {specialist.lower()} evaluation and management of {reason}.
        <br/><br/>
        <b>Relevant History:</b><br/>
        The patient has a past medical history significant for {random.choice(['hypertension', 'diabetes', 'hyperlipidemia', 'COPD', 'CAD'])},
        {random.choice(['chronic kidney disease', 'osteoarthritis', 'GERD', 'depression', 'hypothyroidism'])}, and
        {random.choice(['obesity', 'sleep apnea', 'peripheral neuropathy', 'anemia', 'atrial fibrillation'])}.
        Current medications include Lisinopril 20mg daily, Metformin 1000mg BID, and Atorvastatin 40mg QHS.
        <br/><br/>
        <b>Current Issue:</b><br/>
        Over the past {random.randint(3, 12)} months, the patient has experienced {random.choice(['progressive symptoms', 'worsening condition', 'recurrent episodes', 'persistent complaints'])}.
        Recent workup including {random.choice(['laboratory studies', 'imaging', 'EKG', 'stress test'])} has shown {random.choice(['abnormal findings', 'concerning results', 'borderline values'])}.
        I have initiated conservative management with {random.choice(['lifestyle modifications', 'medication adjustment', 'physical therapy'])}, but symptoms persist.
        <br/><br/>
        <b>Reason for Referral:</b><br/>
        I would greatly appreciate your expertise in evaluating and managing this patient's {specialist.lower()} concerns.
        Specific questions include further diagnostic workup recommendations and optimization of medical therapy.
        <br/><br/>
        Thank you for seeing this patient. Please feel free to contact me at {referring_phone} if you have any questions
        or need additional information. I look forward to collaborating on this patient's care.
        <br/><br/>
        Sincerely,<br/>
        {referring_md}<br/>
        {referring_practice}
        """

        story.append(Paragraph(letter_body, self.styles['Normal']))

        doc.build(story)
        return phi_annotations

    def create_registration_form(self, patient_data, output_path):
        """Create patient registration/intake form."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Header
        practice = random.choice([
            "Boston Health Center",
            "Massachusetts Medical Group",
            "Commonwealth Care Associates"
        ])

        story.append(Paragraph(f"<b>{practice}</b>", self.styles['CenterBold']))
        story.append(Paragraph("PATIENT REGISTRATION FORM", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.append({'type': 'institution', 'value': practice, 'page': 1, 'context': 'practice'})

        reg_date = datetime.now().strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': reg_date, 'page': 1, 'context': 'registration'})

        story.append(Paragraph(f"<b>Date:</b> {reg_date}", self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Patient Demographics
        story.append(Paragraph("<b>PATIENT INFORMATION</b>", self.styles['Heading2']))
        story.append(Spacer(1, 0.1 * inch))

        patient_email = patient_data.get('email', self.faker.email())

        demographics = [
            ['Full Name:', patient_data['name'], 'Preferred Name:', patient_data['name'].split()[0]],
            ['Date of Birth:', patient_data['birth_date'], 'SSN:', patient_data['ssn']],
            ['Sex:', random.choice(['Male', 'Female']), 'Gender Identity:', random.choice(['Male', 'Female', 'Non-binary'])],
            ['Marital Status:', random.choice(['Single', 'Married', 'Divorced', 'Widowed']), 'Race:', random.choice(['White', 'Black', 'Asian', 'Hispanic', 'Other'])],
        ]

        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'ssn', 'value': patient_data['ssn'], 'page': 1}
        ])

        demo_table = Table(demographics, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
        demo_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(demo_table)
        story.append(Spacer(1, 0.1 * inch))

        # Contact Information
        story.append(Paragraph("<b>CONTACT INFORMATION</b>", self.styles['Heading2']))
        story.append(Spacer(1, 0.1 * inch))

        contact_info = [
            ['Address:', patient_data['address'], '', ''],
            ['Phone (Home):', patient_data['phone'], 'Phone (Mobile):', self.faker.phone_number()],
            ['Email:', patient_email, '', ''],
        ]

        mobile_phone = contact_info[1][3]

        phi_annotations.extend([
            {'type': 'address', 'value': patient_data['address'], 'page': 1},
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1, 'context': 'home'},
            {'type': 'phone', 'value': mobile_phone, 'page': 1, 'context': 'mobile'},
            {'type': 'email', 'value': patient_email, 'page': 1}
        ])

        contact_table = Table(contact_info, colWidths=[1.5*inch, 2*inch, 1.5*inch, 1.5*inch])
        contact_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('SPAN', (1, 0), (3, 0)),
            ('SPAN', (1, 2), (3, 2)),
        ]))
        story.append(contact_table)
        story.append(Spacer(1, 0.1 * inch))

        # Emergency Contact
        story.append(Paragraph("<b>EMERGENCY CONTACT</b>", self.styles['Heading2']))
        story.append(Spacer(1, 0.1 * inch))

        emergency_name = self.faker.name()
        emergency_phone = self.faker.phone_number()
        emergency_relation = random.choice(['Spouse', 'Parent', 'Child', 'Sibling', 'Friend'])

        emergency_info = [
            ['Name:', emergency_name, 'Relationship:', emergency_relation],
            ['Phone:', emergency_phone, 'Alt Phone:', self.faker.phone_number()],
        ]

        alt_emergency_phone = emergency_info[1][3]

        phi_annotations.extend([
            {'type': 'name', 'value': emergency_name, 'page': 1, 'context': 'emergency_contact'},
            {'type': 'phone', 'value': emergency_phone, 'page': 1, 'context': 'emergency'},
            {'type': 'phone', 'value': alt_emergency_phone, 'page': 1, 'context': 'emergency_alt'}
        ])

        emergency_table = Table(emergency_info, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1*inch])
        emergency_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(emergency_table)
        story.append(Spacer(1, 0.1 * inch))

        # Insurance Information
        story.append(Paragraph("<b>INSURANCE INFORMATION</b>", self.styles['Heading2']))
        story.append(Spacer(1, 0.1 * inch))

        insurance_company = random.choice(['Blue Cross Blue Shield', 'Aetna', 'United Healthcare', 'Cigna', 'Medicare'])
        group_number = f"GRP{self.faker.random_number(digits=8, fix_len=True)}"

        insurance_info = [
            ['Primary Insurance:', insurance_company, 'Member ID:', patient_data['insurance_id']],
            ['Group Number:', group_number, 'Effective Date:', self.faker.date_between(start_date='-2y', end_date='today').strftime('%Y-%m-%d')],
            ['Subscriber Name:', patient_data['name'], 'Relationship:', 'Self'],
        ]

        effective_date = insurance_info[1][3]

        phi_annotations.extend([
            {'type': 'institution', 'value': insurance_company, 'page': 1, 'context': 'insurance'},
            {'type': 'insurance_id', 'value': patient_data['insurance_id'], 'page': 1},
            {'type': 'unique_id', 'value': group_number, 'page': 1, 'context': 'insurance_group'},
            {'type': 'date', 'value': effective_date, 'page': 1, 'context': 'insurance_effective'}
        ])

        insurance_table = Table(insurance_info, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1*inch])
        insurance_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(insurance_table)
        story.append(Spacer(1, 0.2 * inch))

        # Consent signature
        story.append(Paragraph("<b>PATIENT CONSENT AND SIGNATURE</b>", self.styles['Heading2']))
        story.append(Spacer(1, 0.1 * inch))

        consent_text = """
        I certify that the information provided above is accurate and complete to the best of my knowledge.
        I authorize the release of medical information necessary for insurance claims and treatment coordination.
        """
        story.append(Paragraph(consent_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        sig_date = datetime.now().strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': sig_date, 'page': 1, 'context': 'signature'})

        sig_info = [
            ['Patient Signature:', '_' * 40, 'Date:', sig_date],
        ]

        sig_table = Table(sig_info, colWidths=[1.5*inch, 3*inch, 1*inch, 1*inch])
        sig_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
        ]))
        story.append(sig_table)

        doc.build(story)
        return phi_annotations

    def create_immunization_record(self, patient_data, output_path):
        """Create immunization/vaccination history record."""
        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        phi_annotations = []

        # Header
        provider = random.choice([
            "Massachusetts Immunization Program",
            "Boston Public Health Department",
            "Commonwealth Vaccine Services"
        ])

        story.append(Paragraph(f"<b>{provider}</b>", self.styles['CenterBold']))
        story.append(Paragraph("IMMUNIZATION RECORD", self.styles['CenterBold']))
        story.append(Spacer(1, 0.2 * inch))

        phi_annotations.append({'type': 'institution', 'value': provider, 'page': 1, 'context': 'vaccine_provider'})

        # Patient info
        record_date = datetime.now().strftime('%Y-%m-%d')
        phi_annotations.append({'type': 'date', 'value': record_date, 'page': 1, 'context': 'record'})

        patient_info = [
            ['Patient Name:', patient_data['name'], 'MRN:', patient_data['mrn']],
            ['Date of Birth:', patient_data['birth_date'], 'Record Date:', record_date],
            ['Address:', patient_data['address'], '', ''],
            ['Phone:', patient_data['phone'], 'Email:', patient_data.get('email', self.faker.email())],
        ]

        patient_email = patient_info[3][3]

        phi_annotations.extend([
            {'type': 'name', 'value': patient_data['name'], 'page': 1, 'context': 'patient'},
            {'type': 'mrn', 'value': patient_data['mrn'], 'page': 1},
            {'type': 'date', 'value': patient_data['birth_date'], 'page': 1, 'context': 'dob'},
            {'type': 'address', 'value': patient_data['address'], 'page': 1},
            {'type': 'phone', 'value': patient_data['phone'], 'page': 1},
            {'type': 'email', 'value': patient_email, 'page': 1}
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

        # Immunization history
        story.append(Paragraph("<b>IMMUNIZATION HISTORY</b>", self.styles['Heading2']))
        story.append(Spacer(1, 0.1 * inch))

        # Create vaccine records
        vaccines = [
            {
                'vaccine': 'COVID-19 (Moderna)',
                'date': self.faker.date_between(start_date='-2y', end_date='-1y').strftime('%Y-%m-%d'),
                'lot': f"MOD{self.faker.random_number(digits=6, fix_len=True)}",
                'site': 'Left deltoid',
                'provider': f"Dr. {self.faker.last_name()}"
            },
            {
                'vaccine': 'COVID-19 Booster (Moderna)',
                'date': self.faker.date_between(start_date='-1y', end_date='-6m').strftime('%Y-%m-%d'),
                'lot': f"MOD{self.faker.random_number(digits=6, fix_len=True)}",
                'site': 'Left deltoid',
                'provider': f"Dr. {self.faker.last_name()}"
            },
            {
                'vaccine': 'Influenza (Quadrivalent)',
                'date': self.faker.date_between(start_date='-6m', end_date='today').strftime('%Y-%m-%d'),
                'lot': f"FLU{self.faker.random_number(digits=6, fix_len=True)}",
                'site': 'Right deltoid',
                'provider': f"Dr. {self.faker.last_name()}"
            },
            {
                'vaccine': 'Tdap (Tetanus/Diphtheria/Pertussis)',
                'date': self.faker.date_between(start_date='-5y', end_date='-3y').strftime('%Y-%m-%d'),
                'lot': f"TDAP{self.faker.random_number(digits=5, fix_len=True)}",
                'site': 'Left deltoid',
                'provider': f"Dr. {self.faker.last_name()}"
            },
            {
                'vaccine': 'Pneumococcal (PPSV23)',
                'date': self.faker.date_between(start_date='-4y', end_date='-2y').strftime('%Y-%m-%d'),
                'lot': f"PPSV{self.faker.random_number(digits=5, fix_len=True)}",
                'site': 'Right deltoid',
                'provider': f"Dr. {self.faker.last_name()}"
            },
        ]

        # Add PHI annotations for vaccine dates and providers
        for vaccine in vaccines:
            phi_annotations.append({'type': 'date', 'value': vaccine['date'], 'page': 1, 'context': 'vaccination'})
            phi_annotations.append({'type': 'name', 'value': vaccine['provider'], 'page': 1, 'context': 'vaccine_provider'})
            phi_annotations.append({'type': 'unique_id', 'value': vaccine['lot'], 'page': 1, 'context': 'lot_number'})

        # Create table
        vaccine_data = [['Vaccine', 'Date Given', 'Lot Number', 'Site', 'Provider']]
        for vaccine in vaccines:
            vaccine_data.append([
                vaccine['vaccine'],
                vaccine['date'],
                vaccine['lot'],
                vaccine['site'],
                vaccine['provider']
            ])

        vaccine_table = Table(vaccine_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1.5*inch])
        vaccine_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        story.append(vaccine_table)
        story.append(Spacer(1, 0.2 * inch))

        # Next due
        story.append(Paragraph("<b>UPCOMING IMMUNIZATIONS</b>", self.styles['Heading2']))
        story.append(Spacer(1, 0.1 * inch))

        next_covid = (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d')
        next_flu = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')

        phi_annotations.extend([
            {'type': 'date', 'value': next_covid, 'page': 1, 'context': 'next_due'},
            {'type': 'date', 'value': next_flu, 'page': 1, 'context': 'next_due'}
        ])

        upcoming = f"""
        - COVID-19 Booster: Due {next_covid}
        <br/>- Influenza (Annual): Due {next_flu}
        <br/>- Tdap Booster: Due in 10 years from last dose
        """
        story.append(Paragraph(upcoming, self.styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))

        # Footer
        story.append(Paragraph("<i>This is an official immunization record. Please keep for your records.</i>", self.styles['Normal']))
        story.append(Paragraph(f"<i>Record generated: {record_date}</i>", self.styles['Normal']))
        story.append(Paragraph(f"<i>For questions, contact {provider} at {self.faker.phone_number()}</i>", self.styles['Normal']))

        provider_phone = self.faker.phone_number()
        phi_annotations.append({'type': 'phone', 'value': provider_phone, 'page': 1, 'context': 'provider'})

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

    parser = argparse.ArgumentParser(description='Generate additional medical document types')
    parser.add_argument('--samples-only', action='store_true', help='Generate one sample of each type only')
    parser.add_argument('--num-each', type=int, default=1000, help='Number of each document type to generate')
    parser.add_argument('--output-dir', type=str, default='./data/pdfs', help='Output directory')
    parser.add_argument('--annotations-dir', type=str, default='./data/annotations', help='Annotations directory')

    args = parser.parse_args()

    print("="*60)
    print("Generating Additional Medical Documents")
    print("="*60)

    output_dir = Path(args.output_dir)
    annotations_dir = Path(args.annotations_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    annotations_dir.mkdir(parents=True, exist_ok=True)

    generator = AdditionalDocumentsGenerator()

    document_types = [
        ('discharge_summary', generator.create_discharge_summary),
        ('radiology_report', generator.create_radiology_report),
        ('operative_report', generator.create_operative_report),
        ('pathology_report', generator.create_pathology_report),
        ('ed_note', generator.create_ed_note),
        ('consultation_note', generator.create_consultation_note),
        ('history_physical', generator.create_history_physical),
        ('referral_letter', generator.create_referral_letter),
        ('registration_form', generator.create_registration_form),
        ('immunization_record', generator.create_immunization_record),
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
        print("To generate full dataset, run without --samples-only flag:")
        print(f"  python {sys.argv[0]} --num-each 1000")


if __name__ == "__main__":
    main()
