# from sqlalchemy.orm import Session
# from fastapi import UploadFile, HTTPException
# from patient_fao_agent.app.models.database_models import AIChatHistory
# from patient_fao_agent.app.models.schema_models import DocumentUploadResponse
# from patient_fao_agent.app.services.ai_service import AIService
# from patient_fao_agent.app.services.patient_service import PatientService
# from patient_fao_agent.app.config import settings
# import pdfplumber
# import pytesseract
# from PIL import Image
# from pdf2image import convert_from_bytes
# import io
# import uuid
#
#
# class DocumentService:
#     def __init__(self, db: Session):
#         self.db = db
#         self.ai_service = AIService()
#         self.patient_service = PatientService(db)
#
#     async def process_document(
#             self,
#             patient_id: int,
#             file: UploadFile
#     ) -> DocumentUploadResponse:
#         """Process uploaded medical document"""
#         try:
#             # Validate file
#             if file.content_type not in settings.ALLOWED_FILE_TYPES:
#                 raise HTTPException(status_code=400, detail="Only PDF files are allowed")
#
#             # Get patient info
#             patient = await self.patient_service.get_patient_by_id(patient_id)
#
#             # Read file
#             file_content = await file.read()
#             file_size_mb = len(file_content) / (1024 * 1024)
#
#             if file_size_mb > settings.MAX_FILE_SIZE_MB:
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
#                 )
#
#             # Extract text from PDF
#             extracted_text = await self._extract_text_from_pdf(file_content)
#
#             if not extracted_text or len(extracted_text.strip()) < 50:
#                 return DocumentUploadResponse(
#                     success=False,
#                     message="Could not extract meaningful text from the document"
#                 )
#
#             # Anonymize and structure data using Groq
#             anonymized_data = await self.ai_service.anonymize_medical_text(extracted_text)
#
#             # Generate patient explanation using OpenAI
#             explanation = await self.ai_service.generate_patient_explanation(
#                 medical_data=anonymized_data,
#                 patient_name=patient.patient_name
#             )
#
#             # Generate unique document number
#             doc_number = f"DOC-{uuid.uuid4().hex[:8].upper()}"
#
#             # Store in database
#             chat_record = AIChatHistory(
#                 patient_id=patient_id,
#                 document_number=doc_number,
#                 document={
#                     "type": "document_upload",
#                     "filename": file.filename,
#                     "anonymized_data": anonymized_data,
#                     "explanation": explanation,
#                     "document_number": doc_number
#                 }
#             )
#
#             self.db.add(chat_record)
#             self.db.commit()
#             self.db.refresh(chat_record)
#
#             return DocumentUploadResponse(
#                 success=True,
#                 message="Document processed successfully",
#                 chat_id=chat_record.id,
#                 explanation=explanation
#             )
#
#         except HTTPException:
#             raise
#         except Exception as e:
#             self.db.rollback()
#             raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
#
#     async def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
#         """Extract text from PDF using pdfplumber and OCR fallback"""
#         text = ""
#
#         try:
#             # Try pdfplumber first (for text-based PDFs)
#             with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
#                 for page in pdf.pages[:10]:  # Limit to first 10 pages
#                     page_text = page.extract_text()
#                     if page_text:
#                         text += page_text + "\n"
#
#             # If no text extracted, use OCR
#             if len(text.strip()) < 50:
#                 text = await self._extract_text_with_ocr(pdf_bytes)
#
#             return text
#
#         except Exception as e:
#             # Fallback to OCR if pdfplumber fails
#             try:
#                 return await self._extract_text_with_ocr(pdf_bytes)
#             except Exception as ocr_error:
#                 raise Exception(f"Text extraction failed: {str(e)}, OCR: {str(ocr_error)}")
#
#     async def _extract_text_with_ocr(self, pdf_bytes: bytes) -> str:
#         """Extract text using OCR (for image-based PDFs)"""
#         try:
#             # Convert PDF to images
#             images = convert_from_bytes(pdf_bytes, first_page=1, last_page=10)
#
#             text = ""
#             for image in images:
#                 # Perform OCR
#                 page_text = pytesseract.image_to_string(image)
#                 text += page_text + "\n"
#
#             return text
#
#         except Exception as e:
#             raise Exception(f"OCR extraction failed: {str(e)}")

# ##second version
# from sqlalchemy.orm import Session
# from fastapi import UploadFile, HTTPException
# from patient_fao_agent.app.models.database_models import AIChatHistory
# from patient_fao_agent.app.models.schema_models import DocumentUploadResponse
# from patient_fao_agent.app.services.ai_service import AIService
# from patient_fao_agent.app.services.patient_service import PatientService
# from patient_fao_agent.app.config import settings
# import pdfplumber
# import pytesseract
# from PIL import Image
# from pdf2image import convert_from_bytes
# import io
# import uuid
#
#
# class DocumentService:
#     def __init__(self, db: Session):
#         self.db = db
#         self.ai_service = AIService()
#         self.patient_service = PatientService(db)
#
#     async def process_document(
#             self,
#             patient_id: int,
#             file: UploadFile
#     ) -> DocumentUploadResponse:
#         """Process uploaded medical document"""
#         try:
#             print(f"\n{'=' * 50}")
#             print(f"[Step 1] Starting document processing for patient ID: {patient_id}")
#             print(f"[Step 1] File: {file.filename}, Type: {file.content_type}")
#
#             # Validate file
#             if file.content_type not in settings.ALLOWED_FILE_TYPES:
#                 raise HTTPException(status_code=400, detail="Only PDF files are allowed")
#
#             # Get patient info
#             patient = await self.patient_service.get_patient_by_id(patient_id)
#             print(f"[Step 1] Patient verified: {patient.patient_name}")
#
#             # Read file
#             file_content = await file.read()
#             file_size_mb = len(file_content) / (1024 * 1024)
#             print(f"[Step 1] File size: {file_size_mb:.2f} MB")
#
#             if file_size_mb > settings.MAX_FILE_SIZE_MB:
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
#                 )
#
#             # Extract text from PDF
#             print(f"[Step 2] Extracting text from PDF...")
#             extracted_text = await self._extract_text_from_pdf(file_content)
#             print(f"[Step 2] Extracted {len(extracted_text)} characters")
#
#             if not extracted_text or len(extracted_text.strip()) < 50:
#                 return DocumentUploadResponse(
#                     success=False,
#                     message="Could not extract meaningful text from the document"
#                 )
#
#             # Anonymize and structure data using Groq
#             print(f"[Step 3] Anonymizing data with Groq...")
#             anonymized_data = await self.ai_service.anonymize_medical_text(extracted_text)
#             print(f"[Step 3] Data anonymized and structured")
#
#             # Generate patient explanation using OpenAI
#             print(f"[Step 4] Generating patient explanation with OpenAI...")
#             explanation = await self.ai_service.generate_patient_explanation(
#                 medical_data=anonymized_data,
#                 patient_name=patient.patient_name
#             )
#             print(f"[Step 4] Explanation generated successfully")
#
#             # Generate unique document number
#             doc_number = f"DOC-{uuid.uuid4().hex[:8].upper()}"
#             print(f"[Step 5] Storing in database with doc number: {doc_number}")
#
#             # Store in database
#             chat_record = AIChatHistory(
#                 patient_id=patient_id,
#                 document_number=doc_number,
#                 document={
#                     "type": "document_upload",
#                     "filename": file.filename,
#                     "anonymized_data": anonymized_data,
#                     "explanation": explanation,
#                     "document_number": doc_number
#                 }
#             )
#
#             self.db.add(chat_record)
#             self.db.commit()
#             self.db.refresh(chat_record)
#
#             print(f"[Step 5] Document processing complete! Chat ID: {chat_record.id}")
#             print(f"{'=' * 50}\n")
#
#             return DocumentUploadResponse(
#                 success=True,
#                 message="Document processed successfully",
#                 chat_id=chat_record.id,
#                 explanation=explanation
#             )
#
#         except HTTPException as he:
#             self.db.rollback()
#             raise he
#         except Exception as e:
#             self.db.rollback()
#             import traceback
#             error_detail = traceback.format_exc()
#             print(f"Document processing error: {error_detail}")
#             raise HTTPException(
#                 status_code=500,
#                 detail=f"Error processing document: {str(e)}"
#             )
#
#     async def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
#         """Extract text from PDF using pdfplumber and OCR fallback"""
#         text = ""
#
#         try:
#             # Try pdfplumber first (for text-based PDFs)
#             with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
#                 for page in pdf.pages[:10]:  # Limit to first 10 pages
#                     page_text = page.extract_text()
#                     if page_text:
#                         text += page_text + "\n"
#
#             # If no text extracted, use OCR
#             if len(text.strip()) < 50:
#                 text = await self._extract_text_with_ocr(pdf_bytes)
#
#             return text
#
#         except Exception as e:
#             # Fallback to OCR if pdfplumber fails
#             try:
#                 return await self._extract_text_with_ocr(pdf_bytes)
#             except Exception as ocr_error:
#                 raise Exception(f"Text extraction failed: {str(e)}, OCR: {str(ocr_error)}")
#
#     async def _extract_text_with_ocr(self, pdf_bytes: bytes) -> str:
#         """Extract text using OCR (for image-based PDFs)"""
#         try:
#             # Convert PDF to images
#             images = convert_from_bytes(pdf_bytes, first_page=1, last_page=10)
#
#             text = ""
#             for image in images:
#                 # Perform OCR
#                 page_text = pytesseract.image_to_string(image)
#                 text += page_text + "\n"
#
#             return text
#
#         except Exception as e:
#             raise Exception(f"OCR extraction failed: {str(e)}")
#
#

#third version

from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
from patient_fao_agent.app.models.database_models import AIChatHistory
from patient_fao_agent.app.models.schema_models import DocumentUploadResponse
from patient_fao_agent.app.services.ai_service import AIService
from patient_fao_agent.app.services.patient_service import PatientService
from patient_fao_agent.app.config import settings
import io
import uuid

# Try to import PDF processing libraries
try:
    import pdfplumber

    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("WARNING: pdfplumber not installed")

try:
    import pytesseract

    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False
    print("WARNING: pytesseract not installed")

try:
    from pdf2image import convert_from_bytes
    from PIL import Image

    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    print("WARNING: pdf2image not installed")


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
        self.patient_service = PatientService(db)

    async def process_document(
            self,
            patient_id: int,
            file: UploadFile
    ) -> DocumentUploadResponse:
        """Process uploaded medical document"""
        try:
            print(f"\n{'=' * 50}")
            print(f"[Step 1] Starting document processing for patient ID: {patient_id}")
            print(f"[Step 1] File: {file.filename}, Type: {file.content_type}")

            # Validate file
            if file.content_type not in settings.ALLOWED_FILE_TYPES:
                raise HTTPException(status_code=400, detail="Only PDF files are allowed")

            # Get patient info
            patient = await self.patient_service.get_patient_by_id(patient_id)
            print(f"[Step 1] Patient verified: {patient.patient_name}")

            # Read file
            file_content = await file.read()
            file_size_mb = len(file_content) / (1024 * 1024)
            print(f"[Step 1] File size: {file_size_mb:.2f} MB")

            if file_size_mb > settings.MAX_FILE_SIZE_MB:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds {settings.MAX_FILE_SIZE_MB}MB limit"
                )

            # Extract text from PDF
            print(f"[Step 2] Extracting text from PDF...")
            extracted_text = await self._extract_text_from_pdf(file_content)
            print(f"[Step 2] Extracted {len(extracted_text)} characters")

            if not extracted_text or len(extracted_text.strip()) < 50:
                return DocumentUploadResponse(
                    success=False,
                    message="Could not extract meaningful text from the document"
                )

            # Anonymize and structure data using Groq
            print(f"[Step 3] Anonymizing data with Groq...")
            anonymized_data = await self.ai_service.anonymize_medical_text(extracted_text)
            print(f"[Step 3] Data anonymized and structured")

            # Generate patient explanation using OpenAI
            print(f"[Step 4] Generating patient explanation with OpenAI...")
            explanation = await self.ai_service.generate_patient_explanation(
                medical_data=anonymized_data,
                patient_name=patient.patient_name
            )
            print(f"[Step 4] Explanation generated successfully")

            # Generate unique document number
            doc_number = f"DOC-{uuid.uuid4().hex[:8].upper()}"
            print(f"[Step 5] Storing in database with doc number: {doc_number}")

            # Store in database
            chat_record = AIChatHistory(
                patient_id=patient_id,
                document_number=doc_number,
                document={
                    "type": "document_upload",
                    "filename": file.filename,
                    "anonymized_data": anonymized_data,
                    "explanation": explanation,
                    "document_number": doc_number
                }
            )

            self.db.add(chat_record)
            self.db.commit()
            self.db.refresh(chat_record)

            print(f"[Step 5] Document processing complete! Chat ID: {chat_record.id}")
            print(f"{'=' * 50}\n")

            return DocumentUploadResponse(
                success=True,
                message="Document processed successfully",
                chat_id=chat_record.id,
                explanation=explanation
            )

        except HTTPException as he:
            self.db.rollback()
            raise he
        except Exception as e:
            self.db.rollback()
            import traceback
            error_detail = traceback.format_exc()
            print(f"Document processing error: {error_detail}")
            raise HTTPException(
                status_code=500,
                detail=f"Error processing document: {str(e)}"
            )

    async def _extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """Extract text from PDF using pdfplumber and OCR fallback"""

        if not PDFPLUMBER_AVAILABLE:
            raise Exception(
                "pdfplumber is not installed. Install with: pip install pdfplumber"
            )

        text = ""

        try:
            print("[Text Extraction] Attempting pdfplumber extraction...")
            # Try pdfplumber first (for text-based PDFs)
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                page_count = len(pdf.pages)
                print(f"[Text Extraction] PDF has {page_count} pages")

                for i, page in enumerate(pdf.pages[:10]):  # Limit to first 10 pages
                    print(f"[Text Extraction] Processing page {i + 1}...")
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            print(f"[Text Extraction] pdfplumber extracted {len(text)} characters")

            # If no text extracted, use OCR
            if len(text.strip()) < 50:
                if not PYTESSERACT_AVAILABLE or not PDF2IMAGE_AVAILABLE:
                    raise Exception(
                        "Document appears to be image-based but OCR libraries are not available. "
                        "Install with: pip install pytesseract pdf2image pillow\n"
                        "Also install Tesseract OCR on your system."
                    )
                print("[Text Extraction] Insufficient text, attempting OCR...")
                text = await self._extract_text_with_ocr(pdf_bytes)

            return text

        except Exception as e:
            error_msg = str(e)
            print(f"[Text Extraction] Error: {error_msg}")

            # Check if it's a dependency issue
            if "not installed" in error_msg or "not available" in error_msg:
                raise Exception(error_msg)

            # Fallback to OCR if pdfplumber fails
            if PYTESSERACT_AVAILABLE and PDF2IMAGE_AVAILABLE:
                try:
                    print("[Text Extraction] Falling back to OCR...")
                    return await self._extract_text_with_ocr(pdf_bytes)
                except Exception as ocr_error:
                    print(f"[Text Extraction] OCR also failed: {str(ocr_error)}")
                    raise Exception(
                        f"Could not extract text from PDF. "
                        f"Please ensure the PDF contains readable text or images. "
                        f"Error details: {str(e)}"
                    )
            else:
                raise Exception(
                    f"Text extraction failed and OCR is not available. "
                    f"Error: {error_msg}"
                )

    async def _extract_text_with_ocr(self, pdf_bytes: bytes) -> str:
        """Extract text using OCR (for image-based PDFs)"""
        try:
            print("[OCR] Converting PDF pages to images...")
            # Convert PDF to images
            images = convert_from_bytes(pdf_bytes, first_page=1, last_page=10, dpi=150)
            print(f"[OCR] Converted to {len(images)} images")

            text = ""
            for i, image in enumerate(images):
                print(f"[OCR] Processing image {i + 1}/{len(images)}...")
                # Perform OCR
                page_text = pytesseract.image_to_string(image)
                text += page_text + "\n"

            print(f"[OCR] Total extracted text: {len(text)} characters")
            return text

        except Exception as e:
            print(f"[OCR] Error: {str(e)}")
            raise Exception(f"OCR extraction failed: {str(e)}")