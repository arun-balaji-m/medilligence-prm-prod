from sqlalchemy.orm import Session
from patient_fao_agent.app.models.database_models import Patient
from patient_fao_agent.app.models.schema_models import PatientVerifyResponse
from fastapi import HTTPException


class PatientService:
    def __init__(self, db: Session):
        self.db = db

    async def verify_patient(self, mobile_number: str) -> PatientVerifyResponse:
        """Verify patient by mobile number"""
        try:
            patient = self.db.query(Patient).filter(
                Patient.mobile_number == mobile_number
            ).first()

            if patient:
                return PatientVerifyResponse(
                    verified=True,
                    patient_id=patient.id,
                    patient_name=patient.patient_name,
                    message="Patient verified successfully"
                )
            else:
                return PatientVerifyResponse(
                    verified=False,
                    message="Patient not found. Please check your mobile number."
                )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error verifying patient: {str(e)}")

    async def get_patient_by_id(self, patient_id: int) -> Patient:
        """Get patient by ID"""
        patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient