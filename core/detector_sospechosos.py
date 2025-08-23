# core/detector_sospechosos.py

from core.procesador import escanear_red_completa
from core.comparador_lista_blanca import cargar_lista_blanca
from datetime import datetime
from utils import obtener_rango_red  # ✅ Detectar rango automáticamente
import os
import csv
import json

# 📌 Ruta de la lista blanca
RUTA_LISTA_BLANCA = "data/usuarios.json"

# 📌 Detectar interfaz y rango de red automáticamente
INTERFAZ = "wlan0"  # Cambia a "eth0" si usas cable
RANGO_IP = obtener_rango_red(INTERFAZ)
RANGO_LIMPIO = RANGO_IP.replace("/", "_") if RANGO_IP else "rango_desconocido"

# 📂 Carpetas de reportes
CARPETA_CSV = "reportes/sospechosos/csv"
CARPETA_JSON = "reportes/sospechosos/json"
CARPETA_AUDITORIA = "reportes/auditoria"
os.makedirs(CARPETA_CSV, exist_ok=True)
os.makedirs(CARPETA_JSON, exist_ok=True)
os.makedirs(CARPETA_AUDITORIA, exist_ok=True)


def guardar_reporte_csv(sospechosos):
    """Guarda el reporte en formato CSV"""
    fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = os.path.join(
        CARPETA_CSV, f"resultado_{RANGO_LIMPIO}_{fecha_actual}.csv"
    )

    with open(nombre_archivo, mode="w", newline="", encoding="utf-8") as archivo_csv:
        escritor = csv.writer(archivo_csv)
        escritor.writerow(
            ["MAC", "IP", "Tipo", "Nombre Host", "Usuario", "Fecha detección", "Rango Escaneado"]
        )
        for s in sospechosos:
            escritor.writerow([
                s.get("mac", "Desconocido"),
                s.get("ip", "Desconocido"),
                s.get("tipo", "Desconocido"),
                s.get("nombre_host", "Desconocido"),
                s.get("usuario", "Desconocido"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                RANGO_IP
            ])

    print(f"[💾] Reporte CSV guardado en: {nombre_archivo}")
    return nombre_archivo


def guardar_reporte_json(sospechosos, modo="normal"):
    """Guarda el reporte en formato JSON unificado"""
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 📌 Definir carpeta y nombre de archivo según el modo
    if modo == "auditoria":
        carpeta = CARPETA_AUDITORIA
        nombre_archivo = os.path.join(carpeta, f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    else:
        carpeta = CARPETA_JSON
        nombre_archivo = os.path.join(
            carpeta, f"resultado_{RANGO_LIMPIO}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    # 📌 Estructura unificada del JSON
    data = {
        "fecha_generacion": fecha_actual,
        "rango_ip_escaneado": RANGO_IP,
        "sospechosos": sospechosos
    }

    with open(nombre_archivo, "w", encoding="utf-8") as archivo_json:
        json.dump(data, archivo_json, indent=4, ensure_ascii=False)

    print(f"[💾] Reporte JSON guardado en: {nombre_archivo}")
    return nombre_archivo, data


def detectar_sospechosos(modo="normal"):
    """
    Escanea la red y detecta dispositivos que NO estén en la lista blanca.
    Combina escaneo ARP + Ping Scan para mayor precisión.
    """
    if not RANGO_IP:
        print("[⚠] No se pudo detectar el rango de red.")
        return None, None

    print(f"[🔍] Escaneando la red en {RANGO_IP} (ARP + Ping Scan)...")
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
            print(f" - MAC: {s.get('mac')} | IP: {s.get('ip')} | Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # 🔑 Guardar reportes
        archivo_json, _ = guardar_reporte_json(sospechosos, modo=modo)

        # Solo guardar CSV si es ejecución normal (independiente)
        archivo_csv = None
        if modo == "normal":
            archivo_csv = guardar_reporte_csv(sospechosos)

        return archivo_csv, archivo_json
    else:
        print("[✔] No se detectaron dispositivos sospechosos.")
        return None, None


# 🔑 Función wrapper para auditoría
def ejecutar(interfaz=None, modo_auditoria=True):
    """
    Función de compatibilidad para ser llamada desde el módulo de auditoría.
    Si modo_auditoria=True -> guarda JSON en reportes/auditoria en formato unificado.
    Si modo_auditoria=False -> guarda reportes normales (CSV + JSON).
    """
    rango = RANGO_IP
    dispositivos = escanear_red_completa(rango)
    lista_blanca = cargar_lista_blanca(RUTA_LISTA_BLANCA)

    sospechosos = []
    for disp in dispositivos:
        mac = disp.get("mac", "").lower()
        if mac not in (m.lower() for m in lista_blanca.keys()):
            sospechosos.append(disp)

    if modo_auditoria:
        # 🔥 Guardar reporte JSON en formato unificado (reportes/auditoria)
        archivo_json, data = guardar_reporte_json(sospechosos, modo="auditoria")

        return data  # 👈 Retorna el JSON en formato correcto

    else:
        # Modo independiente -> guarda CSV + JSON
        archivo_csv, archivo_json = detectar_sospechosos()
        return {
            "csv": archivo_csv,
            "json": archivo_json,
            "estado": "ok" if archivo_csv or archivo_json else "sin_sospechosos"
        }


if __name__ == "__main__":
    detectar_sospechosos(modo="normal")
