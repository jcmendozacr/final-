# Las mejores estrategias de ETF de OKRUS en el Backtest Engine del hackathon

**Reglas:** las originales de OKRUS (`preparar.py`), leídas de `backtest_final` sin modificarlo.
**Precios:** Data Curator. **Benchmark:** KN US Equity Core. **Calendario:** señal al cierre de fin
de mes, operación el primer día hábil siguiente. **Motor:** 0.68.0, con costos base de 1 + 5 pb y de
estrés de 5 + 10 pb, y 2% de reserva de efectivo. Tabla completa: `evaluacion.csv`.

**2001–2009 es una prueba fuera de muestra para estas estrategias:** en OKRUS se diseñaron y se
probaron con datos de 2009 en adelante.

## Resultados

| Estrategia | Peso máx. | Alfa 2007–26 (estrés) | Caída 2007–26 | Sharpe 2007–26 | Alfa 2010–26 (estrés) | Alfa 2001–26 (estrés) | Caída 2001–26 | Vs KN 01–09 | Vs KN 10–17 | Vs KN 18–26 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **sector_core4_top2** | 50%¹ | **+3.73 (+3.42)** | **−33.0%** | **0.70** | **+2.94 (+2.61)** | +3.52 (+3.14) | −33.0% | **+4.7** | **+1.0** | **+5.0** |
| estrella_top1_momentum | 100% | +3.87 (+3.20) | −37.6% | 0.57 | +2.09 (+1.42) | +3.33 (+2.72) | −37.6% | +5.5 | −6.1 | +10.0 |
| sector_rotation_top2 | 50%¹ | +2.83 (+2.51) | −36.3% | 0.64 | +1.77 (+1.45) | +3.43 (+3.10) | −36.3% | +6.5 | −0.9 | +4.4 |
| sector_rotation_top1 | 100% | +2.16 (+1.68) | −33.0% | 0.55 | +0.39 (−0.11) | +3.65 (+3.18) | −33.0% | +9.7 | −3.2 | +3.7 |
| xlk_above_sma200 | 100% | +1.46 (+1.20) | −30.6% | 0.66 | −0.86 (−1.12) | +1.50 (+1.21) | −30.6% | +5.8 | −3.4 | +1.4 |
| sector_tech | 50% | +6.41 (+6.39) | −56.7% | 0.65 | +7.22 (+7.20) | +2.35 (+2.33) | **−66.7%** | **−5.5** | +3.0 | +11.6 |
| tech_growth | 50% | +4.75 (+4.73) | −53.9% | 0.67 | +5.04 (+5.02) | +1.81 (+1.79) | −61.8% | −3.5 | +3.2 | +7.0 |
| buy_hold_qqq | 100% | +4.43 (+4.43) | −52.6% | 0.68 | +3.87 (+3.87) | +1.16 (+1.15) | −66.5% | −3.3 | +3.7 | +4.2 |
| millennial_growth² | 60% | +3.75 (+3.72) | −44.9% | 0.76 | +2.91 (+2.88) | +2.79 (+2.76) | −44.9% | +2.5 | +0.8 | +5.0 |
| *Modelo principal del hackathon* | 6% | *+3.00 (+2.23)* | *−30.9%* | *0.65* | *+0.08 (−0.65)* | — | — | — | — | — |
| *A con tope de 20%* | 20% | *+1.42 (+0.60)* | *−29.3%* | *0.66* | *−0.80 (−1.64)* | *+2.60 (+1.86)* | *−29.3%* | *+6.5* | *−5.8* | *+3.8* |

¹ 50% por ETF cuando hay 2 con momentum positivo; si no, hasta 100% en SHY.
² Empieza en 2004-12 porque GLD no existía antes.

## Lectura

- **El sesgo temático se confirma.** sector_tech, tech_growth y QQQ, que apuestan a tecnología,
  tienen el mayor alfa desde 2007 y desde 2010, pero en 2001–2009 (fuera de muestra) pierden contra
  el KN y caen −62% a −67%. Su alfa depende de que la tecnología haya ganado.
- **sector_core4_top2 es la más sólida.** Rota cada mes a los 2 sectores con mayor momentum de 12
  meses entre XLK, XLF, XLE y XLY, y va a SHY si ninguno tiene momentum positivo.
  - **Le gana al KN en los tres periodos:** 2001–09 (+4.7), 2010–17 (+1.0) y 2018–26 (+5.0). Es la
    única que lo hace en los tres.
  - **Supera al modelo principal del hackathon en las dos ventanas:** +3.42% contra +2.23% con estrés
    en 2007–26, y +2.61% contra −0.65% en 2010–26.
  - Tiene una caída parecida (−33.0% contra −30.9%) y mejor Sharpe (0.70 contra 0.65).
- **Pendientes antes de adoptarla:**
  1. **El tope de 20%:** pone 50% en cada ETF. Cumple si el tope es solo para acciones individuales
     (así dice la regla 3), pero no si aplica a ETFs. Es la pregunta pendiente para los mentores.
  2. **La lista de 4 sectores:** se eligió en OKRUS. Una prueba de robustez, fijada antes, sería la
     misma regla con los 9 sectores originales de SPDR (XLK, XLF, XLE, XLY, XLV, XLP, XLI, XLU y XLB),
     para descartar que la lista esté hecha a la medida.

## Prueba de robustez: la misma regla con los 9 sectores de SPDR (`robustez9.py`, `sector_all9_top2/`)

Criterio fijado antes de correr: pasa si su alfa con estrés en 2007–2026 supera +2.23%, el del
modelo principal.

| Estrategia | Alfa 2001–26 (estrés) | Alfa 2007–26 (estrés) | Caída máx. | Sharpe 2001–26 |
| --- | --- | --- | --- | --- |
| sector_core4_top2 (4 sectores) | +3.52% (+3.14%) | +3.73% (+3.42%) | −33.0% | 0.62 |
| **sector_all9_top2 (9 sectores)** | **+0.08% (−0.59%)** | **−1.78% (−2.40%)** | −38.7% | 0.46 |

**No pasa.** Con los 9 sectores, el alfa desaparece. La ventaja de sector_core4_top2 venía de la
lista de 4 sectores elegida en OKRUS (tecnología, finanzas, energía y consumo discrecional), no de
la regla de rotación. Es sesgo de selección del universo, igual que en las estrategias de acciones.
**sector_core4_top2 se descarta y se queda el modelo principal del hackathon.**

## Filtros a priori para justificar la lista de sectores (`filtros_ciclicos.py`)

Criterio fijado antes de correr: **las dos** deben superar +2.23% de alfa con estrés en 2007–2026.

| Estrategia | Alfa 2001–26 (estrés) | Alfa 2007–26 (estrés) | Caída máx. | ¿Pasa? |
| --- | --- | --- | --- | --- |
| ciclicos6_top2: 6 SPDR no defensivos (Morningstar) | +3.11% (+2.57%) | +2.79% (+2.32%) | −32.1% | Sí, por 0.09 puntos |
| beta4_top2: los 4 de mayor beta a 3 años, cada mes | +1.33% (+0.80%) | +2.48% (+2.02%) | −32.1% | **No** |
| *Referencia: sector_core4_top2 (lista de OKRUS)* | *+3.52% (+3.14%)* | *+3.73% (+3.42%)* | *−33.0%* | — |
| *Referencia: los 9 sectores* | *+0.08% (−0.59%)* | *−1.78% (−2.40%)* | *−38.7%* | — |

**Veredicto: no pasa, porque se exigían las dos.** Se queda el modelo principal del hackathon.

Lectura:
- **La lógica de "sectores cíclicos" sí se confirma.** El filtro por beta, sin que nadie le diga
  nada, elige casi siempre sectores cíclicos (XLF, XLK, XLB, XLY, XLE y XLI) y nunca los defensivos.
  Quitar los defensivos sube el alfa de −0.6% a +2.6% (2001–26, con estrés).
- **Pero la ventaja de los 4 sectores de OKRUS no se reproduce por completo con ningún filtro
  objetivo.** Los 6 cíclicos pasan apenas, por 0.09 puntos (dentro del ruido), y el filtro por beta
  no pasa. La parte del alfa que viene de haber elegido justo XLK, XLF, XLE y XLY, y no XLI ni XLB,
  sigue sin justificación previa.
