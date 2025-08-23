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

    // ==================== CARGA DE DATOS SEGÚN SECCIÓN ====================
    if (seccionId === 'seccion-lista-blanca') {
        cargarListaBlanca();
    }

    if (seccionId === 'sesccion-dispositivos-sospechosos') {
        cargarIntrusos(); // ✅ Solo cuando entro a intrusos
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


// ==================== LISTAR INTRUSOS ====================
async function cargarIntrusos() {
    try {
        let res = await fetch("/api/intrusos");
        let data = await res.json();

        if (data.error) {
            showAlert("⚠ " + data.error, "warning");
            return;
        }

        let tbody = document.querySelector("#tabla-intrusos tbody");
        tbody.innerHTML = "";

        data.intrusos.forEach(dev => {
            let row = `
                <tr>
                    <td>${dev.ip}</td>
                    <td>${dev.mac}</td>
                    <td>${dev.nombre_host}</td>
                    <td>${data.fecha_generacion}</td>
                    <td>${dev.tipo}</td>
                </tr>`;
            tbody.innerHTML += row;
        });

        // ✅ Solo se muestra cuando entras a la sección intrusos
        showAlert("📊 Intrusos cargados correctamente.", "success", 2000);

    } catch (err) {
        console.error(err);
        showAlert("❌ Error al cargar intrusos.", "error");
    }
}




async function ejecutarEscaneo() {
    const loader = document.getElementById("loader-intrusos");
    try {
        // Mostrar loader
        loader.style.display = "flex";

        let res = await fetch("/api/scan_intrusos", { method: "POST" });
        let data = await res.json();

        if (data.mensaje) {
            showAlert("✅ " + data.mensaje, "success", 4000);
            cargarIntrusos(); // refrescar tabla
        } else {
            showAlert("❌ " + data.error, "error");
        }
    } catch (err) {
        console.error(err);
        showAlert("❌ Error en la conexión con el servidor.", "error");
    } finally {
        // Ocultar loader
        loader.style.display = "none";
    }
}


function descargarReporte() {
    window.location.href = "/api/descargar_intrusos";
    showAlert("⬇ Descargando reporte de intrusos...", "success", 3000);
}


/* =========================
   LÓGICA AUDITORÍA COMPLETA
============================ */

// Cambiar modo entre "completa" y "generar"
function cambiarModo(modo) {
    const red = document.getElementById("red");
    const puertos = document.getElementById("puertos");
    const intrusos = document.getElementById("intrusos");

    if (modo === "completa") {
        // Marcar y bloquear todas las operaciones
        red.checked = true;
        puertos.checked = true;
        intrusos.checked = true;

        red.disabled = true;
        puertos.disabled = true;
        intrusos.disabled = true;

    } else if (modo === "generar") {
        // Habilitar checkboxes para selección manual
        red.disabled = false;
        puertos.disabled = false;
        intrusos.disabled = false;

        // Resetear selección
        red.checked = false;
        puertos.checked = false;
        intrusos.checked = false;
    }
}

// Dependencias: Puertos depende de Red
document.addEventListener("DOMContentLoaded", () => {
    const red = document.getElementById("red");
    const puertos = document.getElementById("puertos");

    // Si se activa Puertos → se activa Red
    puertos.addEventListener("change", function() {
        if (this.checked) {
            red.checked = true;
        }
    });

    // Si se desactiva Red → se desactiva Puertos
    red.addEventListener("change", function() {
        if (!this.checked) {
            puertos.checked = false;
        }
    });
});

// Ejecutar auditoría
function ejecutarSeleccion() {
    const modo = document.querySelector('input[name="modo"]:checked')?.value;
    const red = document.getElementById("red").checked;
    const puertos = document.getElementById("puertos").checked;
    const intrusos = document.getElementById("intrusos").checked;

    if (!modo) {
        showAlert("⚠️ Debes seleccionar un modo (Completa o Generar)", "warning", 4000);
        return;
    }

    // Datos a enviar al backend
    const payload = {
        modo: modo,
        operaciones: {
            escaneo_red: red,
            escaneo_puertos: puertos,
            detectar_intrusos: intrusos
        }
    };

    // Mostrar loader específico de auditoría
    mostrarLoader(true);

    // Enviar petición al backend
    fetch("/auditoria", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        mostrarResultadosAuditoria(data);
        mostrarLoader(false);
        showAlert("✅ Auditoría ejecutada con éxito", "success", 4000);
    })
    .catch(error => {
        console.error("Error en auditoría:", error);
        mostrarLoader(false);
        showAlert("❌ Error al ejecutar auditoría", "error", 4000);
    });
}

// Mostrar resultados en el contenedor
function mostrarResultadosAuditoria(data) {
    const contenedor = document.getElementById("resultado-auditoria");
    let html = `
        <h2>Resultados Auditoría (${data.modo})</h2>
        <p><b>Fecha:</b> ${data.fecha}</p>
    `;

// ==============================
// Escaneo de Red
// ==============================
if (data.resultados.escaneo_red) {
    const red = data.resultados.escaneo_red.dispositivos || [];
    html += `
        <h3>🌐 Escaneo de Red</h3>
        <p><b>Interfaz:</b> ${data.resultados.escaneo_red.interfaz || '-'}<br>
           <b>Rango:</b> ${data.resultados.escaneo_red.rango_ip || '-'}<br>
           <b>Total detectados:</b> ${data.resultados.escaneo_red.total_detectados || 0}</p>

        <table class="tabla-resultado">
            <thead>
                <tr>
                    <th>IP</th>
                    <th>MAC</th>
                    <th>Host</th>
                    <th>Usuario</th>
                    <th>Tipo</th>
                </tr>
            </thead>
            <tbody>
                ${red.map(d => `
                    <tr>
                        <td>${d.ip || '-'}</td>
                        <td>${d.mac || '-'}</td>
                        <td>${d.nombre_host || '-'}</td>
                        <td>${d.usuario || '-'}</td>
                        <td>${d.tipo || '-'}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;
}


    // ==============================
    // Escaneo de Puertos
    // ==============================
    if (data.resultados.escaneo_puertos) {
        html += `
            <h3>🔌 Escaneo de Puertos</h3>
        `;

        for (const [ip, puertos] of Object.entries(data.resultados.escaneo_puertos)) {
            html += `
                <h4>Host: ${ip}</h4>
                <table class="tabla-resultado">
                    <thead>
                        <tr>
                            <th>Puerto</th>
                            <th>Estado</th>
                            <th>Servicio</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${Object.entries(puertos).map(([puerto, info]) => `
                            <tr>
                                <td>${puerto}</td>
                                <td>${info.estado || '-'}</td>
                                <td>${info.servicio || '-'}</td>
                            </tr>
                        `).join("")}
                    </tbody>
                </table>
            `;
        }
    }

// ==============================
// Dispositivos Sospechosos
// ==============================
if (data.resultados.dispositivos_sospechosos) {
    const sospechososData = data.resultados.dispositivos_sospechosos;

    // Extraemos array de sospechosos
    const lista = Array.isArray(sospechososData.sospechosos)
        ? sospechososData.sospechosos
        : [];

    html += `
        <h3>🚨 Dispositivos Sospechosos</h3>
        <p><b>Fecha generación:</b> ${sospechososData.fecha_generacion || '-'}<br>
           <b>Rango IP:</b> ${sospechososData.rango_ip_escaneado || '-'}</p>
    `;

    if (lista.length > 0) {
        html += `
            <table class="tabla-resultado">
                <thead>
                    <tr>
                        <th>IP</th>
                        <th>MAC</th>
                        <th>Host</th>
                        <th>Usuario</th>
                        <th>Tipo</th>
                    </tr>
                </thead>
                <tbody>
                    ${lista.map(d => `
                        <tr>
                            <td>${d.ip || '-'}</td>
                            <td>${d.mac || '-'}</td>
                            <td>${d.nombre_host || '-'}</td>
                            <td>${d.usuario || '-'}</td>
                            <td>${d.tipo || '-'}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    } else {
        html += `<p>✅ No se detectaron dispositivos sospechosos.</p>`;
    }
}


    contenedor.innerHTML = html;
}

// ==============================
// 📥 Gestión de Reportes
// ==============================

// Cargar lista de reportes disponibles
function cargarReportes() {
    fetch("/auditoria/reportes")
        .then(res => res.json())
        .then(archivos => {
            const lista = document.getElementById("lista-reportes");
            if (!archivos.length) {
                lista.innerHTML = "<li>No hay reportes disponibles.</li>";
                return;
            }

            lista.innerHTML = archivos.map(file => `
                <li>
                    <a href="/auditoria/download/${file}" target="_blank">
                        ${file}
                    </a>
                </li>
            `).join("");
        })
        .catch(err => {
            console.error("Error al listar reportes:", err);
            showAlert("❌ No se pudo cargar la lista de reportes", "error", 4000);
        });
}

// Descargar el  reporte de auditoría

function descargarReporteauditoria() {
    window.open("/auditoria/ultimo/pdf", "_blank");
}


/* =========================
   UTILIDADES VISUALES
============================ */

// Mostrar/ocultar loader de auditoría
function mostrarLoader(estado) {
    let loader = document.getElementById("loader-auditoria");
    if (!loader) return;
    loader.style.display = estado ? "flex" : "none";
}
