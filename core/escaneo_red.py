
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
"""
Módulo encargado de escanear todos los dispositivos
conectados a la red local mediante ARP y tráfico.
Devuelve una lista de IPs y MACs detectados.
Utiliza scapy.
"""
from scapy.all import ARP, Ether, srp, sniff
import socket
import subprocess
import time


# -------------------------------
# FUNCIÓN PARA DETECTAR INTERFAZ
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

# -------------------------------
# FUNCIONES DE ESCANEO Y GESTIÓN
# -------------------------------

def cargar_usuarios(ruta):
    try:
        with open(ruta, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Archivo usuarios.json no encontrado.")
        return {}

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


