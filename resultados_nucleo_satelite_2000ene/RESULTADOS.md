# Núcleo ETF + satélite de momentum — resultados 2000-01-03 a 2026-11-06

Equipo de Habib, Talavera Valley Hackathon 2026, Track 04 WealthTech. Corridas del 2026-11-13 con
el Backtest Engine 0.68.0 y Attribution Analysis 0.7.0 de KaxaNuk, en la computadora de Habib (no en
la plataforma web del Lab). Benchmark: KN US Equity Core.

## La regla (escrita antes del backtest)

- Núcleo: 70% en SPY.
- Satélite: 30% en las 20 acciones con mayor momentum de 12 meses sin el último mes, entre las 300
  de mayor peso del KN US Equity Core en la fecha de la señal (miembros a la fecha), 1.5% cada una.
- Señal al cierre de fin de mes; se opera el día hábil siguiente. Primer rebalanceo 2000-01-03,
  último 2026-11-02, 323 rebalanceos, 663 tickers.
- Lógica económica: las acciones que más subieron en 12 meses tienden a seguir rindiendo más unos
  meses (Jegadeesh y Titman, 1993); el núcleo mantiene la beta cerca de 1.

## Backtest Engine, 2000-01-03 a 2026-11-06 (27.79 años valuados, la ventana completa)

Costos base: comisión 1 pb y slippage plano 5 pb. Estrés: 5 pb y 10 pb. Capital $100,000, 1% de
efectivo de reserva, posiciones de empresas que dejan de cotizar vendidas al último precio.

| | Núcleo + satélite | Estrés de costos | KN US Equity Core | SPY |
| --- | --- | --- | --- | --- |
| CAGR (años del motor) | 9.04% | 8.78% | 7.85% | 7.81% |
| Volatilidad anual | 20.43% | 20.44% | 19.63% | 19.65% |
| Caída máxima | -53.10% | -53.30% | -52.67% | -55.18% |
| Alfa anual | +1.19% | +0.93% | — | — |
| Information Ratio | +0.21 | +0.18 | — | — |
| Comisiones | $1,959 | $9,335 | — | — |
| Slippage | $9,292 | $17,692 | — | — |

El Sharpe del motor se calculó con tasa libre de riesgo de 0 (sin archivo de tasas): cartera 0.44,
KN US Equity Core 0.40, SPY 0.40; solo sirve para comparar entre columnas.

## Por periodo (serie diaria del motor, costos base)

| Periodo | Cartera, anual | KN Core, anual | Exceso anual | IR |
| --- | --- | --- | --- | --- |
| 2000 (satélite aproximado, ver abajo) | -10.3% | -9.9% | -0.4 | +0.15 |
| 2000-2002, caída de las puntocom | -13.6% (total -35.4%) | -15.2% (total -38.8%) | +1.5 | +0.27 |
| 2000-2008 | -1.7% | -3.5% | +1.8 | +0.32 |
| 2009-2018, periodo de diseño | 13.4% | 13.1% | +0.3 | +0.09 |
| 2019-2026-11-06, prueba fuera de muestra | 18.0% | 16.3% | +1.7 | +0.26 |

Por año (Brinson-Fachler de Attribution Analysis): alfa positivo en 17 de 27 años; 2000 -1.1
puntos, 2001 +0.5, 2002 +3.7.

## Attribution Analysis, 2000-01-04 a 2026-11-06

Modelo de factores de KaxaNuk (KN US Equity Factor Model, 17 factores: mercado, tamaño, valor,
momentum, beta, volatilidad residual y 11 sectores), aplicado también a los pesos del benchmark
(active_factor_model). Efectos acumulados enlazados con Carino.

- Rendimiento total: cartera +952.2%, benchmark +640.1%; rendimiento activo +312.1 puntos.
- Activo anualizado +1.42%; tracking error 5.73%; Information Ratio +0.27; beta 1.03; la cartera
  le ganó al benchmark el 53.5% de los días.
- Del rendimiento activo: factores +80.2 puntos, específico de las acciones +232.0 puntos.

| Factor | Aportación al rendimiento activo (puntos) |
| --- | --- |
| Momentum | +262.5 |
| Específico de las acciones (idiosincrático) | +232.0 |
| Tamaño | +32.5 |
| Energía | +25.1 |
| Comunicaciones | +14.1 |
| Tecnología | +10.8 |
| Materiales | +10.2 |
| Consumo discrecional | +9.5 |
| Otros sectores y mercado | +0.5 en conjunto |
| Valor | -24.0 |
| Volatilidad residual | -84.9 |
| Beta | -155.1 |

- Cobertura de factores: 98.2% del portafolio (falta el efectivo), 99.999% del benchmark.
- Conciliación del benchmark: el rendimiento calculado desde sus pesos queda 0.34 puntos al año
  debajo de la serie oficial (9.35% contra 9.69%, media diaria por 252), dentro de la tolerancia de
  1 punto; la librería avisa diferencias mayores a 1 pb en 1,623 de 6,752 días (máximo 36 pb).
- El SPY del núcleo se atribuyó con los pesos diarios del KN US Equity Core.

## Limitaciones

- 2000: los rendimientos por acción de KaxaNuk empiezan el 2000-01-03. Las señales de 2000 usan
  rendimientos de 1999 reconstruidos de los pesos diarios del índice, (peso hoy / peso ayer) x
  (1 + rendimiento del índice) - 1. Contra los reales de 2000: correlación diaria 0.94, error
  absoluto mediano 6 pb, y el top 20 por momentum coincide en 11 de 20. La señal de diciembre de
  1999 usa 251 días en vez de 252. Ningún día simulado usa la reconstrucción; desde el rebalanceo
  del 2001-02-01 las acciones elegidas son idénticas a una corrida sin reconstrucción.
- Precios: 433 tickers de Yahoo vía el Data Curator y 230 con la serie de KaxaNuk (226 que Yahoo no
  tiene, 2 que Yahoo no cubre completos y 2 cuyos precios de Yahoo no coinciden con KaxaNuk, como
  JCI con correlación 0.46). El detalle está en `datos_backtest_2000ene/fuente_de_precios.csv`.
- Yahoo no trae precios sin ajustar ni apertura ajustada: se opera al cierre ajustado por
  dividendos y la comisión se calcula sobre el cierre ajustado por splits. Las series de KaxaNuk no
  traen rango diario, por eso el slippage es plano.
- Cuando una acción deja de cotizar, el motor la vende y ese peso queda en efectivo hasta el
  siguiente rebalanceo: el satélite tuvo entre 17 y 19 acciones parte del tiempo.
- El IR de Attribution Analysis (+0.27) y el del motor (+0.21) difieren porque sus precios difieren
  (KaxaNuk en la atribución, Yahoo y KaxaNuk en el motor); para citar, el del motor.

## Corridas relacionadas

- 2019-01-02 a 2026-11-06 (`resultados_nucleo_satelite/`): CAGR 17.2% contra 15.7% del KN Core,
  alfa +1.6%, IR +0.17; estrés de costos IR +0.14.
- 2001-02-01 a 2026-11-06 (`resultados_nucleo_satelite_2000/`): CAGR 9.9% contra 8.4%, alfa +1.4%,
  IR +0.25.

## Cómo reproducirlo

```
.venv/bin/python nucleo_satelite.py <CSV de KaxaNuk> resultados_nucleo_satelite_2000ene 1999-12-31 reconstruir-1999
.venv/bin/python descargar_precios.py resultados_nucleo_satelite_2000ene/tickers_para_curator.csv datos_backtest_2000/precios 2000-01-01
.venv/bin/python preparar_motor.py <CSV de KaxaNuk> resultados_nucleo_satelite_2000ene/weights.csv datos_backtest_2000/precios datos_backtest_2000ene/motor 2000-01-01
KNBE_API_KEY_KAXANUK=<licencia> .venv/bin/python correr_backtest.py datos_backtest_2000ene/motor resultados_nucleo_satelite_2000ene weights resultados_nucleo_satelite_2000ene/backtest_base 2000-01-03 2026-11-06 1.0 5.0
.venv/bin/python preparar_atribucion.py <CSV de KaxaNuk> resultados_nucleo_satelite_2000ene/backtest_base/Daily_Weights.csv datos_atribucion_2000ene
KNAA_API_KEY_KAXANUK=<licencia> .venv/bin/python correr_atribucion.py datos_atribucion_2000ene
```
