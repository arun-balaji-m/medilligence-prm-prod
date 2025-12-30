##working version
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

# ##updated version
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from appointment_agent.app.database import get_db
# from appointment_agent.app import crud, schemas
# from appointment_agent.app.utils.ai_handler import process_chat_message, add_function_result, clear_session
# from datetime import datetime
# import uuid
# import json
#
# router = APIRouter(prefix="/api/chat", tags=["chat"])
#
#
# def execute_function(function_name: str, function_args: dict, db: Session):
#     """Execute the requested function and return result"""
#     try:
#         if function_name == "getPatientDetails":
#             patient = crud.get_patient_by_mobile(db, function_args["mobile_number"])
#             if patient:
#                 return json.dumps({
#                     "success": True,
#                     "data": {
#                         "id": patient.id,
#                         "patient_name": patient.patient_name,
#                         "patient_mrn": patient.patient_mrn,
#                         "dob": str(patient.dob) if patient.dob else None,
#                         "gender": patient.gender,
#                         "mobile_number": patient.mobile_number,
#                         "email": patient.email
#                     }
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "Patient not found"})
#
#         elif function_name == "getDoctorDepartmentDetails":
#             doctors = crud.get_doctors_by_name_or_department(
#                 db,
#                 function_args.get("doctor_name"),
#                 function_args.get("specialization")
#             )
#             if doctors:
#                 return json.dumps({
#                     "success": True,
#                     "data": [
#                         {
#                             "id": doc.id,
#                             "doctor_name": doc.doctor_name,
#                             "specialization": doc.specialization
#                         }
#                         for doc in doctors
#                     ]
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "No doctors found"})
#
#         elif function_name == "getAvailableSlots":
#             date_str = function_args["appointment_date"]
#             date_obj = datetime.strptime(date_str, "%Y-%m-%d")
#
#             slots = crud.get_available_slots(
#                 db,
#                 function_args.get("doctor_id"),
#                 None,
#                 date_obj
#             )
#
#             if slots:
#                 return json.dumps({
#                     "success": True,
#                     "data": [
#                         {
#                             "id": slot.id,
#                             "doctor_id": slot.doctor_id,
#                             "doctor_name": slot.doctor.doctor_name if slot.doctor else None,
#                             "specialization": slot.doctor.specialization if slot.doctor else None,
#                             "start_time": slot.start_time.isoformat(),
#                             "end_time": slot.end_time.isoformat(),
#                             "status": slot.status
#                         }
#                         for slot in slots
#                     ]
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "No available slots found"})
#
#         elif function_name == "bookAnAppointment":
#             appointment_date = datetime.fromisoformat(function_args["appointment_date"])
#             appointment, error = crud.book_appointment(
#                 db,
#                 function_args["patient_id"],
#                 function_args["slot_id"],
#                 appointment_date
#             )
#
#             if error:
#                 return json.dumps({"success": False, "message": error})
#
#             return json.dumps({
#                 "success": True,
#                 "data": {
#                     "id": appointment.id,
#                     "appointment_number": appointment.appointment_number,
#                     "appointment_date": appointment.appointment_date.isoformat(),
#                     "slot_id": appointment.slot_id,
#                     "patient_id": appointment.patient_id
#                 }
#             })
#
#         elif function_name == "cancelAppointment":
#             success, error = crud.cancel_appointment(db, function_args["appointment_id"])
#
#             if error:
#                 return json.dumps({"success": False, "message": error})
#
#             return json.dumps({"success": True, "message": "Appointment cancelled successfully"})
#
#         else:
#             return json.dumps({"success": False, "message": f"Unknown function: {function_name}"})
#
#     except Exception as e:
#         return json.dumps({"success": False, "message": f"Error: {str(e)}"})
#
#
# @router.post("/message", response_model=schemas.ChatMessage)
# def chat_message(chat_input: schemas.ChatMessage, db: Session = Depends(get_db)):
#     """Process a chat message and return AI response"""
#     try:
#         # Generate or use existing session ID
#         session_id = chat_input.session_id or str(uuid.uuid4())
#
#         # Process message with AI
#         result = process_chat_message(chat_input.message, session_id)
#
#         # Handle function calls
#         while result["type"] == "function_call":
#             function_name = result["function_name"]
#             function_args = result["function_args"]
#
#             # Execute the function
#             function_result = execute_function(function_name, function_args, db)
#
#             # Send result back to AI and get next response
#             result = add_function_result(session_id, function_name, function_result)
#
#         # Return final text response
#         return schemas.ChatResponse(
#             response=result["content"],
#             session_id=session_id
#         )
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.delete("/session/{session_id}")
# def clear_chat_session(session_id: str):
#     """Clear a chat session"""
#     clear_session(session_id)
#     return {"message": "Session cleared"}


##third version
#
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from appointment_agent.app.database import get_db
# from appointment_agent.app import crud, schemas
# from appointment_agent.app.utils.ai_handler import process_chat_message, add_function_result, clear_session
# from datetime import datetime
# import uuid
# import json
#
# router = APIRouter(prefix="/api/chat", tags=["chat"])
#
#
# def execute_function(function_name: str, function_args: dict, db: Session):
#     """Execute the requested function and return result"""
#     try:
#         if function_name == "getPatientDetails":
#             patient = crud.get_patient_by_mobile(db, function_args["mobile_number"])
#             if patient:
#                 return json.dumps({
#                     "success": True,
#                     "data": {
#                         "id": patient.id,
#                         "patient_name": patient.patient_name,
#                         "patient_mrn": patient.patient_mrn,
#                         "dob": str(patient.dob) if patient.dob else None,
#                         "gender": patient.gender,
#                         "mobile_number": patient.mobile_number,
#                         "email": patient.email
#                     }
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "Patient not found"})
#
#         elif function_name == "getDoctorDepartmentDetails":
#             doctors = crud.get_doctors_by_name_or_department(
#                 db,
#                 function_args.get("doctor_name"),
#                 function_args.get("specialization")
#             )
#             if doctors:
#                 return json.dumps({
#                     "success": True,
#                     "data": [
#                         {
#                             "id": doc.id,
#                             "doctor_name": doc.doctor_name,
#                             "specialization": doc.specialization
#                         }
#                         for doc in doctors
#                     ]
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "No doctors found"})
#
#         elif function_name == "getAvailableSlots":
#             date_str = function_args["appointment_date"]
#             date_obj = datetime.strptime(date_str, "%Y-%m-%d")
#
#             slots = crud.get_available_slots(
#                 db,
#                 function_args.get("doctor_id"),
#                 None,
#                 date_obj
#             )
#
#             if slots:
#                 return json.dumps({
#                     "success": True,
#                     "data": [
#                         {
#                             "id": slot.id,
#                             "doctor_id": slot.doctor_id,
#                             "doctor_name": slot.doctor.doctor_name if slot.doctor else None,
#                             "specialization": slot.doctor.specialization if slot.doctor else None,
#                             "start_time": slot.start_time.isoformat(),
#                             "end_time": slot.end_time.isoformat(),
#                             "status": slot.status
#                         }
#                         for slot in slots
#                     ]
#                 })
#             else:
#                 return json.dumps({"success": False, "message": "No available slots found"})
#
#         elif function_name == "bookAnAppointment":
#             appointment_date = datetime.fromisoformat(function_args["appointment_date"])
#             appointment, error = crud.book_appointment(
#                 db,
#                 function_args["patient_id"],
#                 function_args["slot_id"],
#                 appointment_date
#             )
#
#             if error:
#                 return json.dumps({"success": False, "message": error})
#
#             return json.dumps({
#                 "success": True,
#                 "data": {
#                     "id": appointment.id,
#                     "appointment_number": appointment.appointment_number,
#                     "appointment_date": appointment.appointment_date.isoformat(),
#                     "slot_id": appointment.slot_id,
#                     "patient_id": appointment.patient_id
#                 },
#                 "message": f"Appointment booked successfully! Your appointment number is {appointment.appointment_number}"
#             })
#
#         elif function_name == "cancelAppointment":
#             success, error = crud.cancel_appointment(db, function_args["appointment_id"])
#
#             if error:
#                 return json.dumps({"success": False, "message": error})
#
#             return json.dumps({"success": True, "message": "Appointment cancelled successfully"})
#
#         else:
#             return json.dumps({"success": False, "message": f"Unknown function: {function_name}"})
#
#     except Exception as e:
#         print(f"Error executing function {function_name}: {e}")
#         import traceback
#         traceback.print_exc()
#         return json.dumps({"success": False, "message": f"Error: {str(e)}"})
#
#
# @router.post("/message", response_model=schemas.ChatMessage)
# def chat_message(chat_input: schemas.ChatMessage, db: Session = Depends(get_db)):
#     """Process a chat message and return AI response"""
#     try:
#         # Generate or use existing session ID
#         session_id = chat_input.session_id or str(uuid.uuid4())
#
#         print(f"Processing message: '{chat_input.message}' for session: {session_id}")
#
#         # Process message with AI
#         result = process_chat_message(chat_input.message, session_id)
#
#         print(f"AI result type: {result['type']}")
#
#         # Handle function calls in a loop
#         max_iterations = 10  # Prevent infinite loops
#         iteration = 0
#
#         while result["type"] == "function_call" and iteration < max_iterations:
#             iteration += 1
#             function_name = result["function_name"]
#             function_args = result["function_args"]
#
#             print(f"Iteration {iteration}: Calling function '{function_name}' with args: {function_args}")
#
#             # Execute the function
#             function_result = execute_function(function_name, function_args, db)
#             print(f"Function result: {function_result}")
#
#             # Send result back to AI and get next response
#             result = add_function_result(session_id, function_name, function_result)
#             print(f"Next result type: {result['type']}")
#
#         if iteration >= max_iterations:
#             print("Warning: Max iterations reached")
#
#         # Return final text response
#         print(f"Final response: {result['content']}")
#
#         return schemas.ChatMessage(
#             response=result["content"],
#             session_id=session_id
#         )
#
#     except Exception as e:
#         print(f"Error in chat_message: {e}")
#         import traceback
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.delete("/session/{session_id}")
# def clear_chat_session(session_id: str):
#     """Clear a chat session"""
#     clear_session(session_id)
#     return {"message": "Session cleared"}