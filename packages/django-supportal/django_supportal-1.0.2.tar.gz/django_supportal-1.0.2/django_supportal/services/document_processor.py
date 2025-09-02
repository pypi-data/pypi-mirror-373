import logging

from typing import List, Tuple

import tiktoken

from django.utils.translation import gettext_lazy as _
from docx import Document as DocxDocument
from PyPDF2 import PdfReader

from ..settings import SUPPORTAL_SETTINGS

logger = logging.getLogger("django_supportal")


class DocumentProcessor:
    def __init__(self):
        self.chunk_size = SUPPORTAL_SETTINGS["CHUNK_SIZE"]
        self.chunk_overlap = SUPPORTAL_SETTINGS["CHUNK_OVERLAP"]
        self.encoding = tiktoken.encoding_for_model(SUPPORTAL_SETTINGS["OPENAI_MODEL"])

    def extract_text(self, file_path: str, file_type: str) -> str:
        """extract text from uploaded file"""
        try:
            if file_type == "pdf":
                return self._extract_pdf_text(file_path)
            elif file_type == "docx":
                return self._extract_docx_text(file_path)
            elif file_type == "txt":
                return self._extract_txt_text(file_path)
            else:
                raise ValueError(
                    _("Unsupported file type: {file_type}").format(file_type=file_type)
                )
        except Exception as e:
            logger.error(f"error extracting text from {file_path}: {str(e)}")
            return ""

    def _extract_pdf_text(self, file_path: str) -> str:
        """extract text from pdf file"""
        text = ""
        with open(file_path, "rb") as file:
            pdf_reader = PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text

    def _extract_docx_text(self, file_path: str) -> str:
        """extract text from docx file"""
        doc = DocxDocument(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def _extract_txt_text(self, file_path: str) -> str:
        """extract text from txt file"""
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

    def chunk_text(self, text: str) -> List[Tuple[str, int]]:
        """split text into chunks with overlap"""
        chunks = []
        tokens = self.encoding.encode(text)

        start = 0
        chunk_index = 0

        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)

            chunks.append((chunk_text, chunk_index))
            chunk_index += 1

            # move start position with overlap
            start = end - self.chunk_overlap

            if start >= len(tokens):
                break

        return chunks

    def preprocess_text(self, text: str) -> str:
        """clean and preprocess text"""
        # remove extra whitespace
        text = " ".join(text.split())

        # remove empty lines
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        return "\n".join(lines)
