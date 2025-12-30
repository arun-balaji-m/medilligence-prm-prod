"""
Service layer for pre-assessment operations
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from pre_assessment_agent.app.models.database_models import PreAssessment


class AssessmentService:
    """Handle pre-assessment database operations"""

    @staticmethod
    def create_assessment(
            db: Session,
            patient_id: int,
            appointment_id: Optional[int],
            document: Dict[str, Any]
    ) -> PreAssessment:
        """
        Create a new pre-assessment record

        Args:
            db: Database session
            patient_id: Patient ID
            appointment_id: Appointment ID (optional)
            document: Assessment data as JSON

        Returns:
            Created PreAssessment object
        """
        assessment = PreAssessment(
            patient_id=patient_id,
            appointment_id=appointment_id,
            document=document,
            created_at=datetime.now()
        )

        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        return assessment

    @staticmethod
    def update_assessment(
            db: Session,
            assessment_id: int,
            document: Dict[str, Any]
    ) -> Optional[PreAssessment]:
        """
        Update an existing pre-assessment record

        Args:
            db: Database session
            assessment_id: Assessment ID
            document: Updated assessment data

        Returns:
            Updated PreAssessment object or None
        """
        assessment = db.query(PreAssessment).filter(
            PreAssessment.id == assessment_id
        ).first()

        if assessment:
            assessment.document = document
            db.commit()
            db.refresh(assessment)

        return assessment

    @staticmethod
    def get_assessment_by_id(
            db: Session,
            assessment_id: int
    ) -> Optional[PreAssessment]:
        """
        Get assessment by ID

        Args:
            db: Database session
            assessment_id: Assessment ID

        Returns:
            PreAssessment object or None
        """
        return db.query(PreAssessment).filter(
            PreAssessment.id == assessment_id
        ).first()

    @staticmethod
    def get_assessment_by_appointment(
            db: Session,
            appointment_id: int
    ) -> Optional[PreAssessment]:
        """
        Get assessment for a specific appointment

        Args:
            db: Database session
            appointment_id: Appointment ID

        Returns:
            PreAssessment object or None
        """
        return db.query(PreAssessment).filter(
            PreAssessment.appointment_id == appointment_id
        ).first()

    @staticmethod
    def get_assessments_by_patient(
            db: Session,
            patient_id: int,
            limit: int = 10
    ) -> list:
        """
        Get all assessments for a patient

        Args:
            db: Database session
            patient_id: Patient ID
            limit: Maximum number of records to return

        Returns:
            List of PreAssessment objects
        """
        return db.query(PreAssessment).filter(
            PreAssessment.patient_id == patient_id
        ).order_by(PreAssessment.created_at.desc()).limit(limit).all()