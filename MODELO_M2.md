# Modelo M2 — modelo de régimen (anterior)

> **Ya no es el modelo principal.** Desde el 2026-11-13 el modelo principal congelado es el modelo
> de régimen con 10 acciones e interruptor de volatilidad: ver `MODELO_ACTUAL.md`. Este documento se
> conserva como referencia.

Equipo de Habib · Talavera Valley Hackathon 2026 · Track 04 WealthTech.
Fue el modelo vigente el 2026-11-13, entre la estrategia núcleo + satélite
(`ESTRATEGIA_NUCLEO_SATELITE.md`, aquí C0) y el modelo principal actual.

> Investigación y aprendizaje, no asesoría de inversión. Las cifras vienen de un backtest sobre
> precios pasados: muestran el método, no prometen ni recomiendan nada.

---

## 1. La idea

Cada fin de mes, el modelo identifica en qué estado está el mercado con dos señales públicas y
aplica la estrategia que la literatura respalda para ese estado:

- **Concentración en momentum** cuando el mercado sube con calma.
- **Una mezcla moderada** cuando hay señales encontradas.
- **Bonos** cuando hay tendencia bajista y estrés a la vez.

**Lógica económica, escrita antes de probarlo:**
- El momentum de acciones paga más cuando el mercado está en tendencia alcista y sin estrés.
- Las caídas fuertes suelen llegar con una ruptura de la tendencia (Faber, 2007) y con estrés en
  las tasas reales, que el TIP anticipa (Keller y Keuning).
- Cuando las dos señales avisan a la vez, conviene proteger capital en bonos del Tesoro.

---

## 2. Señales (al cierre del último día hábil de cada mes)

| Señal | Definición | Fuente |
| --- | --- | --- |
| **Tendencia** | Arriba si el precio de SPY (cierre ajustado por dividendos) es **mayor o igual** al promedio de sus últimos **10 cierres de fin de mes**, el actual incluido | Faber (2007) |
| **Canario** | OK si el momentum **13612 de TIP** es **≥ 0** | Keller y Keuning, HAA (2023) |
| Momentum 13612 | Promedio simple de los rendimientos totales a 1, 3, 6 y 12 meses, medidos entre cierres de fin de mes | Keller y Keuning |

## 3. Regímenes y qué hace en cada uno

| Régimen | Condición | Cartera |
| --- | --- | --- |
| **Alcista** | Tendencia arriba **y** canario OK | **40% SPY + 60%** en las 20 acciones de mayor momentum, **3.0% cada una** |
| **Mixto** | Solo una de las dos señales en alerta | **70% SPY + 30%** en las mismas 20 acciones, **1.5% cada una** |
| **Caída** | Tendencia abajo **y** canario en alerta | **100%** en el mejor de **SHY o IEF**: IEF si su 13612 es mayor que el de SHY, si no SHY |

## 4. Cómo se eligen las 20 acciones (igual en alcista y en mixto)

1. **Universo:** las **300 acciones de mayor peso** del **KN US Equity Core** en la fecha de la
   señal, contando solo a los miembros de esa fecha.
2. **Historia mínima:** al menos **240 rendimientos diarios válidos de los últimos 252**.
3. **Señal:** momentum **12-1**, la suma de rendimientos logarítmicos diarios desde 252 días
   hábiles atrás hasta 21 días hábiles atrás.
4. Se eligen las **20** con la señal más alta, con **pesos iguales**.

## 5. Operación

- **Se opera el día hábil siguiente a la señal.** Cada mes se rebalancea completo a la cartera
  del régimen.
- **Entre rebalanceos** los pesos se mueven con los precios.
- **Empresas que dejan de cotizar:** se venden a su último precio y ese peso queda en efectivo
  hasta el siguiente rebalanceo.
- **Restricciones:** sin apalancamiento ni ventas en corto; los pesos suman 1 en cada rebalanceo.
  Ninguna acción pasa de 3% al rebalancear, muy debajo del tope de 20% del reto.

---

## 6. Parámetros

| Parámetro | Valor | Dónde vive |
| --- | --- | --- |
| Promedio de tendencia | 10 cierres de fin de mes de SPY | `modelo_regimen.py`, `trend` |
| Canario | TIP, momentum 13612 ≥ 0 | `momentum_13612()` |
| Refugio | mejor de SHY o IEF por 13612 | `main()` |
| Alcista: SPY / satélite | 0.40 / 0.60 | `WEIGHTS["alcista"]` |
| Mixto: SPY / satélite | 0.70 / 0.30 | `WEIGHTS["mixto"]` |
| Caída | 1.00 en el refugio | `main()` |
| Número de acciones | 20 | `STOCKS` |
| Peso por acción | 0.030000 en alcista, 0.015000 en mixto (6 decimales, hacia abajo) | `main()` |
| Universo | 300 de mayor peso del KN Core | `nucleo_satelite.UNIVERSE_SIZE` |
| Ventana de momentum | 252 días hábiles, sin los últimos 21 | `nucleo_satelite.signals()` |
| Historia mínima | 240 de 252 días | `nucleo_satelite.signals()` |
| Primera señal | 2006-01-31 | `FIRST_SIGNAL` |

Resultado del `weights.csv`: **537 tickers × 250 rebalanceos**, del **2006-02-01** al
**2026-11-02**. El backtest se corre desde el **2007-03-01**, la ventana en que el modelo se eligió.

---

## 7. Datos

- **ETFs (SPY, TIP, SHY, IEF):** Data Curator 0.51.0 con la extensión Yahoo Finance 0.5.1, columna
  `m_close_dividend_and_split_adjusted`, desde el 2000-01-01. TIP cotiza desde el 2003-12-05.
- **Acciones:** rendimientos del KN US Equity Factor Model (exceso de rendimiento + tasa libre de
  riesgo implícita del índice; ver `ESTRATEGIA_NUCLEO_SATELITE.md`, 5.2). Miembros y pesos del
  KN US Equity Core.
- **Precios para el motor:** la misma regla de `preparar_motor.py`. Se usa Yahoo si cubre todo el
  periodo y coincide con KaxaNuk (correlación ≥ 0.9); si no, la serie de KaxaNuk. Resultado: 400
  de Yahoo y 137 de KaxaNuk. Detalle en `datos_backtest_m2/fuente_de_precios.csv`.

---

## 8. Backtest Engine 0.68.0, 2007-03-01 a 2026-11-06 (20.38 años, la ventana completa)

Configuración idéntica a la de `ESTRATEGIA_NUCLEO_SATELITE.md`, sección 6, con estos cambios:
precios en `datos_backtest_m2/motor` y pesos en `resultados_regimen_m2/weights.csv`. Costos base: 1
pb de comisión y 5 pb de slippage plano. Estrés: 5 y 10 pb. $100,000 iniciales y 1% de efectivo de
reserva.

| | M2 base | M2 estrés | KN US Equity Core | SPY |
| --- | --- | --- | --- | --- |
| CAGR (años del motor) | **11.22%** | 10.58% | 10.45% | 10.39% |
| Volatilidad anual | 20.82% | 20.84% | 20.01% | 19.99% |
| **Caída máxima** | **−34.73%** | −34.79% | −52.67% | −55.18% |
| Alfa (campo del motor) | +0.77% | +0.13% | — | — |
| Information Ratio | +0.09 | +0.04 | — | — |
| Sharpe (tasa 0) | 0.54 | 0.51 | 0.52 | 0.52 |
| Sortino (tasa 0) | 0.72 | 0.68 | 0.69 | 0.73 |
| Comisiones | $4,612 | $21,355 | — | — |
| Slippage | $21,998 | $40,693 | — | — |

**Calculado con la serie diaria del motor, contra el KN Core:**
- **Costos base:** CAGR 11.7% contra 10.9%, beta 0.80, alfa ajustado por beta +3.4%, IR +0.07.
- **Costos de estrés:** CAGR 11.0%, alfa +2.8%, IR +0.03.
- **Por qué hay dos alfas:** el campo "Alpha" del motor usa una definición que su documentación no
  aclara. Para citar, di cuál de los dos usas.

**Valor y caída máxima:**
- **Valor del portafolio base:** $99,941 al cierre del 2007-03-01 y **$873,691** el 2026-11-06.
- **La caída máxima, −34.7%,** fue en la caída por COVID: del 19 de febrero al 23 de marzo de 2020,
  recuperada el 17 de julio de 2020. Era régimen alcista, y una señal mensual no alcanza a reaccionar
  a una caída de un mes.

**Regímenes en la ventana:** 148 meses alcista, 70 mixto y 19 caída, con 59 cambios de régimen.

### Por año (serie diaria del motor, costos base)

| Año | M2 | KN Core | SPY | Exceso (puntos) |
| --- | --- | --- | --- | --- |
| 2007 (desde el 1 de marzo) | +25.7% | +7.2% | +6.0% | +18.5 |
| 2008 | −19.0% | −36.9% | −36.8% | +17.9 |
| 2009 | +19.3% | +27.9% | +26.4% | −8.6 |
| 2010 | +18.4% | +16.0% | +15.1% | +2.4 |
| 2011 | −1.9% | +1.2% | +1.9% | −3.1 |
| 2012 | +18.8% | +16.5% | +16.0% | +2.3 |
| 2013 | +38.7% | +33.1% | +32.3% | +5.6 |
| 2014 | +17.0% | +12.7% | +13.5% | +4.3 |
| 2015 | −3.8% | +0.7% | +1.2% | −4.5 |
| 2016 | +9.5% | +11.5% | +12.0% | −2.0 |
| 2017 | +14.3% | +22.0% | +21.7% | −7.7 |
| 2018 | −1.7% | −4.6% | −4.6% | +2.8 |
| 2019 | +13.2% | +31.2% | +31.2% | −18.0 |
| 2020 | +37.0% | +22.3% | +18.3% | +14.8 |
| 2021 | +19.6% | +25.9% | +28.7% | −6.3 |
| 2022 | −18.9% | −20.0% | −18.2% | +1.1 |
| 2023 | +4.8% | +26.9% | +26.2% | −22.1 |
| 2024 | +39.5% | +24.8% | +24.9% | +14.8 |
| 2025 | +16.2% | +17.4% | +17.7% | −1.2 |
| 2026 (al 6 de noviembre) | +6.2% | +8.7% | +8.7% | −2.6 |

Le ganó al KN Core en **10 de 20 años**. Su ventaja viene de pocos años grandes (2007, 2008, 2020,
2024) y pierde en las recuperaciones rápidas (2009, 2019, 2023).

### Comparación con el modelo anterior (C0), misma ventana, serie diaria del motor

| | M2 (actual) | C0 (anterior) | KN Core |
| --- | --- | --- | --- |
| CAGR 2007-03 a 2026-11 | 11.7% | 11.9% | 10.9% |
| Caída máxima | **−34.7%** | −53.1% | −52.7% |
| Beta | 0.80 | 1.02 | 1.00 |
| Alfa ajustado por beta | **+3.4%** | +1.0% | — |
| IR | +0.07 | +0.21 | — |
| CAGR 2020 a 2026-11 | 13.7% | 16.8% | 14.3% |

---

## 9. Cómo se eligió (y qué no es)

- **El proceso:**
  - Se probaron, en un simulador propio, cinco combinaciones del documento *Estrategias con Mayor
    CAGR Histórico* (C0 a C4) y dos variantes de régimen (M1 y M2), con reglas y parámetros fijados
    antes de correrlas.
  - El periodo de diseño fue del 2007-03 al 2019-12.
  - M2 fue la de mayor CAGR en el diseño (12.0% contra 9.0% del KN Core en el simulador). Ese es el
    objetivo de máximo rendimiento que fijó Habib.
- **Limitación importante:** el modelo de régimen se diseñó **después de haber visto 2020–2026**
  con otras estrategias, así que ese periodo es **referencia, no prueba ciega**.
- **Las cifras citables son las del Backtest Engine** (sección 8). Las del simulador fueron
  mayores (CAGR 12.4%, alfa +4.0%) porque su ejecución era más barata.

## 10. Limitaciones

1. **Rotación alta:** cada cambio de régimen mueve entre 30% y 100% de la cartera. Con costos de
   estrés, el CAGR queda casi igual al del KN Core.
2. **Lento en las recuperaciones:** 2009, 2019 y 2023 quedaron entre 9 y 22 puntos debajo del
   índice, porque las señales mensuales reaccionan con meses de retraso.
3. **No protege contra caídas de un mes,** como la de COVID en 2020: su peor caída, −34.7%, fue ahí.
4. **Más volatilidad que el índice** (20.8% contra 20.0%), por la concentración del régimen alcista.
5. **Mismas limitaciones de datos y ejecución que C0:** precios mixtos de Yahoo y KaxaNuk,
   ejecución al cierre ajustado, slippage plano, Sharpe con tasa 0 y corrida local, no en la
   plataforma web del Lab.

---

## 11. Cómo replicarlo

Entorno: el de `ESTRATEGIA_NUCLEO_SATELITE.md`, 8.1. `<KN>` es la carpeta con los CSV de los dos
zips de KaxaNuk.

```bash
# 1. ETFs con el Data Curator (SPY, TIP, SHY, IEF y el resto del universo HAA)
.venv/bin/python descargar_precios.py <lista con SPY, TIP, SHY, IEF> datos_etf/precios 2000-01-01

# 2. Señales, regímenes y weights.csv
.venv/bin/python modelo_regimen.py <KN> datos_etf/precios resultados_regimen_m2

# 3. Precios de las acciones y carpeta del motor
cp datos_etf/precios/{SPY,SHY,IEF}.csv datos_backtest_m2/precios/
.venv/bin/python descargar_precios.py resultados_regimen_m2/tickers_para_curator.csv datos_backtest_m2/precios 2000-01-01
.venv/bin/python preparar_motor.py <KN> resultados_regimen_m2/weights.csv datos_backtest_m2/precios datos_backtest_m2/motor 2006-01-01

# 4. Backtest Engine, base y estrés
KNBE_API_KEY_KAXANUK=<LICENCIA> .venv/bin/python correr_backtest.py datos_backtest_m2/motor resultados_regimen_m2 weights resultados_regimen_m2/backtest_base 2007-03-01 2026-11-06 1.0 5.0
KNBE_API_KEY_KAXANUK=<LICENCIA> .venv/bin/python correr_backtest.py datos_backtest_m2/motor resultados_regimen_m2 weights resultados_regimen_m2/backtest_estres 2007-03-01 2026-11-06 5.0 10.0
```

**Puntos de control:**
- **`weights.csv`:** 537 × 250, del 2006-02-01 al 2026-11-02, md5 `8663ddc7480cf4713745431c9d13ee18`.
- **md5 de los ETFs usados:** SPY `809149bf9de075c53b9e954f48a20a44`, TIP
  `12f85060a9f9ebf283b369c890dbce88`, SHY `8302231f7aff89aad81ebaea5348597b` e IEF
  `f0d12b5451a7622a8fa2bd3c83e8db60`. Yahoo puede cambiar sus datos con el tiempo.
- **Última señal (2026-10-30), operada el 2026-11-02**, solo como control, no como recomendación:
  régimen **alcista** (tendencia arriba, canario OK). SPY 40% y AMAT, AMD, COHR, DELL, HPE, ILMN,
  INTC, KEYS, LITE, LRCX, MPC, MRNA, MRVL, MU, RVMD, SNDK, STX, TER, VLO y WDC, con 3% cada una.
- **`backtest_base/resumen.json`:** ventana valuada del 2007-03-01 al 2026-11-06, CAGR 0.1122,
  Information Ratio 0.0863.

## 12. Referencias

- Faber, M. (2007). *A Quantitative Approach to Tactical Asset Allocation* (regla de 10 meses).
- Keller, W. y Keuning, J. *Hybrid Asset Allocation* (canario TIP y momentum 13612), SSRN.
- Jegadeesh, N. y Titman, S. (1993). *Returns to Buying Winners and Selling Losers.* Journal of Finance.
- *Estrategias con Mayor CAGR Histórico* (documento del equipo), arquitectura núcleo táctico + satélite.
