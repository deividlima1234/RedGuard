# utils/archivo.py

import csv
import os
from datetime import datetime

def guardar_csv(dispositivos, usuarios):
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    carpeta_reportes = "reportes/red"
    if not os.path.exists(carpeta_reportes):
        os.makedirs(carpeta_reportes)
    nombre_archivo = os.path.join(carpeta_reportes, f"resultado-{fecha}.csv")

    with open(nombre_archivo, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["IP", "MAC", "Usuario", "Nombre Host", "Método Detección"])
        for d in dispositivos:
            usuario = usuarios.get(d["mac"], "Desconocido")
            nombre_host = d.get("nombre_host", "Desconocido")
            metodo = d.get("tipo", "Desconocido")
            writer.writerow([d["ip"], d["mac"], usuario, nombre_host, metodo])

    print(f"Resultado guardado en {nombre_archivo}")
    return nombre_archivo
