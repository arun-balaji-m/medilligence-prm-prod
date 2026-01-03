from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import json
import uuid
from appointment_agent.app.database import get_db
from appointment_agent.app import crud, schemas
from appointment_agent.app.utils import ai_handler

router = APIRouter(prefix="/api/chat", tags=["ai-chat"])


@router.post("/message")
def chat_message(chat_msg: schemas.ChatMessage, db: Session = Depends(get_db)):
    """Process a chat message with AI agent"""

    # Generate session ID if not provided
    session_id = chat_msg.session_id or str(uuid.uuid4())

    # Process the message with AI
    ai_response = ai_handler.process_chat_message(chat_msg.message, session_id)

    # If AI wants to call a function, execute it
    while ai_response["type"] == "function_call":
        function_name = ai_response["function_name"]
        function_args = ai_response["function_args"]

        # Execute the function
        function_result = execute_function(function_name, function_args, db)

        # Send result back to AI
        ai_response = ai_handler.add_function_result(
            session_id,
            function_name,
            json.dumps(function_result)
        )

    return {
        "response": ai_response["content"],
        "session_id": session_id
    }


def execute_function(function_name: str, args: dict, db: Session):
    """Execute the requested function and return results"""

    try:
        if function_name == "getPatientDetails":
            patient = crud.get_patient_by_mobile(db, args["mobile_number"])
            if patient:
                return {
                    "success": True,
                    "data": {
                        "id": patient.id,
                        "patient_mrn": patient.patient_mrn,
                        "patient_name": patient.patient_name,
                        "dob": str(patient.dob) if patient.dob else None,
                        "gender": patient.gender,
                        "mobile_number": patient.mobile_number,
                        "email": patient.email
                    }
                }
            else:
                return {"success": False, "message": "Patient not found"}

        elif function_name == "getDoctorDepartmentDetails":
            doctors = crud.get_doctors_by_name_or_department(
                db,
                args.get("doctor_name"),
                args.get("specialization")
            )
            if doctors:
                return {
                    "success": True,
                    "data": [
                        {
                            "id": doc.id,
                            "doctor_name": doc.doctor_name,
                            "specialization": doc.specialization,
                            "doctor_login": doc.doctor_login
                        }
                        for doc in doctors
                    ]
                }
            else:
                return {"success": False, "message": "No doctors found"}

        elif function_name == "getAvailableSlots":
            date_obj = None
            if args.get("appointment_date"):
                date_obj = datetime.strptime(args["appointment_date"], "%Y-%m-%d").date()

            slots = crud.get_available_slots(
                db,
                args.get("doctor_id"),
                date_obj
            )

            if slots:
                from appointment_agent.app import models
                result_slots = []
                for slot in slots:
                    doctor = db.query(models.Doctor).filter(models.Doctor.id == slot.doctor_id).first()
                    result_slots.append({
                        "id": slot.id,
                        "doctor_id": slot.doctor_id,
                        "doctor_name": doctor.doctor_name if doctor else None,
                        "start_time": slot.start_time.isoformat(),
                        "end_time": slot.end_time.isoformat(),
                        "status": slot.status
                    })

                return {"success": True, "data": result_slots}
            else:
                return {"success": False, "message": "No available slots found"}

        elif function_name == "bookAnAppointment":
            appointment_date = datetime.fromisoformat(args["appointment_date"])

            appointment = crud.book_appointment(
                db,
                args["patient_id"],
                args["slot_id"],
                appointment_date
            )

            if appointment:
                return {
                    "success": True,
                    "data": {
                        "id": appointment.id,
                        "appointment_number": appointment.appointment_number,
                        "appointment_date": appointment.appointment_date.isoformat(),
                        "slot_id": appointment.slot_id,
                        "patient_id": appointment.patient_id
                    },
                    "message": f"Appointment booked successfully! Appointment number: {appointment.appointment_number}"
                }
            else:
                return {"success": False, "message": "Slot not available or booking failed"}

        elif function_name == "cancelAppointment":
            result = crud.cancel_appointment(db, args["appointment_id"])

            if result:
                return {"success": True, "message": "Appointment cancelled successfully"}
            else:
                return {"success": False, "message": "Appointment not found"}

        else:
            return {"success": False, "message": f"Unknown function: {function_name}"}

    except Exception as e:
        return {"success": False, "message": f"Error executing function: {str(e)}"}
