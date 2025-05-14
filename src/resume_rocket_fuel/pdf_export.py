from pathlib import Path
import logging
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import textwrap
import re
import os

# Enhanced Logging Setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Font configuration
SCRIPT_DIR = Path(__file__).parent.absolute()
FONT_DIR = SCRIPT_DIR / "fonts"
FONT_PATH_REGULAR = FONT_DIR / "DejaVuSans.ttf"
FONT_PATH_BOLD = FONT_DIR / "DejaVuSans-Bold.ttf"

def verify_font_file(file_path):
    """Verify that a font file is valid"""
    try:
        with open(file_path, 'rb') as f:
            # Check for TrueType font signature
            signature = f.read(4)
            return signature in [b'\x00\x01\x00\x00', b'true', b'typ1', b'OTTO']
    except Exception as e:
        logger.error(f"Error verifying font file {file_path}: {e}")
        return False

def download_fonts():
    """Download and verify DejaVu fonts"""
    try:
        # Create fonts directory if it doesn't exist
        FONT_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Font directory created/verified at {FONT_DIR}")

        # Font URLs from a more reliable source
        font_urls = {
            FONT_PATH_REGULAR: "https://github.com/liberationfonts/liberation-fonts/raw/main/liberation-fonts-ttf-2.1.5/LiberationSans-Regular.ttf",
            FONT_PATH_BOLD: "https://github.com/liberationfonts/liberation-fonts/raw/main/liberation-fonts-ttf-2.1.5/LiberationSans-Bold.ttf"
        }

        for font_path, url in font_urls.items():
            try:
                # Download to a temporary file first
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.ttf', delete=False) as temp_file:
                    logger.info(f"Downloading font from {url}")
                    import urllib.request
                    urllib.request.urlretrieve(url, temp_file.name)
                    
                    # Verify the downloaded font
                    if verify_font_file(temp_file.name):
                        # If verification passes, move to final location
                        import shutil
                        shutil.move(temp_file.name, str(font_path))
                        logger.info(f"Font downloaded and verified at {font_path}")
                    else:
                        logger.error(f"Downloaded font file is invalid: {font_path}")
                        if temp_file.name:
                            os.unlink(temp_file.name)
                        return False
            except Exception as e:
                logger.error(f"Error downloading font {url}: {e}")
                return False

        # Final verification of all fonts
        all_fonts_valid = all(verify_font_file(str(path)) for path in [FONT_PATH_REGULAR, FONT_PATH_BOLD])
        if not all_fonts_valid:
            logger.error("One or more font files failed verification")
            return False

        return True
    except Exception as e:
        logger.error(f"Error in font download process: {str(e)}")
        return False

def debug_text(text, context=""):
    """Helper function to debug text content"""
    logger.debug(f"{context} Text length: {len(text)}")
    logger.debug(f"{context} Text (raw): {repr(text)}")
    logger.debug(f"{context} Text (normal): {text}")
    # Print character codes for special characters
    special_chars = [(i, char, ord(char)) for i, char in enumerate(text) if ord(char) > 127]
    if special_chars:
        logger.debug(f"{context} Special characters found:")
        for pos, char, code in special_chars:
            logger.debug(f"  Position {pos}: '{char}' (Unicode: {code})")

def sanitize_text(text, context=""):
    """Sanitize text by replacing special characters with ASCII equivalents"""
    try:
        # Replace common special characters with ASCII equivalents
        replacements = {
            ''': "'",  # Right single quote
            ''': "'",  # Left single quote
            '"': '"',  # Right double quote
            '"': '"',  # Left double quote
            '—': '-',  # Em dash
            '–': '-',  # En dash
            '…': '...',  # Ellipsis
            '•': '*',  # Bullet point
            '©': '(c)',  # Copyright
            '®': '(R)',  # Registered trademark
            '™': '(TM)',  # Trademark
            '°': ' degrees',  # Degree symbol
            '±': '+/-',  # Plus-minus
            '×': 'x',  # Multiplication
            '÷': '/',  # Division
            '≤': '<=',  # Less than or equal
            '≥': '>=',  # Greater than or equal
            '≠': '!=',  # Not equal
            '≈': '~',  # Approximately equal
            '∞': 'infinity',  # Infinity
            '∑': 'sum',  # Summation
            '∏': 'product',  # Product
            '∆': 'delta',  # Delta
            '∂': 'd',  # Partial derivative
            '√': 'sqrt',  # Square root
            '∫': 'integral',  # Integral
            '∴': 'therefore',  # Therefore
            '∵': 'because',  # Because
            '∼': '~',  # Tilde
            '≅': '~=',  # Approximately equal
            '≡': '===',  # Identity
            '≤': '<=',  # Less than or equal
            '≥': '>=',  # Greater than or equal
            '⊂': 'subset of',  # Subset
            '⊃': 'superset of',  # Superset
            '⊆': 'subset or equal',  # Subset or equal
            '⊇': 'superset or equal',  # Superset or equal
            '⊕': '(+)',  # Circled plus
            '⊗': '(x)',  # Circled times
            '⊥': '_|_',  # Perpendicular
            '‖': '||',  # Parallel
            '∠': 'angle',  # Angle
            '∧': 'and',  # Logical and
            '∨': 'or',  # Logical or
            '¬': 'not',  # Logical not
            '∃': 'exists',  # Exists
            '∀': 'for all',  # For all
            '∈': 'in',  # Element of
            '∉': 'not in',  # Not element of
            '∋': 'contains',  # Contains
            '∌': 'does not contain',  # Does not contain
            '∩': 'intersection',  # Intersection
            '∪': 'union',  # Union
            '∅': 'empty set',  # Empty set
            '∇': 'nabla',  # Nabla
            '∎': 'QED',  # End of proof
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        # Log the sanitized text for debugging
        logger.debug(f"Sanitizing text: {text}")
        logger.debug(f"After sanitization: {text}")
        
        return text
    except Exception as e:
        logger.error(f"Error sanitizing text: {e}")
        return text

class SimplePDF(FPDF):
    def __init__(self):
        logger.debug("Initializing SimplePDF")
        super().__init__(format='A4')
        self.set_margins(8, 15, 8)
        self.set_auto_page_break(auto=True, margin=15)
        self.font_size_normal = 9
        self.font_size_header = 10
        self.font_size_title = 14
        self.effective_width = self.w - 2 * self.l_margin
        
        # Initialize with Helvetica font
        self.set_font('Helvetica', '', self.font_size_normal)

    def write_text(self, text, context=""):
        """Write text with proper encoding and error handling"""
        if text is None:
            logger.warning(f"Received None text in write_text ({context})")
            return
            
        try:
            # Ensure text is a string
            text = str(text)
            
            # Sanitize the text
            text = sanitize_text(text, context)
            
            # Encode as UTF-8 first, then decode as ASCII with replacement
            encoded_text = text.encode('utf-8', 'replace')
            ascii_text = encoded_text.decode('ascii', 'replace')
            
            # Write the text
            self.write(5, ascii_text)
            
        except Exception as e:
            logger.error(f"Error in write_text: {e}")
            logger.error(f"Problematic text: {text}")
            # Try to write a safe version of the text
            try:
                safe_text = str(text).encode('ascii', 'replace').decode()
                self.write(5, safe_text)
            except Exception as e2:
                logger.error(f"Error writing safe text: {e2}")
                pass

    def calculate_line_breaks(self, text, width):
        """Calculate line breaks for text to fit within a given width"""
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_width = self.get_string_width(word)
            if current_width + word_width <= width:
                current_line.append(word)
                current_width += word_width + self.get_string_width(' ')
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width + self.get_string_width(' ')
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def write_wrapped_cell(self, text, width=None, height=5, align='L', indent=0):
        """Write a cell with text wrapping and proper indentation"""
        try:
            if text is None:
                logger.warning("Received None text in write_wrapped_cell")
                return

            # Convert numeric parameters to float
            width = float(width) if width is not None else self.effective_width
            height = float(height)
            indent = float(indent)

            # Calculate available width
            available_width = width - indent

            # Split text into lines that fit within available width
            lines = []
            words = text.split()
            current_line = []
            current_width = 0

            for word in words:
                word_width = self.get_string_width(word)
                if current_width + word_width <= available_width:
                    current_line.append(word)
                    current_width += word_width + self.get_string_width(' ')
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
                    current_width = word_width + self.get_string_width(' ')

            if current_line:
                lines.append(' '.join(current_line))

            # Write each line with proper indentation
            for line in lines:
                if indent > 0:
                    self.cell(indent, height)
                self.cell(available_width, height, line, ln=True, align=align)

        except Exception as e:
            logger.error(f"Error in write_wrapped_cell: {e}")
            logger.error(f"Problematic text: {text}")
            raise

    def safe_write(self, text, context=""):
        """Safely write text with error handling and debugging"""
        try:
            # Debug the text being processed
            debug_text(text, context)
            
            # Sanitize the text
            text = sanitize_text(text, context)
            
            # Write the text
            self.write_text(text, context)
            
        except Exception as e:
            logger.error(f"Error in safe_write: {e}")
            logger.error(f"Problematic text: {text}")
            # Try to write the text without special characters
            try:
                safe_text = str(text).encode('ascii', 'ignore').decode()
                self.write_text(safe_text, context)
            except Exception as e2:
                logger.error(f"Error writing ASCII text: {e2}")
                # As a last resort, skip this text
                logger.error(f"Skipping problematic text: {text}")
                pass

    def write_header(self, text, level=1):
        """Special method to handle headers of different levels"""
        if level == 1:  # Main title
            self.set_font('Helvetica', 'B', self.font_size_title)
            self.cell(0, 10, self.safe_write(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
            self.ln(5)
        elif level == 2:  # Section headers
            self.set_font('Helvetica', 'B', self.font_size_header)
            self.cell(0, 8, self.safe_write(text), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(2)

    def write_field(self, label, value):
        """Write a field with a label and value"""
        self.set_font('Helvetica', 'B', self.font_size_normal)
        self.cell(43.8003111111111, 6, self.safe_write(label), new_x=XPos.RIGHT, new_y=YPos.TOP)
        
        self.set_font('Helvetica', '', self.font_size_normal)
        self.write_wrapped_cell(150.2012444444444, 6, self.safe_write(value), align="L")
        self.ln()

def process_bold_text(text):
    """Process bold text with debugging"""
    logger.debug(f"Processing bold text: {repr(text)}")
    result = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    logger.debug(f"After bold processing: {repr(result)}")
    return result

def convert_markdown_to_pdf(md_path: Path, pdf_path: Path) -> bool:
    try:
        logger.info(f"🔧 Starting PDF conversion...")
        logger.info(f"📄 Markdown Input Path: {md_path.resolve()}")
        logger.info(f"📄 PDF Output Path: {pdf_path.resolve()}")

        if not md_path.exists():
            logger.error(f"❌ Markdown file not found at {md_path.resolve()}")
            return False

        # Initialize PDF
        pdf = SimplePDF()
        
        pdf.add_page()
        logger.info("PDF initialized and page added")

        with open(md_path, "r", encoding="utf-8") as file:
            logger.debug("Reading markdown file...")
            lines = file.readlines()
            logger.info(f"Read {len(lines)} lines from markdown file")

            in_education_section = False
            for line_num, line in enumerate(lines, 1):
                try:
                    logger.debug(f"\nProcessing line {line_num}: {repr(line.strip())}")
                    
                    # Process and sanitize the line
                    line = sanitize_text(process_bold_text(line.strip()))
                    debug_text(line, f"Line {line_num} after processing")
                    
                    if not line:
                        logger.debug("Empty line - adding spacing")
                        pdf.ln(5)
                        continue

                    # Section detection
                    if line.startswith("## Education"):
                        logger.debug("Entering Education section")
                        in_education_section = True
                    elif line.startswith("## "):
                        logger.debug("Exiting Education section")
                        in_education_section = False

                    # Process different line types
                    try:
                        if line.startswith("# "):
                            logger.debug("Processing H1 header")
                            pdf.write_header(line[2:], level=1)
                        elif line.startswith("## "):
                            logger.debug("Processing H2 header")
                            pdf.write_header(line[3:], level=2)
                        elif line.startswith("### "):
                            logger.debug("Processing H3 header")
                            pdf.write_header(line[4:], level=3)
                        elif line.startswith("**") and in_education_section:
                            logger.debug("Processing education entry")
                            # Special handling for education entries
                            parts = line.split(",", 1)  # Split at first comma
                            if len(parts) == 2:
                                degree = parts[0].strip("*").strip()
                                institution_and_date = parts[1].strip()
                                
                                # Calculate widths
                                pdf.set_font('Helvetica', 'B', pdf.font_size_normal)
                                
                                # Write degree (bold, no wrap)
                                degree_width = pdf.get_string_width(degree + ", ")
                                pdf.cell(degree_width, 6, degree + ",", new_x=XPos.RIGHT)
                                
                                # Write institution and date (normal, can wrap)
                                pdf.set_font('Helvetica', '', pdf.font_size_normal)
                                pdf.write_wrapped_cell(pdf.effective_width - degree_width, 6, institution_and_date)
                            else:
                                # Fallback for unexpected format
                                pdf.write_wrapped_cell(pdf.effective_width, 6, line)
                            pdf.ln(3)
                        elif line.startswith("- "):
                            logger.debug("Processing list item")
                            # Handle bullet points with potential date separators
                            content = line[2:]
                            if " | " in content:
                                # Split content by vertical bars and handle each part
                                items = [item.strip() for item in content.split(" | ")]
                                for i, item in enumerate(items):
                                    if i > 0:
                                        pdf.write_wrapped_cell(10, 6, "-", align="C", no_split=True)
                                    # For contact info, don't split labels
                                    if ":" in item and len(item.split(":")[0]) < 15:  # Assume it's a label if before : is short
                                        label, value = item.split(":", 1)
                                        pdf.write_wrapped_cell(pdf.get_string_width(label + ": "), 6, label + ":", bold=True, no_split=True)
                                        pdf.write_wrapped_cell((pdf.effective_width - 10 * (len(items) - 1)) / len(items) - pdf.get_string_width(label + ": "), 6, value.strip())
                                    else:
                                        pdf.write_wrapped_cell((pdf.effective_width - 10 * (len(items) - 1)) / len(items), 6, item)
                            else:
                                # Regular bullet point
                                pdf.write_wrapped_cell(pdf.effective_width, 6, "- " + content, indent=5)
                            pdf.ln(2)
                        else:
                            logger.debug("Processing regular text or field")
                            if ":" in line and len(line.split(":")[0]) < 15:
                                key, value = line.split(":", 1)
                                logger.debug(f"Processing field - Key: {repr(key)}, Value: {repr(value)}")
                                pdf.write_field(key.strip(), value.strip())
                            else:
                                logger.debug("Processing regular text")
                                pdf.write_wrapped_cell(pdf.effective_width, 6, line)
                            pdf.ln(2)
                    except Exception as e:
                        logger.error(f"Error processing line {line_num}: {str(e)}")
                        logger.error(f"Problematic line: {repr(line)}")
                        raise

                except Exception as e:
                    logger.error(f"Error in line {line_num}: {str(e)}")
                    logger.error(f"Skipping problematic line: {repr(line)}")
                    continue

        pdf.output(str(pdf_path))
        logger.info(f"✅ PDF successfully created at {pdf_path}")
        return True

    except Exception as e:
        logger.error(f"❌ PDF conversion failed: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting PDF conversion script")
    md_input_path = Path("output/final_polished_cv.md")
    pdf_output_path = Path("output/test_cv_output.pdf")
    
    logger.info(f"Input path: {md_input_path}")
    logger.info(f"Output path: {pdf_output_path}")
    
    success = convert_markdown_to_pdf(md_input_path, pdf_output_path)
    
    if success:
        logger.info("🎉 Test completed successfully!")
    else:
        logger.error("❌ Test failed. Review the logs for details.")
