"""
generar_f29.py — Genera un archivo Excel con el Formulario 29 completo.

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
# Colores y estilos del SII
# ============================================================
AZUL_SII = "1F3864"
AZUL_CLARO = "D6E4F0"
AMARILLO_INPUT = "FFF2CC"
VERDE_CALCULO = "E2EFDA"
GRIS_HEADER = "D9D9D9"
ROJO_ALERTA = "FCE4EC"
BLANCO = "FFFFFF"

FONT_HEADER = Font(name="Arial", size=12, bold=True, color=BLANCO)
FONT_SECTION = Font(name="Arial", size=10, bold=True, color=AZUL_SII)
FONT_NORMAL = Font(name="Arial", size=9, color="333333")
FONT_CODE = Font(name="Arial", size=9, bold=True, color=AZUL_SII)
FONT_TOTAL = Font(name="Arial", size=10, bold=True, color="CC0000")
FONT_SMALL = Font(name="Arial", size=8, color="666666")

FILL_HEADER = PatternFill(start_color=AZUL_SII, end_color=AZUL_SII, fill_type="solid")
FILL_SECTION = PatternFill(start_color=AZUL_CLARO, end_color=AZUL_CLARO, fill_type="solid")
FILL_INPUT = PatternFill(start_color=AMARILLO_INPUT, end_color=AMARILLO_INPUT, fill_type="solid")
FILL_CALC = PatternFill(start_color=VERDE_CALCULO, end_color=VERDE_CALCULO, fill_type="solid")
FILL_TOTAL = PatternFill(start_color=GRIS_HEADER, end_color=GRIS_HEADER, fill_type="solid")
FILL_ALERTA = PatternFill(start_color=ROJO_ALERTA, end_color=ROJO_ALERTA, fill_type="solid")

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


def calcular_f29(datos):
    """
    Calcula todos los códigos del F29 a partir de los datos de entrada.

    Parámetros:
        datos (dict): Diccionario con los datos del contribuyente y período.

    Estructura esperada de `datos`:
    {
        "encabezado": {
            "rut": "76.123.456-7",
            "razon_social": "Mi Empresa SpA",
            "periodo_mes": 1,        # 1-12
            "periodo_anio": 2026,
            "regimen": "pro_pyme_general",  # pro_pyme_transparente | pro_pyme_general | semi_integrado
        },
        "ventas": {
            "facturas_afectas_cant": 15,
            "facturas_afectas_neto": 25000000,      # Monto neto (sin IVA)
            "notas_credito_cant": 1,
            "notas_credito_neto": 500000,
            "notas_debito_cant": 0,
            "notas_debito_neto": 0,
            "facturas_exportacion_cant": 3,
            "facturas_exportacion_neto": 18000000,   # En pesos
            "facturas_exentas_giro_cant": 0,
            "facturas_exentas_giro_neto": 0,
            "boletas_cant": 0,
            "boletas_neto": 0,
            "ventas_activo_fijo_cant": 0,
            "ventas_activo_fijo_neto": 0,
        },
        "compras": {
            "facturas_giro_cant": 22,
            "facturas_giro_iva": 1200000,            # IVA total de facturas recibidas
            "facturas_activo_fijo_cant": 1,
            "facturas_activo_fijo_iva": 380000,
            "notas_credito_recibidas_cant": 0,
            "notas_credito_recibidas_iva": 0,
            "notas_debito_recibidas_cant": 0,
            "notas_debito_recibidas_iva": 0,
            "facturas_compra_digital_cant": 2,       # AWS, Azure, etc.
            "facturas_compra_digital_neto": 800000,
            "din_giro_cant": 0,
            "din_giro_iva": 0,
            "din_activo_fijo_cant": 0,
            "din_activo_fijo_iva": 0,
            "compras_sin_credito_cant": 0,
            "compras_sin_credito_neto": 0,
        },
        "remanente_anterior": 0,       # Código 504/77 del F29 anterior
        "devoluciones": {
            "art_36_exportador": 0,     # Código 593
            "art_27_bis": 0,            # Código 594
            "certificado_27_bis": 0,    # Código 592
            "cambio_sujeto": 0,         # Código 539
        },
        "retenciones": {
            "iusc_impuesto": 350000,    # Código 48: Impuesto Único 2da Cat. neto
            "honorarios_retencion": 760000,  # Código 151: total retención boletas honorarios
            "directores_retencion": 0,  # Código 153
        },
        "ppm": {
            "tasa": 0.25,              # Tasa PPM en % (ej: 0.25 para Pro Pyme General)
            "base_imponible": None,     # Si None, se calcula automáticamente
            "credito_sence": 0,         # Código 723
            "remanente_sence_anterior": 0,  # Código 722
            "suspension": False,        # True si PPM está suspendido por pérdida
        },
    }

    Retorna:
        dict con todos los códigos calculados del F29.
    """
    v = datos.get("ventas", {})
    c = datos.get("compras", {})
    ret = datos.get("retenciones", {})
    ppm = datos.get("ppm", {})
    dev = datos.get("devoluciones", {})
    enc = datos.get("encabezado", {})

    IVA_TASA = 0.19
    codigos = {}

    # === DÉBITOS ===
    # Líneas informativas
    codigos[585] = v.get("facturas_exportacion_cant", 0)
    codigos[20] = v.get("facturas_exportacion_neto", 0)
    codigos[586] = v.get("facturas_exentas_giro_cant", 0)
    codigos[142] = v.get("facturas_exentas_giro_neto", 0)
    codigos[515] = c.get("facturas_compra_digital_cant", 0)
    codigos[587] = c.get("facturas_compra_digital_neto", 0)

    # Líneas generadoras de débito
    codigos[503] = v.get("facturas_afectas_cant", 0)
    codigos[502] = int(v.get("facturas_afectas_neto", 0) * IVA_TASA)

    codigos[716] = v.get("ventas_activo_fijo_cant", 0)
    codigos[717] = int(v.get("ventas_activo_fijo_neto", 0) * IVA_TASA)

    codigos[110] = v.get("boletas_cant", 0)
    codigos[111] = int(v.get("boletas_neto", 0) * IVA_TASA)

    codigos[512] = v.get("notas_debito_cant", 0)
    codigos[513] = int(v.get("notas_debito_neto", 0) * IVA_TASA)

    codigos[509] = v.get("notas_credito_cant", 0)
    codigos[510] = int(v.get("notas_credito_neto", 0) * IVA_TASA)

    # Total Débito (código 538)
    total_debito = (
        codigos[502]
        + codigos[717]
        + codigos[111]
        + codigos[513]
        - codigos[510]
    )
    codigos[538] = total_debito

    # === CRÉDITOS ===
    # Línea informativa
    codigos[511] = c.get("facturas_giro_cant", 0) + c.get("facturas_activo_fijo_cant", 0)
    codigos[514] = c.get("facturas_giro_iva", 0) + c.get("facturas_activo_fijo_iva", 0)
    codigos[564] = c.get("compras_sin_credito_cant", 0)
    codigos[521] = c.get("compras_sin_credito_neto", 0)

    # Líneas generadoras de crédito
    codigos[519] = c.get("facturas_giro_cant", 0)
    codigos[520] = c.get("facturas_giro_iva", 0)

    codigos[524] = c.get("facturas_activo_fijo_cant", 0)
    codigos[525] = c.get("facturas_activo_fijo_iva", 0)

    codigos[527] = c.get("notas_credito_recibidas_cant", 0)
    codigos[528] = c.get("notas_credito_recibidas_iva", 0)

    codigos[531] = c.get("notas_debito_recibidas_cant", 0)
    codigos[532] = c.get("notas_debito_recibidas_iva", 0)

    codigos[534] = c.get("din_giro_cant", 0)
    codigos[535] = c.get("din_giro_iva", 0)

    codigos[536] = c.get("din_activo_fijo_cant", 0)
    codigos[553] = c.get("din_activo_fijo_iva", 0)

    codigos[504] = datos.get("remanente_anterior", 0)

    codigos[593] = dev.get("art_36_exportador", 0)
    codigos[594] = dev.get("art_27_bis", 0)
    codigos[592] = dev.get("certificado_27_bis", 0)
    codigos[539] = dev.get("cambio_sujeto", 0)

    # IVA de facturas de compra digitales (débito y crédito simultáneo)
    iva_digital = int(c.get("facturas_compra_digital_neto", 0) * IVA_TASA)

    # Total Crédito (código 537)
    total_credito = (
        codigos[520]
        + codigos[525]
        - codigos[528]
        + codigos[532]
        + codigos[535]
        + codigos[553]
        + codigos[504]
        - codigos[593]
        - codigos[594]
        - codigos[592]
        - codigos[539]
        + iva_digital  # Crédito por facturas de compra a proveedores digitales
    )
    codigos[537] = total_credito

    # Si hay facturas de compra digitales, ajustar también el débito
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
    codigos[48] = ret.get("iusc_impuesto", 0)
    codigos[151] = ret.get("honorarios_retencion", 0)
    codigos[153] = ret.get("directores_retencion", 0)

    # === PPM ===
    tasa_ppm = ppm.get("tasa", 0.25)
    codigos[115] = tasa_ppm

    # Base imponible PPM = ingresos netos (afectos + exentos + exportaciones)
    if ppm.get("base_imponible") is not None:
        base_ppm = ppm["base_imponible"]
    else:
        base_ppm = (
            v.get("facturas_afectas_neto", 0)
            + v.get("facturas_exentas_giro_neto", 0)
            + v.get("facturas_exportacion_neto", 0)
            + v.get("boletas_neto", 0)
            + v.get("notas_debito_neto", 0)
            - v.get("notas_credito_neto", 0)
        )
    codigos[563] = base_ppm

    if ppm.get("suspension", False):
        codigos[750] = 1  # Marca de suspensión
        codigos[62] = 0
    else:
        codigos[750] = 0
        codigos[62] = int(base_ppm * tasa_ppm / 100)

    # Crédito SENCE
    codigos[722] = ppm.get("remanente_sence_anterior", 0)
    credito_sence_disponible = ppm.get("credito_sence", 0) + codigos[722]
    codigos[721] = ppm.get("credito_sence", 0)

    # SENCE se imputa hasta el monto del PPM
    sence_aplicado = min(credito_sence_disponible, codigos[62])
    codigos[723] = sence_aplicado
    codigos[724] = credito_sence_disponible - sence_aplicado

    # PPM neto después de SENCE
    ppm_neto = codigos[62] - codigos[723]

    # === TOTAL A PAGAR ===
    codigos[595] = (
        codigos[89]
        + codigos[48]
        + codigos[151]
        + codigos[153]
        + ppm_neto
    )
    codigos[91] = codigos[595]
    codigos[92] = 0  # IPC (solo si fuera de plazo)
    codigos[93] = 0  # Intereses y multas
    codigos[94] = codigos[91]

    return codigos


def generar_f29_excel(datos, output_path):
    """
    Genera el archivo Excel del F29 con 3 hojas.

    Parámetros:
        datos (dict): Datos del contribuyente (ver estructura en calcular_f29).
        output_path (str): Ruta del archivo Excel de salida.
    """
    codigos = calcular_f29(datos)
    enc = datos.get("encabezado", {})
    v = datos.get("ventas", {})
    c = datos.get("compras", {})
    ret = datos.get("retenciones", {})
    ppm_data = datos.get("ppm", {})

    mes = enc.get("periodo_mes", 1)
    anio = enc.get("periodo_anio", 2026)
    nombre_mes = MESES.get(mes, str(mes))

    wb = openpyxl.Workbook()

    # ============================================================
    # HOJA 1: Formulario F29
    # ============================================================
    ws = wb.active
    ws.title = f"F29 — {nombre_mes} {anio}"

    # Anchos de columna
    ws.column_dimensions["A"].width = 8    # Línea
    ws.column_dimensions["B"].width = 10   # Código
    ws.column_dimensions["C"].width = 48   # Descripción
    ws.column_dimensions["D"].width = 14   # Cantidad
    ws.column_dimensions["E"].width = 10   # Código monto
    ws.column_dimensions["F"].width = 20   # Monto

    row = 1

    # --- Encabezado ---
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    cell = ws.cell(row=row, column=1,
                   value="FORMULARIO 29 — DECLARACIÓN MENSUAL Y PAGO SIMULTÁNEO DE IMPUESTOS")
    cell.font = FONT_HEADER
    cell.fill = FILL_HEADER
    cell.alignment = ALIGN_CENTER
    for col in range(1, 7):
        ws.cell(row=row, column=col).fill = FILL_HEADER
    row += 1

    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
    cell = ws.cell(row=row, column=1,
                   value=f"Servicio de Impuestos Internos — Chile")
    cell.font = Font(name="Arial", size=9, italic=True, color=BLANCO)
    cell.fill = FILL_HEADER
    cell.alignment = ALIGN_CENTER
    for col in range(1, 7):
        ws.cell(row=row, column=col).fill = FILL_HEADER
    row += 2

    # --- Datos del contribuyente ---
    info_fields = [
        ("RUT:", enc.get("rut", "—")),
        ("Razón Social:", enc.get("razon_social", "—")),
        ("Período Tributario:", f"{mes:02d}-{anio}"),
        ("Régimen:", enc.get("regimen", "—").replace("_", " ").title()),
    ]
    for label, value in info_fields:
        ws.cell(row=row, column=1, value=label).font = FONT_CODE
        ws.merge_cells(start_row=row, start_column=2, end_row=row, end_column=3)
        ws.cell(row=row, column=2, value=value).font = FONT_NORMAL
        row += 1
    row += 1

    def write_section_header(ws, row, title):
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=6)
        cell = ws.cell(row=row, column=1, value=title)
        cell.font = FONT_SECTION
        cell.fill = FILL_SECTION
        cell.alignment = ALIGN_LEFT
        for col in range(1, 7):
            ws.cell(row=row, column=col).fill = FILL_SECTION
            ws.cell(row=row, column=col).border = BORDER_THIN
        return row + 1

    def write_column_headers(ws, row, headers):
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col_idx, value=header)
            cell.font = Font(name="Arial", size=8, bold=True, color="333333")
            cell.fill = PatternFill(start_color=GRIS_HEADER, end_color=GRIS_HEADER, fill_type="solid")
            cell.alignment = ALIGN_CENTER
            cell.border = BORDER_THIN
        return row + 1

    def write_data_row(ws, row, linea, cod_cant, descripcion, cantidad, cod_monto, monto,
                       is_total=False, is_calc=False, signo=""):
        fill = FILL_TOTAL if is_total else (FILL_CALC if is_calc else None)
        font_val = FONT_TOTAL if is_total else FONT_NORMAL

        cells_data = [
            (1, linea, FONT_CODE, ALIGN_CENTER),
            (2, cod_cant if cod_cant else "", FONT_SMALL, ALIGN_CENTER),
            (3, descripcion, font_val, ALIGN_LEFT),
            (4, cantidad if cantidad else "", FONT_NORMAL, ALIGN_RIGHT),
            (5, cod_monto if cod_monto else "", FONT_SMALL, ALIGN_CENTER),
            (6, formato_peso(monto) if monto is not None else "", font_val, ALIGN_RIGHT),
        ]
        for col, val, font, align in cells_data:
            cell = ws.cell(row=row, column=col, value=val)
            cell.font = font
            cell.alignment = align
            cell.border = BORDER_THIN
            if fill:
                cell.fill = fill
        return row + 1

    # === SECCIÓN DÉBITO FISCAL ===
    row = write_section_header(ws, row, "DÉBITO FISCAL — Ventas y Servicios (Líneas 1–23)")
    row = write_column_headers(ws, row,
        ["Línea", "Cód.", "Descripción", "Cantidad", "Cód.", "Monto ($)"])

    # Líneas informativas
    debito_rows = [
        ("1", "585", "Exportaciones (facturas exportación)", codigos[585], "20", codigos[20]),
        ("2", "586", "Ventas/servicios exentos del giro", codigos[586], "142", codigos[142]),
        ("5", "515", "Facturas de compra (serv. digitales extranjeros)", codigos[515], "587", codigos[587]),
        ("7", "503", "⭐ Facturas afectas del giro (IVA)", codigos[503], "502", codigos[502]),
        ("9", "716", "Facturas ventas activo fijo (no del giro)", codigos[716], "717", codigos[717]),
        ("10", "110", "Boletas", codigos[110], "111", codigos[111]),
        ("12", "512", "Notas de débito emitidas", codigos[512], "513", codigos[513]),
        ("13", "509", "(-) Notas de crédito emitidas", codigos[509], "510", -codigos[510] if codigos[510] else 0),
        ("23", "", "TOTAL DÉBITOS", "", "538", codigos[538]),
    ]
    for linea, cod_c, desc, cant, cod_m, monto in debito_rows:
        is_total = linea == "23"
        row = write_data_row(ws, row, linea, cod_c, desc, cant, cod_m, monto,
                            is_total=is_total, is_calc=(linea == "23"))
    row += 1

    # === SECCIÓN CRÉDITO FISCAL ===
    row = write_section_header(ws, row, "CRÉDITO FISCAL — Compras y Gastos (Líneas 24–49)")
    row = write_column_headers(ws, row,
        ["Línea", "Cód.", "Descripción", "Cantidad", "Cód.", "Monto ($)"])

    credito_rows = [
        ("24", "511", "[Info] IVA total DTE recibidos", codigos[511], "514", codigos[514]),
        ("25", "564", "[Info] Compras sin derecho a CF", codigos[564], "521", codigos[521]),
        ("28", "519", "⭐ Facturas recibidas del giro (IVA)", codigos[519], "520", codigos[520]),
        ("31", "524", "⭐ Facturas activo fijo (computadores, etc.)", codigos[524], "525", codigos[525]),
        ("32", "527", "(-) NC recibidas", codigos[527], "528", -codigos[528] if codigos[528] else 0),
        ("33", "531", "ND recibidas", codigos[531], "532", codigos[532]),
        ("34", "534", "DIN importaciones del giro", codigos[534], "535", codigos[535]),
        ("35", "536", "DIN importaciones activo fijo", codigos[536], "553", codigos[553]),
        ("36", "", "Remanente CF mes anterior", "", "504", codigos[504]),
        ("37", "", "(-) Devolución Art. 36 (exportador)", "", "593", -codigos[593] if codigos[593] else 0),
        ("38", "", "(-) Devolución Art. 27 bis", "", "594", -codigos[594] if codigos[594] else 0),
        ("49", "", "TOTAL CRÉDITOS", "", "537", codigos[537]),
    ]
    for linea, cod_c, desc, cant, cod_m, monto in credito_rows:
        is_total = linea == "49"
        row = write_data_row(ws, row, linea, cod_c, desc, cant, cod_m, monto,
                            is_total=is_total, is_calc=(linea == "49"))
    row += 1

    # === DETERMINACIÓN IVA ===
    row = write_section_header(ws, row, "DETERMINACIÓN DEL IVA (Línea 50)")
    row = write_column_headers(ws, row,
        ["Línea", "Cód.", "Descripción", "", "Cód.", "Monto ($)"])

    if codigos[89] > 0:
        row = write_data_row(ws, row, "50", "", "IVA DETERMINADO (a pagar)", "",
                            "89", codigos[89], is_calc=True)
    else:
        row = write_data_row(ws, row, "50", "", "REMANENTE CF (para mes siguiente)", "",
                            "77", codigos[77], is_calc=True)
    row += 1

    # === RETENCIONES ===
    row = write_section_header(ws, row, "RETENCIONES DE IMPUESTO A LA RENTA (Líneas 59–68)")
    row = write_column_headers(ws, row,
        ["Línea", "Cód.", "Descripción", "", "Cód.", "Monto ($)"])

    ret_rows = [
        ("60", "", "Impuesto Único 2da Categoría (sueldos)", "", "48", codigos[48]),
        ("61", "", "⭐ Retención honorarios Art. 42 N°2 (15,25%)", "", "151", codigos[151]),
        ("62", "", "Retención dietas directores S.A.", "", "153", codigos[153]),
    ]
    for linea, cod_c, desc, cant, cod_m, monto in ret_rows:
        row = write_data_row(ws, row, linea, cod_c, desc, cant, cod_m, monto)
    row += 1

    # === PPM ===
    row = write_section_header(ws, row, "PAGOS PROVISIONALES MENSUALES — PPM (Líneas 69–78)")
    row = write_column_headers(ws, row,
        ["Línea", "Cód.", "Descripción", "", "Cód.", "Monto ($)"])

    suspension_text = " [SUSPENDIDO]" if codigos.get(750, 0) == 1 else ""
    ppm_rows = [
        ("69", "563", f"Base imponible PPM{suspension_text}", "", "", codigos[563]),
        ("69", "115", f"Tasa PPM: {codigos[115]}%", "", "", None),
        ("69", "", f"PPM determinado", "", "62", codigos[62]),
        ("75", "723", "(-) Crédito SENCE aplicado", "", "", -codigos[723] if codigos[723] else 0),
        ("75", "724", "Remanente SENCE para siguiente período", "", "", codigos[724]),
    ]
    for linea, cod_c, desc, cant, cod_m, monto in ppm_rows:
        row = write_data_row(ws, row, linea, cod_c, desc, cant, cod_m, monto)
    row += 1

    # === TOTAL A PAGAR ===
    row = write_section_header(ws, row, "TOTAL A PAGAR (Líneas 141–144)")
    row = write_column_headers(ws, row,
        ["Línea", "Cód.", "Descripción", "", "Cód.", "Monto ($)"])

    total_rows = [
        ("80", "", "Subtotal impuesto determinado", "", "595", codigos[595]),
        ("141", "", "TOTAL A PAGAR EN PLAZO LEGAL", "", "91", codigos[91]),
        ("142", "", "Más IPC (reajuste fuera de plazo)", "", "92", codigos[92]),
        ("143", "", "Más intereses y multas", "", "93", codigos[93]),
        ("144", "", "TOTAL A PAGAR CON RECARGO", "", "94", codigos[94]),
    ]
    for linea, cod_c, desc, cant, cod_m, monto in total_rows:
        is_total = linea in ("141", "144")
        row = write_data_row(ws, row, linea, cod_c, desc, cant, cod_m, monto,
                            is_total=is_total, is_calc=is_total)

    # ============================================================
    # HOJA 2: Detalle de Cálculos
    # ============================================================
    ws2 = wb.create_sheet(title="Detalle de Cálculos")
    ws2.column_dimensions["A"].width = 45
    ws2.column_dimensions["B"].width = 20
    ws2.column_dimensions["C"].width = 50

    r = 1
    ws2.cell(row=r, column=1, value="DETALLE DE CÁLCULOS DEL F29").font = FONT_SECTION
    r += 2

    details = [
        ("DÉBITO FISCAL", ""),
        ("Facturas afectas: neto × 19%",
         f"{formato_peso(v.get('facturas_afectas_neto', 0))} × 19% = {formato_peso(codigos[502])}"),
        ("Notas de débito: neto × 19%",
         f"{formato_peso(v.get('notas_debito_neto', 0))} × 19% = {formato_peso(codigos[513])}"),
        ("Notas de crédito: neto × 19%",
         f"{formato_peso(v.get('notas_credito_neto', 0))} × 19% = {formato_peso(codigos[510])} (se resta)"),
        ("Total Débito (código 538)", formato_peso(codigos[538])),
        ("", ""),
        ("CRÉDITO FISCAL", ""),
        ("IVA facturas recibidas del giro (código 520)", formato_peso(codigos[520])),
        ("IVA facturas activo fijo (código 525)", formato_peso(codigos[525])),
        ("IVA facturas compra digital (efecto neutro)", formato_peso(int(c.get('facturas_compra_digital_neto', 0) * 0.19))),
        ("Remanente CF mes anterior (código 504)", formato_peso(codigos[504])),
        ("Total Crédito (código 537)", formato_peso(codigos[537])),
        ("", ""),
        ("DETERMINACIÓN IVA", ""),
        ("Débito − Crédito", f"{formato_peso(codigos[538])} − {formato_peso(codigos[537])}"),
        ("IVA a pagar (código 89)" if codigos[89] > 0 else "Remanente CF (código 77)",
         formato_peso(codigos[89]) if codigos[89] > 0 else formato_peso(codigos[77])),
        ("", ""),
        ("PPM", ""),
        ("Base imponible (código 563)", formato_peso(codigos[563])),
        ("Tasa (código 115)", f"{codigos[115]}%"),
        ("PPM determinado (código 62)", f"{formato_peso(codigos[563])} × {codigos[115]}% = {formato_peso(codigos[62])}"),
        ("Crédito SENCE aplicado (código 723)", formato_peso(codigos[723])),
        ("", ""),
        ("TOTAL", ""),
        ("IVA determinado", formato_peso(codigos[89])),
        ("+ IUSC (código 48)", formato_peso(codigos[48])),
        ("+ Retención honorarios (código 151)", formato_peso(codigos[151])),
        ("+ PPM neto (62 − 723)", formato_peso(codigos[62] - codigos[723])),
        ("= TOTAL A PAGAR (código 91)", formato_peso(codigos[91])),
    ]
    for desc, valor in details:
        ws2.cell(row=r, column=1, value=desc).font = FONT_SECTION if valor == "" and desc else FONT_NORMAL
        ws2.cell(row=r, column=2, value=valor).font = FONT_NORMAL
        r += 1

    # ============================================================
    # HOJA 3: Alertas y Notas
    # ============================================================
    ws3 = wb.create_sheet(title="Alertas y Notas")
    ws3.column_dimensions["A"].width = 12
    ws3.column_dimensions["B"].width = 70

    r = 1
    ws3.cell(row=r, column=1, value="ALERTAS Y VALIDACIONES").font = FONT_SECTION
    r += 2

    alertas = []

    # Validaciones
    if codigos[77] > 0 and codigos[77] > codigos[538] * 3:
        alertas.append(("⚠️ ATENCIÓN",
            f"El remanente de CF ({formato_peso(codigos[77])}) es muy superior al débito. "
            "Verificar que las compras sean del giro y considerar solicitar devolución Art. 36 (exportador) o Art. 27 bis (activo fijo)."))

    if codigos.get(585, 0) > 0:
        alertas.append(("📦 EXPORTACIÓN",
            f"Se registraron {codigos[585]} facturas de exportación por {formato_peso(codigos[20])} neto. "
            "Verificar que estén calificadas ante el Servicio Nacional de Aduanas. "
            "Si el monto supera USD 2.000, se requiere DUS a través de agente de aduanas."))

    if codigos.get(515, 0) > 0:
        alertas.append(("☁️ SERV. DIGITALES",
            f"Se registraron {codigos[515]} facturas de compra por servicios digitales extranjeros "
            f"(neto: {formato_peso(codigos[587])}). Verificar que se emitió Factura de Compra (tipo 46) "
            "y que el IVA retenido está registrado como débito Y crédito simultáneamente."))

    if codigos[151] > 0:
        alertas.append(("👤 HONORARIOS",
            f"Se declaró retención de honorarios por {formato_peso(codigos[151])}. "
            "Tasa vigente 2026: 15,25%. Verificar que coincide con las boletas de honorarios recibidas."))

    if codigos[504] > 0:
        alertas.append(("🔄 REMANENTE",
            f"Se arrastra un remanente de CF del mes anterior por {formato_peso(codigos[504])}. "
            "Verificar que coincide con el código 77 del F29 del período anterior."))

    if codigos[91] == 0 and codigos[89] == 0:
        alertas.append(("ℹ️ SIN PAGO IVA",
            "Esta declaración no genera pago de IVA (crédito ≥ débito). "
            "Verificar que sea correcto y no se hayan omitido facturas de venta."))

    if v.get("facturas_afectas_cant", 0) == 0 and v.get("facturas_exportacion_cant", 0) == 0:
        alertas.append(("⚠️ SIN VENTAS",
            "No se registraron facturas de venta (ni afectas ni de exportación). "
            "Si es correcto, considerar declarar sin movimiento. Si hay ventas, revisar los datos de entrada."))

    tasa = ppm_data.get("tasa", 0.25)
    regimen = enc.get("regimen", "")
    if "pro_pyme_transparente" in regimen and tasa != 0.20:
        alertas.append(("⚠️ TASA PPM",
            f"El régimen es Pro Pyme Transparente pero la tasa PPM es {tasa}% (debería ser 0,20%). Verificar."))
    elif "pro_pyme_general" in regimen and tasa != 0.25:
        alertas.append(("⚠️ TASA PPM",
            f"El régimen es Pro Pyme General pero la tasa PPM es {tasa}% (debería ser 0,25%). Verificar."))

    # Alerta de prorrateo
    if (v.get("facturas_afectas_cant", 0) > 0 and
        (v.get("facturas_exportacion_cant", 0) > 0 or v.get("facturas_exentas_giro_cant", 0) > 0)):
        alertas.append(("⚠️ PRORRATEO",
            "La empresa tiene ventas afectas Y exentas/exportación en el mismo período. "
            "Verificar que se aplicó correctamente el prorrateo de crédito fiscal "
            "(CF proporcional = CF total × ventas afectas / ventas totales)."))

    alertas.append(("📅 PLAZO",
        f"Plazo de declaración por internet: día 20 de {MESES.get(mes % 12 + 1 if mes < 12 else 1, '')} {anio if mes < 12 else anio + 1}. "
        "Si cae en feriado o fin de semana, se traslada al siguiente día hábil."))

    alertas.append(("📋 DISCLAIMER",
        "Este formulario fue generado como herramienta de apoyo. "
        "NO constituye asesoría tributaria. Debe ser revisado por un contador o asesor tributario "
        "antes de ser presentado al SII. Los cálculos se basan en la información proporcionada "
        "y pueden no contemplar todas las situaciones particulares del contribuyente."))

    for tipo, mensaje in alertas:
        cell_tipo = ws3.cell(row=r, column=1, value=tipo)
        cell_tipo.font = Font(name="Arial", size=9, bold=True)
        cell_msg = ws3.cell(row=r, column=2, value=mensaje)
        cell_msg.font = FONT_NORMAL
        cell_msg.alignment = Alignment(wrap_text=True, vertical="top")
        if "⚠️" in tipo:
            cell_tipo.fill = FILL_ALERTA
            cell_msg.fill = FILL_ALERTA
        r += 1

    # ============================================================
    # Guardar
    # ============================================================
    wb.save(output_path)
    return codigos


# ============================================================
# Ejecución directa para testing
# ============================================================
if __name__ == "__main__":
    # Datos de ejemplo: empresa de software Pro Pyme General
    datos_ejemplo = {
        "encabezado": {
            "rut": "76.123.456-7",
            "razon_social": "DevSoft SpA",
            "periodo_mes": 1,
            "periodo_anio": 2026,
            "regimen": "pro_pyme_general",
        },
        "ventas": {
            "facturas_afectas_cant": 8,
            "facturas_afectas_neto": 15000000,
            "notas_credito_cant": 1,
            "notas_credito_neto": 1000000,
            "notas_debito_cant": 0,
            "notas_debito_neto": 0,
            "facturas_exportacion_cant": 2,
            "facturas_exportacion_neto": 12000000,
            "facturas_exentas_giro_cant": 0,
            "facturas_exentas_giro_neto": 0,
            "boletas_cant": 0,
            "boletas_neto": 0,
            "ventas_activo_fijo_cant": 0,
            "ventas_activo_fijo_neto": 0,
        },
        "compras": {
            "facturas_giro_cant": 15,
            "facturas_giro_iva": 950000,
            "facturas_activo_fijo_cant": 1,
            "facturas_activo_fijo_iva": 285000,
            "notas_credito_recibidas_cant": 0,
            "notas_credito_recibidas_iva": 0,
            "notas_debito_recibidas_cant": 0,
            "notas_debito_recibidas_iva": 0,
            "facturas_compra_digital_cant": 3,
            "facturas_compra_digital_neto": 1200000,
            "compras_sin_credito_cant": 0,
            "compras_sin_credito_neto": 0,
            "din_giro_cant": 0,
            "din_giro_iva": 0,
            "din_activo_fijo_cant": 0,
            "din_activo_fijo_iva": 0,
        },
        "remanente_anterior": 450000,
        "devoluciones": {
            "art_36_exportador": 0,
            "art_27_bis": 0,
            "certificado_27_bis": 0,
            "cambio_sujeto": 0,
        },
        "retenciones": {
            "iusc_impuesto": 280000,
            "honorarios_retencion": 457500,
            "directores_retencion": 0,
        },
        "ppm": {
            "tasa": 0.25,
            "base_imponible": None,
            "credito_sence": 0,
            "remanente_sence_anterior": 0,
            "suspension": False,
        },
    }

    output = "f29_enero_2026.xlsx"
    codigos = generar_f29_excel(datos_ejemplo, output)
    print(f"✅ F29 generado exitosamente: {output}")
    print(f"   Total Débito (538): {formato_peso(codigos[538])}")
    print(f"   Total Crédito (537): {formato_peso(codigos[537])}")
    print(f"   IVA a pagar (89): {formato_peso(codigos[89])}")
    print(f"   Remanente CF (77): {formato_peso(codigos[77])}")
    print(f"   Total a pagar (91): {formato_peso(codigos[91])}")