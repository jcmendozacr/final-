"""Arma la carpeta de precios que lee el Backtest Engine.

Por cada ticker del weights.csv:
- Usa el CSV que bajó el Data Curator (Yahoo) solo si cubre todo el tiempo en que se tiene la
  acción y sus rendimientos diarios se parecen a los de KaxaNuk para ese ticker (correlación de al
  menos MIN_CORRELATION). Así se descarta un ticker que Yahoo asigna hoy a otra empresa.
- Si no, construye su índice de rendimiento total con los datos de KaxaNuk (exceso de rendimiento
  + tasa implícita); la serie termina cuando el dato de KaxaNuk termina, y el motor vende ahí.
Además escribe KN_US_Equity_Core.csv, el benchmark, desde su serie de rendimientos, y un registro
de qué fuente se usó para cada ticker y por qué.

Uso:
    .venv/bin/python preparar_motor.py <carpeta con CSV de KaxaNuk> <weights.csv> <precios curator> <salida> [inicio]
"""

import shutil
import sys
from pathlib import Path

import pandas as pd

COLUMNS = [
    "m_date",
    "m_open_split_adjusted",
    "m_high_split_adjusted",
    "m_low_split_adjusted",
    "m_close_split_adjusted",
    "m_volume_split_adjusted",
    "m_close_dividend_and_split_adjusted",
]
MIN_CORRELATION = 0.9
PRICE = "m_close_dividend_and_split_adjusted"


def index_frame(returns):
    """A price index starting at 100, with every price column equal to it."""
    level = 100 * (1 + returns.fillna(0)).cumprod()
    level = level[returns.notna().cumsum() > 0]
    level = level[:returns.last_valid_index()]
    frame = pd.DataFrame({"m_date": level.index.strftime("%Y-%m-%d")})
    for column in COLUMNS[1:]:
        frame[column] = level.values
    frame["m_volume_split_adjusted"] = 1_000_000_000

    return frame[COLUMNS]


def holding_spans(weights):
    """First trade date and the date the position can be closed, for each ticker."""
    dates = pd.to_datetime(weights.columns)
    spans = {}
    for ticker, row in weights.iterrows():
        held = [i for i, value in enumerate(row.values) if value > 0]
        if not held:
            continue
        last = held[-1]
        until = dates[last + 1] if last + 1 < len(dates) else dates[-1] + pd.Timedelta(days=31)
        spans[ticker] = (dates[held[0]], until)

    return spans


def read_dated(path):
    frame = pd.read_csv(path, index_col=0)
    frame.index = pd.to_datetime(frame.index)

    return frame


def main():
    kn_dir, weights_file, curator_dir, out_dir = (Path(p) for p in sys.argv[1:5])
    start = sys.argv[5] if len(sys.argv) > 5 else "2000-01-01"
    out_dir.mkdir(parents=True, exist_ok=True)
    weights = pd.read_csv(weights_file, index_col=0)
    spans = holding_spans(weights)

    core = read_dated(kn_dir / "KN_US_Equity_Core_Returns_Daily.csv")["return"]
    index_frame(core[start:]).to_csv(out_dir / "KN_US_Equity_Core.csv", index=False)

    excess = read_dated(kn_dir / "KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv")
    holdings = read_dated(kn_dir / "KN_US_Equity_Core_Holdings_Daily.csv")
    dates = excess.index.intersection(core.index).intersection(holdings.index)
    shared = excess.columns.intersection(holdings.columns)
    implied = core.loc[dates] - (holdings.loc[dates, shared].shift(1) * excess.loc[dates, shared].fillna(0)).sum(axis=1)
    bill = implied.rolling(21, min_periods=1).median()
    del holdings

    log = []
    for ticker in weights.index:
        first, until = spans.get(ticker, (None, None))
        source = curator_dir / f"{ticker}.csv"
        kaxanuk = (excess[ticker] + bill) if ticker in excess.columns else None
        reason = ""
        if ticker == "SPY":
            reason = "ETF del núcleo"
        elif not source.exists():
            reason = "Yahoo no lo tiene"
        else:
            yahoo = pd.read_csv(source, usecols=["m_date", PRICE])
            yahoo.index = pd.to_datetime(yahoo["m_date"])
            if yahoo.index[0] > first or yahoo.index[-1] < min(until, yahoo.index[-1] if kaxanuk is None else kaxanuk.last_valid_index()) - pd.Timedelta(days=5):
                reason = "Yahoo no cubre todo el periodo en que se tiene"
            elif kaxanuk is not None:
                window = slice(first - pd.Timedelta(days=60), until)
                pair = pd.concat([yahoo[PRICE].pct_change()[window], kaxanuk[window]], axis=1).dropna()
                correlation = pair.corr().iloc[0, 1] if len(pair) > 20 else float("nan")
                if not correlation >= MIN_CORRELATION:
                    reason = f"Yahoo no coincide con KaxaNuk (correlación {correlation:.2f})"
        if reason in ("", "ETF del núcleo"):
            shutil.copyfile(source, out_dir / f"{ticker}.csv")
            log.append((ticker, "yahoo", reason or "cubre y coincide"))
        elif kaxanuk is None:
            log.append((ticker, "ninguna", reason + "; sin datos de KaxaNuk"))
        else:
            index_frame(kaxanuk[start:]).to_csv(out_dir / f"{ticker}.csv", index=False)
            log.append((ticker, "kaxanuk", reason))

    table = pd.DataFrame(log, columns=["ticker", "fuente", "motivo"])
    table.to_csv(out_dir.parent / "fuente_de_precios.csv", index=False)
    print(table["fuente"].value_counts().to_string())
    print(table[table["fuente"] != "yahoo"]["motivo"].str.split(" \\(").str[0].value_counts().to_string())


if __name__ == "__main__":
    main()
