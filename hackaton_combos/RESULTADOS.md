# Combinaciones del modelo principal (acciones) con 6 sectores cíclicos (ETF)

Reglas y criterio, fijados antes de correr: `preparar.py`.
- **Motor:** Backtest Engine 0.68.0, con costos base de 1 + 5 pb y de estrés de 5 + 10 pb, y 2% de
  reserva de efectivo.
- **Precios:** `datos_backtest_combo/motor`, que es la carpeta del principal (reproduce su +3.00%)
  más los ETF sectoriales del Curator.

| | CAGR 2007–26 | Alfa 2007–26 (estrés) | Volatilidad | Sharpe | Caída máx. | Alfa 2010–26 (estrés) | Caída 2010–26 | Acción máx. | ETF máx. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Modelo principal | 13.46% | +3.00% (+2.23%) | 20.7% | 0.65 | −30.9% | +0.08% (−0.65%) | −30.9% | 6% | 100% (SHY/IEF) |
| **C1: 50% principal + 50% cíclicos** | 13.65% | +3.20% (+2.58%) | **18.5%** | **0.74** | **−25.6%** | **+1.24% (+0.62%)** | **−23.1%** | 3% | 100% (SHY) |
| **C2: el núcleo SPY del principal pasa a cíclicos** | **14.22%** | **+3.77% (+2.85%)** | 22.0% | 0.65 | −27.9% | +0.47% (−0.44%) | −27.5% | 6% | 100% (SHY/IEF); XLK/XLY hasta 70% |

**Las dos cumplen el criterio:** acciones de 20% o menos; alfa con estrés en 2007–26 mayor que
+2.23%; alfa con estrés en 2010–26 mayor que −0.65%; caída máxima de −35% o menos.
**Con la regla de desempate (mayor alfa con estrés en 2007–26), gana C2.**

Notas:
- C1 tiene mejor relación riesgo/rendimiento: mejor Sharpe, menos volatilidad, menos caída y el
  mejor alfa en 2010–26 (+0.62% con estrés, la única positiva en esa ventana). C2 tiene más alfa
  total, pero depende más de 2007–09.
- Si el tope de 20% aplicara también a ETFs, ninguna de las dos lo cumpliría, igual que el modelo
  principal, que ya pone 40–70% en SPY.
- Componente de ETF: ciclicos6_top2 pasó su propio criterio por 0.09 puntos (ver
  `hackaton_etf/RESULTADOS.md`).
- El modelo principal congelado no se modificó; estas combinaciones son alternativas.

## Corrección de C2: refugio confirmado por el modelo de riesgo (`c2_confirmado.py`, `C2_confirmado/`)

**Diagnóstico** (`diagnostico.py`, `DIAGNOSTICO_2010_2026.txt`): en 2010–2026, los refugios de C2
restan −2.95 puntos al año, porque salen tarde y se pierden el rebote (−14.6 en 2023, −8.6 en 2015,
−8.2 en 2019 y −7.3 en 2025). Las acciones suman +4.24 y los sectores +0.86.

**Corrección (pre-registrada):** el refugio del principal (régimen de caída o interruptor) solo se
toma si el modelo de `filtro_riesgo` confirma el riesgo (probabilidad mayor a 0.222). Si no lo
confirma, se usa la rotación de sectores cíclicos. El modelo vetó 8 de 34 fechas de refugio, entre
ellas 2018-11, 2020-03-06, 2022-10, 2023-11 y 2025-04-10.

| | Alfa 2007–26 (estrés) | Sharpe 2007–26 | Caída máx. 2007–26 | Alfa 2010–26 (estrés) | Caída 2010–26 |
| --- | --- | --- | --- | --- | --- |
| C1: mitad y mitad | +3.20% (+2.58%) | 0.74 | −25.6% | +1.24% (+0.62%) | −23.1% |
| C2: núcleo cíclico | +3.77% (+2.85%) | 0.65 | −27.9% | +0.47% (−0.44%) | −27.5% |
| **C2 confirmado** | **+4.28% (+3.33%)** | 0.64 | **−33.8%** | **+1.98% (+1.06%)** | −33.9% |

**Cumple el criterio:** alfa con estrés positivo en 2010–26 (+1.06%), alfa con estrés en 2007–26
mayor al de C1 (+3.33% contra +2.58%) y caída máxima de −33.8% (el límite era −35%).

**Costo a la vista:** su peor caída pasa a ser la de 2018-09 a 2020-03-23 (−33.9%). El 2020-03-06 el
modelo vetó la salida del interruptor, porque su probabilidad era la del cierre de febrero (0.17,
todavía tranquila), y la estrategia se quedó en sectores durante el desplome del COVID. Tiene menos
Sharpe que C1 (0.64 contra 0.74).

## Variante pre-registrada: 3 acciones al 20% (`variante_20pct.py`, `C2_20pct/`)

**Cambio:** el componente de acciones lleva 3 acciones en vez de 10, a 20% cada una en el régimen
alcista y a 10% en el mixto. Todo lo demás es igual a C2 confirmada.

**Criterio, fijado antes de correr:**
- alfa con estrés 2007–26 mayor a +3.33%;
- alfa con estrés 2010–26 mayor a +1.06%;
- caída máxima de −40% o menos;
- ninguna acción arriba de 20%.

| | C2 confirmada (principal) | Variante 20% |
| --- | --- | --- |
| CAGR 2007–26 (estrés) | 14.74% (13.78%) | 16.25% (15.22%) |
| Alfa 2007–26 (estrés) | +4.28% (+3.33%) | **+5.80% (+4.77%)** ✅ |
| Alfa 2010–26 (estrés) | +1.98% (+1.06%) | **+3.49% (+2.47%)** ✅ |
| Volatilidad / Sharpe 2007–26 | 23.2% / **0.64** | 27.4% / 0.59 |
| Caída máxima 2007–26 | −33.8% | **−40.4%** ❌ (estrés −41.3%) |
| Acción máxima | 6% | 20% ✅ |

**Veredicto: no pasa por la caída máxima** (−40.4% contra el límite de −40%). Se queda C2
confirmada. La variante gana más alfa, pero con más riesgo: su Sharpe es menor (0.59 contra 0.64).

Nota técnica: las corridas de 2010 se cortaban por "Cash error" (redondeo a acciones enteras con 20%
en una acción). Se repitieron con los precios divididos entre 100 (`datos_backtest_combo_x01/motor`),
lo que no cambia ningún rendimiento: la corrida de 2007–2026 da lo mismo con las dos escalas (16.23%
contra 16.25%).

## Versión agresiva: regla de selección de OKRUS con tope de 20% (`variante_okrus_20pct.py`, `C2_okrus_20pct/`)

**Regla:** igual que C2 confirmada, pero las acciones se eligen con la regla "Agresiva" de OKRUS,
aplicada sin sesgo.
- Universo: las 300 más grandes del KN Core en cada fecha.
- Elegibles: precio arriba de su EMA200, a no más de 15% del máximo de 63 días, y momentum de 126
  días positivo.
- Las 3 mejores, a 20% en alcista y a 10% en mixto.

**Límite de caída del usuario para el perfil agresivo:** −55%. **Regla de elección (fijada antes):**
la versión agresiva es la de mayor alfa con estrés en 2007–26 entre las dos variantes al 20%, siempre
que su alfa con estrés en 2010–26 sea positivo.

| | C2 confirmada | C2 20% (momentum 12-1) | **C2 20% regla OKRUS** |
| --- | --- | --- | --- |
| CAGR 2007–26 (estrés) | 14.74% (13.78%) | 16.25% (15.22%) | **17.82% (16.62%)** |
| Alfa 2007–26 (estrés) | +4.28% (+3.33%) | +5.80% (+4.74%) | **+7.37% (+6.17%)** |
| Alfa 2010–26 (estrés) | +1.98% (+1.06%) | +3.49% (+2.47%) | **+5.97% (+4.78%)** |
| Sharpe 2007–26 | 0.64 | 0.59 | **0.68** |
| Volatilidad | 23.2% | 27.4% | 26.3% |
| Caída máxima | −33.8% | −40.4% | **−34.0%** (estrés −35.1%) |
| Acción máxima | 6% | 20% | 20% |

**Elegida como versión agresiva.** Además, en esta ventana supera al modelo principal en alfa y en
Sharpe, con una caída casi igual. Las acciones más elegidas fueron NVDA, MU, TSLA, LVS, NFLX y WDC.
El universo es el KN Core de cada fecha, no una lista elegida hoy.

**Advertencia de método:** esta variante salió después de muchas pruebas sobre la misma ventana
(2007–2026). Su resultado fuera de muestra del modelo de riesgo (2010–26) es sólido, pero la
selección de la regla en sí no tuvo un periodo de prueba ciego.
