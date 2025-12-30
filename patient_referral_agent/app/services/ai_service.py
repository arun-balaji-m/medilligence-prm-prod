# import openai
# import requests
# import json
# from patient_referral_agent.app.config import OPENAI_API_KEY, GROK_API_KEY, GROK_API_URL, GROK_MODEL, OPENAI_MODEL
# from patient_referral_agent.app.utils.prompts import (
#     PATIENT_INFO_PROMPT,
#     HISTORY_COLLECTION_PROMPT,
#     SANITIZE_PROMPT,
#     TIMELINE_CREATION_PROMPT
# )
#
# openai.api_key = OPENAI_API_KEY
#
#
# class AIService:
#     @staticmethod
#     def collect_patient_info(message: str, patient_data: dict) -> dict:
#         prompt = PATIENT_INFO_PROMPT.format(
#             patient_data=json.dumps(patient_data),
#             message=message
#         )
#
#         response = openai.chat.completions.create(
#             model=OPENAI_MODEL,
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.7
#         )
#
#         return json.loads(response.choices[0].message.content)
#
#     @staticmethod
#     def collect_medical_history(message: str, timeline: list) -> dict:
#         prompt = HISTORY_COLLECTION_PROMPT.format(
#             timeline=json.dumps(timeline),
#             message=message
#         )
#
#         response = openai.chat.completions.create(
#             model=OPENAI_MODEL,
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.7
#         )
#
#         return json.loads(response.choices[0].message.content)
#
#     @staticmethod
#     def sanitize_text_with_grok(text: str) -> str:
#         prompt = SANITIZE_PROMPT.format(text=text)
#
#         headers = {
#             "Authorization": f"Bearer {GROK_API_KEY}",
#             "Content-Type": "application/json"
#         }
#
#         payload = {
#             "model": GROK_MODEL,
#             "messages": [{"role": "user", "content": prompt}],
#             "temperature": 0.3
#         }
#
#         response = requests.post(GROK_API_URL, headers=headers, json=payload)
#         result = response.json()
#
#         return result["choices"][0]["message"]["content"]
#
#     @staticmethod
#     def create_timeline_from_data(data: str) -> dict:
#         prompt = TIMELINE_CREATION_PROMPT.format(data=data)
#
#         response = openai.chat.completions.create(
#             model=OPENAI_MODEL,
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.5
#         )
#
#         return json.loads(response.choices[0].message.content)
#
#     @staticmethod
#     def merge_timelines(existing: list, new_events: list) -> list:
#         """Merge and sort timeline events chronologically"""
#         all_events = existing + new_events
#         all_events.sort(key=lambda x: x.get("date", ""))
#         return all_events


##second version
#
# import openai
# import requests
# import json
# from patient_referral_agent.app.config import OPENAI_API_KEY, GROK_API_KEY, GROK_API_URL, GROK_MODEL, OPENAI_MODEL
# from patient_referral_agent.app.utils.prompts import (
#     PATIENT_INFO_PROMPT,
#     HISTORY_COLLECTION_PROMPT,
#     SANITIZE_PROMPT,
#     TIMELINE_CREATION_PROMPT
# )
#
# openai.api_key = OPENAI_API_KEY
#
#
# class AIService:
#     @staticmethod
#     def collect_patient_info(message: str, patient_data: dict) -> dict:
#         try:
#             prompt = PATIENT_INFO_PROMPT.format(
#                 patient_data=json.dumps(patient_data),
#                 message=message
#             )
#
#             response = openai.chat.completions.create(
#                 model=OPENAI_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.7
#             )
#
#             content = response.choices[0].message.content
#             print(f"OpenAI Response: {content}")
#             return json.loads(content)
#         except json.JSONDecodeError as e:
#             print(f"JSON Parse Error: {e}, Content: {content}")
#             return {
#                 "response": "Great! What is your date of birth? (YYYY-MM-DD)",
#                 "patient_data": patient_data,
#                 "complete": False
#             }
#         except Exception as e:
#             print(f"Error in collect_patient_info: {str(e)}")
#             raise
#
#     @staticmethod
#     def collect_medical_history(message: str, timeline: list) -> dict:
#         prompt = HISTORY_COLLECTION_PROMPT.format(
#             timeline=json.dumps(timeline),
#             message=message
#         )
#
#         response = openai.chat.completions.create(
#             model=OPENAI_MODEL,
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.7
#         )
#
#         return json.loads(response.choices[0].message.content)
#
#     @staticmethod
#     def sanitize_text_with_grok(text: str) -> str:
#         prompt = SANITIZE_PROMPT.format(text=text)
#
#         headers = {
#             "Authorization": f"Bearer {GROK_API_KEY}",
#             "Content-Type": "application/json"
#         }
#
#         payload = {
#             "model": GROK_MODEL,
#             "messages": [{"role": "user", "content": prompt}],
#             "temperature": 0.3
#         }
#
#         response = requests.post(GROK_API_URL, headers=headers, json=payload)
#         result = response.json()
#
#         return result["choices"][0]["message"]["content"]
#
#     @staticmethod
#     def create_timeline_from_data(data: str) -> dict:
#         prompt = TIMELINE_CREATION_PROMPT.format(data=data)
#
#         response = openai.chat.completions.create(
#             model=OPENAI_MODEL,
#             messages=[{"role": "user", "content": prompt}],
#             temperature=0.5
#         )
#
#         return json.loads(response.choices[0].message.content)
#
#     @staticmethod
#     def merge_timelines(existing: list, new_events: list) -> list:
#         """Merge and sort timeline events chronologically"""
#         all_events = existing + new_events
#         all_events.sort(key=lambda x: x.get("date", ""))
#         return all_events


##third version
#
# import openai
# import requests
# import json
# from patient_referral_agent.app.config import OPENAI_API_KEY, GROK_API_KEY, GROK_API_URL, GROK_MODEL, OPENAI_MODEL
# from patient_referral_agent.app.utils.prompts import (
#     PATIENT_INFO_PROMPT,
#     HISTORY_COLLECTION_PROMPT,
#     SANITIZE_PROMPT,
#     TIMELINE_CREATION_PROMPT
# )
#
# openai.api_key = OPENAI_API_KEY
#
#
# class AIService:
#     @staticmethod
#     def collect_patient_info(message: str, patient_data: dict) -> dict:
#         try:
#             prompt = PATIENT_INFO_PROMPT.format(
#                 patient_data=json.dumps(patient_data),
#                 message=message
#             )
#
#             response = openai.chat.completions.create(
#                 model=OPENAI_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.3,
#                 response_format={"type": "json_object"}
#             )
#
#             content = response.choices[0].message.content
#             print(f"OpenAI Response: {content}")
#
#             result = json.loads(content)
#
#             # Merge patient data - keep existing non-null values
#             new_data = result.get("patient_data", {})
#             merged_data = {}
#
#             for key in ["patient_name", "dob", "gender", "mobile_number", "email"]:
#                 # Use new value if exists and is not None, otherwise keep old value
#                 if new_data.get(key):
#                     merged_data[key] = new_data[key]
#                 elif patient_data.get(key):
#                     merged_data[key] = patient_data[key]
#                 else:
#                     merged_data[key] = None
#
#             result["patient_data"] = merged_data
#
#             print(f"Merged patient data: {merged_data}")
#             return result
#
#         except json.JSONDecodeError as e:
#             print(f"JSON Parse Error: {e}, Content: {content}")
#             return {
#                 "response": "I didn't quite catch that. Could you please repeat?",
#                 "patient_data": patient_data,
#                 "complete": False
#             }
#         except Exception as e:
#             print(f"Error in collect_patient_info: {str(e)}")
#             raise
#
#     @staticmethod
#     def collect_medical_history(message: str, timeline: list) -> dict:
#         try:
#             prompt = HISTORY_COLLECTION_PROMPT.format(
#                 timeline=json.dumps(timeline) if timeline else "[]",
#                 message=message
#             )
#
#             response = openai.chat.completions.create(
#                 model=OPENAI_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.5,
#                 response_format={"type": "json_object"}
#             )
#
#             content = response.choices[0].message.content
#             print(f"History collection response: {content}")
#             return json.loads(content)
#         except Exception as e:
#             print(f"Error in collect_medical_history: {str(e)}")
#             raise
#
#     @staticmethod
#     def sanitize_text_with_grok(text: str) -> str:
#         prompt = SANITIZE_PROMPT.format(text=text)
#
#         headers = {
#             "Authorization": f"Bearer {GROK_API_KEY}",
#             "Content-Type": "application/json"
#         }
#
#         payload = {
#             "model": GROK_MODEL,
#             "messages": [{"role": "user", "content": prompt}],
#             "temperature": 0.3
#         }
#
#         response = requests.post(GROK_API_URL, headers=headers, json=payload)
#         result = response.json()
#
#         return result["choices"][0]["message"]["content"]
#
#     @staticmethod
#     def create_timeline_from_data(data: str) -> dict:
#         try:
#             prompt = TIMELINE_CREATION_PROMPT.format(data=data)
#
#             response = openai.chat.completions.create(
#                 model=OPENAI_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.5,
#                 response_format={"type": "json_object"}
#             )
#
#             content = response.choices[0].message.content
#             print(f"Timeline creation response: {content}")
#             return json.loads(content)
#         except Exception as e:
#             print(f"Error in create_timeline_from_data: {str(e)}")
#             raise
#
#     @staticmethod
#     def merge_timelines(existing: list, new_events: list) -> list:
#         """Merge and sort timeline events chronologically"""
#         all_events = existing + new_events
#         all_events.sort(key=lambda x: x.get("date", ""))
#         return all_events


# ##fourth version
#
# import openai
# import requests
# import json
# from patient_referral_agent.app.config import OPENAI_API_KEY, GROK_API_KEY, GROK_API_URL, GROK_MODEL, OPENAI_MODEL
# from patient_referral_agent.app.utils.prompts import (
#     PATIENT_INFO_PROMPT,
#     HISTORY_COLLECTION_PROMPT,
#     SANITIZE_PROMPT,
#     TIMELINE_CREATION_PROMPT
# )
#
# openai.api_key = OPENAI_API_KEY
#
#
# class AIService:
#     @staticmethod
#     def collect_patient_info(message: str, patient_data: dict, asked_fields: list = None) -> dict:
#         if asked_fields is None:
#             asked_fields = []
#
#         try:
#             prompt = PATIENT_INFO_PROMPT.format(
#                 patient_data=json.dumps(patient_data),
#                 asked_fields=json.dumps(asked_fields),
#                 message=message
#             )
#
#             response = openai.chat.completions.create(
#                 model=OPENAI_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.3,
#                 response_format={"type": "json_object"}
#             )
#
#             content = response.choices[0].message.content
#             print(f"OpenAI Response: {content}")
#
#             result = json.loads(content)
#
#             # Merge patient data - keep existing non-null values
#             new_data = result.get("patient_data", {})
#             merged_data = {}
#
#             for key in ["patient_name", "dob", "gender", "mobile_number", "email"]:
#                 # Use new value if exists and is not None, otherwise keep old value
#                 if new_data.get(key):
#                     merged_data[key] = new_data[key]
#                 elif patient_data.get(key):
#                     merged_data[key] = patient_data[key]
#                 else:
#                     merged_data[key] = None
#
#             result["patient_data"] = merged_data
#
#             # Update asked_fields list
#             new_asked = result.get("asked_fields", asked_fields)
#             if not isinstance(new_asked, list):
#                 new_asked = asked_fields
#             result["asked_fields"] = new_asked
#
#             print(f"Merged patient data: {merged_data}")
#             print(f"Asked fields: {new_asked}")
#             return result
#
#         except json.JSONDecodeError as e:
#             print(f"JSON Parse Error: {e}, Content: {content}")
#             return {
#                 "response": "I didn't quite catch that. Could you please repeat?",
#                 "patient_data": patient_data,
#                 "asked_fields": asked_fields,
#                 "complete": False
#             }
#         except Exception as e:
#             print(f"Error in collect_patient_info: {str(e)}")
#             raise
#
#     @staticmethod
#     def collect_medical_history(message: str, timeline: list) -> dict:
#         try:
#             prompt = HISTORY_COLLECTION_PROMPT.format(
#                 timeline=json.dumps(timeline) if timeline else "[]",
#                 message=message
#             )
#
#             response = openai.chat.completions.create(
#                 model=OPENAI_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.5,
#                 response_format={"type": "json_object"}
#             )
#
#             content = response.choices[0].message.content
#             print(f"History collection response: {content}")
#             return json.loads(content)
#         except Exception as e:
#             print(f"Error in collect_medical_history: {str(e)}")
#             raise
#
#     @staticmethod
#     def sanitize_text_with_grok(text: str) -> str:
#         prompt = SANITIZE_PROMPT.format(text=text)
#
#         headers = {
#             "Authorization": f"Bearer {GROK_API_KEY}",
#             "Content-Type": "application/json"
#         }
#
#         payload = {
#             "model": GROK_MODEL,
#             "messages": [{"role": "user", "content": prompt}],
#             "temperature": 0.3
#         }
#
#         response = requests.post(GROK_API_URL, headers=headers, json=payload)
#         result = response.json()
#
#         return result["choices"][0]["message"]["content"]
#
#     @staticmethod
#     def create_timeline_from_data(data: str) -> dict:
#         try:
#             prompt = TIMELINE_CREATION_PROMPT.format(data=data)
#
#             response = openai.chat.completions.create(
#                 model=OPENAI_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.5,
#                 response_format={"type": "json_object"}
#             )
#
#             content = response.choices[0].message.content
#             print(f"Timeline creation response: {content}")
#             return json.loads(content)
#         except Exception as e:
#             print(f"Error in create_timeline_from_data: {str(e)}")
#             raise
#
#     @staticmethod
#     def merge_timelines(existing: list, new_events: list) -> list:
#         """Merge and sort timeline events chronologically"""
#         all_events = existing + new_events
#         all_events.sort(key=lambda x: x.get("date", ""))
#         return all_events


##fifth version

import openai
import requests
import json
from patient_referral_agent.app.config import OPENAI_API_KEY, GROK_API_KEY, GROK_API_URL, GROK_MODEL, OPENAI_MODEL
from patient_referral_agent.app.utils.prompts import (
    PATIENT_INFO_PROMPT,
    HISTORY_COLLECTION_PROMPT,
    SANITIZE_PROMPT,
    TIMELINE_CREATION_PROMPT
)

openai.api_key = OPENAI_API_KEY


class AIService:
    @staticmethod
    def collect_patient_info(message: str, patient_data: dict, asked_fields: list = None) -> dict:
        if asked_fields is None:
            asked_fields = []

        try:
            prompt = PATIENT_INFO_PROMPT.format(
                patient_data=json.dumps(patient_data),
                asked_fields=json.dumps(asked_fields),
                message=message
            )

            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            print(f"OpenAI Response: {content}")

            result = json.loads(content)

            # Merge patient data - keep existing non-null values
            new_data = result.get("patient_data", {})
            merged_data = {}

            for key in ["patient_name", "dob", "gender", "mobile_number", "email"]:
                # Use new value if exists and is not None, otherwise keep old value
                if new_data.get(key):
                    merged_data[key] = new_data[key]
                elif patient_data.get(key):
                    merged_data[key] = patient_data[key]
                else:
                    merged_data[key] = None

            result["patient_data"] = merged_data

            # Update asked_fields list
            new_asked = result.get("asked_fields", asked_fields)
            if not isinstance(new_asked, list):
                new_asked = asked_fields
            result["asked_fields"] = new_asked

            print(f"Merged patient data: {merged_data}")
            print(f"Asked fields: {new_asked}")
            return result

        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}, Content: {content}")
            return {
                "response": "I didn't quite catch that. Could you please repeat?",
                "patient_data": patient_data,
                "asked_fields": asked_fields,
                "complete": False
            }
        except Exception as e:
            print(f"Error in collect_patient_info: {str(e)}")
            raise

    @staticmethod
    def collect_medical_history(message: str, timeline: list) -> dict:
        try:
            prompt = HISTORY_COLLECTION_PROMPT.format(
                timeline=json.dumps(timeline) if timeline else "[]",
                message=message
            )

            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            print(f"History collection response: {content}")
            return json.loads(content)
        except Exception as e:
            print(f"Error in collect_medical_history: {str(e)}")
            raise

    @staticmethod
    def sanitize_text_with_grok(text: str) -> str:
        try:
            prompt = SANITIZE_PROMPT.format(text=text)

            headers = {
                "Authorization": f"Bearer {GROK_API_KEY}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": GROK_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3
            }

            print(f"Calling Grok API to sanitize text (length: {len(text)} chars)...")
            response = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=60)

            # Check if request was successful
            if response.status_code != 200:
                print(f"Grok API Error: {response.status_code} - {response.text}")
                # Fallback: basic sanitization without Grok
                return AIService._basic_sanitize(text)

            result = response.json()
            print(f"Grok API response received")

            # Check if response has expected structure
            if "choices" not in result:
                print(f"Unexpected Grok response structure: {result}")
                return AIService._basic_sanitize(text)

            return result["choices"][0]["message"]["content"]

        except requests.exceptions.Timeout:
            print("Grok API timeout, using basic sanitization")
            return AIService._basic_sanitize(text)
        except Exception as e:
            print(f"Error in sanitize_text_with_grok: {str(e)}")
            # Fallback to basic sanitization
            return AIService._basic_sanitize(text)

    @staticmethod
    def _basic_sanitize(text: str) -> str:
        """Basic PII removal as fallback when Grok is unavailable"""
        import re

        # Remove common PII patterns
        # Remove phone numbers
        text = re.sub(r'\b\d{10}\b', '[PHONE]', text)
        text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', text)

        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', text)

        # Remove common ID patterns (MRN, SSN, etc.)
        text = re.sub(r'\b(MRN|SSN|ID)\s*:?\s*\d+\b', '[ID]', text, flags=re.IGNORECASE)

        # Remove addresses (basic pattern)
        text = re.sub(
            r'\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Boulevard|Blvd)\b',
            '[ADDRESS]', text, flags=re.IGNORECASE)

        return text

    @staticmethod
    def create_timeline_from_data(data: str) -> dict:
        try:
            prompt = TIMELINE_CREATION_PROMPT.format(data=data)

            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            print(f"Timeline creation response: {content}")
            return json.loads(content)
        except Exception as e:
            print(f"Error in create_timeline_from_data: {str(e)}")
            raise

    @staticmethod
    def merge_timelines(existing: list, new_events: list) -> list:
        """Merge and sort timeline events chronologically"""
        all_events = existing + new_events
        all_events.sort(key=lambda x: x.get("date", ""))
        return all_events