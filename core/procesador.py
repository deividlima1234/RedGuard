from core.escaneo_red import (
    obtener_interfaz_activa,
    escanear_arp,
    escuchar_trafico,
    combinar_dispositivos,
    obtener_nombres
)
from core.comparador_lista_blanca import comparar_dispositivos

def escanear_red_completa(rango_ip, timeout=30, ruta_usuarios="data/usuarios.json"):
    interfaz = obtener_interfaz_activa()
    print(f"Usando interfaz de red: {interfaz}")

    dispositivos_arp = escanear_arp(rango_ip, interfaz)
    dispositivos_trafico = escuchar_trafico(interfaz, timeout)

    dispositivos = combinar_dispositivos(dispositivos_arp, dispositivos_trafico)
    dispositivos = obtener_nombres(dispositivos)

    dispositivos = comparar_dispositivos(dispositivos, ruta_usuarios)
    return dispositivos

def ejecutar_escaneo(rango_ip, timeout, ruta_usuarios="data/usuarios.json"):
    dispositivos = escanear_red_completa(rango_ip, timeout, ruta_usuarios)
    return dispositivos, {}
