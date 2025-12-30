# from sqlalchemy.orm import Session
# from ..models.database_models import Appointment
# from datetime import datetime, timedelta
# from typing import Optional, Dict, Any
#
#
# class AppointmentService:
#     @staticmethod
#     def get_doctor_from_appointment(db: Session, appointment_id: int) -> Optional[int]:
#         """Get doctor_id from appointment"""
#         appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
#         return appointment.doctor_id if appointment else None
#
#     @staticmethod
#     def suggest_early_appointment_date() -> datetime:
#         """Suggest an appointment date within next 3-5 days"""
#         # Suggest appointment 3 days from now
#         suggested_date = datetime.now() + timedelta(days=3)
#
#         # Skip weekends (Saturday=5, Sunday=6)
#         while suggested_date.weekday() >= 5:
#             suggested_date += timedelta(days=1)
#
#         # Set time to 10:00 AM
#         suggested_date = suggested_date.replace(hour=10, minute=0, second=0, microsecond=0)
#
#         return suggested_date
#
#     @staticmethod
#     def create_early_followup_appointment(
#             db: Session,
#             patient_id: int,
#             doctor_id: int,
#             appointment_date: str
#     ) -> Optional[Dict[str, Any]]:
#         """Create an early follow-up appointment"""
#         try:
#             appointment_datetime = datetime.fromisoformat(appointment_date)
#             appointment_number = f"EF-{patient_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
#
#             new_appointment = Appointment(
#                 appointment_number=appointment_number,
#                 patient_id=patient_id,
#                 doctor_id=doctor_id,
#                 appointment_date=appointment_datetime,
#                 appointment_status="scheduled"
#             )
#
#             db.add(new_appointment)
#             db.commit()
#             db.refresh(new_appointment)
#
#             return {
#                 "appointment_number": new_appointment.appointment_number,
#                 "appointment_date": new_appointment.appointment_date.strftime("%B %d, %Y at %I:%M %p"),
#                 "appointment_id": new_appointment.id
#             }
#         except Exception as e:
#             db.rollback()
#             print(f"Error creating appointment: {e}")
#             return None

#second screen
#
# from sqlalchemy.orm import Session
# from ..models.database_models import Appointment
# from datetime import datetime, timedelta
# from typing import Optional, Dict, Any
#
#
# class AppointmentService:
#     @staticmethod
#     def get_doctor_from_appointment(db: Session, appointment_id: int) -> Optional[int]:
#         """Get doctor_id from appointment"""
#         appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
#         return appointment.doctor_id if appointment else None
#
#     @staticmethod
#     def suggest_early_appointment_date() -> datetime:
#         """Suggest an appointment date within next 3-5 days"""
#         # Suggest appointment 3 days from now
#         suggested_date = datetime.now() + timedelta(days=3)
#
#         # Skip weekends (Saturday=5, Sunday=6)
#         while suggested_date.weekday() >= 5:
#             suggested_date += timedelta(days=1)
#
#         # Set time to 10:00 AM
#         suggested_date = suggested_date.replace(hour=10, minute=0, second=0, microsecond=0)
#
#         return suggested_date
#
#     @staticmethod
#     def create_early_followup_appointment(
#             db: Session,
#             patient_id: int,
#             doctor_id: int,
#             appointment_date: str
#     ) -> Optional[Dict[str, Any]]:
#         """Create an early follow-up appointment"""
#         try:
#             appointment_datetime = datetime.fromisoformat(appointment_date)
#             appointment_number = f"EF-{patient_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
#
#             new_appointment = Appointment(
#                 appointment_number=appointment_number,
#                 patient_id=patient_id,
#                 doctor_id=doctor_id,
#                 appointment_date=appointment_datetime,
#                 appointment_status="scheduled"
#             )
#
#             db.add(new_appointment)
#             db.commit()
#             db.refresh(new_appointment)
#
#             return {
#                 "appointment_number": new_appointment.appointment_number,
#                 "appointment_date": new_appointment.appointment_date.strftime("%B %d, %Y at %I:%M %p"),
#                 "appointment_id": new_appointment.id
#             }
#         except Exception as e:
#             db.rollback()
#             print(f"Error creating appointment: {e}")
#             return None


from sqlalchemy.orm import Session
from ..models.database_models import Appointment
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class AppointmentService:
    @staticmethod
    def get_doctor_from_appointment(db: Session, appointment_id: int) -> Optional[int]:
        """Get doctor_id from appointment"""
        appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
        return appointment.doctor_id if appointment else None

    @staticmethod
    def suggest_early_appointment_date() -> datetime:
        """Suggest an appointment date within next 3-5 days"""
        # Suggest appointment 3 days from now
        suggested_date = datetime.now() + timedelta(days=3)

        # Skip weekends (Saturday=5, Sunday=6)
        while suggested_date.weekday() >= 5:
            suggested_date += timedelta(days=1)

        # Set time to 10:00 AM
        suggested_date = suggested_date.replace(hour=10, minute=0, second=0, microsecond=0)

        return suggested_date

    @staticmethod
    def create_early_followup_appointment(
            db: Session,
            patient_id: int,
            doctor_id: int,
            appointment_date: str
    ) -> Optional[Dict[str, Any]]:
        """Create an early follow-up appointment"""
        try:
            appointment_datetime = datetime.fromisoformat(appointment_date)
            appointment_number = f"EF-{patient_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            new_appointment = Appointment(
                appointment_number=appointment_number,
                patient_id=patient_id,
                doctor_id=doctor_id,
                appointment_date=appointment_datetime,
                appointment_status="scheduled"
            )

            db.add(new_appointment)
            db.commit()
            db.refresh(new_appointment)

            return {
                "appointment_number": new_appointment.appointment_number,
                "appointment_date": new_appointment.appointment_date.strftime("%B %d, %Y at %I:%M %p"),
                "appointment_id": new_appointment.id
            }
        except Exception as e:
            db.rollback()
            print(f"Error creating appointment: {e}")
            return None
