from openai import OpenAI
from ..config import settings
from ..utils.prompts import SYSTEM_PROMPT, EXTRACTION_PROMPT
from typing import List, Dict
import json


class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    def get_response(self, messages: List[Dict[str, str]], context: str = "") -> str:
        system_message = SYSTEM_PROMPT
        if context:
            system_message += f"\n\nCONTEXT:\n{context}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_message}] + messages,
            temperature=0.7,
            max_tokens=400
        )
        return response.choices[0].message.content

    def extract_adherence_data(self, conversation_history: List[Dict[str, str]]) -> Dict[str, str]:
        # Create a summary of the conversation for extraction
        conversation_text = "\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in conversation_history
        ])

        extraction_prompt = f"""Based on this follow-up conversation, extract adherence data in medical terminology.

CONVERSATION:
{conversation_text}

{EXTRACTION_PROMPT}"""

        messages = [{"role": "user", "content": extraction_prompt}]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
            max_tokens=500
        )

        try:
            data = json.loads(response.choices[0].message.content)
            # Ensure all fields are present with better defaults
            default_data = {
                "medication_received": "Not discussed during follow-up",
                "medication_adherence": "Not discussed during follow-up",
                "medication_timing": "Not discussed during follow-up",
                "side_effects_check": "Not discussed during follow-up",
                "recovery_assessment": "Not discussed during follow-up",
                "lifestyle_coaching": "Not provided",
                "early_followup_recommended": "No"
            }
            default_data.update(data)
            return default_data
        except json.JSONDecodeError:
            return {
                "medication_received": "Unable to extract from conversation",
                "medication_adherence": "Unable to extract from conversation",
                "medication_timing": "Unable to extract from conversation",
                "side_effects_check": "Unable to extract from conversation",
                "recovery_assessment": "Unable to extract from conversation",
                "lifestyle_coaching": "Not provided",
                "early_followup_recommended": "No"
            }

    def check_early_followup_needed(self, conversation_history: List[Dict[str, str]]) -> Dict[str, any]:
        """Analyze if patient needs early follow-up based on conversation"""
        analysis_prompt = """Analyze the conversation and determine if the patient needs an early follow-up appointment. 
Consider: severe side effects, no improvement in condition, worsening symptoms, patient distress.
Return ONLY valid JSON:
{
  "needs_early_followup": true/false,
  "reason": "brief medical reason",
  "urgency": "high/medium/low"
}"""

        messages = conversation_history + [{"role": "user", "content": analysis_prompt}]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=150
        )

        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            return {
                "needs_early_followup": False,
                "reason": "Unable to determine",
                "urgency": "low"
            }
