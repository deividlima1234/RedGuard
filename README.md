# RedGuard: Herramienta de Monitoreo y Seguridad de Red

<p align="center">
  <img src="static/img/RedGuar-logo-01.png" alt="RedGuard Logo" width="200"/>
</p>

**RedGuard** es una herramienta integral de seguridad de red desarrollada en Python, diseñada para ofrecer una visión completa y detallada de los dispositivos y la actividad en su red local. Con una interfaz web intuitiva construida con Flask y un potente conjunto de herramientas de línea de comandos, RedGuard facilita la identificación de dispositivos, el escaneo de puertos, la detección de intrusos y la realización de auditorías de seguridad.

## Características Principales

- **Escaneo de Red:** Descubre todos los dispositivos conectados a su red utilizando técnicas de escaneo ARP y análisis de tráfico.
- **Escáner de Puertos:** Identifica puertos abiertos y los servicios que se ejecutan en ellos para cualquier dispositivo en la red, utilizando Nmap.
- **Detección de Intrusos:** Detecta y alerta sobre dispositivos "sospechosos" que no están en una lista blanca predefinida.
- **Auditoría de Seguridad:** Realiza una auditoría de seguridad completa o personalizada, combinando las funcionalidades anteriores para generar un informe de estado de la red.
- **Gestión de Lista Blanca:** Administre fácilmente una lista de dispositivos "confiables" para minimizar las falsas alarmas.
- **Generación de Informes:** Crea informes detallados en formatos CSV, JSON y PDF para un fácil análisis y archivo.
- **Sistema de Alertas:** Envía notificaciones por correo electrónico con los informes generados para mantenerlo informado.
- **Interfaz Web:** Un panel de control fácil de usar para visualizar los resultados del escaneo, gestionar la lista blanca y ejecutar auditorías.

## Tecnologías Utilizadas

- **Backend:** Python
- **Framework Web:** Flask
- **Análisis de Red:** Scapy, Nmap
- **Generación de PDF:** ReportLab
- **Dependencias:** Consulte `requirements.txt` para obtener una lista completa.

## Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/RedGuard.git
    cd RedGuard
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Instalar Nmap:**
    Asegúrese de tener Nmap instalado en su sistema. Puede instalarlo usando el administrador de paquetes de su distribución:
    ```bash
    # En Debian/Ubuntu
    sudo apt-get install nmap

    # En Fedora
    sudo dnf install nmap
    ```

## Uso

RedGuard se puede utilizar de dos maneras: a través de su interfaz web o mediante la línea de comandos.

### Interfaz Web

Para iniciar la aplicación web, ejecute:

```bash
python3 app.py
```

Luego, abra su navegador y vaya a `http://127.0.0.1:5000` para acceder al panel de control de RedGuard.

### Línea de Comandos

Para utilizar la versión de línea de comandos, ejecute `main.py`:

```bash
python3 main.py
```

Esto le presentará un menú con las siguientes opciones:

1.  **Ejecutar escaneo de red:** Descubre dispositivos en la red.
2.  **Ejecutar escaneo de puertos:** Escanea los puertos de una IP específica.
3.  **Ejecutar detector de dispositivos sospechosos:** Busca dispositivos que no estén en la lista blanca.
4.  **Ejecutar auditoría:** Realiza una auditoría de seguridad completa o personalizada.
5.  **Salir:** Cierra la aplicación.

## Estructura del Proyecto

```
/
├── app.py                  # Aplicación web Flask
├── main.py                 # Interfaz de línea de comandos
├── requirements.txt        # Dependencias de Python
├── setup.sh                # Script de configuración (si aplica)
├── config/                 # Archivos de configuración
├── core/                   # Lógica principal de la aplicación
│   ├── escaneo_red.py
│   ├── escaner_puertos.py
│   ├── detector_sospechosos.py
│   └── auditoria.py
├── data/                   # Datos (ej. lista blanca de usuarios)
├── reportes/               # Informes generados
├── static/                 # Archivos estáticos para la web (CSS, JS, imágenes)
├── templates/              # Plantillas HTML de Flask
├── tests/                  # Pruebas unitarias
└── utils/                  # Funciones de utilidad
```
