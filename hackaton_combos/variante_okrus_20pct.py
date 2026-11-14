"""Versión agresiva candidata: C2 con 3 acciones al 20%, elegidas con la regla de las estrategias top de OKRUS.

Pre-registro (2026-11-14): se compara contra C2_20pct (3 acciones al 20% por momentum 12-1). La versión
agresiva será la de mayor alfa con estrés 2007–2026, si su caída máxima no pasa de −55% y su alfa con
estrés 2010–2026 es positivo.

Regla de selección (la "Agresiva" de OKRUS, aplicada sin sesgo):
- Universo: las 300 acciones de mayor peso del KN US Equity Core al cierre de fin de mes.
- Elegibles: precio > EMA de 200 días, precio >= 85% del máximo de 63 días y momentum de 126 días > 0.
- Se toman las 3 de mayor momentum de 126 días. Si hay menos de 3, ese peso va a SHY.
Todo lo demás (pesos por régimen, núcleo cíclico, freno de emergencia, interruptor y confirmación del
modelo de riesgo) se toma tal cual de C2_20pct: solo se cambian los nombres de las acciones.
Precios: índices de rendimiento total con datos de KaxaNuk, escalados para empezar en 1.

Uso:
    python hackaton_combos/variante_okrus_20pct.py <carpeta KN>
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from preparar_motor import index_frame, read_dated  # noqa: E402

BASE = ROOT / "hackaton_combos" / "C2_20pct" / "weights.csv"
OUT = ROOT / "hackaton_combos" / "C2_okrus_20pct"
MOTOR = ROOT / "datos_backtest_combo_x01" / "motor"
ETF = {"SPY", "SHY", "IEF", "TIP", "XLK", "XLF", "XLE", "XLY", "XLI", "XLB"}


def main(kn, variantes):
    core = read_dated(kn / "KN_US_Equity_Core_Returns_Daily.csv")["return"]
    holdings = read_dated(kn / "KN_US_Equity_Core_Holdings_Daily.csv")
    excess = read_dated(kn / "KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv")
    dates = excess.index.intersection(core.index).intersection(holdings.index)
    holdings = holdings.loc[dates]
    shared = excess.columns.intersection(holdings.columns)
    implied = core.loc[dates] - (holdings[shared].shift(1) * excess.loc[dates, shared].fillna(0)).sum(axis=1)
    bill = implied.rolling(21, min_periods=1).median()
    r = excess.loc[dates, shared].add(bill, axis=0)
    valid = r.notna()
    alive = valid.cummax() & valid[::-1].cummax()[::-1]
    P = (1 + r.fillna(0)).cumprod().where(alive)
    ema = P.ewm(span=200, adjust=False, ignore_na=True).mean().where(alive)
    peak = P.rolling(63, min_periods=1).max()
    for nombre, N, LB, STOP in variantes:
        construir(nombre, N, LB, STOP, P, ema, peak, holdings, alive, dates, r)


def construir(nombre, N, LB, STOP, P, ema, peak, holdings, alive, dates, r):
    out_dir = ROOT / "hackaton_combos" / nombre
    m126 = P / P.shift(LB) - 1

    base = pd.read_csv(BASE, index_col=0)
    stocks_rows = [t for t in base.index if t not in ETF]
    out = base.drop(index=stocks_rows)
    picks_log, nuevos = [], set()
    month_end = pd.Series(dates, index=dates).groupby(dates.to_period("M")).max()
    for col in base.columns:
        d = pd.Timestamp(col)
        w_acc = base.loc[stocks_rows, col]
        sleeve = float(w_acc.sum())
        if sleeve <= 1e-9:
            continue
        per = d.to_period("M") - 1 if d.day <= 7 else d.to_period("M") - 1
        s = month_end.get(per)
        if s is None:
            continue
        hs = holdings.loc[s]
        univ = hs[(hs > 0) & alive.loc[s].reindex(hs.index).fillna(False)].sort_values(ascending=False).index[:300]
        univ = [t for t in univ if t in P.columns]
        p = P.loc[s, univ]
        ok = (p > ema.loc[s, univ]) & (p >= peak.loc[s, univ] * (1 - STOP)) & (m126.loc[s, univ] > 0)
        top = list(m126.loc[s, univ][ok].dropna().sort_values(ascending=False).index[:N])
        cada = sleeve / N
        for t in top:
            if t not in out.index:
                out.loc[t] = 0.0
            out.at[t, col] = cada
            nuevos.add(t)
        falta = sleeve - cada * len(top)
        if falta > 1e-9:
            out.at["SHY", col] = out.at["SHY", col] + falta
        picks_log.append((col, round(sleeve, 3), " ".join(top)))
    out = out.fillna(0.0)
    out = out.loc[(out > 0).any(axis=1)]
    assert abs(out.sum() - 1).max() < 1e-6
    acc = out.loc[[t for t in out.index if t not in ETF]]
    assert acc.values.max() <= 0.20 + 1e-9
    out_dir.mkdir(parents=True, exist_ok=True)
    out.index.name = "Ticker"
    out.to_csv(out_dir / "weights.csv", float_format="%.6f")
    pd.DataFrame(picks_log, columns=["fecha", "peso_acciones", "acciones"]).to_csv(out_dir / "acciones_por_fecha.csv", index=False)

    for t in sorted(nuevos):
        if (MOTOR / f"{t}.csv").exists():
            continue
        frame = index_frame(r[t].where(alive[t]).dropna())
        cols = [c for c in frame.columns if c not in ("m_date", "m_volume_split_adjusted")]
        frame[cols] = frame[cols] / 100
        frame.to_csv(MOTOR / f"{t}.csv", index=False, float_format="%.8f")
    cuenta = pd.Series([t for _, _, x in picks_log for t in x.split()]).value_counts()
    print(f"{nombre}: {out.shape}; acción máx {acc.values.max():.3f}; más elegidas: {cuenta.head(10).to_dict()}")


if __name__ == "__main__":
    BASE_VAR = [("C2_okrus_20pct", 3, 126, 0.15)]
    SENS = [("sens_N4", 4, 126, 0.15), ("sens_N5", 5, 126, 0.15), ("sens_LB63", 3, 63, 0.15),
            ("sens_LB189", 3, 189, 0.15), ("sens_LB252", 3, 252, 0.15), ("sens_stop10", 3, 126, 0.10),
            ("sens_stop20", 3, 126, 0.20)]
    main(Path(sys.argv[1]), SENS if "--sensibilidad" in sys.argv else BASE_VAR)
