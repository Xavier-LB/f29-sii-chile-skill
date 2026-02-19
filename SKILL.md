---
name: f29-chile
description: >
  Genera el Formulario 29 (F29) del SII de Chile a partir de documentos contables del usuario.
  Usa esta skill cuando el usuario quiera: generar su declaración mensual de IVA (F29),
  calcular débitos y créditos fiscales a partir de facturas, calcular PPM, calcular retenciones
  de honorarios, revisar o validar un F29 ya llenado, o entender qué códigos del F29 aplican
  a su situación. Trigger: cualquier mención de "F29", "formulario 29", "declaración mensual",
  "IVA mensual", "PPM", o "declarar IVA" en contexto chileno. Especialmente optimizada para
  empresas de desarrollo de software / tecnología.
---

# Skill: Generador de Formulario 29 — Empresas de Software en Chile

## Propósito

Esta skill lee documentos contables del usuario (PDFs, Excel, CSV, imágenes) y genera un
Formulario 29 completo y validado, listo para declarar en sii.cl. Está optimizada para
empresas de desarrollo de software, pero funciona para cualquier contribuyente de IVA.

---

## Fuente de datos preferida: RCV del SII

### ¿Por qué usar el RCV?

El **Registro de Compras y Ventas (RCV)** del SII es la fuente **autoritativa** para
determinar qué documentos pertenecen a cada período tributario. Esto es crítico porque:

1. **Las Facturas de Compra (FC) pueden emitirse fuera de plazo**: Una FC con fecha de
   enero puede haberse emitido efectivamente en febrero en el SII. En ese caso, la FC
   pertenece al período de **febrero** (mes de emisión real), no al de enero (fecha del
   documento).

2. **El RCV refleja la realidad del SII**: Muestra los documentos tal como están registrados
   en el sistema del SII, con sus fechas reales de emisión/recepción. No hay ambigüedad.

3. **Las Notas de Crédito anulan y reemplazan**: Si una FC fue anulada con NC y reemplazada
   por otra, el RCV solo muestra los documentos vigentes del período.

### Regla fundamental: Fecha de emisión real > Fecha del documento

| Situación | ¿A qué período pertenece? |
|-----------|--------------------------|
| FC con fecha enero, emitida en SII en enero | Enero |
| FC con fecha enero, emitida en SII en febrero | **Febrero** |
| FC con fecha enero, emitida en SII en enero, anulada en febrero | No aparece (anulada) |
| Factura recibida de proveedor chileno, recepcionada en enero | Enero |

### Cómo obtener el RCV

El usuario puede descargar el RCV desde el portal del SII:
1. Ir a sii.cl → Mi SII → Registro de Compras y Ventas
2. Seleccionar el período tributario (mes/año)
3. Descargar en formato CSV o Excel
4. Hay dos secciones: **Registro de Ventas** y **Registro de Compras**

### Formato típico del RCV

#### RCV de Ventas (CSV)
Columnas típicas:
- Tipo Doc (33=Factura, 61=NC, 56=ND)
- Folio
- Fecha Docto
- RUT Receptor
- Razón Social
- Monto Exento
- Monto Neto
- Monto IVA
- Monto Total

#### RCV de Compras (CSV)
Columnas típicas:
- Tipo Doc (33=Factura recibida, 46=Factura de Compra, 61=NC recibida)
- Folio
- Fecha Docto
- Fecha Recepción (esta es la fecha real en que el SII la registró)
- RUT Proveedor
- Razón Social
- Monto Exento
- Monto Neto
- Monto IVA Recuperable
- Monto Total
- IVA No Recuperable
- IVA Retenido Total
- IVA Retenido Parcial

### Mapeo RCV → Códigos F29

#### Ventas (Débito Fiscal)
| Tipo Doc RCV | Descripción | Códigos F29 |
|-------------|-------------|-------------|
| 33 | Factura Electrónica | 503 (cantidad), 502 (IVA) |
| 34 | Factura No Afecta o Exenta | 586 (cantidad), 142 (monto exento) |
| 61 | Nota de Crédito Electrónica | 509 (cantidad), 510 (IVA) |
| 56 | Nota de Débito Electrónica | 512 (cantidad), 513 (IVA) |
| 110 | Factura de Exportación | 585 (cantidad), 20 (monto) |
| 39 | Boleta Electrónica | 110 (cantidad), 111 (IVA) |

#### Compras (Crédito Fiscal)
| Tipo Doc RCV | Descripción | Códigos F29 |
|-------------|-------------|-------------|
| 33 | Factura recibida (del giro) | 519 (cantidad), 520 (IVA) |
| 46 | Factura de Compra (cambio sujeto) | 515 (cantidad), 587 (IVA retenido) → también suma a 520 |
| 61 | NC recibida | 527 (cantidad), 528 (IVA) |
| 56 | ND recibida | 531 (cantidad), 532 (IVA) |

> **IMPORTANTE sobre FC (tipo 46)**: Las Facturas de Compra tienen doble efecto:
> - Se registran como IVA Retenido (débito): código 596 = suma IVA de todas las FC
> - Se registran como Crédito Fiscal: código 520 incluye el IVA de las FC
> - Efecto neto = $0, pero ambos registros son obligatorios

### Procedimiento cuando se tiene el RCV

1. **Leer el RCV** de ventas y compras del período
2. **Clasificar** cada documento según su tipo (ver tabla de mapeo arriba)
3. **Sumar** por tipo de documento para obtener cantidades y montos por código F29
4. **Cruzar** con los datos internos (CSVs del repositorio) para agregar descripciones
   y detalles a la hoja de documentos
5. **Verificar** que los totales del RCV coincidan con los datos internos. Si hay
   discrepancias, **el RCV manda** — informar las diferencias al usuario

### Procedimiento cuando NO se tiene el RCV (fallback)

Si el usuario no proporciona el RCV, se puede generar el F29 usando los datos internos
(CSVs de facturas emitidas, recibidas y de compra), pero con las siguientes advertencias:

1. **Advertir** que las FC se están contando por la fecha del documento, no por la fecha
   real de emisión en el SII
2. **Recomendar** verificar el resultado contra el RCV del SII antes de declarar
3. **Marcar** en la hoja de Alertas que el F29 fue generado sin RCV

---

## Flujo de trabajo

### Paso 1 — Identificar documentos disponibles

Revisar los archivos disponibles. **Solicitar siempre el RCV al usuario** como fuente
principal. Los documentos típicos son:

| Tipo de documento | Información que aporta | Prioridad |
|-------------------|----------------------|-----------|
| **RCV del SII** (CSV/XLSX) | Ventas y compras del período, con fechas reales | **PREFERIDO** |
| **Libro de Ventas** (CSV/XLSX/PDF) | Facturas emitidas → Débito fiscal | Alternativa |
| **Libro de Compras** (CSV/XLSX/PDF) | Facturas recibidas → Crédito fiscal | Alternativa |
| **Libro de Remuneraciones** (XLSX/PDF) | Impuesto Único 2da Categoría (línea 60) | Complementario |
| **Listado de Boletas de Honorarios** (CSV/PDF) | Retenciones Art. 42 N°2 (línea 61) | Complementario |
| **Facturas de Exportación** | Ventas exentas de exportación (línea 1) | Si aplica |
| **F29 del mes anterior** (PDF/imagen) | Remanente de crédito fiscal (código 504) | Siempre |
| **Resumen de PPM** | Tasa y base imponible PPM (línea 69) | Si aplica |

Si faltan documentos críticos, **preguntar al usuario** antes de continuar. Los datos mínimos
necesarios son:

1. **RCV del período** (ventas + compras) — o en su defecto, libros de ventas/compras
2. Remanente de crédito fiscal del mes anterior (código 504/77 del F29 previo), si existe
3. Tasa de PPM vigente (preguntar si no se deduce de los documentos)
4. Retenciones de honorarios pagados, si aplica
5. IUSC de liquidaciones de sueldo, si hay empleados

### Paso 2 — Extraer datos de los documentos

#### Opción A: Desde el RCV (preferido)

```python
import pandas as pd

# Leer RCV de ventas y compras
rcv_ventas = pd.read_csv("rcv_ventas.csv")  # o pd.read_excel()
rcv_compras = pd.read_csv("rcv_compras.csv")

# Clasificar por tipo de documento
facturas_emitidas = rcv_ventas[rcv_ventas["Tipo Doc"] == 33]
nc_emitidas = rcv_ventas[rcv_ventas["Tipo Doc"] == 61]
nd_emitidas = rcv_ventas[rcv_ventas["Tipo Doc"] == 56]

facturas_recibidas = rcv_compras[rcv_compras["Tipo Doc"] == 33]
fc_emitidas = rcv_compras[rcv_compras["Tipo Doc"] == 46]  # Facturas de Compra
nc_recibidas = rcv_compras[rcv_compras["Tipo Doc"] == 61]
```

**Nota**: Los nombres de columnas pueden variar según la versión del export del SII.
Adaptar según las columnas reales del archivo. Verificar si hay columnas para IVA
Retenido (para FCs tipo 46).

#### Opción B: Desde archivos internos (fallback)

```python
# Para PDFs: usar pypdf o pdfplumber
import pdfplumber
with pdfplumber.open("archivo.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        tables = page.extract_tables()

# Para Excel/CSV: usar openpyxl o pandas
import pandas as pd
df = pd.read_excel("libro_ventas.xlsx")
# o
df = pd.read_csv("libro_ventas.csv")
```

**Datos a extraer de cada fuente:**

#### Del RCV o Libro de Ventas / Facturas emitidas:
- Cantidad de facturas afectas del giro → código 503
- Monto neto total de facturas afectas → para calcular código 502 (neto × 19%)
- Cantidad y monto de notas de crédito emitidas → códigos 509/510
- Cantidad y monto de notas de débito emitidas → códigos 512/513
- Facturas de exportación → códigos 585/20
- Facturas exentas → códigos 586/142
- Boletas electrónicas → códigos 110/111 o 758/759

#### Del RCV o Libro de Compras / Facturas recibidas:
- Facturas con derecho a crédito fiscal → códigos 519/520
- Facturas de activo fijo → códigos 524/525
- Notas de crédito recibidas → códigos 527/528
- Notas de débito recibidas → códigos 531/532
- Facturas de compra (servicios digitales extranjeros) → códigos 515/587
- Compras sin derecho a crédito → códigos 564/521 (informativo)

#### Del Libro de Remuneraciones:
- Impuesto Único de Segunda Categoría retenido → código 48

#### De Boletas de Honorarios:
- Total retención sobre honorarios pagados → código 151
- Tasa vigente 2026: **15,25%** del monto bruto

### Paso 3 — Calcular cada sección del F29

Seguir estrictamente la lógica de cálculo descrita en `references/F29_CODIGOS.md`.

#### Fórmulas principales:

```
DÉBITO FISCAL (código 538) =
  + código 502 (facturas afectas)
  + código 717 (ventas no del giro)
  + código 111 (boletas)
  + código 759 (boletas electrónicas POS)
  + código 513 (notas de débito)
  − código 510 (notas de crédito)
  + código 517 (retención parcial cambio sujeto)
  + código 501 (liquidaciones)
  + código 154 (adiciones por Art. 27 bis)
  + código 518 (restitución adicional)
  + código 713 (reintegro timbres)
  + códigos 738+739+740+741 (IEPD)
  + código 791 (restitución remanente)

CRÉDITO FISCAL (código 537) =
  + código 520 (facturas recibidas del giro)
  + código 762 (facturas supermercados)
  + código 766 (facturas inmuebles)
  + código 525 (facturas activo fijo)
  − código 528 (notas de crédito recibidas)
  + código 532 (notas de débito recibidas)
  + código 535 (DIN del giro)
  + código 553 (DIN activo fijo)
  + código 504 (remanente mes anterior)
  − código 593 (devolución Art. 36 exportadores)
  − código 594 (devolución Art. 27 bis)
  − código 592 (certificado Art. 27 bis)
  − código 539 (devolución cambio sujeto)
  + código 164 (reintegro devoluciones indebidas)
  + códigos de recuperación IEPD
  + código 523 (crédito Zona Franca)
  + código 712 (crédito Timbres)
  + código 757 (crédito IVA restituido)

IVA DETERMINADO:
  Si código 538 > código 537 → código 89 = 538 − 537 (IVA a pagar)
  Si código 537 > código 538 → código 77 = 537 − 538 (remanente para siguiente mes)

PPM (código 62) = código 563 (base imponible) × código 115 (tasa %) / 100
  Donde base imponible = ingresos netos del mes (ventas afectas + exentas + exportaciones)

TOTAL A PAGAR (código 91) =
  código 89 (IVA determinado, si hay)
  + código 48 (IUSC)
  + código 151 (retención honorarios)
  + código 153 (retención directores)
  + código 62 (PPM neto)
  − código 723 (crédito SENCE aplicado)
  + otros impuestos adicionales del reverso (si aplica)
```

### Paso 4 — Validar

Ejecutar las siguientes validaciones antes de generar el archivo:

1. **Cruce débito-crédito**: código 538 debe ser ≥ 0 o justificadamente negativo
2. **Remanente**: código 504 debe coincidir con código 77 del mes anterior (si se proporcionó)
3. **PPM**: tasa debe estar entre 0,20% y 3% según régimen
4. **Retención honorarios**: verificar que tasa aplicada sea 15,25% (2026)
5. **Consistencia cantidades vs montos**: si hay 0 facturas, el monto debe ser 0
6. **Código 91 ≥ 0**: el total a pagar no puede ser negativo (sería un error)
7. **Exportaciones**: si hay facturas de exportación, no deben generar débito fiscal
8. **Cruce RCV vs datos internos** (si se usó RCV): Comparar las cantidades y montos
   del RCV con los datos de los CSVs internos. Reportar diferencias, especialmente:
   - FCs que aparecen en el CSV interno pero NO en el RCV del período (posible emisión
     tardía — la FC se emitió en otro mes)
   - FCs que aparecen en el RCV pero NO en el CSV interno (falta registrar en el sistema)
   - Diferencias de montos entre RCV y datos internos
9. **Alerta sin RCV**: Si no se usó el RCV, agregar alerta prominente indicando que las
   FCs se contaron por fecha del documento y podrían no coincidir con la emisión real

Si alguna validación falla, **informar al usuario** con detalle del error y pedir confirmación
o corrección antes de continuar.

### Paso 5 — Generar el archivo Excel

**IMPORTANTE**: Usar SIEMPRE el script `scripts/generar_f29.py` y su función `generar_f29_excel(datos, output_path)`.
Este script replica exactamente la estructura del formulario F29 oficial del SII (ver `f29-ejemplo.xlsx` como
referencia visual del formato esperado). **NUNCA generar un Excel con formato custom o inventado.**

El script genera un workbook con 3 hojas:
1. **F29**: Réplica completa del formulario oficial (150 líneas, colores verde/azul/gris, fórmulas Excel)
2. **Detalle Documentos**: Desglose de cada línea con los documentos individuales
3. **Alertas y Notas**: Validaciones, advertencias y notas relevantes

#### Cómo llamar al script

```python
import sys
sys.path.insert(0, "/ruta/al/repo/.claude/skills/f29-sii-chile")
from scripts.generar_f29 import generar_f29_excel

datos = {
    "encabezado": {
        "rut": "78.033.706-0",
        "razon_social": "TOTOMENU SPA",
        "periodo_mes": 1,
        "periodo_anio": 2026,
        "folio": "________",
    },
    # Opción A: pasar códigos directamente (si ya están calculados)
    "codigos": {
        503: 9, 502: 1486239, 538: 1486239,
        519: 28, 520: 505218, 527: 1, 528: 4309, 504: 0, 537: 500909,
        # ... etc
    },
    # Opción B: pasar datos desglosados (ventas, compras, etc.) y dejar que calcular_f29() los procese
    # "ventas": { ... }, "compras": { ... }, "retenciones": { ... }, "ppm": { ... },

    # Documentos individuales para la hoja de detalle (opcional pero recomendado)
    "documentos": {
        "linea_7": [ {"numero": "F-116", "fecha": "02/01/2026", ...}, ... ],
        "linea_28": [ ... ],
        # etc
    },
    # Notas adicionales para la hoja de alertas
    "notas": [
        ("NOTA", "15 de 21 FCs tienen fecha dic 2025 pero emisión SII en enero"),
    ],
}

codigos = generar_f29_excel(datos, "/ruta/output/F29-Enero-2026.xlsx")
```

#### Referencia visual: `f29-ejemplo.xlsx`

El archivo `f29-ejemplo.xlsx` en este directorio contiene un ejemplo del formato de salida esperado.
Usa los mismos colores, estructura y fórmulas que el script produce:
- Headers verdes (#73B464) para secciones principales
- Sub-headers azules (#D9EDF7) para subsecciones
- Filas de datos con fondo gris (#E8E8E8) en columna de línea/código
- Celdas de fórmula con fondo gris claro (#EEEEEE)
- 7 columnas: Línea, Descripción, Cód, Cantidad/Base, Cód, Monto/Valor, +/-

---

## Reglas específicas para empresas de software

### IVA en servicios de software (post Ley 21.420, vigente desde 01/01/2023)

| Tipo de operación | ¿Afecto a IVA? | Línea F29 |
|-------------------|----------------|-----------|
| Desarrollo de software a medida (cliente Chile) | **Sí, 19%** | Línea 7 (código 502) |
| Licencia de software (SaaS, on-premise) | **Sí, 19%** | Línea 7 (código 502) |
| Mantención y soporte de software | **Sí, 19%** | Línea 7 (código 502) |
| Consultoría tecnológica | **Sí, 19%** | Línea 7 (código 502) |
| Software exportado a cliente extranjero | **Exento** (Art. 12 E N°16) | Línea 1 (código 585/20) |
| Sociedad de profesionales (Art. 12 E N°8) | **Exento** | Línea 2 (código 586/142) |
| Desarrollador freelance (boleta honorarios) | **No aplica IVA** | No va en F29 propio |

### Servicios digitales extranjeros (AWS, Azure, Google Cloud, etc.)

Desde 2020 (Ley 21.210), la empresa chilena debe:
1. Emitir **Factura de Compra (tipo 46)** al proveedor extranjero
2. Retener el IVA (19% sobre el monto pagado)
3. Registrar como débito fiscal en línea 5 (códigos 515/587)
4. Registrar simultáneamente como crédito fiscal en línea 28 (código 520)
5. Efecto neto = $0, pero AMBOS registros deben existir

### Tasas de PPM por régimen tributario

| Régimen | Tasa PPM | Código 115 |
|---------|----------|------------|
| Pro Pyme Transparente (Art. 14D N°8) | 0,20% | 0.2 |
| Pro Pyme General (Art. 14D N°3) | 0,25% | 0.25 |
| Régimen General (Semi-Integrado, 1er año) | 1,00% | 1.0 |
| Régimen General (años siguientes) | Variable según F22 anterior | Consultar |

### Retención de boletas de honorarios (desarrolladores freelance)

| Año | Tasa retención |
|-----|---------------|
| 2024 | 13,75% |
| 2025 | 14,50% |
| **2026** | **15,25%** |
| 2027 | 16,00% |
| 2028+ | 17,00% |

La retención se declara en el código 151 (línea 61).
La base es el **monto bruto** de la boleta de honorarios.

### Exportación de software — Recuperación IVA exportador

Si la empresa exporta software (desarrollo para clientes extranjeros):
1. Las facturas de exportación van en línea 1 (exentas)
2. El crédito fiscal de compras asociadas a exportación se acumula
3. Se puede pedir devolución del remanente de CF vía Art. 36 DL 825
4. La solicitud se hace por Formulario 3600 (separado del F29)
5. En el F29, la devolución otorgada se descuenta en código 593 (línea 37)

### Prorrateo de IVA (ventas mixtas: afectas + exentas/exportación)

Si la empresa tiene TANTO ventas afectas como exentas o de exportación en el mismo período:
- El crédito fiscal de uso común debe **prorratearse** proporcionalmente
- Solo se puede usar como crédito la fracción proporcional a ventas afectas
- Fórmula: CF utilizable = CF total × (ventas afectas / ventas totales)
- El CF no utilizable se registra en compras sin derecho a crédito

---

## Preguntas que SIEMPRE debes hacer al usuario si no tienes la información

1. **¿Cuál es el período tributario?** (mes/año que se declara)
2. **¿Cuál es el RUT de la empresa?**
3. **¿Hay remanente de crédito fiscal del mes anterior?** (código 77 del F29 previo)
4. **¿Cuál es el régimen tributario?** (Pro Pyme Transparente, Pro Pyme General, Semi-Integrado)
5. **¿La tasa de PPM ha sido modificada?** (si no, usar la tasa por defecto del régimen)
6. **¿Hay facturas de exportación este mes?**
7. **¿Se pagaron boletas de honorarios?**
8. **¿Hay trabajadores en nómina con retención de IUSC?**

---

## Formato de salida

El archivo Excel generado debe tener 4 hojas:

### Hoja 1: "F29 — [Mes] [Año]"
Replica la estructura oficial del F29 con todos los códigos, valores calculados y totales.
Cada línea que tiene documentos de respaldo indica la cantidad y referencia a la hoja de detalle.

### Hoja 2: "Detalle Documentos"
**NUEVA v2**: Desglosa cada línea del F29 con los documentos individuales que la componen.
Para cada documento muestra: N° documento, fecha, RUT, razón social, descripción, neto, IVA,
exento y total. Incluye fila de totales por sección. Columnas adaptadas según tipo:
- Ventas/Débito: N° Doc, Fecha, RUT Cliente, Razón Social, Descripción, Neto, IVA, Exento, Total
- Compras/Crédito: N° Doc, Fecha, RUT Proveedor, Razón Social, Descripción, Neto, IVA, Total
- Honorarios: N° Boleta, Fecha, RUT Profesional, Razón Social, Descripción, Bruto, Retención, Líquido
- Sueldos: N° Liquidación, Fecha, RUT Trabajador, Nombre, Cargo, Sueldo Bruto, IUSC, Líquido

### Hoja 3: "Detalle de Cálculos"
Muestra el desglose de cada código: de dónde viene cada número, las fórmulas aplicadas.

### Hoja 4: "Alertas y Notas"
Validaciones, advertencias y notas relevantes para el período.

## Estructura de documentos individuales

Cuando Claude extrae datos de los archivos del usuario, debe organizar los documentos
en el dict `datos["documentos"]` agrupados por línea del F29:

```python
datos["documentos"] = {
    "linea_7": [     # Facturas afectas del giro
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
    ],
    "linea_13": [],  # Notas de crédito emitidas
    "linea_1": [],   # Facturas de exportación
    "linea_28": [],  # Facturas recibidas (compras)
    "linea_31": [],  # Facturas activo fijo
    "linea_5": [],   # Facturas de compra (serv. digitales)
    "linea_12": [],  # Notas de débito emitidas
    "linea_61": [    # Boletas de honorarios → campos: bruto, retencion, liquido
        {
            "tipo": "boleta_honorarios",
            "numero": "BH-3001",
            "rut": "15.123.456-7",
            "razon_social": "María Pérez",
            "descripcion": "Desarrollo frontend",
            "bruto": 2000000,
            "retencion": 305000,
            "liquido": 1695000,
        },
    ],
    "linea_60": [    # Liquidaciones de sueldo → campos: bruto, iusc, liquido, cargo
        {
            "tipo": "liquidacion_sueldo",
            "numero": "LIQ-001",
            "rut": "17.111.222-3",
            "razon_social": "Andrea López",
            "cargo": "Tech Lead",
            "bruto": 3500000,
            "iusc": 185000,
            "liquido": 2800000,
        },
    ],
}
```

Si se proporcionan documentos para una línea, los totales se recalculan automáticamente
desde ellos. Si no hay documentos, se usan los totales agregados de datos["ventas"],
datos["compras"] y datos["retenciones"].

---

## Dependencias

```bash
pip install openpyxl pandas pdfplumber --break-system-packages
```

## Referencias

- `references/F29_CODIGOS.md` — Tabla completa de todos los códigos del F29 con líneas y descripciones
- `references/GUIA_SOFTWARE.md` — Contexto legal, casos especiales y matices prácticos para empresas de software. Consultar cuando haya dudas sobre exenciones, exportación, prorrateo o servicios digitales extranjeros.
- Instrucciones oficiales del SII: https://www.sii.cl/servicios_online/instrucciones_f29_20241112.pdf
- Circular SII N°50 de 2022 (IVA a servicios): https://www.sii.cl/normativa_legislacion/circulares/2022/circu50.pdf