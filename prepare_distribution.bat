@echo off
echo ==========================================
echo  OPTIMIZACIÓN Y PREPARACIÓN PARA DISTRIBUCIÓN
echo           CONTRACT INSPECTOR
echo ==========================================
echo.

REM Ejecutar el script de limpieza de entornos
python clean_env.py

REM Verificar si el script terminó correctamente
if errorlevel 0 (
    echo.
    echo ¿Desea crear el ejecutable ahora? (s/n)
    choice /c SN /m "Seleccione una opción"
    
    if errorlevel 2 (
        echo.
        echo Proceso finalizado. No se creará el ejecutable.
        goto :end
    )
    
    if errorlevel 1 (
        call create_executable.bat
    )
) else (
    echo.
    echo No se pudo completar la limpieza del entorno.
)

:end
echo.
pause