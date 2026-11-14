"""Paralelo ETF: el modelo principal con refugio y núcleo de ETFs ampliados (P1–P4).

No toca el modelo principal. Lee la corrida del Backtest Engine del modelo principal y separa
el portafolio en dos partes:

- ETFs (SPY, SHY, IEF), con precios del Data Curator (datos_etf/precios);
- "bolsa de acciones" = las 10 acciones + efectivo, cuyo rendimiento diario se despeja de la
  corrida del motor: (rendimiento bruto del día − aporte de los ETFs) / peso de la bolsa.

Después vuelve a simular día a día, cambiando solo la parte en ETFs según PARALELO_ETF.md. Los
costos de las acciones son los que cobró el motor (por ticker y fecha); los de los ETFs se cobran
en bp sobre lo operado. Primero se verifica que la réplica del modelo principal coincida con el motor.

Uso:
    python paralelo_etf/paralelo.py            # escribe paralelo_etf/resultados/
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "resultados_regimen_n10_a60"
RUNS = {"base": ("backtest_base_r2", 6.0), "estres": ("backtest_estres_r2", 15.0)}  # pb por lado
PRICE_DIRS = [ROOT / "datos_etf" / "precios", ROOT / "paralelo_etf" / "precios"]
OUT = ROOT / "paralelo_etf" / "resultados"
START_VALUE = 100_000.0
DESIGN_END = "2019-12-31"

REFUGIO_P1 = ["SHY", "IEF", "TLT", "TIP", "GLD", "LQD", "BWX", "UUP"]
NUCLEO_P2 = ["SPY", "IWM", "EFA", "EEM", "VNQ", "DBC", "GLD", "TLT", "LQD", "HYG", "EMB"]
NUCLEO_P4 = NUCLEO_P2 + ["SLV", "USO", "DBA", "UUP"]
VARIANTES = {
    "Principal (réplica)": dict(refugio=None, nucleo=None),
    "P1 refugio ampliado": dict(refugio=REFUGIO_P1, nucleo=None),
    "P2 núcleo dinámico": dict(refugio=None, nucleo=NUCLEO_P2),
    "P3 = P1 + P2": dict(refugio=REFUGIO_P1, nucleo=NUCLEO_P2),
    "P4 = P3 + SLV/USO/DBA/UUP": dict(refugio=REFUGIO_P1, nucleo=NUCLEO_P4),
}
N_REFUGIO, N_NUCLEO = 3, 4
BASE_ETFS = ["SPY", "SHY", "IEF"]


def load_prices():
    tickers = sorted(set(REFUGIO_P1 + NUCLEO_P4 + BASE_ETFS))
    series = {}
    for t in tickers:
        for d in PRICE_DIRS:
            f = d / f"{t}.csv"
            if f.exists():
                s = pd.read_csv(f, index_col=0, parse_dates=True)["m_close_dividend_and_split_adjusted"]
                series[t] = s.astype(float)
                break
        else:
            raise FileNotFoundError(t)
    return pd.DataFrame(series).sort_index()


def sheet(xlsx, name, header_row):
    x = pd.read_excel(xlsx, sheet_name=name, header=None)
    x.columns = x.iloc[header_row]
    x = x.iloc[header_row + 1:].set_index("date")
    x.index = pd.to_datetime(x.index)
    return x.apply(pd.to_numeric)


def load_run(folder):
    d = MODEL / folder
    xlsx = next(d.glob("*_backtest_results.xlsx"))
    values = sheet(xlsx, "portfolio_bench_total_value", 2)
    costs = sheet(xlsx, "commissions", 2).add(sheet(xlsx, "slippage", 2), fill_value=0).fillna(0)
    weights = pd.read_csv(d / "Daily_Weights.csv", index_col=0, parse_dates=True).fillna(0)
    weights = weights.loc[:, ~weights.columns.duplicated()]
    summary = json.loads((d / "resumen.json").read_text(encoding="utf-8"))
    return values, costs, weights, summary


def momentum_13612(prices, signal_dates):
    """13612 al cierre de cada fecha de señal (fin de mes), solo con 12 meses de historia."""
    monthly = prices.resample("ME").last()
    monthly.index = [prices.index[prices.index <= d][-1] for d in monthly.index]
    rows = {}
    for sd in signal_dates:
        m = monthly.loc[:sd]
        if len(m) < 13:
            continue
        p = m.iloc[-1]
        r = sum(p / m.iloc[-1 - k] - 1 for k in (1, 3, 6, 12)) / 4
        ok = m.iloc[-13:].notna().all()
        rows[sd] = r.where(ok)
    return pd.DataFrame(rows).T


def basket(mom_row, universe, n):
    """Los n mejores con 13612 > el de SHY, peso 1/n cada uno; lo vacío va a SHY."""
    bar = mom_row["SHY"]
    ranked = mom_row[universe].dropna().sort_values(ascending=False)
    picks = [t for t in ranked.index if ranked[t] > bar and t != "SHY"][:n]
    w = {t: 1.0 / n for t in picks}
    if len(picks) < n:
        w["SHY"] = w.get("SHY", 0) + (n - len(picks)) / n
    return w


def decompose(values, costs, weights, prices):
    """Rendimiento diario bruto de la bolsa de acciones y costos de acciones (fracción del valor)."""
    v = values["Total_Portfolio_Value"]
    dates = v.index
    etf_ret = prices[BASE_ETFS].reindex(dates).pct_change()
    cost_total = costs.sum(axis=1).reindex(dates).fillna(0)
    cost_stock = costs.drop(columns=[c for c in BASE_ETFS if c in costs]).sum(axis=1).reindex(dates).fillna(0)
    gross = (v + cost_total) / v.shift(1) - 1
    w = weights.reindex(dates)
    w_etf_prev = w[BASE_ETFS].shift(1)
    w_bag_prev = 1 - w_etf_prev.sum(axis=1)
    contrib = (w_etf_prev * etf_ret).sum(axis=1)
    bag_ret = ((gross - contrib) / w_bag_prev).where(w_bag_prev > 0.025, 0.0).fillna(0)
    stock_cost_frac = cost_stock / (v + cost_total)
    return bag_ret, stock_cost_frac


def targets(weights, trade_dates, regimes, mom, cfg):
    """Pesos objetivo por fecha de operación: los del motor, cambiando solo la parte en ETFs."""
    out = {}
    for td in trade_dates:
        w = weights.loc[td]
        etf = {t: float(w[t]) for t in BASE_ETFS if w[t] > 1e-9}
        bag = 1 - sum(etf.values())
        reg = regimes[regimes["operación"] <= td].iloc[-1]
        sd = reg["señal"]
        stocks_on = bag > 0.05
        if reg["régimen"] == "caida" and cfg["refugio"] and sd in mom.index:
            total = sum(etf.values())
            etf = {t: total * x for t, x in basket(mom.loc[sd], cfg["refugio"], N_REFUGIO).items()}
        elif reg["régimen"] == "mixto" and cfg["nucleo"] and stocks_on and "SPY" in etf and sd in mom.index:
            spy = etf.pop("SPY")
            for t, x in basket(mom.loc[sd], cfg["nucleo"], N_NUCLEO).items():
                etf[t] = etf.get(t, 0) + spy * x
        out[td] = (bag, etf)
    return out


def simulate(dates, bag_ret, stock_cost_frac, prices, tgt, bp):
    rets = prices.reindex(dates).pct_change().fillna(0)
    value = START_VALUE
    hold = {}  # activo -> valor en dólares; "BAG" es la bolsa de acciones + efectivo
    path = []
    for i, d in enumerate(dates):
        if i > 0:
            for a in hold:
                hold[a] *= 1 + (bag_ret[d] if a == "BAG" else rets.at[d, a])
            value = sum(hold.values())
        if d in tgt:
            bag, etf = tgt[d]
            new = {"BAG": bag * value, **{t: x * value for t, x in etf.items()}}
            traded = sum(abs(new.get(a, 0) - hold.get(a, 0)) for a in set(new) | set(hold) if a != "BAG")
            cost = traded * bp / 1e4 + stock_cost_frac[d] * value
            value -= cost
            hold = {a: x * value / sum(new.values()) for a, x in new.items()}
        path.append(value)
    return pd.Series(path, index=dates)


def stats(series, bench, years):
    out = {}
    cagr = (series.iloc[-1] / START_VALUE) ** (1 / years) - 1
    bcagr = (bench.iloc[-1] / START_VALUE) ** (1 / years) - 1
    r = series.pct_change().dropna()
    out["CAGR"] = cagr
    out["Alfa (CAGR − KN Core)"] = cagr - bcagr
    out["Volatilidad"] = r.std() * np.sqrt(252)
    out["Caída máxima"] = (series / series.cummax() - 1).min()
    last_design = series.index[series.index <= DESIGN_END][-1]
    for name, sl in (("2007-03 a 2019", slice(None, last_design)), ("2020 a 2026-11", slice(last_design, None))):
        s, b = series.loc[sl], bench.loc[sl]
        if sl.stop is not None:  # el diseño arranca en los $100,000 iniciales, como el motor
            s = pd.concat([pd.Series([START_VALUE], [s.index[0] - pd.Timedelta(days=1)]), s])
            b = pd.concat([pd.Series([START_VALUE], [b.index[0] - pd.Timedelta(days=1)]), b])
        yrs = (s.index[-1] - s.index[0]).days / 365.25
        out[f"Exceso {name}"] = (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - (b.iloc[-1] / b.iloc[0]) ** (1 / yrs)
        out[f"Caída máx. {name}"] = (s / s.cummax() - 1).min()
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prices = load_prices()
    regimes = pd.read_csv(MODEL / "regimenes.csv", parse_dates=["señal", "operación"])
    mom = momentum_13612(prices, regimes["señal"])
    report, curves, picks = {}, {}, []
    for run, (folder, bp) in RUNS.items():
        values, costs, weights, summary = load_run(folder)
        dates = values.index
        years = summary["años_valuados"]
        bench = values["KN_US_Equity_Core_Value"].astype(float)
        bag_ret, stock_cost = decompose(values, costs, weights, prices)
        trade_dates = [d for d in costs.index if d in dates]
        engine = values["Total_Portfolio_Value"].astype(float)
        report[run] = {"Motor KaxaNuk (oficial)": stats(engine, bench, years)}
        for name, cfg in VARIANTES.items():
            tgt = targets(weights, trade_dates, regimes, mom, cfg)
            s = simulate(dates, bag_ret, stock_cost, prices, tgt, bp)
            report[run][name] = stats(s, bench, years)
            curves[f"{run} · {name}"] = s
            if run == "base" and name == "P4 = P3 + SLV/USO/DBA/UUP":
                for d, (bag, etf) in tgt.items():
                    picks.append({"fecha": d.date(), "bolsa_acciones": round(bag, 4),
                                  **{k: round(v, 4) for k, v in sorted(etf.items())}})
        report[run]["KN US Equity Core"] = stats(bench, bench, years)
        curves[f"{run} · KN US Equity Core"] = bench
    pd.DataFrame(curves).to_csv(OUT / "curvas_diarias.csv", float_format="%.2f")
    pd.DataFrame(picks).to_csv(OUT / "pesos_etf_P4.csv", index=False)
    mom.to_csv(OUT / "momentum_13612.csv", float_format="%.5f")
    (OUT / "resumen.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    for run, rows in report.items():
        df = pd.DataFrame(rows).T
        print(f"\n=== Costos {run} ===")
        print((df * 100).round(2).to_string())
        df.to_csv(OUT / f"tabla_{run}.csv", float_format="%.5f")


if __name__ == "__main__":
    main()
