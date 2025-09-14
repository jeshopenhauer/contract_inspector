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
    from inspector_functions.pdf_to_txt_pdfminer import convert_pdf_to_text, get_pdf_info
    from inspector_functions.txt_to_txt_splitter import split_contract_text
    from inspector_functions.txt_cleaner import standardize_page_breaks
except ImportError:
    # Si falla, usa importación relativa (cuando se importa como módulo)
    from .pdf_to_txt_pdfminer import convert_pdf_to_text, get_pdf_info
    from .txt_to_txt_splitter import split_contract_text
    from .txt_cleaner import standardize_page_breaks

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
    # Obtener información del PDF (número de páginas y metadatos)
    page_count, metadata = get_pdf_info(input_pdf)
    standard_page_count = 10  # Número estándar de páginas para este tipo de contrato
    
    report = {
        "timestamp": time.time(),
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "input_file": os.path.basename(input_pdf),
        "status": "processing",
        "page_count": page_count,
        "standard_page_ratio": page_count / standard_page_count if standard_page_count > 0 else 0,
        "metadata": metadata,
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
            
        print(f"[INFO] create_report: PASO 1 completado")
        
        # Paso 1.5: Aplicar limpieza al archivo de texto completo
        print(f"[INFO] create_report: PASO 1.5 - Aplicando limpieza al archivo de texto completo")
        cleaned_output_txt = output_txt
        try:
            print(f"[DEBUG] create_report: Verificando existencia del archivo de texto {output_txt}")
            if os.path.exists(output_txt):
                print(f"[DEBUG] create_report: El archivo {output_txt} existe y tiene {os.path.getsize(output_txt)} bytes")
                # Aplicar limpieza al archivo completo
                print(f"[DEBUG] create_report: Limpiando archivo {output_txt}")
                standardize_page_breaks(output_txt, output_txt)
                print(f"[DEBUG] create_report: Archivo {output_txt} limpiado correctamente")
            else:
                print(f"[ERROR] create_report: El archivo {output_txt} no existe")
                raise FileNotFoundError(f"Archivo no encontrado: {output_txt}")
        except Exception as e:
            print(f"[WARNING] create_report: Error al limpiar archivo {output_txt}: {str(e)}")
            report["warnings"].append(f"Error al limpiar archivo de texto completo: {str(e)}")
            
        print(f"[INFO] create_report: PASO 1.5 completado")
        
        # Paso 2: Dividir el texto en secciones
        print(f"[INFO] create_report: PASO 2 - Dividiendo texto en secciones")
        
        # Crear directorio de salida si no existe
        print(f"[DEBUG] create_report: Creando directorio de salida {output_dir} si no existe")
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            print(f"[DEBUG] create_report: Verificando existencia del archivo de texto limpio {output_txt}")
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
                
            # Ya no es necesario aplicar limpieza a cada archivo pues ya se limpió el archivo original
        except Exception as e:
            import traceback
            error_msg = f"Error al dividir el texto: {str(e)}"
            print(f"[ERROR] create_report: {error_msg}")
            print(f"[DEBUG] {traceback.format_exc()}")
            report["errors"].append(error_msg)
            report["status"] = "error"
            return report
            
        print(f"[INFO] create_report: PASO 2 completado")
        
        # Paso 3: Analizar estadísticas
        
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
            
        except Exception as e:
            report["warnings"].append(f"Error al analizar estadísticas: {str(e)}")
        
        # Paso 4: Analizar párrafos
        
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
            
        except Exception as e:
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


def get_report_html(report, output_dir="output_split"):
    """
    Convierte el reporte en formato HTML para mostrarlo en la página web.
    
    Args:
        report (dict): El reporte generado por create_report()
        output_dir (str): Directorio donde se encuentran los archivos divididos
        
    Returns:
        str: HTML formateado del reporte
    """
    html = []
    # Iniciar el contenedor principal del reporte en formato ASCII
    html.append('<div class="report-container">')
    
    # Iniciar el contenedor ASCII único para todo el reporte
    html.append('<pre class="ascii-table">')
    
    # Encabezado del reporte con estilo ASCII simple
    header_ascii = f"""REPORTE DE ANÁLISIS DE CONTRATO
Archivo: {report['input_file']}
Fecha: {report['date']}

"""
    
    # Quitar el resumen de pasos (simplificación solicitada)
    
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
    
    # Análisis combinado (estadísticas y párrafos)
    if report["statistics"] and report["paragraph_analysis"]:
        html.append('<div class="report-combined-analysis">')
        
        
        # Crear tabla en formato ASCII usando tabulate
        from tabulate import tabulate
        
        # Preparar datos para la tabla combinada
        table_data = []
        headers = ['Art.', 'palabras', 'puntos.', 'comas.', 's', 'a', 'e', 'i', 'o', 'u', 
                   'Párrafos (Contrato)', 'Párrafos (Plantilla)', 'Relación']
        
        # Solo incluir los artículos (1-15), omitir title, between, and
        for i in range(1, 16):
            article_key = f'article_{i}'
            row = [i]
            
            # Añadir estadísticas
            if article_key in report["statistics"]:
                data = report["statistics"][article_key]
                if 'ratios' in data:
                    output_stats = data['output_stats']
                    template_stats = data['template_stats']
                    
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
                else:
                    row.extend(['ERROR'] * 9)
            else:
                row.extend(['-'] * 9)
            
            # Añadir análisis de párrafos
            if article_key in report["paragraph_analysis"]:
                data = report["paragraph_analysis"][article_key]
                if 'error' not in data:
                    output_count = data['output_paragraphs']
                    template_count = data['template_paragraphs']
                    ratio = data['ratio']
                    row.extend([output_count, template_count, ratio])
                else:
                    row.extend([f"ERROR", "-", "-"])
            else:
                row.extend(['-', '-', '-'])
            
            table_data.append(row)
        
        # Generar tabla ASCII
        ascii_table = tabulate(table_data, headers=headers, tablefmt="grid")
        
        # Crear una tabla ASCII para información de páginas y metadatos
        page_ratio = report.get("standard_page_ratio", 0)
        page_count = report.get("page_count", 0)
        standard_page_count = 10  # Número estándar de páginas
        
        # Información sobre páginas
        page_info = [
            ["Información de Páginas", "Valor"],
            ["Número de páginas en el documento", f"{page_count}"],
            ["Número estándar de páginas", f"{standard_page_count}"],
            ["Ratio de páginas (Actual/Estándar)", f"{page_ratio:.2f}"]
        ]
        
        page_info_table = tabulate(page_info, headers="firstrow", tablefmt="grid")
        
        # Información sobre metadatos
        metadata = report.get("metadata", {})
        metadata_rows = [["Metadatos del PDF", "Valor"]]
        
        # Filtrar y mostrar los metadatos más relevantes
        important_keys = ['Title', 'Author', 'Creator', 'Producer', 'CreationDate', 'ModDate', 'Subject', 'Keywords']
        for key in important_keys:
            if key in metadata:
                value = metadata[key]
                # Truncar valores muy largos
                if len(str(value)) > 50:
                    value = str(value)[:47] + "..."
                metadata_rows.append([key, value])
        
        # Si no hay metadatos importantes, mostrar un mensaje
        if len(metadata_rows) == 1:
            metadata_rows.append(["No se encontraron metadatos", "-"])
        
        metadata_table = tabulate(metadata_rows, headers="firstrow", tablefmt="grid")
        
        # Añadir directamente las tablas ASCII al contenedor único
        html.append(header_ascii)  # Ya se inicializó el encabezado antes
        html.append(page_info_table)
        html.append('\n')
        html.append(metadata_table)
        html.append('\n')
        html.append(ascii_table)
        html.append('</pre>')  # Cerrar el contenedor ASCII único
        
        # No cerramos el div.report-container aquí, lo haremos al final
        
        # Añadir sección de comparación visual con desplegables (con separación)
        html.append('<div class="visual-comparison" style="margin-top:30px; padding-top:20px;">')
        
        
        # Incluir enlace a Material Icons
        html.append('<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">')
        
        # Obtener la ruta al directorio de plantillas
        base_dir = Path(__file__).parent.parent
        template_dir = os.path.join(base_dir, "template")
        
        # Crear desplegables para cada artículo, alternando contrato y plantilla
        for i in range(1, 16):
            article_key = f'article_{i}'
            
            # Ruta al archivo de salida del artículo
            output_article_path = os.path.join(output_dir, f'output_{article_key}.txt')
            # Ruta al archivo de plantilla del artículo
            template_article_path = os.path.join(template_dir, f'template_{article_key}.txt')
            
            # Verificar si existen los archivos
            if os.path.exists(output_article_path):
                # Añadir desplegable para el artículo del contrato
                html.append(f'<details class="article-comparison">')
                html.append(f'<summary>')
                html.append(f'<div class="summary-content">output_{article_key}</div>')
                html.append(f'<span class="dropdown-icon">▼</span>')
                html.append(f'</summary>')
                try:
                    with open(output_article_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Mostrar directamente el contenido sin encabezado
                        content_ascii = content
                        
                        html.append(f'<div class="content-container">')
                        html.append(f'<pre id="output-content-{i}" class="article-content ascii-style">')
                        html.append(content_ascii)
                        html.append('</pre>')
                        html.append('</div>')
                except Exception as e:
                    html.append(f'<p class="error">Error al leer el archivo: {str(e)}</p>')
                html.append('</details>')
            
            # Verificar si existe el archivo de plantilla
            if os.path.exists(template_article_path):
                # Añadir desplegable para el artículo de la plantilla
                html.append(f'<details class="template-comparison">')
                html.append(f'<summary>')
                html.append(f'<div class="summary-content">template_{article_key}</div>')
                html.append(f'<span class="dropdown-icon">▼</span>')
                html.append(f'</summary>')
                try:
                    with open(template_article_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Mostrar directamente el contenido sin encabezado
                        content_ascii = content
                        
                        html.append(f'<div class="content-container">')
                        html.append(f'<pre id="template-content-{i}" class="template-content ascii-style">')
                        html.append(content_ascii)
                        html.append('</pre>')
                        html.append('</div>')
                except Exception as e:
                    html.append(f'<p class="error">Error al leer el archivo: {str(e)}</p>')
                html.append('</details>')
        
        # Añadir sección para furthermore si existe
        furthermore_path = os.path.join(output_dir, 'output_furthermore.txt')
        if os.path.exists(furthermore_path):
            # Añadir desplegable para la sección furthermore
            html.append(f'<details class="article-comparison">')
            html.append(f'<summary>')
            html.append(f'<div class="summary-content">output_furthermore</div>')
            html.append(f'<span class="dropdown-icon">▼</span>')
            html.append(f'</summary>')
            try:
                with open(furthermore_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    html.append(f'<div class="content-container">')
                    html.append(f'<pre id="output-furthermore" class="article-content ascii-style">')
                    html.append(content)
                    html.append('</pre>')
                    html.append('</div>')
            except Exception as e:
                html.append(f'<p class="error">Error al leer el archivo furthermore: {str(e)}</p>')
            html.append('</details>')
        
        html.append('</div>')
        
        # Añadir JavaScript para la función de copiar al portapapeles
        html.append('''
        <script>
        function copyToClipboard(button, elementId, event) {
            // Evitar que se abra/cierre el desplegable
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            } else if (window.event) {
                window.event.preventDefault();
                window.event.stopPropagation();
            }
            
            // Obtener el elemento con el contenido
            const element = document.getElementById(elementId);
            if (!element) {
                console.error(`Elemento con ID ${elementId} no encontrado`);
                return;
            }
            
            console.log(`Copiando contenido del elemento: ${elementId}`);
            const text = element.textContent || element.innerText;
            console.log(`Longitud del texto: ${text.length} caracteres`);
            
            // Guardar el icono original
            const iconSpan = button.querySelector('.material-icons');
            const originalIcon = iconSpan.textContent;
            
            // Método fallback para navegadores que no soportan clipboard API
            function fallbackCopyTextToClipboard(text) {
                const textArea = document.createElement("textarea");
                textArea.value = text;
                
                // Hacerlo invisible
                textArea.style.position = "fixed";
                textArea.style.top = "0";
                textArea.style.left = "0";
                textArea.style.width = "2em";
                textArea.style.height = "2em";
                textArea.style.padding = "0";
                textArea.style.border = "none";
                textArea.style.outline = "none";
                textArea.style.boxShadow = "none";
                textArea.style.background = "transparent";
                
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                
                let successful = false;
                try {
                    successful = document.execCommand('copy');
                } catch (err) {
                    console.error('Fallback: Error al copiar', err);
                }
                
                document.body.removeChild(textArea);
                return successful;
            }
            
            // Intentar usar el API de Clipboard moderno primero
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    // Cambiar el icono y dar feedback visual
                    iconSpan.textContent = 'check';
                    button.classList.add('copy-success');
                    
                    // Restaurar el icono original después de 2 segundos
                    setTimeout(() => {
                        iconSpan.textContent = 'content_copy';
                        button.classList.remove('copy-success');
                    }, 2000);
                }).catch(err => {
                    console.error('Error al copiar al portapapeles: ', err);
                    // Intentar método fallback
                    if (fallbackCopyTextToClipboard(text)) {
                        iconSpan.textContent = 'check';
                        button.classList.add('copy-success');
                    } else {
                        iconSpan.textContent = 'error';
                        button.classList.add('copy-error');
                    }
                    
                    // Restaurar el icono original después de 2 segundos
                    setTimeout(() => {
                        iconSpan.textContent = 'content_copy';
                        button.classList.remove('copy-success');
                        button.classList.remove('copy-error');
                    }, 2000);
                });
            } else {
                // Fallback para navegadores más antiguos
                if (fallbackCopyTextToClipboard(text)) {
                    iconSpan.textContent = 'check';
                    button.classList.add('copy-success');
                } else {
                    iconSpan.textContent = 'error';
                    button.classList.add('copy-error');
                }
                
                // Restaurar el icono original después de 2 segundos
                setTimeout(() => {
                    iconSpan.textContent = 'content_copy';
                    button.classList.remove('copy-success');
                    button.classList.remove('copy-error');
                }, 2000);
            }
        }
        </script>
        ''')
    
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




