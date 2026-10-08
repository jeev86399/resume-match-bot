import os
import fitz  # PyMuPDF
from docx import Document

def parse_pdf(filepath: str) -> str:
    text = ""
    try:
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text("text") + "\n"
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return ""
    return text.strip()

def parse_docx(filepath: str) -> str:
    text = ""
    try:
        doc = Document(filepath)
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text.strip() + "\n"
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text += cell.text.strip() + " "
                text += "\n"
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
        return ""
    return text.strip()

def parse_txt(filepath: str) -> str:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read().strip()
        except Exception:
            return ""
    except Exception as e:
        print(f"Error parsing TXT: {e}")
        return ""

def parse_document(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    
    if ext == '.pdf':
        text = parse_pdf(filepath)
    elif ext == '.docx':
        text = parse_docx(filepath)
    elif ext == '.txt':
        text = parse_txt(filepath)
        
    return _normalize_text(text)

def _normalize_text(text: str) -> str:
    if not text:
        return ""
    # Simple normalization: reduce multiple newlines and spaces
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join([line for line in lines if line])
    return text
