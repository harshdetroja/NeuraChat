
from pydoc import text
import pypdf
import io
import docx
import os

class Parser:
 
    def extract_from_txt(self, file_bytes: bytes) -> list[dict]:
        text = file_bytes.decode("utf-8", errors="ignore").strip()
        if not text:
            return []
        return [{"text": text, "page_number": 1}]
    
    def extract_from_docx(self, file_bytes: bytes) -> list[dict]:
        doc = docx.Document(io.BytesIO(file_bytes))

        results = []

        current_page_text = []
        current_word_count = 0
        page_number = 1

        for p in doc.paragraphs:
            text = p.text.strip()
            if not text:
                continue
            
            words = len(text.split())
            current_page_text.append(text)
            current_word_count += words

            if current_word_count >= 500:
                results.append({
                    "text": " ".join(current_page_text),
                    "page_number": page_number
                })
                current_page_text = []
                current_word_count = 0
                page_number += 1
        
        if current_page_text:
            results.append({
                "text": " ".join(current_page_text),
                "page_number": page_number
            })      
        
        return results
            

    def extract_from_pdf(self,file_bytes: bytes) -> list[dict]:

        reader = pypdf.PdfReader(io.BytesIO(file_bytes))

        results = []
        for idx, page in enumerate(reader.pages):
            page_text = page.extract_text() or ""
            page_text = page_text.strip()
            if page_text:
                results.append({
                    "text": page_text,
                    "page_number": idx + 1
                })
        
        return results

    def extract_text(self, file_bytes:bytes, filename: str) -> list[dict]:
        
        file_extension = os.path.splitext(filename)[1].lower().lstrip(".")

        if file_extension not in ["txt","docx","pdf"]:
            return {"text": None, "error": "Unsupported file type"}
        
        if file_extension == "txt":
            return self.extract_from_txt(file_bytes)
        elif file_extension == "docx":
            return self.extract_from_docx(file_bytes)
        
        return self.extract_from_pdf(file_bytes)
        
parser = Parser()