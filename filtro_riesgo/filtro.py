"""Filtro de riesgo confirmado por un modelo, entrenado 2000–2009 y probado 2010–2026 (solo datos KaxaNuk).

Pre-registro (fijado antes de ver resultados de prueba):
- Señal base: KN US Equity Core < su media de 200 días al cierre de fin de mes.
- Modelo: regresión logística (numpy, L2 fija = 1.0, variables estandarizadas con medias y desviaciones
  del entrenamiento), 4 variables calculadas solo con el precio de cada índice:
      tendencia = precio / media 200 días − 1
      mom12     = rendimiento de 252 días
      vol63     = volatilidad anualizada de 63 días
      dist_max  = precio / máximo de 252 días − 1
- Etiqueta: el índice cae más de 5% en los siguientes 63 días hábiles.
- Entrenamiento: panel del KN Core + 11 índices sectoriales KN (ponderados por capitalización, con la
  clasificación sectorial de KN de cada día), meses de 2000 a 2009-09 (embargo: la etiqueta del último
  mes de entrenamiento termina dentro de 2009).
- Prueba: KN Core, meses de 2010-01 a 2026-08 (el último con etiqueta completa).
- Umbral: frecuencia de la etiqueta en el entrenamiento.
- Filtro confirmado: salir solo si la señal base está activa Y la probabilidad del modelo > umbral.
- Se adopta si en la prueba elimina ≥ 25% de las falsas alarmas del filtro base (señal activa sin caída
  > 5% en 3 meses) y no pierde ninguna salida correcta del filtro base en 2020 ni en 2022.

Uso:
    python filtro_riesgo/filtro.py <carpeta KN> <carpeta KN_sectores>
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from preparar_motor import read_dated  # noqa: E402

HERE = ROOT / "filtro_riesgo"
SECTORES = ["Energy", "Materials", "Industrials", "Consumer_Discretionary", "Consumer_Staples",
            "Health_Care", "Financials", "Technology", "Communication", "Utilities", "Real_Estate"]
VARS = ["tendencia", "mom12", "vol63", "dist_max"]
FIN_TRAIN, INI_TEST = "2009-09-30", "2010-01-01"
HORIZONTE, CAIDA, L2 = 63, -0.05, 1.0


def indices(kn, kn_sect):
    core = read_dated(kn / "KN_US_Equity_Core_Returns_Daily.csv")["return"]
    holdings = read_dated(kn / "KN_US_Equity_Core_Holdings_Daily.csv")
    excess = read_dated(kn / "KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv")
    dates = excess.index.intersection(core.index).intersection(holdings.index)
    shared = excess.columns.intersection(holdings.columns)
    h = holdings.loc[dates, shared].shift(1)
    x = excess.loc[dates, shared]
    implied = core.loc[dates] - (h * x.fillna(0)).sum(axis=1)
    bill = implied.rolling(21, min_periods=1).median()
    total = x.add(bill, axis=0)
    out = {"KN_Core": (1 + core.loc[dates]).cumprod()}
    for s in SECTORES:
        m = read_dated(kn_sect / f"KN_US_Equity_Factor_{s}_Daily.csv").reindex(index=dates, columns=shared).notna()
        w = h.where(m.shift(1, fill_value=False)).fillna(0)
        r = (w * total.fillna(0)).sum(axis=1) / w.sum(axis=1).replace(0, np.nan)
        out[s] = (1 + r.fillna(0)).cumprod()
    return pd.DataFrame(out)


def variables(p):
    f = pd.DataFrame({
        "tendencia": p / p.rolling(200).mean() - 1,
        "mom12": p / p.shift(252) - 1,
        "vol63": p.pct_change().rolling(63).std() * 252 ** 0.5,
        "dist_max": p / p.rolling(252).max() - 1,
    })
    f["etiqueta"] = (p.shift(-HORIZONTE) / p - 1) < CAIDA
    f.loc[p.shift(-HORIZONTE).isna(), "etiqueta"] = np.nan
    f["señal_base"] = f["tendencia"] < 0
    fin_mes = p.groupby(p.index.to_period("M")).apply(lambda s: s.index[-1])
    return f.loc[fin_mes.values]


def logistica(X, y, l2):
    Xb = np.c_[np.ones(len(X)), X]
    b = np.zeros(Xb.shape[1])
    for _ in range(100):  # Newton-Raphson con L2 (sin penalizar la constante)
        pr = 1 / (1 + np.exp(-Xb @ b))
        P = np.eye(len(b)) * l2
        P[0, 0] = 0
        g = Xb.T @ (pr - y) + P @ b
        H = Xb.T @ (Xb * (pr * (1 - pr))[:, None]) + P
        paso = np.linalg.solve(H, g)
        b -= paso
        if np.abs(paso).max() < 1e-9:
            break
    return b


def main(kn, kn_sect):
    idx = indices(kn, kn_sect)
    idx.to_csv(HERE / "indices_kn.csv")
    panel = {c: variables(idx[c]).dropna(subset=VARS) for c in idx.columns}

    train = pd.concat([d.loc[:FIN_TRAIN] for d in panel.values()]).dropna(subset=["etiqueta"])
    mu, sd = train[VARS].mean(), train[VARS].std()
    b = logistica(((train[VARS] - mu) / sd).values, train["etiqueta"].astype(float).values, L2)
    umbral = train["etiqueta"].mean()

    test = panel["KN_Core"].loc[INI_TEST:].copy()
    test["prob"] = 1 / (1 + np.exp(-(np.c_[np.ones(len(test)), ((test[VARS] - mu) / sd).values] @ b)))
    test["señal_modelo"] = test["señal_base"] & (test["prob"] > umbral)
    test.to_csv(HERE / "prueba_mensual.csv")
    ev = test.dropna(subset=["etiqueta"])
    ev = ev.assign(etiqueta=ev["etiqueta"].astype(bool))

    def cuenta(col):
        s = ev[col]
        return {"salidas": int(s.sum()), "correctas": int((s & ev.etiqueta).sum()),
                "falsas": int((s & ~ev.etiqueta).sum()), "caídas_reales": int(ev.etiqueta.sum()),
                "caídas_detectadas": int((s & ev.etiqueta).sum())}

    base, mod = cuenta("señal_base"), cuenta("señal_modelo")
    reduccion = 1 - mod["falsas"] / base["falsas"] if base["falsas"] else 0.0
    perdidas = {}
    for año in ("2020", "2022"):
        e = ev.loc[año]
        perdidas[año] = [str(d.date()) for d in e.index[e["señal_base"] & e.etiqueta & ~e["señal_modelo"]]]
    adopta = reduccion >= 0.25 and not any(perdidas.values())

    coef = dict(zip(["constante"] + VARS, np.round(b, 3)))
    resumen = {"entrenamiento_meses": len(train), "entrenamiento_caídas": int(train["etiqueta"].sum()),
               "umbral": round(float(umbral), 3), "coeficientes": coef,
               "prueba": {"filtro_base": base, "filtro_confirmado": mod,
                          "reducción_falsas_alarmas": round(reduccion, 3),
                          "salidas_correctas_perdidas": perdidas},
               "se_adopta": adopta}
    (HERE / "resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    print("\nMeses de prueba con señal base (fecha, prob, caída real >5% en 3m, sale con modelo):")
    for d, r in ev[ev["señal_base"]].iterrows():
        print(f"  {d.date()}  p={r.prob:.2f}  caída={'SÍ' if r.etiqueta else 'no'}  modelo={'sale' if r['señal_modelo'] else 'se queda'}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
