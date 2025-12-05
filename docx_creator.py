from docx import Document
import datetime

def create_docx(summary_text: str) -> str:
    doc = Document()
    doc.add_heading("Haftalık Rapor", 0)
    doc.add_paragraph(summary_text)
    filename = f"rapor_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"
    doc.save(filename)
    return filename
