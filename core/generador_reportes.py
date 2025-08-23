# -- core/generador_reportes.py --
import os, tempfile
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def generar_pdf(titulo, metadatos, columnas, filas, nombre_archivo="reporte.pdf"):
    """
    Genera un PDF con logo, título, metadatos y una tabla de datos.
    Retorna la ruta del archivo PDF generado.
    (Versión original, usada por otros módulos)
    """
    pdf_path = os.path.join(tempfile.gettempdir(), nombre_archivo)
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # ---------------- ENCABEZADO CON LOGO ----------------
    logo_path = os.path.join("static", "img", "RedGuar-logo-01.png")
    if os.path.exists(logo_path):
        img = Image(logo_path, width=150, height=150)
        elements.append(img)

    elements.append(Paragraph(titulo, styles["Title"]))
    elements.append(Spacer(1, 12))

    # ---------------- METADATOS ----------------
    for key, value in metadatos.items():
        elements.append(Paragraph(f"<b>{key}:</b> {value}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # ---------------- TABLA ----------------
    table_data = [columnas] + filas
    table = Table(table_data, colWidths=[100]*len(columnas))
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#00ff88")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 10),
        ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#18191b")),
        ("TEXTCOLOR", (0,1), (-1,-1), colors.white),
        ("GRID", (0,0), (-1,-1), 0.5, colors.gray),
    ]))
    elements.append(table)

    doc.build(elements)
    return pdf_path


def generar_pdf_multiple(titulo, metadatos, tablas, nombre_archivo="reporte.pdf"):
    """
    Genera un PDF con logo, título, metadatos y múltiples tablas.
    `tablas` debe ser una lista de tuplas: (titulo_tabla, columnas, filas)
    """
    pdf_path = os.path.join(tempfile.gettempdir(), nombre_archivo)
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # ---------------- ENCABEZADO CON LOGO ----------------
    logo_path = os.path.join("static", "img", "RedGuar-logo-01.png")
    if os.path.exists(logo_path):
        img = Image(logo_path, width=150, height=150)
        elements.append(img)

    elements.append(Paragraph(titulo, styles["Title"]))
    elements.append(Spacer(1, 12))

    # ---------------- METADATOS ----------------
    for key, value in metadatos.items():
        elements.append(Paragraph(f"<b>{key}:</b> {value}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # ---------------- TABLAS ----------------
    for titulo_tabla, columnas, filas in tablas:
        elements.append(Paragraph(titulo_tabla, styles["Heading2"]))
        table_data = [columnas] + filas if filas else [columnas, ["-"]*len(columnas)]
        table = Table(table_data, colWidths=[100]*len(columnas))
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#00ff88")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.black),
            ("ALIGN", (0,0), (-1,-1), "CENTER"),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0,0), (-1,0), 10),
            ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#18191b")),
            ("TEXTCOLOR", (0,1), (-1,-1), colors.white),
            ("GRID", (0,0), (-1,-1), 0.5, colors.gray),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

    doc.build(elements)
    return pdf_path
