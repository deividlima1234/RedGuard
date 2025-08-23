# utils/usuarios.py
import json

def cargar_usuarios(ruta='data/usuarios.json'):
    try:
        with open(ruta, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Archivo usuarios.json no encontrado.")
        return {}
    except json.JSONDecodeError:
        print("Error al leer el archivo usuarios.json (¿JSON inválido?)")
        return {}
