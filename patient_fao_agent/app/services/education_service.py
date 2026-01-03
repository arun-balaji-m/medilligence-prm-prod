from sqlalchemy.orm import Session
from patient_fao_agent.app.models.database_models import AIChatHistory, Patient
from patient_fao_agent.app.models.schema_models import ChatQueryResponse, ChatHistoryResponse
from patient_fao_agent.app.services.ai_service import AIService
from patient_fao_agent.app.services.patient_service import PatientService
from fastapi import HTTPException
from typing import List, Optional
import uuid


class EducationService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
        self.patient_service = PatientService(db)

    async def handle_query(
            self,
            patient_id: int,
            query: str,
            session_id: Optional[str] = None
    ) -> ChatQueryResponse:
        """Handle direct patient queries"""
        try:
            # Get patient info
            patient = await self.patient_service.get_patient_by_id(patient_id)

            # Get recent chat history for context
            chat_history = self._get_recent_chats(patient_id, limit=3)

            # Generate AI response
            response = await self.ai_service.answer_patient_query(
                query=query,
                patient_name=patient.patient_name,
                chat_history=chat_history
            )

            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())

            # Store in database
            chat_record = AIChatHistory(
                patient_id=patient_id,
                document_number=session_id,
                document={
                    "type": "query",
                    "query": query,
                    "response": response,
                    "session_id": session_id
                }
            )

            self.db.add(chat_record)
            self.db.commit()
            self.db.refresh(chat_record)

            return ChatQueryResponse(
                response=response,
                chat_id=chat_record.id,
                session_id=session_id
            )

        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

    def _get_recent_chats(self, patient_id: int, limit: int = 3) -> List[dict]:
        """Get recent chat history for context"""
        chats = self.db.query(AIChatHistory).filter(
            AIChatHistory.patient_id == patient_id
        ).order_by(AIChatHistory.created_at.desc()).limit(limit).all()

        return [chat.document for chat in chats if chat.document]

    async def get_chat_history(
            self,
            patient_id: int,
            limit: int = 20
    ) -> List[ChatHistoryResponse]:
        """Get patient chat history"""
        try:
            chats = self.db.query(AIChatHistory).filter(
                AIChatHistory.patient_id == patient_id
            ).order_by(AIChatHistory.created_at.desc()).limit(limit).all()

            return [
                ChatHistoryResponse(
                    id=chat.id,
                    document_number=chat.document_number,
                    document=chat.document,
                    patient_id=chat.patient_id,
                    created_at=chat.created_at
                ) for chat in chats
            ]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

    async def delete_chat(self, chat_id: int):
        """Delete a specific chat entry"""
        try:
            chat = self.db.query(AIChatHistory).filter(AIChatHistory.id == chat_id).first()
            if not chat:
                raise HTTPException(status_code=404, detail="Chat not found")

            self.db.delete(chat)
            self.db.commit()

            return {"message": "Chat deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting chat: {str(e)}")