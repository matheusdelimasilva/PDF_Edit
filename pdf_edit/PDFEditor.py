import PyPDF2
from .FontManager import FontManager
import fitz
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class PDFEditor:
    def __init__(self):
        self.current_pdf = None
        self.current_page = None
        self.page_number = 0
        self.filename = None
        self.verbose = False
        self.FontManager = FontManager(verbose=False)

    def set_verbose(self, verbose):
        """Set verbose mode for detailed output."""
        self.verbose = verbose
        self.FontManager.set_verbose(verbose)

    def open_pdf(self, pdf_path):
        """Open a PDF file for editing."""
        try:
            self.current_pdf = PyPDF2.PdfReader(pdf_path)
            self.filename = pdf_path
            self.page_number = 0
            return True
        except Exception as e:
            print(f"Error opening PDF: {str(e)}")
            return False

    def get_page_text(self, page_number):
        """Extract text from a specific page."""
        if not self.current_pdf:
            return None
        
        try:
            page = self.current_pdf.pages[page_number]
            return page.extract_text()
        except Exception as e:
            print(f"Error extracting text: {str(e)}")
            return None

    def redact_text(self, page, text_instance):
        """Remove the original text using redaction."""
        try:
            annot = page.add_redact_annot(text_instance, "")
            page.apply_redactions()
            return True
        except Exception as e:
            print(f"Error redacting text: {str(e)}")
            return False
        
    def get_text_properties(self, page, text_instance):
        """Extract text properties (font, size, color, etc.) from the original text."""
        try:
            font_info = page.get_text("dict", clip=text_instance)
            properties = {
                'font': 'helv',  # default font
                'size': 11,      # default size
                'color': (0, 0, 0)  # default color (black)
            }
            
            # Extract font properties if available
            if isinstance(font_info, dict) and 'blocks' in font_info and font_info['blocks']:
                try:
                    span = font_info['blocks'][0]['lines'][0]['spans'][0]
                    
                    if 'font' in span:
                        properties['font'] = span['font']
                    elif self.verbose:
                        print("Warning: Font information not found in span properties")
                    
                    if 'size' in span:
                        properties['size'] = span['size']
                    elif self.verbose:
                        print("Warning: Font size not found in span properties")
                    
                    if 'color' in span:
                        properties['color'] = span['color']
                    elif self.verbose:
                        print("Warning: Text color not found in span properties")
                    
                    if self.verbose:
                        print(f"Extracted properties from span: {properties}")
                        print(f"Raw span data: {span}")
                    
                except (IndexError, KeyError) as e:
                    if self.verbose:
                        print(f"Warning: Could not access span properties: {str(e)}")
                        print(f"Raw font_info structure: {font_info}")
                
            return properties
        except Exception as e:
            if self.verbose:
                print(f"Error getting text properties: {str(e)}")
            return None

    def insert_new_text(self, page, position, text, properties):
        """Insert new text with the original text properties."""
        try:
            # Built-in fonts in PyMuPDF
            builtin_fonts = {
                'helv', 'tiro', 'cour', 'symb', 'zadb'
            }
            
            font_name = properties['font']
            
            # If font is already a built-in font, use it directly
            if font_name in builtin_fonts:
                use_font = font_name
            else:
                # Try to get the actual font file
                font_file = self.FontManager.find_font(font_name)
                
                if font_file:
                    # Register the font with PyMuPDF
                    try:
                        page.parent.load_font(font_file)
                        use_font = font_name  # Use the actual font name
                        
                        if self.verbose:
                            print(f"Successfully loaded font file: {font_file}")
                    except Exception as e:
                        if self.verbose:
                            print(f"Error loading font {font_file}: {str(e)}")
                        use_font = 'helv'  # Fall back to Helvetica
                else:
                    # Fall back to Helvetica
                    if self.verbose:
                        print(f"Could not find font {font_name}, falling back to Helvetica")
                    use_font = 'helv'
            
            if self.verbose:
                print(f"Using position: {position}")
            
            # Insert the text with the font
            page.insert_text(
                position,
                text,
                fontname=use_font,
                fontsize=properties['size'],
                color=properties['color']
            )
            
            if self.verbose:
                print(f"Inserted text with font: {use_font}")
            
            return True
        except Exception as e:
            if self.verbose:
                print(f"Error inserting new text: {str(e)}")
                print(f"Attempted font properties: {properties}")
            return False
    
    def edit_text(self, page_number, old_text, new_text):
        """Edit text while preserving formatting"""
        
        try:
            # Open the PDF with PyMuPDF
            doc = fitz.open(self.filename)
            page = doc[page_number]

            # Find text instances on the page
            text_instances = page.search_for(old_text)
            
            if not text_instances and self.verbose:
                print(f"Warning: Text '{old_text}' not found on page {page_number}")
            
            # Replace each instance
            for inst in text_instances:
                # Get the original text properties
                properties = self.get_text_properties(page, inst)
                if not properties:
                    continue
                
                # Store rectangle information before redaction
                original_rect = fitz.Rect(inst)
                
                if self.verbose:
                    print(f"Original text rectangle: {original_rect}")
                    print(f"Top-left: {original_rect.tl}, Bottom-right: {original_rect.br}")
                    print(f"Width: {original_rect.width}, Height: {original_rect.height}")
                    
                # Remove the original text
                if not self.redact_text(page, inst):
                    continue
                
                # TODO: actually find out a decent baseline_offset
                font_size = properties['size']
                baseline_offset = font_size + (font_size * 0.08)
                
                # Calculate the position for the new text based on the original rectangle
                text_position = fitz.Point(
                    original_rect.x0,  # Keep x the same (left aligned)
                    original_rect.y0 + baseline_offset  # Adjust y for baseline
                )
                
                # Insert the new text with original properties
                if not self.insert_new_text(page, text_position, new_text, properties):
                    continue
            
            # Save the final modified document
            output_path = self.filename.replace('.pdf', '_edited.pdf')
            doc.save(output_path)
            return True
            
        except Exception as e:
            print(f"Error editing text with formatting: {str(e)}")
            return False

    def save_pdf(self, output_path):
        """Save the current PDF to a new file."""
        if not self.current_pdf:
            return False

        try:
            writer = PyPDF2.PdfWriter()
            for page in self.current_pdf.pages:
                writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            return True
        except Exception as e:
            print(f"Error saving PDF: {str(e)}")
            return False
