# Tres ideas con tope de 20% × dos filtros de mercado: resultados (Backtest Engine, 2010-01-04 a 2026-11-06)

Reglas: `preparar.py`. Criterio, fijado antes de correr: `evaluar.py`. Tabla completa: `evaluacion.csv`.

- **Datos:** acciones con datos de KaxaNuk; ETFs con el Data Curator.
- **Motor:** Backtest Engine 0.68.0, con costos base de 1 + 5 pb y de estrés de 5 + 10 pb, y 2% de
  reserva de efectivo.
- **Modelo de riesgo:** entrenado con 2000–2009 (`filtro_riesgo/`).
- **Referencia:** el modelo principal congelado, corrido en la misma ventana con
  `datos_backtest_p1/motor`. Esa carpeta reproduce exactamente su resultado oficial de 2007–2026
  (CAGR 13.46%, alfa +3.00%, caída −30.87%).

## Resultados (costos base, salvo la columna de estrés)

| Combinación | CAGR | Alfa vs KN | Alfa estrés | Volatilidad | Sharpe | Caída máx. | Vs KN 2010–17 | Vs KN 2018–26 | Ref. 2001–09 (dentro de muestra) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Modelo principal | 13.24% | +0.08% | −0.65% | 20.7% | 0.64 | −30.9% | +0.61 | −0.49 | — |
| I1 líder sectorial, filtro base | 9.42% | −3.73% | −4.98% | 24.1% | 0.39 | −41.7% | −8.95 | +0.85 | +14.21 |
| I1 líder sectorial, filtro modelo | 9.39% | −3.76% | −5.04% | 25.8% | 0.36 | −41.7% | −7.74 | −0.38 | +10.24 |
| I2 Estrella + A1, filtro base | 13.13% | −0.03% | −0.91% | 18.4% | 0.71 | −26.8% | −5.31 | +4.92 | +10.87 |
| **I2 Estrella + A1, filtro modelo** | **14.57%** | **+1.41%** | **+0.51%** | 19.3% | **0.76** | **−26.8%** | −4.65 | **+7.23** | +7.08 |
| I3 top 5, filtro base | 12.09% | −1.07% | −1.94% | 19.1% | 0.63 | −32.0% | −6.02 | +3.53 | +7.28 |
| I3 top 5, filtro modelo | 11.62% | −1.54% | −2.39% | 19.9% | 0.58 | −30.0% | −5.18 | +1.75 | +2.21 |

"Vs KN" = diferencia de CAGR contra el KN Core en el periodo, en puntos por año.

## Veredicto con el criterio

Ninguna cumple las cuatro condiciones, así que se queda el modelo principal. I2 con el filtro del
modelo cumple tres: tope de 20%, más alfa con estrés que el modelo principal (+0.51% contra −0.65%)
y una caída de −26.8%. **Falla la cuarta:** pierde contra el KN Core por 4.65 puntos al año en
2010–2017.

## Hallazgos

1. **En 2010–2026, el modelo principal tampoco tiene alfa:** +0.08%, y −0.65% con estrés. Su +3.00%
   oficial (2007–2026) sale casi todo de 2007–2009. Hay que tenerlo en cuenta en el pitch.
2. **2010–2017 fue un mercado alcista largo y parejo, y ninguna estrategia de momentum le ganó al
   índice ahí.** Todas pierden entre 4.6 y 9 puntos al año. Desde 2018 sí ganan: I2 con el modelo,
   +7.2 puntos al año.
3. **El filtro del modelo no ayuda de forma consistente.** Mejora a I2 (+1.4 puntos de alfa), pero
   empeora un poco a I1 y a I3. Con esta evidencia no se puede afirmar que agregue valor de forma
   robusta.
4. **El tope de 20% por posición no limita la concentración por tema.** En mayo–julio de 2026, I2
   tenía XLK, SMH, MU y AMD: 80% en semiconductores y tecnología. Desde el 2026-06-15 cae −25%,
   mientras el KN baja −2%. La misma caída aparece en todas las estrategias de momentum de este
   trabajo.
5. **I2 (Estrella + A1) es la más sólida de las tres:** mejor Sharpe (0.71–0.76) y menor caída
   (−26.8%) que el modelo principal en 2010–2026, con todas las posiciones de 20% o menos.
