"""
PDF Text Cleaner

This module contains functions to clean and standardize text extracted from PDFs,
particularly focusing on handling special page break characters.
"""
import os
import re
import sys

def standardize_page_breaks(input_path, output_path=None):
    """
    Processes a text file from a PDF conversion and standardizes page break characters.
    
    Args:
        input_path (str): Path to the input text file
        output_path (str, optional): Path for the cleaned output file. If None, creates 'output_ready.txt'
                                     in the same directory as the input file.
    
    Returns:
        str: Path to the created output file
    """
    # Validate input file path
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Determine output path if not specified
    if output_path is None:
        input_dir = os.path.dirname(input_path)
        output_path = os.path.join(input_dir, "output_ready.txt")
    
    # Read input file
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    print(f"Read {len(content)} characters from {input_path}")
    
    # Find and replace special page break characters
    # These can appear differently depending on the PDF extraction tool used
    
    # Common page break characters:
    # 1. Form feed character (ASCII 12, \f)
    # 2. Special Unicode characters
    # 3. Custom sequences like "FF", "^L", etc.
    
    # Pattern to look for: sequence of FF characters, form feed chars, or other special markers
    cleaned_content = content
    
    # Replace form feed character
    form_feed_count = cleaned_content.count('\f')
    cleaned_content = cleaned_content.replace('\f', '\n===PAGE_BREAK===\n')
    
    # Replace vertical tab
    vtab_count = cleaned_content.count('\v')
    cleaned_content = cleaned_content.replace('\v', '\n===PAGE_BREAK===\n')
    
    # Replace common PDF page break markers
    markers = [
        '\x0c',                          # Form feed character
        '\u000C',                        # Unicode form feed
        '\u240C',                        # Unicode symbol for form feed
        chr(12),                         # ASCII 12
        'FF',                            # Common FF marker
        '\\u000c',                       # Escaped unicode
        '\\f',                           # Escaped form feed
        '\n\n\n\n\n',                    # Multiple newlines (often indicates page break)
    ]
    
    replacement_count = 0
    for marker in markers:
        count = cleaned_content.count(marker)
        if count > 0:
            cleaned_content = cleaned_content.replace(marker, '\n===PAGE_BREAK===\n')
            replacement_count += count
            print(f"Replaced {count} occurrences of page break marker")
    
    # Look for unusual patterns that often indicate page breaks
    # For example, a line number followed by a title (common in legal documents)
    unusual_breaks = re.findall(r'\n\s*\d+\s*\n[A-Z\s]{5,}', cleaned_content)
    if unusual_breaks:
        print(f"Found {len(unusual_breaks)} potential unusual page break patterns")
    
    # Look for patterns in the text that might indicate page breaks
    # Scan the content for patterns like a line with just numbers (page numbers)
    # or a line with dashes or other separators
    page_number_lines = re.findall(r'\n\s*\d+\s*\n', cleaned_content)
    if page_number_lines:
        print(f"Found {len(page_number_lines)} potential page number lines")
    
    # Write cleaned content to output file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f"Processed file and found:")
    print(f"- Form feed characters: {form_feed_count}")
    print(f"- Vertical tab characters: {vtab_count}")
    print(f"- Other page break markers: {replacement_count}")
    print(f"Cleaned content written to {output_path}")
    
    return output_path

def detect_encoding(file_path):
    """
    Try to detect the encoding of a text file.
    """
    import chardet
    
    # Read a sample of the file
    with open(file_path, 'rb') as f:
        sample = f.read(10000)  # Read first 10KB
    
    result = chardet.detect(sample)
    return result['encoding']

def main():
    """
    Main function to demonstrate the usage of standardize_page_breaks
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Clean and standardize text extracted from PDFs')
    parser.add_argument('input_file', help='Path to the input text file')
    parser.add_argument('--output_file', help='Path for the cleaned output file', default=None)
    parser.add_argument('--verbose', '-v', action='store_true', help='Print detailed information')
    
    args = parser.parse_args()
    
    try:
        output_file = standardize_page_breaks(args.input_file, args.output_file)
        print(f"Successfully processed {args.input_file}")
        print(f"Output saved to {output_file}")
        
        if args.verbose:
            # Print first few lines of output file
            print("\nPreview of processed file:")
            with open(output_file, 'r', encoding='utf-8', errors='replace') as f:
                preview = ''.join(f.readlines()[:20])
                print(preview)
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
