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
    nombre_archivo = f"resultado-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
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
# auditoria 
# ==============================
from flask import Flask, request, jsonify, render_template
from core.auditoria import ejecutar_auditoria

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("dashboard.html")

@app.route("/auditoria", methods=["POST"])
def api_auditoria():
    data = request.get_json()
    modo = data.get("modo", "completa")
    operaciones = data.get("operaciones", None)

    resultados = ejecutar_auditoria(modo=modo, operaciones=operaciones)
    return jsonify(resultados)
from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
from core.procesador import ejecutar_escaneo
from core.escaner_puertos import escanear_puertos, guardar_resultados_csv
from core.auditoria import ejecutar_auditoria
from core.detector_sospechosos import detectar_sospechosos
from core.generador_reportes import generar_pdf

from datetime import datetime
import json, os, tempfile, csv, glob


# ==============================
# 📌 APP PRINCIPAL
# ==============================
app = Flask(__name__, template_folder="templates", static_folder="static")

RUTA_USUARIOS = "data/usuarios.json"


# ==============================
# 📌 FUNCIONES AUXILIARES
# ==============================
def leer_usuarios_lista():
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
    with open(RUTA_USUARIOS, "w") as f:
        json.dump(lista, f, indent=4)


# ==============================
# 📌 RUTA PRINCIPAL (Dashboard)
# ==============================
@app.route('/')
def index():
    return render_template('dashboard.html', dispositivos=[])


# ==============================
# 📌 ESCANEO DE RED (Módulo 01)
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

    REPORTE_DIR = "reportes/red"
    os.makedirs(REPORTE_DIR, exist_ok=True)
    nombre_archivo = f"resultado-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    ruta_archivo = os.path.join(REPORTE_DIR, nombre_archivo)

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
# 📌 AUDITORÍA (Módulo 05)
# ==============================
@app.route("/auditoria", methods=["POST"])
def api_auditoria():
    data = request.get_json()
    modo = data.get("modo", "completa")
    operaciones = data.get("operaciones", None)

    resultados = ejecutar_auditoria(modo=modo, operaciones=operaciones)

    # Guardar también en disco como en main.py
    import datetime, json, os
    os.makedirs("reportes/auditoria", exist_ok=True)
    archivo_salida = f"reportes/auditoria/reporte_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(archivo_salida, "w") as f:
        json.dump(resultados, f, indent=4)

    print(f"[✅] Auditoría ({modo}) completada. Reporte guardado en {archivo_salida}")

    return jsonify(resultados)

@app.route("/auditoria/reportes", methods=["GET"])
def listar_reportes():
    folder = "reportes/auditoria"
    archivos = sorted(os.listdir(folder), reverse=True) if os.path.exists(folder) else []
    return jsonify(archivos)

@app.route("/auditoria/download/<filename>")
def descargar_reporte(filename):
    folder = os.path.join(os.getcwd(), "reportes", "auditoria")
    return send_from_directory(folder, filename, as_attachment=True)

# ==============================
# 📌 DESCARGAR REPORTES PDF -- AUDITORIA
# ==============================
from flask import send_file, jsonify
import glob, os, json
from core.generador_reportes import generar_pdf_multiple

@app.route("/auditoria/ultimo/pdf")
def descargar_reporte_pdf():
    folder = os.path.join(os.getcwd(), "reportes", "auditoria")
    archivos = sorted(glob.glob(os.path.join(folder, "*.json")), reverse=True)
    if not archivos:
        return jsonify({"error": "No hay reportes disponibles"}), 404

    ultimo_json = archivos[0]

    # Leer datos JSON
    with open(ultimo_json, "r") as f:
        data = json.load(f)

    titulo = "📊 Reporte de Auditoría"
    metadatos = {
        "Fecha": data.get("fecha", "-"),
        "Modo": data.get("modo", "-"),
        "Interfaz": data.get("resultados", {}).get("escaneo_red", {}).get("interfaz", "-"),
        "Rango IP": data.get("resultados", {}).get("escaneo_red", {}).get("rango_ip", "-"),
    }

    # Aquí juntamos todas las tablas que queramos incluir
    tablas = []

    # 🌐 Escaneo de Red
    if "escaneo_red" in data["resultados"]:
        dispositivos = data["resultados"]["escaneo_red"].get("dispositivos", [])
        columnas = ["IP", "MAC", "Host", "Usuario", "Tipo"]
        filas = [
            [d.get("ip","-"), d.get("mac","-"), d.get("nombre_host","-"), d.get("usuario","-"), d.get("tipo","-")]
            for d in dispositivos
        ]
        tablas.append(("🌐 Escaneo de Red", columnas, filas))

    # 🔌 Escaneo de Puertos
    if "escaneo_puertos" in data["resultados"]:
        for host, puertos in data["resultados"]["escaneo_puertos"].items():
            columnas = ["Puerto", "Estado", "Servicio"]
            filas = [
                [p, info.get("estado","-"), info.get("servicio","-")]
                for p, info in puertos.items()
            ]
            tablas.append((f"🔌 Escaneo de Puertos ({host})", columnas, filas))

    # 🚨 Dispositivos Sospechosos
    if "dispositivos_sospechosos" in data["resultados"]:
        sospechosos = data["resultados"]["dispositivos_sospechosos"].get("sospechosos", [])
        columnas = ["IP", "MAC", "Host", "Usuario", "Tipo"]
        filas = [
            [d.get("ip","-"), d.get("mac","-"), d.get("nombre_host","-"), d.get("usuario","-"), d.get("tipo","-")]
            for d in sospechosos
        ]
        tablas.append(("🚨 Dispositivos Sospechosos", columnas, filas))

    # Generar PDF con múltiples tablas
    pdf_path = generar_pdf_multiple(titulo, metadatos, tablas, "reporte_auditoria.pdf")

    return send_file(pdf_path, as_attachment=True, download_name="reporte_auditoria.pdf")



# ==============================
# 📌 LISTA BLANCA (Módulo 02)
# ==============================
@app.route("/lista_blanca", methods=["GET"])
def obtener_lista_blanca():
    usuarios = leer_usuarios_lista()
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
    nuevo = request.get_json()
    if not nuevo.get("identificador") or not nuevo.get("nombre"):
        return jsonify({"error": "Datos incompletos"}), 400

    usuarios = leer_usuarios_lista()
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
    datos = request.get_json()
    if not datos.get("identificador"):
        return jsonify({"error": "Identificador no proporcionado"}), 400

    usuarios = leer_usuarios_lista()
    usuarios = [u for u in usuarios if u["mac"] != datos["identificador"]]

    guardar_usuarios(usuarios)
    return jsonify({"mensaje": "Dispositivo eliminado correctamente"})


# ==============================
# 📌 ESCÁNER DE PUERTOS (Módulo 03)
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

@app.route("/download_csv/<filename>")
def download_csv(filename):
    carpeta = os.path.join(os.getcwd(), "reportes", "puertos")
    return send_from_directory(carpeta, filename, as_attachment=True)


# ==============================
# 📌 INTRUSOS (Módulo 4.1)
# ==============================
@app.route("/api/intrusos", methods=["GET"])
def obtener_intrusos():
    folder = "reportes/sospechosos/json"
    lista_archivos = sorted(glob.glob(os.path.join(folder, "resultado_*.json")), reverse=True)
    if not lista_archivos:
        return jsonify({"error": "No hay reportes disponibles"}), 404

    archivo_mas_reciente = lista_archivos[0]
    with open(archivo_mas_reciente, "r") as f:
        data = json.load(f)

    respuesta = {
        "archivo": os.path.basename(archivo_mas_reciente),
        "fecha_generacion": data.get("fecha_generacion"),
        "rango_ip": data.get("rango_ip_escaneado"),
        "intrusos": data.get("sospechosos", [])
    }
    return jsonify(respuesta)

@app.route("/api/scan_intrusos", methods=["POST"])
def scan_intrusos():
    try:
        ruta_csv, ruta_json = detectar_sospechosos()
        return jsonify({"mensaje": "Escaneo completado", "reporte_json": ruta_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/descargar_intrusos", methods=["GET"])
def descargar_intrusos_pdf():
    folder = "reportes/sospechosos/json"
    lista_archivos = sorted(glob.glob(os.path.join(folder, "resultado_*.json")), reverse=True)
    if not lista_archivos:
        return jsonify({"error": "No hay reportes disponibles"}), 404

    archivo_mas_reciente = lista_archivos[0]
    with open(archivo_mas_reciente, "r") as f:
        data = json.load(f)

    titulo = "📄 Reporte de Dispositivos Sospechosos"
    metadatos = {
        "Fecha del escaneo": data.get("fecha_generacion"),
        "Rango escaneado": data.get("rango_ip_escaneado")
    }
    columnas = ["IP", "MAC", "Host", "Fecha Detectado", "Tipo"]
    filas = [
        [dev.get("ip",""), dev.get("mac",""), dev.get("nombre_host",""),
         data.get("fecha_generacion",""), dev.get("tipo","")]
        for dev in data.get("sospechosos", [])
    ]

    pdf_path = generar_pdf(titulo, metadatos, columnas, filas, "intrusos.pdf")
    return send_file(pdf_path, as_attachment=True, download_name="intrusos.pdf")


# ==============================
# 📌 MAIN
# ==============================
if __name__ == '__main__':
    app.run(debug=True)
