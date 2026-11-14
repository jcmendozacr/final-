"""Combinaciones del modelo principal (acciones) con la rotación de 6 sectores cíclicos (ETF). Pre-registro.

Componentes (sin cambios):
    principal   resultados_regimen_n10_a60/weights.csv (congelado; incluye fechas extra del interruptor)
    ciclicos6   hackaton_etf/ciclicos6_top2/weights.csv (top 2 por momentum de 252 días entre XLK, XLF, XLE,
                XLY, XLI, XLB; si ninguno > 0, SHY)

Combinaciones (fijadas antes de correr, sin optimizar pesos):
    C1_mitad      50% principal + 50% ciclicos6, en cada fecha de rebalanceo del principal.
    C2_nucleo     El principal, pero el peso que asigna a SPY (su núcleo de mercado) se reparte según
                  ciclicos6. Acciones, refugios e interruptor del principal no cambian.
En las fechas del principal se usa la última asignación de ciclicos6 vigente.

Criterio (todas): acciones ≤ 20%; alfa con estrés 2007–2026 > +2.23% (principal); alfa con estrés
2010–2026 > −0.65% (principal en esa ventana); caída máxima 2007–2026 de −35% o menos.
Si las dos cumplen, gana la de mayor alfa con estrés en 2007–2026. Si ninguna, se queda el principal.

Uso:
    python hackaton_combos/preparar.py
"""

import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "hackaton_combos"
MOTOR = ROOT / "datos_backtest_combo" / "motor"

main = pd.read_csv(ROOT / "resultados_regimen_n10_a60" / "weights.csv", index_col=0)
cic = pd.read_csv(ROOT / "hackaton_etf" / "ciclicos6_top2" / "weights.csv", index_col=0)
fechas = main.columns
cic_t = cic.T
cic_t.index = pd.to_datetime(cic_t.index)
cic_en = cic_t.reindex(pd.to_datetime(fechas), method="ffill").fillna(0)
cic_en.index = fechas
cic_en = cic_en.T
tickers = sorted(set(main.index) | set(cic.index))
M = main.reindex(tickers).fillna(0)
C = cic_en.reindex(tickers).fillna(0)

combos = {
    "C1_mitad": 0.5 * M + 0.5 * C,
    "C2_nucleo": M.drop(index="SPY").reindex(tickers).fillna(0) + C.mul(M.loc["SPY"], axis=1),
}
ETF = {"SPY", "SHY", "IEF", "TIP", "XLK", "XLF", "XLE", "XLY", "XLI", "XLB"}
for nombre, w in combos.items():
    w = w.loc[(w > 0).any(axis=1)]
    assert abs(w.sum() - 1).max() < 1e-6, nombre
    acciones = w.loc[[t for t in w.index if t not in ETF]]
    assert acciones.values.max() <= 0.20 + 1e-9
    out = HERE / nombre
    out.mkdir(parents=True, exist_ok=True)
    w.index.name = "Ticker"
    w.to_csv(out / "weights.csv", float_format="%.6f")
    print(f"{nombre}: {w.shape[1]} fechas; acción máx {acciones.values.max():.3f}; "
          f"peso medio en sectores {w.reindex(['XLK','XLF','XLE','XLY','XLI','XLB']).fillna(0).sum().mean():.2f}; "
          f"ETF máx {w.loc[[t for t in w.index if t in ETF]].max(axis=1).round(2).to_dict()}")

MOTOR.mkdir(parents=True, exist_ok=True)
for f in (ROOT / "datos_backtest_p1" / "motor").glob("*.csv"):
    shutil.copyfile(f, MOTOR / f.name)
for t in ["XLK", "XLF", "XLE", "XLY", "XLI", "XLB"]:
    shutil.copyfile(ROOT / "datos_backtest_etf" / "motor" / f"{t}.csv", MOTOR / f"{t}.csv")
