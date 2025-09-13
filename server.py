from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import sys
import json

# Añadir el directorio actual al path para poder importar inspector_functions
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Importar la función para crear reportes
from inspector_functions.create_report import create_report, get_report_html

app = Flask(__name__, static_url_path='', static_folder='./')

# Configuración para aumentar el tamaño máximo de los archivos
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['JSON_AS_ASCII'] = False  # Permite caracteres Unicode en las respuestas JSON
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Deshabilitar caché para archivos estáticos

# Configurar CORS de forma más permisiva - incluir TODOS los headers necesarios
CORS(app, supports_credentials=True, resources={r"/*": {
    "origins": "*",
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Cache-Control", "Accept", "Origin", "Pragma", "Expires"],
    "expose_headers": ["Content-Type", "Authorization", "X-Requested-With", "Cache-Control", "Accept", "Origin", "Pragma", "Expires"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]
}})

@app.route('/', methods=['GET', 'OPTIONS'])
def index():
    """
    Ruta principal para verificar si el servidor está activo
    """
    print("[INFO] server.py: Solicitud recibida en la ruta principal")
    
    # Comprobar si se solicita el archivo html o la API
    accept_header = request.headers.get('Accept', '')
    if 'text/html' in accept_header and 'application/json' not in accept_header:
        print("[INFO] server.py: Solicitud HTML detectada, sirviendo index.html")
        return app.send_static_file('index.html')
    
    # Por defecto responder con estado JSON
    return jsonify({
        'status': 'ok',
        'message': 'Server is running'
    })

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,X-Requested-With,Cache-Control,Accept,Origin,Pragma,Expires")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS,HEAD")
        print(f"[DEBUG] server.py: Respondiendo a solicitud OPTIONS/preflight")
        return response

@app.after_request
def add_cors_headers(response):
    # Asegurarse de que todas las respuestas tengan los headers CORS correctos
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With,Cache-Control,Accept,Origin,Pragma,Expires'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS,HEAD'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    # Imprimir headers de la respuesta para depuración
    print(f"[DEBUG] server.py: Enviando respuesta con headers CORS para {request.path}")
    return response

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print(f"[INFO] server.py: Recibida solicitud de carga de archivo")
        
        if 'file' not in request.files:
            print(f"[ERROR] server.py: No se encontró el archivo en la solicitud")
            return jsonify({'success': False, 'error': 'No se ha proporcionado ningún archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print(f"[ERROR] server.py: Nombre de archivo vacío")
            return jsonify({'success': False, 'error': 'Nombre de archivo vacío'}), 400
        
        print(f"[INFO] server.py: Procesando archivo: {file.filename}")
        
        # Guardar como input.pdf en el directorio actual
        file_path = os.path.join(current_dir, 'input.pdf')
        print(f"[DEBUG] server.py: Guardando archivo en {file_path}")
        file.save(file_path)
        
        print(f"[INFO] server.py: Archivo guardado correctamente")
        
        # Iniciar análisis automáticamente
        print(f"[INFO] server.py: Iniciando análisis automático")
        
        # Definir directorio de salida
        output_dir = os.path.join(current_dir, 'output_split')
        
        # Generar reporte
        try:
            report = create_report(file_path, output_dir)
            print(f"[INFO] server.py: Reporte generado con estado: {report['status']}")
            
            # Convertir reporte a HTML
            html_content = get_report_html(report)
            
            return jsonify({
                'success': True,
                'message': 'Archivo guardado y analizado correctamente',
                'file_path': file_path,
                'html': html_content,
                'report_status': report['status']
            })
        except Exception as e:
            import traceback
            print(f"[ERROR] server.py: Error al generar reporte: {str(e)}")
            print(f"[DEBUG] {traceback.format_exc()}")
            
            return jsonify({
                'success': True,
                'message': 'Archivo guardado correctamente, pero hubo un error al generar el reporte',
                'file_path': file_path,
                'error_report': str(e)
            })
        
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze', methods=['GET'])
def analyze_contract():
    try:
        print(f"[INFO] server.py: Recibida solicitud de análisis manual")
        
        # Verificar si existe el archivo input.pdf
        file_path = os.path.join(current_dir, 'input.pdf')
        if not os.path.exists(file_path):
            print(f"[ERROR] server.py: No existe el archivo {file_path}")
            return jsonify({
                'success': False,
                'error': 'No se ha subido ningún archivo para analizar'
            }), 400
        
        print(f"[DEBUG] server.py: Verificado archivo {file_path}, tamaño: {os.path.getsize(file_path)} bytes")
        
        # Definir directorio de salida
        output_dir = os.path.join(current_dir, 'output_split')
        print(f"[DEBUG] server.py: Directorio de salida: {output_dir}")
        
        # Verificar si existe el archivo de reporte
        report_path = os.path.join(current_dir, 'contract_report.json')
        use_cached_report = False
        
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    if report['status'] == 'complete' and 'input_file' in report and report['input_file'] == 'input.pdf':
                        use_cached_report = True
                        print(f"[INFO] server.py: Usando reporte en caché desde {report_path}")
            except Exception as e:
                print(f"[WARNING] server.py: Error al leer reporte en caché: {str(e)}")
                
        # Generar reporte si no existe o no es válido
        if not use_cached_report:
            print(f"[INFO] server.py: Iniciando generación de reporte")
            report = create_report(file_path, output_dir)
            print(f"[INFO] server.py: Reporte generado con estado: {report['status']}")
            
            # Guardar el reporte para uso futuro
            try:
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, ensure_ascii=False, indent=2)
                print(f"[INFO] server.py: Reporte guardado en {report_path}")
            except Exception as e:
                print(f"[WARNING] server.py: Error al guardar reporte: {str(e)}")
        
        # Convertir reporte a HTML si se solicita
        format_type = request.args.get('format', 'json')
        print(f"[DEBUG] server.py: Formato solicitado: {format_type}")
        
        if format_type == 'html':
            html_content = get_report_html(report, output_dir)
            print(f"[INFO] server.py: Reporte HTML generado, longitud: {len(html_content)} caracteres")
            print(f"[DEBUG] server.py: Primeros 100 caracteres del HTML: {html_content[:100]}")
            
            response_data = {
                'success': True,
                'html': html_content,
                'status': report['status']
            }
            
            return jsonify(response_data)
        
        # Por defecto devolver el reporte como JSON
        print(f"[INFO] server.py: Devolviendo reporte en formato JSON")
        return jsonify({
            'success': True,
            'report': report
        })
    
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"[ERROR] server.py: Error en análisis: {str(e)}")
        print(f"[DEBUG] server.py: {error_traceback}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_traceback
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')