@echo off
echo Ejecutando diagnóstico del Contract Inspector...
echo.

REM Ejecutar el script de diagnóstico desde el ejecutable
cd dist\ContractInspector
ContractInspector.exe --diagnose

echo.
pause