"""C2 con refugio confirmado por el modelo de riesgo. Pre-registro (2026-11-14), escrito antes de correr.

Diagnóstico (DIAGNOSTICO_2010_2026.txt): en 2010–2026 los refugios de C2 restan −2.95 puntos/año
(salidas tardías que pierden el rebote); acciones +4.24 y sectores +0.86 suman.

Cambio único: en cada fecha en que C2 pone ≥ 50% en refugios (SHY/IEF/TIP: régimen de caída o
interruptor del principal), se mira la probabilidad del modelo de filtro_riesgo (entrenado 2000–2009)
al cierre del último fin de mes anterior a esa fecha. Si es ≤ umbral (0.222), el modelo NO confirma el
riesgo y esa fecha usa la asignación de ciclicos6 vigente (top 2 sectores cíclicos, o SHY si ninguno
tiene momentum positivo) en lugar del refugio. Si es > umbral, se respeta el refugio del principal.
Nota: las probabilidades de 2007–2009 están dentro de la muestra de entrenamiento del modelo.

Criterio: alfa con estrés 2010–2026 > 0; alfa con estrés 2007–2026 > +2.58% (C1); caída máxima
2007–2026 de −35% o menos. Si no cumple, se adopta C1.

Uso:
    python hackaton_combos/c2_confirmado.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "filtro_riesgo"))
import filtro  # noqa: E402

HERE = ROOT / "hackaton_combos"
REF = ["SHY", "IEF", "TIP"]

idx = pd.read_csv(ROOT / "filtro_riesgo" / "indices_kn.csv", index_col=0, parse_dates=True)
panel = {c: filtro.variables(idx[c]).dropna(subset=filtro.VARS) for c in idx.columns}
train = pd.concat([d.loc[:filtro.FIN_TRAIN] for d in panel.values()]).dropna(subset=["etiqueta"])
mu, sd = train[filtro.VARS].mean(), train[filtro.VARS].std()
b = filtro.logistica(((train[filtro.VARS] - mu) / sd).values, train["etiqueta"].astype(float).values, filtro.L2)
umbral = train["etiqueta"].mean()
kc = panel["KN_Core"]
prob = pd.Series(1 / (1 + np.exp(-(np.c_[np.ones(len(kc)), ((kc[filtro.VARS] - mu) / sd).values] @ b))), index=kc.index)

c2 = pd.read_csv(HERE / "C2_nucleo" / "weights.csv", index_col=0)
cic = pd.read_csv(ROOT / "hackaton_etf" / "ciclicos6_top2" / "weights.csv", index_col=0).T
cic.index = pd.to_datetime(cic.index)
out = c2.copy()
cambios = []
for col in c2.columns:
    d = pd.Timestamp(col)
    if c2[col].reindex(REF).fillna(0).sum() < 0.5:
        continue
    fin_mes = prob.index[prob.index < d.to_period("M").start_time]
    p = prob.loc[fin_mes[-1]] if len(fin_mes) else np.nan
    if pd.notna(p) and p <= umbral:
        nuevo = cic.loc[:d].iloc[-1]
        out[col] = 0.0
        for t, x in nuevo[nuevo > 0].items():
            if t not in out.index:
                out.loc[t] = 0.0
            out.at[t, col] = x
        cambios.append((col, round(float(p), 3), "cíclicos"))
    else:
        cambios.append((col, round(float(p), 3) if pd.notna(p) else None, "refugio"))
out = out.fillna(0.0)
assert abs(out.sum() - 1).max() < 1e-6
dst = HERE / "C2_confirmado"
dst.mkdir(exist_ok=True)
out.index.name = "Ticker"
out.to_csv(dst / "weights.csv", float_format="%.6f")
pd.DataFrame(cambios, columns=["fecha", "prob", "decisión"]).to_csv(dst / "decisiones_refugio.csv", index=False)
print(f"umbral {umbral:.3f}; fechas de refugio: {len(cambios)}; vetadas por el modelo: "
      f"{sum(1 for c in cambios if c[2] == 'cíclicos')}")
for c in cambios:
    if c[0] >= "2007":
        print(" ", c)
