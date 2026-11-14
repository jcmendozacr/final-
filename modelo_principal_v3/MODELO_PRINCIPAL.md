# Modelo principal (v3): "Momentum concentrado"

Equipo **Los LITpsteins** · Talavera Valley Hackathon 2026 · Track 04 WealthTech.

> **Congelado el 2026-11-14 como modelo principal.** Reemplaza a la v2, "C2 confirmada"
> (`modelo_principal_c2/`), que se conserva como versión previa. Comparte con ella toda la
> estructura: regímenes, núcleo cíclico, freno de emergencia y modelo de riesgo. **Solo cambia cómo
> se eligen las acciones y cuántas son.** Huellas md5 en `MODELO_PRINCIPAL.md5`.
>
> Investigación y aprendizaje, no asesoría de inversión.

## 1. La idea

Concentrar la parte de acciones en las **3 acciones con la tendencia más fuerte**, aprovechando el
tope de 20% por acción del reto. Solo entran acciones que siguen en tendencia (arriba de su EMA de
200 días) y que no se están desplomando (a no más de 15% de su máximo de 63 días). El resto de la
cartera rota entre sectores cíclicos, y un freno de emergencia, confirmado por un modelo de riesgo,
pasa a bonos en las crisis.

## 2. Reglas

### 2.1 Señales mensuales (al cierre del último día hábil del mes)

| Señal | Definición |
| --- | --- |
| Tendencia | SPY ≥ al promedio de sus últimos 10 cierres de fin de mes |
| Canario | Momentum 13612 de TIP ≥ 0 (promedio de sus rendimientos totales a 1, 3, 6 y 12 meses) |
| Sectores cíclicos | Momentum de 252 sesiones de XLK, XLF, XLE, XLY, XLI y XLB |
| Riesgo | Probabilidad del modelo de riesgo (sección 2.6) |

### 2.2 Regímenes y cartera objetivo

| Régimen | Condición | Cartera |
| --- | --- | --- |
| **Alcista** | Tendencia arriba **y** canario OK | **60% en 3 acciones (20% cada una)** + **40%** núcleo cíclico |
| **Mixto** | Solo una señal en alerta | **30% en 3 acciones (10% cada una)** + **70%** núcleo cíclico |
| **Caída** | Tendencia abajo **y** canario en alerta | 100% en IEF o SHY (el de mayor 13612), sujeto a la confirmación de la sección 2.5 |

### 2.3 Las 3 acciones (la regla "Agresiva" de OKRUS, aplicada sin sesgo)

1. **Universo:** las **300 acciones de mayor peso** del KN US Equity Core al cierre de fin de mes,
   con los miembros de esa fecha.
2. **Precio:** índice de rendimiento total con datos de KaxaNuk (rendimiento en exceso + tasa
   implícita).
3. **Elegibles:** las que cumplen las tres condiciones:
   - precio > su **EMA de 200 días**;
   - precio ≥ **85% de su máximo de 63 días** (stop de 15%);
   - momentum de **126 días** > 0.
4. Se toman las **3** con mayor momentum de 126 días, a partes iguales. Si hay menos de 3
   elegibles, el peso que falta va a **SHY**.

### 2.4 Núcleo cíclico

Top 2 por momentum de 252 sesiones (> 0) entre XLK, XLF, XLE, XLY, XLI y XLB (los SPDR no
defensivos según Morningstar), a partes iguales. Si solo uno tiene momentum positivo, ese se lleva
todo el núcleo. Si ninguno, el núcleo va a SHY.

### 2.5 Salidas a refugio confirmadas por el modelo de riesgo

Hay fecha de refugio cuando la cartera objetivo pone 50% o más en SHY, IEF o TIP (régimen de caída o
interruptor de volatilidad). Si la probabilidad del modelo al último fin de mes anterior a la fecha
de operación es **mayor a 0.2222**, se ejecuta el refugio. Si no, esa fecha se usa la asignación del
núcleo cíclico al 100%.

### 2.6 Modelo de riesgo

Regresión logística con 4 variables (tendencia contra el promedio de 200 días, momentum de 12 meses,
volatilidad de 63 días y distancia al máximo de 252 sesiones). Se entrenó una sola vez, con datos de
2000-01 a 2009-09 del KN Core y de 11 índices sectoriales de KN, para predecir una caída de más de 5%
en 63 sesiones. Coeficientes, medias y desviaciones: `modelo_principal_c2/MODELO_PRINCIPAL.md`,
sección 2.6 (sin cambios).

### 2.7 Interruptor de volatilidad y operación

- **Interruptor:** si la volatilidad del SPY a 20 días pasa de 35%, la parte invertida va a SHY (con
  la confirmación de la sección 2.5). No actúa en régimen de caída.
- **Operación:** se opera el día hábil siguiente a la señal. En los días del interruptor se usan las
  acciones de la última señal de fin de mes.
- **Restricciones:** sin apalancamiento ni cortos. **Ninguna acción pasa de 20%**, el tope del reto.

## 3. Resultados (Backtest Engine 0.68.0, $100,000, reserva de 2%, costos en pb)

**Alfa = CAGR del modelo − CAGR del KN US Equity Core**, el campo "Alpha" del motor.

### 3.1 Del 2007-03-01 al 2026-11-06

| | **Costos base (1 + 5 pb)** | Costos de estrés (5 + 10 pb) | KN US Equity Core | SPY |
| --- | --- | --- | --- | --- |
| CAGR | **17.82%** | 16.62% | 10.45% | 10.39% |
| **Alfa vs KN Core** | **+7.37%** | **+6.17%** | — | — |
| Volatilidad | 26.3% | 26.3% | 20.0% | 20.0% |
| Sharpe / Sortino | **0.68** / 0.91 | 0.63 / 0.85 | 0.52 | 0.52 |
| Information Ratio | 0.39 | 0.34 | — | — |
| **Caída máxima** | **−34.0%** | −35.1% | −52.7% | −55.2% |
| Valor final de $100,000 | $2.83 M | — | $0.76 M | — |

**Peor caída:** del 2025-02-14 al 2025-04-08 (aranceles), recuperada el 2025-10-31. Al 2026-11-06 la
cartera está −27.3% abajo de su máximo del 2026-06-22.

### 3.2 Fuera de muestra del modelo de riesgo: 2010-01-04 a 2026-11-06

| | Costos base | Costos de estrés | KN Core |
| --- | --- | --- | --- |
| CAGR | 19.13% | 17.93% | 13.16% |
| **Alfa** | **+5.97%** | **+4.78%** | — |
| Sharpe | 0.73 | 0.68 | 0.74 |
| Caída máxima | −34.0% | −34.2% | −33.0% |

### 3.3 Por periodo (CAGR, costos base)

| Periodo | Modelo | KN Core | Diferencia |
| --- | --- | --- | --- |
| 2007–2014 (fuera de muestra para la regla de selección) | 11.5% | 7.6% | **+3.9** |
| 2015–2019 | 10.5% | 11.4% | −1.0 |
| 2020–2026 | 33.3% | 14.1% | +19.2 |

Le gana al KN Core en 11 de 19 años calendario.

## 4. Pruebas contra el sobreajuste y el sesgo (fijadas antes de verlas)

| Prueba | Resultado |
| --- | --- |
| Sin información del futuro | ✅ Señal al cierre de fin de mes, operación al día siguiente; el universo usa los pesos del KN Core de ese día |
| Sin sesgo de supervivencia | ✅ Universo del KN Core de cada fecha; las acciones que dejan de cotizar se venden a su último precio (MEDI, UST, FRX, PCYC, GMCR, entre otras) |
| Fuera de muestra para la regla (OKRUS la diseñó con datos de 2012+) | ✅ 2007–2014: +3.9 puntos al año contra el KN |
| Sensibilidad: al menos 5 de 7 variantes superan el +4.28% de la v2 | ✅ **6 de 7** (tabla abajo) |
| Acción máxima ≤ 20% | ✅ |

| Variante (un parámetro a la vez) | Alfa (costos base) | Sharpe | Caída máx. |
| --- | --- | --- | --- |
| **Base: 3 acciones, momentum 126 días, stop 15%** | **+7.37%** | 0.68 | −34.0% |
| 4 acciones (15% c/u) | +5.45% | 0.63 | −36.3% |
| 5 acciones (12% c/u) | +5.27% | 0.65 | −37.6% |
| Momentum 63 días | +1.74% | 0.49 | −34.0% |
| Momentum 189 días | +8.53% | 0.72 | −34.6% |
| Momentum 252 días | +8.42% | 0.70 | −35.6% |
| Stop 10% | +7.93% | 0.71 | −33.5% |
| Stop 20% | +8.74% | 0.72 | −35.6% |

Los parámetros base no son los que dan más alfa: no se eligieron a mano para maximizar el resultado.

**Limitaciones honestas:**
1. El alfa se concentra en 2020–2026 (+19.2 puntos al año). En 2015–2019 empató con el índice.
2. La regla salió después de varias rondas de pruebas sobre la misma ventana. La prueba de 2007–2014
   y la sensibilidad la respaldan, pero no es una prueba ciega completa.
3. Concentración: 60% en 3 acciones en régimen alcista. La volatilidad (26.3%) es mayor que la del
   índice.

## 5. Comparación con versiones anteriores (2007–2026; entre paréntesis, con estrés)

| | Alfa | Sharpe | Caída máx. | Acción máx. |
| --- | --- | --- | --- | --- |
| **v3 (este modelo)** | **+7.37% (+6.17%)** | **0.68** | −34.0% | 20% |
| v2, C2 confirmada | +4.28% (+3.33%) | 0.64 | −33.8% | 6% |
| v1, `MODELO_ACTUAL.md` | +3.00% (+2.23%) | 0.65 | −30.9% | 6% |

## 6. Cómo replicarlo

Requiere `KN/` (CSV del KN US Equity Core y del Factor Model), `KN_sectores/` y la licencia del
Backtest Engine.

```powershell
$env:PYTHONUTF8 = 1
# 1. Régimen con 3 acciones (pesos por régimen e interruptor)
.venv\Scripts\python modelo_regimen.py KN datos_etf\precios resultados_regimen_n3_a60 0.35 3 0.60
# 2. Modelo de riesgo y núcleo cíclico (ver modelo_principal_c2/MODELO_PRINCIPAL.md, sección 7)
.venv\Scripts\python filtro_riesgo\filtro.py KN KN_sectores
.venv\Scripts\python hackaton_etf\filtros_ciclicos.py
# 3. Estructura C2 con 3 acciones y confirmación del modelo de riesgo
.venv\Scripts\python hackaton_combos\variante_20pct.py
# 4. Precios del motor reescalados y selección de acciones con la regla OKRUS
.venv\Scripts\python hackaton_combos\escalar_motor.py hackaton_combos\C2_20pct\weights.csv
.venv\Scripts\python hackaton_combos\variante_okrus_20pct.py KN     # → hackaton_combos\C2_okrus_20pct\weights.csv
# 5. Backtest
$env:KNBE_API_KEY_KAXANUK = "<LICENCIA>"
.venv\Scripts\python correr_backtest.py datos_backtest_combo_x01\motor modelo_principal_v3 weights salida\base 2007-03-01 2026-11-06 1.0 5.0 0.02
```

**Control:** `weights.csv` debe dar el md5 de `MODELO_PRINCIPAL.md5`. La última asignación (señal del
2026-10-30, operada el 2026-11-02) es MRNA, CRWD y PANW a 20% cada una, más XLB 20% y XLE 20%. Se
reporta solo como control, no como recomendación.
