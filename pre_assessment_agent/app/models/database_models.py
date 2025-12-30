"""
SQLAlchemy database models
"""

from sqlalchemy import Column, BigInteger, String, Date, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from pre_assessment_agent.app.database import Base


class Patient(Base):
    __tablename__ = "patient"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_mrn = Column(String)
    patient_name = Column(String)
    dob = Column(Date)
    gender = Column(String)
    mobile_number = Column(String, index=True)
    email = Column(String)

    # Relationships
    appointments = relationship("Appointment", back_populates="patient")
    pre_assessments = relationship("PreAssessment", back_populates="patient")


class Appointment(Base):
    __tablename__ = "appointment"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    appointment_number = Column(String)
    appointment_date = Column(DateTime)
    slot_id = Column(BigInteger)
    patient_id = Column(BigInteger, ForeignKey("patient.id"))

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    pre_assessments = relationship("PreAssessment", back_populates="appointment")


class PreAssessment(Base):
    __tablename__ = "pre_assessment"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    document = Column(JSON)
    patient_id = Column(BigInteger, ForeignKey("patient.id"))
    appointment_id = Column(BigInteger, ForeignKey("appointment.id"))
    created_at = Column(DateTime, default=datetime.now, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="pre_assessments")
    appointment = relationship("Appointment", back_populates="pre_assessments")