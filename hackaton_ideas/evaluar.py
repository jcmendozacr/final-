"""Evalúa las 6 combinaciones con el criterio fijado antes de correr (ventana 2010-01-04 a 2026-11-06).

1. Ninguna posición > 20% (acciones y ETFs).
2. Alfa con costos de estrés > alfa con estrés del modelo principal en la misma ventana.
3. Caída máxima (costos base) de −40% o menos.
4. Le gana al KN Core en 2010–2017 y en 2018–2026 (CAGR con la serie diaria del motor, costos base).
Gana la de mayor alfa con estrés entre las que cumplan; si ninguna, se queda el modelo principal.
2001–2009 se reporta aparte (dentro de muestra del modelo de riesgo; solo referencia).
"""

import glob
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "hackaton_ideas"
sys.path.insert(0, str(ROOT / "paralelo_etf"))
import paralelo as p  # noqa: E402


def serie(carpeta):
    t = p.sheet(glob.glob(str(carpeta / "*_backtest_results.xlsx"))[0], "portfolio_bench_total_value", 2)
    t.index = pd.to_datetime(t.index)
    return t["Total_Portfolio_Value"].astype(float), t["KN_US_Equity_Core_Value"].astype(float)


def cagr(s, a, b):
    x = s[a:b]
    return (x.iloc[-1] / x.iloc[0]) ** (365.25 / (x.index[-1] - x.index[0]).days) - 1


def leer(c):
    return json.loads((c / "resumen.json").read_text(encoding="utf-8"))


ref = HERE / "referencia_modelo_principal"
rb, re_ = leer(ref / "backtest_base")["portafolio"], leer(ref / "backtest_estres")["portafolio"]
alfa_ref = re_["Alpha"]
filas = [{"combinación": "Modelo principal (referencia)", "CAGR": rb["Annualized Return (CAGR)"],
          "alfa": rb["Alpha"], "alfa_estrés": re_["Alpha"], "vol": rb["Annualized Volatility"],
          "sharpe": rb["Portfolio Sharpe Ratio"], "caída_máx": rb["Max Drawdown"], "peso_máx": 0.06}]
sv, kv = serie(ref / "backtest_base")
filas[0].update({"vs_KN_2010_17": cagr(sv, "2010", "2017") - cagr(kv, "2010", "2017"),
                 "vs_KN_2018_26": cagr(sv, "2018", "2026") - cagr(kv, "2018", "2026")})

for d in sorted(HERE.glob("I*__*")):
    b, e = leer(d / "backtest_base"), leer(d / "backtest_estres")
    bp, ep = b["portafolio"], e["portafolio"]
    s, k = serie(d / "backtest_base")
    sc, kc = serie(d / "backtest_completo_base")
    w = pd.read_csv(d / "weights.csv", index_col=0)
    dd = s / s.cummax() - 1
    fila = {"combinación": d.name, "CAGR": bp["Annualized Return (CAGR)"], "alfa": bp["Alpha"],
            "alfa_estrés": ep["Alpha"], "vol": bp["Annualized Volatility"], "sharpe": bp["Portfolio Sharpe Ratio"],
            "caída_máx": bp["Max Drawdown"], "peso_máx": w.values.max(),
            "vs_KN_2010_17": cagr(s, "2010", "2017") - cagr(k, "2010", "2017"),
            "vs_KN_2018_26": cagr(s, "2018", "2026") - cagr(k, "2018", "2026"),
            "caída_actual": dd.iloc[-1], "peor_caída": f"{s[:dd.idxmin()].idxmax().date()} → {dd.idxmin().date()}",
            "ref_2001_09": cagr(sc, "2001", "2009") - cagr(kc, "2001", "2009")}
    fila["c1"] = fila["peso_máx"] <= 0.2 + 1e-9
    fila["c2"] = fila["alfa_estrés"] > alfa_ref
    fila["c3"] = fila["caída_máx"] >= -0.40
    fila["c4"] = fila["vs_KN_2010_17"] > 0 and fila["vs_KN_2018_26"] > 0
    fila["cumple"] = fila["c1"] and fila["c2"] and fila["c3"] and fila["c4"]
    filas.append(fila)

t = pd.DataFrame(filas).set_index("combinación")
pct = ["CAGR", "alfa", "alfa_estrés", "vol", "caída_máx", "vs_KN_2010_17", "vs_KN_2018_26", "caída_actual", "ref_2001_09"]
v = t.copy()
v[pct] = (v[pct] * 100).round(2)
v["sharpe"] = v["sharpe"].round(2)
v["peso_máx"] = v["peso_máx"].round(2)
pd.set_option("display.width", 300)
print(v.to_string())
ok = t[t["cumple"] == True]  # noqa: E712
ganador = ok["alfa_estrés"].idxmax() if len(ok) else "Modelo principal (ninguna cumple)"
print("\nAlfa con estrés del modelo principal en 2010–2026: %.2f%%" % (alfa_ref * 100))
print("GANADOR:", ganador)
v.to_csv(HERE / "evaluacion.csv")
(HERE / "ganador.txt").write_text(ganador, encoding="utf-8")
