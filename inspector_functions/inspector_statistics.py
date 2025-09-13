"""
Inspector Unified

Este módulo combina las funcionalidades de inspector_general.py e inspector_general_comparison.py
para analizar y comparar archivos de texto de contratos con sus plantillas de referencia.
"""
import os
import re
import sys
from tabulate import tabulate


def analyze_text(file_path):
    """
    Analiza un archivo de texto y cuenta palabras, puntos, comas, la letra "s" y vocales,
    excluyendo el marcador de salto de página.
    
    Args:
        file_path (str): Ruta al archivo de texto a analizar
    
    Returns:
        dict: Diccionario con los siguientes conteos:
            - word_count: Número de palabras
            - period_count: Número de puntos (.)
            - comma_count: Número de comas (,)
            - s_count: Número de letras "s" (mayúscula o minúscula)
            - a_count, e_count, i_count, o_count, u_count: Número de cada vocal
        
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
    
    # Eliminar el marcador de salto de página
    text_clean = text.replace('===PAGE_BREAK===', '')
    
    # Limpiar el texto para contar palabras (manteniendo espacios donde había puntuación)
    text_for_words = re.sub(r'[^\w\s]', ' ', text_clean)
    
    # Dividir el texto en palabras y contar
    words = text_for_words.split()
    word_count = len(words)
    
    # Texto en minúsculas para contar letras sin distinguir mayúsculas/minúsculas
    text_lower = text_clean.lower()
    
    # Contar puntos, comas, letra "s" y vocales
    period_count = text_clean.count('.')
    comma_count = text_clean.count(',')
    s_count = text_lower.count('s')
    a_count = text_lower.count('a')
    e_count = text_lower.count('e')
    i_count = text_lower.count('i')
    o_count = text_lower.count('o')
    u_count = text_lower.count('u')
    
    # Crear diccionario de resultados
    results = {
        'word_count': word_count,
        'period_count': period_count,
        'comma_count': comma_count,
        's_count': s_count,
        'a_count': a_count,
        'e_count': e_count,
        'i_count': i_count,
        'o_count': o_count,
        'u_count': u_count,
    }
    
    return results


def compare_files_with_templates(output_dir, template_dir):
    """
    Compara archivos de salida con sus plantillas correspondientes.
    
    Args:
        output_dir (str): Directorio con archivos de salida
        template_dir (str): Directorio con archivos de plantilla
        
    Returns:
        dict: Diccionario con resultados de comparación
    """
    results = {}
    
    # Analizar archivos para artículos 1 a 15
    for i in range(1, 16):
        output_file = os.path.join(output_dir, f'output_article_{i}.txt')
        template_file = os.path.join(template_dir, f'template_article_{i}.txt')
        
        if os.path.exists(output_file) and os.path.exists(template_file):
            try:
                output_stats = analyze_text(output_file)
                template_stats = analyze_text(template_file)
                
                # Calcular cocientes
                ratios = {}
                for key in ['word_count', 'period_count', 'comma_count', 's_count', 
                           'a_count', 'e_count', 'i_count', 'o_count', 'u_count']:
                    if template_stats[key] > 0:  # Evitar división por cero
                        ratios[key] = output_stats[key] / template_stats[key]
                    else:
                        ratios[key] = float('inf') if output_stats[key] > 0 else 1.0
                
                results[f'article_{i}'] = {
                    'output_stats': output_stats,
                    'template_stats': template_stats,
                    'ratios': ratios
                }
            except Exception as e:
                results[f'article_{i}'] = {'error': str(e)}
    
    return results


def print_comparison_table(results):
    """
    Imprime una tabla con los resultados de comparación utilizando tabulate.
    
    Args:
        results (dict): Resultados de la comparación
    """
    # Encabezado
    headers = ['Art.', 'palabras', 'puntos.', 'comas.', 's', 'a', 'e', 'i', 'o', 'u']
    
    # Preparar datos para la tabla
    table_data = []
    for i in range(1, 16):
        article_key = f'article_{i}'
        if article_key in results:
            data = results[article_key]
            if 'ratios' in data and 'output_stats' in data and 'template_stats' in data:
                ratios = data['ratios']
                output_stats = data['output_stats']
                template_stats = data['template_stats']
                row = [i]
                for key in ['word_count', 'period_count', 'comma_count', 's_count', 
                           'a_count', 'e_count', 'i_count', 'o_count', 'u_count']:
                    if template_stats[key] == 0:
                        if output_stats[key] > 0:
                            row.append('inf')
                        else:
                            row.append('1')
                    else:
                        # Expresar como fracción sin reducir
                        row.append(f"{output_stats[key]}/{template_stats[key]}")
                table_data.append(row)
            else:
                row = [i] + ['ERROR'] * 9
                table_data.append(row)
    
    # Imprimir tabla con formato mejorado (usando 'grid' format para mejor legibilidad)
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def save_comparison_results(results, output_file):
    """
    Guarda los resultados de comparación en un archivo CSV.
    
    Args:
        results (dict): Resultados de la comparación
        output_file (str): Ruta al archivo de salida
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        # Escribir encabezado
        f.write("article,word_ratio,period_ratio,comma_ratio,s_ratio,a_ratio,e_ratio,i_ratio,o_ratio,u_ratio\n")
        
        # Escribir filas
        for i in range(1, 16):
            article_key = f'article_{i}'
            if article_key in results:
                data = results[article_key]
                if 'ratios' in data and 'output_stats' in data and 'template_stats' in data:
                    output_stats = data['output_stats']
                    template_stats = data['template_stats']
                    keys = ['word_count', 'period_count', 'comma_count', 's_count', 
                           'a_count', 'e_count', 'i_count', 'o_count', 'u_count']
                    
                    values = []
                    for key in keys:
                        if template_stats[key] == 0:
                            if output_stats[key] > 0:
                                values.append("inf")
                            else:
                                values.append("1")
                        else:
                            # Expresar como fracción sin reducir
                            values.append(f"{output_stats[key]}/{template_stats[key]}")
                    
                    f.write(f"{i},{values[0]},{values[1]},{values[2]},{values[3]}," +
                           f"{values[4]},{values[5]},{values[6]},{values[7]},{values[8]}\n")
                else:
                    f.write(f"{i},ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR,ERROR\n")


def file_statistics(file_path):
    """
    Genera estadísticas básicas de un archivo de texto.
    
    Args:
        file_path (str): Ruta al archivo de texto a analizar
        
    Returns:
        dict: Diccionario con estadísticas del archivo
    """
    return analyze_text(file_path)


# Si se ejecuta este script directamente
if __name__ == "__main__":
    # Verificar si se proporciona un archivo específico para análisis simple
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        file_path = sys.argv[1]
        
        try:
            # Analizar el texto
            stats = analyze_text(file_path)
            
            print(f"Archivo: {file_path}")
            print(f"Número de palabras: {stats['word_count']}")
            print(f"Número de puntos (.): {stats['period_count']}")
            print(f"Número de comas (,): {stats['comma_count']}")
            print(f"Número de letras 's': {stats['s_count']}")
            print(f"Número de letras 'a': {stats['a_count']}")
            print(f"Número de letras 'e': {stats['e_count']}")
            print(f"Número de letras 'i': {stats['i_count']}")
            print(f"Número de letras 'o': {stats['o_count']}")
            print(f"Número de letras 'u': {stats['u_count']}")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
    else:
        # Directorios por defecto para análisis de comparación
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(root_dir, "output_split")
        template_dir = os.path.join(root_dir, "template")
        results_file = os.path.join(root_dir, "comparison_results.csv")
        
        print(f"Analizando archivos en {output_dir}")
        print(f"Comparando con plantillas en {template_dir}")
        
        try:
            results = compare_files_with_templates(output_dir, template_dir)
            print_comparison_table(results)
            save_comparison_results(results, results_file)
            print(f"\nResultados guardados en {results_file}")
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)
