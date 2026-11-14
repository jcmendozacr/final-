# Attribution Analysis del modelo principal v3

Librería **Attribution Analysis** del Investment Lab de KaxaNuk (`correr_atribucion.py`), con los
métodos Brinson-Fachler, modelo de factores y modelo de factores activo, contra el KN US Equity Core.
Del 2007-03-02 al 2026-11-06 (4,954 días).

- **Entradas:** `hackaton_combos/preparar_atribucion_c2.py` con el `Daily_Weights.csv` del backtest
  oficial (`backtests/backtest_2007_base`).
- **Resultado:** `datos_atribucion_v3/Output/*.xlsx` (no va en el repo: son datos derivados de
  KaxaNuk).

**Aproximaciones:**
- los ETF sectoriales se abren en las acciones del KN Core de su sector KN;
- SHY, IEF y TIP cuentan como efectivo (rendimiento 0);
- no incluye costos.

Por eso su rendimiento acumulado (+2,846%) difiere del backtest oficial (+2,730%, con costos y con el
rendimiento de los bonos).

## De dónde viene el rendimiento activo

Rendimiento activo acumulado: +2,235% (+8.29% al año en esta aproximación), con un Information Ratio
de 0.41.

| Fuente | Contribución acumulada | Lectura |
| --- | --- | --- |
| **Específico de cada acción** | **+1,670%** | La selección de las 3 acciones gana más de lo que explican los factores |
| **Factor momentum** | **+1,029%** | La idea central del modelo funciona |
| Sector tecnología | +162% | |
| Sector energía | +136% | |
| Sector comunicación | +112% | |
| Mercado | −310% | El modelo tiene menos exposición al mercado que el índice (refugios) |
| Volatilidad residual | −295% | Las acciones de momentum son volátiles y ese factor restó |
| Tamaño | −113% | Sesgo hacia empresas algo menores que el índice |

**Conclusión:** el alfa viene del **momentum** y de la **selección de acciones**, no de tomar más
riesgo de mercado. Es consistente con la lógica escrita antes del backtest.
