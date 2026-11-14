"""Variante pre-registrada (2026-11-14): el modelo principal v2 con 3 acciones (20% c/u en alcista).

Única diferencia con C2 confirmada: el componente de acciones se genera con modelo_regimen.py usando
3 acciones en vez de 10 (alcista: 60% / 3 = 20% por acción, el tope del reto; mixto: 30% / 3 = 10%).
El núcleo de 6 sectores cíclicos, el freno de emergencia, el interruptor y la confirmación del modelo de
riesgo son idénticos (mismo código que hackaton_combos/preparar.py y c2_confirmado.py).

Criterio (fijado antes de correr): alfa con estrés 2007–2026 > +3.33%; alfa con estrés 2010–2026 >
+1.06%; caída máxima 2007–2026 de −40% o menos; ninguna acción > 20%. Si no cumple todo, se queda C2.

Uso (después de: modelo_regimen.py KN datos_etf/precios resultados_regimen_n3_a60 0.35 3 0.60):
    python hackaton_combos/variante_20pct.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "filtro_riesgo"))
import filtro  # noqa: E402

OUT = ROOT / "hackaton_combos" / "C2_20pct"
REF = ["SHY", "IEF", "TIP"]
ETF = {"SPY", "SHY", "IEF", "TIP", "XLK", "XLF", "XLE", "XLY", "XLI", "XLB"}

main = pd.read_csv(ROOT / "resultados_regimen_n3_a60" / "weights.csv", index_col=0)
cic = pd.read_csv(ROOT / "hackaton_etf" / "ciclicos6_top2" / "weights.csv", index_col=0)
fechas = main.columns
cic_t = cic.T
cic_t.index = pd.to_datetime(cic_t.index)
cic_en = cic_t.reindex(pd.to_datetime(fechas), method="ffill").fillna(0)
cic_en.index = fechas
tickers = sorted(set(main.index) | set(cic.index))
M = main.reindex(tickers).fillna(0)
C = cic_en.T.reindex(tickers).fillna(0)
c2 = M.drop(index="SPY").reindex(tickers).fillna(0) + C.mul(M.loc["SPY"], axis=1)

idx = pd.read_csv(ROOT / "filtro_riesgo" / "indices_kn.csv", index_col=0, parse_dates=True)
panel = {c: filtro.variables(idx[c]).dropna(subset=filtro.VARS) for c in idx.columns}
train = pd.concat([d.loc[:filtro.FIN_TRAIN] for d in panel.values()]).dropna(subset=["etiqueta"])
mu, sd = train[filtro.VARS].mean(), train[filtro.VARS].std()
b = filtro.logistica(((train[filtro.VARS] - mu) / sd).values, train["etiqueta"].astype(float).values, filtro.L2)
umbral = train["etiqueta"].mean()
kc = panel["KN_Core"]
prob = pd.Series(1 / (1 + np.exp(-(np.c_[np.ones(len(kc)), ((kc[filtro.VARS] - mu) / sd).values] @ b))), index=kc.index)

out = c2.copy()
vetos = 0
for col in c2.columns:
    d = pd.Timestamp(col)
    if c2[col].reindex(REF).fillna(0).sum() < 0.5:
        continue
    fm = prob.index[prob.index < d.to_period("M").start_time]
    p = prob.loc[fm[-1]] if len(fm) else np.nan
    if pd.notna(p) and p <= umbral:
        nuevo = cic_t.loc[:d].iloc[-1]
        out[col] = 0.0
        for t, x in nuevo[nuevo > 0].items():
            out.at[t, col] = x
        vetos += 1
out = out.fillna(0.0)
out = out.loc[(out > 0).any(axis=1)]
assert abs(out.sum() - 1).max() < 1e-6
acc = out.loc[[t for t in out.index if t not in ETF]]
assert acc.values.max() <= 0.20 + 1e-9, acc.values.max()
OUT.mkdir(parents=True, exist_ok=True)
out.index.name = "Ticker"
out.to_csv(OUT / "weights.csv", float_format="%.6f")
print(f"{out.shape}, vetos {vetos}, acción máx {acc.values.max():.3f}")
