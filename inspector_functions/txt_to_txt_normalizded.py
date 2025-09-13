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
