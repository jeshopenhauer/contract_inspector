@echo off
echo Creando ejecutable de Contract Inspector...

REM Ejecutar script de preparación
echo Ejecutando preparación...
python prepare_build.py

if errorlevel 1 (
    echo Error en la preparación del entorno.
    pause
    exit /b 1
)

echo.
echo Compilando ejecutable...
REM Ejecutar PyInstaller con el archivo de especificación
pyinstaller contract_inspector.spec

echo.
if errorlevel 0 (
    echo ==========================================
    echo Ejecutable creado correctamente!
    echo El ejecutable se encuentra en la carpeta 'dist\ContractInspector'
    echo Para distribuirlo, copie toda la carpeta 'ContractInspector' a los usuarios.
    echo ==========================================
) else (
    echo ERROR: No se pudo crear el ejecutable. Revise los mensajes anteriores.
)

echo.
pause