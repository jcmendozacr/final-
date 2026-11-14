"""Diagnóstico de C2 (y del principal) en 2010–2026: de dónde sale y dónde se pierde el alfa.

Exceso diario contra el KN Core = Σ peso_ayer × (rendimiento del activo − rendimiento del KN), por grupo:
acciones, sectores (XL*), SPY, refugios (SHY/IEF/TIP), efectivo; costos = residuo.
Se agrupa por año y por régimen del modelo principal (alcista / mixto / caída / interruptor).

Uso:
    python hackaton_combos/diagnostico.py
"""
import glob
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "paralelo_etf"))
import paralelo as p  # noqa: E402

MOTOR = ROOT / "datos_backtest_combo" / "motor"
PRICE = "m_close_dividend_and_split_adjusted"
SECT = ["XLK", "XLF", "XLE", "XLY", "XLI", "XLB"]
REF = ["SHY", "IEF", "TIP"]
RUNS = {"Principal": ROOT / "hackaton_ideas/referencia_modelo_principal/backtest_base",
        "C2": ROOT / "hackaton_combos/C2_nucleo/backtest_2010_base",
        "C2 estrés": ROOT / "hackaton_combos/C2_nucleo/backtest_2010_estres"}


def px(t):
    d = pd.read_csv(MOTOR / f"{t}.csv", usecols=["m_date", PRICE])
    return pd.Series(d[PRICE].values, index=pd.to_datetime(d.m_date))


reg = pd.read_csv(ROOT / "resultados_regimen_n10_a60/regimenes.csv", parse_dates=["operación"]).set_index("operación")["régimen"]
salidas = []
for nombre, run in RUNS.items():
    t = p.sheet(glob.glob(str(run / "*_backtest_results.xlsx"))[0], "portfolio_bench_total_value", 2)
    t.index = pd.to_datetime(t.index)
    v, k = t["Total_Portfolio_Value"].astype(float), t["KN_US_Equity_Core_Value"].astype(float)
    rp, rk = v.pct_change().fillna(0), k.pct_change().fillna(0)
    w = pd.read_csv(run / "Daily_Weights.csv", index_col=0, parse_dates=True).fillna(0)
    w = w.loc[:, ~w.columns.duplicated()].reindex(v.index).ffill().fillna(0)
    wp = w.shift(1).fillna(0)
    activos = [c for c in w.columns if c not in ("CASH_RESERVE", "KN_US_Equity_Core")]
    R = pd.DataFrame({c: px(c) for c in activos}).reindex(v.index).pct_change(fill_method=None).fillna(0)
    ex = wp[activos].mul(R.sub(rk, axis=0))
    grupos = {"acciones": [c for c in activos if c not in SECT + REF + ["SPY"]], "sectores": SECT,
              "SPY": ["SPY"], "refugios": REF}
    c = pd.DataFrame({g: ex[[x for x in cols if x in ex.columns]].sum(axis=1) for g, cols in grupos.items()})
    c["efectivo"] = wp.get("CASH_RESERVE", 0) * (0 - rk)
    c["costos"] = (rp - rk) - c.sum(axis=1)
    reg_d = reg.reindex(v.index, method="ffill")
    interr = w.reindex(columns=activos).sum(axis=1) < 0.5
    reg_d = reg_d.where(~(interr & (reg_d != "caída")), "interruptor")
    años = len(v) / 252
    por_año = (c.groupby(v.index.year).sum() * 100).round(1)
    por_año["total"] = por_año.sum(axis=1)
    por_reg = (c.groupby(reg_d).sum() / años * 100).round(2)
    por_reg["total"] = por_reg.sum(axis=1)
    por_reg["% del tiempo"] = (reg_d.value_counts(normalize=True) * 100).round(0)
    salidas += [f"\n### {nombre}: exceso aditivo contra el KN, puntos por año de calendario", por_año.to_string(),
                f"\n### {nombre}: por régimen, puntos anualizados (sobre toda la ventana)", por_reg.to_string(),
                f"\n### {nombre}: total por fuente, puntos/año: " +
                ", ".join(f"{g} {x:+.2f}" for g, x in (c.sum() / años * 100).items())]
texto = "\n".join(salidas)
print(texto)
(ROOT / "hackaton_combos" / "DIAGNOSTICO_2010_2026.txt").write_text(texto, encoding="utf-8")
