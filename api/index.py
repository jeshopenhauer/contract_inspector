from flask import Flask, request, jsonify, make_response, send_from_directory
from flask_cors import CORS
import os
import sys
import json

# Añadir el directorio padre al path para poder importar inspector_functions
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Importar la función para crear reportes
try:
    from inspector_functions.create_report import create_report, get_report_html
except ImportError:
    print("Warning: No se pudieron importar las funciones de inspector")
    def create_report(*args, **kwargs):
        return {"status": "error", "message": "Funciones no disponibles"}
    def get_report_html(*args, **kwargs):
        return "<p>Funciones no disponibles</p>"

app = Flask(__name__)

# Configuración para aumentar el tamaño máximo de los archivos
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['JSON_AS_ASCII'] = False  # Permite caracteres Unicode en las respuestas JSON

# Configurar CORS de forma más permisiva
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
    print("[INFO] api/index.py: Solicitud recibida en la ruta principal")
    
    # Comprobar si se solicita el archivo html o la API
    accept_header = request.headers.get('Accept', '')
    if 'text/html' in accept_header and 'application/json' not in accept_header:
        print("[INFO] api/index.py: Solicitud HTML detectada, sirviendo index.html")
        try:
            return send_from_directory(parent_dir, 'index.html')
        except:
            return '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Inspector de Contratos</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="header header-flex">
        <h1>Inspector de Contratos</h1>
        <div class="header-actions">
            <div class="server-status">
                <span id="server-indicator" class="indicator"></span>
                <span id="server-status-text">Verificando...</span>
            </div>
            <button class="btn" onclick="loadContract()">Cargar contrato PDF</button>
            <button class="btn btn-secondary" onclick="clearSavedReports()">Limpiar reportes</button>
        </div>
    </div>
    <div id="panel-container"></div>
    <script src="/functions.js"></script>
</body>
</html>'''
    
    # Por defecto responder con estado JSON
    return jsonify({
        'status': 'ok',
        'message': 'Server is running on Vercel'
    })

@app.route('/style.css', methods=['GET'])
def serve_css():
    try:
        return send_from_directory(parent_dir, 'style.css')
    except:
        return "", 404

@app.route('/functions.js', methods=['GET'])
def serve_js():
    try:
        return send_from_directory(parent_dir, 'functions.js')
    except:
        return "", 404

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,X-Requested-With,Cache-Control,Accept,Origin,Pragma,Expires")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS,HEAD")
        print(f"[DEBUG] api/index.py: Respondiendo a solicitud OPTIONS/preflight")
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
    
    return response

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        print(f"[INFO] api/index.py: Recibida solicitud de carga de archivo")
        
        if 'file' not in request.files:
            print(f"[ERROR] api/index.py: No se encontró el archivo en la solicitud")
            return jsonify({'success': False, 'error': 'No se ha proporcionado ningún archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            print(f"[ERROR] api/index.py: Nombre de archivo vacío")
            return jsonify({'success': False, 'error': 'Nombre de archivo vacío'}), 400
        
        print(f"[INFO] api/index.py: Procesando archivo: {file.filename}")
        
        # En Vercel, usar /tmp para archivos temporales
        temp_dir = '/tmp'
        file_path = os.path.join(temp_dir, 'input.pdf')
        print(f"[DEBUG] api/index.py: Guardando archivo en {file_path}")
        file.save(file_path)
        
        print(f"[INFO] api/index.py: Archivo guardado correctamente")
        
        # Iniciar análisis automáticamente
        print(f"[INFO] api/index.py: Iniciando análisis automático")
        
        # Definir directorio de salida temporal
        output_dir = os.path.join(temp_dir, 'output_split')
        os.makedirs(output_dir, exist_ok=True)
        
        # Generar reporte
        try:
            report = create_report(file_path, output_dir)
            print(f"[INFO] api/index.py: Reporte generado con estado: {report['status']}")
            
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
            print(f"[ERROR] api/index.py: Error al generar reporte: {str(e)}")
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
        print(f"[INFO] api/index.py: Recibida solicitud de análisis manual")
        
        # En Vercel, verificar archivo temporal
        temp_dir = '/tmp'
        file_path = os.path.join(temp_dir, 'input.pdf')
        if not os.path.exists(file_path):
            print(f"[ERROR] api/index.py: No existe el archivo {file_path}")
            return jsonify({
                'success': False,
                'error': 'No se ha subido ningún archivo para analizar'
            }), 400
        
        print(f"[DEBUG] api/index.py: Verificado archivo {file_path}, tamaño: {os.path.getsize(file_path)} bytes")
        
        # Definir directorio de salida temporal
        output_dir = os.path.join(temp_dir, 'output_split')
        os.makedirs(output_dir, exist_ok=True)
        print(f"[DEBUG] api/index.py: Directorio de salida: {output_dir}")
        
        # Generar reporte
        print(f"[INFO] api/index.py: Iniciando generación de reporte")
        report = create_report(file_path, output_dir)
        print(f"[INFO] api/index.py: Reporte generado con estado: {report['status']}")
        
        # Convertir reporte a HTML si se solicita
        format_type = request.args.get('format', 'json')
        print(f"[DEBUG] api/index.py: Formato solicitado: {format_type}")
        
        if format_type == 'html':
            html_content = get_report_html(report, output_dir)
            print(f"[INFO] api/index.py: Reporte HTML generado, longitud: {len(html_content)} caracteres")
            
            response_data = {
                'success': True,
                'html': html_content,
                'status': report['status']
            }
            
            return jsonify(response_data)
        
        # Por defecto devolver el reporte como JSON
        print(f"[INFO] api/index.py: Devolviendo reporte en formato JSON")
        return jsonify({
            'success': True,
            'report': report
        })
    
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"[ERROR] api/index.py: Error en análisis: {str(e)}")
        print(f"[DEBUG] api/index.py: {error_traceback}")
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': error_traceback
        }), 500

# Para Vercel, la función debe ser la aplicación Flask
def handler(request):
    return app(request.environ, start_response)

# Export para Vercel
app = app