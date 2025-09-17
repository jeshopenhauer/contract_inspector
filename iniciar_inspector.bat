@echo off
echo Iniciando Contract Inspector...
echo Por favor, espere mientras se inicia el servidor y el navegador...
echo.

REM Verificar que existe el ejecutable
if not exist "dist\ContractInspector\ContractInspector.exe" (
    echo ERROR: No se encontró el ejecutable de Contract Inspector.
    echo Debe compilar la aplicación primero usando create_executable.bat
    echo.
    pause
    exit /b 1
)

REM Crear directorio output_split si no existe
if not exist "dist\ContractInspector\output_split" (
    echo Creando directorio output_split en la distribución...
    mkdir "dist\ContractInspector\output_split"
)

REM Asegurarse de que output_split esté en el directorio _internal
if not exist "dist\ContractInspector\_internal\output_split" (
    echo Creando directorio output_split en _internal...
    mkdir "dist\ContractInspector\_internal\output_split"
)

REM Iniciar la aplicación
echo Iniciando aplicación...
start "" "dist\ContractInspector\ContractInspector.exe"

echo.
echo Contract Inspector ha sido iniciado. Puede cerrar esta ventana.
timeout /t 5 >nul