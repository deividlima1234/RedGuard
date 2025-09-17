#!/bin/bash

echo "🛠️  Iniciando configuración del entorno..."

# 1. Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv .venv
else
    echo "✅ Entorno virtual ya existe"
fi

# 2. Activar entorno virtual
echo "⚙️  Activando entorno virtual..."
source .venv/bin/activate

# 3. Actualizar pip
echo "🔄 Actualizando pip..."
pip install --upgrade pip

# 4. Instalar dependencias
echo "📚 Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt

echo ""
echo "✅ Entorno configurado correctamente."
echo ""
echo "⚠️  IMPORTANTE:"
echo "Para ejecutar funciones de escaneo de red necesitas permisos de administrador (sudo)."
echo ""
echo "Ejecuta así:"
echo "  sudo .venv/bin/python main.py"
echo ""
echo "O, sudo $(which python) app.py - para abrir la interfaz grafica:"
echo "  source .venv/bin/activate"
echo "  python app.py"
echo ""
echo "🚀 ¡Listo para usar RedGuard!"