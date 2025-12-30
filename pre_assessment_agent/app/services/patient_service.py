"""
Service layer for patient and appointment operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import Optional, Tuple
from datetime import datetime
from pre_assessment_agent.app.models.database_models import Patient, Appointment


class PatientService:
    """Handle patient-related database operations"""

    @staticmethod
    def get_patient_by_mobile(db: Session, mobile_number: str) -> Optional[Patient]:
        """
        Fetch patient by mobile number

        Args:
            db: Database session
            mobile_number: Patient's mobile number

        Returns:
            Patient object or None
        """
        return db.query(Patient).filter(
            Patient.mobile_number == mobile_number
        ).first()

    @staticmethod
    def get_patient_by_id(db: Session, patient_id: int) -> Optional[Patient]:
        """
        Fetch patient by ID

        Args:
            db: Database session
            patient_id: Patient ID

        Returns:
            Patient object or None
        """
        return db.query(Patient).filter(Patient.id == patient_id).first()

    @staticmethod
    def get_upcoming_appointment(db: Session, patient_id: int) -> Optional[Appointment]:
        """
        Get the next upcoming appointment for a patient

        Args:
            db: Database session
            patient_id: Patient ID

        Returns:
            Appointment object or None
        """
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
        """
        Get the most recent appointment for a patient

        Args:
            db: Database session
            patient_id: Patient ID

        Returns:
            Appointment object or None
        """
        return db.query(Appointment).filter(
            Appointment.patient_id == patient_id
        ).order_by(desc(Appointment.appointment_date)).first()

    @staticmethod
    def verify_patient_and_get_details(
            db: Session,
            mobile_number: str
    ) -> Tuple[Optional[Patient], Optional[Appointment]]:
        """
        Verify patient by mobile number and fetch their appointment

        Args:
            db: Database session
            mobile_number: Patient's mobile number

        Returns:
            Tuple of (Patient, Appointment) or (None, None)
        """
        # Get patient
        patient = PatientService.get_patient_by_mobile(db, mobile_number)

        if not patient:
            return None, None

        # Try to get upcoming appointment first, fallback to latest
        appointment = PatientService.get_upcoming_appointment(db, patient.id)

        if not appointment:
            appointment = PatientService.get_latest_appointment(db, patient.id)

        return patient, appointment