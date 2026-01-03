from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from pre_assessment_agent.app.models.database_models import PreAssessment


class AssessmentService:

    @staticmethod
    def create_assessment(
            db: Session,
            patient_id: int,
            appointment_id: Optional[int],
            document: Dict[str, Any]
    ) -> PreAssessment:
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
        return db.query(PreAssessment).filter(
            PreAssessment.id == assessment_id
        ).first()

    @staticmethod
    def get_assessment_by_appointment(
            db: Session,
            appointment_id: int
    ) -> Optional[PreAssessment]:
        return db.query(PreAssessment).filter(
            PreAssessment.appointment_id == appointment_id
        ).first()

    @staticmethod
    def get_assessments_by_patient(
            db: Session,
            patient_id: int,
            limit: int = 10
    ) -> list:
        return db.query(PreAssessment).filter(
            PreAssessment.patient_id == patient_id
        ).order_by(PreAssessment.created_at.desc()).limit(limit).all()