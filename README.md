# 🇨🇱 F29 Chile — Skill para Claude AI

Skill de Claude que genera automáticamente el **Formulario 29 (F29)** del Servicio de Impuestos Internos de Chile a partir de documentos contables. Optimizada para **empresas de desarrollo de software y tecnología**.

> **¿Qué es una skill?** Es un conjunto de instrucciones y archivos que le enseñan a Claude a realizar una tarea específica con alta precisión. En este caso: leer tus documentos contables y generar tu declaración mensual de IVA.

---

## ✨ Qué hace

- 📄 **Lee tus documentos contables** (PDFs, Excel, CSV) del período mensual
- 🧮 **Calcula automáticamente** débito fiscal, crédito fiscal, IVA, PPM y retenciones
- 📊 **Genera un Excel de 3 hojas** con el F29 completo, detalle de cálculos y alertas
- ✅ **Valida** la consistencia de los datos antes de generar el formulario
- ⚠️ **Alerta** sobre situaciones especiales (prorrateo, exportaciones, servicios digitales)

---

## 🎯 Para quién es

- Empresas de **desarrollo de software** en Chile (SaaS, consultoras, agencias)
- **Contadores y agentes contables** que atienden empresas tecnológicas
- Cualquier **contribuyente de IVA** en Chile (funciona para todos los giros)

---

## 🏗️ Estructura

```
f29-chile-skill/
├── SKILL.md                      # Instrucciones principales de la skill
├── README.md                     # Este archivo
├── references/
│   ├── F29_CODIGOS.md            # Tabla completa de ~80 códigos del F29
│   └── GUIA_SOFTWARE.md          # Contexto legal y casos especiales para software
└── scripts/
    └── generar_f29.py            # Script Python que genera el Excel
```

---

## 🚀 Cómo usarla

### Paso 1 — Crear un Proyecto en Claude

1. Entra a [claude.ai](https://claude.ai)
2. En la barra lateral, haz clic en **"Projects"**
3. Crea un nuevo proyecto (ej: *"Contabilidad Empresa"*)

### Paso 2 — Subir los archivos

En la sección **"Project knowledge"** del proyecto, sube estos 4 archivos:

- `SKILL.md`
- `references/F29_CODIGOS.md`
- `references/GUIA_SOFTWARE.md`
- `scripts/generar_f29.py`

### Paso 3 — Agregar instrucciones

En **"Custom instructions"** pega:

```
Eres un asistente contable para una empresa de desarrollo de software en Chile.
Cuando te pida generar el F29 de un mes, sigue las instrucciones del SKILL.md,
usa la referencia de códigos F29_CODIGOS.md, y genera el Excel usando el script
generar_f29.py. Siempre pregunta los datos que falten antes de calcular.
```

### Paso 4 — Usar mes a mes

Abre un chat nuevo dentro del proyecto, sube los documentos del mes y pide:

> *"Genera el F29 de enero 2026 con estos documentos"*

Claude te pedirá los datos que falten y generará el Excel.

---

## 📎 Documentos que acepta como input

| Documento | Qué aporta | Formato |
|-----------|-----------|---------|
| Libro de Ventas | Facturas emitidas → Débito fiscal | CSV, XLSX, PDF |
| Libro de Compras | Facturas recibidas → Crédito fiscal | CSV, XLSX, PDF |
| Registro de Compras y Ventas (RCV) del SII | Ambos lados ya conciliados | CSV, XLSX, PDF |
| Libro de Remuneraciones | Impuesto Único 2da Categoría | XLSX, PDF |
| Boletas de Honorarios | Retenciones a freelancers | CSV, PDF |
| Facturas de Exportación | Ventas exentas al exterior | PDF |
| F29 del mes anterior | Remanente de crédito fiscal | PDF, imagen |

---

## 📊 Output: Excel de 3 hojas

### Hoja 1 — F29 del período
Replica la estructura oficial del SII con todos los códigos, montos y totales.

### Hoja 2 — Detalle de Cálculos
Desglose de cada código: de dónde viene cada número, qué facturas lo componen, fórmulas aplicadas. Para que el contador pueda verificar línea por línea.

### Hoja 3 — Alertas y Notas
Validaciones automáticas, advertencias y recomendaciones:
- Prorrateo de IVA cuando hay ventas afectas + exentas
- Verificación de calificación de exportaciones ante Aduanas
- Consistencia de tasas de PPM según régimen tributario
- Recordatorio de plazos

---

## 💻 Lo que sabe de software

La skill incluye conocimiento específico sobre la tributación de empresas de tecnología en Chile:

| Tema | Detalle |
|------|---------|
| **IVA en software** | Desde Ley 21.420 (01/01/2023), todo servicio de desarrollo, licencia y consultoría está afecto a IVA 19% |
| **Exportación de software** | Exenta de IVA (Art. 12 E N°16) con recuperación de crédito fiscal vía Art. 36 |
| **Servicios digitales extranjeros** | AWS, Azure, Google Cloud requieren Factura de Compra con retención de IVA (efecto neutro) |
| **Sociedad de profesionales** | Exención IVA Art. 12 E N°8 para sociedades donde todos los socios tienen título profesional |
| **PPM Pro Pyme** | Tasas reducidas: 0,20% (Transparente) o 0,25% (General) |
| **Retención honorarios 2026** | 15,25% (escala progresiva Ley 21.133) |

---

## ⚙️ Requisitos técnicos

El script Python necesita:

```bash
pip install openpyxl pandas pdfplumber
```

Claude instala estas dependencias automáticamente cuando genera el Excel.

---

## ⚠️ Disclaimer

**Esta herramienta es de apoyo y no constituye asesoría tributaria.** El F29 generado debe ser revisado por un contador o asesor tributario antes de presentarse al SII. Los cálculos se basan en la información proporcionada por el usuario y en la normativa vigente a febrero 2026. Ante cualquier duda, consultar directamente al [SII](https://www.sii.cl) o a un profesional.

---

## 📚 Fuentes y normativa

- [Instrucciones oficiales del F29 (SII)](https://www.sii.cl/servicios_online/instrucciones_f29_20241112.pdf)
- [Guía para declarar F29 por internet (SII)](https://www.sii.cl/pagina/iva/guia_f29.htm)
- [Circular SII N°50 de 2022 — IVA a servicios](https://www.sii.cl/normativa_legislacion/circulares/2022/circu50.pdf)
- [Imagen oficial del F29 (PDF)](https://www.sii.cl/formularios/imagen/F29.pdf)
- [Oficio SII 1154/2023 — IVA exportador en software](https://www.bbsc.cl/oficio-1154-del-2023-iva-exportador-en-el-desarrollo-de-software/)
- [Calendario de IVA (F29)](https://www.sii.cl/destacados/f29/index.html)

---

## 🤝 Contribuir

Si encuentras errores, quieres agregar soporte para otros giros, o mejorar la skill:

1. Fork el repositorio
2. Crea una rama (`git checkout -b mejora/descripcion`)
3. Haz tus cambios
4. Abre un Pull Request

Las contribuciones más útiles serían:
- Soporte para más tipos de documentos de entrada
- Validaciones adicionales
- Adaptaciones para otros giros (retail, servicios profesionales, construcción)
- Actualización de tasas cuando cambie la normativa