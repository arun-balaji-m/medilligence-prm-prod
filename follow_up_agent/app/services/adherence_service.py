# from sqlalchemy.orm import Session
# from ..models.database_models import FollowUpAdherence
# from typing import Dict, Any
# import json
# from datetime import datetime
#
#
# class AdherenceService:
#     @staticmethod
#     def save_adherence_data(
#             db: Session,
#             consultation_id: int,
#             adherence_data: Dict[str, Any]
#     ) -> FollowUpAdherence:
#         document_number = f"FA-{consultation_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
#
#         adherence_record = FollowUpAdherence(
#             document_number=document_number,
#             document=adherence_data,
#             consultation_id=consultation_id,
#             status="completed"
#         )
#
#         db.add(adherence_record)
#         db.commit()
#         db.refresh(adherence_record)
#
#         return adherence_record
#

# #second version
# from sqlalchemy.orm import Session
# from ..models.database_models import FollowUpAdherence
# from typing import Dict, Any
# import json
# from datetime import datetime
#
#
# class AdherenceService:
#     @staticmethod
#     def save_adherence_data(
#             db: Session,
#             consultation_id: int,
#             adherence_data: Dict[str, Any],
#             early_followup_info: Dict[str, Any] = None
#     ) -> FollowUpAdherence:
#         document_number = f"FA-{consultation_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
#
#         # Add early follow-up information to the document
#         if early_followup_info and early_followup_info.get("needs_early_followup"):
#             adherence_data["early_followup_details"] = {
#                 "recommended": "Yes",
#                 "reason": early_followup_info.get("reason", ""),
#                 "urgency": early_followup_info.get("urgency", "medium")
#             }
#
#         status = "early_followup_needed" if (
#                     early_followup_info and early_followup_info.get("needs_early_followup")) else "completed"
#
#         adherence_record = FollowUpAdherence(
#             document_number=document_number,
#             document=adherence_data,
#             consultation_id=consultation_id,
#             status=status
#         )
#
#         db.add(adherence_record)
#         db.commit()
#         db.refresh(adherence_record)
#
#         return adherence_record
#


# #second version
# from sqlalchemy.orm import Session
# from ..models.database_models import FollowUpAdherence
# from typing import Dict, Any
# import json
# from datetime import datetime
#
#
# class AdherenceService:
#     @staticmethod
#     def save_adherence_data(
#             db: Session,
#             consultation_id: int,
#             adherence_data: Dict[str, Any],
#             early_followup_info: Dict[str, Any] = None
#     ) -> FollowUpAdherence:
#         document_number = f"FA-{consultation_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
#
#         # Add early follow-up information to the document
#         if early_followup_info and early_followup_info.get("needs_early_followup"):
#             adherence_data["early_followup_details"] = {
#                 "recommended": "Yes",
#                 "reason": early_followup_info.get("reason", ""),
#                 "urgency": early_followup_info.get("urgency", "medium")
#             }
#
#         status = "early_followup_needed" if (
#                     early_followup_info and early_followup_info.get("needs_early_followup")) else "completed"
#
#         adherence_record = FollowUpAdherence(
#             document_number=document_number,
#             document=adherence_data,
#             consultation_id=consultation_id,
#             status=status
#         )
#
#         db.add(adherence_record)
#         db.commit()
#         db.refresh(adherence_record)
#
#         return adherence_record

##working third version
from sqlalchemy.orm import Session
from ..models.database_models import FollowUpAdherence
from typing import Dict, Any
import json
from datetime import datetime


class AdherenceService:
    @staticmethod
    def save_adherence_data(
            db: Session,
            consultation_id: int,
            adherence_data: Dict[str, Any],
            early_followup_info: Dict[str, Any] = None
    ) -> FollowUpAdherence:
        document_number = f"FA-{consultation_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Add early follow-up information to the document
        if early_followup_info and early_followup_info.get("needs_early_followup"):
            adherence_data["early_followup_details"] = {
                "recommended": "Yes",
                "reason": early_followup_info.get("reason", ""),
                "urgency": early_followup_info.get("urgency", "medium")
            }

        status = "early_followup_needed" if (
                    early_followup_info and early_followup_info.get("needs_early_followup")) else "completed"

        adherence_record = FollowUpAdherence(
            document_number=document_number,
            document=adherence_data,
            consultation_id=consultation_id,
            status=status
        )

        db.add(adherence_record)
        db.commit()
        db.refresh(adherence_record)

        return adherence_record

