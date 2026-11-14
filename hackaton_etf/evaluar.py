"""Resume las corridas del motor de las estrategias de ETF de OKRUS (3 ventanas × 2 costos)."""
import glob
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "hackaton_etf"
sys.path.insert(0, str(ROOT / "paralelo_etf"))
import paralelo as p  # noqa: E402


def r(d):
    return json.loads((d / "resumen.json").read_text(encoding="utf-8"))


rows = []
for d in sorted(x for x in HERE.iterdir() if (x / "weights.csv").exists()):
    row = {"estrategia": d.name, "peso_máx": pd.read_csv(d / "weights.csv", index_col=0).values.max()}
    for w in ["completo", "2007", "2010"]:
        b, e = r(d / f"backtest_{w}_base"), r(d / f"backtest_{w}_estres")["portafolio"]
        bp = b["portafolio"]
        row[f"alfa_{w}"], row[f"estrés_{w}"] = bp["Alpha"] * 100, e["Alpha"] * 100
        row[f"DD_{w}"], row[f"Sharpe_{w}"] = bp["Max Drawdown"] * 100, bp["Portfolio Sharpe Ratio"]
        if w == "completo":
            row["inicio"], row["CAGR"] = b["ventana_valuada"][0], bp["Annualized Return (CAGR)"] * 100
            row["vol"] = bp["Annualized Volatility"] * 100
    t = p.sheet(glob.glob(str(d / "backtest_completo_base" / "*.xlsx"))[0], "portfolio_bench_total_value", 2)
    t.index = pd.to_datetime(t.index)
    s, k = t["Total_Portfolio_Value"].astype(float), t["KN_US_Equity_Core_Value"].astype(float)
    for a, bb in [("2001", "2009"), ("2010", "2017"), ("2018", "2026")]:
        x, kk = s[a:bb], k[a:bb]
        n = (x.index[-1] - x.index[0]).days / 365.25
        row[f"vsKN_{a[2:]}-{bb[2:]}"] = ((x.iloc[-1] / x.iloc[0]) ** (1 / n) - (kk.iloc[-1] / kk.iloc[0]) ** (1 / n)) * 100
    rows.append(row)

df = pd.DataFrame(rows).set_index("estrategia").round(2).sort_values("estrés_2007", ascending=False)
pd.set_option("display.width", 320)
print(df.to_string())
df.to_csv(HERE / "evaluacion.csv")
