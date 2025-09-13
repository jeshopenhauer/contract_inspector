#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    print("Iniciando Servidor de Inspector de Contratos...")
    print("")
    
    # Verificar si existe un entorno virtual
    venv_activate_path = ".venv/bin/activate"
    if os.path.exists(venv_activate_path):
        print("Entorno virtual encontrado.")
        
        # Usar el intérprete de Python del entorno virtual directamente
        venv_python = ".venv/bin/python"
        if os.path.exists(venv_python):
            print("Iniciando servidor en http://localhost:5000")
            subprocess.call([venv_python, "server.py"])
        else:
            print("No se pudo encontrar el ejecutable de Python en el entorno virtual.")
            print("Intentando con el Python del sistema...")
            print("Iniciando servidor en http://localhost:5000")
            subprocess.call(["python", "server.py"])
    else:
        print("No se encontró un entorno virtual.")
        print("Asegúrese de tener instaladas todas las dependencias necesarias:")
        print("- Flask")
        print("- Flask-CORS")
        print("")
        
        # Intentar ejecutar directamente con Python
        print("Intentando iniciar el servidor directamente...")
        print("Iniciando servidor en http://localhost:5000")
        subprocess.call(["python", "server.py"])

if __name__ == "__main__":
    main()
