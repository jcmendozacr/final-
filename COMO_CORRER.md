# Cómo correr el backtest del modelo principal

Equipo **Los LITpsteins** · Talavera Valley Hackathon 2026 · Track 04 WealthTech.
Modelo: **v3, "Momentum concentrado"**. Las reglas completas y las pruebas contra el sobreajuste
están en [`modelo_principal_v3/MODELO_PRINCIPAL.md`](modelo_principal_v3/MODELO_PRINCIPAL.md).

## Resultado esperado (Backtest Engine 0.68.0, del 2007-03-01 al 2026-11-06)

| | Costos base (1 + 5 pb) | Costos de estrés (5 + 10 pb) | KN US Equity Core |
| --- | --- | --- | --- |
| CAGR | **17.82%** | 16.62% | 10.45% |
| Alfa vs KN Core (CAGR − CAGR del KN) | **+7.37%** | +6.17% | — |
| Sharpe | 0.68 | 0.63 | 0.52 |
| Caída máxima | −34.0% | −35.1% | −52.7% |
| Peso máximo por acción | 20% | 20% | — |

---

## Opción A: correr el backtest directo (5 minutos)

El repo trae todo lo que el motor necesita:
- **`modelo_principal_v3/weights.csv`:** pesos del modelo en el formato horizontal del Backtest
  Engine.
- **`motor/precios/`:** un CSV por ticker, más el benchmark `KN_US_Equity_Core.csv`.
  - Las acciones vienen de los datos de KaxaNuk y los ETF del Data Curator.
  - Los precios están divididos entre 100, lo que no cambia ningún rendimiento. Así, con 20% en una
    acción, el redondeo a acciones enteras no deja el efectivo en negativo.

```bash
# 1. Entorno (Python 3.12+) con el Backtest Engine de KaxaNuk
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt        # Mac/Linux: .venv/bin/pip

# 2. Licencia del Backtest Engine
$env:KNBE_API_KEY_KAXANUK = "<LICENCIA>"             # PowerShell
# export KNBE_API_KEY_KAXANUK=<LICENCIA>             # Mac/Linux

# 3. Backtest con costos base y con costos de estrés
.venv\Scripts\python correr_backtest.py motor/precios modelo_principal_v3 weights salida/base   2007-03-01 2026-11-06 1.0 5.0 0.02
.venv\Scripts\python correr_backtest.py motor/precios modelo_principal_v3 weights salida/estres 2007-03-01 2026-11-06 5.0 10.0 0.02
```

**Argumentos:** carpeta de precios, carpeta del weights, nombre del weights, salida, inicio, fin,
comisión en pb, slippage en pb y reserva de efectivo.

**Configuración:** $100,000 iniciales, 2% de reserva, costos en puntos base, ejecución al cierre
ajustado y venta de las acciones que dejan de cotizar a su último precio. Benchmarks: KN US Equity
Core y SPY.

**Prueba fuera de muestra del modelo de riesgo:** la misma corrida con inicio `2010-01-04` da +5.97%
de alfa (+4.78% con costos de estrés).

**Atribución:** `modelo_principal_v3/ATRIBUCION.md` (Attribution Analysis de KaxaNuk).

---

## Opción B: regenerar todo desde los datos de KaxaNuk

Requiere los CSV de KaxaNuk, que no van en el repo:
- `KN/`: los de `KN_US_Equity_Core.zip` y `KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv`;
- `KN_sectores/`: los archivos de factores de `KN_US_Equity_Factor_Model.zip`.

Los pasos están en
[`modelo_principal_v3/MODELO_PRINCIPAL.md`](modelo_principal_v3/MODELO_PRINCIPAL.md), sección 6.

**Comprobación:** el `weights.csv` regenerado debe dar el md5 de `modelo_principal_v3/MODELO_PRINCIPAL.md5`
(`93df96d7497fea54bbb9ffaa3188c952`).

---

## Dónde está cada cosa

| Carpeta o archivo | Qué es |
| --- | --- |
| `modelo_principal_v3/` | **El modelo principal:** reglas, pruebas contra el sobreajuste, resultados, atribución, pesos y md5 |
| `motor/precios/` | Precios listos para el Backtest Engine (opción A) |
| `pitch/` | Pitch (`PITCH.md`: guion de 5 minutos y fuentes de cada cifra) y presentación |
| `modelo_principal_c2/`, `MODELO_ACTUAL.md` | Versiones previas (v2 y v1) |
| `hackaton_combos/` | Scripts del modelo (combinación, variantes, sensibilidad) y sus resultados |
| `filtro_riesgo/`, `hackaton_etf/`, `hackaton_ideas/`, `paralelo_etf/` | Modelo de riesgo, núcleo de sectores y pruebas descartadas: la evidencia contra el sobreajuste |
