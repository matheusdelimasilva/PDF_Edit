import unittest
import os
import sys
import tempfile
import shutil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import fitz
from pdf_edit.PDFEditor import PDFEditor

class TestPDFEditor(unittest.TestCase):
    def setUp(self):
        self.editor = PDFEditor()
        self.test_pdf_path = "examples/example.pdf"
        
        # Create a test PDF file
        if not os.path.exists(self.test_pdf_path):
            self.create_test_pdf()

    def tearDown(self):
        # Clean up any edited PDFs that might have been created
        edited_pdf = self.test_pdf_path.replace('.pdf', '_edited.pdf')
        if os.path.exists(edited_pdf):
            os.remove(edited_pdf)

    def create_test_pdf(self):
        """Create a test PDF file with some sample text."""
        c = canvas.Canvas(self.test_pdf_path, pagesize=letter)
        c.drawString(100, 750, "This is a test PDF file. It might contain sensitive information.")
        c.drawString(100, 700, "It contains multiple lines of text.")
        c.drawString(100, 650, "This sensitive information can be edited using PDFEditor")
        c.save()

if __name__ == '__main__':
    test = TestPDFEditor()
    test.setUp()
    test.editor.open_pdf("examples/example.pdf")
    test.editor.set_verbose(True)
    test.editor.edit_text(0, "sensitive", "redacted")