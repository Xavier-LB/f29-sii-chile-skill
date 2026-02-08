"""
generar_f29.py — Genera un archivo Excel con el Formulario 29 completo.
Versión 2.0 — Con detalle de documentos por línea.

Uso:
    from scripts.generar_f29 import generar_f29_excel
    generar_f29_excel(datos, output_path)

    donde `datos` es un dict con la estructura definida abajo.
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from datetime import datetime

# ============================================================
# Colores y estilos
# ============================================================
AZUL_SII = "1F3864"
AZUL_CLARO = "D6E4F0"
AMARILLO_INPUT = "FFF2CC"
VERDE_CALCULO = "E2EFDA"
GRIS_HEADER = "D9D9D9"
ROJO_ALERTA = "FCE4EC"
BLANCO = "FFFFFF"
VERDE_CLARO = "E8F5E9"
NARANJA_CLARO = "FFF3E0"

FONT_HEADER = Font(name="Arial", size=12, bold=True, color=BLANCO)
FONT_SECTION = Font(name="Arial", size=10, bold=True, color=AZUL_SII)
FONT_NORMAL = Font(name="Arial", size=9, color="333333")
FONT_CODE = Font(name="Arial", size=9, bold=True, color=AZUL_SII)
FONT_TOTAL = Font(name="Arial", size=10, bold=True, color="CC0000")
FONT_SMALL = Font(name="Arial", size=8, color="666666")
FONT_DOC = Font(name="Arial", size=8, color="444444")
FONT_DOC_BOLD = Font(name="Arial", size=8, bold=True, color="333333")

FILL_HEADER = PatternFill(start_color=AZUL_SII, end_color=AZUL_SII, fill_type="solid")
FILL_SECTION = PatternFill(start_color=AZUL_CLARO, end_color=AZUL_CLARO, fill_type="solid")
FILL_CALC = PatternFill(start_color=VERDE_CALCULO, end_color=VERDE_CALCULO, fill_type="solid")
FILL_TOTAL = PatternFill(start_color=GRIS_HEADER, end_color=GRIS_HEADER, fill_type="solid")
FILL_ALERTA = PatternFill(start_color=ROJO_ALERTA, end_color=ROJO_ALERTA, fill_type="solid")
FILL_DEBITO_ROW = PatternFill(start_color=NARANJA_CLARO, end_color=NARANJA_CLARO, fill_type="solid")
FILL_CREDITO_ROW = PatternFill(start_color=VERDE_CLARO, end_color=VERDE_CLARO, fill_type="solid")

BORDER_THIN = Border(
    left=Side(style="thin", color="AAAAAA"),
    right=Side(style="thin", color="AAAAAA"),
    top=Side(style="thin", color="AAAAAA"),
    bottom=Side(style="thin", color="AAAAAA"),
)

ALIGN_CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
ALIGN_RIGHT = Alignment(horizontal="right", vertical="center")
ALIGN_LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


def formato_peso(valor):
    """Formatea un número como peso chileno."""
    if valor is None or valor == 0:
        return "$0"
    if valor < 0:
        return f"-${abs(int(valor)):,}".replace(",", ".")
    return f"${int(valor):,}".replace(",", ".")


# ============================================================
# Estructura de documentos
# ============================================================
"""
Cada línea del F29 puede tener una lista de documentos asociados.
Se pasan en datos["documentos"] organizado por línea:

{
    "linea_7": [   # Facturas afectas del giro
        {
            "tipo": "factura",
            "numero": "F-00101",
            "fecha": "2026-01-05",
            "rut": "76.543.210-K",
            "razon_social": "Cliente SpA",
            "descripcion": "Desarrollo módulo X",
            "neto": 5000000,
            "iva": 950000,
            "exento": 0,
            "total": 5950000,
        },
        ...
    ],
    "linea_13": [ ... ],   # Notas de crédito emitidas
    "linea_1":  [ ... ],   # Facturas de exportación
    "linea_28": [ ... ],   # Facturas recibidas del giro (compras)
    "linea_31": [ ... ],   # Facturas activo fijo
    "linea_5":  [ ... ],   # Facturas de compra (serv. digitales)
    "linea_61": [          # Boletas de honorarios
        {
            "tipo": "boleta_honorarios",
            "numero": "BH-3001",
            "fecha": "2026-01-31",
            "rut": "15.123.456-7",
            "razon_social": "Juan Pérez",
            "descripcion": "Desarrollo frontend",
            "bruto": 2000000,
            "retencion": 305000,
            "liquido": 1695000,
        },
    ],
    "linea_60": [          # Liquidaciones de sueldo (IUSC)
        {
            "tipo": "liquidacion_sueldo",
            "numero": "LIQ-001",
            "fecha": "2026-01-31",
            "rut": "17.111.222-3",
            "razon_social": "Andrea López",
            "cargo": "Tech Lead",
            "bruto": 3500000,
            "iusc": 185000,
            "liquido": 2800000,
        },
    ],
}

Si datos["documentos"] tiene entradas para una línea, los totales se
recalculan desde los documentos. Si no, se usan los totales de
datos["ventas"] / datos["compras"] / datos["retenciones"].
"""

LINEAS_INFO = {
    "linea_1":  {"linea": "1",  "codigo": "585/20",  "nombre": "Facturas de Exportación", "seccion": "debito"},
    "linea_2":  {"linea": "2",  "codigo": "586/142", "nombre": "Ventas/Servicios Exentos del Giro", "seccion": "debito"},
    "linea_5":  {"linea": "5",  "codigo": "515/587", "nombre": "Facturas de Compra (Serv. Digitales Extranjeros)", "seccion": "debito"},
    "linea_7":  {"linea": "7",  "codigo": "503/502", "nombre": "Facturas Afectas del Giro", "seccion": "debito"},
    "linea_9":  {"linea": "9",  "codigo": "716/717", "nombre": "Ventas Activo Fijo (No del Giro)", "seccion": "debito"},
    "linea_10": {"linea": "10", "codigo": "110/111", "nombre": "Boletas", "seccion": "debito"},
    "linea_11": {"linea": "11", "codigo": "758/759", "nombre": "Boletas Electrónicas / POS", "seccion": "debito"},
    "linea_12": {"linea": "12", "codigo": "512/513", "nombre": "Notas de Débito Emitidas", "seccion": "debito"},
    "linea_13": {"linea": "13", "codigo": "509/510", "nombre": "Notas de Crédito Emitidas", "seccion": "debito"},
    "linea_28": {"linea": "28", "codigo": "519/520", "nombre": "Facturas Recibidas del Giro", "seccion": "credito"},
    "linea_29": {"linea": "29", "codigo": "761/762", "nombre": "Facturas Supermercados/Comercios", "seccion": "credito"},
    "linea_31": {"linea": "31", "codigo": "524/525", "nombre": "Facturas Activo Fijo", "seccion": "credito"},
    "linea_32": {"linea": "32", "codigo": "527/528", "nombre": "Notas de Crédito Recibidas", "seccion": "credito"},
    "linea_33": {"linea": "33", "codigo": "531/532", "nombre": "Notas de Débito Recibidas", "seccion": "credito"},
    "linea_34": {"linea": "34", "codigo": "534/535", "nombre": "DIN Importaciones del Giro", "seccion": "credito"},
    "linea_35": {"linea": "35", "codigo": "536/553", "nombre": "DIN Importaciones Activo Fijo", "seccion": "credito"},
    "linea_60": {"linea": "60", "codigo": "48",      "nombre": "Impuesto Único 2da Categoría (Sueldos)", "seccion": "retencion"},
    "linea_61": {"linea": "61", "codigo": "151",     "nombre": "Retención Honorarios Art. 42 N°2", "seccion": "retencion"},
}

COLUMNAS_VENTAS = ["N° Doc", "Fecha", "RUT Cliente", "Razón Social", "Descripción", "Neto", "IVA", "Exento", "Total"]
COLUMNAS_COMPRAS = ["N° Doc", "Fecha", "RUT Proveedor", "Razón Social", "Descripción", "Neto", "IVA", "Total"]
COLUMNAS_HONORARIOS = ["N° Boleta", "Fecha", "RUT Profesional", "Razón Social", "Descripción", "Bruto", "Retención", "Líquido"]
COLUMNAS_SUELDOS = ["N° Liquidación", "Fecha", "RUT Trabajador", "Nombre", "Cargo", "Sueldo Bruto", "IUSC", "Líquido"]


def get_columnas_para_linea(seccion, linea_key):
    if linea_key == "linea_61":
        return COLUMNAS_HONORARIOS
    elif linea_key == "linea_60":
        return COLUMNAS_SUELDOS
    elif seccion == "debito":
        return COLUMNAS_VENTAS
    else:
        return COLUMNAS_COMPRAS


def get_doc_values(doc, seccion, linea_key):
    """Extrae los valores de un documento como lista, según el tipo de columnas."""
    if linea_key == "linea_61":
        return [
            doc.get("numero", ""),
            doc.get("fecha", ""),
            doc.get("rut", ""),
            doc.get("razon_social", ""),
            doc.get("descripcion", ""),
            doc.get("bruto", doc.get("neto", 0)),
            doc.get("retencion", doc.get("iva", 0)),
            doc.get("liquido", doc.get("total", 0)),
        ]
    elif linea_key == "linea_60":
        return [
            doc.get("numero", ""),
            doc.get("fecha", ""),
            doc.get("rut", ""),
            doc.get("razon_social", doc.get("nombre", "")),
            doc.get("cargo", doc.get("descripcion", "")),
            doc.get("bruto", doc.get("neto", 0)),
            doc.get("iusc", doc.get("iva", 0)),
            doc.get("liquido", doc.get("total", 0)),
        ]
    elif seccion == "debito":
        return [
            doc.get("numero", ""),
            doc.get("fecha", ""),
            doc.get("rut", ""),
            doc.get("razon_social", ""),
            doc.get("descripcion", ""),
            doc.get("neto", 0),
            doc.get("iva", 0),
            doc.get("exento", 0),
            doc.get("total", 0),
        ]
    else:
        return [
            doc.get("numero", ""),
            doc.get("fecha", ""),
            doc.get("rut", ""),
            doc.get("razon_social", ""),
            doc.get("descripcion", ""),
            doc.get("neto", 0),
            doc.get("iva", 0),
            doc.get("total", 0),
        ]


# ============================================================
# Cálculo del F29
# ============================================================

def calcular_f29(datos):
    """
    Calcula todos los códigos del F29.
    Si hay documentos individuales en datos["documentos"], los totales se
    recalculan desde ellos. Si no, usa datos["ventas"]/datos["compras"].
    """
    v = datos.get("ventas", {})
    c = datos.get("compras", {})
    ret = datos.get("retenciones", {})
    ppm = datos.get("ppm", {})
    dev = datos.get("devoluciones", {})
    docs = datos.get("documentos", {})

    IVA_TASA = 0.19
    codigos = {}

    def has_docs(lk):
        return lk in docs and len(docs[lk]) > 0

    def count_docs(lk):
        return len(docs.get(lk, []))

    def sum_field(lk, campo):
        return sum(d.get(campo, 0) for d in docs.get(lk, []))

    # === DÉBITOS ===

    if has_docs("linea_1"):
        codigos[585] = count_docs("linea_1")
        codigos[20] = sum_field("linea_1", "neto")
    else:
        codigos[585] = v.get("facturas_exportacion_cant", 0)
        codigos[20] = v.get("facturas_exportacion_neto", 0)

    if has_docs("linea_2"):
        codigos[586] = count_docs("linea_2")
        codigos[142] = sum_field("linea_2", "neto")
    else:
        codigos[586] = v.get("facturas_exentas_giro_cant", 0)
        codigos[142] = v.get("facturas_exentas_giro_neto", 0)

    if has_docs("linea_5"):
        codigos[515] = count_docs("linea_5")
        codigos[587] = sum_field("linea_5", "neto")
    else:
        codigos[515] = c.get("facturas_compra_digital_cant", 0)
        codigos[587] = c.get("facturas_compra_digital_neto", 0)

    if has_docs("linea_7"):
        codigos[503] = count_docs("linea_7")
        iva_sum = sum_field("linea_7", "iva")
        codigos[502] = iva_sum if iva_sum else int(sum_field("linea_7", "neto") * IVA_TASA)
    else:
        codigos[503] = v.get("facturas_afectas_cant", 0)
        codigos[502] = int(v.get("facturas_afectas_neto", 0) * IVA_TASA)

    if has_docs("linea_9"):
        codigos[716] = count_docs("linea_9")
        iva_sum = sum_field("linea_9", "iva")
        codigos[717] = iva_sum if iva_sum else int(sum_field("linea_9", "neto") * IVA_TASA)
    else:
        codigos[716] = v.get("ventas_activo_fijo_cant", 0)
        codigos[717] = int(v.get("ventas_activo_fijo_neto", 0) * IVA_TASA)

    if has_docs("linea_10"):
        codigos[110] = count_docs("linea_10")
        iva_sum = sum_field("linea_10", "iva")
        codigos[111] = iva_sum if iva_sum else int(sum_field("linea_10", "neto") * IVA_TASA)
    else:
        codigos[110] = v.get("boletas_cant", 0)
        codigos[111] = int(v.get("boletas_neto", 0) * IVA_TASA)

    if has_docs("linea_12"):
        codigos[512] = count_docs("linea_12")
        iva_sum = sum_field("linea_12", "iva")
        codigos[513] = iva_sum if iva_sum else int(sum_field("linea_12", "neto") * IVA_TASA)
    else:
        codigos[512] = v.get("notas_debito_cant", 0)
        codigos[513] = int(v.get("notas_debito_neto", 0) * IVA_TASA)

    if has_docs("linea_13"):
        codigos[509] = count_docs("linea_13")
        iva_sum = sum_field("linea_13", "iva")
        codigos[510] = iva_sum if iva_sum else int(sum_field("linea_13", "neto") * IVA_TASA)
    else:
        codigos[509] = v.get("notas_credito_cant", 0)
        codigos[510] = int(v.get("notas_credito_neto", 0) * IVA_TASA)

    total_debito = codigos[502] + codigos[717] + codigos[111] + codigos[513] - codigos[510]
    codigos[538] = total_debito

    # === CRÉDITOS ===

    if has_docs("linea_28"):
        codigos[519] = count_docs("linea_28")
        codigos[520] = sum_field("linea_28", "iva")
    else:
        codigos[519] = c.get("facturas_giro_cant", 0)
        codigos[520] = c.get("facturas_giro_iva", 0)

    if has_docs("linea_31"):
        codigos[524] = count_docs("linea_31")
        codigos[525] = sum_field("linea_31", "iva")
    else:
        codigos[524] = c.get("facturas_activo_fijo_cant", 0)
        codigos[525] = c.get("facturas_activo_fijo_iva", 0)

    if has_docs("linea_32"):
        codigos[527] = count_docs("linea_32")
        codigos[528] = sum_field("linea_32", "iva")
    else:
        codigos[527] = c.get("notas_credito_recibidas_cant", 0)
        codigos[528] = c.get("notas_credito_recibidas_iva", 0)

    if has_docs("linea_33"):
        codigos[531] = count_docs("linea_33")
        codigos[532] = sum_field("linea_33", "iva")
    else:
        codigos[531] = c.get("notas_debito_recibidas_cant", 0)
        codigos[532] = c.get("notas_debito_recibidas_iva", 0)

    if has_docs("linea_34"):
        codigos[534] = count_docs("linea_34")
        codigos[535] = sum_field("linea_34", "iva")
    else:
        codigos[534] = c.get("din_giro_cant", 0)
        codigos[535] = c.get("din_giro_iva", 0)

    if has_docs("linea_35"):
        codigos[536] = count_docs("linea_35")
        codigos[553] = sum_field("linea_35", "iva")
    else:
        codigos[536] = c.get("din_activo_fijo_cant", 0)
        codigos[553] = c.get("din_activo_fijo_iva", 0)

    codigos[511] = codigos[519] + codigos[524]
    codigos[514] = codigos[520] + codigos[525]
    codigos[564] = c.get("compras_sin_credito_cant", 0)
    codigos[521] = c.get("compras_sin_credito_neto", 0)

    codigos[504] = datos.get("remanente_anterior", 0)
    codigos[593] = dev.get("art_36_exportador", 0)
    codigos[594] = dev.get("art_27_bis", 0)
    codigos[592] = dev.get("certificado_27_bis", 0)
    codigos[539] = dev.get("cambio_sujeto", 0)

    iva_digital = int(codigos[587] * IVA_TASA)

    total_credito = (
        codigos[520] + codigos[525]
        - codigos[528] + codigos[532]
        + codigos[535] + codigos[553]
        + codigos[504]
        - codigos[593] - codigos[594] - codigos[592] - codigos[539]
        + iva_digital
    )
    codigos[537] = total_credito

    if iva_digital > 0:
        codigos[538] = total_debito + iva_digital
        total_debito = codigos[538]

    # === DETERMINACIÓN IVA ===
    if total_debito > total_credito:
        codigos[89] = total_debito - total_credito
        codigos[77] = 0
    else:
        codigos[89] = 0
        codigos[77] = total_credito - total_debito

    # === RETENCIONES ===
    if has_docs("linea_60"):
        codigos[48] = sum(d.get("iusc", d.get("iva", 0)) for d in docs["linea_60"])
    else:
        codigos[48] = ret.get("iusc_impuesto", 0)

    if has_docs("linea_61"):
        codigos[151] = sum(d.get("retencion", d.get("iva", 0)) for d in docs["linea_61"])
    else:
        codigos[151] = ret.get("honorarios_retencion", 0)

    codigos[153] = ret.get("directores_retencion", 0)

    # === PPM ===
    tasa_ppm = ppm.get("tasa", 0.25)
    codigos[115] = tasa_ppm

    if ppm.get("base_imponible") is not None:
        base_ppm = ppm["base_imponible"]
    else:
        def neto_linea(lk, fallback_key):
            if has_docs(lk):
                return sum_field(lk, "neto")
            return v.get(fallback_key, 0)

        base_ppm = (
            neto_linea("linea_7", "facturas_afectas_neto")
            + neto_linea("linea_2", "facturas_exentas_giro_neto")
            + neto_linea("linea_1", "facturas_exportacion_neto")
            + neto_linea("linea_10", "boletas_neto")
            + neto_linea("linea_12", "notas_debito_neto")
            - neto_linea("linea_13", "notas_credito_neto")
        )
    codigos[563] = base_ppm

    if ppm.get("suspension", False):
        codigos[750] = 1
        codigos[62] = 0
    else:
        codigos[750] = 0
        codigos[62] = int(base_ppm * tasa_ppm / 100)

    codigos[722] = ppm.get("remanente_sence_anterior", 0)
    codigos[721] = ppm.get("credito_sence", 0)
    credito_sence_disponible = codigos[721] + codigos[722]
    sence_aplicado = min(credito_sence_disponible, codigos[62])
    codigos[723] = sence_aplicado
    codigos[724] = credito_sence_disponible - sence_aplicado

    ppm_neto = codigos[62] - codigos[723]

    # === TOTAL ===
    codigos[595] = codigos[89] + codigos[48] + codigos[151] + codigos[153] + ppm_neto
    codigos[91] = codigos[595]
    codigos[92] = 0
    codigos[93] = 0
    codigos[94] = codigos[91]

    return codigos


# ============================================================
# Escritura del Excel
# ============================================================

def _write_section_header(ws, row, title):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    cell = ws.cell(row=row, column=1, value=title)
    cell.font = FONT_SECTION
    cell.fill = FILL_SECTION
    cell.alignment = ALIGN_LEFT
    for col in range(1, 7):
        ws.cell(row=row, column=col).fill = FILL_SECTION
        ws.cell(row=row, column=col).border = BORDER_THIN
    return row + 1


def _write_col_headers(ws, row, headers):
    for i, h in enumerate(headers, 1):
        c = ws.cell(row=row, column=i, value=h)
        c.font = Font(name="Arial", size=8, bold=True, color="333333")
        c.fill = PatternFill(start_color=GRIS_HEADER, end_color=GRIS_HEADER, fill_type="solid")
        c.alignment = ALIGN_CENTER
        c.border = BORDER_THIN
    return row + 1


def _write_data_row(ws, row, linea, cod_cant, desc, cantidad, cod_monto, monto,
                    is_total=False, is_calc=False):
    fill = FILL_TOTAL if is_total else (FILL_CALC if is_calc else None)
    font_val = FONT_TOTAL if is_total else FONT_NORMAL
    for col, val, font, align in [
        (1, linea, FONT_CODE, ALIGN_CENTER),
        (2, cod_cant or "", FONT_SMALL, ALIGN_CENTER),
        (3, desc, font_val, ALIGN_LEFT),
        (4, cantidad if cantidad else "", FONT_NORMAL, ALIGN_RIGHT),
        (5, cod_monto or "", FONT_SMALL, ALIGN_CENTER),
        (6, formato_peso(monto) if monto is not None else "", font_val, ALIGN_RIGHT),
    ]:
        c = ws.cell(row=row, column=col, value=val)
        c.font = font
        c.alignment = align
        c.border = BORDER_THIN
        if fill:
            c.fill = fill
    return row + 1


def _write_hoja_f29(wb, codigos, enc, datos):
    """Hoja 1: Formulario F29 resumen."""
    mes = enc.get("periodo_mes", 1)
    anio = enc.get("periodo_anio", 2026)
    nombre_mes = MESES.get(mes, str(mes))
    docs = datos.get("documentos", {})

    ws = wb.active
    ws.title = f"F29 — {nombre_mes} {anio}"
    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 10
    ws.column_dimensions["C"].width = 52
    ws.column_dimensions["D"].width = 14
    ws.column_dimensions["E"].width = 10
    ws.column_dimensions["F"].width = 20

    row = 1

    # Encabezado principal
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    c = ws.cell(row=row, column=1,
                value="FORMULARIO 29 — DECLARACIÓN MENSUAL Y PAGO SIMULTÁNEO DE IMPUESTOS")
    c.font = FONT_HEADER; c.fill = FILL_HEADER; c.alignment = ALIGN_CENTER
    for col in range(1, 7): ws.cell(row=row, column=col).fill = FILL_HEADER
    row += 1
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    c = ws.cell(row=row, column=1, value="Servicio de Impuestos Internos — Chile")
    c.font = Font(name="Arial", size=9, italic=True, color=BLANCO)
    c.fill = FILL_HEADER; c.alignment = ALIGN_CENTER
    for col in range(1, 7): ws.cell(row=row, column=col).fill = FILL_HEADER
    row += 2

    for label, value in [
        ("RUT:", enc.get("rut", "—")),
        ("Razón Social:", enc.get("razon_social", "—")),
        ("Período Tributario:", f"{mes:02d}-{anio}"),
        ("Régimen:", enc.get("regimen", "—").replace("_", " ").title()),
    ]:
        ws.cell(row=row, column=1, value=label).font = FONT_CODE
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
        ws.cell(row=row, column=2, value=value).font = FONT_NORMAL
        row += 1
    row += 1

    def dlabel(lk):
        n = len(docs.get(lk, []))
        return f" [{n} docs → hoja Detalle]" if n > 0 else ""

    # DÉBITO
    row = _write_section_header(ws, row, "DÉBITO FISCAL — Ventas y Servicios (Líneas 1–23)")
    row = _write_col_headers(ws, row, ["Línea", "Cód.", "Descripción", "Cant.", "Cód.", "Monto ($)"])
    for li, cc, desc, cant, cm, monto in [
        ("1",  "585", f"Exportaciones{dlabel('linea_1')}", codigos[585], "20", codigos[20]),
        ("2",  "586", f"Ventas/servicios exentos{dlabel('linea_2')}", codigos[586], "142", codigos[142]),
        ("5",  "515", f"FC serv. digitales extranjeros{dlabel('linea_5')}", codigos[515], "587", codigos[587]),
        ("7",  "503", f"⭐ Facturas afectas del giro{dlabel('linea_7')}", codigos[503], "502", codigos[502]),
        ("9",  "716", f"Ventas activo fijo{dlabel('linea_9')}", codigos[716], "717", codigos[717]),
        ("10", "110", f"Boletas{dlabel('linea_10')}", codigos[110], "111", codigos[111]),
        ("12", "512", f"Notas de débito emitidas{dlabel('linea_12')}", codigos[512], "513", codigos[513]),
        ("13", "509", f"(-) Notas de crédito emitidas{dlabel('linea_13')}", codigos[509], "510", -codigos[510] if codigos[510] else 0),
        ("23", "",    "TOTAL DÉBITOS", "", "538", codigos[538]),
    ]:
        row = _write_data_row(ws, row, li, cc, desc, cant, cm, monto,
                              is_total=(li == "23"), is_calc=(li == "23"))
    row += 1

    # CRÉDITO
    row = _write_section_header(ws, row, "CRÉDITO FISCAL — Compras y Gastos (Líneas 24–49)")
    row = _write_col_headers(ws, row, ["Línea", "Cód.", "Descripción", "Cant.", "Cód.", "Monto ($)"])
    for li, cc, desc, cant, cm, monto in [
        ("24", "511", "[Info] IVA total DTE recibidos", codigos[511], "514", codigos[514]),
        ("28", "519", f"⭐ Facturas recibidas del giro{dlabel('linea_28')}", codigos[519], "520", codigos[520]),
        ("31", "524", f"⭐ Facturas activo fijo{dlabel('linea_31')}", codigos[524], "525", codigos[525]),
        ("32", "527", f"(-) NC recibidas{dlabel('linea_32')}", codigos[527], "528", -codigos[528] if codigos[528] else 0),
        ("33", "531", f"ND recibidas{dlabel('linea_33')}", codigos[531], "532", codigos[532]),
        ("34", "534", f"DIN importaciones giro{dlabel('linea_34')}", codigos[534], "535", codigos[535]),
        ("35", "536", f"DIN importaciones activo fijo{dlabel('linea_35')}", codigos[536], "553", codigos[553]),
        ("36", "",    "Remanente CF mes anterior", "", "504", codigos[504]),
        ("37", "",    "(-) Devolución Art. 36 exportador", "", "593", -codigos[593] if codigos[593] else 0),
        ("38", "",    "(-) Devolución Art. 27 bis", "", "594", -codigos[594] if codigos[594] else 0),
        ("49", "",    "TOTAL CRÉDITOS", "", "537", codigos[537]),
    ]:
        row = _write_data_row(ws, row, li, cc, desc, cant, cm, monto,
                              is_total=(li == "49"), is_calc=(li == "49"))
    row += 1

    # IVA
    row = _write_section_header(ws, row, "DETERMINACIÓN DEL IVA (Línea 50)")
    row = _write_col_headers(ws, row, ["Línea", "Cód.", "Descripción", "", "Cód.", "Monto ($)"])
    if codigos[89] > 0:
        row = _write_data_row(ws, row, "50", "", "IVA DETERMINADO (a pagar)", "", "89", codigos[89], is_calc=True)
    else:
        row = _write_data_row(ws, row, "50", "", "REMANENTE CF (para mes siguiente)", "", "77", codigos[77], is_calc=True)
    row += 1

    # RETENCIONES
    row = _write_section_header(ws, row, "RETENCIONES DE IMPUESTO A LA RENTA (Líneas 59–68)")
    row = _write_col_headers(ws, row, ["Línea", "Cód.", "Descripción", "", "Cód.", "Monto ($)"])
    for li, cc, desc, cant, cm, monto in [
        ("60", "", f"IUSC sueldos{dlabel('linea_60')}", "", "48", codigos[48]),
        ("61", "", f"⭐ Retención honorarios 15,25%{dlabel('linea_61')}", "", "151", codigos[151]),
        ("62", "", "Retención dietas directores", "", "153", codigos[153]),
    ]:
        row = _write_data_row(ws, row, li, cc, desc, cant, cm, monto)
    row += 1

    # PPM
    row = _write_section_header(ws, row, "PPM (Líneas 69–78)")
    row = _write_col_headers(ws, row, ["Línea", "Cód.", "Descripción", "", "Cód.", "Monto ($)"])
    susp = " [SUSPENDIDO]" if codigos.get(750) == 1 else ""
    for li, cc, desc, cant, cm, monto in [
        ("69", "563", f"Base imponible PPM{susp}", "", "", codigos[563]),
        ("69", "115", f"Tasa PPM: {codigos[115]}%", "", "", None),
        ("69", "",    "PPM determinado", "", "62", codigos[62]),
        ("75", "723", "(-) Crédito SENCE aplicado", "", "", -codigos[723] if codigos[723] else 0),
    ]:
        row = _write_data_row(ws, row, li, cc, desc, cant, cm, monto)
    row += 1

    # TOTAL
    row = _write_section_header(ws, row, "TOTAL A PAGAR (Líneas 141–144)")
    row = _write_col_headers(ws, row, ["Línea", "Cód.", "Descripción", "", "Cód.", "Monto ($)"])
    for li, cc, desc, cant, cm, monto in [
        ("80",  "", "Subtotal impuesto determinado", "", "595", codigos[595]),
        ("141", "", "TOTAL A PAGAR EN PLAZO LEGAL", "", "91", codigos[91]),
        ("142", "", "Más IPC (reajuste fuera de plazo)", "", "92", codigos[92]),
        ("143", "", "Más intereses y multas", "", "93", codigos[93]),
        ("144", "", "TOTAL A PAGAR CON RECARGO", "", "94", codigos[94]),
    ]:
        is_t = li in ("141", "144")
        row = _write_data_row(ws, row, li, cc, desc, cant, cm, monto,
                              is_total=is_t, is_calc=is_t)


def _write_hoja_detalle_docs(wb, datos, codigos):
    """Hoja 2: Detalle de documentos por cada línea del F29."""
    docs = datos.get("documentos", {})
    if not docs:
        ws = wb.create_sheet(title="Detalle Documentos")
        ws.cell(row=1, column=1, value="Sin documentos individuales. Se usaron totales agregados.").font = FONT_SECTION
        return

    ws = wb.create_sheet(title="Detalle Documentos")
    for i, w in enumerate([4, 14, 12, 16, 28, 28, 16, 16, 16, 16], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    row = 1
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=10)
    c = ws.cell(row=row, column=1, value="DETALLE DE DOCUMENTOS POR LÍNEA DEL F29")
    c.font = FONT_HEADER; c.fill = FILL_HEADER; c.alignment = ALIGN_CENTER
    for col in range(1, 11): ws.cell(row=row, column=col).fill = FILL_HEADER
    row += 2

    orden_lineas = [
        "linea_1", "linea_2", "linea_5", "linea_7", "linea_9",
        "linea_10", "linea_11", "linea_12", "linea_13",
        "linea_28", "linea_29", "linea_31", "linea_32", "linea_33",
        "linea_34", "linea_35", "linea_60", "linea_61",
    ]

    for lk in orden_lineas:
        if lk not in docs or not docs[lk]:
            continue

        info = LINEAS_INFO.get(lk, {})
        seccion = info.get("seccion", "")
        doc_list = docs[lk]

        # --- Encabezado de sección por línea ---
        header = (
            f"LÍNEA {info.get('linea', '?')} — "
            f"{info.get('nombre', lk)} — "
            f"Cód. {info.get('codigo', '?')} — "
            f"{len(doc_list)} documento(s)"
        )
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=10)
        cell = ws.cell(row=row, column=1, value=header)
        cell.font = Font(name="Arial", size=10, bold=True, color=BLANCO)

        color = {"debito": "E65100", "credito": "2E7D32", "retencion": "1565C0"}.get(seccion, "333333")
        fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
        for col in range(1, 11):
            ws.cell(row=row, column=col).fill = fill
            ws.cell(row=row, column=col).font = Font(name="Arial", size=10, bold=True, color=BLANCO)
        row += 1

        # --- Encabezados de columnas ---
        columnas = get_columnas_para_linea(seccion, lk)
        ws.cell(row=row, column=1, value="#").font = FONT_DOC_BOLD
        ws.cell(row=row, column=1).fill = FILL_TOTAL
        ws.cell(row=row, column=1).alignment = ALIGN_CENTER
        ws.cell(row=row, column=1).border = BORDER_THIN
        for ci, cn in enumerate(columnas, 2):
            c = ws.cell(row=row, column=ci, value=cn)
            c.font = FONT_DOC_BOLD; c.fill = FILL_TOTAL
            c.alignment = ALIGN_CENTER; c.border = BORDER_THIN
        row += 1

        # --- Filas de documentos ---
        # Detectar cuáles columnas son de montos (las últimas 2-4 según tipo)
        n_text_cols = 5  # numero, fecha, rut, razon_social, descripcion/cargo
        totals = {}

        for i, doc in enumerate(doc_list, 1):
            values = get_doc_values(doc, seccion, lk)

            # Número de fila
            ws.cell(row=row, column=1, value=i).font = FONT_DOC
            ws.cell(row=row, column=1).alignment = ALIGN_CENTER
            ws.cell(row=row, column=1).border = BORDER_THIN

            alt_fill = None
            if i % 2 == 0:
                alt_fill = FILL_DEBITO_ROW if seccion == "debito" else (
                    FILL_CREDITO_ROW if seccion == "credito" else None)
            if alt_fill:
                ws.cell(row=row, column=1).fill = alt_fill

            for ci, val in enumerate(values, 2):
                cell = ws.cell(row=row, column=ci)
                cell.border = BORDER_THIN

                col_name = columnas[ci - 2]
                is_monto = ci - 2 >= n_text_cols  # columnas después de los 5 campos de texto

                if is_monto and isinstance(val, (int, float)):
                    cell.value = formato_peso(val)
                    cell.font = FONT_DOC; cell.alignment = ALIGN_RIGHT
                    totals[col_name] = totals.get(col_name, 0) + val
                else:
                    cell.value = val
                    cell.font = FONT_DOC; cell.alignment = ALIGN_LEFT

                if alt_fill:
                    cell.fill = alt_fill

            row += 1

        # --- Fila TOTAL ---
        ws.cell(row=row, column=1, value="").fill = FILL_TOTAL
        ws.cell(row=row, column=1).border = BORDER_THIN
        ws.cell(row=row, column=2, value="TOTAL").font = FONT_DOC_BOLD
        ws.cell(row=row, column=2).fill = FILL_TOTAL
        ws.cell(row=row, column=2).border = BORDER_THIN

        for ci, cn in enumerate(columnas, 2):
            cell = ws.cell(row=row, column=ci)
            cell.fill = FILL_TOTAL; cell.border = BORDER_THIN
            if cn in totals:
                cell.value = formato_peso(totals[cn])
                cell.font = Font(name="Arial", size=8, bold=True, color="CC0000")
                cell.alignment = ALIGN_RIGHT
            else:
                cell.font = FONT_DOC_BOLD

        row += 2  # espacio entre secciones


def _write_hoja_calculos(wb, codigos, datos):
    """Hoja 3: Resumen de fórmulas."""
    ws = wb.create_sheet(title="Detalle de Cálculos")
    ws.column_dimensions["A"].width = 45
    ws.column_dimensions["B"].width = 25

    r = 1
    ws.cell(row=r, column=1, value="DETALLE DE CÁLCULOS DEL F29").font = FONT_SECTION
    r += 2

    for desc, val in [
        ("DÉBITO FISCAL", ""),
        ("Facturas afectas IVA (código 502)", formato_peso(codigos[502])),
        ("ND emitidas IVA (código 513)", formato_peso(codigos[513])),
        ("(-) NC emitidas IVA (código 510)", formato_peso(codigos[510])),
        ("Total Débito (código 538)", formato_peso(codigos[538])),
        ("", ""),
        ("CRÉDITO FISCAL", ""),
        ("Facturas del giro IVA (código 520)", formato_peso(codigos[520])),
        ("Activo fijo IVA (código 525)", formato_peso(codigos[525])),
        ("FC digital IVA (efecto neutro)", formato_peso(int(codigos[587] * 0.19))),
        ("Remanente CF anterior (código 504)", formato_peso(codigos[504])),
        ("Total Crédito (código 537)", formato_peso(codigos[537])),
        ("", ""),
        ("DETERMINACIÓN IVA", ""),
        ("Débito − Crédito", f"{formato_peso(codigos[538])} − {formato_peso(codigos[537])}"),
        ("IVA a pagar (89)" if codigos[89] > 0 else "Remanente CF (77)",
         formato_peso(codigos[89]) if codigos[89] > 0 else formato_peso(codigos[77])),
        ("", ""),
        ("PPM", ""),
        ("Base (código 563)", formato_peso(codigos[563])),
        ("Tasa (código 115)", f"{codigos[115]}%"),
        ("PPM determinado (código 62)", formato_peso(codigos[62])),
        ("(-) SENCE (código 723)", formato_peso(codigos[723])),
        ("", ""),
        ("TOTAL", ""),
        ("IVA determinado", formato_peso(codigos[89])),
        ("+ IUSC (código 48)", formato_peso(codigos[48])),
        ("+ Retención honorarios (código 151)", formato_peso(codigos[151])),
        ("+ PPM neto", formato_peso(codigos[62] - codigos[723])),
        ("= TOTAL A PAGAR (código 91)", formato_peso(codigos[91])),
    ]:
        ws.cell(row=r, column=1, value=desc).font = FONT_SECTION if val == "" and desc else FONT_NORMAL
        ws.cell(row=r, column=2, value=val).font = FONT_NORMAL
        r += 1


def _write_hoja_alertas(wb, codigos, datos):
    """Hoja 4: Alertas y notas."""
    enc = datos.get("encabezado", {})
    docs = datos.get("documentos", {})

    ws = wb.create_sheet(title="Alertas y Notas")
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = 70

    r = 1
    ws.cell(row=r, column=1, value="ALERTAS Y VALIDACIONES").font = FONT_SECTION
    r += 2

    alertas = []

    if codigos[77] > 0 and codigos[538] > 0 and codigos[77] > codigos[538] * 3:
        alertas.append(("⚠️ REMANENTE",
            f"Remanente CF ({formato_peso(codigos[77])}) muy superior al débito. "
            "Considerar devolución Art. 36 o Art. 27 bis."))

    if codigos.get(585, 0) > 0:
        alertas.append(("📦 EXPORTACIÓN",
            f"{codigos[585]} facturas de exportación ({formato_peso(codigos[20])} neto). "
            "Verificar calificación Aduanas. DUS requerido si > USD 2.000."))

    if codigos.get(515, 0) > 0:
        alertas.append(("☁️ SERV. DIGITALES",
            f"{codigos[515]} FC servicios digitales (neto: {formato_peso(codigos[587])}). "
            "Verificar emisión Factura de Compra tipo 46."))

    if codigos[151] > 0:
        alertas.append(("👤 HONORARIOS",
            f"Retención: {formato_peso(codigos[151])}. Tasa 2026: 15,25%."))

    if codigos[504] > 0:
        alertas.append(("🔄 REMANENTE ANT.",
            f"Remanente CF arrastrado: {formato_peso(codigos[504])}. "
            "Verificar vs código 77 del F29 anterior."))

    has_afectas = codigos.get(503, 0) > 0 or codigos.get(110, 0) > 0
    has_exentas = codigos.get(585, 0) > 0 or codigos.get(586, 0) > 0
    if has_afectas and has_exentas:
        alertas.append(("⚠️ PRORRATEO",
            "Ventas afectas + exentas/exportación. Verificar prorrateo de CF de uso común."))

    # Validar consistencia docs vs códigos
    check_map = {"linea_7": 503, "linea_13": 509, "linea_12": 512,
                 "linea_28": 519, "linea_31": 524, "linea_1": 585}
    for lk, cod in check_map.items():
        if lk in docs and docs[lk]:
            n = len(docs[lk])
            if codigos.get(cod, 0) != n:
                info = LINEAS_INFO.get(lk, {})
                alertas.append(("⚠️ INCONSISTENCIA",
                    f"Línea {info.get('linea', '?')}: cantidad calculada={codigos[cod]} "
                    f"pero hay {n} documentos."))

    mes = enc.get("periodo_mes", 1)
    anio = enc.get("periodo_anio", 2026)
    sig_mes = mes % 12 + 1
    sig_anio = anio if mes < 12 else anio + 1
    alertas.append(("📅 PLAZO",
        f"Declarar antes del 20 de {MESES.get(sig_mes, '')} {sig_anio} (internet)."))

    alertas.append(("📋 DISCLAIMER",
        "Herramienta de apoyo. NO es asesoría tributaria. "
        "Debe ser revisado por un contador antes de presentarse al SII."))

    for tipo, msg in alertas:
        c1 = ws.cell(row=r, column=1, value=tipo)
        c1.font = Font(name="Arial", size=9, bold=True)
        c2 = ws.cell(row=r, column=2, value=msg)
        c2.font = FONT_NORMAL
        c2.alignment = Alignment(wrap_text=True, vertical="top")
        if "⚠️" in tipo:
            c1.fill = FILL_ALERTA; c2.fill = FILL_ALERTA
        r += 1


def generar_f29_excel(datos, output_path):
    """
    Genera Excel del F29 con 4 hojas:
        1. F29 resumen
        2. Detalle de documentos por línea (NUEVO v2)
        3. Detalle de cálculos
        4. Alertas y notas
    """
    codigos = calcular_f29(datos)
    enc = datos.get("encabezado", {})
    wb = openpyxl.Workbook()
    _write_hoja_f29(wb, codigos, enc, datos)
    _write_hoja_detalle_docs(wb, datos, codigos)
    _write_hoja_calculos(wb, codigos, datos)
    _write_hoja_alertas(wb, codigos, datos)
    wb.save(output_path)
    return codigos


# ============================================================
# Testing
# ============================================================
if __name__ == "__main__":
    datos_ejemplo = {
        "encabezado": {
            "rut": "76.123.456-7",
            "razon_social": "DevSoft SpA",
            "periodo_mes": 1,
            "periodo_anio": 2026,
            "regimen": "pro_pyme_general",
        },
        "documentos": {
            "linea_7": [
                {"tipo": "factura", "numero": "F-00101", "fecha": "2026-01-05",
                 "rut": "77.000.100-5", "razon_social": "Banco Nacional S.A.",
                 "descripcion": "Desarrollo módulo core banking",
                 "neto": 8000000, "iva": 1520000, "exento": 0, "total": 9520000},
                {"tipo": "factura", "numero": "F-00102", "fecha": "2026-01-10",
                 "rut": "76.500.200-3", "razon_social": "Retail Chile SpA",
                 "descripcion": "Mantención plataforma e-commerce",
                 "neto": 3500000, "iva": 665000, "exento": 0, "total": 4165000},
                {"tipo": "factura", "numero": "F-00103", "fecha": "2026-01-15",
                 "rut": "78.900.300-1", "razon_social": "Logística Express Ltda.",
                 "descripcion": "Consultoría arquitectura microservicios",
                 "neto": 2000000, "iva": 380000, "exento": 0, "total": 2380000},
                {"tipo": "factura", "numero": "F-00104", "fecha": "2026-01-18",
                 "rut": "76.500.200-3", "razon_social": "Retail Chile SpA",
                 "descripcion": "Desarrollo integración API pagos",
                 "neto": 4500000, "iva": 855000, "exento": 0, "total": 5355000},
                {"tipo": "factura", "numero": "F-00105", "fecha": "2026-01-22",
                 "rut": "79.100.400-K", "razon_social": "Seguros del Pacífico S.A.",
                 "descripcion": "Sprint 3 - Portal clientes",
                 "neto": 6000000, "iva": 1140000, "exento": 0, "total": 7140000},
                {"tipo": "factura", "numero": "F-00106", "fecha": "2026-01-25",
                 "rut": "77.000.100-5", "razon_social": "Banco Nacional S.A.",
                 "descripcion": "Soporte mensual sistemas",
                 "neto": 1500000, "iva": 285000, "exento": 0, "total": 1785000},
                {"tipo": "factura", "numero": "F-00107", "fecha": "2026-01-28",
                 "rut": "76.800.500-7", "razon_social": "Minera Austral SpA",
                 "descripcion": "Dashboard analítica operacional",
                 "neto": 3200000, "iva": 608000, "exento": 0, "total": 3808000},
                {"tipo": "factura", "numero": "F-00108", "fecha": "2026-01-30",
                 "rut": "78.200.600-2", "razon_social": "Constructora Pacífico Ltda.",
                 "descripcion": "App mobile seguimiento obras",
                 "neto": 2800000, "iva": 532000, "exento": 0, "total": 3332000},
            ],
            "linea_13": [
                {"tipo": "nota_credito", "numero": "NC-0015", "fecha": "2026-01-20",
                 "rut": "76.500.200-3", "razon_social": "Retail Chile SpA",
                 "descripcion": "Descuento por volumen Q4 2025",
                 "neto": 1000000, "iva": 190000, "exento": 0, "total": 1190000},
            ],
            "linea_1": [
                {"tipo": "factura_exportacion", "numero": "EXP-0021", "fecha": "2026-01-08",
                 "rut": "EXT-001", "razon_social": "TechCorp Inc. (USA)",
                 "descripcion": "SaaS platform - monthly license",
                 "neto": 7000000, "iva": 0, "exento": 7000000, "total": 7000000},
                {"tipo": "factura_exportacion", "numero": "EXP-0022", "fecha": "2026-01-22",
                 "rut": "EXT-002", "razon_social": "DataFlow GmbH (Germany)",
                 "descripcion": "Custom API development - milestone 2",
                 "neto": 5000000, "iva": 0, "exento": 5000000, "total": 5000000},
            ],
            "linea_28": [
                {"tipo": "factura", "numero": "F-98001", "fecha": "2026-01-02",
                 "rut": "96.000.000-0", "razon_social": "Inmobiliaria Oficinas SpA",
                 "descripcion": "Arriendo oficina enero",
                 "neto": 1800000, "iva": 342000, "total": 2142000},
                {"tipo": "factura", "numero": "F-98002", "fecha": "2026-01-05",
                 "rut": "76.100.100-1", "razon_social": "VTR Comunicaciones S.A.",
                 "descripcion": "Internet fibra 1Gbps",
                 "neto": 89000, "iva": 16910, "total": 105910},
                {"tipo": "factura", "numero": "F-98003", "fecha": "2026-01-10",
                 "rut": "76.200.200-2", "razon_social": "Enel Distribución Chile",
                 "descripcion": "Electricidad oficina",
                 "neto": 120000, "iva": 22800, "total": 142800},
                {"tipo": "factura", "numero": "F-98004", "fecha": "2026-01-12",
                 "rut": "78.300.300-3", "razon_social": "Cleaning Pro Ltda.",
                 "descripcion": "Servicio aseo oficina",
                 "neto": 250000, "iva": 47500, "total": 297500},
                {"tipo": "factura", "numero": "F-98005", "fecha": "2026-01-15",
                 "rut": "76.400.400-4", "razon_social": "Café & Snacks SpA",
                 "descripcion": "Coffee break mensual",
                 "neto": 180000, "iva": 34200, "total": 214200},
                {"tipo": "factura", "numero": "F-98006", "fecha": "2026-01-20",
                 "rut": "79.500.500-5", "razon_social": "LegalTech Abogados Ltda.",
                 "descripcion": "Asesoría legal contratos software",
                 "neto": 800000, "iva": 152000, "total": 952000},
            ],
            "linea_31": [
                {"tipo": "factura", "numero": "F-55001", "fecha": "2026-01-18",
                 "rut": "76.600.600-6", "razon_social": "Apple Chile SpA",
                 "descripcion": "3x MacBook Pro M4 para equipo dev",
                 "neto": 8700000, "iva": 1653000, "total": 10353000},
            ],
            "linea_5": [
                {"tipo": "factura_compra", "numero": "FC-0031", "fecha": "2026-01-31",
                 "rut": "EXT-AWS", "razon_social": "Amazon Web Services Inc.",
                 "descripcion": "Cloud computing enero (EC2, S3, RDS)",
                 "neto": 850000, "iva": 161500, "total": 1011500},
                {"tipo": "factura_compra", "numero": "FC-0032", "fecha": "2026-01-31",
                 "rut": "EXT-GCP", "razon_social": "Google Cloud Platform",
                 "descripcion": "Cloud Run + BigQuery enero",
                 "neto": 320000, "iva": 60800, "total": 380800},
                {"tipo": "factura_compra", "numero": "FC-0033", "fecha": "2026-01-31",
                 "rut": "EXT-GH", "razon_social": "GitHub Inc.",
                 "descripcion": "GitHub Enterprise - 15 seats",
                 "neto": 180000, "iva": 34200, "total": 214200},
            ],
            "linea_61": [
                {"tipo": "boleta_honorarios", "numero": "BH-5001", "fecha": "2026-01-31",
                 "rut": "15.123.456-7", "razon_social": "María Pérez González",
                 "descripcion": "Desarrollo frontend React - 80hrs",
                 "bruto": 2000000, "retencion": 305000, "liquido": 1695000},
                {"tipo": "boleta_honorarios", "numero": "BH-5002", "fecha": "2026-01-31",
                 "rut": "16.789.012-3", "razon_social": "Carlos Muñoz Rivera",
                 "descripcion": "QA testing automatizado",
                 "bruto": 1000000, "retencion": 152500, "liquido": 847500},
            ],
            "linea_60": [
                {"tipo": "liquidacion_sueldo", "numero": "LIQ-001", "fecha": "2026-01-31",
                 "rut": "17.111.222-3", "razon_social": "Andrea López Silva",
                 "cargo": "Tech Lead", "bruto": 3500000, "iusc": 185000, "liquido": 2800000},
                {"tipo": "liquidacion_sueldo", "numero": "LIQ-002", "fecha": "2026-01-31",
                 "rut": "18.333.444-5", "razon_social": "Diego Fernández Castro",
                 "cargo": "Senior Developer", "bruto": 2800000, "iusc": 95000, "liquido": 2350000},
                {"tipo": "liquidacion_sueldo", "numero": "LIQ-003", "fecha": "2026-01-31",
                 "rut": "19.555.666-7", "razon_social": "Valentina Rojas Morales",
                 "cargo": "UX Designer", "bruto": 2200000, "iusc": 45000, "liquido": 1900000},
            ],
        },
        "remanente_anterior": 450000,
        "devoluciones": {
            "art_36_exportador": 0, "art_27_bis": 0,
            "certificado_27_bis": 0, "cambio_sujeto": 0,
        },
        "retenciones": {"directores_retencion": 0},
        "ppm": {
            "tasa": 0.25, "base_imponible": None,
            "credito_sence": 0, "remanente_sence_anterior": 0,
            "suspension": False,
        },
        "ventas": {},
        "compras": {},
    }

    output = "f29_enero_2026_v2.xlsx"
    codigos = generar_f29_excel(datos_ejemplo, output)
    print(f"✅ F29 v2.0 generado: {output}")
    print(f"   Facturas afectas: {codigos[503]} docs → Débito IVA: {formato_peso(codigos[502])}")
    print(f"   NC emitidas: {codigos[509]} docs → IVA: {formato_peso(codigos[510])}")
    print(f"   Exportaciones: {codigos[585]} docs → Neto: {formato_peso(codigos[20])}")
    print(f"   Facturas compras: {codigos[519]} docs → CF IVA: {formato_peso(codigos[520])}")
    print(f"   Activo fijo: {codigos[524]} docs → CF IVA: {formato_peso(codigos[525])}")
    print(f"   FC digitales: {codigos[515]} docs → Neto: {formato_peso(codigos[587])}")
    print(f"   Honorarios: retención {formato_peso(codigos[151])}")
    print(f"   IUSC: {formato_peso(codigos[48])}")
    print(f"   ---")
    print(f"   Total Débito (538): {formato_peso(codigos[538])}")
    print(f"   Total Crédito (537): {formato_peso(codigos[537])}")
    print(f"   IVA a pagar (89): {formato_peso(codigos[89])}")
    print(f"   Remanente CF (77): {formato_peso(codigos[77])}")
    print(f"   PPM (62): {formato_peso(codigos[62])}")
    print(f"   TOTAL A PAGAR (91): {formato_peso(codigos[91])}")