import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# Tiempo de escucha
TIEMPO_ESCUCHA = 10

# Correo (tomado desde .env)
REMITENTE = os.getenv("REMITENTE")
DESTINATARIO = os.getenv("DESTINATARIO")
CONTRASENA_APP = os.getenv("CONTRASENA_APP")
