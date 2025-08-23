import os
import json
import datetime
import subprocess

# Importar módulos
from core import escaneo_red, escaner_puertos, detector_sospechosos
from utils.utils import obtener_rango_red  # Se mantiene por si otros módulos lo necesitan


# -------------------------------
# FUNCIÓN: obtener interfaz activa
# -------------------------------
def obtener_interfaz_activa():
    """Detecta la interfaz activa (ej: wlan0, eth0)"""
    try:
        result = subprocess.run(['ip', 'route', 'show', 'default'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            partes = result.stdout.split()
            if "dev" in partes:
                return partes[partes.index("dev") + 1]
    except Exception as e:
        print(f"[⚠] Error al detectar interfaz: {e}")
    return None


# -------------------------------
# FUNCIÓN: ejecutar auditoría
# -------------------------------
def ejecutar_auditoria(modo="completa", operaciones=None):
    """
    Ejecuta la auditoría en modo completo o generar.
    - modo = "completa": ejecuta todas las operaciones.
    - modo = "generar": ejecuta operaciones seleccionadas.
      - Si operaciones es None -> menú interactivo (terminal).
      - Si operaciones es dict -> ejecuta solo lo marcado desde interfaz web.
    """
    reporte = {
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "modo": modo,
        "resultados": {}
    }

    # Detectar interfaz
    interfaz = obtener_interfaz_activa()

    # -------------------------------
    # MODO COMPLETO
    # -------------------------------
    if modo == "completa":
        print("[*] Ejecutando auditoría completa...")

        # Escaneo de red
        if interfaz:
            try:
                resultado_red = escaneo_red.ejecutar(interfaz=interfaz)
                reporte["resultados"]["escaneo_red"] = resultado_red
            except Exception as e:
                reporte["resultados"]["escaneo_red"] = {"error": str(e)}
        else:
            reporte["resultados"]["escaneo_red"] = {"error": "No se pudo detectar interfaz automáticamente"}

        # Escaneo de puertos
        try:
            ips_detectadas = [
                d["ip"] for d in reporte["resultados"].get("escaneo_red", {}).get("dispositivos", [])
            ]
            if not ips_detectadas:
                raise Exception("No se detectaron IPs activas para escanear.")

            resultados_puertos = {}
            puertos_comunes = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 8080]

            for ip in ips_detectadas:
                resultados_puertos[ip] = {}
                print(f"[*] Escaneando puertos comunes en {ip}...")
                resultado = escaner_puertos.escanear_puertos(ip, puertos=",".join(map(str, puertos_comunes)))
                dicc_puertos = {str(d["puerto"]): {"estado": d["estado"], "servicio": d["servicio"]} for d in resultado}
                resultados_puertos[ip].update(dicc_puertos)

            reporte["resultados"]["escaneo_puertos"] = resultados_puertos
        except Exception as e:
            reporte["resultados"]["escaneo_puertos"] = {"error": str(e)}

        # Detector de sospechosos
        try:
            resultado_sospechosos = detector_sospechosos.ejecutar(interfaz=interfaz)
            reporte["resultados"]["dispositivos_sospechosos"] = resultado_sospechosos
        except Exception as e:
            reporte["resultados"]["dispositivos_sospechosos"] = {"error": str(e)}

        return reporte

    # -------------------------------
    # MODO GENERAR
    # -------------------------------
    elif modo == "generar":
        if operaciones is None:
            # 🔹 Compatibilidad con terminal
            print("[*] Auditoría personalizada (Generar).")
            print("Seleccione los módulos a ejecutar:")
            print("1. Escaneo de Red")
            print("2. Escaneo de Puertos")
            print("3. Detector de Dispositivos Sospechosos")
            print("4. Finalizar selección")

            seleccionados = set()
            while True:
                opcion = input("Seleccione una opción (1-4): ").strip()
                if opcion == "1":
                    seleccionados.add("escaneo_red")
                elif opcion == "2":
                    seleccionados.add("escaneo_puertos")
                elif opcion == "3":
                    seleccionados.add("sospechosos")
                elif opcion == "4":
                    break
                else:
                    print("Opción inválida.")
        else:
            # 🔹 Usar selección enviada desde la interfaz web
            seleccionados = set()
            if operaciones.get("escaneo_red"): seleccionados.add("escaneo_red")
            if operaciones.get("escaneo_puertos"): seleccionados.add("escaneo_puertos")
            if operaciones.get("detectar_intrusos"): seleccionados.add("sospechosos")

        # -------------------------------
        # Ejecución según seleccionados
        # -------------------------------
        if "escaneo_red" in seleccionados:
            if interfaz:
                try:
                    resultado_red = escaneo_red.ejecutar(interfaz=interfaz)
                    reporte["resultados"]["escaneo_red"] = resultado_red
                except Exception as e:
                    reporte["resultados"]["escaneo_red"] = {"error": str(e)}
            else:
                reporte["resultados"]["escaneo_red"] = {"error": "No se pudo detectar interfaz automáticamente"}

        if "escaneo_puertos" in seleccionados:
            try:
                ips_detectadas = [
                    d["ip"] for d in reporte["resultados"].get("escaneo_red", {}).get("dispositivos", [])
                ]
                if not ips_detectadas:
                    raise Exception("No se detectaron IPs activas para escanear.")

                resultados_puertos = {}
                puertos_comunes = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 8080]

                for ip in ips_detectadas:
                    resultados_puertos[ip] = {}
                    print(f"[*] Escaneando puertos comunes en {ip}...")
                    resultado = escaner_puertos.escanear_puertos(ip, puertos=",".join(map(str, puertos_comunes)))
                    dicc_puertos = {str(d["puerto"]): {"estado": d["estado"], "servicio": d["servicio"]} for d in resultado}
                    resultados_puertos[ip].update(dicc_puertos)

                reporte["resultados"]["escaneo_puertos"] = resultados_puertos
            except Exception as e:
                reporte["resultados"]["escaneo_puertos"] = {"error": str(e)}

        if "sospechosos" in seleccionados:
            try:
                resultado_sospechosos = detector_sospechosos.ejecutar(interfaz=interfaz)
                reporte["resultados"]["dispositivos_sospechosos"] = resultado_sospechosos
            except Exception as e:
                reporte["resultados"]["dispositivos_sospechosos"] = {"error": str(e)}

        return reporte


# -------------------------------
# PUNTO DE ENTRADA
# -------------------------------   
if __name__ == "__main__":
    # Pedir al usuario el modo
    print("Seleccione el modo de auditoría:")
    print("1. Completa")
    print("2. Generar")
    opcion = input("Opción: ").strip()

    modo = "completa" if opcion == "1" else "generar"

    resultado = ejecutar_auditoria(modo=modo)

    # Guardar resultados en JSON
    os.makedirs("reportes/auditoria", exist_ok=True)
    archivo_salida = f"reportes/auditoria/reporte_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(archivo_salida, "w") as f:
        json.dump(resultado, f, indent=4)

    print(f"[✅] Auditoría ({modo}) completada. Reporte guardado en {archivo_salida}")