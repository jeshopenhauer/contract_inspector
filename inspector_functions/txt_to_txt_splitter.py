"""
Contract Text Splitter

This module contains functions to split a contract text file into separate files
based on specific sections like title, between, and, preamble and articles.
"""
import os
import re

def split_contract_text(input_file_path, output_dir=None):
    """
    Splits a contract text file into separate files for different sections.
    
    Args:
        input_file_path (str): Path to the input text file containing the contract
        output_dir (str, optional): Directory to save output files. If None, will save in the same directory as input file
    
    Returns:
        dict: Dictionary containing paths of created output files
    """
    # If output directory is not specified, use the directory of the input file
    if output_dir is None:
        output_dir = os.path.dirname(input_file_path)
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Validate input file path
    if not os.path.isfile(input_file_path):
        raise FileNotFoundError(f"Input file not found: {input_file_path}")
        
    # Read the input file
    with open(input_file_path, 'r', encoding='utf-8') as f:
        contract_text = f.read()
    
    # Dictionary to store the extracted content
    sections = {}
    output_files = {}
    
    # 1.Extract the title (first line) - from beginning to "Between:" (not including)
    title_match = re.search(r'^(.*?)(?=\s*Between:)', contract_text, re.DOTALL)
    if title_match:
        sections['title'] = title_match.group(1).strip()
    
    # 2.Extract 'Between' section - from "Between:" (included) to "And:" (not including)
    between_match = re.search(r'(Between:.*?)(?=\s*And:)', contract_text, re.DOTALL)
    if between_match:
        sections['between'] = between_match.group(1).strip()
    
    # 3.Extract 'And' section - from "And:" (included) to "Article 1:" (not including)
    and_match = re.search(r'(And:.*?)(?=\s*Article\s+1\s*:)', contract_text, re.DOTALL)
    if and_match:
        sections['and'] = and_match.group(1).strip()
    
    # 4.Extract 'Preamble' section - if present
    preamble_match = re.search(r'(Preamble.*?)(?=\s*Article\s+1\s*:)', contract_text, re.DOTALL)
    if preamble_match:
        sections['preamble'] = preamble_match.group(1).strip()
    
    # 5.Extract Articles 1 to 14
    for i in range(1, 15):  # Articles 1 to 14
        article_pattern = f"(Article\\s*{i}\\s*:.*?)(?=\\s*Article\\s*{i+1}\\s*:|$)"
        article_match = re.search(article_pattern, contract_text, re.DOTALL)
        if article_match:
            sections[f'article_{i}'] = article_match.group(1).strip()
    
    # 6. Extract Article 15 specifically - from "Article 15:" to the end
    article_15_match = re.search(r'(Article\s*15\s*:.*?)$', contract_text, re.DOTALL)
    if article_15_match:
        sections['article_15'] = article_15_match.group(1).strip()
    
    # Write sections to separate files
    for section_name, content in sections.items():
        if content:
            output_file_path = os.path.join(output_dir, f'output_{section_name}.txt')
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            output_files[section_name] = output_file_path
    
    return output_files


def main():
    """
    Main function to demonstrate the usage of the split_contract_text function
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Split contract text file into separate sections')
    parser.add_argument('input_file', help='Path to the input contract text file')
    parser.add_argument('--output_dir', help='Directory to save output files', default='output_split')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print detailed information about extracted sections')
    
    args = parser.parse_args()
    
    # Convert to absolute path
    input_file = os.path.abspath(args.input_file)
    
    # Set default output directory to 'output_split' in the workspace root
    output_dir = args.output_dir
    if output_dir:
        # If the path is relative, make it relative to the workspace root
        if not os.path.isabs(output_dir):
            workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(workspace_root, output_dir)
        output_dir = os.path.abspath(output_dir)
    
    print(f"Processing contract file: {input_file}")
    try:
        output_files = split_contract_text(input_file, output_dir)
        
        print(f"\nContract successfully split into {len(output_files)} files in '{os.path.relpath(os.path.dirname(list(output_files.values())[0]), os.getcwd())}':")
        for section, file_path in sorted(output_files.items()):
            file_size = os.path.getsize(file_path)
            print(f"  - {section}: {os.path.basename(file_path)} ({file_size} bytes)")
            
            if args.verbose and file_size > 0:
                # Print the first few lines of each file
                with open(file_path, 'r', encoding='utf-8') as f:
                    preview = '\n'.join(f.read().split('\n')[:3])
                    print(f"    Preview: {preview[:100]}...")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

def batch_process_contracts(input_dir, output_base_dir=None):
    """
    Process all .txt files in a directory, splitting each into separate section files.
    
    Args:
        input_dir (str): Directory containing contract text files
        output_base_dir (str, optional): Base directory for output files. If None,
                                        subdirectories will be created in the input directory.
    
    Returns:
        dict: Dictionary mapping input files to their respective output file dictionaries
    """
    if not os.path.isdir(input_dir):
        raise ValueError(f"Input directory {input_dir} does not exist")
    
    if output_base_dir is None:
        output_base_dir = input_dir
    
    results = {}
    
    # Find all .txt files in the input directory
    txt_files = [f for f in os.listdir(input_dir) if f.endswith('.txt') and os.path.isfile(os.path.join(input_dir, f))]
    
    if not txt_files:
        print(f"No .txt files found in {input_dir}")
        return results
    
    for txt_file in txt_files:
        input_path = os.path.join(input_dir, txt_file)
        # Create a subdirectory for each input file
        file_base_name = os.path.splitext(txt_file)[0]
        output_dir = os.path.join(output_base_dir, f"{file_base_name}_sections")
        
        try:
            result = split_contract_text(input_path, output_dir)
            results[input_path] = result
        except Exception as e:
            print(f"Error processing {input_path}: {str(e)}")
    
    return results


if __name__ == "__main__":
    # Si no hay argumentos en línea de comandos, usa estos valores predeterminados para pruebas
    import sys
    if len(sys.argv) == 1:
        print("Ejecutando con valores predeterminados para prueba...")
        # Configura rutas absolutas para pruebas
        workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        input_file = os.path.join(workspace_root, "output.txt")
        output_dir = os.path.join(workspace_root, "output_split")
        
        # Asegúrate de que el archivo de entrada existe
        if os.path.isfile(input_file):
            print(f"Procesando archivo: {input_file}")
            print(f"Guardando resultados en: {output_dir}")
            try:
                output_files = split_contract_text(input_file, output_dir)
                
                print(f"\nContrato dividido exitosamente en {len(output_files)} archivos en '{os.path.relpath(output_dir, workspace_root)}':")
                for section, file_path in sorted(output_files.items()):
                    file_size = os.path.getsize(file_path)
                    print(f"  - {section}: {os.path.basename(file_path)} ({file_size} bytes)")
            except Exception as e:
                print(f"Error: {str(e)}")
                sys.exit(1)
        else:
            print(f"Error: No se encontró el archivo de entrada {input_file}")
            sys.exit(1)
    else:
        # Si hay argumentos, ejecuta el comportamiento normal
        main()
