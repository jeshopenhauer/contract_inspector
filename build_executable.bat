@echo off
echo Contract Inspector - Generador de Ejecutable
echo ===================================
echo.

echo 1. Instalando dependencias necesarias...
pip install pyinstaller flask flask_cors pdfminer.six
echo.

echo 2. Generando ejecutable con PyInstaller...
pyinstaller contract_inspector.spec
echo.

echo 3. Proceso finalizado.
echo.
echo El ejecutable ha sido creado en la carpeta "dist\ContractInspector".
echo Para distribuir la aplicación, comparte toda la carpeta "dist\ContractInspector".
echo Los usuarios solo necesitarán hacer doble clic en "ContractInspector.exe" para usar la aplicación.
echo.
echo Presiona cualquier tecla para abrir la carpeta con el ejecutable...
pause > nul
explorer "dist\ContractInspector"