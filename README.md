# Contract Inspector

Aplicación de análisis de contratos con interfaz web y empaquetada como ejecutable.

## Preparación para distribución

Para preparar la aplicación para su distribución a los usuarios de la oficina, siga los siguientes pasos:

1. **Limpiar los entornos virtuales**:
   - Ejecute `prepare_distribution.bat`
   - Este script elimina los entornos virtuales existentes y crea uno nuevo con solo los paquetes esenciales
   - Responda "s" cuando se le pregunte si desea continuar

2. **Crear el ejecutable**:
   - Si eligió crear el ejecutable en el paso anterior, este se generará automáticamente
   - Si no, puede ejecutar `create_executable.bat` en cualquier momento

3. **Distribución**:
   - El ejecutable se creará en la carpeta `dist\ContractInspector`
   - Copie toda esta carpeta a los usuarios finales
   - Los usuarios solo necesitan hacer doble clic en `iniciar_inspector.bat` para iniciar la aplicación

## Estructura del paquete distribuible

El paquete distribuible contiene:

- `ContractInspector.exe`: El ejecutable principal
- `iniciar_inspector.bat`: Script para iniciar la aplicación
- Archivos necesarios para el funcionamiento (HTML, CSS, JS)
- Carpetas con plantillas y funciones

## Requisitos del sistema

- Windows 10 o superior
- No requiere instalación de Python ni otras dependencias
- Navegador web moderno (Chrome, Firefox, Edge)

## Notas importantes

- No elimine ni modifique ningún archivo del paquete distribuible
- Si necesita modificar la aplicación, hágalo en el proyecto original y vuelva a crear el ejecutable
- La aplicación crea un servidor web local temporal que se cierra al cerrar la aplicación