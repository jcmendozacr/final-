"""Escribe el weights.csv de P1 (refugio ampliado) para el Backtest Engine de KaxaNuk.

Parte de un weights.csv y cambia solo las columnas del régimen de caída: la posición en IEF/SHY
se reemplaza por la canasta P1 (paralelo.py).

Uso:
    python paralelo_etf/generar_weights_P1.py
        -> parte del congelado del modelo principal (que no se toca) y escribe
           paralelo_etf/resultados_P1/
También lo usa variantes_kn.py, con aplicar_a_carpeta(), sobre otras variantes.
"""
import pandas as pd

import paralelo as p

OUT = p.ROOT / "paralelo_etf" / "resultados_P1"
ETFS_NUEVOS = sorted(set(p.REFUGIO_P1) - {"SHY", "IEF"})


def aplicar(w, reg):
    """Devuelve (weights con P1 en las columnas de caída, número de columnas cambiadas)."""
    w = w.copy()
    mom = p.momentum_13612(p.load_prices(), reg["señal"])
    changed = 0
    for _, r in reg[reg["régimen"] == "caida"].iterrows():
        col = r["operación"].strftime("%Y-%m-%d")
        if col not in w.columns or r["señal"] not in mom.index:
            continue
        total = w.loc[w.index.isin(["IEF", "SHY"]), col].sum()
        w.loc[w.index.isin(["IEF", "SHY"]), col] = 0.0
        for t, x in p.basket(mom.loc[r["señal"]], p.REFUGIO_P1, p.N_REFUGIO).items():
            if t not in w.index:
                w.loc[t] = 0.0
            w.loc[t, col] += total * x
        changed += 1
    w = w.fillna(0.0)
    assert (w.sum() - 1).abs().max() < 1e-6, "los pesos no suman 1"
    return w, changed


def aplicar_a_carpeta(carpeta):
    """Aplica P1 al weights.csv de una carpeta de variante y agrega los ETFs a su lista del Curator."""
    w = pd.read_csv(carpeta / "weights.csv", index_col="Ticker").astype(float)
    reg = pd.read_csv(carpeta / "regimenes.csv", parse_dates=["señal", "operación"])
    w, changed = aplicar(w, reg)
    w.to_csv(carpeta / "weights.csv", float_format="%.10f")
    lista = carpeta / "tickers_para_curator.csv"
    if lista.exists():
        t = pd.read_csv(lista)
        nuevos = pd.DataFrame({"ticker": [x for x in ETFS_NUEVOS if x not in set(t["ticker"])], "nota": "ETF P1"})
        pd.concat([t, nuevos], ignore_index=True).to_csv(lista, index=False)
    print(f"P1 aplicado: {changed} columnas de caída cambiadas en {carpeta}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    w = pd.read_csv(p.MODEL / "weights.csv", index_col="Ticker")
    reg = pd.read_csv(p.MODEL / "regimenes.csv", parse_dates=["señal", "operación"])
    w, changed = aplicar(w, reg)
    w.to_csv(OUT / "weights.csv", float_format="%.10f")
    pd.DataFrame({"ticker": ETFS_NUEVOS}).to_csv(OUT / "etfs_nuevos_para_curator.csv", index=False)
    print(f"{changed} columnas de caída cambiadas; {w.shape[0]} tickers × {w.shape[1]} fechas -> {OUT}")


if __name__ == "__main__":
    main()
