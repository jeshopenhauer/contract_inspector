@echo off
echo Iniciando Servidor de Inspector de Contratos...
echo.

REM Verificar si existe un entorno virtual
if exist ".venv\Scripts\python.exe" (
    echo Entorno virtual encontrado.
    
    REM Usar el intérprete de Python del entorno virtual directamente
    echo Iniciando servidor en http://localhost:5000
    .venv\Scripts\python.exe server.py
) else (
    echo No se encontró un entorno virtual.
    echo Asegúrese de tener instaladas todas las dependencias necesarias:
    echo - Flask
    echo - Flask-CORS
    echo.
    
    REM Intentar ejecutar directamente con Python
    echo Intentando iniciar el servidor directamente...
    echo Iniciando servidor en http://localhost:5000
    python server.py
)

pause