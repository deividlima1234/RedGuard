from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__, template_folder='../templates', static_folder='../static')

# Simulación de datos (luego se conectará con escaneo real)
dispositivos_detectados = [
    {
        'ip': '192.168.1.1',
        'mac': 'AA:BB:CC:DD:EE:FF',
        'fabricante': 'TP-Link',
        'estado': 'Confiable',
        'ultima_deteccion': 'Hace 2 min'
    },
    {
        'ip': '192.168.1.157',
        'mac': '00:1B:44:11:3A:B7',
        'fabricante': 'Desconocido',
        'estado': 'Sospechoso',
        'ultima_deteccion': 'Hace 5 min'
    }
]


@app.route('/')
def index():
    return render_template('dashboard.html', dispositivos=dispositivos_detectados)


@app.route('/escaneo', methods=['POST'])
def escanear_red():
    data = request.get_json()
    ip_range = data.get('ip_range')
    timeout = data.get('timeout')
    protocolo = data.get('protocolo')

    print(f"Iniciando escaneo con: IP={ip_range}, Timeout={timeout}, Protocolo={protocolo}")

    # Aquí se llamará a `escaneo_red.py` en el futuro

    return jsonify({"status": "ok", "mensaje": "Escaneo iniciado"})


if __name__ == '__main__':
    app.run(debug=True)
