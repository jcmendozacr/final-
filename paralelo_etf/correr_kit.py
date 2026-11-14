"""Corre una variante en el Backtest Engine oficial y la compara con el modelo principal.

No toca el modelo principal: sus pesos, precios y resultados solo se leen. Todo lo nuevo va a
datos_backtest_<variante>/ y a la carpeta de la variante.

Uso (desde la carpeta del proyecto, con el .venv que ya tiene el motor):
    python paralelo_etf/correr_kit.py <carpeta KN>                                  # P1
    python paralelo_etf/correr_kit.py <carpeta KN> paralelo_etf/variantes/I1        # otra variante
    python paralelo_etf/correr_kit.py <carpeta KN> [variante] --comparar            # solo la tabla

<carpeta KN> = los CSV de KN_US_Equity_Core.zip y KN_US_Equity_Factor_Model.zip, sin subcarpetas.
La variante es una carpeta con weights.csv (y, si cambia acciones, tickers_para_curator.csv).
La licencia se lee de KNBE_API_KEY_KAXANUK y nunca se imprime.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable
P1 = ROOT / "paralelo_etf" / "resultados_P1"
PRINCIPAL = ROOT / "resultados_regimen_n10_a60"
PRECIOS_PRINCIPAL = ROOT / "datos_backtest_m2" / "precios"
VENTANA = ("2007-03-01", "2026-11-06")
CORRIDAS = {"base": ("1.0", "5.0"), "estres": ("5.0", "10.0")}
ESPERADO_P1 = {"base": 0.0310, "estres": 0.0234}  # alfa de la réplica (PARALELO_ETF.md)
KN_CSV = [
    "KN_US_Equity_Core_Returns_Daily.csv",
    "KN_US_Equity_Core_Holdings_Daily.csv",
    "KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv",
]


def instalado(modulo):
    try:
        return importlib.util.find_spec(modulo) is not None
    except ModuleNotFoundError:
        return False


def rutas(variante):
    nombre = "p1" if variante == P1 else variante.name.lower()
    datos = ROOT / f"datos_backtest_{nombre}"
    return datos / "precios", datos / "motor"


def revisar(kn, variante):
    faltas = []
    if not kn.is_dir():
        faltas.append(f"No existe la carpeta KN: {kn}")
    else:
        faltas += [f"Falta {f} en {kn}" for f in KN_CSV if not (kn / f).exists()]
    if not instalado("kaxanuk.backtest_engine"):
        faltas.append("El Backtest Engine no está instalado en este Python (usa el .venv del proyecto)")
    if not instalado("kaxanuk.data_curator"):
        faltas.append("El Data Curator no está instalado en este Python")
    if not os.environ.get("KNBE_API_KEY_KAXANUK"):
        faltas.append("Falta la licencia en la variable KNBE_API_KEY_KAXANUK")
    if not PRECIOS_PRINCIPAL.is_dir():
        faltas.append(f"Falta {PRECIOS_PRINCIPAL} (los precios del Curator del modelo principal)")
    if not (variante / "weights.csv").exists():
        faltas.append(f"Falta {variante / 'weights.csv'} (¿corriste variantes_kn.py?)")
    return faltas


def paso(titulo, args):
    print(f"\n=== {titulo} ===", flush=True)
    subprocess.run([PY, *map(str, args)], cwd=ROOT, check=True)


def correr(kn, variante):
    precios, motor = rutas(variante)
    if not precios.is_dir():
        print(f"Copiando {PRECIOS_PRINCIPAL} -> {precios} (el original no se toca)")
        shutil.copytree(PRECIOS_PRINCIPAL, precios)
    lista = variante / "tickers_para_curator.csv"
    if not lista.exists():
        lista = variante / "etfs_nuevos_para_curator.csv"
    paso("1/4 Precios que falten, con el Data Curator", ["descargar_precios.py", lista, precios, "2000-01-01"])
    paso("2/4 Carpeta de precios del motor",
         ["preparar_motor.py", kn, variante / "weights.csv", precios, motor, "2006-01-01"])
    for i, (corrida, (comision, slippage)) in enumerate(CORRIDAS.items(), start=3):
        paso(f"{i}/4 Backtest Engine, costos {corrida}",
             ["correr_backtest.py", motor, variante, "weights", variante / f"backtest_{corrida}",
              *VENTANA, comision, slippage, "0.02"])


def leer(carpeta):
    f = carpeta / "resumen.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def por_periodo(carpeta):
    """Exceso por periodo con la serie diaria del motor; None si no se puede leer el Excel."""
    try:
        sys.path.insert(0, str(ROOT / "paralelo_etf"))
        import paralelo

        xlsx = next(carpeta.glob("*_backtest_results.xlsx"))
        v = paralelo.sheet(xlsx, "portfolio_bench_total_value", 2)
        return paralelo.stats(v["Total_Portfolio_Value"].astype(float),
                              v["KN_US_Equity_Core_Value"].astype(float), leer(carpeta)["años_valuados"])
    except Exception as error:  # sin openpyxl, sin Excel, etc.
        print(f"  (no se pudo calcular por periodo en {carpeta.name}: {type(error).__name__})")
        return None


def comparar(variante):
    nombre = "P1 refugio ampliado" if variante == P1 else variante.name
    print(f"\n=== {nombre} contra el modelo principal (Backtest Engine, misma ventana) ===")
    filas, veredicto = [], []
    for corrida in CORRIDAS:
        base = leer(PRINCIPAL / f"backtest_{corrida}_r2")
        nuevo = leer(variante / f"backtest_{corrida}")
        if base is None or nuevo is None:
            print(f"Falta el resumen.json de {corrida}; corre primero sin --comparar.")
            return
        for etiqueta, r in (("Principal", base), (nombre, nuevo)):
            p = r["portafolio"]
            filas.append((corrida, etiqueta, p["Annualized Return (CAGR)"], p["Alpha"],
                          p["Max Drawdown"], p["Annualized Volatility"], p["Information Ratio"]))
        kn = nuevo["benchmarks"]["KN_US_Equity_Core"]
        filas.append((corrida, "KN US Equity Core", kn["Annualized Return (CAGR)"], 0.0,
                      kn["Max Drawdown"], kn["Annualized Volatility"], None))
        veredicto.append((corrida, nuevo["portafolio"]["Alpha"] - base["portafolio"]["Alpha"],
                          nuevo["portafolio"]["Max Drawdown"] - base["portafolio"]["Max Drawdown"],
                          nuevo["portafolio"]["Alpha"]))

    print(f"{'costos':<8}{'modelo':<22}{'CAGR':>8}{'alfa':>8}{'caída máx':>11}{'vol':>8}{'IR':>7}")
    for c, n, cagr, alfa, dd, vol, ir in filas:
        ir_txt = f"{ir:7.2f}" if ir is not None else f"{'—':>7}"
        print(f"{c:<8}{n[:21]:<22}{cagr:8.2%}{alfa:+8.2%}{dd:11.2%}{vol:8.2%}{ir_txt}")

    print("\nExceso contra el KN Core por periodo (costos base):")
    pb = por_periodo(PRINCIPAL / "backtest_base_r2")
    pn = por_periodo(variante / "backtest_base")
    periodos_ok = None
    if pb and pn:
        for k in ("Exceso 2007-03 a 2019", "Exceso 2020 a 2026-11"):
            print(f"  {k}: principal {pb[k]:+.2%} · {nombre} {pn[k]:+.2%} ({pn[k] - pb[k]:+.2%})")
        periodos_ok = all(pn[k] > pb[k] for k in ("Exceso 2007-03 a 2019", "Exceso 2020 a 2026-11"))

    print("\nCriterio pre-registrado:")
    for corrida, d_alfa, d_dd, alfa in veredicto:
        extra = f"; la réplica esperaba {ESPERADO_P1[corrida]:+.2%}" if variante == P1 else ""
        print(f"  {corrida}: alfa {alfa:+.2%} ({d_alfa:+.2%} contra el principal{extra}), caída máx. {d_dd:+.2%}")
    sube = all(d > 0 for _, d, _, _ in veredicto)
    dd_ok = all(d >= -0.02 for _, _, d, _ in veredicto)
    print(f"  1. Sube el exceso en 2007–2019 y en 2020–2026: "
          f"{'sí' if periodos_ok else ('NO' if periodos_ok is False else 'sin dato')}")
    print(f"  2. La caída máxima no empeora más de 2 puntos: {'sí' if dd_ok else 'NO'}")
    print(f"  3. Arriba del principal en base y en estrés: {'sí' if sube else 'NO'}")
    pasa = sube and dd_ok and periodos_ok is not False
    print(f"\n  => {nombre}: {'MEJORA al principal en el motor oficial' if pasa else 'NO mejora: el principal se queda'}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return
    kn = Path(args[0]).resolve()
    variante = Path(args[1]).resolve() if len(args) > 1 else P1
    if "--comparar" not in sys.argv:
        faltas = revisar(kn, variante)
        if faltas:
            print("No se corrió nada. Falta:")
            print("\n".join(f"  - {f}" for f in faltas))
            sys.exit(1)
        correr(kn, variante)
    comparar(variante)


if __name__ == "__main__":
    main()
