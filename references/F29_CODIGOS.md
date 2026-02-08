# Referencia Completa de Códigos del Formulario 29

## Encabezado

| Campo | Descripción |
|-------|-------------|
| RUT | Rol Único Tributario del contribuyente |
| Período Tributario | Mes y año (ej: 01-2026 para enero 2026) |
| Folio | Asignado automáticamente por el SII al declarar por internet |
| Razón Social | Nombre o razón social del contribuyente |

---

## ANVERSO — DÉBITO FISCAL (Líneas 1–23)

### Líneas Informativas (no generan débito directo)

| Línea | Cód. Cantidad | Cód. Monto Neto | Descripción | Notas Software |
|-------|--------------|-----------------|-------------|----------------|
| 1 | 585 | 20 | Exportaciones: facturas de exportación emitidas | **CLAVE para software exportado**. Monto neto en pesos. Exentas de IVA. |
| 2 | 586 | 142 | Ventas y/o servicios exentos del giro | Sociedades de profesionales exentas Art. 12 E N°8. |
| 3 | 731 | 732 | Ventas con retención sobre margen (contribuyente retenido) | No aplica habitualmente a software. |
| 4 | 714 | 715 | Ventas exentas que NO son del giro | Ventas esporádicas exentas. |
| 5 | 515 (cant.) | 587 (neto) | Facturas de compra recibidas con retención total + facturas de inicio | **IMPORTANTE**: Aquí van las facturas de compra emitidas a proveedores digitales extranjeros (AWS, Azure, etc.). |
| 6 | — | 720 | Facturas de compra con retención parcial (contribuyente retenido) | Poco frecuente en software. |

### Líneas Generadoras de Débito (+) y Reducciones (−)

| Línea | Cód. Cantidad | Cód. Débito/Monto | Signo | Descripción | Notas Software |
|-------|--------------|-------------------|-------|-------------|----------------|
| 7 | 503 | 502 | **+** | **Facturas afectas del giro** | ⭐ LÍNEA PRINCIPAL: IVA de todas las facturas de venta de servicios de desarrollo, licencias, consultoría. Código 502 = IVA (19% del neto). |
| 8 | 763 | 764 | + | Facturas venta bienes inmuebles | No aplica a software. |
| 9 | 716 | 717 | + | Facturas y ND ventas NO del giro (activo fijo) | Si vendes un equipo usado. |
| 10 | 110 | 111 | + | Boletas manuales y vales máquinas | Poco frecuente en software B2B. |
| 11 | 758 | 759 | + | Boletas electrónicas / transacciones POS | Ventas menores con boleta. |
| 12 | 512 | 513 | **+** | **Notas de débito emitidas** | Ajustes al alza de precio a clientes. |
| 13 | 509 | 510 | **−** | **Notas de crédito emitidas** | Anulaciones, descuentos, ajustes a la baja. |
| 14 | 708 | 709 | − | NC por anulación ventas con POS/vales | — |
| 15 | 733 | 734 | − | NC por ventas NO del giro | — |
| 16 | 516 | 517 | + | Facturas de compra retención parcial (fracción no retenida) | — |
| 17 | 500 | 501 | + | Liquidaciones y liquidaciones-factura | Mandatos. |
| 18 | — | 154 | + | Adiciones: devolución excedente Art. 27 bis | — |
| 19 | — | 518 | + | Restitución adicional Art. 27 bis (operaciones exentas) | — |
| 20 | — | 713 | + | Reintegro Timbres + IVA arriendo amoblado esporádico | — |
| 21 | — | 738, 739, 740, 741 | + | Adiciones por IEPD (combustibles) | No aplica a software. |
| 22 | — | 791 | + | Restitución remanente CF IVA devuelto | — |
| **23** | — | **538** | **=** | **TOTAL DÉBITOS** | Suma líneas 7 a 22. |

---

## ANVERSO — CRÉDITO FISCAL (Líneas 24–49)

### Líneas Informativas

| Línea | Cód. Cantidad | Cód. IVA/Monto | Descripción | Notas Software |
|-------|--------------|----------------|-------------|----------------|
| 24 | 511 | 514 | IVA total en DTE recibidos (referencial, con y sin derecho a CF) | Solo informativo. |
| 25 | 564 | 521 | Compras internas afectas SIN derecho a crédito fiscal | Gastos no relacionados al giro. |
| 26 | 566 | 560 | Importaciones SIN derecho a CF | — |
| 27 | 584 | 562 | Compras internas exentas o no gravadas | — |

### Líneas Generadoras de Crédito

| Línea | Cód. Cantidad | Cód. Crédito | Signo | Descripción | Notas Software |
|-------|--------------|-------------|-------|-------------|----------------|
| 28 | 519 | 520 | **+** | **Facturas recibidas del giro con derecho a CF** | ⭐ LÍNEA PRINCIPAL: IVA de arriendos, internet, servicios cloud, insumos. |
| 29 | 761 | 762 | + | Facturas supermercados/comercios | Compras menores. |
| 30 | 765 | 766 | + | Facturas inmuebles | No aplica habitualmente. |
| 31 | 524 | 525 | **+** | **Facturas activo fijo** | ⭐ IVA de computadores, servidores, monitores. Separar porque permite Art. 27 bis. |
| 32 | 527 | 528 | **−** | NC recibidas (y emitidas asociadas a FC) | Reducen crédito. |
| 33 | 531 | 532 | + | ND recibidas (y emitidas asociadas a FC) | Aumentan crédito. |
| 34 | 534 | 535 | + | DIN importaciones del giro | IVA en importación de hardware/software. |
| 35 | 536 | 553 | + | DIN importaciones activo fijo | — |
| 36 | — | 504 | **+** | **Remanente CF del mes anterior** | ⭐ CRÍTICO: Debe coincidir con código 77 del F29 anterior. |
| 37 | — | 593 | − | Devolución Art. 36 (IVA exportador solicitada) | Si se pidió devolución de CF por exportaciones. |
| 38 | — | 594 | − | Devolución Art. 27 bis (activo fijo) | — |
| 39 | — | 592 | − | Certificado imputación Art. 27 bis | — |
| 40 | — | 539 | − | Devolución Art. 3° cambio de sujeto | — |
| 41 | — | 718 | − | Devolución Ley 20.258 (generadoras eléctricas) | No aplica. |
| 42 | — | 790 | − | Devolución reembolso remanente CF | — |
| 43 | — | 164 | + | Reintegro por devoluciones indebidas | — |
| 44 | — | 730, 742, 743, 127 | + | Recuperación IEPD Art. 7° Ley 18.502 | No aplica a software. |
| 45 | — | 729, 744, 745, 544 | + | Recuperación IEPD transportistas | No aplica. |
| 46 | — | 523 | + | Crédito Zona Franca Extensión | — |
| 47 | — | 712 | + | Crédito Impuesto Timbres y Estampillas | — |
| 48 | — | 757 | + | Crédito IVA restituido aportantes sin domicilio | — |
| **49** | — | **537** | **=** | **TOTAL CRÉDITOS** | Suma líneas 28 a 48. |

---

## DETERMINACIÓN DEL IVA (Línea 50)

| Código | Nombre | Cálculo |
|--------|--------|---------|
| **89** | IVA Determinado (Débito > Crédito) | código 538 − código 537 (cuando 538 > 537) |
| **77** | Remanente de Crédito Fiscal (Crédito > Débito) | código 537 − código 538 (cuando 537 > 538) |
| 756 | IVA determinado parcialmente postergado | Postergación Art. 64 DL 825 (PYME). |
| 755 | IVA postergado neto | Monto efectivamente postergado. |

---

## RETENCIONES DE IMPUESTO A LA RENTA (Líneas 59–68)

| Línea | Código(s) | Descripción | Notas Software |
|-------|----------|-------------|----------------|
| 59 | 50 | Retención Impuesto 1ra Categoría sobre rentas Art. 20 N°2 | Poco frecuente. |
| 60 | 751, 735, **48** | **Impuesto Único Segunda Categoría (IUSC)** sobre sueldos | ⭐ Retención mensual a empleados. Código 48 = impuesto neto. |
| 61 | **151** | **Retención honorarios Art. 42 N°2** | ⭐ Retención a freelancers. Tasa 2026 = 15,25%. |
| 62 | 153 | Retención 10% dietas directores S.A. | Solo si hay directorio. |
| 63 | 49 | Retención adicional 3% Art. 42 N°1 (préstamo tasa 0%) | — |
| 64 | 155 | Retención adicional 3% Art. 42 N°2 (préstamo tasa 0%) | — |
| 65 | 54 | Retención suplementeros 0,5% | No aplica. |
| 66 | 56 | Retención compra productos mineros | No aplica. |
| 67 | 588 | Retención seguros dotales 15% | — |
| 68 | 589 | Retención APV retiros 15% | — |

---

## PAGOS PROVISIONALES MENSUALES — PPM (Líneas 69–78)

| Línea | Código(s) principales | Descripción | Notas Software |
|-------|----------------------|-------------|----------------|
| 69 | 750 (suspensión), 30 (pérdida), **563** (base), **115** (tasa), 68 (crédito), **62** (PPM neto) | ⭐ **PPM 1ra Categoría Art. 84 a)** | Línea principal. Base = ingresos netos. Tasa según régimen. |
| 70 | 156 | PPM adicional 3% préstamo tasa 0% | — |
| 71–73 | Varios | PPM minería | No aplica. |
| 74 | 66 | PPM transportistas renta presunta | No aplica. |
| 75 | **721**, 722, **724**, **723** | **Crédito SENCE (capacitación)** | Imputar gastos capacitación contra PPM. 721=crédito mes, 722=remanente anterior, 723=aplicado, 724=remanente siguiente. |
| 76 | 152 | PPM 2da Categoría Art. 84 b) | Profesionales independientes. |
| 77 | 157 | PPM Taller Artesanal | No aplica. |
| 78 | 70 | PPM sobre Renta Líquida Provisional | — |

---

## SUBTOTAL Y TOTAL A PAGAR (Líneas 80, 141–144)

| Línea | Código | Descripción | Cálculo |
|-------|--------|-------------|---------|
| 80 | **595** | Subtotal impuesto determinado anverso | código 89 + retenciones (48+151+153+...) + PPM (62) − crédito SENCE (723) |
| 141 | **91** | **TOTAL A PAGAR EN PLAZO LEGAL** | código 595 + impuestos adicionales reverso (si aplica) |
| 142 | 92 | Más IPC (reajuste por atraso) | Solo si se paga fuera de plazo |
| 143 | 93 | Más intereses (1,5%/mes) y multas | Solo si se paga fuera de plazo |
| 144 | **94** | **TOTAL A PAGAR CON RECARGO** | código 91 + código 92 + código 93 |

---

## PLAZOS DE DECLARACIÓN

| Medio de declaración | Plazo |
|---------------------|-------|
| Internet (sii.cl) + facturador electrónico | Día **20** del mes siguiente |
| Papel / no facturador electrónico | Día **12** del mes siguiente |
| Si cae en feriado/fin de semana | Se traslada al siguiente día hábil |

---

## MULTAS POR ATRASO

| Concepto | Monto |
|----------|-------|
| Multa base (declaración con pago) | 10% del impuesto adeudado |
| Incremento por mes adicional (después de 5 meses) | +2% mensual |
| Tope multa (presentación voluntaria) | 30% |
| Tope multa (detectada por SII) | 60% (base 20%) |
| Intereses por mora | 1,5% mensual sobre monto reajustado |
| Multa declaración sin movimiento fuera de plazo | 1 UTM a 1 UTA |
| No declarar (consecuencia) | Estado "Inconcurrente a Operación IVA" — bloqueo total |

---

## CÓDIGOS DE ESTADO DEL F29 POST-ENVÍO

| Estado | Significado | Acción requerida |
|--------|-------------|-----------------|
| O | No observada | Todo correcto. Ninguna. |
| S | Observación secundaria | Discrepancias menores. Revisar. |
| I | Impugnada | Inconsistencias graves. Rectificar o justificar ante SII. |