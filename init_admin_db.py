import sqlite3
import bcrypt
import os

# Ruta de la base de datos
DB_PATH = os.path.join("data", "admin_users.db")

def init_db():
    # Crear carpeta data si no existe
    os.makedirs("data", exist_ok=True)

    # Conectar a SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tabla administradores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS administradores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            nombre_completo TEXT,
            ultimo_acceso TEXT
        )
    """)

    # Usuario inicial
    usuario = "admin"
    password = "admin123"  # cámbialo después
    nombre_completo = "Administrador Principal"

    # Hashear la contraseña
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute("""
            INSERT INTO administradores (usuario, password_hash, nombre_completo)
            VALUES (?, ?, ?)
        """, (usuario, password_hash.decode('utf-8'), nombre_completo))
        print(f"[OK] Usuario '{usuario}' creado con éxito.")
    except sqlite3.IntegrityError:
        print(f"[INFO] El usuario '{usuario}' ya existe.")

    # Guardar cambios y cerrar
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
