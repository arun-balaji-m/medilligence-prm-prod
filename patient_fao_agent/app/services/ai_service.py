import openai
from groq import Groq
from patient_fao_agent.app.config import settings
from patient_fao_agent.app.utils.prompts import Prompts
from typing import Dict, Any
import json


class AIService:
    def __init__(self):
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
        self.prompts = Prompts()

    async def anonymize_medical_text(self, text: str) -> Dict[str, Any]:
        try:
            print(f"[Groq] Starting anonymization for {len(text)} characters...")

            response = self.groq_client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": self.prompts.ANONYMIZE_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Text:\n{text[:3000]}"}  # Limit input
                ],
                temperature=0.1,
                max_tokens=1500
            )

            result = response.choices[0].message.content
            print(f"[Groq] Anonymization complete. Response length: {len(result)}")

            # Parse JSON response
            parsed_data = json.loads(result)
            print(f"[Groq] Successfully parsed JSON with keys: {parsed_data.keys()}")
            return parsed_data

        except json.JSONDecodeError as je:
            print(f"[Groq] JSON decode error: {str(je)}")
            print(f"[Groq] Raw response: {result[:500]}")
            # Fallback if not valid JSON
            return {"medical_content": result, "anonymized": True}
        except Exception as e:
            print(f"[Groq] Error in anonymization: {str(e)}")
            raise Exception(f"Error in anonymization: {str(e)}")

    async def generate_patient_explanation(
            self,
            medical_data: Dict[str, Any],
            patient_name: str = None
    ) -> str:
        """Generate patient-friendly explanation using OpenAI"""
        try:
            print(f"[OpenAI] Generating explanation for patient: {patient_name or 'Unknown'}")

            # Create concise context
            context = json.dumps(medical_data, indent=2)[:2500]  # Limit size
            print(f"[OpenAI] Context size: {len(context)} characters")

            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self.prompts.EXPLANATION_SYSTEM_PROMPT},
                    {"role": "user", "content": f"Patient: {patient_name or 'Patient'}\n\nMedical Data:\n{context}"}
                ],
                temperature=0.7,
                max_tokens=settings.MAX_OUTPUT_TOKENS
            )

            explanation = response.choices[0].message.content
            print(f"[OpenAI] Explanation generated: {len(explanation)} characters")
            return explanation

        except Exception as e:
            print(f"[OpenAI] Error generating explanation: {str(e)}")
            raise Exception(f"Error generating explanation: {str(e)}")

    async def answer_patient_query(
            self,
            query: str,
            patient_name: str = None,
            chat_history: list = None
    ) -> str:
        """Answer patient's medical/lifestyle query"""
        try:
            messages = [
                {"role": "system", "content": self.prompts.FAQ_SYSTEM_PROMPT}
            ]

            # Add limited chat history for context
            if chat_history:
                for chat in chat_history[-3:]:  # Only last 3 exchanges
                    messages.append({"role": "user", "content": chat.get("query", "")[:200]})
                    messages.append({"role": "assistant", "content": chat.get("response", "")[:200]})

            messages.append({
                "role": "user",
                "content": f"Patient: {patient_name or 'User'}\n\nQuestion: {query}"
            })

            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=settings.MAX_OUTPUT_TOKENS
            )

            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error answering query: {str(e)}")