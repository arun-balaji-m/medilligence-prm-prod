# from openai import OpenAI
# import json
# import os
# from datetime import datetime
# from typing import Dict, List
#
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
# # Store conversation history per session
# conversation_sessions: Dict[str, List[Dict]] = {}
#
# SYSTEM_PROMPT = """You are a helpful medical appointment booking assistant. Your role is to help patients:
# 1. Book appointments with doctors
# 2. Cancel existing appointments
# 3. Check available slots
# 4. Find doctors by name or department
#
# Always be polite and professional. When collecting information:
# - Ask for the patient's mobile number to identify them
# - If booking, ask for doctor name or department preference
# - Ask for preferred date for appointments
# - Confirm all details before booking
#
# Use the available functions to:
# - getPatientDetails: Get patient info using mobile number
# - getDoctorDepartmentDetails: Find doctors by name or specialization
# - getAvailableSlots: Check available time slots
# - bookAnAppointment: Book the appointment
# - cancelAppointment: Cancel an existing appointment
#
# Always confirm successful operations with the patient."""
#
# FUNCTIONS = [
#     {
#         "name": "getPatientDetails",
#         "description": "Get patient details using mobile number",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "mobile_number": {
#                     "type": "string",
#                     "description": "The patient's mobile number"
#                 }
#             },
#             "required": ["mobile_number"]
#         }
#     },
#     {
#         "name": "getDoctorDepartmentDetails",
#         "description": "Get doctor details using doctor name or department/specialization",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "doctor_name": {
#                     "type": "string",
#                     "description": "The doctor's name (optional)"
#                 },
#                 "specialization": {
#                     "type": "string",
#                     "description": "The department or specialization (optional)"
#                 }
#             }
#         }
#     },
#     {
#         "name": "getAvailableSlots",
#         "description": "Get available appointment slots for a doctor on a specific date",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "doctor_id": {
#                     "type": "integer",
#                     "description": "The doctor's ID (optional)"
#                 },
#                 "appointment_date": {
#                     "type": "string",
#                     "description": "The requested date in YYYY-MM-DD format"
#                 }
#             },
#             "required": ["appointment_date"]
#         }
#     },
#     {
#         "name": "bookAnAppointment",
#         "description": "Book an appointment for a patient",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "patient_id": {
#                     "type": "integer",
#                     "description": "The patient's ID"
#                 },
#                 "slot_id": {
#                     "type": "integer",
#                     "description": "The slot ID to book"
#                 },
#                 "appointment_date": {
#                     "type": "string",
#                     "description": "The appointment date and time in ISO format"
#                 }
#             },
#             "required": ["patient_id", "slot_id", "appointment_date"]
#         }
#     },
#     {
#         "name": "cancelAppointment",
#         "description": "Cancel an existing appointment",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "appointment_id": {
#                     "type": "integer",
#                     "description": "The appointment ID to cancel"
#                 }
#             },
#             "required": ["appointment_id"]
#         }
#     }
# ]
#
#
# def get_or_create_session(session_id: str) -> List[Dict]:
#     if session_id not in conversation_sessions:
#         conversation_sessions[session_id] = [
#             {"role": "system", "content": SYSTEM_PROMPT}
#         ]
#     return conversation_sessions[session_id]
#
#
# def process_chat_message(message: str, session_id: str) -> Dict:
#     """Process a chat message and return AI response with function calls if needed"""
#     messages = get_or_create_session(session_id)
#     messages.append({"role": "user", "content": message})
#
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages,
#         functions=FUNCTIONS,
#         function_call="auto"
#     )
#
#     response_message = response.choices[0].message
#
#     # Check if AI wants to call a function
#     if response_message.function_call:
#         function_name = response_message.function_call.name
#         function_args = json.loads(response_message.function_call.arguments)
#
#         messages.append({
#             "role": "assistant",
#             "content": None,
#             "function_call": {
#                 "name": function_name,
#                 "arguments": response_message.function_call.arguments
#             }
#         })
#
#         return {
#             "type": "function_call",
#             "function_name": function_name,
#             "function_args": function_args,
#             "messages": messages
#         }
#     else:
#         # Regular text response
#         messages.append({
#             "role": "assistant",
#             "content": response_message.content
#         })
#
#         return {
#             "type": "text",
#             "content": response_message.content,
#             "messages": messages
#         }
#
#
# def add_function_result(session_id: str, function_name: str, function_result: str) -> Dict:
#     """Add function execution result and get AI's next response"""
#     messages = get_or_create_session(session_id)
#
#     messages.append({
#         "role": "function",
#         "name": function_name,
#         "content": function_result
#     })
#
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages,
#         functions=FUNCTIONS,
#         function_call="auto"
#     )
#
#     response_message = response.choices[0].message
#
#     # Check if AI wants to call another function
#     if response_message.function_call:
#         function_name = response_message.function_call.name
#         function_args = json.loads(response_message.function_call.arguments)
#
#         messages.append({
#             "role": "assistant",
#             "content": None,
#             "function_call": {
#                 "name": function_name,
#                 "arguments": response_message.function_call.arguments
#             }
#         })
#
#         return {
#             "type": "function_call",
#             "function_name": function_name,
#             "function_args": function_args,
#             "messages": messages
#         }
#     else:
#         messages.append({
#             "role": "assistant",
#             "content": response_message.content
#         })
#
#         return {
#             "type": "text",
#             "content": response_message.content,
#             "messages": messages
#         }


# ##seond version
# from openai import OpenAI
# import json
# import os
# from datetime import datetime
# from typing import Dict, List
#
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
# # Store conversation history per session
# conversation_sessions: Dict[str, List[Dict]] = {}
#
# SYSTEM_PROMPT = """You are a helpful medical appointment booking assistant. Your role is to help patients:
# 1. Book appointments with doctors
# 2. Cancel existing appointments
# 3. Check available slots
# 4. Find doctors by name or department
#
# Always be polite and professional. When collecting information:
# - Ask for the patient's mobile number to identify them
# - If booking, ask for doctor name or department preference
# - Ask for preferred date for appointments
# - Confirm all details before booking
#
# Use the available functions to:
# - getPatientDetails: Get patient info using mobile number
# - getDoctorDepartmentDetails: Find doctors by name or specialization
# - getAvailableSlots: Check available time slots
# - bookAnAppointment: Book the appointment
# - cancelAppointment: Cancel an existing appointment
#
# Always confirm successful operations with the patient."""
#
# FUNCTIONS = [
#     {
#         "name": "getPatientDetails",
#         "description": "Get patient details using mobile number",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "mobile_number": {
#                     "type": "string",
#                     "description": "The patient's mobile number"
#                 }
#             },
#             "required": ["mobile_number"]
#         }
#     },
#     {
#         "name": "getDoctorDepartmentDetails",
#         "description": "Get doctor details using doctor name or department/specialization",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "doctor_name": {
#                     "type": "string",
#                     "description": "The doctor's name (optional)"
#                 },
#                 "specialization": {
#                     "type": "string",
#                     "description": "The department or specialization (optional)"
#                 }
#             }
#         }
#     },
#     {
#         "name": "getAvailableSlots",
#         "description": "Get available appointment slots for a doctor on a specific date",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "doctor_id": {
#                     "type": "integer",
#                     "description": "The doctor's ID (optional)"
#                 },
#                 "appointment_date": {
#                     "type": "string",
#                     "description": "The requested date in YYYY-MM-DD format"
#                 }
#             },
#             "required": ["appointment_date"]
#         }
#     },
#     {
#         "name": "bookAnAppointment",
#         "description": "Book an appointment for a patient",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "patient_id": {
#                     "type": "integer",
#                     "description": "The patient's ID"
#                 },
#                 "slot_id": {
#                     "type": "integer",
#                     "description": "The slot ID to book"
#                 },
#                 "appointment_date": {
#                     "type": "string",
#                     "description": "The appointment date and time in ISO format"
#                 }
#             },
#             "required": ["patient_id", "slot_id", "appointment_date"]
#         }
#     },
#     {
#         "name": "cancelAppointment",
#         "description": "Cancel an existing appointment",
#         "parameters": {
#             "type": "object",
#             "properties": {
#                 "appointment_id": {
#                     "type": "integer",
#                     "description": "The appointment ID to cancel"
#                 }
#             },
#             "required": ["appointment_id"]
#         }
#     }
# ]
#
#
# def get_or_create_session(session_id: str) -> List[Dict]:
#     if session_id not in conversation_sessions:
#         conversation_sessions[session_id] = [
#             {"role": "system", "content": SYSTEM_PROMPT}
#         ]
#     return conversation_sessions[session_id]
#
#
# def process_chat_message(message: str, session_id: str) -> Dict:
#     """Process a chat message and return AI response with function calls if needed"""
#     messages = get_or_create_session(session_id)
#     messages.append({"role": "user", "content": message})
#
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages,
#         functions=FUNCTIONS,
#         function_call="auto"
#     )
#
#     response_message = response.choices[0].message
#
#     # Check if AI wants to call a function
#     if response_message.function_call:
#         function_name = response_message.function_call.name
#         function_args = json.loads(response_message.function_call.arguments)
#
#         messages.append({
#             "role": "assistant",
#             "content": None,
#             "function_call": {
#                 "name": function_name,
#                 "arguments": response_message.function_call.arguments
#             }
#         })
#
#         return {
#             "type": "function_call",
#             "function_name": function_name,
#             "function_args": function_args,
#             "messages": messages
#         }
#     else:
#         # Regular text response
#         messages.append({
#             "role": "assistant",
#             "content": response_message.content
#         })
#
#         return {
#             "type": "text",
#             "content": response_message.content,
#             "messages": messages
#         }
#
#
# def add_function_result(session_id: str, function_name: str, function_result: str) -> Dict:
#     """Add function execution result and get AI's next response"""
#     messages = get_or_create_session(session_id)
#
#     messages.append({
#         "role": "function",
#         "name": function_name,
#         "content": function_result
#     })
#
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages,
#         functions=FUNCTIONS,
#         function_call="auto"
#     )
#
#     response_message = response.choices[0].message
#
#     # Check if AI wants to call another function
#     if response_message.function_call:
#         function_name = response_message.function_call.name
#         function_args = json.loads(response_message.function_call.arguments)
#
#         messages.append({
#             "role": "assistant",
#             "content": None,
#             "function_call": {
#                 "name": function_name,
#                 "arguments": response_message.function_call.arguments
#             }
#         })
#
#         return {
#             "type": "function_call",
#             "function_name": function_name,
#             "function_args": function_args,
#             "messages": messages
#         }
#     else:
#         messages.append({
#             "role": "assistant",
#             "content": response_message.content
#         })
#
#         return {
#             "type": "text",
#             "content": response_message.content,
#             "messages": messages
#         }
#
#
# def clear_session(session_id: str):
#     """Clear a conversation session"""
#     if session_id in conversation_sessions:
#         del conversation_sessions[session_id]

##third version

from openai import OpenAI
import json
import os
from datetime import datetime
from typing import Dict, List

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store conversation history per session
conversation_sessions: Dict[str, List[Dict]] = {}

SYSTEM_PROMPT = """You are a helpful medical appointment booking assistant. Your role is to help patients:
1. Book appointments with doctors
2. Cancel existing appointments
3. Check available slots
4. Find doctors by name or department

Always be polite and professional. When collecting information:
- Ask for the patient's mobile number to identify them
- If booking, ask for doctor name or department preference
- Ask for preferred date for appointments
- Confirm all details before booking

Use the available functions to:
- getPatientDetails: Get patient info using mobile number
- getDoctorDepartmentDetails: Find doctors by name or specialization
- getAvailableSlots: Check available time slots
- bookAnAppointment: Book the appointment
- cancelAppointment: Cancel an existing appointment

Always confirm successful operations with the patient."""

FUNCTIONS = [
    {
        "name": "getPatientDetails",
        "description": "Get patient details using mobile number",
        "parameters": {
            "type": "object",
            "properties": {
                "mobile_number": {
                    "type": "string",
                    "description": "The patient's mobile number"
                }
            },
            "required": ["mobile_number"]
        }
    },
    {
        "name": "getDoctorDepartmentDetails",
        "description": "Get doctor details using doctor name or department/specialization",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_name": {
                    "type": "string",
                    "description": "The doctor's name (optional)"
                },
                "specialization": {
                    "type": "string",
                    "description": "The department or specialization (optional)"
                }
            }
        }
    },
    {
        "name": "getAvailableSlots",
        "description": "Get available appointment slots for a doctor on a specific date",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_id": {
                    "type": "integer",
                    "description": "The doctor's ID (optional)"
                },
                "appointment_date": {
                    "type": "string",
                    "description": "The requested date in YYYY-MM-DD format"
                }
            },
            "required": ["appointment_date"]
        }
    },
    {
        "name": "bookAnAppointment",
        "description": "Book an appointment for a patient",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_id": {
                    "type": "integer",
                    "description": "The patient's ID"
                },
                "slot_id": {
                    "type": "integer",
                    "description": "The slot ID to book"
                },
                "appointment_date": {
                    "type": "string",
                    "description": "The appointment date and time in ISO format"
                }
            },
            "required": ["patient_id", "slot_id", "appointment_date"]
        }
    },
    {
        "name": "cancelAppointment",
        "description": "Cancel an existing appointment",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "integer",
                    "description": "The appointment ID to cancel"
                }
            },
            "required": ["appointment_id"]
        }
    }
]


def get_or_create_session(session_id: str) -> List[Dict]:
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
    return conversation_sessions[session_id]


def process_chat_message(message: str, session_id: str) -> Dict:
    """Process a chat message and return AI response with function calls if needed"""
    messages = get_or_create_session(session_id)
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            functions=FUNCTIONS,
            function_call="auto"
        )

        response_message = response.choices[0].message

        print(
            f"OpenAI response - has function_call: {hasattr(response_message, 'function_call') and response_message.function_call is not None}")

        # Check if AI wants to call a function
        if hasattr(response_message, 'function_call') and response_message.function_call:
            function_name = response_message.function_call.name
            function_args = json.loads(response_message.function_call.arguments)

            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": function_name,
                    "arguments": response_message.function_call.arguments
                }
            })

            return {
                "type": "function_call",
                "function_name": function_name,
                "function_args": function_args,
                "messages": messages
            }
        else:
            # Regular text response
            content = response_message.content or "I apologize, but I encountered an issue. Could you please try again?"

            messages.append({
                "role": "assistant",
                "content": content
            })

            return {
                "type": "text",
                "content": content,
                "messages": messages
            }
    except Exception as e:
        print(f"Error in process_chat_message: {e}")
        import traceback
        traceback.print_exc()
        return {
            "type": "text",
            "content": "Sorry, there was an error processing your request. Please try again.",
            "messages": messages
        }


def add_function_result(session_id: str, function_name: str, function_result: str) -> Dict:
    """Add function execution result and get AI's next response"""
    messages = get_or_create_session(session_id)

    messages.append({
        "role": "function",
        "name": function_name,
        "content": function_result
    })

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            functions=FUNCTIONS,
            function_call="auto"
        )

        response_message = response.choices[0].message

        # Check if AI wants to call another function
        if hasattr(response_message, 'function_call') and response_message.function_call:
            function_name = response_message.function_call.name
            function_args = json.loads(response_message.function_call.arguments)

            messages.append({
                "role": "assistant",
                "content": None,
                "function_call": {
                    "name": function_name,
                    "arguments": response_message.function_call.arguments
                }
            })

            return {
                "type": "function_call",
                "function_name": function_name,
                "function_args": function_args,
                "messages": messages
            }
        else:
            content = response_message.content or "Thank you for that information. How else can I help you?"

            messages.append({
                "role": "assistant",
                "content": content
            })

            return {
                "type": "text",
                "content": content,
                "messages": messages
            }
    except Exception as e:
        print(f"Error in add_function_result: {e}")
        import traceback
        traceback.print_exc()
        return {
            "type": "text",
            "content": "Sorry, there was an error processing the information. Please try again.",
            "messages": messages
        }


def clear_session(session_id: str):
    """Clear a conversation session"""
    if session_id in conversation_sessions:
        del conversation_sessions[session_id]