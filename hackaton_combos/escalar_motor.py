"""Copia de la carpeta del motor con los precios divididos entre 100 (datos_backtest_combo_x01/motor).

Con 20% en una sola acción y niveles de precio altos, el redondeo a acciones enteras dejaba el efectivo
negativo ("Cash error") y el motor dejaba de valuar. Dividir todos los precios entre 100 no cambia ningún
rendimiento. variante_okrus_20pct.py agrega después, en la misma carpeta, los precios de las acciones
nuevas (índices de KaxaNuk que empiezan en 1).

Uso:
    python hackaton_combos/escalar_motor.py hackaton_combos/C2_20pct/weights.csv
"""

import os
import sys

import pandas as pd

SRC, DST = "datos_backtest_combo/motor", "datos_backtest_combo_x01/motor"
os.makedirs(DST, exist_ok=True)
w = pd.read_csv(sys.argv[1], index_col=0)
need = set(w.index) | {"KN_US_Equity_Core", "SPY"}
for t in sorted(need):
    d = pd.read_csv(f"{SRC}/{t}.csv")
    cols = [c for c in d.columns if c not in ("m_date", "m_volume_split_adjusted")]
    d[cols] = d[cols] / 100
    d.to_csv(f"{DST}/{t}.csv", index=False, float_format="%.8f")
print(len(need), "archivos")
