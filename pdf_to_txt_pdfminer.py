"""
PDF to Text Converter and Normalizer

This script:
1. Extracts text from PDF files with better handling of spacing using pdfminer.six
2. Normalizes the text by removing spaces, line breaks, and converting to lowercase
3. Can compare the normalized text with a reference pattern
"""

import os
import re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO


def convert_pdf_to_text(pdf_path):
    """
    Convert a PDF file to plain text using pdfminer.six.
    
    Args:
        pdf_path (str): Path to the PDF file
    
    Returns:
        str: Plain text content of the PDF with proper spacing
    """
    try:
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"Error: File {pdf_path} does not exist.")
            return ""
        
        # Check if file is a PDF
        if not pdf_path.lower().endswith('.pdf'):
            print(f"Error: File {pdf_path} is not a PDF file.")
            return ""
        
        print(f"Processing PDF: {pdf_path}")
        
        # Create a string buffer for the extracted text
        output_string = StringIO()
        
        # Create resource manager
        resource_manager = PDFResourceManager()
        
        # Configure layout analysis parameters for better text extraction
        laparams = LAParams(
            line_margin=0.5,      # Adjust line margin for better line detection
            word_margin=0.1,      # Adjust word margin for better word separation
            char_margin=2.0,      # Character margin
            all_texts=True        # Extract all text, including text in figures
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
        
        print(f"Successfully extracted {len(text)} characters of text.")
        return text
    
    except Exception as e:
        import traceback
        print(f"Error processing PDF: {str(e)}")
        print(traceback.format_exc())
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


def normalize_text(text, remove_placeholders=True):
    """
    Normaliza un texto para comparación, eliminando espacios y opcionalmente placeholders.
    
    Args:
        text (str): Texto a normalizar
        remove_placeholders (bool): Si se deben eliminar los placeholders [texto]
    
    Returns:
        str: Texto normalizado
    """
    # 1. Reemplazar placeholders con texto genérico o eliminarlos
    if remove_placeholders:
        placeholder_pattern = r'\[.*?\]'
        text = re.sub(placeholder_pattern, '', text)
    
    # 2. Convertir a minúsculas para evitar problemas de case
    text = text.lower()
    
    # 3. Eliminar espacios en blanco, tabulaciones y saltos de línea
    text = re.sub(r'\s+', '', text)
    
    return text


def normalize_file(input_path, output_path=None, remove_placeholders=True):
    """
    Normaliza el archivo para que sea comparable con otros textos normalizados.
    
    Args:
        input_path (str): Ruta al archivo de entrada
        output_path (str, optional): Ruta para guardar el archivo normalizado
                                    Si no se proporciona, se usa input_path + '_normalized.txt'
        remove_placeholders (bool): Si se deben eliminar los placeholders [texto]
    
    Returns:
        str: Texto normalizado
    """
    try:
        # Leer el archivo de entrada
        with open(input_path, 'r', encoding='utf-8') as file:
            input_text = file.read()
        
        # Normalizar el texto
        normalized_text = normalize_text(input_text, remove_placeholders)
        
        # Determinar la ruta de salida
        if output_path is None:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_normalized{ext}"
        
        # Guardar el texto normalizado
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(normalized_text)
        
        print(f"Texto normalizado guardado en {output_path}")
        print(f"Longitud del texto original: {len(input_text)}")
        print(f"Longitud del texto normalizado: {len(normalized_text)}")
        return normalized_text
    
    except Exception as e:
        import traceback
        print(f"Error al normalizar el archivo: {str(e)}")
        print(traceback.format_exc())
        return ""


# Execute the function when this script is run directly
if __name__ == "__main__":
    # Input and output file paths
    input_pdf = "input.pdf"
    output_txt = "input.txt"
    normalized_output = "input_normalized.txt"
    
    # Step 1: Convert PDF to text
    print(f"\n1. Converting {input_pdf} to text using pdfminer.six...")
    extracted_text = convert_pdf_to_text(input_pdf)
    
    if not extracted_text:
        print("Conversion failed. Check the errors above.")
        exit(1)
    
    # Step 2: Save the extracted text to file
    save_text_to_file(extracted_text, output_txt)
    
    # Step 3: Show a preview of the extracted text
    print("\n2. Preview of extracted text:")
    compare_preview(extracted_text)
    
    # Step 4: Normalize the extracted text
    print(f"\n3. Normalizing extracted text...")
    normalize_file(output_txt, normalized_output)
    
    print("\nProcess completed!")
    print(f"- Original text saved to: {output_txt}")
    print(f"- Normalized text saved to: {normalized_output}")
    print(f"\nUse '{normalized_output}' as your pattern for comparing with other documents.")
