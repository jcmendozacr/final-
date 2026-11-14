# Modelo principal (v2): "C2 confirmada"

> **VERSIÓN PREVIA desde el 2026-11-14.** El modelo principal es la v3, "Momentum concentrado"
> (`modelo_principal_v3/MODELO_PRINCIPAL.md`): +7.37% de alfa (+6.17% con estrés). Esta versión sigue
> congelada sin cambios.

Equipo de Habib · Talavera Valley Hackathon 2026 · Track 04 WealthTech.

> **Congelado el 2026-11-14 como modelo principal del equipo.** Reemplaza al modelo de
> `MODELO_ACTUAL.md` (congelado el 2026-11-13), que se conserva como versión previa y además es el
> componente de acciones de este modelo. Las huellas md5 están en `MODELO_PRINCIPAL.md5`.
>
> Investigación y aprendizaje, no asesoría de inversión. Las cifras vienen de un backtest con
> precios pasados.

---

## 1. La idea en una frase

Las mismas 10 acciones de momentum y el mismo régimen de mercado del modelo anterior, pero **el
núcleo que antes era SPY ahora rota entre los 2 sectores cíclicos más fuertes**, y **las salidas a
refugio solo se ejecutan si un modelo de riesgo, entrenado con 2000–2009, confirma el peligro**.

---

## 2. Reglas

### 2.1 Señales mensuales (al cierre del último día hábil de cada mes)

| Señal | Definición |
| --- | --- |
| Tendencia | Arriba si el SPY (cierre ajustado por dividendos) es **≥** al promedio de sus últimos **10 cierres de fin de mes**, el actual incluido |
| Canario | OK si el momentum **13612 de TIP** es **≥ 0**: el promedio simple de sus rendimientos totales a 1, 3, 6 y 12 meses |
| Sectores cíclicos | Momentum de **252 sesiones** de XLK, XLF, XLE, XLY, XLI y XLB |
| Riesgo (modelo) | Probabilidad del modelo de la sección 2.6 con los datos del KN US Equity Core |

### 2.2 Regímenes y cartera objetivo

| Régimen | Condición | Cartera objetivo |
| --- | --- | --- |
| **Alcista** | Tendencia arriba **y** canario OK | **60%** en las 10 acciones (6% c/u) + **40%** en el núcleo cíclico |
| **Mixto** | Solo una de las dos señales en alerta | **30%** en las 10 acciones (3% c/u) + **70%** en el núcleo cíclico |
| **Caída** | Tendencia abajo **y** canario en alerta | **100% en refugio:** IEF si su 13612 es mayor que el de SHY; si no, SHY. Sujeto a la confirmación de la sección 2.5 |

### 2.3 Núcleo cíclico (reemplaza al SPY del modelo anterior)

- **Universo fijo:** los 6 SPDR sectoriales que Morningstar no clasifica como defensivos: XLK, XLF,
  XLE, XLY, XLI y XLB. Quedan fuera consumo básico (XLP), salud (XLV) y servicios públicos (XLU).
- Se toman los **2 con mayor momentum de 252 sesiones**, si es **> 0**. El peso del núcleo se
  reparte por igual entre ellos: 20% + 20% en alcista y 35% + 35% en mixto.
- Si solo uno tiene momentum positivo, ese se lleva todo el peso del núcleo.
- Si ninguno tiene momentum positivo, el peso del núcleo va a **SHY**.

### 2.4 Las 10 acciones (iguales en alcista y en mixto; sin cambios respecto al modelo anterior)

1. **Universo:** las **300 acciones de mayor peso** del KN US Equity Core en la fecha de la señal.
2. **Historia mínima:** 240 rendimientos diarios válidos de los últimos 252.
3. **Señal:** momentum **12-1**, la suma de los rendimientos logarítmicos diarios desde 252 hasta 21
   días hábiles atrás.
4. Se eligen las **10** con la señal más alta, con pesos iguales.

### 2.5 Salidas a refugio confirmadas por el modelo de riesgo

Hay **fecha de refugio** cuando la cartera objetivo pone **50% o más en SHY, IEF o TIP**. Eso pasa
en dos casos: en el régimen de caída, o cuando se activa el interruptor de volatilidad (sección 2.7).

En cada fecha de refugio se toma la probabilidad del modelo (sección 2.6) **al cierre del último fin
de mes anterior a la fecha de operación**:
- **Probabilidad > 0.2222 (el modelo confirma el riesgo):** se ejecuta el refugio.
- **Probabilidad ≤ 0.2222 (no lo confirma):** esa fecha se usa la **asignación del núcleo cíclico al
  100%** vigente, según la sección 2.3: 50% en cada uno de los 2 sectores, o SHY si ninguno tiene
  momentum positivo.

### 2.6 Modelo de riesgo (regresión logística, entrenado una sola vez y congelado)

- **Variables**, calculadas con el índice de precios en la fecha de fin de mes:

  | Variable | Definición |
  | --- | --- |
  | tendencia | precio / promedio de 200 días − 1 |
  | mom12 | precio / precio de 252 sesiones antes − 1 |
  | vol63 | desviación estándar de los rendimientos diarios de 63 días × √252 |
  | dist_max | precio / máximo de 252 sesiones − 1 |

- **Etiqueta de entrenamiento:** el índice cae más de 5% en las siguientes 63 sesiones.
- **Datos de entrenamiento:** observaciones de fin de mes del 2000-01 al 2009-09 de **12 índices
  construidos con datos de KaxaNuk**: el KN US Equity Core y los 11 índices sectoriales de KN.
  Cada índice sectorial está ponderado por el peso de cada acción en el KN Core, con la
  clasificación sectorial de KN de cada día. Son 1,260 observaciones y 280 caídas.
- **Estandarización:** (x − media) / desviación, con los valores del entrenamiento:

  | | tendencia | mom12 | vol63 | dist_max |
  | --- | --- | --- | --- | --- |
  | media | 0.00402 | 0.01795 | 0.22054 | −0.12231 |
  | desviación | 0.11324 | 0.21995 | 0.15113 | 0.13710 |

- **Coeficientes** (Newton-Raphson con L2 = 1.0, sin penalizar la constante): constante −1.315,
  tendencia −0.402, mom12 −0.258, vol63 +0.655, dist_max +0.748.
  p = 1 / (1 + e^−(constante + Σ coef × variable estandarizada)).
- **Umbral:** 0.2222, la frecuencia de caídas en el entrenamiento.
- **Uso:** se aplica solo al KN US Equity Core. De 2010 en adelante, sus probabilidades son fuera
  de muestra.

### 2.7 Interruptor de volatilidad (diario; igual que el modelo anterior, aplicado al núcleo)

- Cada día, al cierre, se calcula la volatilidad del SPY de los últimos 20 días, anualizada
  (desviación estándar diaria × √252).
- Si **pasa de 35%**, al día hábil siguiente la parte invertida (acciones + núcleo cíclico) pasa a
  **SHY**. Esa fecha es fecha de refugio y aplica la confirmación de la sección 2.5.
- Cuando cierra en 35% o menos, al día hábil siguiente se vuelve a la cartera del régimen vigente.
- **En régimen de caída no actúa.**

### 2.8 Operación

- Se opera el **día hábil siguiente** a cada señal. Cada mes se rebalancea completo, y también en
  los días del interruptor.
- Entre rebalanceos, los pesos se mueven con los precios.
- **Empresas que dejan de cotizar:** se venden a su último precio y el peso queda en efectivo hasta
  el siguiente rebalanceo.
- **Restricciones:** sin apalancamiento ni ventas en corto; los pesos suman 1 en cada rebalanceo.
  **Ninguna acción pasa de 6%**, lejos del tope de 20% del reto. Los ETF pueden pasar de 20%
  (XLK o XLY hasta 70% en mixto; SHY o IEF hasta 100% en refugio), igual que el SPY en el modelo
  anterior.

---

## 3. Parámetros congelados

| Parámetro | Valor |
| --- | --- |
| Acciones | 10, top 300 del KN Core, momentum 12-1, historia de 240/252 días |
| Alcista: acciones / núcleo | 0.60 / 0.40 |
| Mixto: acciones / núcleo | 0.30 / 0.70 |
| Núcleo cíclico | top 2 de XLK, XLF, XLE, XLY, XLI y XLB por momentum de 252 sesiones > 0; si no, SHY |
| Tendencia / canario | SPY contra el promedio de 10 fines de mes / TIP 13612 ≥ 0 |
| Refugio en caída | IEF o SHY, el de mayor 13612 |
| Interruptor | volatilidad del SPY a 20 días > 35% → SHY |
| Confirmación de refugio | probabilidad del modelo > 0.2222 al último fin de mes |
| Modelo de riesgo | logística de 4 variables, entrenada 2000-01 a 2009-09, embargo de 3 meses |

`weights.csv`: 381 tickers × 259 fechas, del 2006-02-01 al 2026-11-02.
`decisiones_refugio.csv`: 34 fechas de refugio; el modelo vetó 8 (2008-09-22, 2009-06-01,
2011-08-10, 2018-11-01, 2020-03-06, 2022-10-03, 2023-11-01 y 2025-04-10).

---

## 4. Datos (todos de KaxaNuk o de su Data Curator)

- **Acciones:** KN US Equity Core (miembros y pesos) y KN US Equity Factor Model (rendimiento en
  exceso + tasa implícita). Los precios del motor son los de `datos_backtest_p1/motor`, que
  reproducen exactamente el resultado oficial del modelo anterior.
- **ETF (SPY, TIP, SHY, IEF, XLK, XLF, XLE, XLY, XLI y XLB):** Data Curator (extensión Yahoo
  Finance), columna `m_close_dividend_and_split_adjusted`.
- **Sectores para el modelo de riesgo:** archivos de sector de `KN_US_Equity_Factor_Model.zip`
  (carpeta `KN_sectores/`).

---

## 5. Resultados en el Backtest Engine 0.68.0

**Configuración:** `correr_backtest.py` con $100,000 iniciales y 2% de reserva de efectivo.
Comisiones y slippage en puntos base: base de 1 + 5 pb y estrés de 5 + 10 pb. Benchmarks: KN US
Equity Core y SPY.

**El alfa es contra el KN US Equity Core de KaxaNuk:** alfa = CAGR del modelo − CAGR del KN Core, en
la misma ventana. Es el campo "Alpha" del motor, que en todas las corridas coincide con esa
diferencia.

### 5.1 Ventana completa: 2007-03-01 a 2026-11-06

| | **Modelo (costos base)** | Costos de estrés | KN US Equity Core | SPY |
| --- | --- | --- | --- | --- |
| **CAGR** | **14.74%** | **13.78%** | 10.45% | 10.39% |
| **Alfa vs KN Core** | **+4.28%** | **+3.33%** | — | — |
| Volatilidad | 23.2% | 23.2% | 20.0% | 20.0% |
| Sharpe (tasa 0) | 0.64 | 0.59 | 0.52 | 0.52 |
| Sortino (tasa 0) | 0.84 | 0.79 | 0.69 | 0.73 |
| **Caída máxima** | **−33.8%** | −34.8% | −52.7% | −55.2% |
| Information Ratio | 0.27 | 0.23 | — | — |
| Comisiones / slippage | $9,151 / $43,835 | $40,743 / $77,934 | — | — |

### 5.2 Fuera de muestra del modelo de riesgo: 2010-01-04 a 2026-11-06

| | Modelo (costos base) | Costos de estrés | KN US Equity Core |
| --- | --- | --- | --- |
| CAGR | 15.13% | 14.22% | 13.16% |
| **Alfa vs KN Core** | **+1.98%** | **+1.06%** | — |
| Sharpe | 0.66 | 0.62 | 0.74 |
| Caída máxima | −33.9% | −34.8% | −33.0% |

### 5.3 Comparación con las alternativas (2007–2026; entre paréntesis, con estrés)

| | Alfa 2007–26 | Alfa 2010–26 | Sharpe | Caída máx. |
| --- | --- | --- | --- | --- |
| **C2 confirmada (este modelo)** | **+4.28% (+3.33%)** | **+1.98% (+1.06%)** | 0.64 | −33.8% |
| Modelo anterior (`MODELO_ACTUAL.md`) | +3.00% (+2.23%) | +0.08% (−0.65%) | 0.65 | −30.9% |
| C1: 50% anterior + 50% cíclicos | +3.20% (+2.58%) | +1.24% (+0.62%) | 0.74 | −25.6% |
| C2 sin confirmación | +3.77% (+2.85%) | +0.47% (−0.44%) | 0.65 | −27.9% |

---

## 6. Riesgos y limitaciones

1. **La peor caída (−33.8%) va de 2018-09 a 2020-03-23.** El 2020-03-06 el interruptor quiso salir,
   pero el modelo, con la probabilidad del cierre de febrero (0.17), vetó la salida, y la cartera se
   quedó en sectores durante el desplome del COVID. Es el costo de usar una señal mensual para
   confirmar una alarma diaria.
2. **Más volatilidad que el índice** (23.2% contra 20.0%). En 2010–2026 su Sharpe (0.66) queda
   debajo del KN Core (0.74): da más rendimiento, pero no mejor rendimiento por unidad de riesgo en
   esa ventana.
3. **El núcleo cíclico pasó su propia prueba por poco.** La rotación de 6 sectores superó el umbral
   por 0.09 puntos, y el filtro alternativo por beta no lo superó (`hackaton_etf/RESULTADOS.md`).
4. **Concentración en ETF:** XLK o XLY pueden llegar a 70%. Si el tope de 20% aplicara a ETFs, no se
   cumpliría (tampoco en el modelo anterior, por el SPY). Pregunta pendiente para los mentores.
5. **No es una prueba ciega completa.** El modelo de riesgo es fuera de muestra desde 2010, pero esta
   combinación se eligió después de varias rondas de pruebas con 2007–2026 (ver `hackaton_combos/`).
   Todas las decisiones se fijaron antes de cada corrida, y las variantes descartadas están
   documentadas.

---

## 7. Cómo replicarlo

Entorno: `.venv` del proyecto con `kaxanuk.backtest_engine` 0.68.0 y su licencia en
`KNBE_API_KEY_KAXANUK`. Carpetas de datos:
- `KN/`: CSV de `KN_US_Equity_Core.zip` y `KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv`;
- `KN_sectores/`: los 11 archivos de sector del zip del Factor Model.

```powershell
$env:PYTHONUTF8 = 1
# 1. Componente de acciones: el modelo anterior, congelado (pesos en resultados_regimen_n10_a60/weights.csv).
#    Para regenerarlo, ver MODELO_ACTUAL.md, sección 9.

# 2. ETF sectoriales con el Data Curator
#    (con Avast u otro antivirus que intercepte TLS, usar el lanzador con certificados de Windows)
.venv\Scripts\python descargar_precios.py datos_etf_hackaton\tickers.csv datos_etf_hackaton\precios 1999-01-01

# 3. Modelo de riesgo (índices KN, entrenamiento 2000–2009, prueba 2010–2026)
.venv\Scripts\python filtro_riesgo\filtro.py KN KN_sectores

# 4. Precios del benchmark y de los ETF para el motor, y núcleo cíclico
.venv\Scripts\python hackaton_ideas\preparar.py KN KN_sectores   # escribe datos_backtest_hack\motor\KN_US_Equity_Core.csv
.venv\Scripts\python hackaton_etf\preparar.py
.venv\Scripts\python hackaton_etf\filtros_ciclicos.py            # hackaton_etf\ciclicos6_top2\weights.csv

# 5. Combinación y confirmación
.venv\Scripts\python hackaton_combos\preparar.py                 # C2 y la carpeta datos_backtest_combo\motor
.venv\Scripts\python hackaton_combos\c2_confirmado.py            # hackaton_combos\C2_confirmado\weights.csv

# 6. Backtest Engine
$env:KNBE_API_KEY_KAXANUK = "<LICENCIA>"
.venv\Scripts\python correr_backtest.py datos_backtest_combo\motor modelo_principal_c2 weights modelo_principal_c2\backtests\nuevo_base 2007-03-01 2026-11-06 1.0 5.0 0.02
```

Para los costos de estrés se usa `5.0 10.0`. Para la prueba fuera de muestra, la ventana empieza el
`2010-01-04`.

**Puntos de control:**
- `weights.csv` debe dar el md5 de `MODELO_PRINCIPAL.md5`.
- La última asignación (señal del 2026-10-30, operada el 2026-11-02) es: DELL, INTC, LITE, MRNA,
  MRVL, MU, RVMD, SNDK, STX y WDC a 6% cada una, más XLB 20% y XLE 20%. Se reporta solo como
  control, no como recomendación.
