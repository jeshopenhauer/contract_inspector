"""
Script para preparar la compilación del ejecutable.
Crea directorios necesarios y asegura que existan archivos mínimos.
"""

import os
import sys

def main():
    print("Preparando entorno para compilación...")
    
    # Directorio base del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Asegurarse de que existe el directorio output_split
    output_split_dir = os.path.join(base_dir, 'output_split')
    os.makedirs(output_split_dir, exist_ok=True)
    print(f"Directorio output_split creado en: {output_split_dir}")
    
    # Crear archivo placeholder en output_split si está vacío
    if not os.listdir(output_split_dir):
        placeholder_path = os.path.join(output_split_dir, '.placeholder')
        with open(placeholder_path, 'w', encoding='utf-8') as f:
            f.write("# Este archivo es un marcador para asegurar que el directorio output_split se incluye en el paquete.\n")
        print(f"Archivo placeholder creado en: {placeholder_path}")
    
    print("Preparación completada.")
    return 0

if __name__ == "__main__":
    sys.exit(main())