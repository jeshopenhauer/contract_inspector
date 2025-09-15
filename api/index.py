from flask import Flask, request, jsonify, send_from_directory
import os
import sys
import json

# Configuración básica para Vercel
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
app.config['JSON_AS_ASCII'] = False  # Permite caracteres Unicode en las respuestas JSON

# Obtener directorios para las rutas de archivos
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

# Agregar CORS headers
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/', methods=['GET', 'OPTIONS'])
def index():
    """Ruta principal que sirve la página web"""
    try:
        return send_from_directory(parent_dir, 'index.html')
    except Exception as e:
        # HTML mínimo como respaldo
        return '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Inspector de Contratos</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="header">
        <h1>Inspector de Contratos - Vercel</h1>
        <div>
            <span>Servidor activo</span>
        </div>
    </div>
    <div>
        <p>Versión mínima para Vercel. El servidor está funcionando.</p>
    </div>
    <script src="/functions.js"></script>
</body>
</html>'''
@app.route('/style.css', methods=['GET'])
def serve_css():
    try:
        return send_from_directory(parent_dir, 'style.css')
    except Exception as e:
        return "", 404

@app.route('/functions.js', methods=['GET'])
def serve_js():
    try:
        return send_from_directory(parent_dir, 'functions.js')
    except Exception as e:
        return "", 404

@app.route('/api/status', methods=['GET'])
def status():
    """Endpoint para verificar el estado del servidor"""
    return jsonify({
        'status': 'ok',
        'message': 'API is running on Vercel',
        'version': '1.0'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint simulado para cargar archivos (versión Vercel)"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No se ha proporcionado ningún archivo'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nombre de archivo vacío'}), 400
        
        # En Vercel no podemos guardar archivos permanentemente
        # Este es un endpoint simulado para desarrollo
        return jsonify({
            'success': True,
            'message': 'Esta es una versión de demostración en Vercel. El procesamiento completo de PDFs no está disponible en este entorno.',
            'demo': True,
            'filename': file.filename
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analyze', methods=['GET'])
def analyze_contract():
    """Endpoint simulado para análisis (versión Vercel)"""
    return jsonify({
        'success': True,
        'message': 'Esta es una versión de demostración en Vercel. El procesamiento completo de PDFs no está disponible en este entorno.',
        'demo': True
    })

# Para Vercel - nos aseguramos de que esto se ejecute
if __name__ == '__main__':
    app.run(debug=True)

# La aplicación Flask ya está definida como "app", que es lo que Vercel espera