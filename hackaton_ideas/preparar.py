"""Tres ideas con tope de 20% por posición, cada una con dos filtros de mercado. Solo genera pesos y precios.

Calendario: señal al cierre de fin de mes, operación el primer día hábil siguiente (calendario KN).
Precios: acciones con datos de KaxaNuk (índice de rendimiento total, escalado a 1); ETFs con el Data
Curator (datos_etf/precios y datos_etf_hackaton/precios).

Filtros de mercado:
    base    KN Core < su media de 200 días al cierre de la señal -> canasta de refugio
    modelo  base Y probabilidad del modelo de filtro_riesgo > umbral (entrenado 2000–2009)
Canasta de refugio: SHY, IEF, TLT, GLD, UUP al 20% cada uno (si alguno aún no existe, su 20% queda en
efectivo). Los lugares vacíos de cualquier idea se llenan, en ese orden, con los refugios no tenidos.

Universos de acciones (sin sesgo, con datos del día de la señal):
    sectorial18  criterio OKRUS: más grandes del KN Core por grupo (Tech/IA 8, Financiero 3,
                 Energía 2, Salud 2, Consumo 3) con sectores KN
    sector_top20 las 20 más grandes del KN Core dentro de un sector KN

Ideas:
    I1_lider_sectorial  ETF sectorial con mayor momentum de 252 días (si es > 0): 20% en el ETF + 4
                        acciones de ese sector (sector_top20) por momentum 252d / volatilidad 63d,
                        elegibles si precio > EMA200, precio >= 85% del máximo de 63 días y mom252 > 0;
                        vacíos -> siguientes ETFs sectoriales con momentum > 0, luego refugios.
    I2_estrella_a1      3 acciones A1 (sectorial18; precio >= 85% del máximo de 63 días, mom252 > 0;
                        score mom252 / vol63) + 2 ETFs Estrella por mom252 (precio > SMA200 y mom252 > 0)
                        entre SPY, QQQ, IWM, EFA, EEM, TLT, GLD, VNQ, DBC, XLK, XLE, XLF, SMH; 20% c/u.
    I3_top5             5 acciones Agresiva (sectorial18; precio > EMA200, precio >= 85% del máximo de
                        63 días, mom126 > 0) por mom126, 20% c/u.

Uso:
    python hackaton_ideas/preparar.py <carpeta KN> <carpeta KN_sectores>
"""

import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "filtro_riesgo"))
from preparar_motor import index_frame, read_dated  # noqa: E402
import filtro  # noqa: E402

HERE = ROOT / "hackaton_ideas"
MOTOR = ROOT / "datos_backtest_hack" / "motor"
ETF_DIRS = [ROOT / "datos_etf_hackaton" / "precios", ROOT / "datos_etf" / "precios"]
PRICE = "m_close_dividend_and_split_adjusted"
REFUGIOS = ["SHY", "IEF", "TLT", "GLD", "UUP"]
ESTRELLA = ["SPY", "QQQ", "IWM", "EFA", "EEM", "TLT", "GLD", "VNQ", "DBC", "XLK", "XLE", "XLF", "SMH"]
SECTOR_ETF = {"Technology": ["XLK"], "Financials": ["XLF"], "Energy": ["XLE"], "Health_Care": ["XLV"],
              "Consumer_Discretionary": ["XLY"], "Consumer_Staples": ["XLP"], "Industrials": ["XLI"],
              "Utilities": ["XLU"], "Materials": ["XLB"], "Communication": ["XLC"],
              "Real_Estate": ["XLRE", "IYR"]}
GRUPOS = {"Tech/IA": (8, ["Technology", "Communication"]), "Financiero": (3, ["Financials"]),
          "Energía": (2, ["Energy", "Utilities"]), "Salud": (2, ["Health_Care"]),
          "Consumo": (3, ["Consumer_Discretionary", "Consumer_Staples"])}
CAP, START = 0.20, "2000-01-01"


def etf_file(t):
    for d in ETF_DIRS:
        if (d / f"{t}.csv").exists():
            return d / f"{t}.csv"
    raise FileNotFoundError(t)


def main(kn, kn_sect):
    MOTOR.mkdir(parents=True, exist_ok=True)
    core = read_dated(kn / "KN_US_Equity_Core_Returns_Daily.csv")["return"]
    holdings = read_dated(kn / "KN_US_Equity_Core_Holdings_Daily.csv")
    excess = read_dated(kn / "KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv")
    dates = excess.index.intersection(core.index).intersection(holdings.index)
    holdings = holdings.loc[dates]
    shared = excess.columns.intersection(holdings.columns)
    implied = core.loc[dates] - (holdings[shared].shift(1) * excess.loc[dates, shared].fillna(0)).sum(axis=1)
    bill = implied.rolling(21, min_periods=1).median()
    r = excess.loc[dates].add(bill, axis=0)
    valid = r.notna()
    alive = valid.cummax() & valid[::-1].cummax()[::-1]
    P = (1 + r.fillna(0)).cumprod().where(alive)

    # Sector KN de cada acción en cada día
    sector = pd.DataFrame(index=dates, columns=holdings.columns, dtype=object)
    for s in SECTOR_ETF:
        m = read_dated(kn_sect / f"KN_US_Equity_Factor_{s}_Daily.csv").reindex(index=dates, columns=holdings.columns)
        sector = sector.mask(m.notna(), s)

    # Variables de las acciones
    F = {"ema": P.ewm(span=200, adjust=False, ignore_na=True).mean().where(alive),
         "m126": P / P.shift(126) - 1, "m252": P / P.shift(252) - 1,
         "vol": P.pct_change(fill_method=None).rolling(63).std() * 252 ** 0.5,
         "peak": P.rolling(63, min_periods=1).max()}

    # ETFs
    etfs = sorted(set(REFUGIOS + ESTRELLA + ["SPY"] + [e for v in SECTOR_ETF.values() for e in v]))
    E = {}
    for t in etfs:
        d = pd.read_csv(etf_file(t), usecols=["m_date", PRICE])
        E[t] = pd.Series(d[PRICE].values, index=pd.to_datetime(d.m_date)).reindex(dates).ffill(limit=5)
        E[t] = E[t].where(E[t].index >= pd.Timestamp(d.m_date.iloc[0]))
    E = pd.DataFrame(E)
    E_m252 = E / E.shift(252) - 1
    E_sma = E.rolling(200).mean()

    # Calendario
    dias = dates[dates >= START]
    g = pd.Series(dias, index=dias).groupby(dias.to_period("M"))
    fin, ini = list(g.max()), list(g.first())
    pares = list(zip(fin[:-1], ini[1:]))

    # Filtros: base y modelo (coeficientes re-entrenados exactamente como en filtro_riesgo/filtro.py)
    idx = pd.read_csv(ROOT / "filtro_riesgo" / "indices_kn.csv", index_col=0, parse_dates=True)
    panel = {c: filtro.variables(idx[c]).dropna(subset=filtro.VARS) for c in idx.columns}
    train = pd.concat([d.loc[:filtro.FIN_TRAIN] for d in panel.values()]).dropna(subset=["etiqueta"])
    mu, sd = train[filtro.VARS].mean(), train[filtro.VARS].std()
    b = filtro.logistica(((train[filtro.VARS] - mu) / sd).values, train["etiqueta"].astype(float).values, filtro.L2)
    umbral = train["etiqueta"].mean()
    kc = panel["KN_Core"]
    prob = 1 / (1 + np.exp(-(np.c_[np.ones(len(kc)), ((kc[filtro.VARS] - mu) / sd).values] @ b)))
    kc = kc.assign(prob=prob)
    print("coeficientes:", dict(zip(["constante"] + filtro.VARS, np.round(b, 3))), "umbral", round(umbral, 3))
    knp = (1 + core.loc[dates]).cumprod()
    base_on = (knp < knp.rolling(200).mean())
    filtros = {"base": lambda d: bool(base_on.loc[d]),
               "modelo": lambda d: bool(base_on.loc[d]) and d in kc.index and kc.at[d, "prob"] > umbral}

    def existe(t, d):
        return t in E.columns and pd.notna(E.at[d, t])

    def rellenar(w, opera, extra=()):
        for t in list(extra) + REFUGIOS:
            if sum(w.values()) >= 1 - 1e-9:
                break
            if t not in w and existe(t, opera):
                w[t] = CAP
        return w

    def canasta(opera):
        return {t: CAP for t in REFUGIOS if existe(t, opera)}

    def sectorial18(d):
        w, s = holdings.loc[d], sector.loc[d]
        out = []
        for cupo, secs in GRUPOS.values():
            c = w[s.isin(secs) & (w > 0) & alive.loc[d]].sort_values(ascending=False)
            out += list(c.index[:cupo])
        return out

    def a1_rank(d, u):
        p = P.loc[d, u]
        ok = (p >= F["peak"].loc[d, u] * 0.85) & (F["m252"].loc[d, u] > 0) & (F["vol"].loc[d, u] > 0)
        return (F["m252"].loc[d, u] / F["vol"].loc[d, u])[ok].dropna().sort_values(ascending=False)

    def i1(d, opera):
        cand = {}
        for s, lista in SECTOR_ETF.items():
            t = next((e for e in lista if existe(e, d) and pd.notna(E_m252.at[d, e])), None)
            if t:
                cand[s] = (t, E_m252.at[d, t])
        orden = sorted(cand.items(), key=lambda x: -x[1][1])
        if not orden or orden[0][1][1] <= 0:
            return canasta(opera)
        s, (etf, _) = orden[0]
        w = {etf: CAP}
        hs = holdings.loc[d]
        top20 = hs[(sector.loc[d] == s) & (hs > 0) & alive.loc[d]].sort_values(ascending=False).index[:20]
        sc = a1_rank(d, list(top20))
        sc = sc[(P.loc[d, sc.index] > F["ema"].loc[d, sc.index])]
        for t in sc.index[:4]:
            w[t] = CAP
        otros = [e for _, (e, m) in orden[1:] if m > 0]
        return rellenar(w, opera, otros)

    def i2(d, opera):
        u = sectorial18(d)
        w = {t: CAP for t in a1_rank(d, u).index[:3]}
        ok = [t for t in ESTRELLA if existe(t, d) and pd.notna(E_m252.at[d, t]) and E_m252.at[d, t] > 0
              and E.at[d, t] > E_sma.at[d, t]]
        for t in sorted(ok, key=lambda t: -E_m252.at[d, t])[:2]:
            w[t] = CAP
        return rellenar(w, opera)

    def i3(d, opera):
        u = sectorial18(d)
        p = P.loc[d, u]
        ok = (p > F["ema"].loc[d, u]) & (p >= F["peak"].loc[d, u] * 0.85) & (F["m126"].loc[d, u] > 0)
        sc = F["m126"].loc[d, u][ok].dropna().sort_values(ascending=False)
        return rellenar({t: CAP for t in sc.index[:5]}, opera)

    ideas = {"I1_lider_sectorial": i1, "I2_estrella_a1": i2, "I3_top5": i3}
    usados = set()
    for nombre, regla in ideas.items():
        for fnombre, f_on in filtros.items():
            cols = {}
            for señal, opera in pares:
                if señal < pd.Timestamp("2001-01-01"):
                    continue  # 252 días de historia para las señales
                w = canasta(opera) if f_on(señal) else regla(señal, opera)
                cols[opera.strftime("%Y-%m-%d")] = w
            df = pd.DataFrame(cols).fillna(0.0)
            df.index.name = "Ticker"
            assert df.values.max() <= CAP + 1e-9, nombre
            assert (df.sum() <= 1 + 1e-9).all(), nombre
            out = HERE / f"{nombre}__{fnombre}"
            out.mkdir(parents=True, exist_ok=True)
            df.to_csv(out / "weights.csv", float_format="%.6f")
            usados |= set(df.index)
            acc = df.drop(index=[t for t in df.index if t in E.columns])
            print(f"{nombre}/{fnombre}: {df.shape[1]} rebalanceos; meses en canasta de refugio: "
                  f"{int((df.reindex(REFUGIOS).fillna(0).sum() >= 0.6).sum())}; acciones distintas: {len(acc)}; "
                  f"peso medio en acciones: {acc.sum().mean():.2f}")

    # Carpeta del motor
    index_frame(core.loc[dates]).to_csv(MOTOR / "KN_US_Equity_Core.csv", index=False)
    for t in usados | {"SPY"}:
        if t in E.columns:
            shutil.copyfile(etf_file(t), MOTOR / f"{t}.csv")
        else:
            frame = index_frame(r[t].where(alive[t]).dropna())
            cols_p = [c for c in frame.columns if c not in ("m_date", "m_volume_split_adjusted")]
            frame[cols_p] = frame[cols_p] / 100
            # 8 decimales: con más, el motor no lee precios casi en cero (p. ej. Nortel tras quebrar)
            frame.to_csv(MOTOR / f"{t}.csv", index=False, float_format="%.8f")
    print(f"motor: {len(usados | {'SPY'})} archivos de precios + benchmark")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
