"""Genera los pesos de las variantes que cambian las acciones (necesita los datos KN).

Usa el mismo código del modelo principal (modelo_regimen.py y nucleo_satelite.py, sin
modificarlos) y solo cambia la selección de acciones:

- replica/  : el principal tal cual. Debe salir IDÉNTICO a resultados_regimen_n10_a60/weights.csv;
              si no, el script se detiene y no escribe las variantes.
- I1/       : regla de permanencia (IDEA_1.md): entra en el top 10, sale al caer del top 20.
- P1_I1/    : I1 + el refugio ampliado de P1 en el régimen de caída.

Uso (con el .venv del proyecto):
    python paralelo_etf/variantes_kn.py <carpeta KN>   ->  paralelo_etf/variantes/
"""

import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(AQUI))

import modelo_regimen  # noqa: E402
import nucleo_satelite  # noqa: E402

import generar_weights_P1  # noqa: E402

SALIDA = AQUI / "variantes"
ETF_DIR = ROOT / "datos_etf" / "precios"
CONGELADO = ROOT / "resultados_regimen_n10_a60" / "weights.csv"
ARGS_PRINCIPAL = ["0.35", "10", "0.60"]  # interruptor, número de acciones, % en acciones en alcista
BANDA = 20  # I1: una acción se queda mientras siga en el top 20

_signals_original = nucleo_satelite.signals


def signals_permanencia(returns, holdings):
    """Igual que nucleo_satelite.signals, pero con banda de permanencia (top N entra, top BANDA sale)."""
    n = nucleo_satelite.N_STOCKS
    log_cum = np.log1p(returns.fillna(0).clip(lower=-0.99)).cumsum()
    momentum = log_cum.shift(21) - log_cum.shift(252).fillna(0)
    has_history = returns.notna().rolling(252).sum() >= 240
    dates = returns.index
    month_ends = pd.Series(dates, index=dates).groupby([dates.year, dates.month]).max()
    picks, actuales = {}, []
    for signal_date in month_ends[month_ends >= nucleo_satelite.FIRST_SIGNAL]:
        next_days = dates[dates > signal_date]
        if len(next_days) == 0:
            continue
        weights_today = holdings.loc[signal_date]
        eligible = weights_today[weights_today > 0].nlargest(nucleo_satelite.UNIVERSE_SIZE).index
        scores = momentum.loc[signal_date, eligible][has_history.loc[signal_date, eligible]].dropna()
        if len(scores) < n:
            continue
        ranking = list(scores.sort_values(ascending=False, kind="mergesort").index)
        lugar = {t: i for i, t in enumerate(ranking)}
        se_quedan = [t for t in actuales if t in lugar and lugar[t] < BANDA]
        entran = [t for t in ranking if t not in se_quedan][: n - len(se_quedan)]
        actuales = sorted(se_quedan + entran, key=lugar.get)
        picks[next_days[0]] = list(actuales)
    return picks


def generar(kn, carpeta, signals):
    carpeta.mkdir(parents=True, exist_ok=True)
    nucleo_satelite.signals = signals
    argv = sys.argv
    sys.argv = ["modelo_regimen.py", str(kn), str(ETF_DIR), str(carpeta), *ARGS_PRINCIPAL]
    try:
        modelo_regimen.main()
    finally:
        sys.argv = argv
        nucleo_satelite.signals = _signals_original


def igual_al_congelado(weights_csv):
    a = pd.read_csv(weights_csv, index_col="Ticker").astype(float)
    b = pd.read_csv(CONGELADO, index_col="Ticker").astype(float)
    if a.shape != b.shape or list(a.columns) != list(b.columns) or set(a.index) != set(b.index):
        return False, f"forma distinta: {a.shape} contra {b.shape}"
    diff = (a.loc[b.index] - b).abs().to_numpy().max()
    return diff < 1e-9, f"diferencia máxima {diff:.2e}"


def rotacion(weights_csv):
    """Acciones nuevas por rebalanceo mensual, en promedio (sin contar SPY ni refugios)."""
    w = pd.read_csv(weights_csv, index_col="Ticker").astype(float)
    etfs = {"SPY", "SHY", "IEF", *generar_weights_P1.ETFS_NUEVOS}
    acciones = w.drop(index=[t for t in w.index if t in etfs])
    listas = [set(acciones.index[acciones[c] > 0]) for c in acciones.columns]
    cambios = [len(b - a) for a, b in zip(listas, listas[1:]) if a and b]
    return np.mean(cambios) if cambios else float("nan")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    kn = Path(sys.argv[1]).resolve()

    print("=== Réplica del principal ===")
    generar(kn, SALIDA / "replica", _signals_original)
    ok, detalle = igual_al_congelado(SALIDA / "replica" / "weights.csv")
    print(f"Réplica idéntica al congelado: {'sí' if ok else 'NO'} ({detalle})")
    if not ok:
        print("Se detiene: sin una réplica exacta no se puede atribuir la diferencia a la regla.")
        sys.exit(1)

    print("\n=== I1 permanencia (top 10 entra, top 20 sale) ===")
    generar(kn, SALIDA / "I1", signals_permanencia)

    print("\n=== P1 + I1 ===")
    destino = SALIDA / "P1_I1"
    if destino.exists():
        shutil.rmtree(destino)
    shutil.copytree(SALIDA / "I1", destino)
    generar_weights_P1.aplicar_a_carpeta(destino)

    print("\nAcciones nuevas por rebalanceo (promedio):")
    for nombre in ("replica", "I1", "P1_I1"):
        print(f"  {nombre:<8} {rotacion(SALIDA / nombre / 'weights.csv'):.2f}")
    print(f"\nListo en {SALIDA}. Siguiente: correr_kit.py <KN> paralelo_etf/variantes/I1")


if __name__ == "__main__":
    main()
