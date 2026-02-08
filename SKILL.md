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

## Flujo de trabajo

### Paso 1 — Identificar documentos disponibles

Revisar los archivos subidos por el usuario en `/mnt/user-data/uploads/`. Los documentos
típicos que se esperan son:

| Tipo de documento | Información que aporta |
|-------------------|----------------------|
| **Libro de Ventas** (CSV/XLSX/PDF) | Facturas emitidas → Débito fiscal (línea 7) |
| **Libro de Compras** (CSV/XLSX/PDF) | Facturas recibidas → Crédito fiscal (líneas 28-35) |
| **Registro de Compras y Ventas (RCV)** del SII | Ambos lados, ya conciliado |
| **Libro de Remuneraciones** (XLSX/PDF) | Impuesto Único 2da Categoría (línea 60) |
| **Listado de Boletas de Honorarios** (CSV/PDF) | Retenciones Art. 42 N°2 (línea 61) |
| **Facturas de Exportación** | Ventas exentas de exportación (línea 1) |
| **F29 del mes anterior** (PDF/imagen) | Remanente de crédito fiscal (código 504) |
| **Resumen de PPM** | Tasa y base imponible PPM (línea 69) |

Si faltan documentos críticos, **preguntar al usuario** antes de continuar. Los datos mínimos
necesarios son:

1. Ventas del período (facturas emitidas o resumen)
2. Compras del período (facturas recibidas o resumen)
3. Remanente de crédito fiscal del mes anterior (código 504/77 del F29 previo), si existe
4. Tasa de PPM vigente (preguntar si no se deduce de los documentos)
5. Retenciones de honorarios pagados, si aplica

### Paso 2 — Extraer datos de los documentos

Usar las herramientas disponibles para leer cada archivo:

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

#### Del Libro de Ventas / Facturas emitidas:
- Cantidad de facturas afectas del giro → código 503
- Monto neto total de facturas afectas → para calcular código 502 (neto × 19%)
- Cantidad y monto de notas de crédito emitidas → códigos 509/510
- Cantidad y monto de notas de débito emitidas → códigos 512/513
- Facturas de exportación → códigos 585/20
- Facturas exentas → códigos 586/142
- Boletas electrónicas → códigos 110/111 o 758/759

#### Del Libro de Compras / Facturas recibidas:
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

Si alguna validación falla, **informar al usuario** con detalle del error y pedir confirmación
o corrección antes de continuar.

### Paso 5 — Generar el archivo Excel

Usar el script `scripts/generar_f29.py` para crear un archivo Excel formateado que replica
la estructura visual del F29 del SII, con:

- Encabezado con RUT, período tributario, razón social
- Sección de Débito Fiscal (líneas 1–23) con códigos y valores
- Sección de Crédito Fiscal (líneas 24–49)
- Determinación del IVA (línea 50)
- Retenciones e Impuesto Único (líneas 59–68)
- PPM (líneas 69–78)
- Total a pagar (líneas 141–144)
- Hoja adicional con resumen ejecutivo y detalle de cálculos
- Hoja con alertas y observaciones

Copiar el resultado a `/mnt/user-data/outputs/` y presentar al usuario.

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

El archivo Excel generado debe tener 3 hojas:

### Hoja 1: "F29 — [Mes] [Año]"
Replica la estructura oficial del F29 con todos los códigos, valores calculados y totales.
Formato visual profesional con colores del SII (azul oscuro para encabezados, celdas amarillas
para valores editables, celdas verdes para cálculos automáticos).

### Hoja 2: "Detalle de Cálculos"
Muestra el desglose de cada código: de dónde viene cada número, qué facturas lo componen,
las fórmulas aplicadas. Esto permite al contador verificar cada línea.

### Hoja 3: "Alertas y Notas"
Lista todas las validaciones ejecutadas, advertencias encontradas, y notas relevantes para
el período (ej: "Se detectaron facturas de exportación — verificar calificación ante Aduanas",
"El remanente de CF es significativo — considerar solicitar devolución Art. 36").

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