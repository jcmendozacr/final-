"""
DIAGNOSTICO DE DATOS - revisa que los CSV del Data Curator esten sanos.
USO:  python diagnostico.py .
Revisa: fechas, dias repetidos (precio sin cambio), saltos raros,
volatilidad y correlacion con SPY (los sectores deberian tener 0.6-0.95).
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

COL = "m_close_dividend_and_split_adjusted"
carpeta = Path(sys.argv[1] if len(sys.argv) > 1 else ".")

archivos = {}
for p in carpeta.rglob("*.csv"):
    if "resultados" in str(p):
        continue
    t = p.stem.upper()
    if t not in archivos or p.stat().st_mtime > archivos[t].stat().st_mtime:
        archivos[t] = p

series, filas = {}, []
for t, p in sorted(archivos.items()):
    try:
        df = pd.read_csv(p, parse_dates=["m_date"]).set_index("m_date").sort_index()
        s = df[COL]
    except Exception as e:
        print(f"{t}: no pude leerlo ({e})"); continue
    series[t] = s
    r = s.pct_change().dropna()
    filas.append({
        "ticker": t, "carpeta": p.parent.name, "filas": len(s),
        "inicio": s.index.min().date(), "fin": s.index.max().date(),
        "fechas_dup": int(s.index.duplicated().sum()),
        "vacios": int(s.isna().sum()),
        "% dias sin cambio": f"{(r == 0).mean():.1%}",
        "max salto diario": f"{r.abs().max():.1%}",
        "vol anual": f"{r.std() * np.sqrt(252):.1%}",
    })

tabla = pd.DataFrame(filas).set_index("ticker")
if "SPY" in series:
    px = pd.DataFrame(series)
    rets = px.pct_change()
    tabla["corr con SPY"] = rets.corr()["SPY"].reindex(tabla.index).map("{:.2f}".format)
    # correlacion si movemos un dia (detecta fechas desfasadas)
    tabla["corr SPY (+1 dia)"] = [f"{rets[t].corr(rets['SPY'].shift(1)):.2f}" for t in tabla.index]
    comunes = px.dropna().index
    print(f"Dias en comun entre TODOS los archivos: {len(comunes)} "
          f"({comunes.min().date()} a {comunes.max().date()})")
pd.set_option("display.width", 200)
print(tabla.to_string())
print("\nQUE BUSCAR:")
print(" - Sectores con 'corr con SPY' menor a 0.5  -> datos sospechosos")
print(" - 'corr SPY (+1 dia)' mayor que 'corr con SPY' -> fechas desfasadas un dia")
print(" - '% dias sin cambio' mayor a 2%  -> precios repetidos / huecos")
print(" - 'max salto diario' mayor a 25%  -> error en el ajuste de precios")
