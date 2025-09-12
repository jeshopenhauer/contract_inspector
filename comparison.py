import difflib
import os
import re

def load_files(template_file, contract_file):
    """
    Carga los archivos de texto normalizados.
    
    Args:
        template_file: Ruta al archivo de plantilla normalizado
        contract_file: Ruta al archivo de contrato normalizado
    
    Returns:
        Tuple con el contenido de los archivos (template_text, contract_text)
    """
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template_text = f.read()
        
        with open(contract_file, 'r', encoding='utf-8') as f:
            contract_text = f.read()
        
        return template_text, contract_text
    except Exception as e:
        raise Exception(f"Error al cargar los archivos: {str(e)}")

def calculate_similarity(text1, text2):
    """
    Calcula el porcentaje de similitud entre dos textos.
    
    Args:
        text1: Primer texto a comparar
        text2: Segundo texto a comparar
    
    Returns:
        Float con el porcentaje de similitud (0.0 a 1.0)
    """
    matcher = difflib.SequenceMatcher(None, text1, text2)
    similarity = matcher.ratio()
    return similarity

def find_differences(text1, text2):
    """
    Encuentra las diferencias entre dos textos.
    
    Args:
        text1: Texto de plantilla
        text2: Texto de contrato
    
    Returns:
        Lista de diferencias encontradas
    """
    differences = []
    matcher = difflib.SequenceMatcher(None, text1, text2)
    
    for op, i1, i2, j1, j2 in matcher.get_opcodes():
        if op != 'equal':
            difference = {
                'type': op,
                'template_text': text1[i1:i2],
                'contract_text': text2[j1:j2],
                'position': i1
            }
            differences.append(difference)
    
    return differences

def evaluate_similarity(similarity):
    """
    Evalúa el nivel de similitud entre los documentos.
    
    Args:
        similarity: Valor de similitud entre 0.0 y 1.0
    
    Returns:
        String con la evaluación del resultado
    """
    if similarity >= 0.95:
        return "Los documentos son prácticamente idénticos."
    elif similarity >= 0.85:
        return "Los documentos son muy similares con pequeñas diferencias."
    elif similarity >= 0.70:
        return "Los documentos son muy similares."
    elif similarity >= 0.50:
        return "Los documentos tienen un nivel moderado de similitud."
    else:
        return "Los documentos tienen diferencias significativas."

def generate_report(template_file, contract_file, similarity, differences):
    """
    Genera un informe detallado de la comparación.
    
    Args:
        template_file: Nombre del archivo de plantilla
        contract_file: Nombre del archivo de contrato
        similarity: Porcentaje de similitud
        differences: Lista de diferencias encontradas
    
    Returns:
        String con el informe completo
    """
    report = f"INFORME DE COMPARACIÓN\n"
    report += f"===================\n\n"
    report += f"Plantilla: {os.path.basename(template_file)}\n"
    report += f"Contrato: {os.path.basename(contract_file)}\n"
    report += f"Similitud: {similarity * 100:.2f}%\n"
    report += f"Diferencias encontradas: {len(differences)}\n\n"
    
    report += f"DETALLE DE DIFERENCIAS:\n"
    report += f"=====================\n\n"
    
    for i, diff in enumerate(differences):
        report += f"Diferencia #{i+1} - Tipo: {diff['type']}\n"
        
        if diff['type'] == 'replace':
            report += f"  En plantilla: \"{diff['template_text']}\"\n"
            report += f"  En contrato:  \"{diff['contract_text']}\"\n"
        elif diff['type'] == 'delete':
            report += f"  Texto eliminado de plantilla: \"{diff['template_text']}\"\n"
        elif diff['type'] == 'insert':
            report += f"  Texto añadido en contrato: \"{diff['contract_text']}\"\n"
        
        report += f"\n"
    
    report += f"EVALUACIÓN:\n"
    report += f"==========\n\n"
    report += evaluate_similarity(similarity)
    
    return report

def compare_documents(template_file, contract_file):
    """
    Compara un contrato normalizado con la plantilla normalizada.
    
    Args:
        template_file: Ruta al archivo de plantilla normalizado
        contract_file: Ruta al archivo de contrato normalizado
        
    Returns:
        Diccionario con los resultados de la comparación
    """
    print(f"Cargando plantilla: {template_file}")
    print(f"Cargando contrato: {contract_file}")
    
    template_text, contract_text = load_files(template_file, contract_file)
    
    print("Comparando documentos...")
    similarity = calculate_similarity(template_text, contract_text)
    differences = find_differences(template_text, contract_text)
    
    print("Generando informe de comparación...")
    report = generate_report(template_file, contract_file, similarity, differences)
    
    # Guardar el informe en un archivo
    with open("comparison_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print("\nRESUMEN:")
    print(f"- Similitud: {similarity * 100:.2f}%")
    print(f"- Diferencias encontradas: {len(differences)}")
    print(f"- Informe completo guardado en: comparison_report.txt")
    print()
    print(f"EVALUACIÓN: {evaluate_similarity(similarity)}")
    
    return {
        'similarity': similarity,
        'differences': len(differences),
        'evaluation': evaluate_similarity(similarity),
        'report_path': "comparison_report.txt"
    }

# Si se ejecuta como script principal
if __name__ == "__main__":
    template_file = "NDA_template_normalized.txt"
    contract_file = "input_normalized.txt"
    
    compare_documents(template_file, contract_file)