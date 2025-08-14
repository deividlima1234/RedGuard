import json
import os

def cargar_lista_blanca(ruta):
    """Carga usuarios.json y devuelve un diccionario {MAC: nombre} tolerante a distintos formatos."""
    if os.path.exists(ruta):
        with open(ruta, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    lista = {}
                    for u in data:
                        # Detectar la clave correcta para la MAC
                        mac_key = "identificador" if "identificador" in u else "mac"
                        # Detectar la clave correcta para el nombre
                        name_key = "nombre" if "nombre" in u else "usuario"

                        if mac_key in u and name_key in u:
                            lista[u[mac_key]] = u[name_key]
                    return lista
                elif isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                print(f"[X] Error al leer el archivo {ruta} (JSON inválido)")
                return {}
    else:
        print(f"[X] Archivo {ruta} no encontrado.")
    return {}

def comparar_dispositivos(dispositivos, ruta_lista_blanca):
    """
    Compara dispositivos con la lista blanca y asigna el usuario correspondiente.
    """
    lista_blanca = cargar_lista_blanca(ruta_lista_blanca)

    for d in dispositivos:
        mac = d.get("mac")
        d["usuario"] = lista_blanca.get(mac, "Desconocido")
        d["nombre_host"] = d.get("nombre_host", "Desconocido")
        d["tipo"] = d.get("tipo", "Desconocido")
    return dispositivos
