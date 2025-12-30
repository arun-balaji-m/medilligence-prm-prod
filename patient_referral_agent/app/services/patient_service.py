from sqlalchemy.orm import Session
from patient_referral_agent.app.models.database_models import Patient, ReferralPatient
from patient_referral_agent.app.models.schema_models import PatientCreate
from datetime import datetime


class PatientService:
    @staticmethod
    def create_patient(db: Session, patient_data: PatientCreate) -> Patient:
        patient_mrn = f"MRN{datetime.now().strftime('%Y%m%d%H%M%S')}"

        patient = Patient(
            patient_mrn=patient_mrn,
            patient_name=patient_data.patient_name,
            dob=patient_data.dob,
            gender=patient_data.gender,
            mobile_number=patient_data.mobile_number,
            email=patient_data.email
        )

        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    @staticmethod
    def get_patient(db: Session, patient_id: int) -> Patient:
        return db.query(Patient).filter(Patient.id == patient_id).first()

    @staticmethod
    def create_referral(db: Session, patient_id: int, document_data: dict, doc_number: str = None) -> ReferralPatient:
        if not doc_number:
            doc_number = f"REF{datetime.now().strftime('%Y%m%d%H%M%S')}"

        referral = ReferralPatient(
            patient_id=patient_id,
            document_number=doc_number,
            refferral_document=document_data
        )

        db.add(referral)
        db.commit()
        db.refresh(referral)
        return referral

    @staticmethod
    def get_referral(db: Session, patient_id: int) -> ReferralPatient:
        return db.query(ReferralPatient).filter(
            ReferralPatient.patient_id == patient_id
        ).first()

    @staticmethod
    def update_referral(db: Session, patient_id: int, updated_data: dict):
        referral = db.query(ReferralPatient).filter(
            ReferralPatient.patient_id == patient_id
        ).first()

        if referral:
            referral.refferral_document = updated_data
            db.commit()
            db.refresh(referral)
        return referral