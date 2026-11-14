# Talavera Valley Hackathon 2026 · Track 04 WealthTech
## Bitácora de progreso del equipo (corte: viernes 13 nov 2026, 15:10)

---

## 1. El reto en una frase

> **Construir una empresa de inversión: estrategias en dólares que le ganen al KN US Equity Core (con código) o al SPY (plataforma), con el riesgo siempre bajo control.**

**Clienta: Ana**, 22 años, primer empleo formal; su pensión depende de su Afore.
- CONSAR proyecta **4% real** durante 43 años para Ana.
- Su Siefore tiene **~22% en acciones** (puede llegar a 60%).
- Las Afores han rendido **4.84% real anual** desde 1997.
- Los planes de pensiones de empresas: **~2.0% real** anual a 5 años.
- **15% del salario** se aportará a su retiro hacia 2030.
- Contraste: Miguel, 60 años, se jubila con Ley 73 (le paga el gobierno).
- Mensaje del reto: *"Lo que el sistema no le garantiza a Ana es una oportunidad de negocio."*

**Definición de alfa del jurado:** lo que la estrategia gana sobre su benchmark, **después de costos** y **considerando el riesgo** que tomó.

---

## 2. Reglas del portafolio

1. Benchmark: con código → **KN US Equity Core**; sin código (plataforma) → **SPY**.
2. Universo: acciones y ETFs de cualquier clase de activo.
3. **Máximo 20% en una sola acción.** (⚠️ pendiente confirmar si aplica a ETFs)
4. Sin límites por clase de activo.
5. Todo se mide **en dólares, después de costos**.
6. Manejar o asesorar dinero de terceros **requiere registro ante la CNBV**.

**Principios del jurado ("Dinámicos, no sobreajustados"):**
- Primero la lógica económica, escrita **antes** del backtest.
- Modelos dinámicos que se adapten al mercado, no reglas fijas calibradas a la historia.
- Riesgo a la vista: volatilidad, peor caída y concentración, siempre junto al rendimiento.
- Contra el sobreajuste: probar en datos no usados para diseñar.

---

## 3. Rúbrica (100 puntos; cada criterio de 1 a 5 × su peso)

| Criterio | Peso | Qué piden |
|---|---|---|
| Problema, usuario y evidencia | 20% | A quién le falta rendimiento (Ana) y con qué datos |
| Calidad de la solución e innovación | 20% | Estrategia diferenciada, lógica y dinámica |
| Uso significativo de tecnología | 20% | Investment Lab y modelos dinámicos dentro del producto |
| **Prototipo + experimentación** | 20% | Backtest en el Lab vs. benchmark, después de costos, sin sobreajuste |
| Impacto, factibilidad y continuidad | 15% | Riesgo bajo control, tope de 20%, cómo sigue la empresa |
| Pitch + demo | 5% | Claro, a tiempo y con backtest en vivo |

**Desempate:** 1º Prototipo + experimentación; 2º Problema, usuario y evidencia.

**Jurado:** Salvador Orozco (Fondo de Fondos) · Fernando Belden, CFA · Sebastián Blanco (KaxaNuk) · Antonio Arizmendi · Jabin Mora.

---

## 4. Calendario y entregables

| Día | Hora | Evento |
|---|---|---|
| 13 | 9:00 | Inicia desarrollo |
| 13 | 22:00 | Cierre del día |
| 14 | **12:00** | **Cierre de entregas** |
| 14 | 12:30 | Presentaciones |
| 14 | 17:00 | Premiación |

**4 entregables:**
1. ☐ Backtest contra el benchmark (KN US Equity Core en el Lab, o SPY en la plataforma).
2. ☐ El código y cómo correrlo.
3. ☐ El pitch: cliente, estrategia, riesgo y quién paga.
4. ☐ Una lámina de método: cómo evitaron el sobreajuste.

**"Una estrategia no es una empresa"**, hay que responder:
1. Cliente: ¿quién es Ana y qué rendimiento le falta?
2. Producto: qué estrategia y cómo se adapta a cada perfil.
3. Modelo: quién paga, cuánto y por qué seguiría pagando.
4. Riesgo: cómo se explica a alguien que no sabe de mercados.
5. La línea: registro ante la CNBV.

---

## 5. Decisiones tomadas

| Decisión | Por qué |
|---|---|
| **Trabajar con código (Python)** | Suma en "uso de tecnología", facilita la lámina anti-sobreajuste y cumple el entregable 02 |
| **No usar la lista de "empresas buenas" del amigo** | Sesgo de anticipación y supervivencia: se eligieron sabiendo que ganaron. Sus estrategias además violaban el 20% (top 1 = 100% en una acción) |
| **Universo de ETFs por clase de activo** | Diversifica, cumple el 20% y evita el sesgo de supervivencia sin pagar datos premium |
| **Proveedor de datos: Yahoo** (vía Data Curator) | FMP gratuito no incluye la lista de acciones ni permitió escribir archivos; Sharadar es de pago |
| **Periodo de diseño 2009–2018; prueba fuera de muestra 2019–hoy** | Separar datos para evitar sobreajuste |
| **Estrategia final: v1 Multiactivo** | Mejor alfa ajustado por riesgo, menor caída y la robustez más estable |
| **Dejar de modificar la estrategia después de la v3** | Seguir cambiando hasta ganarle al SPY sería sobreajuste |

---

## 6. Configuración del Investment Lab (KaxaNuk)

- URL: `lab.kaxanuk.mx` · cuenta de Diego · experimento **"Hakathon 2026"** (experiment=61).
- Computadora: **Zephyrusg14** (laptop de Diego). **Debe estar encendida, con cargador e internet.**
- Carpeta: `C:\Users\vevoe\Downloads\Hakathon\Hakathon 2026`
- Llaves de datos (app KaxaNuk → Data keys): FMP guardada (Usuario = `FMP`, Contraseña = API key). LSEG y Sharadar no se usan.
- **Lecciones:**
  - El error "FMP refused the key" era porque la llave **no estaba guardada**.
  - "Your FMP plan does not include this data": el plan gratuito **no incluye la lista de acciones** (Universe Creator).
  - Curator con FMP: "The download finished without writing any file" → **con Yahoo sí funcionó**.

**Pipeline del Lab:** Universe (Creator) → Data (Curator) → Portfolio (Construction) → Backtest → Attribution (+ Analyzer).

---

## 7. Datos descargados (Data Curator · Yahoo · 2 ene 2008 → 12 nov 2026)

- **Multiactivo:** SPY, QQQ, IWM, EFA, EEM, VNQ, TLT, IEF, LQD, GLD, SHY
- **Sectores:** XLK, XLF, XLV, XLE, XLY, XLP, XLI, XLU, XLB (+ SHY, SPY)
- **4,747 días** por archivo, sin vacíos ni fechas duplicadas.
- Columna usada: **`m_close_dividend_and_split_adjusted`** (rendimiento total; clave para ETFs de bonos).
  - Ejemplo SPY 2008: precio $144.93 vs. ajustado $102.97. Con dividendos creció ~7.4x; sin ellos ~5.2x.
- **Diagnóstico (diagnostico.py):** datos sanos. Correlación de sectores con SPY 0.63–0.91, sin desfase de fechas, volatilidades normales (SHY 1.5%, IEF 7%, TLT 15%, acciones 18–30%).

---

## 8. Estrategias probadas (código propio · después de costos de 10 bps)

### Lógica económica (escrita antes del backtest)
> Los activos que vienen subiendo tienden a seguir subiendo unos meses (momentum). Cuando un activo cae debajo de su tendencia de largo plazo (promedio de 200 días), conviene salir y refugiarse en bonos de corto plazo (SHY). Así Ana participa en los mercados alcistas y se protege en las crisis.

### v1 · Multiactivo (FINAL ✅)
- Universo: SPY, QQQ, IWM, EFA, EEM, VNQ, TLT, IEF, LQD, GLD + **SHY** como refugio.
- Cada fin de mes: ordenar por rendimiento de **126 días (~6 meses)**.
- Comprar el **top 5**, solo si momentum > 0 **y** precio > promedio de 200 días.
- **20% cada uno**; los lugares vacíos van a SHY.
- Se opera el **día hábil siguiente** a la señal.

### v2 · Sectores
- Lo mismo, pero con los 9 sectores originales del S&P 500 (XLK, XLF, XLV, XLE, XLY, XLP, XLI, XLU, XLB).

### v3 · Régimen de mercado
- Si SPY > promedio de 200 días: 100% en el top 5 de sectores por momentum (20% c/u).
- Si SPY < promedio de 200 días: 20% en cada uno de SHY, IEF, TLT, GLD, LQD.
- Estuvo a la defensiva el **17%** de los meses.

### Resultados

**Periodo de PRUEBA (2019–hoy, fuera de muestra):**

| Métrica | v1 Multiactivo | v2 Sectores | v3 Régimen | SPY |
|---|---|---|---|---|
| CAGR | 9.6% | 8.5% | 8.5% | **16.8%** |
| Volatilidad | **11.9%** | 12.7% | 13.0% | 19.2% |
| Sharpe | **0.68** | 0.55 | 0.54 | 0.80 |
| Máx. caída | **-17.7%** | -20.0% | -26.2% | -33.7% |
| Beta | 0.35 | 0.49 | 0.39 | 1.00 |
| **Alfa CAPM anual** | **+2.5%** | -0.6% | +1.1% | 0 |
| Information ratio | -0.47 | -0.65 | -0.53 | — |

**v1 por periodo:**

| | Diseño 2009–2018 | Prueba 2019–hoy | Completo |
|---|---|---|---|
| CAGR | 9.8% | 9.6% | 9.7% |
| CAGR SPY | 12.7% | 16.8% | 14.5% |
| Volatilidad | 11.8% | 11.9% | 11.8% |
| Sharpe | 0.77 | 0.68 | 0.73 |
| Máx. caída | -15.9% | -17.7% | -17.7% |
| Alfa CAPM | +3.8% | +2.5% | +3.2% |

Rotación promedio anual: 531% · Última asignación v1: SPY 20%, EFA 20%, VNQ 20%, SHY 40%.

**Prueba de robustez v1** (Sharpe en prueba con 12 combinaciones): de **0.43 a 0.71**. **Ninguna se derrumba → no está sobreajustada.**

| Lookback | Top 3 | Top 4 | Top 5 |
|---|---|---|---|
| 63 días | 0.669 | 0.528 | 0.530 |
| 126 días | 0.427 | 0.636 | **0.683** |
| 189 días | 0.584 | 0.605 | 0.593 |
| 252 días | 0.628 | 0.604 | 0.708 |

**Por qué ninguna le gana al SPY en rendimiento:**
1. Mucho tiempo en refugio (SHY) por el filtro de tendencia de cada activo.
2. 2019–2025 fue un mercado dominado por pocas gigantes tecnológicas; casi cualquier estrategia diversificada quedó atrás.
3. La beta baja de v2/v3 es real: el filtro sale del mercado en los periodos más turbulentos (COVID 2020, 2022), que son los que más pesan en la beta; el costo es perder los rebotes.

---

## 9. Experimentos dentro del Lab

### Comparación de 15 métodos de Portfolio Construction (11 ETFs, sin límites)

| Método | Activos efectivos | Mayor peso | Volatilidad |
|---|---|---|---|
| Mean-variance (closed form) | 1.4 | 84.8% (SHY) | 2.6% |
| **Equal weight (1/N)** | **11.0** | **9.1%** | 10.9% |
| Metric weight | 3.0 | 41.2% | 16.0% |
| Mean-variance (constrained) | 1.0 | 100% | 1.8% |
| Inverse volatility | 4.8 | 39.8% | 5.6% |
| Risk parity | 4.4 | 43.3% | 5.4% |
| Hierarchical risk parity | 1.4 | 82.8% | 2.4% |
| Hierarchical equal risk contribution | 2.9 | 56.5% | 4.8% |
| Nested clustered optimization | 1.3 | 85.9% | 2.5% |
| Maximum diversification | 2.1 | 66.1% | 4.0% |
| Minimum CVaR | 1.1 | 96.8% | 1.9% |
| Minimum CDaR | 1.1 | 93.2% | 2.2% |
| Black-Litterman / KN index / Feature weighting | — | Cannot be sized | — |

**Hallazgo:** 10 de 15 métodos concentran más de 80% en un activo (SHY), porque los optimizadores premian lo menos volátil. El más diversificado es **1/N** (respaldo: DeMiguel, Garlappi y Uppal, 2009).

### Backtest oficial en el Lab: Risk parity, tope 20%, mensual
Configuración: $100,000 · 1% en efectivo · comisión 0.05¢/acción · **slippage: estimated spread** · vs SPY · 2008–2026.

| | Risk parity (Lab) | SPY |
|---|---|---|
| CAGR | 2.8% | 11.1% |
| Volatilidad | 7.1% | 19.7% |
| Sharpe | 0.40 | 0.56 |
| Sortino | 1.02 | 0.77 |
| Máx. caída | -19.7% | -51.5% |
| CVaR 5% | 1.0% | 3.0% |
| Exceso de rendimiento | -8.3% | — |
| Information ratio | -0.49 | — |
| Costos | $1,351 | — |

Peor año: **2022, -13.8%** (los bonos cayeron con la subida de tasas). Un método **estático** no reacciona.

**Comparación clave para el pitch (mismos 11 ETFs):**

| | Risk parity estático (Lab) | **v1 dinámica (momentum)** |
|---|---|---|
| CAGR | 2.8% | **9.7%** |
| Sharpe | 0.40 | **0.73** |
| Máx. caída | -19.7% | **-17.7%** |

*Periodos no idénticos (el Lab incluye 2008), pero la diferencia es enorme.* Esto responde a "modelos dinámicos, no reglas fijas".

---

## 10. Archivos, comandos y carga de nuestra estrategia al Lab

**Archivos (carpeta `Hakathon 2026`):**
- `estrategia.py` (**v5**): estrategia, backtest, métricas, robustez, gráfica y exportación de pesos (en 3 formatos).
- `diagnostico.py`: revisa la salud de los CSV.
- `resultados_multiactivo\`:
  - `metricas.csv`, `robustez.csv`, `curva.png`
  - `pesos_mensuales.csv`: pesos en la fecha de la señal (fin de mes).
  - `pesos_lab_multiactivo.csv`: formato **vertical** (`date` + una columna por ticker).
  - **`weights.csv`**: formato **horizontal, idéntico al weights.csv que genera el Lab** ← el que se usa para el Lab.
- `resultados_sectores\`, `resultados_regimen\` (versiones descartadas; sirven para la lámina de método).

**Comandos (PowerShell, dentro de la carpeta):**
```
python estrategia.py . multiactivo     # estrategia final (v1) + archivos para el Lab
python estrategia.py . sectores        # v2
python estrategia.py . regimen         # v3
python diagnostico.py .                # revisar datos
```
Requisitos: `pip install pandas numpy matplotlib` (ya instalados; Python 3.14 en la laptop de Diego).

**Corrida confirmada en la laptop de Diego (v5, 14:25):** mismos resultados de la v1 y *"Pesos para el Lab: resultados_multiactivo\pesos_lab_multiactivo.csv (214 rebalanceos)"*.

### Formato del weights.csv del Lab (descubierto con el archivo de Risk parity)

| | weights.csv del Lab (Risk parity) | Nuestro weights.csv (v1) |
|---|---|---|
| Primera columna | `Ticker` | `Ticker` ✅ |
| Filas | 11 ETFs, orden alfabético (EEM, EFA, GLD, IEF, IWM, LQD, QQQ, SHY, SPY, TLT, VNQ) | Los mismos, mismo orden ✅ |
| Columnas | Una por fecha de rebalanceo | Igual ✅ |
| Pesos por fecha | Suman 1 | Suman 1, sin vacíos ✅ |
| Fechas | Fin de mes, 2008-01-31 → 2026-11-12 (227) | **Día hábil siguiente** a la señal, 2009-02-02 → 2026-11-02 (214) |

- El motor de KaxaNuk **rebalancea en la fecha que trae el archivo**. Por eso nuestras fechas son el día hábil siguiente al cierre de fin de mes (sin información del futuro).
- Empezamos en 2009 porque 2008 es el periodo de calentamiento (promedio de 200 días y momentum de 6 meses).
- Dato del Lab: en Risk parity, **SHY está siempre en 20%** (el tope) e **IEF casi siempre en 20%**: el optimizador empuja todo hacia lo menos volátil.

### Cómo meter nuestra v1 al backtest oficial del Lab
1. **Opción oficial:** preguntar a los mentores cómo cargar un weights.csv propio al Backtest Engine.
2. **Plan B (cambio de archivo):**
   1. En la carpeta del portafolio de Risk parity, renombrar el original a `weights_riskparity_ORIGINAL.csv` (no borrarlo).
   2. Copiar `resultados_multiactivo\weights.csv` a esa carpeta con el nombre exacto `weights.csv`.
   3. Backtest → Parameters → elegir ese portafolio con los mismos costos (estimated spread, 0.05¢/acción, $100K, 1% en efectivo, vs SPY) → **Run the backtest**.
   4. Tomar capturas. ⚠️ En el Lab seguirá llamándose "Risk parity": aclarar en el pitch que es nuestra estrategia de momentum.
   5. Restaurar el original al terminar.
- **Resultado esperado:** cercano a nuestro código (~9.7% anual, volatilidad ~12%, caída máxima ~-18%); puede variar un poco por los costos del Lab y la fecha de inicio.

**Formato vertical alternativo (motor standalone, según su documentación):** primera columna `date`, una columna por ticker, sin vacíos; va en `Input/Portfolios/`.

---

## 11. Pendientes

### Hecho desde las 13:25
- [x] Encontrar el weights.csv que generó el Lab para Risk parity y analizar su formato.
- [x] estrategia.py v5: genera `weights.csv` con el mismo formato del Lab (verificado: mismos tickers, mismo orden, sin vacíos, pesos suman 1).
- [x] Diego corrió la v5 en su laptop: resultados confirmados y 214 rebalanceos exportados.

### Ahora
- [ ] Cargar nuestro `weights.csv` al Backtest Engine del Lab (forma oficial o plan B de la sección 10).
- [ ] Correr el backtest oficial de la v1 en el Lab vs SPY (y KN US Equity Core si aparece) y tomar capturas.
- [ ] Plan C, si nada funciona: **Feature weighting** con una columna de momentum creada en **Curator → Calculations**.

### Preguntas para los mentores
- [ ] ¿El **tope de 20%** aplica a ETFs o solo a acciones individuales? (Nuestra v1 llega a tener hasta 60% en SHY en crisis.)
- [ ] ¿Qué es exactamente el **KN US Equity Core** y cómo se agrega como benchmark en el Lab?
- [ ] ¿Cómo se carga un weights.csv propio (mismo formato que Portfolio Construction) al Backtest Engine del Lab?

### Para hoy antes de las 22:00
- [ ] **Simulación de la pensión de Ana** (4% real vs. nuestra estrategia, en pesos al mes).
- [ ] **Modelo de negocio:** quién paga, cuánto, retención, ruta CNBV.
- [ ] **Perfiles de producto** (conservador / dinámico) para "cómo se adapta a cada perfil".
- [ ] Borrador de pitch y lámina de método.

### Mañana (cierre 12:00)
- [ ] README de "cómo correr el código".
- [ ] Capturas finales del Lab.
- [ ] Ensayar el pitch 2 veces con cronómetro.
- [ ] Entregar antes de las 11:30.

---

## 12. Material para el pitch

**Frases clave:**
- *"No le ganamos al SPY en rendimiento bruto en 2019–2025, un periodo dominado por pocas tecnológicas. Pero generamos +2.5% anual de alfa ajustado por riesgo, con la mitad de la caída."*
- *"Probamos 3 versiones y elegimos con disciplina, sin perseguir el resultado."*
- *"Con los mismos 11 ETFs, la regla dinámica rinde más del triple que el método estático del Lab (9.7% vs 2.8%), con menor caída."*
- *"Comparamos 15 métodos del Lab: 10 concentraban más de 80% en un solo activo; por eso no usamos optimizadores de media-varianza."*
- *"Backtest con comisión por acción y slippage estimado con el spread real de cada ETF."*
- *"Elegimos ETFs por clase de activo para evitar el sesgo de supervivencia sin depender de datos premium."*
- **Para Ana:** el mayor riesgo de una inversionista joven es vender en pánico en una caída de -34%. Con una caída máxima de ~-18%, es más probable que se quede invertida 43 años.

**Lámina de método (anti-sobreajuste):**
1. Lógica económica escrita antes del backtest.
2. Separación diseño 2009–2018 / prueba 2019–hoy (una sola vez).
3. Pocos parámetros (ventana de momentum y número de activos).
4. Prueba de robustez: 12 combinaciones, Sharpe en prueba de 0.43 a 0.71.
5. Ejecución al día siguiente de la señal (sin información del futuro).
6. Costos incluidos.
7. Universo elegido por clase de activo, no por desempeño pasado.
8. Transparencia: v2 y v3 no mejoraron; se documentan y se descartan.

**Modelo de negocio (borrador):**
- Cliente: Ana, ahorro voluntario complementario a su Afore.
- Canal sugerido: B2B2C, empresas que lo ofrecen como prestación (cuota ~0.5% anual sobre activos).
- Regulación: operar como asesor en inversiones registrado ante la CNBV o en alianza con una casa de bolsa o distribuidora autorizada.

---

## 13. Referencias

- KaxaNuk Data Curator: https://kaxanuk-data-curator.readthedocs.io · https://pypi.org/project/kaxanuk-data-curator/
- KaxaNuk Backtest Engine (Quick Start): https://kaxanuk-backtest-engine.readthedocs-hosted.com/en/latest/user_guide/quick_start.html
- Jegadeesh, N. y Titman, S. (1993). *Returns to Buying Winners and Selling Losers.* Journal of Finance.
- Moskowitz, T. y Grinblatt, M. (1999). *Do Industries Explain Momentum?* Journal of Finance.
- Faber, M. (2007). *A Quantitative Approach to Tactical Asset Allocation.* Journal of Wealth Management.
- Moskowitz, T., Ooi, Y. H. y Pedersen, L. H. (2012). *Time Series Momentum.* Journal of Financial Economics.
- DeMiguel, V., Garlappi, L. y Uppal, R. (2009). *Optimal Versus Naive Diversification: How Inefficient is the 1/N Portfolio Strategy?* Review of Financial Studies.
- López de Prado, M. (2016). *Building Diversified Portfolios that Outperform Out of Sample.* Journal of Portfolio Management.
- Antonacci, G. (2014). *Dual Momentum Investing.* McGraw-Hill.
