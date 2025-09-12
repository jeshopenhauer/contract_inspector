"""
Script to normalize both the NDA template and input text files for comparison.

This script processes both files to remove all whitespace, line breaks, and convert
to lowercase to facilitate comparison between the template and the extracted text.
"""

import os
import re
import difflib

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

def compare_normalized_files(file1_path, file2_path):
    """
    Compara dos archivos de texto normalizados y calcula la similitud.
    
    Args:
        file1_path (str): Ruta al primer archivo (normalmente el template)
        file2_path (str): Ruta al segundo archivo (normalmente el contrato)
    
    Returns:
        float: Puntuación de similitud entre 0 y 1
    """
    try:
        # Leer los archivos
        with open(file1_path, 'r', encoding='utf-8') as file:
            text1 = file.read()
        
        with open(file2_path, 'r', encoding='utf-8') as file:
            text2 = file.read()
        
        # Calcular la similitud de secuencia
        matcher = difflib.SequenceMatcher(None, text1, text2)
        similarity = matcher.ratio()
        
        print(f"Similitud entre los archivos: {similarity:.2f} ({similarity:.2%})")
        
        # Obtener las diferencias específicas
        diff = list(matcher.get_opcodes())
        
        # Mostrar las primeras diferencias significativas
        print("\nPrimeras diferencias encontradas:")
        count = 0
        for tag, i1, i2, j1, j2 in diff:
            if tag != 'equal':
                count += 1
                # Limitar el tamaño de la salida para diferencias grandes
                t1 = text1[i1:i2]
                t2 = text2[j1:j2]
                max_len = 50  # Mostrar solo los primeros 50 caracteres
                
                if len(t1) > max_len:
                    t1 = t1[:max_len] + "..."
                if len(t2) > max_len:
                    t2 = t2[:max_len] + "..."
                    
                print(f"Diferencia {count}:")
                print(f"  Template: {t1}")
                print(f"  Contrato: {t2}")
                
                if count >= 5:  # Mostrar solo las primeras 5 diferencias
                    print("... (más diferencias no mostradas)")
                    break
        
        return similarity
    
    except Exception as e:
        print(f"Error al comparar archivos: {str(e)}")
        return 0.0

if __name__ == "__main__":
    template_path = "NDA_template.txt"
    normalized_template_path = "NDA_template_normalized.txt"
    input_path = "input.txt"
    normalized_input_path = "input_normalized.txt"
    
    print("1. Normalizando template...")
    normalize_file(template_path, normalized_template_path)
    
    print("\n2. Normalizando contrato...")
    normalize_file(input_path, normalized_input_path)
    
    print("\n3. Comparando archivos normalizados...")
    similarity = compare_normalized_files(normalized_template_path, normalized_input_path)
    
    # Evaluar la similitud
    if similarity >= 0.8:
        print("\nCONCLUSIÓN: Los documentos son muy similares. No se detectan modificaciones significativas.")
    elif similarity >= 0.5:
        print("\nCONCLUSIÓN: Los documentos tienen una similitud moderada. Pueden existir modificaciones importantes.")
    else:
        print("\nCONCLUSIÓN: Los documentos son significativamente diferentes. Se detectan modificaciones mayores.")
