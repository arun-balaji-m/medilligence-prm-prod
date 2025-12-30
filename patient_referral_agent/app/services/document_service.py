import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile
from typing import List


class DocumentService:
    @staticmethod
    def pdf_to_text(pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber and OCR fallback"""
        text = ""

        # Try pdfplumber first
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Pdfplumber error: {e}")

        # If no text extracted, use OCR
        if len(text.strip()) < 100:
            text = DocumentService._ocr_pdf(pdf_path)

        return text.strip()

    @staticmethod
    def _ocr_pdf(pdf_path: str) -> str:
        """Extract text using OCR (pytesseract)"""
        text = ""

        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)

            for i, image in enumerate(images):
                # Save temporary image
                img_path = os.path.join(temp_dir, f"page_{i}.png")
                image.save(img_path, "PNG")

                # OCR
                page_text = pytesseract.image_to_string(Image.open(img_path))
                text += page_text + "\n"

        return text.strip()

    @staticmethod
    def chunk_text(text: str, max_chars: int = 4000) -> List[str]:
        """Split text into chunks for processing"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word) + 1
            if current_length + word_length > max_chars:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks