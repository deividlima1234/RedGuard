// ==================== DASHBOARD ====================


    // ==================== MANEJO DE SECCIONES ====================
function mostrarSeccion(seccionId) {
    // Ocultar todas las secciones
    document.querySelectorAll('.main-content').forEach(sec => {
        sec.style.display = 'none';
    });

    // Quitar clase 'active' del menú
    document.querySelectorAll('.sidebar ul li a').forEach(link => {
        link.classList.remove('active');
    });

    // Mostrar la sección seleccionada
    const seccionActiva = document.getElementById(seccionId);
    if (seccionActiva) {
        seccionActiva.style.display = 'block';
    }

    // Activar enlace correspondiente
    const enlaceActivo = document.querySelector(`.sidebar ul li a[onclick="mostrarSeccion('${seccionId}')"]`);
    if (enlaceActivo) {
        enlaceActivo.classList.add('active');
    }

    // Cargar datos adicionales si aplica
    if (seccionId === 'seccion-lista-blanca') {
        cargarListaBlanca();
    }
}

    // ==================== funciones globales para mostrar alert ====================
function showAlert(message, type = "success", duration = 3000) {
    const container = document.getElementById("alert-container");
    if (!container) return;

    const alertDiv = document.createElement("div");
    alertDiv.classList.add("alert-msg");

    // Clase según tipo
    if (type === "success") alertDiv.classList.add("alert-success");
    if (type === "warning") alertDiv.classList.add("alert-warning");
    if (type === "error") alertDiv.classList.add("alert-error");

    alertDiv.textContent = message;

    container.appendChild(alertDiv);

    // Eliminar después de X segundos
    setTimeout(() => {
        alertDiv.style.animation = "fadeOut 0.3s ease forwards";
        setTimeout(() => {
            alertDiv.remove();
        }, 300);
    }, duration);
}

    // ==================== funciones para el modal de confirmacion ====================
let modalCallback = null; // Acción a ejecutar cuando el usuario confirma

function mostrarModalConfirmacion({ titulo, mensaje, textoBoton = "Confirmar", onConfirm }) {
    // Guardar callback para confirmación
    modalCallback = onConfirm;

    // Asignar textos
    document.getElementById("modal-titulo").innerText = titulo;
    document.getElementById("modal-mensaje").innerText = mensaje;
    document.getElementById("modal-confirmar").innerText = textoBoton;

    // Mostrar modal
    document.getElementById("modal-confirmacion").style.display = "flex";
}

// Cerrar modal
function cerrarModal() {
    document.getElementById("modal-confirmacion").style.display = "none";
    modalCallback = null;
}

// Eventos
document.getElementById("modal-cancelar").addEventListener("click", cerrarModal);

document.getElementById("modal-confirmar").addEventListener("click", () => {
    if (typeof modalCallback === "function") {
        modalCallback();
    }
    cerrarModal();
});


// ==================== ESCANEO DE RED ====================
function iniciarEscaneo() {
    const ip_range = document.getElementById('ip_range').value.trim();
    const timeout = document.getElementById('timeout').value.trim();
    const protocolo = document.getElementById('protocolo').value.trim();
    const loader = document.getElementById('loader');

    // ===== VALIDACIÓN =====
    if (!ip_range || !timeout || !protocolo) {
        showAlert("Por favor, complete todos los campos.", "warning");
        return; // Detener ejecución
    }

    loader.style.display = "flex"; // Mostrar loader

    fetch('/escaneo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip_range, timeout, protocolo })
    })
    .then(res => {
        if (!res.ok) {
            showAlert("Error al iniciar el escaneo en el servidor", "error");
            throw new Error(`HTTP ${res.status}`);
        }
        return res.json();
    })
    .then(data => {
        loader.style.display = "none"; // Ocultar loader
        const tbody = document.querySelector("#seccion-detector tbody");
        tbody.innerHTML = "";

        if (!data.dispositivos || data.dispositivos.length === 0) {
            showAlert("No se encontraron dispositivos en el rango especificado.", "info");
            return;
        }

        data.dispositivos.forEach(dispositivo => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${dispositivo.ip}</td>
                <td>${dispositivo.mac}</td>
                <td>${dispositivo.usuario}</td>
                <td>${dispositivo.nombre_host}</td>
                <td>${dispositivo.tipo}</td>
                <td>${dispositivo.fabricante}</td>
                <td>
                    ${dispositivo.estado === 'Confiable'
                        ? '<span class="estado-verde">Confiable</span>'
                        : '<span class="estado-rojo">No confiable</span>'}
                </td>
                <td>${dispositivo.ultima_deteccion}</td>
                <td>
                    <button>ℹ️</button>
                    <button>🚫</button>
                </td>
            `;
            tbody.appendChild(row);
        });

        showAlert("Escaneo finalizado correctamente", "success");
    })
    .catch(err => {
        loader.style.display = "none";
        console.error(err);
        showAlert("Ocurrió un error al iniciar el escaneo", "error");
    });
}


// ==================== ESCANEO DE PUERTOS ====================
document.getElementById("btn-iniciar-escaneo").addEventListener("click", function () {
    const ip = document.getElementById("ip_objetivo").value.trim();
    const puertos = document.getElementById("rango_puertos").value.trim();
    const loader = document.getElementById("loader-escaner-puertos");
    const tbody = document.querySelector("#tabla-puertos tbody");

    if (!ip || !puertos) {
        showAlert("Por favor, complete todos los campos", "warning");
        return;
    }

    loader.style.display = "flex"; // Mostrar loader
    tbody.innerHTML = ""; // Limpiar resultados anteriores

    fetch("/scan_ports", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ip: ip, puertos: puertos })
    })
    .then(response => response.json())
    .then(data => {
        loader.style.display = "none"; // Ocultar loader

        if (data.error) {
            showAlert(data.error, "error");
            return;
        }

        // Mostrar IP escaneada
        document.getElementById("ip-escaneada").textContent = `IP escaneada: ${data.ip || ip}`;

        // Si no hay puertos abiertos
        if (data.resultados.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="3" style="color: green; font-weight: bold; text-align: center;">
                        ✅ No se detectaron puertos abiertos — Seguridad Alta
                    </td>
                </tr>
            `;
        } else {
            // Llenar tabla con resultados
            data.resultados.forEach(r => {
                let estadoClass = "";
                if (r.estado === "open") estadoClass = "estado-verde";
                else if (r.estado === "closed") estadoClass = "estado-rojo";
                else estadoClass = "estado-amarillo";

                const fila = document.createElement("tr");
                fila.innerHTML = `
                    <td>${r.puerto}</td>
                    <td><span class="${estadoClass}">${r.estado}</span></td>
                    <td>${r.servicio}</td>
                `;
                tbody.appendChild(fila);
            });
        }

        // Botón de descarga CSV
        if (data.csv_file) {
            const link = document.getElementById("descargar-csv");
            link.href = `/download_csv/${data.csv_file}`;
            link.style.display = "inline-block";
        } else {
            document.getElementById("descargar-csv").style.display = "none";
        }
    })
    .catch(err => {
        loader.style.display = "none";
        showAlert("Error en el escaneo: " + err, "error");
    });
});


// ==================== LISTA BLANCA ====================
function cargarListaBlanca() {
    fetch('/lista_blanca')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById("lista-blanca-body");
            tbody.innerHTML = "";
            data.forEach(item => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${item.identificador}</td>
                    <td>${item.nombre}</td>
                    <td>${item.fecha}</td>
                    <td>
                        <button onclick="eliminarListaBlanca('${item.identificador}')">🗑️</button>
                    </td>
                `;
                tbody.appendChild(row);
            });
        });
}

    function agregarListaBlanca() {
        const identificador = document.getElementById('ip_mac').value.trim();
        const nombre = document.getElementById('nombre_usuario').value.trim();

        if (!identificador || !nombre) {
            showAlert("Por favor, complete todos los campos", "warning");
            return;
        }

        fetch('/lista_blanca', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ identificador, nombre })
        })
        .then(res => {
            if (!res.ok) {
                showAlert("Error al agregar a la lista blanca", "error");
                throw new Error(`HTTP ${res.status}`);
            }
            return res.json();
        })
        .then(() => {
            cargarListaBlanca();
            showAlert("Usuario agregado a la lista blanca", "success");
        })
        .catch(err => console.error(err));
    }

        function eliminarListaBlanca(ip) {
            mostrarModalConfirmacion({
                titulo: "Confirmar eliminación",
                mensaje: `¿Seguro que deseas eliminar ${ip} de la lista blanca?`,
                textoBoton: "Eliminar",
                onConfirm: () => {
                    fetch('/lista_blanca', {
                        method: 'DELETE',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ identificador: ip })
                    })
                    .then(res => {
                        if (!res.ok) throw new Error("Error al eliminar");
                        showAlert("El dispositivo fue eliminado de la lista blanca", "success");
                        cargarListaBlanca();
                    })
                    .catch(err => {
                        console.error(err);
                        showAlert("No se pudo eliminar de la lista blanca", "error");
                    });
                }
            });
        }
