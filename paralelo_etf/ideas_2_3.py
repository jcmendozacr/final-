"""Ideas 2 y 3 (IDEAS_2_3.md) sobre la réplica del modelo principal.

I2: escala el peso en acciones por min(1, mediana histórica / volatilidad de 126 días) y manda
    lo que quita a SPY. I3: cuando el interruptor apaga las acciones, el refugio es la canasta de
    P1 en vez de SHY. Usa la misma réplica validada de paralelo.py (coincide con el motor).

Costos: los de las acciones que cobró el motor, escalados por el tamaño de la parte en acciones,
más 6 pb (base) o 15 pb (estrés) sobre lo que cambia ese tamaño; los ETFs, en bp sobre lo operado.

Uso:  python paralelo_etf/ideas_2_3.py   ->  paralelo_etf/resultados_ideas_2_3/
"""

import json

import numpy as np
import pandas as pd

import paralelo as p

OUT = p.ROOT / "paralelo_etf" / "resultados_ideas_2_3"
VOL_DIAS = 126
VARIANTES = {
    "Principal (réplica)": dict(p1=False, i2=False, i3=False),
    "P1 refugio ampliado": dict(p1=True, i2=False, i3=False),
    "I2 momentum escalado": dict(p1=False, i2=True, i3=False),
    "I3 interruptor a refugios": dict(p1=False, i2=False, i3=True),
    "P1 + I3": dict(p1=True, i2=False, i3=True),
    "P1 + I2 + I3": dict(p1=True, i2=True, i3=True),
}


def escalas(bag_ret, stock_on, trade_dates):
    """Escala de I2 en cada fecha de operación, solo con datos anteriores a esa fecha."""
    r = bag_ret.where(stock_on)
    vol = r.rolling(VOL_DIAS, min_periods=VOL_DIAS).std() * np.sqrt(252)
    out = {}
    for td in trade_dates:
        hist = vol[vol.index < td].dropna()
        if len(hist) == 0:
            out[td] = 1.0
            continue
        out[td] = float(min(1.0, hist.median() / hist.iloc[-1]))
    return out, vol


def targets(weights, trade_dates, regimes, mom, cfg, escala):
    out = {}
    s_prev = 1.0
    for td in trade_dates:
        w = weights.loc[td]
        etf = {t: float(w[t]) for t in p.BASE_ETFS if w[t] > 1e-9}
        bag = 1 - sum(etf.values())
        reg = regimes[regimes["operación"] <= td].iloc[-1]
        sd = reg["señal"]
        on = bag > 0.05
        cost_scale, extra = 1.0, 0.0
        canasta = p.basket(mom.loc[sd], p.REFUGIO_P1, p.N_REFUGIO) if sd in mom.index else {"SHY": 1.0}
        if reg["régimen"] == "caida":
            if cfg["p1"]:
                total = sum(etf.values())
                etf = {t: total * x for t, x in canasta.items()}
        elif not on:  # interruptor encendido en alcista o mixto
            if cfg["i3"] and "SHY" in etf:
                shy = etf.pop("SHY")
                for t, x in canasta.items():
                    etf[t] = etf.get(t, 0) + shy * x
        if cfg["i2"]:
            if on:
                s = escala[td]
                quitar = bag * (1 - s)
                etf["SPY"] = etf.get("SPY", 0) + quitar
                extra = abs(s - s_prev) * bag
                bag, cost_scale, s_prev = bag - quitar, s, s
            else:
                cost_scale = s_prev  # se vende la parte en acciones que se tenía
                s_prev = 1.0
        out[td] = (bag, etf, cost_scale, extra)
    return out


def simulate(dates, bag_ret, stock_cost_frac, prices, tgt, bp):
    rets = prices.reindex(dates).pct_change().fillna(0)
    value, hold, path = p.START_VALUE, {}, []
    for i, d in enumerate(dates):
        if i > 0:
            for a in hold:
                hold[a] *= 1 + (bag_ret[d] if a == "BAG" else rets.at[d, a])
            value = sum(hold.values())
        if d in tgt:
            bag, etf, cost_scale, extra = tgt[d]
            new = {"BAG": bag * value, **{t: x * value for t, x in etf.items()}}
            traded = sum(abs(new.get(a, 0) - hold.get(a, 0)) for a in set(new) | set(hold) if a != "BAG")
            cost = (traded + extra * value) * bp / 1e4 + stock_cost_frac[d] * cost_scale * value
            value -= cost
            hold = {a: x * value / sum(new.values()) for a, x in new.items()}
        path.append(value)
    return pd.Series(path, index=dates)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    prices = p.load_prices()
    regimes = pd.read_csv(p.MODEL / "regimenes.csv", parse_dates=["señal", "operación"])
    mom = p.momentum_13612(prices, regimes["señal"])
    report, curves = {}, {}
    for run, (folder, bp) in p.RUNS.items():
        values, costs, weights, summary = p.load_run(folder)
        dates = values.index
        bench = values["KN_US_Equity_Core_Value"].astype(float)
        bag_ret, stock_cost = p.decompose(values, costs, weights, prices)
        stock_on = (1 - weights.reindex(dates)[p.BASE_ETFS].sum(axis=1)).shift(1) > 0.05
        trade_dates = [d for d in costs.index if d in dates]
        esc, vol = escalas(bag_ret, stock_on, trade_dates)
        if run == "base":
            pd.DataFrame({"escala_I2": esc}).to_csv(OUT / "escala_I2.csv", float_format="%.4f")
            vol.to_csv(OUT / "vol_126d_acciones.csv", float_format="%.4f")
        report[run] = {"Motor KaxaNuk (oficial)": p.stats(values["Total_Portfolio_Value"].astype(float), bench,
                                                          summary["años_valuados"])}
        for name, cfg in VARIANTES.items():
            tgt = targets(weights, trade_dates, regimes, mom, cfg, esc)
            s = simulate(dates, bag_ret, stock_cost, prices, tgt, bp)
            report[run][name] = p.stats(s, bench, summary["años_valuados"])
            curves[f"{run} · {name}"] = s
        curves[f"{run} · KN US Equity Core"] = bench
        df = pd.DataFrame(report[run]).T
        df.to_csv(OUT / f"tabla_{run}.csv", float_format="%.5f")
        print(f"\n=== Costos {run} ===")
        print((df * 100).round(2).to_string())
    pd.DataFrame(curves).to_csv(OUT / "curvas_diarias.csv", float_format="%.2f")
    (OUT / "resumen.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    e = pd.Series(esc)
    print(f"\nEscala I2: media {e[e < 1].mean():.2f} cuando recorta; recorta en {(e < 1).mean():.0%} de los rebalanceos")


if __name__ == "__main__":
    main()
