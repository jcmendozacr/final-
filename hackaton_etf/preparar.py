"""Las mejores estrategias de ETF de OKRUS, con sus reglas originales, para el Backtest Engine del hackathon.

Reglas tomadas de backtest_final (solo lectura): run_block_a_sectors2.py, run_block_b_post_covid.py,
run_block_c_thematic.py, run_block_d_trend_sectors.py, run_batch_mix.py, run_batch_extra.py,
generate_momentum_weights.py, generate_trend_weights.py y PROTOCOLO_ESTRATEGIAS_REALES.txt.
Precios: Data Curator (datos_etf/precios, datos_etf_hackaton/precios). Benchmark: KN US Equity Core.
Calendario: señal al cierre de fin de mes, operación el primer día hábil siguiente; las estáticas se
rebalancean cada mes a sus pesos fijos.

Estrella / top1_momentum_rotation: la regla del protocolo (top 1 por momentum de 252 días entre los 13
ETF de generate_live_signals.py, con filtro de SMA200; si no hay, SHY). En OKRUS se corrió desde un
archivo de pesos guardado (portfolio_weights_BACKUP.csv); aquí se reconstruye con esa regla.

Uso:
    python hackaton_etf/preparar.py
"""

import shutil
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "hackaton_etf"
MOTOR = ROOT / "datos_backtest_etf" / "motor"
ETF_DIRS = [ROOT / "datos_etf_hackaton" / "precios", ROOT / "datos_etf" / "precios"]
PRICE = "m_close_dividend_and_split_adjusted"
SAFE = "SHY"
ESTRELLA = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "GLD", "VNQ", "DBC", "XLK", "XLE", "XLF", "SMH"]
ESTATICAS = {
    "sector_tech": {"XLK": 0.5, "SMH": 0.5},
    "tech_growth": {"QQQ": 0.5, "SMH": 0.3, "SPY": 0.2},
    "buy_hold_qqq": {"QQQ": 1.0},
    "millennial_growth": {"QQQ": 0.6, "SMH": 0.2, "GLD": 0.1, "SHY": 0.1},
}
INICIO = "2001-01-01"


def etf_file(t):
    return next(d / f"{t}.csv" for d in ETF_DIRS if (d / f"{t}.csv").exists())


todos = sorted(set(ESTRELLA + ["XLY", SAFE] + [t for w in ESTATICAS.values() for t in w]))
E = {}
for t in todos:
    p = pd.read_csv(etf_file(t), usecols=["m_date", PRICE])
    E[t] = pd.Series(p[PRICE].values, index=pd.to_datetime(p.m_date))
E = pd.DataFrame(E)
kn = pd.read_csv(ROOT / "datos_backtest_hack" / "motor" / "KN_US_Equity_Core.csv", usecols=["m_date"])
dias = pd.to_datetime(kn.m_date)
dias = pd.DatetimeIndex(dias[dias >= INICIO])
E = E.reindex(E.index.union(dias)).ffill(limit=5)
m252 = E / E.shift(252) - 1  # 252 sesiones del propio ETF
sma = E.rolling(200).mean()
E, m252, sma = E.reindex(dias), m252.reindex(dias), sma.reindex(dias)
g = pd.Series(dias, index=dias).groupby(dias.to_period("M"))
fin, ini = list(g.max()), list(g.first())
pares = list(zip(fin[:-1], ini[1:]))


def top_n(universo, n):
    def regla(d):
        m = m252.loc[d, universo].dropna().sort_values(ascending=False)
        top = [t for t, x in m.iloc[:n].items() if x > 0]
        return {t: 1 / len(top) for t in top} if top else {SAFE: 1.0}
    return regla


def estrella(d):
    ok = [t for t in ESTRELLA if pd.notna(m252.at[d, t]) and m252.at[d, t] > 0 and E.at[d, t] > sma.at[d, t]]
    return {max(ok, key=lambda t: m252.at[d, t]): 1.0} if ok else {SAFE: 1.0}


def sma_filtro(t):
    return lambda d: {t: 1.0} if pd.notna(sma.at[d, t]) and E.at[d, t] > sma.at[d, t] else {SAFE: 1.0}


DINAMICAS = {
    "estrella_top1_momentum": estrella,
    "sector_core4_top2": top_n(["XLK", "XLF", "XLE", "XLY"], 2),
    "sector_rotation_top1": top_n(["XLK", "XLF", "XLE"], 1),
    "sector_rotation_top2": top_n(["XLK", "XLF", "XLE"], 2),
    "xlk_above_sma200": sma_filtro("XLK"),
}

MOTOR.mkdir(parents=True, exist_ok=True)
shutil.copyfile(ROOT / "datos_backtest_hack" / "motor" / "KN_US_Equity_Core.csv", MOTOR / "KN_US_Equity_Core.csv")
for t in todos:
    shutil.copyfile(etf_file(t), MOTOR / f"{t}.csv")

for nombre in list(ESTATICAS) + list(DINAMICAS):
    cols = {}
    for señal, opera in pares:
        if nombre in ESTATICAS:
            w = dict(ESTATICAS[nombre])
            if any(pd.isna(E.at[opera, t]) for t in w):
                continue  # algún ETF aún no existe
        else:
            if SAFE not in E.columns or pd.isna(E.at[opera, SAFE]):
                if m252.loc[señal].notna().sum() == 0:
                    continue
            w = DINAMICAS[nombre](señal)
            if SAFE in w and pd.isna(E.at[opera, SAFE]):
                w = {}  # SHY aún no existe: efectivo
        cols[opera.strftime("%Y-%m-%d")] = w
    df = pd.DataFrame(cols).fillna(0.0)
    df.index.name = "Ticker"
    out = HERE / nombre
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "weights.csv", float_format="%.6f")
    print(f"{nombre}: {df.shape[1]} rebalanceos, {df.columns[0]} a {df.columns[-1]}; peso máximo {df.values.max():.2f}")
