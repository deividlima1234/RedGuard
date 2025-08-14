from flask import Flask, request, jsonify, render_template
from core.procesador import ejecutar_escaneo
from datetime import datetime
import json, os, tempfile
import csv

app = Flask(__name__)

RUTA_USUARIOS = "data/usuarios.json"

# ==============================
# 📌 FUNCIONES AUXILIARES
# ==============================
def leer_usuarios_lista():
    """
    Lee usuarios.json y devuelve siempre una lista de objetos
    con identificador, nombre y fecha (para la lista blanca).
    """
    if os.path.exists(RUTA_USUARIOS):
        with open(RUTA_USUARIOS, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    return [
                        {"identificador": mac, "nombre": nombre, "fecha": "Desconocida"}
                        for mac, nombre in data.items()
                    ]
                if isinstance(data, list):
                    return data
            except json.JSONDecodeError:
                return []
    return []

def leer_usuarios_dict():
    """
    Lee usuarios.json y devuelve siempre un diccionario {MAC: nombre}
    (para el módulo de escaneo).
    """
    if os.path.exists(RUTA_USUARIOS):
        with open(RUTA_USUARIOS, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    lista = {}
                    for u in data:
                        mac_key = "identificador" if "identificador" in u else "mac"
                        name_key = "nombre" if "nombre" in u else "usuario"
                        if mac_key in u and name_key in u:
                            lista[u[mac_key]] = u[name_key]
                    return lista
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                return {}
    return {}


def guardar_usuarios(lista):
    """Guarda la lista de usuarios como lista de objetos."""
    with open(RUTA_USUARIOS, "w") as f:
        json.dump(lista, f, indent=4)

# ==============================
# 📌 RUTA PRINCIPAL
# ==============================
@app.route('/')
def index():
    return render_template('dashboard.html', dispositivos=[])

# ==============================
# 📌 ESCANEO DE RED (MÓDULO 01)
# ==============================
@app.route('/escaneo', methods=['POST'])
def escanear_red():
    data = request.get_json()
    ip_range = data.get('ip_range', '192.168.18.0/24')
    timeout = int(data.get('timeout', 30))

    usuarios_dict = leer_usuarios_dict()
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
        json.dump(usuarios_dict, tmp, indent=4)
        tmp_path = tmp.name

    dispositivos, _ = ejecutar_escaneo(ip_range, timeout, tmp_path)

    resultado = []
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for d in dispositivos:
        resultado.append({
            "ip": d["ip"],
            "mac": d["mac"],
            "usuario": d.get("usuario", "Desconocido"),
            "fabricante": d.get("fabricante", "Desconocido"),
            "estado": "Confiable" if d.get("usuario") != "Desconocido" else "No confiable",
            "nombre_host": d.get("nombre_host", "Desconocido"),
            "tipo": d.get("tipo", "Desconocido"),
            "ultima_deteccion": ahora
        })

    # 📌 Guardar en CSV dentro de reportes/red
    REPORTE_DIR = "reportes/red"
    os.makedirs(REPORTE_DIR, exist_ok=True)
    nombre_archivo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
    ruta_archivo = os.path.join(REPORTE_DIR, nombre_archivo)

    # Encabezados CSV
    encabezados = ["ip", "mac", "usuario", "fabricante", "estado", "nombre_host", "tipo", "ultima_deteccion"]

    with open(ruta_archivo, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=encabezados)
        escritor.writeheader()
        escritor.writerows(resultado)

    return jsonify({
        "status": "ok",
        "dispositivos": resultado,
        "total": len(resultado),
        "mensaje": f"Escaneo completado y guardado en {nombre_archivo}"
    })
# ==============================
# 📌 LISTA BLANCA (MÓDULO 02)
# ==============================
@app.route("/lista_blanca", methods=["GET"])
def obtener_lista_blanca():
    """Devuelve la lista de dispositivos confiables."""
    usuarios = leer_usuarios_lista()

    # 🔹 Adaptar formato a lo que espera el frontend
    lista_adaptada = [
        {
            "identificador": u.get("mac"),
            "nombre": u.get("usuario"),
            "fecha": u.get("fecha", "Desconocida")
        }
        for u in usuarios
    ]
    return jsonify(lista_adaptada)


@app.route("/lista_blanca", methods=["POST"])
def agregar_lista_blanca():
    """Agrega un nuevo dispositivo confiable."""
    nuevo = request.get_json()
    if not nuevo.get("identificador") or not nuevo.get("nombre"):
        return jsonify({"error": "Datos incompletos"}), 400

    usuarios = leer_usuarios_lista()

    # Evitar duplicados
    if any(u["mac"] == nuevo["identificador"] for u in usuarios):
        return jsonify({"error": "Este dispositivo ya está registrado"}), 400

    usuarios.append({
        "mac": nuevo["identificador"],
        "usuario": nuevo["nombre"],
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    guardar_usuarios(usuarios)
    return jsonify({"mensaje": "Dispositivo agregado correctamente"})


@app.route("/lista_blanca", methods=["DELETE"])
def eliminar_lista_blanca():
    """Elimina un dispositivo de la lista blanca."""
    datos = request.get_json()
    if not datos.get("identificador"):
        return jsonify({"error": "Identificador no proporcionado"}), 400

    usuarios = leer_usuarios_lista()
    usuarios = [u for u in usuarios if u["mac"] != datos["identificador"]]

    guardar_usuarios(usuarios)
    return jsonify({"mensaje": "Dispositivo eliminado correctamente"})




from core.escaner_puertos import escanear_puertos, guardar_resultados_csv
from flask import send_from_directory

# ==============================
# 📌 ESCÁNER DE PUERTOS (MÓDULO 03)
# ==============================
@app.route("/scan_ports", methods=["POST"])
def scan_ports():
    data = request.get_json()
    ip_objetivo = data.get("ip")
    rango_puertos = data.get("puertos", "1-1024")

    if not ip_objetivo:
        return jsonify({"error": "IP objetivo no proporcionada"}), 400

    resultados = escanear_puertos(ip_objetivo, rango_puertos)

    if not resultados:
        return jsonify({
            "status": "ok",
            "resultados": [],
            "mensaje": "No se encontraron puertos abiertos"
        }), 200

    ruta_csv = guardar_resultados_csv(ip_objetivo, resultados)
    nombre_csv = os.path.basename(ruta_csv)

    return jsonify({
        "status": "ok",
        "resultados": resultados,
        "csv_file": nombre_csv,
        "mensaje": "Escaneo completado correctamente"
    })

# ==============================
# 📌 DESCARGA DE CSV
# ==============================
@app.route("/download_csv/<filename>")
def download_csv(filename):
    carpeta = os.path.join(os.getcwd(), "reportes", "puertos")
    return send_from_directory(carpeta, filename, as_attachment=True)


# ==============================
# 📌 MAIN
# ==============================
if __name__ == '__main__':
    app.run(debug=True)

