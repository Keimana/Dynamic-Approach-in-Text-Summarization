from tkinter import filedialog, Tk
from docx import Document
import fitz  # PyMuPDF

class FileLoader:
    def open_file(self):
        root = Tk()
        root.withdraw()  # Hide the root window

        file_path = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx"), ("PDF Files", "*.pdf")])
        if not file_path:
            return None, None

        if file_path.endswith('.docx'):
            return self._read_docx(file_path)
        elif file_path.endswith('.pdf'):
            return self._read_pdf(file_path)
        else:
            return None, "Unsupported file format"

    def _read_docx(self, file_path):
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return file_path, '\n'.join(full_text)

    def _read_pdf(self, file_path):
        doc = fitz.open(file_path)
        full_text = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            full_text.append(page.get_text())
        return file_path, '\n'.join(full_text)
