"""
generar_f29.py v3 — Genera Excel F29 con estilo SII.

Uso:
    from scripts.generar_f29 import generar_f29_excel
    generar_f29_excel(datos, output_path)

    datos puede tener:
    - "codigos": dict de código F29 → valor (modo directo)
    - O la estructura tradicional con "ventas", "compras", "documentos"
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ============================================================
# Estilos SII
# ============================================================
BLUE = "D9EDF7"
GRAY = "E8E8E8"
LGRAY = "EEEEEE"
WHITE = "FFFFFF"
BLACK = "000000"

FILL_BLUE = PatternFill(start_color=BLUE, end_color=BLUE, fill_type="solid")
FILL_GRAY = PatternFill(start_color=GRAY, end_color=GRAY, fill_type="solid")
FILL_LGRAY = PatternFill(start_color=LGRAY, end_color=LGRAY, fill_type="solid")
FILL_WHITE = PatternFill(start_color=WHITE, end_color=WHITE, fill_type="solid")

F10B = Font(name="Arial", size=10, bold=True, color=BLACK)
F8B = Font(name="Arial", size=8, bold=True, color=BLACK)
F8 = Font(name="Arial", size=8, color=BLACK)
F7 = Font(name="Arial", size=7, color=BLACK)
F7B = Font(name="Arial", size=7, bold=True, color=BLACK)

AL = Alignment(horizontal="left", vertical="center", wrap_text=True)
AC = Alignment(horizontal="center", vertical="center", wrap_text=True)
AR = Alignment(horizontal="right", vertical="center", wrap_text=True)
AJ = Alignment(horizontal="justify", vertical="center", wrap_text=True)

BORDER = Border(
    left=Side(style="medium", color=BLACK),
    right=Side(style="medium", color=BLACK),
    top=Side(style="medium", color=BLACK),
    bottom=Side(style="medium", color=BLACK),
)

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

NCOLS = 7  # Columnas A-G


def fmt(v):
    """Formatea número con separador de miles chileno."""
    if v is None:
        return ""
    if isinstance(v, float):
        if v == int(v):
            v = int(v)
        else:
            return f"{v:,.1f}".replace(",", ".")
    if isinstance(v, int):
        if v == 0:
            return ""
        return f"{v:,}".replace(",", ".")
    return str(v)


def formato_peso(v):
    """Formato con signo $ para compatibilidad."""
    if v is None or v == 0:
        return "$0"
    if isinstance(v, float):
        v = int(v)
    if v < 0:
        return f"-${abs(v):,}".replace(",", ".")
    return f"${v:,}".replace(",", ".")


# ============================================================
# Helpers de escritura
# ============================================================

def _c(ws, r, c, val, font=F7, fill=FILL_WHITE, align=AL):
    """Escribe una celda con formato."""
    cell = ws.cell(row=r, column=c, value=val)
    cell.font = font
    cell.fill = fill
    cell.alignment = align
    cell.border = BORDER
    return cell


def _borders(ws, r, c1, c2):
    """Aplica bordes a un rango de celdas."""
    for c in range(c1, c2 + 1):
        ws.cell(row=r, column=c).border = BORDER


def _section(ws, r, text, font=F10B):
    """Escribe un encabezado de sección que abarca todas las columnas."""
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=NCOLS)
    cell = ws.cell(row=r, column=1, value=text)
    cell.font = font
    cell.fill = FILL_BLUE
    cell.alignment = AJ if font == F10B else AC
    for c in range(1, NCOLS + 1):
        ws.cell(row=r, column=c).fill = FILL_BLUE
        ws.cell(row=r, column=c).border = BORDER
    return r + 1


def _colhdr(ws, r, qty_label="Cantidad de documentos", amt_label="Débitos"):
    """Escribe fila de encabezados de columna."""
    headers = [
        (1, "Línea", AC),
        (2, "", AC),
        (3, "Cód", AC),
        (4, qty_label, AC),
        (5, "Cód", AC),
        (6, amt_label, AC),
        (7, "+/-", AC),
    ]
    for c, val, align in headers:
        _c(ws, r, c, val, F7B, FILL_BLUE, align)
    return r + 1


def _line(ws, r, num, desc, cq, cv, ca, av, op, total=False):
    """Escribe una línea de datos del F29."""
    f = F7B if total else F7
    fd = FILL_GRAY if total else FILL_WHITE
    fv = FILL_GRAY if total else FILL_WHITE

    _c(ws, r, 1, num, f, FILL_GRAY, AC)        # Línea
    _c(ws, r, 2, desc, f, fd, AL)              # Descripción
    _c(ws, r, 3, cq or "", F7, FILL_BLUE, AC)  # Código cant
    _c(ws, r, 4, fmt(cv), f, fv, AR)           # Cantidad
    _c(ws, r, 5, ca or "", F7, FILL_BLUE, AC)  # Código monto
    _c(ws, r, 6, fmt(av), f, fv, AR)           # Monto
    _c(ws, r, 7, op, f, FILL_GRAY, AC)         # Operador
    return r + 1


# ============================================================
# Definición de líneas del F29
# ============================================================
# Cada línea: (num, descripción, código_cant, código_monto, operador)

DEBITOS_INFO = [
    ("1", "Exportaciones", 585, 20, ""),
    ("2", "Ventas y/o Servicios prestados Exentos o No Gravados del giro", 586, 142, ""),
    ("3", "Ventas con retención sobre el margen de comercialización (contribuyentes retenidos)", 731, 732, ""),
    ("4", "Ventas y/o Servicios prestados Exentos o No Gravados que no son del giro", 714, 715, ""),
    ("5", "Facturas de Compra recibidas con retención total (contribuyentes retenidos) y Factura de Inicio emitida", 515, 587, ""),
    ("6", "Facturas de compra recibidas con retención parcial (Total neto)", None, 720, ""),
]

DEBITOS_GENERA = [
    ("7", "Facturas emitidas por ventas y servicios del giro", 503, 502, "+"),
    ("8", "Facturas emitidas por la venta de bienes inmuebles afectas a IVA", 763, 764, "+"),
    ("9", "Facturas y Notas de Débitos por ventas y servicios que no son del giro (activo fijo y otros)", 716, 717, "+"),
    ("10", "Boletas", 110, 111, "+"),
    ("11", "Comprobantes o Recibos de Pago (transacciones medios electrónicos)", 758, 759, "+"),
    ("12", "Notas de débito emitidas del giro y ND recibidas por retención parcial cambio de sujeto", 512, 513, "+"),
    ("13", "Notas de Crédito emitidas por Facturas del giro y NC recibidas por retención parcial cambio de sujeto", 509, 510, "-"),
    ("14", "NC emitidas por Vales de máquinas autorizadas por el Servicio", 708, 709, "-"),
    ("15", "NC emitidas por ventas y servicios que no son del giro (activo fijo y otros)", 733, 734, "-"),
    ("16", "FC recibidas con retención parcial (contribuyentes retenidos)", 516, 517, "+"),
    ("17", "Liquidación y Liquidación Factura", 500, 501, "+"),
    ("18", "Adiciones al Débito Fiscal del mes, Art. 27 bis", None, 154, "+"),
    ("19", "Restitución Adicional Art. 27 bis, inc. 2° (Ley N° 19.738)", None, 518, "+"),
    ("20", "Reintegro Impuesto Timbres y Estampillas, Art 3° Ley N° 20.259", None, 713, "+"),
    ("21", "Adiciones al Débito por IEPD Ley 20.765", None, 741, "+"),
    ("22", "Restitución Adicional Reembolso Remanente CF IVA (Ley 21.256)", None, 791, "+"),
    ("23", "TOTAL DÉBITOS", None, 538, "="),
]

CREDITOS_SIN_DERECHO = [
    ("25", "Internas Afectas", 564, 521, ""),
    ("26", "Importaciones", 566, 560, ""),
    ("27", "Internas exentas, o no gravadas", 584, 562, ""),
]

CREDITOS_CON_DERECHO = [
    ("28", "Facturas recibidas del giro y Facturas de compras emitidas", 519, 520, "+"),
    ("29", "Facturas recibidas de Proveedores: Supermercados y Comercios similares (Ley Nº20.780)", 761, 762, "+"),
    ("30", "Facturas recibidas por Adquisición o Construcción de Bienes Inmuebles (Ley Nº20.780)", 765, 766, "+"),
    ("31", "Facturas activo fijo", 524, 525, "+"),
    ("32", "Notas de Crédito recibidas y NC emitidas por retención de cambio de sujeto", 527, 528, "-"),
    ("33", "Notas de Débito recibidas y ND emitidas por retención de cambio de sujeto", 531, 532, "+"),
]

CREDITOS_IMPORTACIONES = [
    ("34", "Declaraciones de Ingreso (DIN) importaciones del giro", 534, 535, "+"),
    ("35", "Declaraciones de Ingreso (DIN) importaciones activo fijo", 536, 553, "+"),
]

CREDITOS_REMANENTE = [
    ("36", "Remanente Crédito Fiscal mes anterior", None, 504, "+"),
    ("37", "Devolución Solicitud Art.36 (Exportadores)", None, 593, "-"),
    ("38", "Devolución Solicitud Art.27 bis (Activo fijo)", None, 594, "-"),
    ("39", "Certificado Imputación Art.27 bis (Activo fijo)", None, 592, "-"),
    ("40", "Devolución Solicitud Art.3 (Cambio de sujeto)", None, 539, "-"),
    ("41", "Devolución Solicitud Ley Nº 20.258 (Generadoras Eléctricas)", None, 718, "-"),
    ("42", "Devolución Solicitud Reembolso Remanente de Crédito Fiscal IVA", None, 790, "-"),
    ("43", "Monto Reintegrado por Devolución Indebida de Crédito Fiscal D.S. 348 (Exportadores)", None, 164, "+"),
]

CREDITOS_OTROS = [
    ("46", "Crédito del Art.11 Ley 18.211 (Zona Franca de Extensión)", None, 523, "+"),
    ("47", "Crédito por Impuesto de Timbres y Estampillas, Art. 3º Ley Nº 20.259", None, 712, "+"),
    ("48", "Crédito por IVA restituido a aportantes sin domicilio ni residencia en Chile", None, 757, "+"),
    ("49", "TOTAL CRÉDITOS", None, 537, "="),
]

RETENCIONES = [
    ("59", "Retención Impuesto 1ra Categoría Art. 20 Nº2, según Art. 73 LIR", None, 50, "+"),
    ("60", "Retención Impuesto Único a los Trabajadores, según Art. 74 Nº1 LIR", None, 48, "+"),
    ("61", "Retención de Impuesto tasa 10% rentas Art. 42 Nº2, según Art. 74 Nº2 LIR", None, 151, "+"),
    ("62", "Retención de Impuesto tasa 10% rentas Art. 48, según Art. 74 Nº3 LIR", None, 153, "+"),
    ("63", "Retención 3% Art. 42 Nº1 (préstamo tasa 0%)", None, 49, "+"),
    ("64", "Retención 3% Art. 42 Nº2 (préstamo tasa 0%)", None, 155, "+"),
    ("65", "Retención a Suplementeros (tasa 0,5%)", None, 54, "+"),
    ("66", "Retención por compra de productos mineros", None, 56, "+"),
    ("67", "Retención seguros dotales (tasa 15%)", None, 588, "+"),
    ("68", "Retención APV retiros (tasa 15%)", None, 589, "+"),
]

CAMBIO_SUJETO_AGENTE = [
    ("118", "IVA total retenido a terceros (tasa Art.14 D.L. 825/74)", None, 39, "+"),
    ("119", "IVA parcial retenido a terceros (según tasa)", None, 554, "+"),
    ("120", "IVA Retenido por notas de crédito emitidas", None, 736, "-"),
    ("121", "Retención del margen de comercialización", None, 597, "+"),
    ("122", "Retención Anticipo de Cambio de Sujeto / Retención Cambio de Sujeto", None, 596, "+"),
]

TOTALES_FINAL = [
    ("147", "TOTAL A PAGAR DENTRO DEL PLAZO LEGAL", None, 91, "="),
    ("148", "Más IPC", None, 92, "+"),
    ("149", "Más Intereses y multas", None, 93, "+"),
    ("150", "TOTAL A PAGAR CON RECARGO", None, 94, "="),
]


# ============================================================
# Cálculo del F29
# ============================================================

def calcular_f29(datos):
    """
    Calcula códigos del F29.
    Si datos tiene "codigos", los usa directamente.
    Si no, calcula desde ventas/compras/documentos.
    """
    if "codigos" in datos:
        codigos = dict(datos["codigos"])
        # Asegurar que existan los códigos básicos
        codigos.setdefault(538, 0)
        codigos.setdefault(537, 0)
        codigos.setdefault(89, 0)
        codigos.setdefault(77, 0)
        codigos.setdefault(595, 0)
        codigos.setdefault(547, 0)
        codigos.setdefault(91, 0)
        codigos.setdefault(62, 0)
        return codigos

    # Cálculo desde datos desagregados (compatibilidad v2)
    v = datos.get("ventas", {})
    c = datos.get("compras", {})
    ret = datos.get("retenciones", {})
    ppm = datos.get("ppm", {})
    dev = datos.get("devoluciones", {})
    docs = datos.get("documentos", {})
    cs = datos.get("cambio_sujeto", {})

    IVA_TASA = 0.19
    codigos = {}

    def has_docs(lk):
        return lk in docs and len(docs[lk]) > 0

    def count_docs(lk):
        return len(docs.get(lk, []))

    def sum_field(lk, campo):
        return sum(d.get(campo, 0) for d in docs.get(lk, []))

    # === DÉBITOS ===
    for cq, ca, lk, fallback_cant, fallback_neto, is_iva in [
        (585, 20, "linea_1", "facturas_exportacion_cant", "facturas_exportacion_neto", False),
        (586, 142, "linea_2", "facturas_exentas_giro_cant", "facturas_exentas_giro_neto", False),
        (515, 587, "linea_5", "facturas_compra_digital_cant", "facturas_compra_digital_neto", False),
        (503, 502, "linea_7", "facturas_afectas_cant", "facturas_afectas_neto", True),
        (716, 717, "linea_9", "ventas_activo_fijo_cant", "ventas_activo_fijo_neto", True),
        (110, 111, "linea_10", "boletas_cant", "boletas_neto", True),
        (512, 513, "linea_12", "notas_debito_cant", "notas_debito_neto", True),
        (509, 510, "linea_13", "notas_credito_cant", "notas_credito_neto", True),
    ]:
        if has_docs(lk):
            codigos[cq] = count_docs(lk)
            if is_iva:
                iva_sum = sum_field(lk, "iva")
                codigos[ca] = iva_sum if iva_sum else int(sum_field(lk, "neto") * IVA_TASA)
            else:
                codigos[ca] = sum_field(lk, "neto")
        else:
            codigos[cq] = v.get(fallback_cant, c.get(fallback_cant, 0))
            if is_iva:
                codigos[ca] = int(v.get(fallback_neto, 0) * IVA_TASA)
            else:
                codigos[ca] = v.get(fallback_neto, c.get(fallback_neto, 0))

    codigos.setdefault(731, 0); codigos.setdefault(732, 0)
    codigos.setdefault(714, 0); codigos.setdefault(715, 0)
    codigos.setdefault(720, 0)
    codigos.setdefault(763, 0); codigos.setdefault(764, 0)
    codigos.setdefault(758, 0); codigos.setdefault(759, 0)
    codigos.setdefault(708, 0); codigos.setdefault(709, 0)
    codigos.setdefault(733, 0); codigos.setdefault(734, 0)
    codigos.setdefault(516, 0); codigos.setdefault(517, 0)
    codigos.setdefault(500, 0); codigos.setdefault(501, 0)
    codigos.setdefault(154, 0); codigos.setdefault(518, 0)
    codigos.setdefault(713, 0); codigos.setdefault(741, 0)
    codigos.setdefault(791, 0)

    total_debito = (
        codigos.get(502, 0) + codigos.get(764, 0) + codigos.get(717, 0)
        + codigos.get(111, 0) + codigos.get(759, 0)
        + codigos.get(513, 0) - codigos.get(510, 0)
        - codigos.get(709, 0) - codigos.get(734, 0)
        + codigos.get(517, 0) + codigos.get(501, 0)
        + codigos.get(154, 0) + codigos.get(518, 0)
        + codigos.get(713, 0) + codigos.get(741, 0) + codigos.get(791, 0)
    )
    codigos[538] = total_debito

    # === CRÉDITOS ===
    for cq, ca, lk, fallback_cant, fallback_iva in [
        (519, 520, "linea_28", "facturas_giro_cant", "facturas_giro_iva"),
        (524, 525, "linea_31", "facturas_activo_fijo_cant", "facturas_activo_fijo_iva"),
        (527, 528, "linea_32", "notas_credito_recibidas_cant", "notas_credito_recibidas_iva"),
        (531, 532, "linea_33", "notas_debito_recibidas_cant", "notas_debito_recibidas_iva"),
        (534, 535, "linea_34", "din_giro_cant", "din_giro_iva"),
        (536, 553, "linea_35", "din_activo_fijo_cant", "din_activo_fijo_iva"),
    ]:
        if has_docs(lk):
            codigos[cq] = count_docs(lk)
            codigos[ca] = sum_field(lk, "iva")
        else:
            codigos[cq] = c.get(fallback_cant, 0)
            codigos[ca] = c.get(fallback_iva, 0)

    codigos.setdefault(761, 0); codigos.setdefault(762, 0)
    codigos.setdefault(765, 0); codigos.setdefault(766, 0)
    codigos.setdefault(564, 0); codigos.setdefault(521, 0)
    codigos.setdefault(566, 0); codigos.setdefault(560, 0)
    codigos.setdefault(584, c.get("exentas_sin_derecho_cant", 0))
    codigos.setdefault(562, c.get("exentas_sin_derecho_neto", 0))

    codigos[511] = codigos.get(519, 0) + codigos.get(524, 0)
    codigos[514] = codigos.get(520, 0) + codigos.get(525, 0)

    codigos[504] = datos.get("remanente_anterior", 0)
    codigos[593] = dev.get("art_36_exportador", 0)
    codigos[594] = dev.get("art_27_bis", 0)
    codigos[592] = dev.get("certificado_27_bis", 0)
    codigos[539] = dev.get("cambio_sujeto", 0)
    codigos.setdefault(718, 0); codigos.setdefault(790, 0)
    codigos.setdefault(164, 0)
    codigos.setdefault(523, 0); codigos.setdefault(712, 0); codigos.setdefault(757, 0)

    total_credito = (
        codigos.get(520, 0) + codigos.get(762, 0) + codigos.get(766, 0)
        + codigos.get(525, 0)
        - codigos.get(528, 0) + codigos.get(532, 0)
        + codigos.get(535, 0) + codigos.get(553, 0)
        + codigos[504]
        - codigos[593] - codigos[594] - codigos[592] - codigos[539]
        - codigos.get(718, 0) - codigos.get(790, 0)
        + codigos.get(164, 0)
        + codigos.get(523, 0) + codigos.get(712, 0) + codigos.get(757, 0)
    )
    codigos[537] = total_credito

    # === IVA DETERMINADO ===
    if total_debito > total_credito:
        codigos[89] = total_debito - total_credito
        codigos[77] = 0
    else:
        codigos[89] = 0
        codigos[77] = total_credito - total_debito

    # === RETENCIONES ===
    codigos.setdefault(50, 0)
    if has_docs("linea_60"):
        codigos[48] = sum(d.get("iusc", d.get("iva", 0)) for d in docs["linea_60"])
    else:
        codigos[48] = ret.get("iusc_impuesto", 0)
    if has_docs("linea_61"):
        codigos[151] = sum(d.get("retencion", d.get("iva", 0)) for d in docs["linea_61"])
    else:
        codigos[151] = ret.get("honorarios_retencion", 0)
    codigos[153] = ret.get("directores_retencion", 0)
    for c_code in [49, 155, 54, 56, 588, 589]:
        codigos.setdefault(c_code, 0)

    # === PPM ===
    tasa_ppm = ppm.get("tasa", 0.25)
    codigos[115] = tasa_ppm
    codigos.setdefault(750, 0)
    codigos.setdefault(30, 0)

    if ppm.get("base_imponible") is not None:
        base_ppm = ppm["base_imponible"]
    else:
        def neto_linea(lk, fk):
            if has_docs(lk):
                return sum_field(lk, "neto")
            return v.get(fk, 0)
        base_ppm = (
            neto_linea("linea_7", "facturas_afectas_neto")
            + neto_linea("linea_2", "facturas_exentas_giro_neto")
            + neto_linea("linea_1", "facturas_exportacion_neto")
            + neto_linea("linea_10", "boletas_neto")
            + neto_linea("linea_12", "notas_debito_neto")
            - neto_linea("linea_13", "notas_credito_neto")
        )
    codigos[563] = base_ppm
    codigos[68] = 0

    if ppm.get("suspension", False):
        codigos[750] = 1
        codigos[62] = 0
    else:
        codigos[62] = int(base_ppm * tasa_ppm / 100)

    codigos[722] = ppm.get("remanente_sence_anterior", 0)
    codigos[721] = ppm.get("credito_sence", 0)
    sence_disponible = codigos[721] + codigos[722]
    codigos[723] = min(sence_disponible, codigos[62])
    codigos[724] = sence_disponible - codigos[723]

    ppm_neto = codigos[62] - codigos[723]

    # === SUB TOTAL (línea 80) ===
    codigos[595] = (
        codigos[89] + codigos.get(48, 0) + codigos.get(151, 0)
        + codigos.get(153, 0) + ppm_neto
    )

    # === CAMBIO DE SUJETO ===
    codigos[39] = cs.get("iva_retenido_total", cs.get(39, 0))
    codigos[554] = cs.get("iva_parcial_retenido", cs.get(554, 0))
    codigos[736] = cs.get("iva_retenido_nc", cs.get(736, 0))
    codigos[597] = cs.get("retencion_margen", cs.get(597, 0))
    codigos[596] = cs.get("retencion_neta", cs.get(596, 0))
    if codigos[596] == 0 and codigos[39] > 0:
        codigos[596] = codigos[39] + codigos.get(554, 0) - codigos[736] + codigos.get(597, 0)

    # === TOTAL ===
    codigos[547] = codigos[595] + codigos.get(596, 0)
    codigos[91] = codigos[547]
    codigos[92] = 0
    codigos[93] = 0
    codigos[94] = codigos[91] + codigos[92] + codigos[93]

    return codigos


# ============================================================
# Hoja 1: Formulario F29
# ============================================================

def _write_f29(wb, codigos, enc):
    """Hoja 1: Formulario F29 con estilo SII."""
    mes = enc.get("periodo_mes", 1)
    anio = enc.get("periodo_anio", 2026)
    nombre_mes = MESES.get(mes, str(mes))

    ws = wb.active
    ws.title = f"F29 — {nombre_mes} {anio}"

    # Anchos de columna
    ws.column_dimensions["A"].width = 5     # Línea
    ws.column_dimensions["B"].width = 72    # Descripción
    ws.column_dimensions["C"].width = 6     # Código cant
    ws.column_dimensions["D"].width = 12    # Cantidad
    ws.column_dimensions["E"].width = 6     # Código monto
    ws.column_dimensions["F"].width = 18    # Monto
    ws.column_dimensions["G"].width = 3     # Operador

    r = 1

    # === ENCABEZADO ===
    r = _section(ws, r, "Impuestos Mensuales", F10B)

    # Periodo / RUT / Folio
    _c(ws, r, 1, "", F7, FILL_BLUE, AC)
    _c(ws, r, 2, "Periodo Tributario", F8B, FILL_BLUE, AC)
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)
    _c(ws, r, 3, "Rol Único Tributario", F8B, FILL_BLUE, AC)
    ws.cell(row=r, column=4).fill = FILL_BLUE
    ws.cell(row=r, column=4).border = BORDER
    ws.merge_cells(start_row=r, start_column=5, end_row=r, end_column=6)
    _c(ws, r, 5, "Folio", F8B, FILL_BLUE, AC)
    ws.cell(row=r, column=6).fill = FILL_BLUE
    ws.cell(row=r, column=6).border = BORDER
    _c(ws, r, 7, "", F7, FILL_BLUE, AC)
    r += 1

    _c(ws, r, 1, "", F7, FILL_WHITE, AC)
    _c(ws, r, 2, f"Mes: {mes}  —  Año: {anio}", F8, FILL_LGRAY, AC)
    ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=4)
    _c(ws, r, 3, enc.get("rut", ""), F8, FILL_LGRAY, AC)
    ws.cell(row=r, column=4).fill = FILL_LGRAY
    ws.cell(row=r, column=4).border = BORDER
    ws.merge_cells(start_row=r, start_column=5, end_row=r, end_column=6)
    _c(ws, r, 5, enc.get("folio", ""), F8, FILL_LGRAY, AC)
    ws.cell(row=r, column=6).fill = FILL_LGRAY
    ws.cell(row=r, column=6).border = BORDER
    _c(ws, r, 7, "", F7, FILL_WHITE, AC)
    r += 1

    r = _section(ws, r, f"Razón Social: {enc.get('razon_social', '')}", F8B)
    r += 0  # no extra space

    # === DÉBITOS Y VENTAS ===
    r = _section(ws, r, "DÉBITOS y VENTAS")
    r = _section(ws, r, "Ventas y/o Servicios Prestados", F8B)
    r = _section(ws, r, "INFORMACIÓN DE INGRESOS", F8B)
    r = _colhdr(ws, r, "Cantidad de documentos", "Monto Neto")

    for num, desc, cq, ca, op in DEBITOS_INFO:
        cv = codigos.get(cq) if cq else None
        av = codigos.get(ca) if ca else None
        r = _line(ws, r, num, desc, cq, cv, ca, av, op)

    r = _section(ws, r, "Genera Débito", F8B)
    r = _colhdr(ws, r, "Cantidad de documentos", "Débitos")

    for num, desc, cq, ca, op in DEBITOS_GENERA:
        cv = codigos.get(cq) if cq else None
        av = codigos.get(ca) if ca else None
        is_total = (num == "23")
        r = _line(ws, r, num, desc, cq, cv, ca, av, op, total=is_total)

    # === CRÉDITOS Y COMPRAS ===
    r = _section(ws, r, "CRÉDITOS Y COMPRAS")
    r = _section(ws, r, "COMPRAS Y/O SERVICIOS UTILIZADOS", F8B)

    # Línea 24 informativa
    r = _colhdr(ws, r, "Con derecho a Crédito", "Sin derecho a Crédito")
    r = _line(ws, r, "24", "IVA por documentos electrónicos recibidos",
              511, codigos.get(511), 514, codigos.get(514), "")

    # Sin derecho a CF
    r = _section(ws, r, "SIN DERECHO A CRÉDITO FISCAL", F8B)
    r = _colhdr(ws, r, "Cantidad de documentos", "Monto Neto")
    for num, desc, cq, ca, op in CREDITOS_SIN_DERECHO:
        cv = codigos.get(cq) if cq else None
        av = codigos.get(ca) if ca else None
        r = _line(ws, r, num, desc, cq, cv, ca, av, op)

    # Con derecho a CF - Internas
    r = _section(ws, r, "CON DERECHO A CRÉDITO FISCAL — INTERNAS", F8B)
    r = _colhdr(ws, r, "Cantidad de documentos", "Crédito, Recuperación y Reintegro")
    for num, desc, cq, ca, op in CREDITOS_CON_DERECHO:
        cv = codigos.get(cq) if cq else None
        av = codigos.get(ca) if ca else None
        r = _line(ws, r, num, desc, cq, cv, ca, av, op)

    # Importaciones
    r = _section(ws, r, "IMPORTACIONES", F8B)
    for num, desc, cq, ca, op in CREDITOS_IMPORTACIONES:
        cv = codigos.get(cq) if cq else None
        av = codigos.get(ca) if ca else None
        r = _line(ws, r, num, desc, cq, cv, ca, av, op)

    # Remanente y devoluciones
    for num, desc, cq, ca, op in CREDITOS_REMANENTE:
        cv = codigos.get(cq) if cq else None
        av = codigos.get(ca) if ca else None
        r = _line(ws, r, num, desc, cq, cv, ca, av, op)

    # Otros créditos
    for num, desc, cq, ca, op in CREDITOS_OTROS:
        cv = codigos.get(cq) if cq else None
        av = codigos.get(ca) if ca else None
        is_total = (num == "49")
        r = _line(ws, r, num, desc, cq, cv, ca, av, op, total=is_total)

    # === POSTERGACIÓN DE IVA / IVA DETERMINADO ===
    r = _section(ws, r, "POSTERGACIÓN DE IVA (Ley 20.780) — IMPUESTO DETERMINADO", F8B)
    rem77 = codigos.get(77, 0)
    iva89 = codigos.get(89, 0)
    if rem77 > 0:
        r = _line(ws, r, "50", f"Remanente de crédito fiscal para el período siguiente",
                  None, None, 77, rem77, "")
    if iva89 > 0:
        r = _line(ws, r, "50", f"IVA determinado",
                  None, None, 89, iva89, "+", total=True)
    if rem77 == 0 and iva89 == 0:
        r = _line(ws, r, "50", "Sin IVA determinado ni remanente", None, None, 89, 0, "+")

    # === RETENCIONES ===
    r = _section(ws, r, "IMPUESTO A LA RENTA D.L. 824/74")
    r = _section(ws, r, "RETENCIONES", F8B)
    for num, desc, cq, ca, op in RETENCIONES:
        cv = codigos.get(cq) if cq else None
        av = codigos.get(ca) if ca else None
        r = _line(ws, r, num, desc, cq, cv, ca, av, op)

    # === PPM ===
    r = _section(ws, r, "PPM", F8B)
    base = codigos.get(563, 0)
    tasa = codigos.get(115, 0)
    ppm_val = codigos.get(62, 0)
    ppm_desc = f"1ra Categoría Art. 84 a)  |  Base Imponible: {fmt(base)}  |  Tasa: {tasa}%"
    r = _line(ws, r, "69", ppm_desc, None, None, 62, ppm_val, "+")

    # Crédito SENCE
    sence = codigos.get(723, 0)
    if sence > 0:
        r = _line(ws, r, "75", "Crédito Capacitación a Imputar", None, None, 723, sence, "-")

    # SUB TOTAL
    r = _line(ws, r, "80",
              "SUB TOTAL IMPUESTO DETERMINADO ANVERSO (Suma líneas 49 a 64)",
              None, None, 595, codigos.get(595, 0), "=", total=True)

    # === CAMBIO DE SUJETO ===
    cs_total = codigos.get(596, 0)
    if cs_total > 0 or codigos.get(39, 0) > 0:
        r = _section(ws, r, "CAMBIO DE SUJETO D.L. 825")
        r = _section(ws, r, "CAMBIO DE SUJETO (AGENTE RETENEDOR)", F8B)
        for num, desc, cq, ca, op in CAMBIO_SUJETO_AGENTE:
            cv = codigos.get(cq) if cq else None
            av = codigos.get(ca) if ca else None
            is_total = (num == "122")
            r = _line(ws, r, num, desc, cq, cv, ca, av, op, total=is_total)

    # === TOTAL DETERMINADO ===
    r = _line(ws, r, "140", "Total Determinado", None, None, 547,
              codigos.get(547, 0), "=", total=True)

    # === TOTAL A PAGAR ===
    for num, desc, cq, ca, op in TOTALES_FINAL:
        cv = codigos.get(cq) if cq else None
        av = codigos.get(ca) if ca else None
        is_total = (num in ("147", "150"))
        r = _line(ws, r, num, desc, cq, cv, ca, av, op, total=is_total)


# ============================================================
# Hoja 2: Detalle de documentos
# ============================================================

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
    "linea_28": {"linea": "28", "codigo": "519/520", "nombre": "Facturas Recibidas del Giro + FC Emitidas", "seccion": "credito"},
    "linea_29": {"linea": "29", "codigo": "761/762", "nombre": "Facturas Supermercados/Comercios", "seccion": "credito"},
    "linea_31": {"linea": "31", "codigo": "524/525", "nombre": "Facturas Activo Fijo", "seccion": "credito"},
    "linea_32": {"linea": "32", "codigo": "527/528", "nombre": "Notas de Crédito Recibidas", "seccion": "credito"},
    "linea_33": {"linea": "33", "codigo": "531/532", "nombre": "Notas de Débito Recibidas", "seccion": "credito"},
    "linea_60": {"linea": "60", "codigo": "48",      "nombre": "Impuesto Único 2da Categoría (Sueldos)", "seccion": "retencion"},
    "linea_61": {"linea": "61", "codigo": "151",     "nombre": "Retención Honorarios Art. 42 N°2", "seccion": "retencion"},
}

COLUMNAS_VENTAS = ["N° Doc", "Fecha", "RUT", "Razón Social", "Descripción", "Neto", "IVA", "Exento", "Total"]
COLUMNAS_COMPRAS = ["N° Doc", "Fecha", "RUT", "Razón Social", "Descripción", "Neto", "IVA", "Total"]
COLUMNAS_HONORARIOS = ["N° Boleta", "Fecha", "RUT", "Razón Social", "Descripción", "Bruto", "Retención", "Líquido"]
COLUMNAS_SUELDOS = ["N° Liquidación", "Fecha", "RUT", "Nombre", "Cargo", "Sueldo Bruto", "IUSC", "Líquido"]


def _get_columnas(seccion, lk):
    if lk == "linea_61":
        return COLUMNAS_HONORARIOS
    elif lk == "linea_60":
        return COLUMNAS_SUELDOS
    elif seccion == "debito":
        return COLUMNAS_VENTAS
    else:
        return COLUMNAS_COMPRAS


def _get_doc_values(doc, seccion, lk):
    if lk == "linea_61":
        return [doc.get("numero", ""), doc.get("fecha", ""), doc.get("rut", ""),
                doc.get("razon_social", ""), doc.get("descripcion", ""),
                doc.get("bruto", doc.get("neto", 0)), doc.get("retencion", doc.get("iva", 0)),
                doc.get("liquido", doc.get("total", 0))]
    elif lk == "linea_60":
        return [doc.get("numero", ""), doc.get("fecha", ""), doc.get("rut", ""),
                doc.get("razon_social", doc.get("nombre", "")),
                doc.get("cargo", doc.get("descripcion", "")),
                doc.get("bruto", doc.get("neto", 0)), doc.get("iusc", doc.get("iva", 0)),
                doc.get("liquido", doc.get("total", 0))]
    elif seccion == "debito":
        return [doc.get("numero", ""), doc.get("fecha", ""), doc.get("rut", ""),
                doc.get("razon_social", ""), doc.get("descripcion", ""),
                doc.get("neto", 0), doc.get("iva", 0), doc.get("exento", 0),
                doc.get("total", 0)]
    else:
        return [doc.get("numero", ""), doc.get("fecha", ""), doc.get("rut", ""),
                doc.get("razon_social", ""), doc.get("descripcion", ""),
                doc.get("neto", 0), doc.get("iva", 0), doc.get("total", 0)]


def _write_detalle(wb, datos):
    """Hoja 2: Detalle de documentos por línea."""
    docs = datos.get("documentos", {})
    if not docs:
        ws = wb.create_sheet(title="Detalle Documentos")
        _c(ws, 1, 1, "Sin documentos individuales. Se usaron totales agregados.", F8B, FILL_WHITE, AL)
        return

    ws = wb.create_sheet(title="Detalle Documentos")
    for i, w in enumerate([4, 14, 12, 20, 30, 30, 14, 14, 14, 14], 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    r = 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=10)
    cell = ws.cell(row=r, column=1, value="DETALLE DE DOCUMENTOS POR LÍNEA DEL F29")
    cell.font = F10B
    cell.fill = FILL_BLUE
    cell.alignment = AC
    for c in range(1, 11):
        ws.cell(row=r, column=c).fill = FILL_BLUE
        ws.cell(row=r, column=c).border = BORDER
    r += 2

    orden = [
        "linea_1", "linea_2", "linea_5", "linea_7", "linea_9",
        "linea_10", "linea_11", "linea_12", "linea_13",
        "linea_28", "linea_29", "linea_31", "linea_32", "linea_33",
        "linea_60", "linea_61",
    ]

    for lk in orden:
        if lk not in docs or not docs[lk]:
            continue

        info = LINEAS_INFO.get(lk, {})
        seccion = info.get("seccion", "")
        doc_list = docs[lk]
        columnas = _get_columnas(seccion, lk)

        # Header de sección
        header = (
            f"LÍNEA {info.get('linea', '?')} — "
            f"{info.get('nombre', lk)} — "
            f"Cód. {info.get('codigo', '?')} — "
            f"{len(doc_list)} documento(s)"
        )
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=10)
        cell = ws.cell(row=r, column=1, value=header)
        color = {"debito": "E65100", "credito": "2E7D32", "retencion": "1565C0"}.get(seccion, "333333")
        fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
        font_w = Font(name="Arial", size=9, bold=True, color=WHITE)
        for c in range(1, 11):
            ws.cell(row=r, column=c).fill = fill
            ws.cell(row=r, column=c).font = font_w
            ws.cell(row=r, column=c).border = BORDER
        r += 1

        # Column headers
        _c(ws, r, 1, "#", F7B, FILL_GRAY, AC)
        for ci, cn in enumerate(columnas, 2):
            _c(ws, r, ci, cn, F7B, FILL_GRAY, AC)
        r += 1

        # Data rows
        n_text = 5
        totals = {}
        for i, doc in enumerate(doc_list, 1):
            values = _get_doc_values(doc, seccion, lk)
            _c(ws, r, 1, i, F7, FILL_WHITE, AC)
            alt = FILL_LGRAY if i % 2 == 0 else FILL_WHITE
            ws.cell(row=r, column=1).fill = alt

            for ci, val in enumerate(values, 2):
                cell = ws.cell(row=r, column=ci)
                cell.border = BORDER
                cell.fill = alt
                is_monto = ci - 2 >= n_text
                if is_monto and isinstance(val, (int, float)):
                    cell.value = formato_peso(val)
                    cell.font = F7
                    cell.alignment = AR
                    col_name = columnas[ci - 2]
                    totals[col_name] = totals.get(col_name, 0) + val
                else:
                    cell.value = val
                    cell.font = F7
                    cell.alignment = AL
            r += 1

        # Total row
        _c(ws, r, 1, "", F7B, FILL_GRAY, AC)
        _c(ws, r, 2, "TOTAL", F7B, FILL_GRAY, AL)
        for ci, cn in enumerate(columnas, 2):
            cell = ws.cell(row=r, column=ci)
            cell.fill = FILL_GRAY
            cell.border = BORDER
            if cn in totals:
                cell.value = formato_peso(totals[cn])
                cell.font = Font(name="Arial", size=7, bold=True, color="CC0000")
                cell.alignment = AR
            else:
                cell.font = F7B
        r += 2


# ============================================================
# Hoja 3: Alertas
# ============================================================

def _write_alertas(wb, codigos, datos):
    """Hoja 3: Alertas y notas."""
    enc = datos.get("encabezado", {})
    notas = datos.get("notas", [])

    ws = wb.create_sheet(title="Alertas y Notas")
    ws.column_dimensions["A"].width = 16
    ws.column_dimensions["B"].width = 80

    r = 1
    _c(ws, r, 1, "ALERTAS Y VALIDACIONES", F10B, FILL_BLUE, AL)
    _c(ws, r, 2, "", F10B, FILL_BLUE, AL)
    r += 2

    alertas = []

    if codigos.get(77, 0) > 0 and codigos.get(538, 0) > 0:
        ratio = codigos[77] / max(codigos[538], 1)
        if ratio > 3:
            alertas.append(("REMANENTE",
                f"Remanente CF ({formato_peso(codigos[77])}) muy superior al débito. "
                "Considerar devolución Art. 36 o Art. 27 bis."))

    if codigos.get(585, 0) > 0:
        alertas.append(("EXPORTACIÓN",
            f"{codigos[585]} facturas de exportación ({formato_peso(codigos[20])} neto). "
            "Verificar calificación Aduanas."))

    if codigos.get(596, 0) > 0:
        alertas.append(("CAMBIO SUJETO",
            f"Retención cambio de sujeto: {formato_peso(codigos[596])}. "
            "Corresponde a IVA retenido por FC de servicios digitales extranjeros."))

    if codigos.get(151, 0) > 0:
        alertas.append(("HONORARIOS",
            f"Retención: {formato_peso(codigos[151])}. Tasa 2026: 15,25%."))

    if codigos.get(504, 0) > 0:
        alertas.append(("REMANENTE ANT.",
            f"Remanente CF arrastrado: {formato_peso(codigos[504])}. "
            "Verificar vs código 77 del F29 anterior."))

    has_afectas = codigos.get(503, 0) > 0 or codigos.get(110, 0) > 0
    has_exentas = codigos.get(585, 0) > 0 or codigos.get(586, 0) > 0
    if has_afectas and has_exentas:
        alertas.append(("PRORRATEO",
            "Ventas afectas + exentas/exportación. Verificar prorrateo de CF de uso común."))

    # Notas adicionales pasadas por el usuario
    for nota in notas:
        if isinstance(nota, tuple) and len(nota) == 2:
            alertas.append(nota)
        elif isinstance(nota, str):
            alertas.append(("NOTA", nota))

    mes = enc.get("periodo_mes", 1)
    anio = enc.get("periodo_anio", 2026)
    sig_mes = mes % 12 + 1
    sig_anio = anio if mes < 12 else anio + 1
    alertas.append(("PLAZO",
        f"Declarar antes del 20 de {MESES.get(sig_mes, '')} {sig_anio} (internet)."))

    alertas.append(("DISCLAIMER",
        "Herramienta de apoyo administrativo. NO es asesoría tributaria. "
        "Debe ser revisado por un contador antes de presentarse al SII."))

    fill_warn = PatternFill(start_color="FCE4EC", end_color="FCE4EC", fill_type="solid")
    for tipo, msg in alertas:
        c1 = _c(ws, r, 1, tipo, F8B, FILL_WHITE, AL)
        c2 = _c(ws, r, 2, msg, F7, FILL_WHITE, Alignment(wrap_text=True, vertical="top"))
        if tipo in ("REMANENTE", "PRORRATEO"):
            c1.fill = fill_warn
            c2.fill = fill_warn
        r += 1


# ============================================================
# Función principal
# ============================================================

def generar_f29_excel(datos, output_path):
    """
    Genera Excel del F29 con 3 hojas:
        1. F29 formulario (estilo SII)
        2. Detalle de documentos por línea
        3. Alertas y notas

    datos puede incluir:
        - "codigos": dict {código_f29: valor} para usar valores directos
        - O la estructura tradicional (ventas, compras, documentos, etc.)
        - "encabezado": {rut, razon_social, periodo_mes, periodo_anio, folio}
        - "documentos": {linea_7: [...], linea_28: [...], ...}
        - "notas": [(tipo, mensaje), ...] para alertas adicionales
    """
    codigos = calcular_f29(datos)
    enc = datos.get("encabezado", {})

    wb = openpyxl.Workbook()
    _write_f29(wb, codigos, enc)
    _write_detalle(wb, datos)
    _write_alertas(wb, codigos, datos)

    wb.save(output_path)
    return codigos


# ============================================================
# CLI / Testing
# ============================================================
if __name__ == "__main__":
    # Ejemplo: F29 con códigos pre-calculados
    datos_ejemplo = {
        "encabezado": {
            "rut": "78.033.706-0",
            "razon_social": "TOTOMENU SPA",
            "periodo_mes": 12,
            "periodo_anio": 2025,
            "folio": "8740690436",
        },
        "codigos": {
            503: 14, 502: 2541111,
            538: 2541111,
            511: 2074, 514: 0,
            584: 4, 562: 452579,
            519: 32, 520: 497664,
            527: 1, 528: 2934,
            537: 494730,
            77: 0, 89: 2046381,
            48: 0, 151: 0, 153: 0,
            563: 13374273, 115: 2.5, 62: 334357,
            595: 2380738,
            39: 495590, 736: 2934, 596: 492656,
            547: 2873394,
            91: 2873394, 92: 0, 93: 0, 94: 2873394,
        },
    }

    output = "f29_diciembre_2025_test.xlsx"
    codigos = generar_f29_excel(datos_ejemplo, output)
    print(f"F29 generado: {output}")
    print(f"  Débito (538): {formato_peso(codigos.get(538, 0))}")
    print(f"  Crédito (537): {formato_peso(codigos.get(537, 0))}")
    print(f"  IVA det (89): {formato_peso(codigos.get(89, 0))}")
    print(f"  PPM (62): {formato_peso(codigos.get(62, 0))}")
    print(f"  CS (596): {formato_peso(codigos.get(596, 0))}")
    print(f"  Total (91): {formato_peso(codigos.get(91, 0))}")
