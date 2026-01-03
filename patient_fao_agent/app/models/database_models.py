from sqlalchemy import Column, BigInteger, String, Date, TIMESTAMP, ForeignKey, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from patient_fao_agent.app.database import Base


class Patient(Base):
    __tablename__ = "patient"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_mrn = Column(String)
    patient_name = Column(String)
    dob = Column(Date)
    gender = Column(String)
    mobile_number = Column(String)
    email = Column(String)
    ai_chat_history = relationship("AIChatHistory", back_populates="patient")


class AIChatHistory(Base):
    __tablename__ = "ai_chat_history"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    document_number = Column(String)
    document = Column(JSONB)
    patient_id = Column(BigInteger, ForeignKey("patient.id"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("now()"))
    patient = relationship("Patient", back_populates="ai_chat_history")