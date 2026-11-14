# Attribution Analysis del modelo principal v2 (C2 confirmada)

Corrido con la librería **Attribution Analysis** del Investment Lab de KaxaNuk (`correr_atribucion.py`),
con los métodos Brinson-Fachler, modelo de factores y modelo de factores activo. Benchmark: KN US
Equity Core. Ventana: del 2007-03-02 al 2026-11-06 (4,954 días).

- **Entradas:** `preparar_atribucion_c2.py`, a partir del `Daily_Weights.csv` del backtest oficial.
- **Resultado:** `datos_atribucion_c2/Output/*.xlsx`.

## Aproximaciones (leer antes de citar)

- **ETF sectoriales:** se abren en las acciones del KN Core de su sector KN de cada día (XLK →
  Technology, etc.). Los SPDR y los sectores de KN no son idénticos.
- **Refugios:** SHY, IEF y TIP se tratan como efectivo, con rendimiento 0.
- **Costos:** la atribución no incluye costos. Por eso su rendimiento (15.5 veces) difiere del
  backtest oficial (16.5 veces con costos base, porque ahí los refugios sí rinden).
- **Brinson-Fachler:** sin un mapa de sectores, cada acción es su propio segmento, así que todo el
  efecto sale como asignación. Para este modelo, la lectura útil es la del modelo de factores.

## De dónde viene el rendimiento activo (contra el KN US Equity Core)

Rendimiento activo acumulado: +942% (+4.85% al año en esta aproximación). Contribución acumulada de
cada factor (enlazada con Carino):

| Fuente | Contribución acumulada | Lectura |
| --- | --- | --- |
| **Específico de cada acción (idiosincrático)** | **+799%** | La selección de las 10 acciones gana más de lo que explican los factores |
| **Momentum** | **+620%** | La exposición al factor de momentum de KaxaNuk: la idea central del modelo funciona |
| Energía | +209% | La rotación hacia energía cuando tenía tendencia (2021–2022) |
| Tecnología | +73% | La rotación hacia tecnología |
| Mercado | −235% | Menos exposición al mercado que el índice (refugios, beta < 1): cuesta en mercados alcistas |
| Beta | −224% | Ídem |
| Volatilidad residual | −210% | Las acciones de momentum suelen ser volátiles, y ese factor restó |
| Tamaño | −80% | Sesgo hacia empresas algo menores que el índice |

**Conclusión:** el alfa del modelo viene del **momentum** y de la **selección de acciones**, no de
tener más mercado: tiene menos exposición al mercado que el índice. Es consistente con la lógica
económica escrita antes del backtest.
