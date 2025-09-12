@echo off
echo Iniciando Servidor de Inspector de Contratos...
echo.

REM Activar entorno virtual si existe
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Entorno virtual activado.
) else (
    echo No se encontró un entorno virtual.
    echo Asegúrese de tener instaladas todas las dependencias necesarias:
    echo - Flask
    echo - Flask-CORS
    echo.
)

REM Iniciar el servidor
echo Iniciando servidor en http://localhost:5000
.venv\Scripts\python.exe server.py

pause