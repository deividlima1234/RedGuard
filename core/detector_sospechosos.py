# core/detector_sospechosos.py

from core.procesador import escanear_red_completa
from core.comparador_lista_blanca import cargar_lista_blanca
from datetime import datetime
from utils import obtener_rango_red # ✅ Importar función
import os
import csv
import json

RUTA_LISTA_BLANCA = "data/usuarios.json"

# Detectar automáticamente interfaz y rango de red
INTERFAZ = "wlan0"  # Cambia a "eth0" si usas cable
RANGO_IP = obtener_rango_red(INTERFAZ)
RANGO_LIMPIO = RANGO_IP.replace("/", "_") if RANGO_IP else "rango_desconocido"

# Carpetas de reportes separadas por formato
CARPETA_CSV = "reportes/sospechosos/csv"
CARPETA_JSON = "reportes/sospechosos/json"
os.makedirs(CARPETA_CSV, exist_ok=True)
os.makedirs(CARPETA_JSON, exist_ok=True)


def guardar_reporte_csv(sospechosos):
    fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = os.path.join(CARPETA_CSV, f"resultado_{RANGO_LIMPIO}_{fecha_actual}.csv")
    
    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo_csv:
        escritor = csv.writer(archivo_csv)
        escritor.writerow(["MAC", "IP", "Tipo", "Nombre Host", "Usuario", "Fecha detección", "Rango Escaneado"])
        for s in sospechosos:
            escritor.writerow([
                s.get('mac', 'Desconocido'),
                s.get('ip', 'Desconocido'),
                s.get('tipo', 'Desconocido'),
                s.get('nombre_host', 'Desconocido'),
                s.get('usuario', 'Desconocido'),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                RANGO_IP
            ])
    
    print(f"[💾] Reporte CSV guardado en: {nombre_archivo}")
    return nombre_archivo  # ⬅ devolver ruta


def guardar_reporte_json(sospechosos):
    fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = os.path.join(CARPETA_JSON, f"resultado_{RANGO_LIMPIO}_{fecha_actual}.json")
    
    with open(nombre_archivo, "w", encoding="utf-8") as archivo_json:
        json.dump({
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rango_ip_escaneado": RANGO_IP,
            "sospechosos": sospechosos
        }, archivo_json, indent=4, ensure_ascii=False)
    
    print(f"[💾] Reporte JSON guardado en: {nombre_archivo}")
    return nombre_archivo  # ⬅ devolver ruta




def detectar_sospechosos():
    """
    Escanea la red y muestra los dispositivos que no están en la lista blanca.
    """
    if not RANGO_IP:
        print("[⚠] No se pudo detectar el rango de red.")
        return None, None  # ⬅ para evitar error de unpack

    print(f"[🔍] Escaneando la red en {RANGO_IP} en busca de dispositivos...")
    dispositivos = escanear_red_completa(RANGO_IP)
    lista_blanca = cargar_lista_blanca(RUTA_LISTA_BLANCA)

    if not dispositivos:
        print("[ℹ] No se encontraron dispositivos en la red.")
        return None, None

    sospechosos = []
    for disp in dispositivos:
        mac = disp.get("mac", "").lower()
        if mac not in (m.lower() for m in lista_blanca.keys()):
            sospechosos.append(disp)

    if sospechosos:
        print("\n🚨 Dispositivos sospechosos detectados:")
        for s in sospechosos:
            print(f" - MAC: {s['mac']} | IP: {s['ip']} | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Guardar reportes en ambos formatos
        archivo_csv = guardar_reporte_csv(sospechosos)
        archivo_json = guardar_reporte_json(sospechosos)
        return archivo_csv, archivo_json
    else:
        print("[✔] No se detectaron dispositivos sospechosos.")
        return None, None



if __name__ == "__main__":
    detectar_sospechosos()
