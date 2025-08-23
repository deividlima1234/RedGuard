#--utils/utils.py
import netifaces as ni
import ipaddress

def obtener_rango_red(interfaz="wlan0"):
    """
    Detecta automáticamente la subred de la interfaz dada.
    Ejemplo: "192.168.18.0/24"
    """
    try:
        ip_info = ni.ifaddresses(interfaz)[ni.AF_INET][0]
        ip = ip_info['addr']
        mascara = ip_info['netmask']
        red = ipaddress.IPv4Network(f"{ip}/{mascara}", strict=False)
        return str(red)
    except Exception as e:
        print(f"[⚠] No se pudo obtener la red para {interfaz}: {e}")
        return None
