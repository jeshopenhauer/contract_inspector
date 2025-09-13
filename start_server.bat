@echo off
echo Iniciando Servidor de Inspector de Contratos...
echo.

REM Verificar si existe un entorno virtual
if exist ".venv\Scripts\python.exe" (
    echo Entorno virtual encontrado.
    
    REM Usar el intérprete de Python del entorno virtual directamente
    echo Obteniendo dirección IP local...
    REM Crear un script temporal para obtener la IP local
    echo import socket > get_ip.py
    echo hostname = socket.gethostname() >> get_ip.py
    echo local_ip = socket.gethostbyname(hostname) >> get_ip.py
    echo print(f"- Local: http://localhost:5000") >> get_ip.py
    echo print(f"- Red local: http://{local_ip}:5000") >> get_ip.py
    
    echo Iniciando servidor en:
    .venv\Scripts\python.exe get_ip.py
    .venv\Scripts\python.exe server.py
    
    REM Eliminar el script temporal
    del get_ip.py
) else (
    echo No se encontró un entorno virtual.
    echo Asegúrese de tener instaladas todas las dependencias necesarias:
    echo - Flask
    echo - Flask-CORS
    echo.
    
    REM Intentar ejecutar directamente con Python
    echo Intentando iniciar el servidor directamente...
    echo Obteniendo dirección IP local...
    REM Crear un script temporal para obtener la IP local
    echo import socket > get_ip.py
    echo hostname = socket.gethostname() >> get_ip.py
    echo local_ip = socket.gethostbyname(hostname) >> get_ip.py
    echo print(f"- Local: http://localhost:5000") >> get_ip.py
    echo print(f"- Red local: http://{local_ip}:5000") >> get_ip.py
    
    echo Iniciando servidor en:
    python get_ip.py
    python server.py
    
    REM Eliminar el script temporal
    del get_ip.py
)

pause