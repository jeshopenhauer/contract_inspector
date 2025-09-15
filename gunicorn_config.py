# Configuración de Gunicorn para servidor de producción

# Número de workers (procesos) - recomendado: (2 x núm_CPU) + 1
workers = 4

# Número de hilos por worker
threads = 2

# Timeout en segundos para las solicitudes
timeout = 120

# Enlace - 0.0.0.0 para aceptar conexiones desde cualquier IP
bind = '0.0.0.0:$PORT'

# Nivel de registro
loglevel = 'info'

# Acceso a archivos
accesslog = '-'
errorlog = '-'

# Precargar la aplicación para mejorar el rendimiento
preload_app = True