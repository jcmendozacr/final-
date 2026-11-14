"""Diagnóstico del alfa: de dónde sale y dónde se pierde, para cualquier corrida del Backtest Engine.

Separa el exceso diario contra el KN US Equity Core en fuentes y lo agrupa por régimen y por año:

- ETFs de bolsa (SPY, IWM, EFA...) contra el KN Core;
- acciones (todo lo que no es ETF ni efectivo) contra el KN Core;
- refugios (SHY, IEF, TLT, GLD, UUP...) contra el KN Core;
- efectivo (la reserva) contra el KN Core;
- costos = el resto (comisiones y slippage).

Usa el valor diario, los pesos diarios y los costos que escribió el motor, más los precios de los
ETFs (datos_etf/precios y paralelo_etf/precios). Funciona con el modelo principal y con las
corridas de P1 u otras variantes.

Uso:
    python paralelo_etf/diagnostico_alfa.py <carpeta de la corrida> [regimenes.csv] [nombre]
    python paralelo_etf/diagnostico_alfa.py resultados_regimen_n10_a60/backtest_base_r2

Escribe paralelo_etf/diagnosticos/<nombre>/ con las tablas en CSV y DIAGNOSTICO.md.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paralelo as p  # noqa: E402

BOLSA = ["SPY", "IWM", "EFA", "EEM", "VNQ"]
REFUGIOS = ["SHY", "IEF", "TLT", "TIP", "GLD", "LQD", "BWX", "UUP", "HYG", "EMB", "DBC", "SLV", "USO", "DBA"]
NO_ACCION = {"CASH_RESERVE", "KN_US_Equity_Core"}


def tabla(t, **kw):
    try:
        return t.to_markdown(**kw)
    except ImportError:  # sin el paquete tabulate
        return "```\n" + t.to_string(**{k: v for k, v in kw.items() if k == "index"}) + "\n```"


def cargar(carpeta):
    xlsx = next(carpeta.glob("*_backtest_results.xlsx"))
    values = p.sheet(xlsx, "portfolio_bench_total_value", 2)
    costs = p.sheet(xlsx, "commissions", 2).add(p.sheet(xlsx, "slippage", 2), fill_value=0).fillna(0)
    weights = pd.read_csv(carpeta / "Daily_Weights.csv", index_col=0, parse_dates=True).fillna(0)
    return values, costs, weights.loc[:, ~weights.columns.duplicated()]


def fuentes(values, costs, weights, prices):
    d = values.index
    v = values["Total_Portfolio_Value"].astype(float)
    rp = v.pct_change().fillna(0)
    rb = values["KN_US_Equity_Core_Value"].astype(float).pct_change().fillna(0)
    w = weights.reindex(d).fillna(0)
    etfs = [c for c in w.columns if c in BOLSA + REFUGIOS]
    acciones = [c for c in w.columns if c not in etfs and c not in NO_ACCION]
    r_etf = prices[etfs].reindex(d).pct_change().fillna(0)
    wp = w.shift(1).fillna(0)
    gross = (v + costs.sum(axis=1).reindex(d).fillna(0)) / v.shift(1) - 1
    w_acc = wp[acciones].sum(axis=1)
    contrib_etf = (wp[etfs] * r_etf).sum(axis=1)
    r_acc = ((gross - contrib_etf) / w_acc).where(w_acc > 0.02, 0).fillna(0)
    bolsa = [c for c in etfs if c in BOLSA]
    refugio = [c for c in etfs if c in REFUGIOS]
    c = pd.DataFrame({
        "ETFs de bolsa": (wp[bolsa] * r_etf[bolsa].sub(rb, axis=0)).sum(axis=1),
        "Acciones": w_acc * (r_acc - rb),
        "Refugios": (wp[refugio] * r_etf[refugio].sub(rb, axis=0)).sum(axis=1),
        "Efectivo": wp.get("CASH_RESERVE", 0) * (0 - rb),
    })
    c["Costos"] = (rp - rb) - c.sum(axis=1)
    return c, r_acc, w_acc, rb, v, values["KN_US_Equity_Core_Value"].astype(float)


def etiquetas(d, regimenes, w_acc, weights):
    if regimenes is None:
        return pd.Series("sin régimen", index=d)
    reg = pd.read_csv(regimenes, parse_dates=["operación"])
    lab = pd.Series(reg["régimen"].values, index=reg["operación"]).reindex(d, method="ffill")
    apagado = (w_acc <= 0.02) & (lab != "caida")
    return lab.where(~apagado, "interruptor")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    carpeta = Path(sys.argv[1]).resolve()
    regimenes = Path(sys.argv[2]) if len(sys.argv) > 2 else p.MODEL / "regimenes.csv"
    nombre = sys.argv[3] if len(sys.argv) > 3 else f"{carpeta.parent.name}__{carpeta.name}"
    out = p.ROOT / "paralelo_etf" / "diagnosticos" / nombre
    out.mkdir(parents=True, exist_ok=True)

    values, costs, weights = cargar(carpeta)
    prices = p.load_prices()
    c, r_acc, w_acc, rb, v, b = fuentes(values, costs, weights, prices)
    d = c.index
    años = len(d) / 252
    lab = etiquetas(d, regimenes if regimenes.exists() else None, w_acc, weights)

    por_fuente = (c.sum() / años * 100).rename("pts por año")
    g = c.sum(axis=1).groupby(lab)
    por_regimen = pd.DataFrame({
        "meses": g.size() / 21,
        "aporte (pts/año)": g.sum() / años * 100,
        "exceso anualizado dentro del régimen": g.mean() * 252 * 100,
    })
    regimen_fuente = c.groupby(lab).sum() / años * 100
    por_año = c.groupby(d.year).sum() * 100
    por_año["Total"] = por_año.sum(axis=1)

    filas = []
    for nombre_p, m in (("2007-03 a 2019", d < "2020"), ("2020 a 2026", d >= "2020")):
        m = m & (w_acc > 0.1)
        x, y = r_acc[m], rb[m]
        filas.append({"periodo": nombre_p, "rend. anual acciones": x.mean() * 252 * 100,
                      "rend. anual KN Core": y.mean() * 252 * 100, "vol. acciones": x.std() * np.sqrt(252) * 100,
                      "beta": np.cov(x, y)[0, 1] / y.var(), "correlación": x.corr(y)})
    acciones = pd.DataFrame(filas).set_index("periodo")

    rebotes = []
    if regimenes.exists():
        reg = pd.read_csv(regimenes, parse_dates=["operación"])
        reg["antes"] = reg["régimen"].shift()
        for _, r in reg[(reg["antes"] == "caida") & (reg["régimen"] != "caida")].iterrows():
            a = r["operación"]
            if a < d[0]:
                continue
            e = a + pd.DateOffset(months=3)
            rebotes.append({"salida de caída": a.date(), "a régimen": r["régimen"],
                            "KN Core 3m": (b[a:e].iloc[-1] / b[a:e].iloc[0] - 1) * 100,
                            "portafolio 3m": (v[a:e].iloc[-1] / v[a:e].iloc[0] - 1) * 100})
    rebotes = pd.DataFrame(rebotes)

    for nombre_t, t in (("por_fuente", por_fuente), ("por_regimen", por_regimen),
                        ("regimen_por_fuente", regimen_fuente), ("por_año", por_año),
                        ("acciones", acciones), ("rebotes", rebotes)):
        t.to_csv(out / f"{nombre_t}.csv", float_format="%.3f")

    md = [f"# Diagnóstico del alfa: `{carpeta.relative_to(p.ROOT) if carpeta.is_relative_to(p.ROOT) else carpeta}`",
          "", "Exceso aritmético diario contra el KN US Equity Core, sumado y anualizado (pts por año).",
          f"Suma de fuentes: **{c.sum().sum() / años * 100:+.2f} pts/año**.", "",
          "## Por fuente", "", tabla(por_fuente.round(2)), "",
          "## Por régimen", "", tabla(por_regimen.round(2)), "",
          "## Por régimen y fuente", "", tabla(regimen_fuente.round(2)), "",
          "## Las acciones contra el KN Core (días con acciones)", "", tabla(acciones.round(2)), "",
          "## Rebotes: 3 meses después de salir de caída", "",
          tabla(rebotes.round(1), index=False) if len(rebotes) else "Sin datos de régimen.", "",
          "## Por año (pts)", "", tabla(por_año.round(1)), ""]
    (out / "DIAGNOSTICO.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md[:14]))
    print(f"\nCompleto en {out}")


if __name__ == "__main__":
    main()
