# Estrategia Núcleo ETF + Satélite de Momentum

> **Ya no es el modelo actual.** El modelo principal congelado está en `MODELO_ACTUAL.md`. El
> modelo M2, intermedio, está en `MODELO_M2.md`. Este documento se conserva como referencia (en los
> otros dos se llama C0).

Equipo de Habib · Talavera Valley Hackathon 2026 · Track 04 WealthTech.
Documento de replicación: reglas, parámetros, universo, datos, configuración de los motores,
resultados y pasos para reproducir cada número. Corridas del 2026-11-13.

> Investigación y aprendizaje, no asesoría de inversión. Las cifras vienen de un backtest sobre
> precios pasados: muestran el método, no prometen ni recomiendan nada.

---

## 1. La idea en una frase

Mantener casi todo el portafolio en el mercado con un ETF (para no alejarse del benchmark) y usar
una parte pequeña para comprar las acciones grandes que más han subido en el último año, sin contar
el último mes, porque esas tienden a seguir rindiendo más unos meses.

**Lógica económica, escrita antes del backtest.** El momentum de 12 meses menos el último
(Jegadeesh y Titman, 1993; Asness, Moskowitz y Pedersen, 2013) es una de las primas mejor
documentadas en acciones. Se excluye el último mes porque en horizontes de un mes los rendimientos
tienden a revertirse. El núcleo mantiene la beta cerca de 1, así que el exceso sobre el benchmark
no viene de tomar más o menos mercado.

---

## 2. Reglas

| # | Regla |
| --- | --- |
| R1 | **Núcleo:** 70% del portafolio en **SPY**. |
| R2 | **Satélite:** 30% del portafolio en **20 acciones**, con **1.5% cada una** (pesos iguales). |
| R3 | **Universo elegible:** en la fecha de la señal, las **300 acciones de mayor peso** dentro del **KN US Equity Core**, contando solo a los miembros de esa fecha (sin sesgo de supervivencia). |
| R4 | **Historia mínima:** la acción debe tener al menos **240 rendimientos diarios válidos de los últimos 252**. |
| R5 | **Señal de momentum 12-1:** suma de los rendimientos logarítmicos diarios desde 252 días hábiles atrás hasta 21 días hábiles atrás. Se eligen las 20 con la señal más alta. |
| R6 | **Calendario:** la señal se calcula al **cierre del último día hábil de cada mes**; se opera el **día hábil siguiente**. |
| R7 | **Rebalanceo completo cada mes:** se vuelve a 70% SPY + 20 acciones a 1.5%. Entre rebalanceos los pesos se mueven con los precios. |
| R8 | **Empresas que dejan de cotizar:** se venden a su último precio; ese peso queda en efectivo hasta el siguiente rebalanceo. |
| R9 | **Tope del reto:** ninguna acción pasa de 1.5% al rebalancear, muy por debajo del máximo de 20%. |
| R10 | **Sin apalancamiento ni ventas en corto.** Los pesos suman exactamente 1 en cada rebalanceo. |

**Excepción del inicio (solo la señal del 1999-12-31).** Los rendimientos por acción de KaxaNuk
empiezan el 2000-01-03. Para tener una señal en diciembre de 1999 se reconstruyen los rendimientos
de 1999 (sección 5.3), y como los pesos del índice empiezan el 1998-12-31, esa primera ventana
tiene 251 días en vez de 252. Desde la señal del 2001-01-31 la regla se aplica sin ninguna
excepción.

---

## 3. Parámetros

| Parámetro | Valor | Dónde vive |
| --- | --- | --- |
| ETF del núcleo | `SPY` | `nucleo_satelite.py`, `CORE_ETF` |
| Peso del núcleo | 0.70 | `CORE_WEIGHT` |
| Número de acciones | 20 | `N_STOCKS` |
| Peso por acción | 0.015000 (6 decimales, redondeo hacia abajo) | `STOCK_WEIGHT` |
| Tamaño del universo | 300 de mayor peso en el índice | `UNIVERSE_SIZE` |
| Ventana de momentum | 252 días hábiles, sin los últimos 21 | `signals()` |
| Historia mínima | 240 de 252 días con dato | `signals()` |
| Primera señal | 1999-12-31 | argumento 3 |
| Reconstrucción de 1999 | activada | argumento 4, `reconstruir-1999` |
| Costo en la prueba exploratoria | 10 pb por unidad de rotación | `COST` (solo la prueba rápida) |

Resultado: **323 rebalanceos**, del **2000-01-03** al **2026-11-02**, **663 tickers** distintos en
algún momento (SPY + 662 acciones).

---

## 4. Universo

- **Benchmark y fuente del universo:** KN US Equity Core, de KaxaNuk. Es un índice amplio de
  acciones de EE. UU. ponderado por tamaño: entre 694 y 906 miembros según la fecha. El peso de sus
  10 mayores fue del 20.0% en 2009, del 20.7% en 2019 y del 37.0% el 2026-11-06.
- **Elegibles cada mes:** solo las 300 de mayor peso del índice en esa fecha (acciones grandes y
  líquidas).
- **Núcleo:** SPY, un ETF del S&P 500. No es el benchmark, pero se le parece mucho: de 2000-01-03 a
  2026-11-06, CAGR de 7.81% contra 7.85% del KN Core, en el motor.
- **No se usó** ninguna lista de empresas elegidas a mano ni los miembros actuales del índice: cada
  señal usa los miembros de su propia fecha.

---

## 5. Datos

### 5.1 Archivos de KaxaNuk

| Archivo | Contenido | md5 del zip |
| --- | --- | --- |
| `KN_US_Equity_Core.zip` | `KN_US_Equity_Core_Returns_Daily.csv` (rendimiento diario del índice, desde 1999-01-04), `..._Holdings_Daily.csv` (peso diario de cada miembro, desde 1998-12-31), `..._Membership_Daily.csv`, `..._Tickers.csv` | `91712db0c1ef01c2e7d38f7fd63d05cb` |
| `KN_US_Equity_Factor_Model.zip` | KN US Equity Factor Model, experiment_3, diario de 2000-01-03 a 2026-11-06, 6,753 días: rendimiento de cada factor y, por acción, su rendimiento por factor, su exceso de rendimiento total y su parte idiosincrática | `07d373b44738763fbf520d1fa7f49f25` |

Los tickers con un número al final (`SNDK1`, `DTV1`, `EMC1`…) son identificadores de KaxaNuk para
empresas que ya no cotizan con ese símbolo.

### 5.2 Rendimiento diario por acción

Rendimiento total de la acción = exceso de rendimiento
(`KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv`) + tasa libre de riesgo implícita.

La tasa implícita se despeja del propio índice, porque el archivo de KaxaNuk no la trae:

```
tasa_t = rendimiento_KN_t − Σ_i peso_i,t−1 × exceso_i,t
tasa suavizada = mediana móvil de 21 días
```

En promedio da 1.54% anual.

### 5.3 Reconstrucción de 1999 (solo para las señales de 2000)

Entre reconstituciones, el peso de cada acción en un índice ponderado por tamaño se mueve con su
precio:

```
r_i,t = (peso_i,t / peso_i,t−1) × (1 + rendimiento_KN_t) − 1     (solo si es miembro ambos días)
```

Validación contra los rendimientos reales de 2000: correlación diaria de 0.937, error absoluto
mediano de 6.3 pb, error medio de +0.38 pb por día, y 1.5% de los pares con error mayor a 1%. El
ordenamiento por momentum dentro del top 300 tiene una correlación de rangos de 0.913, y el top 20
coincide en 11 de 20. Ningún día simulado usa estos rendimientos: solo las señales de 2000.

### 5.4 Precios para el Backtest Engine

- **Data Curator 0.51.0** con la extensión **Yahoo Finance 0.5.1** (yfinance 1.8.0), del
  2000-01-01 en adelante, en lotes de 25. Columnas: `m_date`, `m_open_split_adjusted`,
  `m_high_split_adjusted`, `m_low_split_adjusted`, `m_close_split_adjusted`,
  `m_volume_split_adjusted` y `m_close_dividend_and_split_adjusted`.
- **Regla de aceptación de Yahoo** (`preparar_motor.py`): se usa el archivo solo si (a) empieza a
  más tardar el día de la primera compra, (b) llega hasta la última fecha en que se tiene la acción
  y (c) sus rendimientos diarios tienen una correlación de al menos **0.9** con los de KaxaNuk en
  ese periodo, para descartar tickers que hoy son de otra empresa.
- **Si no se cumple**, la serie sale de los rendimientos de KaxaNuk (5.2), como un índice de
  precio que empieza en 100. Todas las columnas de precio son iguales a ese índice y el volumen es
  de 1,000,000,000. La serie termina donde termina el dato de KaxaNuk, y ahí el motor vende.
- **Resultado:** 433 tickers de Yahoo y 230 de KaxaNuk. De estos, 226 porque Yahoo no los tiene, 2
  porque Yahoo no cubre el periodo y 2 porque Yahoo no coincide (`JCI`, correlación 0.46; `AD`, sin
  días suficientes para comparar). Detalle por ticker en `datos_backtest_2000ene/fuente_de_precios.csv`.
- **Benchmark para el motor:** `KN_US_Equity_Core.csv`, construido como índice de precio con
  `KN_US_Equity_Core_Returns_Daily.csv`.

---

## 6. Backtest Engine (KaxaNuk, 0.68.0)

Configuración de `correr_backtest.py`:

| Campo | Base | Estrés |
| --- | --- | --- |
| `initial_capital` | 100,000 | 100,000 |
| `start_date` / `end_date` | 2000-01-03 / 2026-11-06 | igual |
| `cash_reserve_percentage` | 0.01 | 0.01 |
| `commission_model` | `basis_points` | `basis_points` |
| `commission_basis_points` | 1.0 | 5.0 |
| `commission_cents` | 0.0 (no se usa) | 0.0 |
| `slippage_model` | `basis_points` (plano) | `basis_points` |
| `slippage_basis_points` | 5.0 | 10.0 |
| `user_column_commission_price` | `m_close_split_adjusted` | igual |
| `user_column_trade_execution_price` | `m_close_dividend_and_split_adjusted` | igual |
| `user_column_mark_to_market_price` | `m_close_dividend_and_split_adjusted` | igual |
| `user_column_high` / `low` / `close` / `volume` | `m_high_split_adjusted` / `m_low_split_adjusted` / `m_close_split_adjusted` / `m_volume_split_adjusted` | igual |
| `rebalance_date_handling` | `next_trading_day` | igual |
| `delisted_position_handling` | `sell_at_last_price` | igual |
| `benchmark_file_name` | `KN_US_Equity_Core,SPY` (alfa e IR contra el primero) | igual |
| `market_data_input_format` / `portfolio_input_format` | `csv` / `csv` | igual |
| Archivo de pesos | `weights.csv`, horizontal: `Ticker` + una columna por fecha | igual |
| Tasa de financiamiento | ninguna (Sharpe con tasa 0) | igual |

Licencia: variable de entorno `KNBE_API_KEY_KAXANUK`. Nunca va en un archivo del proyecto.

---

## 7. Resultados

### 7.1 Ventana completa, 2000-01-03 a 2026-11-06 (27.79 años del motor)

| | Núcleo + satélite | Estrés de costos | KN US Equity Core | SPY |
| --- | --- | --- | --- | --- |
| CAGR (años del motor) | **9.04%** | **8.78%** | 7.85% | 7.81% |
| Volatilidad anual | 20.43% | 20.44% | 19.63% | 19.65% |
| Caída máxima | −53.10% | −53.30% | −52.67% | −55.18% |
| Alfa anual vs KN Core | **+1.19%** | **+0.93%** | — | — |
| Information Ratio vs KN Core | **+0.21** | **+0.18** | — | — |
| Sharpe (tasa 0) | 0.44 | 0.43 | 0.40 | 0.40 |
| Sortino (tasa 0) | 0.61 | 0.59 | 0.54 | 0.54 |
| Comisiones | $1,959 | $9,335 | — | — |
| Slippage | $9,292 | $17,692 | — | — |

Valor del portafolio base: $99,941 al cierre del 2000-01-03 (después de los costos de la primera
compra) y **$1,108,201** el 2026-11-06.

### 7.2 Por periodo (serie diaria del motor, costos base)

| Periodo | Cartera, anual | KN Core, anual | Exceso anual | IR |
| --- | --- | --- | --- | --- |
| 2000 (satélite aproximado) | −10.3% | −9.9% | −0.4 | +0.15 |
| 2000–2002, caída de las puntocom | −13.6% (total −35.4%) | −15.2% (total −38.8%) | +1.5 | +0.27 |
| 2000–2008 | −1.7% | −3.5% | +1.8 | +0.32 |
| 2009–2018, periodo de diseño | 13.4% | 13.1% | +0.3 | +0.09 |
| 2019–2026-11-06, prueba fuera de muestra | 18.0% | 16.3% | +1.7 | +0.26 |

### 7.3 Por año (serie diaria del motor, costos base)

| Año | Cartera | KN Core | SPY | Exceso (puntos) |
| --- | --- | --- | --- | --- |
| 2000 | −10.3% | −9.8% | −8.8% | −0.4 |
| 2001 | −12.0% | −13.3% | −11.8% | +1.3 |
| 2002 | −18.2% | −21.7% | −21.6% | +3.5 |
| 2003 | +32.8% | +29.3% | +28.2% | +3.5 |
| 2004 | +14.9% | +11.2% | +10.7% | +3.7 |
| 2005 | +10.8% | +6.3% | +4.8% | +4.5 |
| 2006 | +11.0% | +15.3% | +15.8% | −4.3 |
| 2007 | +15.1% | +7.1% | +5.1% | +8.0 |
| 2008 | −38.5% | −36.9% | −36.8% | −1.5 |
| 2009 | +23.0% | +27.9% | +26.4% | −4.9 |
| 2010 | +17.6% | +16.0% | +15.1% | +1.6 |
| 2011 | −0.6% | +1.2% | +1.9% | −1.8 |
| 2012 | +17.3% | +16.5% | +16.0% | +0.8 |
| 2013 | +36.7% | +33.1% | +32.3% | +3.5 |
| 2014 | +16.6% | +12.7% | +13.5% | +3.9 |
| 2015 | +2.8% | +0.7% | +1.2% | +2.0 |
| 2016 | +10.7% | +11.5% | +12.0% | −0.8 |
| 2017 | +19.0% | +22.0% | +21.7% | −3.1 |
| 2018 | −3.0% | −4.6% | −4.6% | +1.5 |
| 2019 | +26.8% | +31.2% | +31.2% | −4.5 |
| 2020 | +28.2% | +22.3% | +18.3% | +6.0 |
| 2021 | +24.0% | +25.9% | +28.7% | −1.9 |
| 2022 | −14.2% | −20.0% | −18.2% | +5.7 |
| 2023 | +21.9% | +26.9% | +26.2% | −5.0 |
| 2024 | +32.6% | +24.8% | +24.9% | +7.9 |
| 2025 | +20.3% | +17.4% | +17.7% | +2.9 |
| 2026 (al 6 de noviembre) | +8.8% | +8.7% | +8.7% | +0.1 |

Le ganó al KN Core en 17 de 27 años.

### 7.4 Attribution Analysis (KaxaNuk, 0.7.0), 2000-01-04 a 2026-11-06

**Configuración.** `brinson_fachler_method=True`, `factor_model_method=True`,
`active_factor_model=True` y `linking_method` por omisión (Carino). Los 17 factores del KN US
Equity Factor Model van como `f_market`, `f_size`, `f_value`, `f_momentum`, `f_beta`,
`f_residual_volatility` y once sectores. El precio es `m_close_dividend_and_split_adjusted`, con
series de KaxaNuk para las 2,148 acciones.

**Cómo se arman las entradas** (`preparar_atribucion.py`):
- **Portafolio diario:** `Daily_Weights` del motor, con el SPY abierto en las acciones del KN Core
  según sus pesos de cada día y ampliado a todos los miembros del benchmark con peso 0. Se mueve un
  día: el peso al cierre de t−1 gana el rendimiento de t.
- **Benchmark diario:** los pesos del KN Core, normalizados para que no pasen de 1 y movidos un día
  igual.
- **Efectivo:** el residuo de cada día va como `CASH` explícito.

**Resultados:**

| | Valor |
| --- | --- |
| Rendimiento total de la cartera | +952.2% |
| Rendimiento total del benchmark | +640.1% |
| Rendimiento activo acumulado | +312.1 puntos |
| Activo anualizado | +1.42% |
| Tracking error | 5.73% |
| Information Ratio (librería) | +0.27 |
| Beta | 1.03 |
| Días ganados al benchmark | 53.5% |

| Origen del rendimiento activo | Puntos |
| --- | --- |
| Momentum | **+262.5** |
| Específico de las acciones (idiosincrático) | **+232.0** |
| Tamaño | +32.5 |
| Energía | +25.1 |
| Comunicaciones | +14.1 |
| Tecnología | +10.8 |
| Materiales | +10.2 |
| Consumo discrecional | +9.5 |
| Consumo básico | +2.1 |
| Bienes raíces | +2.1 |
| Mercado | +1.0 |
| Servicios públicos | −5.1 |
| Industriales | −6.6 |
| Salud | −6.7 |
| Financieras | −7.4 |
| Valor | −24.0 |
| Volatilidad residual | −84.9 |
| Beta | −155.1 |
| **Suma de factores** | **+80.2** |

**Controles de la corrida:**
- **Cobertura de factores:** 98.2% del portafolio (falta el efectivo) y 99.999% del benchmark.
- **Conciliación del benchmark:** el rendimiento calculado desde sus pesos da 9.35% contra 9.69%
  de la serie oficial (media diaria × 252), una brecha de −0.34 puntos al año, dentro de la
  tolerancia de 1 punto.
- **Brinson-Fachler:** cada acción es su propio segmento, así que todo el alfa sale como
  "asignación". Solo se usa su tabla por año.

### 7.5 Otras ventanas, con la misma regla

| Ventana | CAGR cartera | CAGR KN Core | Alfa | IR |
| --- | --- | --- | --- | --- |
| 2019-01-02 a 2026-11-06 | 17.2% | 15.7% | +1.6% | +0.17 (estrés +0.14) |
| 2001-02-01 a 2026-11-06 | 9.9% | 8.4% | +1.4% | +0.25 (estrés +0.22) |
| 2000-01-03 a 2026-11-06 | 9.0% | 7.9% | +1.2% | +0.21 (estrés +0.18) |

---

## 8. Cómo replicarlo

### 8.1 Entorno

```
uv 0.13.8 · Python 3.12.16 · pandas 2.3.3 · numpy 2.5.4 · pyarrow 26.0.1
kaxanuk-data-curator 0.51.0 · kaxanuk.data-curator-extensions.yahoo-finance 0.5.1 · yfinance 1.8.0
kaxanuk-backtest-engine 0.68.0 · kaxanuk-attribution-analysis 0.7.0   (con licencia)
```

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python pandas numpy matplotlib kaxanuk-data-curator kaxanuk.data-curator-extensions.yahoo-finance
uv pip install --python .venv/bin/python kaxanuk-backtest-engine kaxanuk-attribution-analysis --extra-index-url https://license:<LICENCIA>@<SERVIDOR>/simple/
```

### 8.2 Pasos

Descomprime los dos zips de KaxaNuk en una carpeta, `<KN>`, con los CSV sueltos (sin subcarpetas).

```bash
# 1. Señales y weights.csv (también imprime la prueba exploratoria)
.venv/bin/python nucleo_satelite.py <KN> resultados_nucleo_satelite_2000ene 1999-12-31 reconstruir-1999

# 2. Precios con el Data Curator (Yahoo)
.venv/bin/python descargar_precios.py resultados_nucleo_satelite_2000ene/tickers_para_curator.csv datos_backtest_2000/precios 2000-01-01

# 3. Carpeta de precios del motor (Yahoo verificado + series de KaxaNuk + benchmark)
.venv/bin/python preparar_motor.py <KN> resultados_nucleo_satelite_2000ene/weights.csv datos_backtest_2000/precios datos_backtest_2000ene/motor 2000-01-01

# 4. Backtest Engine, base y estrés
KNBE_API_KEY_KAXANUK=<LICENCIA> .venv/bin/python correr_backtest.py datos_backtest_2000ene/motor resultados_nucleo_satelite_2000ene weights resultados_nucleo_satelite_2000ene/backtest_base 2000-01-03 2026-11-06 1.0 5.0
KNBE_API_KEY_KAXANUK=<LICENCIA> .venv/bin/python correr_backtest.py datos_backtest_2000ene/motor resultados_nucleo_satelite_2000ene weights resultados_nucleo_satelite_2000ene/backtest_estres 2000-01-03 2026-11-06 5.0 10.0

# 5. Attribution Analysis
.venv/bin/python preparar_atribucion.py <KN> resultados_nucleo_satelite_2000ene/backtest_base/Daily_Weights.csv datos_atribucion_2000ene
KNAA_API_KEY_KAXANUK=<LICENCIA> .venv/bin/python correr_atribucion.py datos_atribucion_2000ene
```

### 8.3 Cómo saber que lo replicaste igual

- **`weights.csv`:** 663 filas × 323 fechas, del 2000-01-03 al 2026-11-02, md5
  `989449bc0b60c32c0704f8b018704671`.
- **Último rebalanceo (2026-11-02)**, solo como punto de control, no como recomendación: SPY 70% y
  AMAT, AMD, COHR, DELL, HPE, ILMN, INTC, KEYS, LITE, LRCX, MPC, MRNA, MRVL, MU, RVMD, SNDK, STX,
  TER, VLO y WDC, con 1.5% cada una.
- **`backtest_base/resumen.json`:** ventana valuada del 2000-01-03 al 2026-11-06, CAGR 0.0904,
  Information Ratio 0.2125.
- **Yahoo puede cambiar sus datos** con el tiempo: si un precio difiere, revisa
  `fuente_de_precios.csv` y el registro del Curator.

### 8.4 Archivos del proyecto

| Archivo | Qué hace |
| --- | --- |
| `nucleo_satelite.py` | Reglas, señales, `weights.csv`, lista de tickers y prueba exploratoria |
| `descargar_precios.py` | Descarga con el Data Curator (Yahoo) y lista lo que no bajó |
| `preparar_motor.py` | Valida Yahoo contra KaxaNuk y arma la carpeta de precios del motor |
| `correr_backtest.py` | Configura y corre el Backtest Engine; guarda `resumen.json`, `Daily_Weights.csv`, `Register.csv` y el Excel |
| `preparar_atribucion.py` | Arma las cuatro entradas de Attribution Analysis |
| `correr_atribucion.py` | Corre la atribución; guarda el Excel y `resultado.pkl` |
| `resultados_nucleo_satelite_2000ene/RESULTADOS.md` | Resumen de resultados |

---

## 9. Limitaciones

1. **El año 2000 es aproximado:** sus señales usan rendimientos reconstruidos (5.3) y la primera
   ventana tiene 251 días.
2. **Precios mixtos:** 230 de 663 tickers usan series de KaxaNuk, sin rango diario, y por eso el
   slippage es plano.
3. **Ejecución:** se opera al cierre ajustado del día de rebalanceo, no a la apertura, y la comisión
   se calcula sobre el cierre ajustado por splits, porque Yahoo no trae precios sin ajustar.
4. **Sharpe con tasa 0:** sirve para comparar entre columnas, no como cifra absoluta.
5. **Corrida local:** el Backtest Engine y Attribution Analysis corrieron en esta computadora, no
   en la plataforma web del Lab.
6. **Lo específico de las acciones (+232 puntos)** no se puede separar de la suerte con 20 nombres
   y 27 años.
7. **La caída máxima es la del mercado:** la estrategia no protege en las crisis.
8. **La investigación y la prueba exploratoria** usaron 2009–2018 como diseño y 2019–hoy como
   prueba. La regla se fijó antes de correr el motor y no se cambió después; la única variante
   probada (momentum ajustado por volatilidad) se descartó por su resultado en el periodo de diseño.

## 10. Referencias

- Jegadeesh, N. y Titman, S. (1993). *Returns to Buying Winners and Selling Losers.* Journal of Finance.
- Asness, C., Moskowitz, T. y Pedersen, L. H. (2013). *Value and Momentum Everywhere.* Journal of Finance 68(3).
- Barroso, P. y Santa-Clara, P. (2015). *Momentum Has Its Moments.* Journal of Financial Economics (la variante descartada).
- McLean, R. D. y Pontiff, J. (2016). *Does Academic Research Destroy Stock Return Predictability?* Journal of Finance 71(1).
- Talavera Valley Hackathon 2026, *Alfa a la vista — Track 04 WealthTech* (reglas del reto).
