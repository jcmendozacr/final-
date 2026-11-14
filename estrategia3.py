"""
ESTRATEGIA: Rotacion por momentum con filtro de tendencia (multi-activo)
Track 04 WealthTech - Talavera Valley Hackathon 2026

LOGICA ECONOMICA (escrita ANTES del backtest):
  Los activos que vienen subiendo tienden a seguir subiendo unos meses (momentum).
  Cuando un activo cae debajo de su tendencia de largo plazo (promedio de 200 dias),
  conviene salir y refugiarse en bonos de corto plazo (SHY).
  Asi Ana participa en los mercados alcistas y se protege en las crisis.

REGLAS:
  1. Universo: 10 ETFs de distintas clases de activo + SHY como refugio.
  2. Al cierre del ultimo dia de cada mes se ordenan por rendimiento de los ultimos 126 dias (~6 meses).
  3. Se eligen los TOP_N mejores, solo si: momentum > 0 Y precio > promedio de 200 dias.
  4. Cada lugar vale 1/TOP_N (20% con TOP_N=5). Lugares vacios -> SHY.
  5. Se opera el dia habil SIGUIENTE a la senal (no usamos informacion del futuro).
  6. Costos: COSTO_BPS por cada peso que se compra o vende (rotacion).
  7. Diseno: 2009-2018. Prueba fuera de muestra (una sola vez): 2019 en adelante.

USO:
  python estrategia.py . multiactivo   (perfil conservador)
  python estrategia.py . sectores      (perfil dinamico)
  python estrategia.py . regimen       (v3: tendencia del mercado + mejores sectores)
  (la carpeta donde el Data Curator guardo SPY.csv, QQQ.csv, etc.; busca en subcarpetas)

REQUISITOS: pip install pandas numpy matplotlib
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# ----------------------------- PARAMETROS ---------------------------------
UNIVERSOS = {
    # Perfil CONSERVADOR: multi-activo (acciones, bonos, bienes raices, oro)
    "multiactivo": ["SPY", "QQQ", "IWM", "EFA", "EEM", "VNQ", "TLT", "IEF", "LQD", "GLD"],
    # Perfil DINAMICO: los 9 sectores originales del S&P 500 (todos, sin escoger ganadores)
    "sectores": ["XLK", "XLF", "XLV", "XLE", "XLY", "XLP", "XLI", "XLU", "XLB"],
}
# Perfil REGIMEN (v3): la tendencia del SPY decide si estamos "en riesgo" o "a la defensiva"
UNIVERSOS["regimen"] = UNIVERSOS["sectores"]
DEFENSIVOS = ["SHY", "IEF", "TLT", "GLD", "LQD"]   # 20% cada uno cuando el mercado esta en crisis

PERFIL = sys.argv[2] if len(sys.argv) > 2 else "multiactivo"
RIESGO = UNIVERSOS[PERFIL]
REFUGIO = "SHY"
EXTRA = DEFENSIVOS if PERFIL == "regimen" else []
BENCHMARK = "SPY"

LOOKBACK = 126        # dias de momentum (~6 meses)
SMA = 200             # dias del filtro de tendencia
TOP_N = 5             # numero de ETFs a comprar (5 -> 20% cada uno)
COSTO_BPS = 10        # costo por operacion en puntos base (0.10%)

INICIO = "2009-01-01"
FIN_DISENO = "2018-12-31"
INICIO_PRUEBA = "2019-01-01"

COLUMNA = "m_close_dividend_and_split_adjusted"
# ---------------------------------------------------------------------------


def cargar_precios(carpeta: Path) -> pd.DataFrame:
    precios = {}
    for t in list(dict.fromkeys(RIESGO + [REFUGIO, BENCHMARK] + EXTRA)):
        archivos = sorted(carpeta.rglob(f"{t}.csv"), key=lambda p: p.stat().st_mtime)
        if not archivos:
            raise FileNotFoundError(f"No encontre {t}.csv dentro de {carpeta}")
        df = pd.read_csv(archivos[-1], parse_dates=["m_date"]).set_index("m_date")
        precios[t] = df[COLUMNA]
    px = pd.DataFrame(precios).sort_index()
    return px.dropna()  # solo dias donde los 11 tienen precio


def calcular_pesos(px: pd.DataFrame, lookback=LOOKBACK, top_n=TOP_N) -> pd.DataFrame:
    """Pesos objetivo decididos al cierre del ultimo dia habil de cada mes."""
    mom = px[RIESGO] / px[RIESGO].shift(lookback) - 1
    sma = px[RIESGO].rolling(SMA).mean()
    fin_de_mes = px.groupby(px.index.to_period("M")).tail(1).index

    filas = []
    for fecha in fin_de_mes:
        m, precio, prom = mom.loc[fecha], px.loc[fecha, RIESGO], sma.loc[fecha]
        if m.isna().any() or prom.isna().any():
            continue  # aun en periodo de calentamiento
        w = pd.Series(0.0, index=px.columns)
        if PERFIL == "regimen":
            mercado_sano = px.loc[fecha, BENCHMARK] > px[BENCHMARK].rolling(SMA).mean().loc[fecha]
            if mercado_sano:
                w[m.sort_values(ascending=False).index[:top_n]] = 1.0 / top_n
            else:
                w[DEFENSIVOS] = 1.0 / len(DEFENSIVOS)
        else:
            elegibles = m[(m > 0) & (precio > prom)].sort_values(ascending=False)
            elegidos = elegibles.index[:top_n]
            w[elegidos] = 1.0 / top_n
            w[REFUGIO] = 1.0 - w[RIESGO].sum()
        w.name = fecha
        filas.append(w)
    return pd.DataFrame(filas)


def backtest(px: pd.DataFrame, pesos_mes: pd.DataFrame, costo_bps=COSTO_BPS):
    """Backtest diario. La senal del dia t se ejecuta al cierre de t+1."""
    rets = px.pct_change().fillna(0.0)
    fechas = px.index
    w_obj = pesos_mes.reindex(fechas).ffill().shift(1)  # ejecutar al dia siguiente
    cambios = pesos_mes.index.map(lambda d: fechas[fechas.get_loc(d) + 1]
                                  if fechas.get_loc(d) + 1 < len(fechas) else None)
    cambios = set(c for c in cambios if c is not None)

    w = pd.Series(0.0, index=px.columns)
    valor, curva, rotacion = 1.0, [], []
    for d in fechas:
        if w_obj.loc[d].isna().all():
            curva.append(np.nan); rotacion.append(0.0); continue
        r = rets.loc[d]
        if w.sum() > 0:
            # crecimiento del dia con los pesos que se tenian
            crec = (w * (1 + r)).sum()
            valor *= crec
            w = w * (1 + r) / crec  # los pesos se mueven con el mercado
        turn = 0.0
        if d in cambios or w.sum() == 0:
            nuevo = w_obj.loc[d].fillna(0.0)
            turn = (nuevo - w).abs().sum()
            valor *= 1 - turn * costo_bps / 10_000
            w = nuevo.copy()
        curva.append(valor); rotacion.append(turn)
    out = pd.DataFrame({"estrategia": curva, "rotacion": rotacion}, index=fechas)
    return out.dropna()


def metricas(serie: pd.Series, bench: pd.Series, refugio: pd.Series) -> dict:
    r = serie.pct_change().dropna()
    rb = bench.pct_change().reindex(r.index).fillna(0)
    rf = refugio.pct_change().reindex(r.index).fillna(0)
    anios = len(r) / 252
    cagr = (serie.iloc[-1] / serie.iloc[0]) ** (1 / anios) - 1
    cagr_b = (bench.loc[r.index[-1]] / bench.loc[serie.index[0]]) ** (1 / anios) - 1
    vol = r.std() * np.sqrt(252)
    exceso = r - rf
    sharpe = exceso.mean() / exceso.std() * np.sqrt(252)
    dd = (serie / serie.cummax() - 1).min()
    beta = np.cov(r, rb)[0, 1] / rb.var()
    alfa = ((r - rf) - beta * (rb - rf)).mean() * 252  # alfa anual ajustado por riesgo (CAPM)
    activo = r - rb
    te = activo.std() * np.sqrt(252)
    ir = activo.mean() * 252 / te if te > 1e-4 else np.nan
    return {
        "CAGR": cagr, "CAGR benchmark": cagr_b, "Exceso vs benchmark": cagr - cagr_b,
        "Volatilidad": vol, "Sharpe": sharpe, "Max caida": dd,
        "Beta": beta, "Alfa (CAPM, anual)": alfa,
        "Tracking error": te, "Information ratio": ir,
    }


def periodo(curva, px, ini, fin=None):
    c = curva.loc[ini:fin, "estrategia"]
    return metricas(c / c.iloc[0], px.loc[c.index, BENCHMARK], px.loc[c.index, REFUGIO])


def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    carpeta = Path(sys.argv[1])
    salida = carpeta / f"resultados_{PERFIL}"
    salida.mkdir(exist_ok=True)
    print(f"PERFIL: {PERFIL}  ->  {', '.join(RIESGO)}  (refugio {REFUGIO})")

    px = cargar_precios(carpeta)
    print(f"Datos: {px.index[0].date()} a {px.index[-1].date()}  ({len(px)} dias, {px.shape[1]} ETFs)")

    pesos = calcular_pesos(px)
    curva = backtest(px, pesos).loc[INICIO:]

    # 1) Metricas por periodo
    tabla = pd.DataFrame({
        "DISENO 2009-2018": periodo(curva, px, INICIO, FIN_DISENO),
        "PRUEBA 2019-hoy": periodo(curva, px, INICIO_PRUEBA),
        "COMPLETO": periodo(curva, px, INICIO),
    })
    # El propio SPY con las mismas metricas, para comparar lado a lado
    spy = px.loc[INICIO_PRUEBA:, BENCHMARK]
    tabla["SPY 2019-hoy"] = pd.Series(metricas(spy / spy.iloc[0], spy, px.loc[spy.index, REFUGIO]))
    pd.set_option("display.float_format", lambda x: f"{x:,.3f}")
    print("\n=== METRICAS (despues de costos, en dolares) ===")
    print(tabla)
    rot = curva["rotacion"].resample("YE").sum().mean()
    print(f"\nRotacion promedio anual: {rot:.0%} del portafolio  |  costo usado: {COSTO_BPS} bps")
    tabla.to_csv(salida / "metricas.csv")
    if PERFIL == "regimen":
        defensa = (pesos.loc[INICIO:, DEFENSIVOS].sum(axis=1) > 0.99).mean()
        print(f"Meses a la defensiva (SPY bajo su promedio de 200 dias): {defensa:.0%}")

    # 2) Robustez: si solo funciona con UN parametro, esta sobreajustada
    print("\n=== ROBUSTEZ (Sharpe en DISENO | PRUEBA) ===")
    filas = []
    for lb in [63, 126, 189, 252]:
        for n in [3, 4, 5]:
            c = backtest(px, calcular_pesos(px, lb, n)).loc[INICIO:]
            d, p = periodo(c, px, INICIO, FIN_DISENO), periodo(c, px, INICIO_PRUEBA)
            filas.append({"lookback": lb, "top_n": n,
                          "Sharpe diseno": d["Sharpe"], "Sharpe prueba": p["Sharpe"],
                          "CAGR prueba": p["CAGR"], "Max caida prueba": p["Max caida"]})
    rob = pd.DataFrame(filas)
    print(rob.to_string(index=False))
    rob.to_csv(salida / "robustez.csv", index=False)

    # 3) Pesos mensuales (para cargar al Lab / mostrar en el pitch)
    pesos.loc[INICIO:].to_csv(salida / "pesos_mensuales.csv", float_format="%.4f")
    print("\nUltima asignacion:")
    print(pesos.iloc[-1][pesos.iloc[-1] > 0].map("{:.0%}".format).to_string())

    # 4) Grafica
    try:
        import matplotlib.pyplot as plt
        c = curva["estrategia"] / curva["estrategia"].iloc[0]
        b = px.loc[c.index, BENCHMARK] / px.loc[c.index[0], BENCHMARK]
        fig, ax = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                               gridspec_kw={"height_ratios": [3, 1]})
        ax[0].plot(c, label="Estrategia"); ax[0].plot(b, label="SPY", alpha=.7)
        ax[0].axvline(pd.Timestamp(INICIO_PRUEBA), color="gray", ls="--")
        ax[0].text(pd.Timestamp(INICIO_PRUEBA), ax[0].get_ylim()[1] * .9, "  fuera de muestra")
        ax[0].set_yscale("log"); ax[0].set_title("Crecimiento de $1 (despues de costos)")
        ax[0].legend()
        ax[1].fill_between(c.index, c / c.cummax() - 1, 0, alpha=.5, label="Estrategia")
        ax[1].plot(b / b.cummax() - 1, alpha=.7, label="SPY"); ax[1].set_title("Caidas")
        plt.tight_layout(); plt.savefig(salida / "curva.png", dpi=150)
        print(f"\nGrafica: {salida / 'curva.png'}")
    except ImportError:
        print("(instala matplotlib para la grafica)")

    print(f"Resultados guardados en: {salida}")


if __name__ == "__main__":
    main()
