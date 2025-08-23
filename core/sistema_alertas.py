# core/sistema_alertas.py

import smtplib
from email.message import EmailMessage
import os
from config.settings import CONTRASENA_APP

def enviar_correo(remitente, destinatario, archivo_adjunto, asunto=None, mensaje=None):
    """
    Envía un correo con un archivo adjunto.
    Los parámetros asunto y mensaje son opcionales y permiten personalizar el correo.
    """
    if asunto is None:
        asunto = "🔐 RedGuard - Nuevo informe de escaneo de red"
    if mensaje is None:
        mensaje = (
            "Hola,\n\n"
            "Adjunto encontrarás el último informe generado por RedGuard.\n\n"
            "Saludos,\nRedGuard"
        )

    try:
        email = EmailMessage()
        email['From'] = remitente
        email['To'] = destinatario
        email['Subject'] = asunto
        email.set_content(mensaje)

        with open(archivo_adjunto, 'rb') as f:
            contenido = f.read()
            nombre_archivo = os.path.basename(archivo_adjunto)
            email.add_attachment(contenido, maintype='application', subtype='octet-stream', filename=nombre_archivo)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(remitente, CONTRASENA_APP)
            smtp.send_message(email)

        print("[✔] Correo enviado correctamente.")

    except Exception as e:
        print(f"[✖] Error al enviar el correo: {e}")
