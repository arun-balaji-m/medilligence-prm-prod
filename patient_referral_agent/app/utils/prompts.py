# PATIENT_INFO_PROMPT = """You are collecting patient information for referral. Ask ONE question at a time.
#
# Required fields: name, date of birth (YYYY-MM-DD), gender, mobile number, email (optional).
#
# Current data: {patient_data}
#
# User message: {message}
#
# Extract any new information and respond with:
# 1. If data incomplete: Ask next missing field naturally
# 2. If data complete: Confirm and ask about medical history
#
# Respond in JSON:
# {{"response": "your question", "patient_data": {{"name": "...", "dob": "...", "gender": "...", "mobile": "...", "email": "..."}}, "complete": true/false}}"""
#
# HISTORY_COLLECTION_PROMPT = """Collect medical history conversationally. Ask about previous conditions, treatments, dates.
#
# Existing timeline: {timeline}
#
# User message: {message}
#
# Extract medical events with dates. Respond in JSON:
# {{"response": "your question/confirmation", "events": [{{"date": "YYYY-MM-DD", "condition": "...", "treatment": "...", "notes": "..."}}], "needs_more": true/false}}"""
#
# SANITIZE_PROMPT = """Remove all PII (names, IDs, addresses, phone numbers) from this medical text. Keep only clinical information.
#
# Text: {text}
#
# Return sanitized text only."""
#
# TIMELINE_CREATION_PROMPT = """Convert medical information into structured timeline events.
#
# Medical data: {data}
#
# Create timeline events in JSON:
# {{
#   "timeline": [
#     {{
#       "date": "YYYY-MM-DD",
#       "title": "Brief title (5-7 words)",
#       "summary": "One sentence summary",
#       "details": "Full clinical details",
#       "category": "diagnosis/treatment/procedure/consultation"
#     }}
#   ],
#   "summary": "Overall patient journey summary (2-3 sentences)"
# }}
#
# Order chronologically. Be concise in title/summary."""


##second version
#
# PATIENT_INFO_PROMPT = """Extract patient information from the conversation and ask for missing required fields ONE at a time.
#
# Required fields:
# - patient_name (full name)
# - dob (date of birth in YYYY-MM-DD format)
# - gender (Male/Female/Other)
# - mobile_number (10 digit phone number)
# - email (optional, email address)
#
# Current collected data:
# {patient_data}
#
# User's latest message: "{message}"
#
# Instructions:
# 1. Extract ANY new information from the user's message and add it to patient_data
# 2. If a required field is still missing, ask for the NEXT missing field
# 3. If all required fields are complete, set complete=true and ask about medical history
#
# Respond ONLY with valid JSON in this exact format:
# {{
#   "response": "your question or confirmation",
#   "patient_data": {{
#     "patient_name": "extracted name or null",
#     "dob": "YYYY-MM-DD or null",
#     "gender": "Male/Female/Other or null",
#     "mobile_number": "phone number or null",
#     "email": "email or null"
#   }},
#   "complete": true or false
# }}
#
# Example:
# User: "Arun M"
# Response: {{"response": "Nice to meet you, Arun M! What is your date of birth (YYYY-MM-DD)?", "patient_data": {{"patient_name": "Arun M", "dob": null, "gender": null, "mobile_number": null, "email": null}}, "complete": false}}"""
#
# HISTORY_COLLECTION_PROMPT = """You are collecting medical history information conversationally.
#
# Existing timeline events:
# {timeline}
#
# User's message: "{message}"
#
# Extract medical events from the user's message. Look for:
# - Conditions/diagnoses
# - Treatments/medications
# - Procedures/surgeries
# - Consultation dates
# - Hospital visits
#
# If the user wants to upload a document instead, acknowledge it.
# If you have enough information, ask if there's anything else to add.
#
# Respond ONLY with valid JSON:
# {{
#   "response": "your question or confirmation",
#   "events": [
#     {{
#       "date": "YYYY-MM-DD or approximate date",
#       "condition": "medical condition",
#       "treatment": "treatment received",
#       "notes": "additional details"
#     }}
#   ],
#   "needs_more": true or false
# }}
#
# If user says they want to upload a document or have nothing more to add, set needs_more to false."""
#
# SANITIZE_PROMPT = """Remove all personally identifiable information (PII) from this medical document while keeping all clinical information.
#
# Remove:
# - Patient names
# - ID numbers (MRN, SSN, etc.)
# - Addresses
# - Phone numbers
# - Email addresses
# - Dates of birth
#
# Keep:
# - Medical conditions
# - Diagnoses
# - Treatment details
# - Medications
# - Procedure dates (relative to admission/visit)
# - Test results
# - Clinical observations
#
# Text:
# {text}
#
# Return only the sanitized clinical text without any preamble."""
#
# TIMELINE_CREATION_PROMPT = """Convert medical information into a structured timeline with chronological events.
#
# Medical data:
# {data}
#
# Create a timeline with events in JSON format. Be concise and clear.
#
# Return ONLY valid JSON in this exact format:
# {{
#   "timeline": [
#     {{
#       "date": "YYYY-MM-DD",
#       "title": "Brief 5-7 word title",
#       "summary": "One sentence summary (max 20 words)",
#       "details": "Full clinical details and relevant information",
#       "category": "diagnosis" or "treatment" or "procedure" or "consultation"
#     }}
#   ],
#   "summary": "Overall patient journey in 2-3 sentences"
# }}
#
# Sort events chronologically from oldest to newest."""


##third version

PATIENT_INFO_PROMPT = """Extract patient information from the conversation. Track which fields have been asked.

Required fields:
- patient_name (full name)
- dob (date of birth - convert ANY date format to YYYY-MM-DD)
- gender (Male/Female/Other)
- mobile_number (phone number)
- email (optional - if user says they don't have it, mark as "none")

Current state:
Collected data: {patient_data}
Already asked: {asked_fields}

User's message: "{message}"

CRITICAL RULES:
1. Extract information from user's message
2. Convert dates to YYYY-MM-DD (e.g., "2nd October 2020" → "2020-10-02", "7 July 2025" → "2025-07-07")
3. NEVER ask for the same field twice - check already_asked list
4. If user says they don't have email, set email to "none" and move on
5. Ask only ONE question for the NEXT field not yet asked
6. When all required fields collected or asked, set complete=true

Respond ONLY with valid JSON:
{{
  "response": "your question or confirmation",
  "patient_data": {{
    "patient_name": "value or null",
    "dob": "YYYY-MM-DD or null", 
    "gender": "value or null",
    "mobile_number": "value or null",
    "email": "value or 'none' or null"
  }},
  "asked_fields": ["list of all fields asked so far"],
  "complete": true or false
}}

Examples:
User: "2nd October 2020"
Response: {{"response": "Thank you! What is your gender?", "patient_data": {{"patient_name": "Arun M", "dob": "2020-10-02", ...}}, "asked_fields": ["patient_name", "dob"], "complete": false}}

User: "I don't have email"
Response: {{"response": "No problem! I've collected all your information. Now, would you like to...", "patient_data": {{..., "email": "none"}}, "asked_fields": ["patient_name", "dob", "gender", "mobile_number", "email"], "complete": true}}"""

HISTORY_COLLECTION_PROMPT = """You are collecting medical history information conversationally.

Existing timeline events:
{timeline}

User's message: "{message}"

Extract medical events from the user's message. Look for:
- Conditions/diagnoses
- Treatments/medications
- Procedures/surgeries
- Consultation dates
- Hospital visits

Handle date formats flexibly - convert to YYYY-MM-DD or use "YYYY-MM" or "YYYY" if only partial date given.

If the user wants to upload a document instead, acknowledge it.
If you have enough information, ask if there's anything else to add.

Respond ONLY with valid JSON:
{{
  "response": "your question or confirmation",
  "events": [
    {{
      "date": "YYYY-MM-DD or YYYY-MM or YYYY",
      "condition": "medical condition",
      "treatment": "treatment received",
      "notes": "additional details"
    }}
  ],
  "needs_more": true or false
}}

If user says they want to upload a document or have nothing more to add, set needs_more to false."""

SANITIZE_PROMPT = """Remove all personally identifiable information (PII) from this medical document while keeping all clinical information.

Remove:
- Patient names
- ID numbers (MRN, SSN, etc.)
- Addresses
- Phone numbers
- Email addresses
- Dates of birth

Keep:
- Medical conditions
- Diagnoses
- Treatment details
- Medications
- Procedure dates (relative to admission/visit)
- Test results
- Clinical observations

Text:
{text}

Return only the sanitized clinical text without any preamble."""

TIMELINE_CREATION_PROMPT = """Convert medical information into a structured timeline with chronological events.

Medical data:
{data}

Create a timeline with events in JSON format. Be concise and clear.

Return ONLY valid JSON in this exact format:
{{
  "timeline": [
    {{
      "date": "YYYY-MM-DD",
      "title": "Brief 5-7 word title",
      "summary": "One sentence summary (max 20 words)",
      "details": "Full clinical details and relevant information",
      "category": "diagnosis" or "treatment" or "procedure" or "consultation"
    }}
  ],
  "summary": "Overall patient journey in 2-3 sentences"
}}

Sort events chronologically from oldest to newest."""