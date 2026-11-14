# Modelo principal — régimen con 10 acciones e interruptor de volatilidad

Equipo de Habib · Talavera Valley Hackathon 2026 · Track 04 WealthTech.

> **VERSIÓN PREVIA desde el 2026-11-14.** El nuevo modelo principal es "C2 confirmada"
> (`modelo_principal_c2/MODELO_PRINCIPAL.md`): +4.28% de alfa (+3.33% con estrés) en 2007–2026.
> Este modelo sigue congelado sin cambios y es su componente de acciones.

> **CONGELADO el 2026-11-13.** Es el modelo principal del equipo. Sus reglas y parámetros no se
> cambian; cualquier variante nueva va en un documento aparte y se compara contra este. Las huellas
> md5 de la sección 11 identifican la versión congelada.
>
> Modelos anteriores, conservados como referencia: `MODELO_M2.md` (M2) y
> `ESTRATEGIA_NUCLEO_SATELITE.md` (C0).
>
> Investigación y aprendizaje, no asesoría de inversión. Las cifras vienen de un backtest sobre
> precios pasados: muestran el método, no prometen ni recomiendan nada.

---

## 1. La idea

Cada fin de mes, el modelo identifica en qué estado está el mercado y aplica la estrategia de ese
estado: concentración en las 10 acciones con más momentum cuando el mercado sube con calma, una
mezcla moderada cuando hay señales encontradas, y bonos cuando hay tendencia bajista y estrés a la
vez. Además, cada día vigila la volatilidad: si se dispara, saca las acciones a bonos de corto plazo
hasta que se calme.

**Lógica económica:**
- El momentum de acciones paga más en tendencias alcistas sin estrés (Jegadeesh y Titman, 1993), y
  su efecto es más fuerte entre las acciones más extremas.
- Las caídas largas llegan con una ruptura de tendencia (Faber, 2007) y con estrés en las tasas
  reales, que el TIP anticipa (Keller y Keuning).
- Las semanas de volatilidad extrema no pagan más, así que reducir exposición en ellas mejora el
  rendimiento ajustado por riesgo (Moreira y Muir, 2017).

---

## 2. Reglas

### 2.1 Señales mensuales (al cierre del último día hábil de cada mes)

| Señal | Definición |
| --- | --- |
| **Tendencia** | Arriba si el SPY (cierre ajustado por dividendos) es **mayor o igual** al promedio de sus últimos **10 cierres de fin de mes**, el actual incluido |
| **Canario** | OK si el momentum **13612 de TIP** es **≥ 0**: el promedio simple de sus rendimientos totales a 1, 3, 6 y 12 meses |

### 2.2 Regímenes

| Régimen | Condición | Cartera |
| --- | --- | --- |
| **Alcista** | Tendencia arriba **y** canario OK | **40% SPY + 60% en 10 acciones, 6% cada una** |
| **Mixto** | Solo una de las dos señales en alerta | **70% SPY + 30% en las mismas 10 acciones, 3% cada una** |
| **Caída** | Tendencia abajo **y** canario en alerta | **100% en el mejor de IEF o SHY**: IEF si su 13612 es mayor que el de SHY, si no SHY |

### 2.3 Las 10 acciones (iguales en alcista y en mixto)

1. **Universo:** las **300 acciones de mayor peso** del **KN US Equity Core** en la fecha de la
   señal, solo con los miembros de esa fecha.
2. **Historia mínima:** al menos **240 rendimientos diarios válidos de los últimos 252**.
3. **Señal:** momentum **12-1**, la suma de rendimientos logarítmicos diarios desde 252 hasta 21
   días hábiles atrás.
4. Se eligen las **10** con la señal más alta, con **pesos iguales**.

### 2.4 Interruptor de volatilidad (diario)

- Cada día, al cierre, se calcula la volatilidad del **SPY de los últimos 20 días**, anualizada
  (desviación estándar diaria × √252).
- Si **pasa de 35%**, al día hábil siguiente la parte en acciones (SPY + las 10) pasa a **SHY**.
- Cuando cierra **en 35% o menos**, al día hábil siguiente se vuelve a la cartera del régimen vigente.
- **En régimen de caída no actúa,** porque la cartera ya está en bonos.
- **Si coincide con un rebalanceo mensual,** se aplica sobre la cartera del nuevo régimen.

### 2.5 Operación

- **Se opera el día hábil siguiente a cada señal.** Cada mes se rebalancea completo a la cartera
  del régimen.
- **Entre rebalanceos** los pesos se mueven con los precios.
- **Empresas que dejan de cotizar:** se venden a su último precio y ese peso queda en efectivo
  hasta el siguiente rebalanceo.
- **Restricciones:** sin apalancamiento ni ventas en corto; los pesos suman 1 en cada rebalanceo.
  Ninguna acción pasa de **6%** al rebalancear, lejos del tope de 20% del reto.

---

## 3. Parámetros congelados

| Parámetro | Valor |
| --- | --- |
| Promedio de tendencia | 10 cierres de fin de mes de SPY |
| Canario | TIP, momentum 13612 ≥ 0 |
| Refugio en caída | IEF o SHY, el de mayor 13612 |
| Alcista: SPY / acciones | 0.40 / 0.60 (6.0% por acción) |
| Mixto: SPY / acciones | 0.70 / 0.30 (3.0% por acción) |
| Caída | 1.00 en el refugio |
| Número de acciones | **10** |
| Universo | top 300 por peso del KN US Equity Core |
| Momentum de acciones | 12-1 (de 252 a 21 días hábiles) |
| Historia mínima | 240 de 252 días |
| Interruptor de volatilidad | SPY, 20 días, umbral **35%**, refugio SHY |
| Rebalanceo | mensual, al día hábil siguiente, más los días del interruptor |
| Primera señal | 2006-01-31 |

Resultado del `weights.csv`: **376 tickers × 259 fechas**, del 2006-02-01 al 2026-11-02 (250
rebalanceos mensuales y 9 del interruptor). En la ventana del backtest se usan 363 tickers.

---

## 4. Datos

- **ETFs (SPY, TIP, SHY, IEF):** Data Curator 0.51.0 con la extensión Yahoo Finance 0.5.1, columna
  `m_close_dividend_and_split_adjusted`.
- **Acciones:** rendimientos del KN US Equity Factor Model (exceso de rendimiento + tasa libre de
  riesgo implícita del índice); miembros y pesos del KN US Equity Core.
- **Precios para el motor:** se usa Yahoo si cubre todo el periodo y coincide con KaxaNuk
  (correlación ≥ 0.9); si no, la serie de KaxaNuk. De los 363 tickers usados, 280 son de Yahoo y 83
  de KaxaNuk.

---

## 5. Backtest Engine 0.68.0, 2007-03-01 a 2026-11-06 (20.38 años, la ventana completa)

**Configuración:** la de `ESTRATEGIA_NUCLEO_SATELITE.md`, sección 6, con estos cambios:
- Reserva de efectivo de **2%** (con 1% el motor se detenía en un rebalanceo por falta de efectivo
  para costos).
- Precios en `datos_backtest_m2/motor` y pesos en `resultados_regimen_n10_a60/weights.csv`.
- Costos base: 1 pb de comisión + 5 pb de slippage plano. Estrés: 5 + 10 pb. $100,000 iniciales.

| | Modelo principal | Con costos de estrés | KN US Equity Core | SPY |
| --- | --- | --- | --- | --- |
| CAGR (años del motor) | **13.46%** | **12.68%** | 10.45% | 10.39% |
| **Alfa del motor** (CAGR − CAGR del KN Core) | **+3.00%** | **+2.23%** | — | — |
| Volatilidad anual | 20.74% | 20.76% | 20.01% | 19.99% |
| **Caída máxima** | **−30.87%** | −31.57% | −52.67% | −55.18% |
| Information Ratio | +0.18 | +0.15 | — | — |
| Sharpe (tasa 0) | 0.65 | 0.61 | 0.52 | 0.52 |
| Sortino (tasa 0) | 0.87 | 0.82 | 0.69 | 0.73 |
| Comisiones | $6,849 | $31,203 | — | — |
| Slippage | $32,814 | $59,722 | — | — |

- **Valor del portafolio base:** $99,942 al cierre del 2007-03-01 y **$1,310,484** el 2026-11-06.
- **Sobre el alfa del motor:** en todas las corridas, el campo "Alpha" coincide con la diferencia
  de CAGR contra el benchmark. La documentación no lo dice; se deduce de los números.

### 5.1 Por periodo (serie diaria del motor, contra el KN Core)

| Periodo | CAGR | KN Core | Exceso | Volatilidad | Caída máxima | Beta | Alfa ajustado por beta | IR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2007-03 a 2019 (diseño) | 12.6% | 9.1% | +3.5 | 17.8% | −25.1% | 0.64 | +6.8% | +0.20 |
| 2020 a 2026-11-06 | 16.6% | 14.3% | +2.3 | 25.4% | −30.9% | 0.71 | +7.6% | +0.15 |
| **Completo** | **14.0%** | 10.9% | **+3.1** | 20.7% | **−30.9%** | **0.67** | **+7.1%** | +0.17 |
| Completo, costos de estrés | 13.2% | 10.9% | +2.3 | 20.8% | −31.6% | 0.67 | +6.4% | +0.13 |

La caída máxima fue del 2021-11-09 al 2023-03-15, durante el mercado bajista de 2022, y se recuperó
el 2024-03-07. Fue una caída lenta: la volatilidad no pasó de 35% y el interruptor no se activó.

### 5.2 Por año (serie diaria del motor, costos base)

| Año | Modelo | KN Core | Exceso (puntos) |
| --- | --- | --- | --- |
| 2007 (desde el 1 de marzo) | +35.0% | +7.2% | +27.8 |
| 2008 | −11.4% | −36.9% | +25.5 |
| 2009 | +21.3% | +27.9% | −6.6 |
| 2010 | +26.0% | +16.0% | +10.0 |
| 2011 | −2.2% | +1.2% | −3.4 |
| 2012 | +23.7% | +16.5% | +7.2 |
| 2013 | +35.9% | +33.1% | +2.8 |
| 2014 | +20.3% | +12.7% | +7.6 |
| 2015 | −2.9% | +0.7% | −3.6 |
| 2016 | +5.0% | +11.5% | −6.5 |
| 2017 | +17.6% | +22.0% | −4.4 |
| 2018 | −3.9% | −4.6% | +0.7 |
| 2019 | +10.3% | +31.2% | −20.9 |
| 2020 | +51.2% | +22.3% | +28.9 |
| 2021 | +15.1% | +25.9% | −10.8 |
| 2022 | −21.1% | −20.0% | −1.1 |
| 2023 | +6.1% | +26.9% | −20.8 |
| 2024 | +40.5% | +24.8% | +15.7 |
| 2025 | +13.5% | +17.4% | −3.9 |
| 2026 (al 6 de noviembre) | +22.9% | +8.7% | +14.2 |

Le ganó al KN Core en 10 de 20 años. La ventaja se concentra en años grandes (2007, 2008, 2020,
2024) y pierde en recuperaciones rápidas (2019, 2023).

### 5.3 Fechas del interruptor de volatilidad

| Fecha | Acción |
| --- | --- |
| 2008-09-22 | sale a SHY |
| 2009-01-22 | sale a SHY |
| 2009-04-22 | regresa |
| 2011-08-10 | sale a SHY |
| 2011-09-09 | regresa |
| 2020-03-06 | sale a SHY |
| 2020-05-06 | regresa |
| 2025-04-10 | sale a SHY |
| 2025-05-09 | regresa |

Esta tabla solo lista los cambios a mitad de mes. Un cambio que cae en día de rebalanceo mensual se
aplica junto con él (por ejemplo, entre el 2008-09-22 y el 2009-01-22 hubo un regreso en un
rebalanceo). En la ventana hubo 148 meses en régimen alcista, 70 en mixto y 19 en caída.

---

## 6. Comparación con los modelos anteriores (Backtest Engine, misma ventana)

| Modelo | CAGR del motor | Alfa del motor | Caída máxima | Alfa ajustado por beta | Supera al KN Core con costos de estrés |
| --- | --- | --- | --- | --- | --- |
| **Principal (10 acciones, 60%, interruptor)** | **13.46%** | **+3.00%** | −30.9% | **+7.1%** | **Sí (12.68%)** |
| 10 acciones, 40%, interruptor | 12.51% | +2.06% | **−27.7%** | +6.2% | Sí (11.90%) |
| M2 + interruptor (20 acciones, reserva 2%) | 10.90% | +0.45% | −28.1% | +4.7% | No (10.21%) |
| M2 (20 acciones, reserva 1%) | 11.22% | +0.77% | −34.7% | +3.4% | Por poco (10.58%) |
| C0, núcleo + satélite (serie desde 2007-03) | — | — | −53.1% | +1.0% | Sí |
| KN US Equity Core | 10.45% | — | −52.7% | — | — |

---

## 7. Cómo se llegó aquí (para la lámina de método)

1. **Lógica escrita antes de probar:** momentum, tendencia, canario y volatilidad, todos con
   literatura publicada.
2. **Periodo de diseño 2007-03 a 2019;** 2020–2026 como referencia.
3. **Variantes probadas y descartadas** por empeorar en el diseño o por no ser consistentes entre
   periodos:
   - stop loss por acción y de cartera (5–15%);
   - 80–100% en momentum;
   - umbrales de volatilidad de 20–30% y volatilidad objetivo;
   - momentum residual, Clenow y la mezcla 50/50;
   - HAA puro y otras combinaciones del documento *Estrategias con Mayor CAGR Histórico*.
4. **Búsqueda de 1,728 combinaciones:** el orden del diseño casi no predijo 2020–2026 (correlación
   de rangos de +0.14 en CAGR). Por eso no se eligió "la mejor". Solo se adoptaron los parámetros
   cuyo efecto fue consistente en los dos periodos: **10 acciones** (escalonado: 10 > 20 > 30),
   **momentum 12-1** e **interruptor de 35%**.
5. **Validación en el Backtest Engine con costos de estrés:** sigue por encima del KN Core.

**Limitación honesta:** 2020–2026 se miró varias veces durante la investigación, así que no es una
prueba ciega. La evidencia a favor es la consistencia de los parámetros elegidos entre los dos
periodos y su respaldo en la literatura.

## 8. Limitaciones

1. **Concentración:** 10 acciones de momentum suelen caer en uno o dos sectores. Hoy predominan
   semiconductores y almacenamiento.
2. **Rotación alta** y costos relevantes: ~$40K en la base y ~$91K en estrés, sobre $100K iniciales
   en 20 años.
3. **Lento en las recuperaciones rápidas** (2009, 2019, 2023) y sin protección ante caídas lentas
   (2022).
4. **Volatilidad parecida a la del índice** (20.7% contra 20.0%), con beta 0.67.
5. **Datos y ejecución:** precios mixtos de Yahoo y KaxaNuk, ejecución al cierre ajustado,
   slippage plano, Sharpe con tasa 0 y corrida local, no en la plataforma web del Lab.

---

## 9. Cómo replicarlo

Entorno: el de `ESTRATEGIA_NUCLEO_SATELITE.md`, 8.1. `<KN>` es la carpeta con los CSV de los zips
de KaxaNuk (incluye `KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv`).

```bash
# 1. ETFs con el Data Curator
.venv/bin/python descargar_precios.py <lista con SPY, TIP, SHY, IEF> datos_etf/precios 2000-01-01

# 2. Señales, regímenes, interruptor y weights.csv (umbral 0.35, 10 acciones, 60% en alcista)
.venv/bin/python modelo_regimen.py <KN> datos_etf/precios resultados_regimen_n10_a60 0.35 10 0.60

# 3. Precios de las acciones y carpeta del motor
cp datos_etf/precios/{SPY,SHY,IEF}.csv datos_backtest_m2/precios/
.venv/bin/python descargar_precios.py resultados_regimen_n10_a60/tickers_para_curator.csv datos_backtest_m2/precios 2000-01-01
.venv/bin/python preparar_motor.py <KN> resultados_regimen_n10_a60/weights.csv datos_backtest_m2/precios datos_backtest_m2/motor 2006-01-01

# 4. Backtest Engine, base y estrés, con 2% de reserva de efectivo
KNBE_API_KEY_KAXANUK=<LICENCIA> .venv/bin/python correr_backtest.py datos_backtest_m2/motor resultados_regimen_n10_a60 weights resultados_regimen_n10_a60/backtest_base_r2 2007-03-01 2026-11-06 1.0 5.0 0.02
KNBE_API_KEY_KAXANUK=<LICENCIA> .venv/bin/python correr_backtest.py datos_backtest_m2/motor resultados_regimen_n10_a60 weights resultados_regimen_n10_a60/backtest_estres_r2 2007-03-01 2026-11-06 5.0 10.0 0.02
```

## 10. Puntos de control

- **`weights.csv`:** 376 × 259, del 2006-02-01 al 2026-11-02, peso máximo por acción 0.06.
- **Última señal (2026-10-30), operada el 2026-11-02**, solo como control, no como recomendación:
  régimen **alcista** (tendencia arriba, canario OK). SPY 40% y DELL, INTC, LITE, MRNA, MRVL, MU,
  RVMD, SNDK, STX y WDC, con 6% cada una.
- **`backtest_base_r2/resumen.json`:** ventana valuada del 2007-03-01 al 2026-11-06, CAGR 0.1346,
  Information Ratio 0.1846, caída máxima −0.3087.

## 11. Huellas de la versión congelada (md5)

| Archivo | md5 |
| --- | --- |
| `resultados_regimen_n10_a60/weights.csv` | `131c0e1b40220654c08ea849244f74c0` |
| `modelo_regimen.py` | `aa27c835a0f734733e021abd44781e8c` |
| `nucleo_satelite.py` | `81d9ef51a2eb6ea726c83bb942b1ca48` |
| `descargar_precios.py` | `f09d432349ca52c430d2d8ff389f4b5e` |
| `preparar_motor.py` | `29e85d5015cc5d83fc5ce4b7d1393458` |
| `correr_backtest.py` | `99d07e7b1e3a749be056d63b0ead623b` |
| `datos_etf/precios/SPY.csv` | `809149bf9de075c53b9e954f48a20a44` |
| `datos_etf/precios/TIP.csv` | `12f85060a9f9ebf283b369c890dbce88` |
| `datos_etf/precios/SHY.csv` | `8302231f7aff89aad81ebaea5348597b` |
| `datos_etf/precios/IEF.csv` | `f0d12b5451a7622a8fa2bd3c83e8db60` |
| `KN_US_Equity_Core.zip` | `91712db0c1ef01c2e7d38f7fd63d05cb` |
| `KN_US_Equity_Factor_Model.zip` | `07d373b44738763fbf520d1fa7f49f25` |

## 12. Referencias

- Jegadeesh, N. y Titman, S. (1993). *Returns to Buying Winners and Selling Losers.* Journal of Finance.
- Faber, M. (2007). *A Quantitative Approach to Tactical Asset Allocation* (regla de 10 meses).
- Keller, W. y Keuning, J. *Hybrid Asset Allocation* (canario TIP, momentum 13612), SSRN.
- Moreira, A. y Muir, T. (2017). *Volatility-Managed Portfolios.* Journal of Finance.
- McLean, R. D. y Pontiff, J. (2016). *Does Academic Research Destroy Stock Return Predictability?* Journal of Finance.
- *Estrategias con Mayor CAGR Histórico* (documento del equipo).
