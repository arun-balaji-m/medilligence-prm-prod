from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
from appointment_agent.app.database import get_db
from appointment_agent.app import crud, schemas, models

router = APIRouter(prefix="/api", tags=["appointments"])


@router.get("/patient/{mobile_number}", response_model=schemas.PatientResponse)
def get_patient_details(mobile_number: str, db: Session = Depends(get_db)):
    """Get patient details by mobile number"""
    patient = crud.get_patient_by_mobile(db, mobile_number)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/doctors", response_model=List[schemas.DoctorResponse])
def get_doctor_department_details(
        doctor_name: Optional[str] = None,
        specialization: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Get doctor details by name or department"""
    if not doctor_name and not specialization:
        raise HTTPException(status_code=400, detail="Provide either doctor_name or specialization")

    doctors = crud.get_doctors_by_name_or_department(db, doctor_name, specialization)
    if not doctors:
        raise HTTPException(status_code=404, detail="No doctors found")
    return doctors


@router.get("/slots", response_model=List[schemas.SlotResponse])
def get_available_slots(
        doctor_id: Optional[int] = None,
        appointment_date: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Get available slots for a doctor on a specific date"""
    date_obj = None
    if appointment_date:
        try:
            date_obj = datetime.strptime(appointment_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    slots = crud.get_available_slots(db, doctor_id, date_obj)

    # Enrich with doctor name
    result = []
    for slot in slots:
        doctor = db.query(models.Doctor).filter(models.Doctor.id == slot.doctor_id).first()
        slot_dict = {
            "id": slot.id,
            "doctor_id": slot.doctor_id,
            "doctor_name": doctor.doctor_name if doctor else None,
            "start_time": slot.start_time,
            "end_time": slot.end_time,
            "status": slot.status
        }
        result.append(schemas.SlotResponse(**slot_dict))

    return result


@router.post("/appointments", response_model=schemas.AppointmentResponse)
def book_appointment(appointment_data: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    """Book an appointment"""
    appointment = crud.book_appointment(
        db,
        appointment_data.patient_id,
        appointment_data.slot_id,
        appointment_data.appointment_date
    )

    if not appointment:
        raise HTTPException(status_code=400, detail="Slot not available or booking failed")

    return appointment


@router.delete("/appointments/{appointment_id}")
def cancel_appointment(appointment_id: int, db: Session = Depends(get_db)):
    """Cancel an appointment"""
    result = crud.cancel_appointment(db, appointment_id)

    if not result:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return {"message": "Appointment cancelled successfully"}


@router.get("/appointments/patient/{patient_id}", response_model=List[schemas.AppointmentResponse])
def get_patient_appointments(patient_id: int, db: Session = Depends(get_db)):
    """Get all appointments for a patient"""
    appointments = crud.get_appointments_by_patient(db, patient_id)
    return appointments