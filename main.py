# main.py
from config.settings import TIEMPO_ESCUCHA, REMITENTE, DESTINATARIO
from core.procesador import escanear_red_completa
from core.escaner_puertos import escanear_puertos, guardar_resultados_csv
from utils.archivo import guardar_csv
from utils.usuarios import cargar_usuarios
from core.sistema_alertas import enviar_correo
import sys

#----------------
# Función para escanear de red
#----------------
def escaneo_red():
    rango_ip = input("Ingrese el rango de IP a escanear (ejemplo: 192.168.1.0): ").strip()

    if not rango_ip:
        print("[X] No se ingresó un rango de IP. Saliendo...")
        return

    print(f"[*] Iniciando escaneo completo de red en {rango_ip}...")

    dispositivos = escanear_red_completa(rango_ip, TIEMPO_ESCUCHA)

    print(f"\n{'IP':<16} {'MAC':<18} {'Usuario':<20} {'Nombre Host':<20} {'Método'}")
    print("-" * 90)
    for d in dispositivos:
        print(f"{d['ip']:<16} {d['mac']:<18} {d['usuario']:<20} {d.get('nombre_host', 'Desconocido'):<20} {d.get('tipo', 'Desconocido')}")

    usuarios = cargar_usuarios()

    if isinstance(usuarios, list):
        usuarios = {u['mac']: u['usuario'] for u in usuarios}

    archivo = guardar_csv(dispositivos, usuarios)

    asunto = f"🔐 RedGuard - Informe de escaneo completo de red para {rango_ip}"
    mensaje = (
        f"Hola,\n\n"
        f"Adjunto el informe detallado del escaneo de red realizado para el rango {rango_ip}.\n\n"
        f"Saludos,\nRedGuard"
    )

    enviar_correo(REMITENTE, DESTINATARIO, archivo, asunto=asunto, mensaje=mensaje)

    print("[✓] Escaneo y notificación finalizados.")
#----------------
# Función para imprimir resultados de Nmap
#----------------
def imprimir_resultados_nmap(resultados):
    abiertos = [r for r in resultados if r['estado'] == 'open']
    otros = [r for r in resultados if r['estado'] != 'open']

    print("\n=== Puertos Abiertos ===")
    if abiertos:
        print(f"{'Puerto':<8} {'Estado':<10} Servicio")
        print("-" * 40)
        for r in abiertos:
            print(f"{r['puerto']}/tcp  {r['estado']:<10} {r['servicio']}")
    else:
        print("No se encontraron puertos abiertos.")

    print("\n=== Puertos Cerrados o Filtrados ===")
    if otros:
        print(f"{'Puerto':<8} {'Estado':<10} Servicio")
        print("-" * 40)
        for r in otros:
            print(f"{r['puerto']}/tcp  {r['estado']:<10} {r['servicio']}")
    else:
        print("No hay puertos cerrados o filtrados reportados.")

#----------------
# Función para escanear puertos
#----------------
def escaneo_puertos():
    ip = input("Ingrese la IP a escanear: ").strip()
    if not ip:
        print("[X] No se ingresó una IP. Cancelando...")
        return

    rango_puertos = input("Ingrese el rango de puertos (ej. 1-1024, default=1-1024): ").strip() or "1-1024"

    print(f"[*] Escaneando puertos en {ip} ({rango_puertos})...")
    resultados = escanear_puertos(ip, rango_puertos)

    if resultados:
        imprimir_resultados_nmap(resultados)

        archivo = guardar_resultados_csv(ip, resultados)
        print(f"\n[✓] Resultados guardados en {archivo}")

        asunto = f"🔐 RedGuard - Informe de escaneo de puertos para {ip}"
        mensaje = (
            f"Hola,\n\n"
            f"Adjunto el informe detallado del escaneo de puertos realizado para la IP {ip}.\n\n"
            f"Saludos,\nRedGuard"
        )

        enviar_correo(REMITENTE, DESTINATARIO, archivo, asunto=asunto, mensaje=mensaje)
        print("[✓] Resultado enviado por correo.")
    else:
        print(f"[-] No se detectaron puertos en {ip}")
#----------------
# Menú principal
#----------------   

def menu():
    print("=== Bienvenido a RedGuard ===")
    while True:
        try:
            print("\n=== RedGuard - Menú Principal ===")
            print("1. Ejecutar escaneo de red")
            print("2. Ejecutar escaneo de puertos")
            print("3. Salir")

            opcion = input("Seleccione una opción: ")

            if opcion == "1":
                escaneo_red()
            elif opcion == "2":
                escaneo_puertos()
            elif opcion == "3":
                print("Saliendo...")
                sys.exit()
            else:
                print("Opción inválida, intente de nuevo.")
        except KeyboardInterrupt:
            print("\nSaliendo por interrupción del usuario.")
            sys.exit()


if __name__ == "__main__":
    menu()

