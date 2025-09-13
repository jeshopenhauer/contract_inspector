"""
Creador de Reportes para Inspector de Contratos

Este módulo contiene funciones para generar reportes a partir de archivos PDF de contratos.
Analiza el contenido del contrato y genera estadísticas y análisis térmicos.
"""

import os
import json
import sys
import time
from pathlib import Path

# Configurar la importación para que funcione tanto cuando se ejecuta directamente como cuando se importa
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))  # Añadir el directorio padre al path

# Importar funciones necesarias de otros módulos
try:
    # Intenta primero importación absoluta (cuando se ejecuta directamente)
    from inspector_functions.pdf_to_txt_pdfminer import convert_pdf_to_text
    from inspector_functions.txt_to_txt_splitter import split_contract_text
except ImportError:
    # Si falla, usa importación relativa (cuando se importa como módulo)
    from .pdf_to_txt_pdfminer import convert_pdf_to_text
    from .txt_to_txt_splitter import split_contract_text

import inspector_functions.inspector_statistics as statistics
import inspector_functions.inspector_thermodynamics as thermodynamics

def create_report(input_pdf="input.pdf", output_dir="output_split"):
    """
    Crea un reporte completo del análisis de un contrato.
    
    Args:
        input_pdf (str): Ruta al archivo PDF del contrato
        output_dir (str): Directorio donde guardar los archivos divididos
        
    Returns:
        dict: Un diccionario con los resultados del análisis para ser entregado al cliente
    """
    report = {
        "timestamp": time.time(),
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "input_file": os.path.basename(input_pdf),
        "status": "processing",
        "steps": [],
        "statistics": {},
        "paragraph_analysis": {},
        "warnings": [],
        "errors": []
    }
    
    try:
        print(f"[DEBUG] create_report: Iniciando proceso para archivo {input_pdf}")
        print(f"[DEBUG] create_report: Directorio de salida: {output_dir}")
        
        # Paso 1: Convertir PDF a texto
        print(f"[INFO] create_report: PASO 1 - Convirtiendo PDF a texto")
        report["steps"].append({"step": "pdf_to_text", "status": "running"})
        output_txt = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output.txt")
        
        print(f"[DEBUG] create_report: La ruta del archivo de salida será {output_txt}")
        print(f"[DEBUG] create_report: Verificando existencia de {input_pdf}")
        if os.path.exists(input_pdf):
            print(f"[DEBUG] create_report: El archivo {input_pdf} existe y tiene {os.path.getsize(input_pdf)} bytes")
        else:
            print(f"[ERROR] create_report: El archivo {input_pdf} no existe")
            
        text_content = convert_pdf_to_text(input_pdf)
        if not text_content:
            error_msg = "No se pudo extraer texto del PDF"
            print(f"[ERROR] create_report: {error_msg}")
            report["errors"].append(error_msg)
            report["status"] = "error"
            report["steps"][-1]["status"] = "error"
            return report
            
        # Guardar el texto extraído
        print(f"[DEBUG] create_report: Guardando {len(text_content)} caracteres en {output_txt}")
        try:
            with open(output_txt, 'w', encoding='utf-8') as f:
                f.write(text_content)
            print(f"[INFO] create_report: Texto guardado exitosamente en {output_txt}")
        except Exception as e:
            print(f"[ERROR] create_report: Error al guardar el texto: {str(e)}")
            report["errors"].append(f"Error al guardar el texto: {str(e)}")
            
        report["steps"][-1]["status"] = "complete"
        print(f"[INFO] create_report: PASO 1 completado")
        
        # Paso 2: Dividir el texto en secciones
        print(f"[INFO] create_report: PASO 2 - Dividiendo texto en secciones")
        report["steps"].append({"step": "split_text", "status": "running"})
        
        # Crear directorio de salida si no existe
        print(f"[DEBUG] create_report: Creando directorio de salida {output_dir} si no existe")
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            print(f"[DEBUG] create_report: Verificando existencia del archivo de texto {output_txt}")
            if os.path.exists(output_txt):
                print(f"[DEBUG] create_report: El archivo {output_txt} existe y tiene {os.path.getsize(output_txt)} bytes")
            else:
                print(f"[ERROR] create_report: El archivo {output_txt} no existe")
                raise FileNotFoundError(f"Archivo no encontrado: {output_txt}")
                
            print(f"[DEBUG] create_report: Iniciando división del texto en {output_dir}")
            split_results = split_contract_text(output_txt, output_dir)
            
            num_files = len(split_results) if isinstance(split_results, dict) else 0
            print(f"[INFO] create_report: Se crearon {num_files} archivos en {output_dir}")
            
            # Listar los archivos creados
            print(f"[DEBUG] create_report: Archivos creados:")
            for section, path in (split_results.items() if isinstance(split_results, dict) else []):
                print(f"[DEBUG] create_report:   - {section}: {path}")
                
            report["steps"][-1]["status"] = "complete"
            report["steps"][-1]["files_created"] = num_files
        except Exception as e:
            import traceback
            error_msg = f"Error al dividir el texto: {str(e)}"
            print(f"[ERROR] create_report: {error_msg}")
            print(f"[DEBUG] {traceback.format_exc()}")
            report["steps"][-1]["status"] = "error"
            report["errors"].append(error_msg)
            report["status"] = "error"
            return report
            
        print(f"[INFO] create_report: PASO 2 completado")
        
        # Paso 3: Analizar estadísticas
        report["steps"].append({"step": "statistics_analysis", "status": "running"})
        
        try:
            # Obtener la ruta al directorio de plantillas
            base_dir = Path(__file__).parent.parent
            template_dir = os.path.join(base_dir, "template")
            
            # Analizar estadísticas
            stats_results = statistics.compare_files_with_templates(output_dir, template_dir)
            
            # Convertir resultados a un formato más adecuado para JSON
            for article, data in stats_results.items():
                if 'ratios' in data:
                    # Convertir los valores de ratio a cadenas de texto para JSON
                    stats_results[article]['ratios'] = {
                        k: str(v) for k, v in data['ratios'].items()
                    }
            
            report["statistics"] = stats_results
            report["steps"][-1]["status"] = "complete"
            
        except Exception as e:
            report["steps"][-1]["status"] = "warning"
            report["warnings"].append(f"Error al analizar estadísticas: {str(e)}")
        
        # Paso 4: Analizar párrafos
        report["steps"].append({"step": "paragraph_analysis", "status": "running"})
        
        try:
            # Analizar párrafos
            para_results = thermodynamics.compare_paragraph_counts(output_dir, template_dir)
            
            # Convertir resultados a un formato más adecuado para JSON
            formatted_para_results = {}
            for section, data in para_results.items():
                if 'error' not in data:
                    formatted_para_results[section] = {
                        'output_paragraphs': data['output_paragraphs'],
                        'template_paragraphs': data['template_paragraphs'],
                        'ratio': data['ratio']
                    }
                else:
                    formatted_para_results[section] = {'error': data['error']}
            
            report["paragraph_analysis"] = formatted_para_results
            report["steps"][-1]["status"] = "complete"
            
        except Exception as e:
            report["steps"][-1]["status"] = "warning"
            report["warnings"].append(f"Error al analizar párrafos: {str(e)}")
        
        # Finalizar reporte
        report["status"] = "complete" if not report["errors"] else "error"
        
        # Guardar el reporte en un archivo JSON para referencia
        report_file = os.path.join(base_dir, "contract_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        return report
        
    except Exception as e:
        report["status"] = "error"
        report["errors"].append(f"Error general: {str(e)}")
        return report


def get_report_html(report):
    """
    Convierte el reporte en formato HTML para mostrarlo en la página web.
    
    Args:
        report (dict): El reporte generado por create_report()
        
    Returns:
        str: HTML formateado del reporte
    """
    html = []
    html.append('<div class="report-container">')
    
    # Encabezado del reporte
    html.append('<div class="report-header">')
    html.append(f'<h2>Reporte de Análisis: {report["input_file"]}</h2>')
    html.append(f'<p>Generado el: {report["date"]}</p>')
    html.append(f'<p class="status-{report["status"]}">Estado: {report["status"].upper()}</p>')
    html.append('</div>')
    
    # Resumen de pasos
    html.append('<div class="report-steps">')
    html.append('<h3>Pasos realizados:</h3>')
    html.append('<ul>')
    for step in report["steps"]:
        status_class = step["status"]
        html.append(f'<li class="step-{status_class}">{step["step"]}: {step["status"].upper()}</li>')
    html.append('</ul>')
    html.append('</div>')
    
    # Si hay errores, mostrarlos
    if report["errors"]:
        html.append('<div class="report-errors">')
        html.append('<h3>Errores encontrados:</h3>')
        html.append('<ul>')
        for error in report["errors"]:
            html.append(f'<li>{error}</li>')
        html.append('</ul>')
        html.append('</div>')
    
    # Si hay advertencias, mostrarlas
    if report["warnings"]:
        html.append('<div class="report-warnings">')
        html.append('<h3>Advertencias:</h3>')
        html.append('<ul>')
        for warning in report["warnings"]:
            html.append(f'<li>{warning}</li>')
        html.append('</ul>')
        html.append('</div>')
    
    # Análisis de párrafos
    if report["paragraph_analysis"]:
        html.append('<div class="report-paragraphs">')
        html.append('<h3>Análisis de Párrafos por Sección</h3>')
        
        # Crear tabla en formato ASCII usando tabulate
        from tabulate import tabulate
        
        # Preparar datos para la tabla
        table_data = []
        headers = ['Sección', 'Párrafos (Contrato)', 'Párrafos (Plantilla)', 'Relación']
        
        # Orden específico de secciones
        section_order = ['title', 'between', 'and', 'preamble']
        for i in range(1, 16):
            section_order.append(f'article_{i}')
        section_order.append('furthermore')
        
        # Preparar filas de datos para tabulate
        for section in section_order:
            if section in report["paragraph_analysis"]:
                data = report["paragraph_analysis"][section]
                if 'error' not in data:
                    output_count = data['output_paragraphs']
                    template_count = data['template_paragraphs']
                    ratio = data['ratio']
                    table_data.append([section, output_count, template_count, ratio])
                else:
                    table_data.append([section, f"ERROR: {data['error']}", "", ""])
        
        # Mostrar secciones adicionales que no estén en el orden predefinido
        for section, data in report["paragraph_analysis"].items():
            if section not in section_order:
                if 'error' not in data:
                    output_count = data['output_paragraphs']
                    template_count = data['template_paragraphs']
                    ratio = data['ratio']
                    table_data.append([section, output_count, template_count, ratio])
                else:
                    table_data.append([section, f"ERROR: {data['error']}", "", ""])
        
        # Generar tabla ASCII
        ascii_table = tabulate(table_data, headers=headers, tablefmt="grid")
        
        # Añadir la tabla ASCII al HTML como texto preformateado
        html.append('<pre class="ascii-table">')
        html.append(ascii_table)
        html.append('</pre>')
        
        html.append('</div>')
    
    # Análisis estadístico (resumido)
    if report["statistics"]:
        html.append('<div class="report-statistics">')
        html.append('<h3>Análisis Estadístico por Sección</h3>')
        
        # Crear tabla en formato ASCII usando tabulate
        from tabulate import tabulate
        
        # Preparar datos para la tabla
        table_data = []
        headers = ['Art.', 'palabras', 'puntos.', 'comas.', 's', 'a', 'e', 'i', 'o', 'u']
        
        # Secciones en orden
        for i in range(1, 16):
            article_key = f'article_{i}'
            if article_key in report["statistics"]:
                data = report["statistics"][article_key]
                if 'ratios' in data:
                    ratios = data['ratios']
                    output_stats = data['output_stats']
                    template_stats = data['template_stats']
                    
                    row = [i]
                    for key in ['word_count', 'period_count', 'comma_count', 's_count', 
                               'a_count', 'e_count', 'i_count', 'o_count', 'u_count']:
                        # Formato como fracción output/template
                        if template_stats[key] == 0:
                            if output_stats[key] > 0:
                                row.append('inf')
                            else:
                                row.append('1')
                        else:
                            row.append(f"{output_stats[key]}/{template_stats[key]}")
                    
                    table_data.append(row)
                else:
                    row = [i] + ['ERROR'] * 9
                    table_data.append(row)
        
        # Generar tabla ASCII
        ascii_table = tabulate(table_data, headers=headers, tablefmt="grid")
        
        # Añadir la tabla ASCII al HTML como texto preformateado
        html.append('<pre class="ascii-table">')
        html.append(ascii_table)
        html.append('</pre>')
        
        html.append('</div>')
    
    html.append('</div>')  # Cierra report-container
    
    return '\n'.join(html)


# Función principal para ejecutar desde la línea de comandos
if __name__ == "__main__":
    input_pdf = "input.pdf"
    output_dir = "output_split"
    
    # Permitir especificar archivo de entrada
    if len(sys.argv) > 1:
        input_pdf = sys.argv[1]
    
    # Permitir especificar directorio de salida
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    print(f"Generando reporte para {input_pdf}...")
    report = create_report(input_pdf, output_dir)
    
    if report["status"] == "complete":
        print("Reporte generado con éxito")
    else:
        print(f"Error al generar reporte: {report['errors']}")
