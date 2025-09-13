"""
PDF to Text Converter and Normalizer

This script:
1. Extracts text from PDF files with better handling of spacing using pdfminer.six
2. Standardizes page breaks with clear markers
3. Saves both the raw extracted text and the cleaned version with standardized page breaks
"""

import os
import re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

# Import the page break standardization function
try:
    # Intenta primero importación absoluta (cuando se ejecuta directamente)
    from inspector_functions.txt_cleaner import standardize_page_breaks
except ImportError:
    # Si falla, usa importación relativa (cuando se importa como módulo)
    from .txt_cleaner import standardize_page_breaks


def convert_pdf_to_text(pdf_path):
    """
    Convert a PDF file to plain text using pdfminer.six.
    
    Args:
        pdf_path (str): Path to the PDF file
    
    Returns:
        str: Plain text content of the PDF with proper spacing
    """
    try:
        print(f"[DEBUG] convert_pdf_to_text: Inicio de procesamiento para {pdf_path}")
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"[ERROR] convert_pdf_to_text: El archivo {pdf_path} no existe")
            return ""
        
        # Check if file is a PDF
        if not pdf_path.lower().endswith('.pdf'):
            print(f"[ERROR] convert_pdf_to_text: El archivo {pdf_path} no es un PDF")
            return ""
        
        print(f"[INFO] Processing PDF: {pdf_path}")
        print(f"[DEBUG] convert_pdf_to_text: Tamaño del archivo: {os.path.getsize(pdf_path)} bytes")
        
        # Create a string buffer for the extracted text
        output_string = StringIO()
        
        # Create resource manager
        resource_manager = PDFResourceManager()
        
        # Configure layout analysis parameters for better text extraction
        laparams = LAParams(
            line_margin=0.5,       # Valor moderado para mantener párrafos juntos
            word_margin=0.1,       # Valor estándar para espaciado entre palabras
            char_margin=5.0,       # Valor más alto para no unir demasiado los caracteres
            boxes_flow=0.5,        # Valor estándar para el flujo de texto
            detect_vertical=False,  # Detectar texto vertical
            all_texts=True         # Incluir todo el texto, incluso en figuras
        )
        
        # Create a text converter
        device = TextConverter(resource_manager, output_string, laparams=laparams)
        
        # Create a PDF interpreter
        interpreter = PDFPageInterpreter(resource_manager, device)
        
        # Process each page
        with open(pdf_path, 'rb') as pdf_file:
            for page in PDFPage.get_pages(pdf_file):
                interpreter.process_page(page)
        
        # Close the converter
        device.close()
        
        # Get the text from the string buffer
        text = output_string.getvalue()
        
        print(f"[INFO] Successfully extracted {len(text)} characters of text.")
        print(f"[DEBUG] convert_pdf_to_text: Primeros 100 caracteres: {text[:100].replace(chr(10), '\\n')}")
        
        if len(text) == 0:
            print(f"[WARNING] convert_pdf_to_text: No se extrajo ningún texto del PDF")
        
        return text
    
    except Exception as e:
        import traceback
        print(f"[ERROR] convert_pdf_to_text: Error procesando PDF: {str(e)}")
        print(f"[DEBUG] {traceback.format_exc()}")
        return ""


def save_text_to_file(text, output_path):
    """
    Save text content to a file.
    
    Args:
        text (str): Text content to save
        output_path (str): Path to save the text file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"Text saved to {output_path}")
    except Exception as e:
        print(f"Error saving text to file: {str(e)}")


def compare_preview(text, max_length=200):
    """
    Show a preview of the extracted text.
    
    Args:
        text (str): Extracted text
        max_length (int): Maximum length of the preview
    """
    if not text:
        return
    
    preview = text[:max_length].replace('\n', ' ')
    print(f"Preview: {preview}...")




# Execute the function when this script is run directly
if __name__ == "__main__":
    import os.path
    
    # Input and output file paths with absolute paths
    # Obtenemos la ruta del directorio raíz del proyecto (contract_inspector)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Construimos las rutas absolutas
    input_pdf = os.path.join(root_dir, "input.pdf")
    temp_txt = os.path.join(root_dir, "output_temp.txt")  # Archivo temporal
    output_txt = os.path.join(root_dir, "output.txt")     # Archivo final
    

    # Step 1: Convert PDF to text
    print(f"\n1. Converting {input_pdf} to text using pdfminer.six...")
    extracted_text = convert_pdf_to_text(input_pdf)
    
    if not extracted_text:
        print("Conversion failed. Check the errors above.")
        exit(1)
    
    # Step 2: Save the extracted text to a temporary file
    save_text_to_file(extracted_text, temp_txt)
    
    # Step 3: Show a preview of the extracted text
    print("\n2. Preview of extracted text:")
    compare_preview(extracted_text)
    
    # Step 4: Standardize page breaks and save directly to output.txt
    print(f"\n3. Standardizing page breaks...")
    cleaned_output_path = standardize_page_breaks(temp_txt, output_txt)
    
    # Step 5: Remove the temporary file
    if os.path.exists(temp_txt):
        os.remove(temp_txt)
        print(f"Temporary file removed")
    
    print("\nProcess completed!")
    print(f"- Text with standardized page breaks saved to: {cleaned_output_path}")

