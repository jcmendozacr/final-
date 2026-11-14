"""Dos filtros a priori para la rotación sectorial (top 2 por momentum de 252 días, 50% c/u; si ninguno > 0, SHY).

Pre-registro (2026-11-14), las DOS deben pasar: alfa con estrés 2007–2026 > +2.23% (modelo principal).
    ciclicos6_top2  Universo fijo: los 6 SPDR no defensivos según la clasificación de Morningstar
                    (defensivos = consumo básico XLP, salud XLV, servicios públicos XLU):
                    XLK, XLF, XLE, XLY, XLI, XLB.
    beta4_top2      Universo dinámico: cada fin de mes, los 4 de los 9 SPDR con mayor beta contra el KN
                    US Equity Core, con rendimientos diarios de los últimos 756 días (3 años; mínimo 252
                    al inicio de la serie).
Señal al cierre de fin de mes, operación el primer día hábil siguiente.

Uso:
    python hackaton_etf/filtros_ciclicos.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "hackaton_etf"
MOTOR = ROOT / "datos_backtest_etf" / "motor"
PRICE = "m_close_dividend_and_split_adjusted"
SECT9 = ["XLK", "XLF", "XLE", "XLY", "XLV", "XLP", "XLI", "XLU", "XLB"]
CICLICOS6 = ["XLK", "XLF", "XLE", "XLY", "XLI", "XLB"]
SAFE = "SHY"


def leer(t):
    p = pd.read_csv(MOTOR / f"{t}.csv", usecols=["m_date", PRICE])
    return pd.Series(p[PRICE].values, index=pd.to_datetime(p.m_date))


kn = leer("KN_US_Equity_Core")
dias = kn.index[kn.index >= "2001-01-01"]
E = pd.DataFrame({t: leer(t) for t in SECT9 + [SAFE]})
E = E.reindex(E.index.union(kn.index)).ffill(limit=5)
m252 = (E / E.shift(252) - 1).reindex(dias)
r = E.reindex(kn.index).pct_change(fill_method=None)
rm = kn.pct_change()
cov = r[SECT9].rolling(756, min_periods=252).cov(rm)
beta = cov.div(rm.rolling(756, min_periods=252).var(), axis=0).reindex(dias)
E = E.reindex(dias)
g = pd.Series(dias, index=dias).groupby(dias.to_period("M"))
pares = list(zip(list(g.max())[:-1], list(g.first())[1:]))


def rotar(universo, señal):
    m = m252.loc[señal, universo].dropna().sort_values(ascending=False)
    top = [t for t, x in m.iloc[:2].items() if x > 0]
    return {t: 1 / len(top) for t in top} if top else {SAFE: 1.0}


VARIANTES = {
    "ciclicos6_top2": lambda s: CICLICOS6,
    "beta4_top2": lambda s: list(beta.loc[s, SECT9].dropna().sort_values(ascending=False).index[:4]),
}
for nombre, universo in VARIANTES.items():
    cols, elegidos = {}, {}
    for señal, opera in pares:
        u = universo(señal)
        if len(u) < 2:
            continue
        for t in u:
            elegidos[t] = elegidos.get(t, 0) + 1
        w = rotar(u, señal)
        if SAFE in w and pd.isna(E.at[opera, SAFE]):
            w = {}
        cols[opera.strftime("%Y-%m-%d")] = w
    df = pd.DataFrame(cols).fillna(0.0)
    df.index.name = "Ticker"
    out = HERE / nombre
    out.mkdir(exist_ok=True)
    df.to_csv(out / "weights.csv", float_format="%.6f")
    print(f"{nombre}: {df.shape[1]} rebalanceos, {df.columns[0]} a {df.columns[-1]}; meses en SHY "
          f"{int((df.loc[SAFE] > 0.5).sum()) if SAFE in df.index else 0}")
    if nombre == "beta4_top2":
        print("  meses en que cada sector estuvo entre los 4 de mayor beta:",
              dict(sorted(elegidos.items(), key=lambda x: -x[1])))
