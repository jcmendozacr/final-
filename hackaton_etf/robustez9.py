"""Prueba de robustez de sector_core4_top2: la misma regla con los 9 sectores originales de SPDR.

Regla: cada fin de mes, los 2 ETF sectoriales con mayor momentum de 252 días (si es > 0), 50% cada uno;
si ninguno tiene momentum positivo, SHY. Se opera el primer día hábil siguiente.
Universo: XLK, XLF, XLE, XLY, XLV, XLP, XLI, XLU, XLB (todos existen desde 1998-12).
Pasa si su alfa con estrés supera al del modelo principal del hackathon en 2007–2026 (+2.23%).

Uso:
    python hackaton_etf/robustez9.py
"""

import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "hackaton_etf" / "sector_all9_top2"
MOTOR = ROOT / "datos_backtest_etf" / "motor"
ETF_DIRS = [ROOT / "datos_etf_hackaton" / "precios", ROOT / "datos_etf" / "precios"]
PRICE = "m_close_dividend_and_split_adjusted"
SECT = ["XLK", "XLF", "XLE", "XLY", "XLV", "XLP", "XLI", "XLU", "XLB"]
SAFE = "SHY"


def etf_file(t):
    return next(d / f"{t}.csv" for d in ETF_DIRS if (d / f"{t}.csv").exists())


E = {}
for t in SECT + [SAFE]:
    p = pd.read_csv(etf_file(t), usecols=["m_date", PRICE])
    E[t] = pd.Series(p[PRICE].values, index=pd.to_datetime(p.m_date))
    shutil.copyfile(etf_file(t), MOTOR / f"{t}.csv")
E = pd.DataFrame(E)
dias = pd.DatetimeIndex(pd.to_datetime(pd.read_csv(MOTOR / "KN_US_Equity_Core.csv", usecols=["m_date"]).m_date))
dias = dias[dias >= "2001-01-01"]
E = E.reindex(E.index.union(dias)).ffill(limit=5)
m252 = (E / E.shift(252) - 1).reindex(dias)
E = E.reindex(dias)
g = pd.Series(dias, index=dias).groupby(dias.to_period("M"))
fin, ini = list(g.max()), list(g.first())

cols = {}
for señal, opera in zip(fin[:-1], ini[1:]):
    m = m252.loc[señal, SECT].dropna().sort_values(ascending=False)
    top = [t for t, x in m.iloc[:2].items() if x > 0]
    w = {t: 1 / len(top) for t in top} if top else {SAFE: 1.0}
    if SAFE in w and pd.isna(E.at[opera, SAFE]):
        w = {}
    cols[opera.strftime("%Y-%m-%d")] = w
df = pd.DataFrame(cols).fillna(0.0)
df.index.name = "Ticker"
HERE.mkdir(parents=True, exist_ok=True)
df.to_csv(HERE / "weights.csv", float_format="%.6f")
print(f"{df.shape[1]} rebalanceos, {df.columns[0]} a {df.columns[-1]}; meses en SHY: {int((df.loc[SAFE] > 0.5).sum())}")
print("meses con peso por ETF:", (df > 0).sum(axis=1).sort_values(ascending=False).to_dict())
