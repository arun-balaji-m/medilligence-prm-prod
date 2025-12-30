from sqlalchemy import Column, BigInteger, String, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base


class Patient(Base):
    __tablename__ = "patient"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_mrn = Column(String)
    patient_name = Column(String)
    dob = Column(Date)
    gender = Column(String)
    mobile_number = Column(String)
    email = Column(String)


class Doctor(Base):
    __tablename__ = "doctor"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    doctor_login = Column(String)
    doctor_name = Column(String)
    specialization = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ResourceCalendar(Base):
    __tablename__ = "resource_calender"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    doctor_id = Column(BigInteger, ForeignKey("doctor.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Appointment(Base):
    __tablename__ = "appointment"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    appointment_number = Column(String)
    appointment_date = Column(DateTime)
    slot_id = Column(BigInteger, ForeignKey("resource_calender.id"))
    patient_id = Column(BigInteger, ForeignKey("patient.id"))