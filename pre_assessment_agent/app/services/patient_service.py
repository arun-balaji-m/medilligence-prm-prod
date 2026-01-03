from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import Optional, Tuple
from datetime import datetime
from pre_assessment_agent.app.models.database_models import Patient, Appointment


class PatientService:
    @staticmethod
    def get_patient_by_mobile(db: Session, mobile_number: str) -> Optional[Patient]:
        return db.query(Patient).filter(
            Patient.mobile_number == mobile_number
        ).first()

    @staticmethod
    def get_patient_by_id(db: Session, patient_id: int) -> Optional[Patient]:
        return db.query(Patient).filter(Patient.id == patient_id).first()

    @staticmethod
    def get_upcoming_appointment(db: Session, patient_id: int) -> Optional[Appointment]:
        now = datetime.now()

        # Get appointments scheduled for today or future
        appointment = db.query(Appointment).filter(
            and_(
                Appointment.patient_id == patient_id,
                Appointment.appointment_date >= now
            )
        ).order_by(Appointment.appointment_date).first()

        return appointment

    @staticmethod
    def get_latest_appointment(db: Session, patient_id: int) -> Optional[Appointment]:
        return db.query(Appointment).filter(
            Appointment.patient_id == patient_id
        ).order_by(desc(Appointment.appointment_date)).first()

    @staticmethod
    def verify_patient_and_get_details(
            db: Session,
            mobile_number: str
    ) -> Tuple[Optional[Patient], Optional[Appointment]]:
        # Get patient
        patient = PatientService.get_patient_by_mobile(db, mobile_number)

        if not patient:
            return None, None

        # Try to get upcoming appointment first, fallback to latest
        appointment = PatientService.get_upcoming_appointment(db, patient.id)

        if not appointment:
            appointment = PatientService.get_latest_appointment(db, patient.id)

        return patient, appointment