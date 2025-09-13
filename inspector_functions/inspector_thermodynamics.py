"""
Inspector Thermodynamics

Este módulo proporciona funciones para analizar la estructura de contratos,
específicamente contando el número de párrafos en archivos de texto y comparando
entre contratos y plantillas para identificar cambios estructurales.
"""
import os
import re
import sys
from tabulate import tabulate


def count_paragraphs(file_path):
    """
    Analiza un archivo de texto y cuenta el número de párrafos.
    
    Args:
        file_path (str): Ruta al archivo de texto a analizar
    
    Returns:
        int: Número de párrafos encontrados en el archivo
        
    Raises:
        FileNotFoundError: Si el archivo no existe
    """
    # Validar que el archivo exista
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"El archivo no existe: {file_path}")
    
    # Leer el contenido del archivo
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
    except Exception as e:
        raise IOError(f"Error al leer el archivo: {str(e)}")
    
    # Eliminar el marcador de salto de página si existe
    text_clean = text.replace('===PAGE_BREAK===', '')
    
    # Dividir el texto por párrafos
    # Consideramos un párrafo como un bloque de texto separado por una o más líneas en blanco
    paragraphs = re.split(r'\n\s*\n', text_clean)
    
    # Filtrar párrafos vacíos (solo espacios en blanco)
    paragraphs = [p for p in paragraphs if p.strip()]
    
    return len(paragraphs)


def compare_paragraph_counts(output_dir, template_dir):
    """
    Compara el número de párrafos entre archivos de salida y sus plantillas correspondientes.
    
    Args:
        output_dir (str): Directorio con archivos de salida
        template_dir (str): Directorio con archivos de plantilla
        
    Returns:
        dict: Diccionario con resultados de comparación de párrafos
    """
    results = {}
    
    # Lista de prefijos de archivo para buscar
    prefixes = [
        'article_1', 'article_2', 'article_3', 'article_4', 'article_5',
        'article_6', 'article_7', 'article_8', 'article_9', 'article_10',
        'article_11', 'article_12', 'article_13', 'article_14', 'article_15',
        'preamble', 'and', 'between'
    ]
    
    # Manejar casos especiales de nombre
    special_cases = {
        'title': {
            'output': 'output_title.txt',
            'template': 'template_tittle.txt'  # Corregido: "tittle" en lugar de "title"
        },
        'furthermore': {
            'output': 'output_furthermore.txt',
            'template': None  # No hay template para furthermore
        }
    }
    
    # Analizar cada tipo de archivo normal
    for prefix in prefixes:
        output_file = os.path.join(output_dir, f'output_{prefix}.txt')
        template_file = os.path.join(template_dir, f'template_{prefix}.txt')
        
        if os.path.exists(output_file) and os.path.exists(template_file):
            try:
                output_paragraphs = count_paragraphs(output_file)
                template_paragraphs = count_paragraphs(template_file)
                
                results[prefix] = {
                    'output_paragraphs': output_paragraphs,
                    'template_paragraphs': template_paragraphs,
                    'ratio': f"{output_paragraphs}/{template_paragraphs}"
                }
            except Exception as e:
                results[prefix] = {'error': str(e)}
    
    # Manejar casos especiales
    for section, files in special_cases.items():
        output_file = os.path.join(output_dir, files['output'])
        
        # Si tiene un template definido
        if files['template']:
            template_file = os.path.join(template_dir, files['template'])
            if os.path.exists(output_file) and os.path.exists(template_file):
                try:
                    output_paragraphs = count_paragraphs(output_file)
                    template_paragraphs = count_paragraphs(template_file)
                    
                    results[section] = {
                        'output_paragraphs': output_paragraphs,
                        'template_paragraphs': template_paragraphs,
                        'ratio': f"{output_paragraphs}/{template_paragraphs}"
                    }
                except Exception as e:
                    results[section] = {'error': str(e)}
        # Si no tiene template (como furthermore)
        elif os.path.exists(output_file):
            try:
                output_paragraphs = count_paragraphs(output_file)
                
                results[section] = {
                    'output_paragraphs': output_paragraphs,
                    'template_paragraphs': 0,  # No hay template, así que marcamos como 0
                    'ratio': f"{output_paragraphs}/0 (N/A)"  # No hay ratio válido
                }
            except Exception as e:
                results[section] = {'error': str(e)}
    
    return results


def print_paragraph_comparison_table(results):
    """
    Imprime una tabla con los resultados de comparación de párrafos.
    
    Args:
        results (dict): Resultados de la comparación de párrafos
    """
    # Encabezado
    headers = ['Sección', 'Párrafos (Contrato)', 'Párrafos (Plantilla)', 'Relación']
    
    # Definir el orden personalizado de las secciones
    section_order = [
        'title',
        'between',
        'and',
        'preamble'
    ]
    # Añadir artículos del 1 al 15 en orden
    for i in range(1, 16):
        section_order.append(f'article_{i}')
    # Añadir furthermore al final si existe
    section_order.append('furthermore')
    
    # Preparar datos para la tabla siguiendo el orden personalizado
    table_data = []
    
    for section in section_order:
        if section in results:
            data = results[section]
            if 'error' in data:
                row = [section, 'ERROR', 'ERROR', 'ERROR']
            else:
                output_paragraphs = data['output_paragraphs']
                template_paragraphs = data['template_paragraphs']
                ratio = data['ratio']
                row = [section, output_paragraphs, template_paragraphs, ratio]
            
            table_data.append(row)
    
    # Añadir secciones que podrían estar presentes pero no incluidas en el orden personalizado
    for section, data in results.items():
        if section not in section_order:
            if 'error' in data:
                row = [section, 'ERROR', 'ERROR', 'ERROR']
            else:
                output_paragraphs = data['output_paragraphs']
                template_paragraphs = data['template_paragraphs']
                ratio = data['ratio']
                row = [section, output_paragraphs, template_paragraphs, ratio]
            
            table_data.append(row)
    
    # Imprimir tabla con formato mejorado
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def save_paragraph_comparison_results(results, output_file):
    """
    Guarda los resultados de comparación de párrafos en un archivo CSV.
    
    Args:
        results (dict): Resultados de la comparación de párrafos
        output_file (str): Ruta al archivo de salida
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        # Escribir encabezado
        f.write("section,output_paragraphs,template_paragraphs,paragraph_ratio\n")
        
        # Definir el orden personalizado de las secciones
        section_order = [
            'title',
            'between',
            'and',
            'preamble'
        ]
        # Añadir artículos del 1 al 15 en orden
        for i in range(1, 16):
            section_order.append(f'article_{i}')
        # Añadir furthermore al final
        section_order.append('furthermore')
        
        # Escribir las secciones en el orden personalizado
        for section in section_order:
            if section in results:
                data = results[section]
                if 'error' in data:
                    f.write(f"{section},ERROR,ERROR,ERROR\n")
                else:
                    output_paragraphs = data['output_paragraphs']
                    template_paragraphs = data['template_paragraphs']
                    ratio = data['ratio']
                    f.write(f"{section},{output_paragraphs},{template_paragraphs},{ratio}\n")
        
        # Añadir secciones que podrían estar presentes pero no incluidas en el orden personalizado
        for section in results.keys():
            if section not in section_order:
                data = results[section]
                if 'error' in data:
                    f.write(f"{section},ERROR,ERROR,ERROR\n")
                else:
                    output_paragraphs = data['output_paragraphs']
                    template_paragraphs = data['template_paragraphs']
                    ratio = data['ratio']
                    f.write(f"{section},{output_paragraphs},{template_paragraphs},{ratio}\n")


def analyze_paragraphs_in_file(file_path):
    """
    Analiza el número de párrafos en un archivo específico.
    
    Args:
        file_path (str): Ruta al archivo de texto a analizar
        
    Returns:
        int: Número de párrafos en el archivo
    """
    return count_paragraphs(file_path)


# Si se ejecuta este script directamente
if __name__ == "__main__":
    # Verificar si se proporciona un archivo específico para análisis simple
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        file_path = sys.argv[1]
        
        try:
            # Analizar el número de párrafos
            paragraph_count = count_paragraphs(file_path)
            
            print(f"Archivo: {file_path}")
            print(f"Número de párrafos: {paragraph_count}")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    else:
        # Directorios por defecto para análisis de comparación
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(root_dir, "output_split")
        template_dir = os.path.join(root_dir, "template")
        results_file = os.path.join(root_dir, "paragraph_comparison_results.csv")
        
        print(f"Analizando párrafos en archivos de {output_dir}")
        print(f"Comparando con plantillas en {template_dir}")
        
        try:
            results = compare_paragraph_counts(output_dir, template_dir)
            print_paragraph_comparison_table(results)
            save_paragraph_comparison_results(results, results_file)
            print(f"\nResultados guardados en {results_file}")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
