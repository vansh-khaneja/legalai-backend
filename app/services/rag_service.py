from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
from typing import List

class RagService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

    def pdf_to_text(self, file_stream) -> str:
        # Convert PDF to text
        reader = PdfReader(file_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    def chunk_text(self, text: str) -> List[str]:
        # Chunk the text using recursive splitting
        chunks = self.text_splitter.split_text(text)
        return chunks
