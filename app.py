"""
Contract Inspector - Aplicación Ejecutable

Este script crea un servidor web local para proporcionar acceso a la funcionalidad
de análisis de contratos a través de una interfaz web.
"""

import os
import sys
import webbrowser
import threading
import time
import json
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

# Añadir el directorio actual al path para poder importar inspector_functions
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Importar la función para crear reportes
from inspector_functions.create_report import create_report, get_report_html

# Configurar aplicación Flask
app = Flask(__name__, static_url_path='', static_folder='./')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['JSON_AS_ASCII'] = False  # Permite caracteres Unicode en las respuestas JSON
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Deshabilitar caché para archivos estáticos

# Configurar CORS para permitir peticiones desde la interfaz web local
CORS(app)

# Variable global para almacenar el puerto en uso
PORT = 5050

@app.route('/', methods=['GET'])
def index():
    """Ruta principal para servir la interfaz web"""
    return app.send_static_file('index.html')

@app.route('/status', methods=['GET'])
def status():
    """Ruta para verificar el estado del servidor"""
    return jsonify({
        'status': 'ok',
        'message': 'Server is running',
        'version': '1.0.0'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Procesa la carga de un archivo PDF"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No se ha proporcionado ningún archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nombre de archivo vacío'}), 400
        
        # Verificar si estamos en modo ejecutable (PyInstaller)
        if getattr(sys, 'frozen', False):
            # Si es ejecutable, usar el directorio donde está el ejecutable
            base_dir = os.path.dirname(sys.executable)
            print(f"[DEBUG] Ejecutando como ejecutable. Base dir: {base_dir}")
        else:
            base_dir = current_dir
            print(f"[DEBUG] Ejecutando como script. Base dir: {base_dir}")
            
        # Guardar como input.pdf en el directorio adecuado
        file_path = os.path.join(base_dir, 'input.pdf')
        file.save(file_path)
        print(f"[DEBUG] PDF guardado en: {file_path}")
        
        # Analizar el contrato y generar el reporte HTML
        try:
            # Definir directorio de salida - siempre en el mismo directorio que el ejecutable o script
            output_dir = os.path.join(base_dir, 'output_split')
            
            # Crear directorio si no existe
            os.makedirs(output_dir, exist_ok=True)
            print(f"[DEBUG] Directorio de salida: {output_dir}")
            
            # Analizar el contrato utilizando la función existente
            report_data = create_report(file_path, output_dir)
            
            if 'errors' in report_data and report_data['errors']:
                return jsonify({
                    'success': False,
                    'error': 'Error al analizar el contrato: ' + ', '.join(report_data['errors'])
                }), 500
            
            # Generar HTML a partir de los resultados
            report_html = get_report_html(report_data)
            
            # Devolver HTML como parte de la respuesta
            return jsonify({
                'success': True,
                'message': 'Archivo procesado correctamente',
                'html': report_html
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False, 
                'error': f'Error al procesar el archivo: {str(e)}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error en la solicitud: {str(e)}'
        }), 400

def open_browser():
    """Abre el navegador automáticamente apuntando a la aplicación"""
    # Esperar un momento para asegurar que el servidor esté funcionando
    time.sleep(1.5)
    url = f"http://localhost:{PORT}"
    print(f"Abriendo navegador en: {url}")
    webbrowser.open(url)

def start_server(debug=False, port=5050):
    """Inicia el servidor Flask"""
    global PORT
    PORT = port
    
    # Si no estamos en modo debug, abrir el navegador automáticamente
    if not debug:
        threading.Timer(1.0, open_browser).start()
    
    # Iniciar el servidor
    try:
        app.run(
            host='127.0.0.1',
            port=port,
            debug=debug,
            use_reloader=debug
        )
    except Exception as e:
        print(f"Error al iniciar el servidor: {str(e)}")
        # Si el puerto está en uso, intentar con otro
        if "Address already in use" in str(e):
            new_port = port + 1
            print(f"Puerto {port} en uso. Intentando con el puerto {new_port}...")
            start_server(debug, new_port)

def run_diagnostics():
    """Ejecuta diagnósticos del sistema y muestra información relevante"""
    print("\n=== DIAGNÓSTICO DEL CONTRACT INSPECTOR ===\n")
    
    # Determinar el directorio base
    is_frozen = getattr(sys, 'frozen', False)
    if is_frozen:
        # Ejecutando como aplicación empaquetada
        base_dir = os.path.dirname(sys.executable)
        print(f"Ejecutando como aplicación empaquetada (PyInstaller)")
    else:
        # Ejecutando como script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Ejecutando como script Python")
    
    print(f"Directorio base: {base_dir}")
    
    # Verificar directorios críticos
    print("\n== Directorios críticos ==")
    critical_dirs = ["inspector_functions", "template", "output_split"]
    for dir_name in critical_dirs:
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.exists(dir_path) and os.path.isdir(dir_path):
            try:
                files = os.listdir(dir_path)
                print(f"✅ {dir_name}: Existe con {len(files)} archivos")
            except:
                print(f"⚠️ {dir_name}: Existe pero no se puede acceder")
        else:
            print(f"❌ {dir_name}: No existe o no es un directorio")
    
    # Verificar archivos críticos
    print("\n== Archivos críticos ==")
    critical_files = [
        "index.html", "functions.js", "style.css",
        os.path.join("inspector_functions", "create_report.py")
    ]
    for file_path in critical_files:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            print(f"✅ {file_path}: Existe ({os.path.getsize(full_path)} bytes)")
        else:
            print(f"❌ {file_path}: No existe o no es un archivo")
    
    # Listar contenido del directorio output_split
    output_split_dir = os.path.join(base_dir, "output_split")
    print(f"\n== Contenido de output_split ==")
    if os.path.exists(output_split_dir) and os.path.isdir(output_split_dir):
        try:
            files = os.listdir(output_split_dir)
            if files:
                for file in files:
                    file_path = os.path.join(output_split_dir, file)
                    if os.path.isfile(file_path):
                        print(f"  - {file} ({os.path.getsize(file_path)} bytes)")
                    else:
                        print(f"  - {file}/ (directorio)")
            else:
                print("  El directorio está vacío")
        except Exception as e:
            print(f"  Error al listar archivos: {str(e)}")
    else:
        print("  El directorio no existe o no es accesible")
    
    print("\n=== FIN DEL DIAGNÓSTICO ===\n")

if __name__ == "__main__":
    # Verificar si estamos en modo diagnóstico
    if len(sys.argv) > 1 and sys.argv[1] == "--diagnose":
        run_diagnostics()
        sys.exit(0)
    
    # Verificar si estamos ejecutando desde PyInstaller
    is_frozen = getattr(sys, 'frozen', False)
    
    # Si es un ejecutable, no usar modo debug
    debug_mode = not is_frozen
    
    print(f"Iniciando Contract Inspector {'(modo debug)' if debug_mode else '(modo producción)'}")
    
    # Iniciar el servidor
    start_server(debug=debug_mode)