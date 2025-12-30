from sqlalchemy import Column, BigInteger, String, Date, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from patient_referral_agent.app.database import Base


class Patient(Base):
    __tablename__ = "patient"

    # Use server_default to let PostgreSQL handle ID generation completely
    id = Column(BigInteger, primary_key=True, server_default=func.nextval('patient_id_seq'))
    patient_mrn = Column(String)
    patient_name = Column(String)
    dob = Column(Date)
    gender = Column(String)
    mobile_number = Column(String)
    email = Column(String)


class ReferralPatient(Base):
    __tablename__ = "referral_patient"

    # Use server_default to let PostgreSQL handle ID generation completely
    id = Column(BigInteger, primary_key=True, server_default=func.nextval('referral_patient_id_seq'))
    patient_id = Column(BigInteger, ForeignKey("patient.id"))
    document_number = Column(String)
    refferral_document = Column(JSONB)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())