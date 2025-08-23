"""
Módulo encargado de escanear todos los dispositivos
conectados a la red local mediante ARP y tráfico.
Devuelve una lista de IPs y MACs detectados.
Utiliza scapy.
"""

import json
import socket
import subprocess
import netifaces
from scapy.all import ARP, Ether, srp, sniff


# -------------------------------
# FUNCIONES DE UTILIDAD
# -------------------------------
def combinar_dispositivos(lista1, lista2):
    """Combina listas de dispositivos evitando duplicados"""
    combinados = []
    macs_vistas = set()

    for lista in [lista1, lista2]:
        for d in lista:
            if d['mac'] not in macs_vistas:
                macs_vistas.add(d['mac'])
                combinados.append(d)

    return combinados


def obtener_nombres(dispositivos):
    """Intenta obtener nombres de host para las IPs encontradas"""
    print("Intentando obtener nombres de host...")
    for d in dispositivos:
        if d['ip']:
            try:
                nombre = socket.gethostbyaddr(d['ip'])[0]
                d['nombre_host'] = nombre
            except (socket.herror, socket.gaierror):
                d['nombre_host'] = "Desconocido"
    return dispositivos


def cargar_usuarios(ruta):
    """Carga usuarios.json si existe"""
    try:
        with open(ruta, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Archivo usuarios.json no encontrado.")
        return {}


# -------------------------------
# FUNCIONES DE ESCANEO
# -------------------------------
def obtener_interfaz_activa():
    """Obtiene la interfaz de red activa sin usar netifaces"""
    try:
        result = subprocess.run(['ip', 'route', 'show', 'default'],
                                capture_output=True, text=True)
        if result.returncode == 0:
            partes = result.stdout.split()
            if "dev" in partes:
                idx = partes.index("dev")
                interfaz = partes[idx + 1]
                return interfaz
    except Exception as e:
        print(f"Error al detectar la interfaz: {e}")
    return "lo"


def obtener_rango_subred(interfaz):
    """Obtiene el rango de IP de la subred local basado en la interfaz"""
    try:
        # Obtener información de la interfaz usando netifaces
        interfaces = netifaces.interfaces()
        if interfaz not in interfaces:
            print(f"Interfaz {interfaz} no encontrada.")
            return None

        # Obtener dirección IP y máscara de subred
        addrs = netifaces.ifaddresses(interfaz)
        if netifaces.AF_INET not in addrs:
            print(f"No se encontró configuración IPv4 para {interfaz}.")
            return None

        ip_info = addrs[netifaces.AF_INET][0]
        ip = ip_info['addr']
        mascara = ip_info['netmask']

        # Calcular el rango de la subred
        import ipaddress
        red = ipaddress.ip_network(f"{ip}/{mascara}", strict=False)
        return str(red)
    except Exception as e:
        print(f"Error al obtener rango de subred: {e}")
        return None


def escanear_arp(rango_ip, interfaz):
    """Escaneo ARP tradicional"""
    print(f"Escaneando la red {rango_ip} en la interfaz {interfaz}...")
    try:
        paquete = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=rango_ip)
        resultado = srp(paquete, timeout=3, iface=interfaz, verbose=0)[0]
        dispositivos = []
        for _, recibido in resultado:
            dispositivos.append({
                "ip": recibido.psrc,
                "mac": recibido.hwsrc.lower(),
                "tipo": "ARP"
            })
        return dispositivos
    except Exception as e:
        print(f"Error en escanear_arp: {e}")
        return []


def escuchar_trafico(interfaz, tiempo):
    """Escucha tráfico para detectar dispositivos que no responden a ARP"""
    print(f"Escuchando tráfico en {interfaz} por {tiempo} segundos...")
    dispositivos = []
    try:
        def procesar_paquete(pkt):
            if pkt.haslayer(Ether):
                mac = pkt[Ether].src.lower()
                if pkt.haslayer('IP'):
                    ip = pkt['IP'].src
                    if not any(d['mac'] == mac for d in dispositivos):
                        dispositivos.append({
                            "ip": ip,
                            "mac": mac,
                            "tipo": "Trafico"
                        })
        sniff(iface=interfaz, prn=procesar_paquete, timeout=tiempo, store=0)
        return dispositivos
    except Exception as e:
        print(f"Error en escuchar_trafico: {e}")
        return []


from core.comparador_lista_blanca import comparar_dispositivos

# =========================================
# WRAPPER PRINCIPAL
# =========================================
def ejecutar(interfaz=None):
    """
    Ejecuta el escaneo de red completo:
    - Determina la interfaz activa si no se proporciona
    - Calcula el rango de la subred local
    - Escaneo ARP
    - Escucha de tráfico
    - Combinación de resultados
    - Resolución de nombres de host
    - Verificación contra usuarios registrados
    """
    # Determinar la interfaz si no se proporciona
    if not interfaz:
        interfaz = obtener_interfaz_activa()
    
    # Obtener el rango de la subred local
    rango_ip = obtener_rango_subred(interfaz)
    if not rango_ip:
        print("No se pudo determinar el rango de la subred. Abortando escaneo.")
        return {
            "interfaz": interfaz,
            "rango_ip": None,
            "total_detectados": 0,
            "dispositivos": []
        }

    print(f"[🔎] Ejecutando escaneo de red en {rango_ip} ({interfaz})...")

    # Escaneo ARP
    dispositivos_arp = escanear_arp(rango_ip, interfaz)

    # Escucha de tráfico
    dispositivos_trafico = escuchar_trafico(interfaz, tiempo=10)

    # Combinar resultados
    dispositivos = combinar_dispositivos(dispositivos_arp, dispositivos_trafico)

    # Resolver nombres de host
    dispositivos = obtener_nombres(dispositivos)

    # 🔹 Comparar con lista blanca (usuarios.json)
    ruta_lista_blanca = "data/usuarios.json"
    dispositivos = comparar_dispositivos(dispositivos, ruta_lista_blanca)

    return {
        "interfaz": interfaz,
        "rango_ip": rango_ip,
        "total_detectados": len(dispositivos),
        "dispositivos": dispositivos
    }