# from sqlalchemy import Column, BigInteger, String, Date, DateTime, ForeignKey, JSON
# from sqlalchemy.dialects.postgresql import JSONB
# from sqlalchemy.sql import func
# from ..database import Base
#
#
# class Patient(Base):
#     __tablename__ = "patient"
#
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     patient_mrn = Column(String)
#     patient_name = Column(String)
#     dob = Column(Date)
#     gender = Column(String)
#     mobile_number = Column(String)
#     email = Column(String)
#
#
# class Consultation(Base):
#     __tablename__ = "consultation"
#
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     consultation_number = Column(String)
#     consultation_date = Column(DateTime)
#     patient_id = Column(BigInteger, ForeignKey("patient.id"))
#     appointment_id = Column(BigInteger)
#     consultation_status = Column(String)
#     medication_id = Column(BigInteger, ForeignKey("medication.id"))
#     follow_up = Column(String)
#     created_at = Column(DateTime, server_default=func.now())
#
#
# class Medication(Base):
#     __tablename__ = "medication"
#
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     document_number = Column(String)
#     document = Column(JSONB)
#     created_at = Column(DateTime, server_default=func.now())
#
#
# class FollowUpAdherence(Base):
#     __tablename__ = "follow_up_adherence"
#
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     document_number = Column(String)
#     document = Column(JSON)
#     consultation_id = Column(BigInteger, ForeignKey("consultation.id"))
#     status = Column(String)
#     created_at = Column(DateTime, server_default=func.now())


# #second version
# from sqlalchemy import Column, BigInteger, String, Date, DateTime, ForeignKey, JSON
# from sqlalchemy.dialects.postgresql import JSONB
# from sqlalchemy.sql import func
# from ..database import Base
#
#
# class Patient(Base):
#     __tablename__ = "patient"
#
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     patient_mrn = Column(String)
#     patient_name = Column(String)
#     dob = Column(Date)
#     gender = Column(String)
#     mobile_number = Column(String)
#     email = Column(String)
#
#
# class Consultation(Base):
#     __tablename__ = "consultation"
#
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     consultation_number = Column(String)
#     consultation_date = Column(DateTime)
#     patient_id = Column(BigInteger, ForeignKey("patient.id"))
#     appointment_id = Column(BigInteger, ForeignKey("appointment.id"))
#     consultation_status = Column(String)
#     medication_id = Column(BigInteger, ForeignKey("medication.id"))
#     follow_up = Column(String)
#     created_at = Column(DateTime, server_default=func.now())
#
#
# class Appointment(Base):
#     __tablename__ = "appointment"
#
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     appointment_number = Column(String)
#     patient_id = Column(BigInteger, ForeignKey("patient.id"))
#     doctor_id = Column(BigInteger)
#     appointment_date = Column(DateTime)
#     appointment_status = Column(String)
#     created_at = Column(DateTime, server_default=func.now())
#
#
# class Medication(Base):
#     __tablename__ = "medication"
#
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     document_number = Column(String)
#     document = Column(JSONB)
#     created_at = Column(DateTime, server_default=func.now())
#
#
# class FollowUpAdherence(Base):
#     __tablename__ = "follow_up_adherence"
#
#     id = Column(BigInteger, primary_key=True, autoincrement=True)
#     document_number = Column(String)
#     document = Column(JSON)
#     consultation_id = Column(BigInteger, ForeignKey("consultation.id"))
#     status = Column(String)
#     created_at = Column(DateTime, server_default=func.now())
#


from sqlalchemy import Column, BigInteger, String, Date, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from ..database import Base


class Patient(Base):
    __tablename__ = "patient"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_mrn = Column(String)
    patient_name = Column(String)
    dob = Column(Date)
    gender = Column(String)
    mobile_number = Column(String)
    email = Column(String)


class Consultation(Base):
    __tablename__ = "consultation"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    consultation_number = Column(String)
    consultation_date = Column(DateTime)
    patient_id = Column(BigInteger, ForeignKey("patient.id"))
    appointment_id = Column(BigInteger, ForeignKey("appointment.id"))
    consultation_status = Column(String)
    medication_id = Column(BigInteger, ForeignKey("medication.id"))
    follow_up = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class Appointment(Base):
    __tablename__ = "appointment"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    appointment_number = Column(String)
    patient_id = Column(BigInteger, ForeignKey("patient.id"))
    doctor_id = Column(BigInteger)
    appointment_date = Column(DateTime)
    appointment_status = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class Medication(Base):
    __tablename__ = "medication"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    document_number = Column(String)
    document = Column(JSONB)
    created_at = Column(DateTime, server_default=func.now())


class FollowUpAdherence(Base):
    __tablename__ = "follow_up_adherence"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    document_number = Column(String)
    document = Column(JSON)
    consultation_id = Column(BigInteger, ForeignKey("consultation.id"))
    status = Column(String)
    created_at = Column(DateTime, server_default=func.now())
