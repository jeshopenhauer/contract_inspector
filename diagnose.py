"""
Script de diagnóstico para el Contract Inspector

Este script verifica la estructura de archivos y directorios del Contract Inspector.
Ayuda a detectar problemas con las rutas de archivos y directorios.
"""

import os
import sys

def check_directory(dir_path, description):
    """Verifica si existe un directorio y muestra su contenido."""
    print(f"\n== Comprobando directorio {description}: {dir_path} ==")
    
    if not os.path.exists(dir_path):
        print(f"  ❌ ERROR: El directorio no existe")
        return False
        
    if not os.path.isdir(dir_path):
        print(f"  ❌ ERROR: La ruta existe pero no es un directorio")
        return False
    
    print(f"  ✅ El directorio existe")
    
    try:
        files = os.listdir(dir_path)
        print(f"  📁 Contiene {len(files)} archivos/subdirectorios:")
        
        for file in files:
            full_path = os.path.join(dir_path, file)
            if os.path.isdir(full_path):
                print(f"    📁 {file}/")
            else:
                size = os.path.getsize(full_path)
                print(f"    📄 {file} ({size} bytes)")
    except Exception as e:
        print(f"  ❌ Error al listar contenido: {str(e)}")
        return False
    
    return True

def main():
    """Función principal del diagnóstico."""
    print("=== DIAGNÓSTICO DEL CONTRACT INSPECTOR ===\n")
    
    # Determinar el directorio base
    if getattr(sys, 'frozen', False):
        # Ejecutando como aplicación empaquetada
        base_dir = os.path.dirname(sys.executable)
        print(f"Ejecutando como aplicación empaquetada (PyInstaller)")
        print(f"Directorio base: {base_dir}")
    else:
        # Ejecutando como script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Ejecutando como script Python")
        print(f"Directorio base: {base_dir}")
    
    # Comprobar directorios críticos
    check_directory(base_dir, "base")
    check_directory(os.path.join(base_dir, "inspector_functions"), "inspector_functions")
    check_directory(os.path.join(base_dir, "template"), "template")
    check_directory(os.path.join(base_dir, "output_split"), "output_split")
    
    # Comprobar archivos críticos
    print("\n== Comprobando archivos críticos ==")
    critical_files = [
        "app.py" if not getattr(sys, 'frozen', False) else "ContractInspector.exe",
        "index.html",
        "style.css",
        "functions.js",
        os.path.join("inspector_functions", "create_report.py")
    ]
    
    for file in critical_files:
        file_path = os.path.join(base_dir, file)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✅ {file} existe ({size} bytes)")
        else:
            print(f"  ❌ {file} no existe")
    
    print("\n=== FIN DEL DIAGNÓSTICO ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())