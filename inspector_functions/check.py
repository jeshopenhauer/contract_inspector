#!/usr/bin/env python3
import os
import difflib
import sys

# Ajuste para permitir importación directa o como módulo
if __name__ == "__main__":
    # Cuando se ejecuta directamente, ajustar el path para importaciones
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    # Añadir el directorio padre al path para que podamos importar inspector_functions
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

from tabulate import tabulate  # Para formatear la tabla
# Importar las funciones de inspector_statistics
try:
    from inspector_functions.inspector_statistics import compare_files_with_templates as stats_compare
    from inspector_functions.inspector_statistics import print_comparison_table as stats_print_table
except ImportError:
    # Importación directa cuando se ejecuta como script independiente
    from inspector_statistics import compare_files_with_templates as stats_compare
    from inspector_statistics import print_comparison_table as stats_print_table

def compare_files_with_templates(output_dir, template_dir):
    """
    Compare files in the output directory with corresponding files in the template directory.
    
    Args:
        output_dir (str): Directory containing the output files to compare
        template_dir (str): Directory containing the template files
    
    Returns:
        dict: A dictionary with comparison results for each file
    """
    results = {}
    
    # Check if directories exist
    if not os.path.isdir(output_dir):
        print(f"Output directory '{output_dir}' does not exist.")
        return results
    
    if not os.path.isdir(template_dir):
        print(f"Template directory '{template_dir}' does not exist.")
        return results
    
    # Get list of files in output directory
    try:
        output_files = os.listdir(output_dir)
    except Exception as e:
        print(f"Error accessing output directory: {e}")
        return results
    
    # Compare each output file with its corresponding template file
    for output_filename in output_files:
        output_path = os.path.join(output_dir, output_filename)
        
        # Skip directories
        if os.path.isdir(output_path):
            continue
        
        # Find corresponding template file
        template_filename = output_filename.replace('output_', 'template_')
        template_path = os.path.join(template_dir, template_filename)
        
        # Check if template file exists
        if not os.path.isfile(template_path):
            print(f"No matching template found for {output_filename}")
            results[output_filename] = {"error": "No matching template"}
            continue
        
        # Read files
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                output_content = f.readlines()
            
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.readlines()
                
            # Compare files
            diff = difflib.unified_diff(
                template_content, 
                output_content,
                fromfile=template_path,
                tofile=output_path
            )
            
            # Convert diff iterator to list
            diff_list = list(diff)
            
            # Store results
            if diff_list:
                similarity = difflib.SequenceMatcher(None, ''.join(template_content), ''.join(output_content)).ratio()
                results[output_filename] = {
                    "differences": len(diff_list),
                    "similarity": similarity,
                    "diff": ''.join(diff_list)
                }
                print(f"File {output_filename}: {len(diff_list)} differences, {similarity:.2f} similarity")
            else:
                results[output_filename] = {
                    "differences": 0,
                    "similarity": 1.0,
                    "diff": ""
                }
                print(f"File {output_filename}: Identical to template")
                
        except Exception as e:
            print(f"Error comparing {output_filename}: {e}")
            results[output_filename] = {"error": str(e)}
    
    return results

if __name__ == "__main__":
    # Llamar a la función con los directorios especificados
    # Determinar la ruta base del proyecto
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    # Si estamos en la carpeta inspector_functions, el directorio base es el padre
    if os.path.basename(script_dir) == "inspector_functions":
        base_dir = os.path.dirname(script_dir)
    else:
        # Si se ejecuta desde otro lugar, usar la ruta actual
        base_dir = os.getcwd()
    
    output_dir = os.path.join(base_dir, "output_split_statistics_check")
    template_dir = os.path.join(base_dir, "template")
    
    # Verificar si se desea usar la función de estadísticas o la función de comparación de archivos
    use_statistics = True  # Cambiar a False si se desea usar la función de comparación de este módulo
    
    if use_statistics:
        # Usar la función de estadísticas de inspector_statistics
        print(f"Analizando archivos en {output_dir}")
        print(f"Comparando con plantillas en {template_dir}")
        
        try:
            # Usar las funciones de inspector_statistics.py
            results = stats_compare(output_dir, template_dir)
            stats_print_table(results)
            
            # No necesitamos mostrar resumen ya que la tabla de estadísticas ya muestra todo lo necesario
            import sys
            sys.exit(0)  # Salimos para evitar que se ejecute el código al final del script
        except Exception as e:
            print(f"Error al generar estadísticas: {e}")
            import sys
            sys.exit(1)  # Salimos con error
    else:
        # Usar la función de comparación de este módulo
        print(f"Comparando archivos entre '{output_dir}' y '{template_dir}'...")
        results = compare_files_with_templates(output_dir, template_dir)
        
        # Mostrar resultados de comparación básicos ya que la función print_comparison_table fue eliminada
        print("\nResumen de comparación:")
        identical_files = sum(1 for data in results.values() 
                            if isinstance(data, dict) and data.get("differences", 1) == 0)
        total_files = len(results)
        print(f"{identical_files} de {total_files} archivos son idénticos a sus plantillas.")
    
    # El código de resumen adicional aquí ya no es necesario porque sys.exit(0) en la 
    # sección use_statistics=True evita que lleguemos a este punto
    pass
