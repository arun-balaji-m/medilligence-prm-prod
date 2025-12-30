from sqlalchemy.orm import Session
from datetime import datetime, date
from . import models
from typing import Optional, List


def get_patient_by_mobile(db: Session, mobile_number: str):
    return db.query(models.Patient).filter(models.Patient.mobile_number == mobile_number).first()


def get_doctors_by_name_or_department(db: Session, doctor_name: Optional[str] = None,
                                      specialization: Optional[str] = None):
    query = db.query(models.Doctor)

    if doctor_name:
        query = query.filter(models.Doctor.doctor_name.ilike(f"%{doctor_name}%"))

    if specialization:
        query = query.filter(models.Doctor.specialization.ilike(f"%{specialization}%"))

    return query.all()


def get_available_slots(db: Session, doctor_id: Optional[int] = None, appointment_date: Optional[date] = None):
    query = db.query(models.ResourceCalendar).filter(models.ResourceCalendar.status == "AVAILABLE")

    if doctor_id:
        query = query.filter(models.ResourceCalendar.doctor_id == doctor_id)

    if appointment_date:
        start_of_day = datetime.combine(appointment_date, datetime.min.time())
        end_of_day = datetime.combine(appointment_date, datetime.max.time())
        query = query.filter(
            models.ResourceCalendar.start_time >= start_of_day,
            models.ResourceCalendar.start_time <= end_of_day
        )

    return query.all()


def book_appointment(db: Session, patient_id: int, slot_id: int, appointment_date: datetime):
    # Check if slot is available
    slot = db.query(models.ResourceCalendar).filter(
        models.ResourceCalendar.id == slot_id,
        models.ResourceCalendar.status == "AVAILABLE"
    ).first()

    if not slot:
        return None

    # Generate appointment number
    appointment_count = db.query(models.Appointment).count()
    appointment_number = f"APT{appointment_count + 1:06d}"

    # Create appointment
    appointment = models.Appointment(
        appointment_number=appointment_number,
        appointment_date=appointment_date,
        slot_id=slot_id,
        patient_id=patient_id
    )
    db.add(appointment)

    # Update slot status
    slot.status = "BOOKED"

    db.commit()
    db.refresh(appointment)

    return appointment


def cancel_appointment(db: Session, appointment_id: int):
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

    if not appointment:
        return None

    # Update slot status back to available
    slot = db.query(models.ResourceCalendar).filter(models.ResourceCalendar.id == appointment.slot_id).first()
    if slot:
        slot.status = "AVAILABLE"

    # Delete appointment
    db.delete(appointment)
    db.commit()

    return True


def get_appointments_by_patient(db: Session, patient_id: int):
    return db.query(models.Appointment).filter(models.Appointment.patient_id == patient_id).all()