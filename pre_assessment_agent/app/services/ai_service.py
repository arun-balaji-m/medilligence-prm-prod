# """
# AI service for conversational interaction using OpenAI GPT
# """
#
# from openai import AsyncOpenAI
# from typing import List, Dict, Any
# import json
# from pre_assessment_agent.app.config import get_settings
# from pre_assessment_agent.app.utils.prompts import SYSTEM_PROMPT, get_context_prompt, EXTRACTION_PROMPT
#
# settings = get_settings()
#
#
# class AIService:
#     """Handle AI-powered conversation and data extraction"""
#
#     def __init__(self):
#         self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
#         self.model = settings.OPENAI_MODEL
#
#     async def generate_response(
#             self,
#             messages: List[Dict[str, str]],
#             session_data: Dict[str, Any]
#     ) -> str:
#         """
#         Generate AI response based on conversation history
#
#         Args:
#             messages: Conversation history
#             session_data: Current session context
#
#         Returns:
#             AI generated response
#         """
#         # Build system prompt with context
#         system_message = SYSTEM_PROMPT
#
#         # Add patient context if available
#         if session_data.get("patient_verified"):
#             context = get_context_prompt(
#                 patient_name=session_data.get("patient_name"),
#                 appointment_date=session_data.get("appointment_date"),
#                 appointment_number=session_data.get("appointment_number"),
#                 current_stage=session_data.get("current_stage")
#             )
#             system_message += context
#
#         # Prepare messages for API
#         api_messages = [
#             {"role": "system", "content": system_message}
#         ]
#
#         # Add conversation history
#         api_messages.extend(messages)
#
#         try:
#             # Call OpenAI API
#             response = await self.client.chat.completions.create(
#                 model=self.model,
#                 messages=api_messages,
#                 temperature=0.7,
#                 max_tokens=500
#             )
#
#             return response.choices[0].message.content
#
#         except Exception as e:
#             print(f"Error calling OpenAI API: {e}")
#             raise
#
#     async def extract_assessment_data(
#             self,
#             conversation_history: List[Dict[str, str]]
#     ) -> Dict[str, Any]:
#         """
#         Extract structured medical information from conversation
#
#         Args:
#             conversation_history: Full conversation history
#
#         Returns:
#             Structured assessment data as JSON
#         """
#         # Format conversation for extraction
#         conversation_text = "\n".join([
#             f"{msg['role'].upper()}: {msg['content']}"
#             for msg in conversation_history
#         ])
#
#         extraction_prompt = EXTRACTION_PROMPT.format(
#             conversation=conversation_text
#         )
#
#         try:
#             # Call OpenAI for structured extraction
#             response = await self.client.chat.completions.create(
#                 model=self.model,
#                 messages=[
#                     {"role": "system",
#                      "content": "You are a medical data extraction assistant. Extract information accurately and return only valid JSON."},
#                     {"role": "user", "content": extraction_prompt}
#                 ],
#                 temperature=0.3,
#                 max_tokens=1000
#             )
#
#             # Parse JSON response
#             content = response.choices[0].message.content
#
#             # Clean up response (remove markdown code blocks if present)
#             content = content.strip()
#             if content.startswith("```json"):
#                 content = content[7:]
#             if content.startswith("```"):
#                 content = content[3:]
#             if content.endswith("```"):
#                 content = content[:-3]
#             content = content.strip()
#
#             assessment_data = json.loads(content)
#             return assessment_data
#
#         except json.JSONDecodeError as e:
#             print(f"Error parsing JSON from AI response: {e}")
#             # Return empty structure if parsing fails
#             return {}
#         except Exception as e:
#             print(f"Error extracting assessment data: {e}")
#             raise
#
#     def determine_completion_status(self, session_data: Dict[str, Any]) -> bool:
#         """
#         Determine if assessment is complete based on collected sections
#
#         Args:
#             session_data: Current session data
#
#         Returns:
#             True if all sections are collected
#         """
#         required_sections = [
#             "chief_complaint",
#             "history_present_illness",
#             "past_medical_history",
#             "procedure_history",
#             "current_medication",
#             "allergy",
#             "comorbidities",
#             "family_history",
#             "social_history"
#         ]
#
#         collected_sections = session_data.get("collected_sections", [])
#
#         # Check if all sections are collected
#         return all(section in collected_sections for section in required_sections)
#
#     def update_session_stage(
#             self,
#             session_data: Dict[str, Any],
#             user_message: str,
#             ai_response: str
#     ) -> Dict[str, Any]:
#         """
#         Update session data based on conversation progress
#
#         Args:
#             session_data: Current session data
#             user_message: User's message
#             ai_response: AI's response
#
#         Returns:
#             Updated session data
#         """
#         # Initialize collected_sections if not exists
#         if "collected_sections" not in session_data:
#             session_data["collected_sections"] = []
#
#         # Track stages based on conversation flow
#         response_lower = ai_response.lower()
#
#         # Check which section is being discussed
#         section_keywords = {
#             "chief_complaint": ["what brings you", "health concerns", "experiencing"],
#             "history_present_illness": ["when did", "symptoms start", "better or worse"],
#             "past_medical_history": ["ongoing health conditions", "diabetes", "blood pressure"],
#             "procedure_history": ["surgeries", "medical procedures"],
#             "current_medication": ["taking any medicines", "medications"],
#             "allergy": ["allergic to", "allergies", "reactions"],
#             "comorbidities": ["other health conditions"],
#             "family_history": ["family", "parents", "siblings"],
#             "social_history": ["smoke", "alcohol", "work", "exercise"]
#         }
#
#         # Mark sections as collected when moving to next topic
#         for section, keywords in section_keywords.items():
#             if any(keyword in response_lower for keyword in keywords):
#                 session_data["current_stage"] = section
#
#                 # Mark previous stage as collected when moving to new stage
#                 if session_data.get("previous_stage") and session_data["previous_stage"] not in session_data[
#                     "collected_sections"]:
#                     session_data["collected_sections"].append(session_data["previous_stage"])
#
#                 session_data["previous_stage"] = section
#                 break
#
#         # Check if assessment is being finalized
#         if any(phrase in response_lower for phrase in ["have i captured everything", "thank you for providing"]):
#             # Mark all sections as collected
#             session_data["assessment_complete"] = True
#             if session_data.get("current_stage") and session_data["current_stage"] not in session_data[
#                 "collected_sections"]:
#                 session_data["collected_sections"].append(session_data["current_stage"])
#
#         return session_data


"""
AI service for conversational interaction using OpenAI GPT
"""

from openai import AsyncOpenAI
from typing import List, Dict, Any
import json
from pre_assessment_agent.app.config import get_settings
from pre_assessment_agent.app.utils.prompts import SYSTEM_PROMPT, get_context_prompt, EXTRACTION_PROMPT

settings = get_settings()


class AIService:
    """Handle AI-powered conversation and data extraction"""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def generate_response(
            self,
            messages: List[Dict[str, str]],
            session_data: Dict[str, Any]
    ) -> str:
        """
        Generate AI response based on conversation history

        Args:
            messages: Conversation history
            session_data: Current session context

        Returns:
            AI generated response
        """
        # Build system prompt with context
        system_message = SYSTEM_PROMPT

        # Add patient context if available
        if session_data.get("patient_verified"):
            context = get_context_prompt(
                patient_name=session_data.get("patient_name"),
                appointment_date=session_data.get("appointment_date"),
                appointment_number=session_data.get("appointment_number"),
                current_stage=session_data.get("current_stage")
            )
            system_message += context

        # Prepare messages for API
        api_messages = [
            {"role": "system", "content": system_message}
        ]

        # Add conversation history
        api_messages.extend(messages)

        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=api_messages,
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            raise

    async def extract_assessment_data(
            self,
            conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Extract structured medical information from conversation

        Args:
            conversation_history: Full conversation history as list of dicts

        Returns:
            Structured assessment data as JSON
        """
        # Format conversation for extraction
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history
        ])

        extraction_prompt = EXTRACTION_PROMPT.format(
            conversation=conversation_text
        )

        try:
            # Call OpenAI for structured extraction
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system",
                     "content": "You are a medical data extraction assistant. Extract information accurately and return only valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )

            # Parse JSON response
            content = response.choices[0].message.content

            # Clean up response (remove markdown code blocks if present)
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            assessment_data = json.loads(content)
            return assessment_data

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from AI response: {e}")
            # Return empty structure if parsing fails
            return {}
        except Exception as e:
            print(f"Error extracting assessment data: {e}")
            raise

    def determine_completion_status(self, session_data: Dict[str, Any]) -> bool:
        """
        Determine if assessment is complete based on collected sections

        Args:
            session_data: Current session data

        Returns:
            True if all sections are collected
        """
        required_sections = [
            "chief_complaint",
            "history_present_illness",
            "past_medical_history",
            "procedure_history",
            "current_medication",
            "allergy",
            "comorbidities",
            "family_history",
            "social_history"
        ]

        collected_sections = session_data.get("collected_sections", [])

        # Check if all sections are collected
        return all(section in collected_sections for section in required_sections)

    def update_session_stage(
            self,
            session_data: Dict[str, Any],
            user_message: str,
            ai_response: str
    ) -> Dict[str, Any]:
        """
        Update session data based on conversation progress

        Args:
            session_data: Current session data
            user_message: User's message
            ai_response: AI's response

        Returns:
            Updated session data
        """
        # Initialize collected_sections if not exists
        if "collected_sections" not in session_data:
            session_data["collected_sections"] = []

        # Track stages based on conversation flow
        response_lower = ai_response.lower()

        # Check which section is being discussed
        section_keywords = {
            "chief_complaint": ["what brings you", "health concerns", "experiencing"],
            "history_present_illness": ["when did", "symptoms start", "better or worse"],
            "past_medical_history": ["ongoing health conditions", "diabetes", "blood pressure"],
            "procedure_history": ["surgeries", "medical procedures"],
            "current_medication": ["taking any medicines", "medications"],
            "allergy": ["allergic to", "allergies", "reactions"],
            "comorbidities": ["other health conditions"],
            "family_history": ["family", "parents", "siblings"],
            "social_history": ["smoke", "alcohol", "work", "exercise"]
        }

        # Mark sections as collected when moving to next topic
        for section, keywords in section_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                session_data["current_stage"] = section

                # Mark previous stage as collected when moving to new stage
                if session_data.get("previous_stage") and session_data["previous_stage"] not in session_data[
                    "collected_sections"]:
                    session_data["collected_sections"].append(session_data["previous_stage"])

                session_data["previous_stage"] = section
                break

        # Check if assessment is being finalized
        if any(phrase in response_lower for phrase in ["have i captured everything", "thank you for providing"]):
            # Mark all sections as collected
            session_data["assessment_complete"] = True
            if session_data.get("current_stage") and session_data["current_stage"] not in session_data[
                "collected_sections"]:
                session_data["collected_sections"].append(session_data["current_stage"])

        return session_data