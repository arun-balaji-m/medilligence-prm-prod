# from sqlalchemy.orm import Session
# from sqlalchemy import desc
# from ..models.database_models import Patient, Consultation, Medication
# from typing import Optional, Dict, Any
#
#
# class PatientService:
#     @staticmethod
#     def get_patient_by_mobile(db: Session, mobile_number: str) -> Optional[Patient]:
#         return db.query(Patient).filter(Patient.mobile_number == mobile_number).first()
#
#     @staticmethod
#     def get_latest_consultation(db: Session, patient_id: int) -> Optional[Dict[str, Any]]:
#         consultation = db.query(Consultation).filter(
#             Consultation.patient_id == patient_id
#         ).order_by(desc(Consultation.consultation_date)).first()
#
#         if not consultation:
#             return None
#
#         medication_doc = None
#         if consultation.medication_id:
#             medication = db.query(Medication).filter(
#                 Medication.id == consultation.medication_id
#             ).first()
#             if medication:
#                 medication_doc = medication.document
#
#         return {
#             "id": consultation.id,
#             "consultation_number": consultation.consultation_number,
#             "consultation_date": consultation.consultation_date,
#             "medication_id": consultation.medication_id,
#             "medication_document": medication_doc
#         }

# #Second version
# from sqlalchemy.orm import Session
# from sqlalchemy import desc
# from ..models.database_models import Patient, Consultation, Medication
# from typing import Optional, Dict, Any
#
#
# class PatientService:
#     @staticmethod
#     def get_patient_by_mobile(db: Session, mobile_number: str) -> Optional[Patient]:
#         return db.query(Patient).filter(Patient.mobile_number == mobile_number).first()
#
#     @staticmethod
#     def get_latest_consultation(db: Session, patient_id: int) -> Optional[Dict[str, Any]]:
#         consultation = db.query(Consultation).filter(
#             Consultation.patient_id == patient_id
#         ).order_by(desc(Consultation.consultation_date)).first()
#
#         if not consultation:
#             return None
#
#         medication_doc = None
#         if consultation.medication_id:
#             medication = db.query(Medication).filter(
#                 Medication.id == consultation.medication_id
#             ).first()
#             if medication:
#                 medication_doc = medication.document
#
#         return {
#             "id": consultation.id,
#             "consultation_number": consultation.consultation_number,
#             "consultation_date": consultation.consultation_date,
#             "medication_id": consultation.medication_id,
#             "medication_document": medication_doc,
#             "follow_up": consultation.follow_up,
#             "appointment_id": consultation.appointment_id
#         }
#
#     @staticmethod
#     def format_medication_list(medication_doc: Dict[str, Any]) -> str:
#         """Format medication document into readable list"""
#         if not medication_doc:
#             return ""
#
#         medications = medication_doc.get("medications", [])
#         if not medications:
#             return ""
#
#         med_list = []
#         for idx, med in enumerate(medications, 1):
#             med_name = med.get("name", "Unknown medication")
#             dosage = med.get("dosage", "")
#             frequency = med.get("frequency", "")
#             duration = med.get("duration", "")
#
#             med_str = f"{idx}. {med_name}"
#             if dosage:
#                 med_str += f" - {dosage}"
#             if frequency:
#                 med_str += f", {frequency}"
#             if duration:
#                 med_str += f", for {duration}"
#
#             med_list.append(med_str)
#
#         return "\n".join(med_list)
#

#thrid version
#
# from sqlalchemy.orm import Session
# from sqlalchemy import desc
# from ..models.database_models import Patient, Consultation, Medication
# from typing import Optional, Dict, Any
#
#
# class PatientService:
#     @staticmethod
#     def get_patient_by_mobile(db: Session, mobile_number: str) -> Optional[Patient]:
#         return db.query(Patient).filter(Patient.mobile_number == mobile_number).first()
#
#     @staticmethod
#     def get_latest_consultation(db: Session, patient_id: int) -> Optional[Dict[str, Any]]:
#         consultation = db.query(Consultation).filter(
#             Consultation.patient_id == patient_id
#         ).order_by(desc(Consultation.consultation_date)).first()
#
#         if not consultation:
#             return None
#
#         medication_doc = None
#         if consultation.medication_id:
#             medication = db.query(Medication).filter(
#                 Medication.id == consultation.medication_id
#             ).first()
#             if medication:
#                 medication_doc = medication.document
#
#         return {
#             "id": consultation.id,
#             "consultation_number": consultation.consultation_number,
#             "consultation_date": consultation.consultation_date,
#             "medication_id": consultation.medication_id,
#             "medication_document": medication_doc,
#             "follow_up": consultation.follow_up,
#             "appointment_id": consultation.appointment_id
#         }
#
#     @staticmethod
#     def format_medication_list(medication_doc: Dict[str, Any]) -> str:
#         """Format medication document into readable list"""
#         if not medication_doc:
#             return None
#
#         # Try different possible structures
#         medications = []
#
#         # Structure 1: {"medications": [...]}
#         if "medications" in medication_doc:
#             medications = medication_doc.get("medications", [])
#         # Structure 2: {"drugs": [...]}
#         elif "drugs" in medication_doc:
#             medications = medication_doc.get("drugs", [])
#         # Structure 3: Direct array
#         elif isinstance(medication_doc, list):
#             medications = medication_doc
#         # Structure 4: Root level with medicine/drug keys
#         else:
#             # Check if document has medicine-like keys
#             for key in medication_doc.keys():
#                 if key.lower() in ['medicine', 'drug', 'prescription', 'med']:
#                     medications = medication_doc[key] if isinstance(medication_doc[key], list) else [
#                         medication_doc[key]]
#                     break
#
#         if not medications or len(medications) == 0:
#             return None
#
#         med_list = []
#         for idx, med in enumerate(medications, 1):
#             # Handle both dict and string formats
#             if isinstance(med, str):
#                 med_list.append(f"{idx}. {med}")
#                 continue
#
#             # Try different key names for medication name
#             med_name = (med.get("name") or med.get("medicine_name") or
#                         med.get("drug_name") or med.get("medication") or
#                         "Unknown medication")
#
#             # Try different key names for other fields
#             dosage = med.get("dosage") or med.get("dose") or med.get("strength") or ""
#             frequency = (med.get("frequency") or med.get("timing") or
#                          med.get("schedule") or "")
#             duration = (med.get("duration") or med.get("days") or
#                         med.get("period") or "")
#
#             med_str = f"{idx}. {med_name}"
#             if dosage:
#                 med_str += f" - {dosage}"
#             if frequency:
#                 med_str += f", {frequency}"
#             if duration:
#                 med_str += f", for {duration}"
#
#             med_list.append(med_str)
#
#         return "\n".join(med_list) if med_list else None
#


from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.database_models import Patient, Consultation, Medication
from typing import Optional, Dict, Any


class PatientService:
    @staticmethod
    def get_patient_by_mobile(db: Session, mobile_number: str) -> Optional[Patient]:
        return db.query(Patient).filter(Patient.mobile_number == mobile_number).first()

    @staticmethod
    def get_latest_consultation(db: Session, patient_id: int) -> Optional[Dict[str, Any]]:
        consultation = db.query(Consultation).filter(
            Consultation.patient_id == patient_id
        ).order_by(desc(Consultation.consultation_date)).first()

        if not consultation:
            return None

        medication_doc = None
        if consultation.medication_id:
            medication = db.query(Medication).filter(
                Medication.id == consultation.medication_id
            ).first()
            if medication:
                medication_doc = medication.document

        return {
            "id": consultation.id,
            "consultation_number": consultation.consultation_number,
            "consultation_date": consultation.consultation_date,
            "medication_id": consultation.medication_id,
            "medication_document": medication_doc,
            "follow_up": consultation.follow_up,
            "appointment_id": consultation.appointment_id
        }

    @staticmethod
    def format_medication_list(medication_doc: Dict[str, Any]) -> str:
        """Format medication document into readable list"""
        if not medication_doc:
            return None

        # Try different possible structures
        medications = []

        # Structure 1: {"medication": [...]} - YOUR FORMAT
        if "medication" in medication_doc:
            medications = medication_doc.get("medication", [])
        # Structure 2: {"medications": [...]}
        elif "medications" in medication_doc:
            medications = medication_doc.get("medications", [])
        # Structure 3: {"drugs": [...]}
        elif "drugs" in medication_doc:
            medications = medication_doc.get("drugs", [])
        # Structure 4: Direct array
        elif isinstance(medication_doc, list):
            medications = medication_doc

        if not medications or len(medications) == 0:
            return None

        med_list = []
        for idx, med in enumerate(medications, 1):
            # Handle both dict and string formats
            if isinstance(med, str):
                med_list.append(f"{idx}. {med}")
                continue

            # Get medication name
            med_name = med.get("name") or med.get("code") or "Unknown medication"

            # Parse dosage instruction
            dosage_inst = med.get("dosageInstruction", {})

            # Build frequency string from dayWiseDosage
            day_wise = dosage_inst.get("dayWiseDosage", {})
            unit = day_wise.get("unit", "dose")
            morning = day_wise.get("morning", 0)
            afternoon = day_wise.get("afternoon", 0)
            evening = day_wise.get("evening", 0)
            night = day_wise.get("night", 0)

            # Build dosage parts
            dosage_parts = []
            if morning: dosage_parts.append(f"{morning} in morning")
            if afternoon: dosage_parts.append(f"{afternoon} in afternoon")
            if evening: dosage_parts.append(f"{evening} in evening")
            if night: dosage_parts.append(f"{night} at night")

            frequency_str = ", ".join(dosage_parts) if dosage_parts else ""

            # Get timing and route
            when = dosage_inst.get("when", "")
            route = dosage_inst.get("route", "")

            # Build medication string
            med_str = f"{idx}. {med_name}"
            if unit and unit != "dose":
                med_str += f" ({unit})"
            if frequency_str:
                med_str += f" - {frequency_str}"
            if when:
                med_str += f", {when}"
            if route and route.lower() != "orally":
                med_str += f", {route}"

            med_list.append(med_str)

        # Add patient instruction if available
        patient_instruction = medication_doc.get("patient-instruction") or medication_doc.get("patientInstruction")
        result = "\n".join(med_list)
        if patient_instruction:
            result += f"\n\nInstructions: {patient_instruction}"

        return result

