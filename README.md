# Inspector de Contratos

Este proyecto proporciona una interfaz web para analizar y comparar contratos con una plantilla de referencia.

## Requisitos

- Python 3.8 o superior
- Un entorno virtual de Python
- Navegador web moderno

## Instalación

1. Clone este repositorio
2. Configure el entorno virtual de Python:
   ```
   python -m venv .venv
   ```
3. Active el entorno virtual:
   - En Linux/Mac:
     ```
     source .venv/bin/activate
     ```
   - En Windows:
     ```
     .venv\Scripts\activate
     ```
4. Instale las dependencias:
   ```
   pip install flask flask-cors pdfminer.six
   ```

## Uso

### Iniciar el servidor

1. Ejecute el script de inicio según su sistema operativo:
   - En Linux:
     ```
     ./start_server_linux.py
     ```
   - En Windows:
     ```
     start_server.bat
     ```

2. Acceder a la aplicación:
   
   El servidor mostrará las URLs disponibles al iniciar. Hay dos formas de acceder:
   
   - **Acceso local** (solo desde el mismo equipo donde se ejecuta el servidor):
     ```
     http://localhost:5000
     ```
   
   - **Acceso desde la red** (desde otros equipos en la misma red):
     ```
     http://IP-DEL-SERVIDOR:5000
     ```
     Donde "IP-DEL-SERVIDOR" es la dirección IP que muestra el script al iniciar.
     Por ejemplo: `http://192.168.1.138:5000`

### Uso de la aplicación

1. Verifique que el indicador verde junto al botón "Cargar contrato" esté encendido, lo que indica que el servidor está funcionando correctamente.
2. Haga clic en "Cargar contrato PDF" y seleccione un archivo PDF de contrato.
3. La aplicación procesará el archivo y mostrará un análisis detallado con comparaciones estadísticas y de párrafos contra la plantilla.

## Solución de problemas

- **Si el indicador de conexión está en rojo**: El servidor no está en ejecución. Asegúrese de ejecutar el script de inicio del servidor.
- **Si no se muestra el reporte**: Revise la consola del navegador (F12) para ver mensajes de error detallados.
- **Errores CORS**: Asegúrese de acceder a la aplicación usando la URL proporcionada por el servidor y no desde Live Server o cualquier otro servidor.

## Estructura de archivos

- `server.py`: Servidor Flask principal
- `functions.js`: Funciones de JavaScript para el cliente
- `index.html`: Página web principal
- `style.css`: Estilos CSS
- `inspector_functions/`: Módulos para el análisis de contratos
  - `create_report.py`: Generación del reporte principal
  - `inspector_statistics.py`: Análisis estadístico de texto
  - `inspector_thermodynamics.py`: Análisis de párrafos
  - `pdf_to_txt_pdfminer.py`: Conversión de PDF a texto
  - `txt_to_txt_splitter.py`: División de texto en secciones

## Notas

Para evitar problemas de CORS, siempre use la aplicación desde la URL que proporciona el servidor Flask y no desde servidores de desarrollo como Live Server de VS Code.

## Compartir con compañeros

Para compartir esta aplicación con sus compañeros en la misma red:

1. Ejecute el script de inicio del servidor (`start_server.bat` en Windows o `start_server_linux.py` en Linux)
2. El script mostrará la dirección IP y puerto donde está disponible la aplicación (ejemplo: `http://192.168.1.138:5000`)
3. Comparta esta dirección con sus compañeros
4. Sus compañeros pueden acceder simplemente ingresando esa dirección en su navegador

> **Nota:** Todos los usuarios deben estar conectados a la misma red (como la WLAN de la empresa) para que esto funcione.
