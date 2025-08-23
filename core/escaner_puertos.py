import subprocess
import os
import csv
from datetime import datetime

REPORTE_DIR = "reportes/puertos"

def crear_carpeta_reportes():
    if not os.path.exists(REPORTE_DIR):
        os.makedirs(REPORTE_DIR)

def guardar_resultados_csv(ip, resultados):
    crear_carpeta_reportes()
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ip_formateada = ip.replace(".", "-")
    nombre_archivo = f"resultado-puertos-{ip_formateada}-{fecha}.csv"
    ruta_completa = os.path.join(REPORTE_DIR, nombre_archivo)

    with open(ruta_completa, mode="w", newline="", encoding="utf-8") as f:
        escritor_csv = csv.writer(f)
        # Línea inicial con IP
        escritor_csv.writerow([f"IP escaneada: {ip}"])
        escritor_csv.writerow([])  # línea en blanco

        # Ahora escribimos el encabezado y datos
        escritor = csv.DictWriter(f, fieldnames=["puerto", "estado", "servicio"])
        escritor.writeheader()
        for r in resultados:
            escritor.writerow(r)

    return ruta_completa

def escanear_puertos(ip_objetivo, puertos="1-1024"):
    try:
        comando = ["nmap", "-p", puertos, "-sV", ip_objetivo]  # sin --host-timeout para evitar errores
        resultado = subprocess.run(comando, capture_output=True, text=True)

        if resultado.returncode != 0:
            raise Exception(resultado.stderr.strip())

        print("=== Salida Nmap ===")
        print(resultado.stdout)
        print("===================")

        resultados = []

        for linea in resultado.stdout.splitlines():
            if "/tcp" in linea:
                partes = linea.split()
                if len(partes) >= 3:
                    puerto_proto = partes[0]
                    estado = partes[1]
                    servicio = " ".join(partes[2:])

                    try:
                        puerto = int(puerto_proto.split("/")[0])
                    except ValueError:
                        continue  # Ignorar líneas mal formateadas

                    resultados.append({
                        "puerto": puerto,
                        "estado": estado,
                        "servicio": servicio
                    })

        return resultados

    except Exception as e:
        print(f"[!] Error al escanear puertos en {ip_objetivo}: {e}")
        return []
    
    