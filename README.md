# PDF Text Editor

A Python-based basic PDF editor that allows you to modify text in PDF files. 
It is a work in progress.

## Prerequisites

- Python 3.7 or higher
- Poppler

### Installing Poppler

#### macOS
```bash
# Install Poppler
brew install poppler
```

#### Ubuntu/Debian
```bash
sudo apt-get install poppler-utils
```

#### Windows
Download poppler from: http://blog.alivate.com.au/poppler-windows/

After installing Poppler, you can verify the installation by running:
```bash
# On macOS/Linux
pdfinfo -v

# On Windows
pdfinfo.exe --version
```

If you see a version number, Poppler is installed correctly.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PDF_Edit
```

2. Install the package in development mode:
```bash
pip install -e .
```

## Usage

```python
from pdf_edit.PDFEditor import PDFEditor

# Create an editor instance
editor = PDFEditor()

# Open a PDF file
editor.open_pdf("path/to/your.pdf")

# Edit text while preserving formatting
editor.edit_text(page_number=0, old_text="original text", new_text="new text")
```

## Running Tests

```bash
python -m pytest test/
```

## Limitations

- Text editing is currently limited to replacing existing text
- The editor preserves the original PDF structure but may not maintain exact formatting
- Complex PDFs with multiple layers or special formatting may not be fully supported