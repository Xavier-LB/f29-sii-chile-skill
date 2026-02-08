# Guía de Referencia: F29 para Empresas de Software en Chile

> Este archivo es una referencia complementaria. No repite los códigos ni las instrucciones
> de proceso (eso está en SKILL.md y F29_CODIGOS.md). Aquí se explica el **contexto legal,
> los matices prácticos y los casos especiales** que pueden surgir al llenar el F29 de una
> empresa de tecnología.

---

## 1. El cambio de la Ley 21.420: por qué importa

Antes de enero 2023, el IVA en Chile solo gravaba servicios provenientes de actividades
del Art. 20 N°3 y N°4 de la Ley de Renta. Muchos servicios de software se clasificaban
bajo el Art. 20 N°5 y quedaban fuera del IVA. La Ley 21.420 eliminó esa distinción:
desde el 1 de enero de 2023, **todos los servicios** prestados o utilizados en Chile
están afectos a IVA al 19%, salvo exenciones expresas.

Esto significa que:
- Una factura de desarrollo de software a medida que antes era exenta, ahora es afecta.
- No importa si el contrato dice "servicio" o "licencia": ambos están gravados.
- La Circular SII N°50 de 2022 detalla las exenciones que sobrevivieron al cambio.

**Implicancia práctica en el F29:** Desde 2023 toda factura de servicio de software
a clientes nacionales debe ir en la línea 7 (código 502) como factura afecta del giro,
nunca en la línea 2 (exentas), a menos que aplique una exención específica.

---

## 2. Cuándo una empresa de software puede ser exenta de IVA

### Sociedad de profesionales (Art. 12 letra E N°8)

Si la empresa está constituida como **sociedad de personas** (no SpA ni S.A.) y todos
los socios poseen título profesional universitario, puede quedar exenta de IVA por los
servicios profesionales que presta, incluso si optó por tributar en primera categoría.

Requisitos clave:
- Debe ser sociedad de personas (sociedad colectiva, limitada, o en comandita)
- **Todos** los socios deben tener título profesional (ingeniero, abogado, etc.)
- Los servicios deben ser de naturaleza profesional (no venta de productos)
- Si la sociedad contrata empleados que ejecutan el trabajo (y los socios solo
  administran), el SII puede cuestionar la exención

Caso práctico: Tres ingenieros informáticos forman una Ltda. para hacer consultoría
de arquitectura de software. Si todos tienen título universitario y prestan
personalmente los servicios → exenta de IVA. Sus facturas van en línea 2 (código 586).

Caso contrario: Esos mismos ingenieros forman una SpA → **no aplica la exención**,
aunque todos tengan título. La forma jurídica importa.

### Qué pasa si se pierde la exención

Si un socio sin título profesional ingresa a la sociedad, o la sociedad se transforma
en SpA, la exención se pierde inmediatamente. A partir de ese momento, todas las
facturas deben emitirse con IVA y declararse en línea 7 del F29.

---

## 3. Exportación de software: el paso a paso real

### ¿Qué cuenta como exportación de servicio?

Para que el software califique como exportación exenta (Art. 12 E N°16):
- El servicio se ejecuta total o parcialmente en Chile
- El cliente **no tiene domicilio ni residencia** en Chile
- El servicio se **utiliza exclusivamente en el exterior**
- La existencia real y el valor son verificables
- El prestador tiene domicilio en Chile

El punto clave es "utilizado exclusivamente en el exterior". Si desarrollas una app
que el cliente extranjero usa globalmente (incluyendo Chile), el SII podría cuestionar
la exención. En la práctica, para software que corre en servidores del cliente en el
extranjero, no hay problema.

### Trámite ante Aduanas

Los servicios de tecnología e ingeniería están en la lista precalificada del Servicio
Nacional de Aduanas (Resolución Exenta SNA N°2.511 de 2007), así que no necesitas
solicitar calificación individual. Pero sí debes:

1. Emitir **Factura de Exportación Electrónica** (exenta de IVA)
2. Para montos > USD 2.000: tramitar un **DUS** (Documento Único de Salida) a través
   de un agente de aduanas
3. Para montos ≤ USD 2.000: basta con un **DUSSI** (simplificado, se hace online)

El DUS/DUSSI es el documento que acredita la exportación y habilita la recuperación
del IVA. Sin él, no puedes pedir devolución del crédito fiscal.

### Recuperación del crédito fiscal (Art. 36)

El beneficio más potente para exportadores de software: puedes **recuperar todo el
IVA pagado en compras** asociadas a tu actividad exportadora. El proceso:

1. Acumulas remanente de crédito fiscal en el F29 (código 77) porque tus ventas
   de exportación no generan débito
2. Solicitas la devolución mediante **Formulario 3600** (separado del F29)
3. Presentas la **Declaración Jurada 3601** con el detalle
4. El SII devuelve el monto al mes siguiente (si todo está en orden)
5. En el F29 del mes en que recibes la devolución, la registras en código 593 (línea 37)

Cuidado: Si tienes ventas mixtas (exportación + domésticas), solo recuperas la
proporción de crédito fiscal correspondiente a exportación (prorrateo).

---

## 4. Servicios digitales extranjeros: el caso AWS/Azure/Google Cloud

### Por qué el efecto es neutro pero el registro es obligatorio

Cuando tu empresa paga USD 500 mensuales a AWS, debes:
1. Emitir Factura de Compra (tipo 46) por el equivalente en pesos
2. El IVA retenido (19%) se declara como débito Y como crédito en el mismo F29
3. Resultado neto: $0

Si **no** emites la Factura de Compra, el SII puede:
- Rechazar el gasto como deducción de renta
- Cobrar el IVA no retenido con multas e intereses
- Observar tu F29

### Qué servicios digitales requieren este tratamiento

Desde la actualización de la Ley 21.713 (noviembre 2024), **todos los servicios
remotos** prestados por no residentes están sujetos, no solo las 4 categorías
originales de la Ley 21.210. Esto incluye:
- Cloud computing (AWS, Azure, GCP, DigitalOcean, Heroku)
- SaaS que usa la empresa (Slack, Notion, Figma, GitHub, etc.)
- Servicios de infraestructura (Cloudflare, Vercel, Netlify)
- Herramientas de desarrollo (JetBrains, Postman Pro, etc.)
- Publicidad digital (Google Ads, Meta Ads) — si se factura desde el exterior

Excepción: Si el proveedor extranjero ya está registrado ante el SII como
contribuyente de IVA digital (Amazon, Google, Microsoft lo están para servicios
a consumidores finales), la obligación de emitir Factura de Compra **persiste**
cuando el beneficiario es empresa, porque el mecanismo de retención B2B es
independiente del registro del proveedor.

---

## 5. Prorrateo de IVA: cuándo y cómo aplicarlo

### Cuándo se activa

El prorrateo es obligatorio cuando en un mismo período la empresa tiene:
- Ventas **afectas** a IVA (desarrollo a clientes nacionales), Y
- Ventas **exentas** o no gravadas (exportaciones, servicios de sociedad profesional)

Y las compras del período no son 100% atribuibles a una u otra actividad.

### Cómo calcularlo

Existen tres tipos de crédito fiscal según su destino:

1. **CF de uso exclusivo afecto**: IVA de compras destinadas solo a generar ventas
   afectas → 100% recuperable
2. **CF de uso exclusivo exento/exportación**: IVA de compras destinadas solo a
   generar ventas exentas → 0% recuperable (pero si es exportación, se recupera
   vía Art. 36)
3. **CF de uso común**: IVA de compras que sirven a ambas actividades (arriendo de
   oficina, internet, servicios generales) → se prorratea:

```
CF utilizable = CF uso común × (ventas afectas del período ÷ ventas totales del período)
```

Ejemplo: Si la empresa facturó $15M afectos + $12M exportación = $27M total:
- Proporción afecta = 15/27 = 55,6%
- De un arriendo de oficina con IVA $190.000, solo usas $105.556 como crédito fiscal
- Los $84.444 restantes van a compras sin derecho a crédito (línea 25)

### Tip práctico

Muchas empresas de software evitan el prorrateo facturando desde entidades separadas
(una para Chile, otra para exportación). Si no es el caso, el prorrateo se calcula
acumulado en el período enero-diciembre y se ajusta proporcionalmente cada mes.

---

## 6. La propuesta del SII: qué revisa un contador experimentado

La propuesta automática del F29 es un buen punto de partida, pero un contador de
empresa de software debería verificar siempre estos puntos:

### Lo que la propuesta HACE bien
- Suma de facturas afectas emitidas y recibidas (líneas 7 y 28)
- Notas de crédito y débito
- Remanente del mes anterior (código 504)
- Cálculo aritmético de débito y crédito total

### Lo que la propuesta NO incluye y hay que agregar manualmente
- **Facturas de exportación** (línea 1, código 585)
- **Facturas de compra por servicios digitales** (línea 5, código 515)
- **Retenciones de boletas de honorarios** (línea 61, código 151)
- **Impuesto Único de Segunda Categoría** si hay nómina (línea 60, código 48)
- **Crédito SENCE** (línea 75, código 723)
- Ajustes por **prorrateo** cuando hay ventas mixtas
- **Separación de activo fijo** (línea 31, código 525) — la propuesta a veces lo
  mezcla con compras del giro

### Errores recurrentes que la propuesta no detecta
- Facturas de proveedores sin **acuse de recibo** dentro de 8 días → el crédito
  fiscal NO es válido aunque la propuesta lo incluya
- Boletas de honorarios que el freelancer emitió con retención pero la empresa
  no declaró → el SII cruza esta información y la observará
- Tasa de PPM desactualizada después de una Operación Renta que la modificó

---

## 7. Casos especiales frecuentes en empresas de software

### Software vendido como SaaS (suscripción mensual)

Cada cobro mensual genera una factura afecta separada. El IVA se devenga al momento
de la facturación, no al momento del cobro. Si facturas en enero pero el cliente paga
en marzo, el IVA de enero se declara en el F29 de enero igual.

### Contratos de desarrollo de largo plazo (hitos)

Si un proyecto de desarrollo tiene hitos de pago, el IVA se devenga al emitir la
factura del hito, no al inicio ni al final del proyecto completo. Si emites factura
por un anticipo, ese anticipo genera IVA en el F29 de ese mes.

### Empresa que solo exporta (sin ventas domésticas)

Si todas las ventas son exportación:
- El débito fiscal será $0 cada mes
- El crédito fiscal se acumula como remanente (código 77)
- Se debe declarar el F29 igual (sin movimiento de IVA, pero con PPM y retenciones)
- La recuperación del CF se hace por Formulario 3600, no por el F29

### Freelancers contratados como "contratistas" con factura

Si un desarrollador freelance tiene inicio de actividades y emite **factura** (no
boleta de honorarios), su factura afecta genera crédito fiscal para la empresa.
Se registra en línea 28 como cualquier otra factura de proveedor. NO va en
código 151 (eso es solo para boletas de honorarios).

### Compra de equipos (notebooks, monitores, servidores)

El IVA de equipamiento tecnológico va en línea 31 (código 525) como activo fijo,
separado de las compras del giro. Esto es importante porque:
- Si la empresa acumula mucho CF por activo fijo, puede pedir devolución anticipada
  bajo Art. 27 bis
- La propuesta del SII a veces clasifica mal estos montos

---

## 8. Rectificación del F29: cuándo y cómo

### Rectificación voluntaria (antes de que el SII detecte el error)
- Se hace en sii.cl → Impuestos Mensuales → Corregir o rectificar
- Plazo: hasta 3 años desde la fecha de vencimiento original
- Si genera mayor impuesto: se aplica reajuste IPC + interés 1,5%/mes
- La multa es condonable total o parcialmente por ser voluntaria

### Rectificación por requerimiento del SII
- El SII envía una notificación con las observaciones
- Se debe rectificar o justificar dentro del plazo indicado
- La multa base sube al 20% (vs 10% de la voluntaria)
- No resolver las observaciones puede escalar a fiscalización formal

### Qué errores justifican rectificar
- Omisión de facturas de venta (el error más grave — el SII lo detecta siempre)
- Remanente de CF incorrecto (efecto dominó en meses siguientes)
- Tasa de PPM equivocada
- Retenciones de honorarios no declaradas
- Facturas de compra digitales no registradas

---

## 9. Links oficiales de referencia

| Recurso | URL |
|---------|-----|
| Guía F29 por internet (SII) | https://www.sii.cl/pagina/iva/guia_f29.htm |
| Instrucciones línea por línea (PDF oficial) | https://www.sii.cl/servicios_online/instrucciones_f29_20241112.pdf |
| Imagen del F29 (PDF) | https://www.sii.cl/formularios/imagen/F29.pdf |
| Calendario de IVA | https://www.sii.cl/destacados/f29/index.html |
| Circular N°50/2022 — IVA servicios | https://www.sii.cl/normativa_legislacion/circulares/2022/circu50.pdf |
| Boletas de honorarios — tasas de retención | https://www.sii.cl/destacados/boletas_honorarios/aumento_gradual.html |
| Preguntas frecuentes IVA software (SII) | https://www.sii.cl/preguntas_frecuentes/impuestos_mensuales/001_130_5446.htm |
| Exportación de servicios (Subrei) | https://www.subrei.gob.cl/preguntas-frecuentes/exportacion-de-servicios |