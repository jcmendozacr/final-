"""Núcleo ETF + satélite de momentum en acciones del KN US Equity Core.

Lógica económica (escrita antes del backtest): las acciones que más subieron en los últimos
12 meses, sin contar el último, tienden a seguir rindiendo más unos meses (Jegadeesh y Titman,
1993). Un núcleo en un ETF de mercado mantiene la beta cerca de 1 frente al benchmark; el
satélite busca el alfa.

Reglas:
- Núcleo: 70% en SPY.
- Satélite: 30% en las 20 acciones con mayor momentum 12-1 entre las 300 de mayor peso del
  KN US Equity Core en la fecha de la señal (miembros a la fecha, sin sesgo de supervivencia),
  1.5% cada una.
- Señal al cierre de fin de mes; se opera el día hábil siguiente.

Uso:
    .venv/bin/python nucleo_satelite.py <carpeta con los CSV de KaxaNuk> [carpeta de salida] [primera señal] [reconstruir-1999]

La carpeta de datos debe tener KN_US_Equity_Core_Holdings_Daily.csv,
KN_US_Equity_Core_Returns_Daily.csv y KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv.

Escribe en la carpeta de salida (por omisión resultados_nucleo_satelite/):
- weights.csv: formato horizontal del Backtest Engine (Ticker + una columna por fecha).
- tickers_para_curator.csv: cada ticker que el motor necesita con precios, y desde qué fecha.
- metricas_exploratorias.csv: la prueba rápida contra el KN Core (no es el backtest oficial).
"""

import sys
from decimal import ROUND_DOWN, Decimal
from pathlib import Path

import numpy as np
import pandas as pd

CORE_ETF = "SPY"
CORE_WEIGHT = Decimal("0.70")
N_STOCKS = 20
UNIVERSE_SIZE = 300
STOCK_WEIGHT = ((Decimal(1) - CORE_WEIGHT) / N_STOCKS).quantize(Decimal("0.000001"), ROUND_DOWN)
FIRST_SIGNAL = pd.Timestamp("2008-12-31")
COST = 0.0010
PERIODS = [
    ("2009-01-01", "2018-12-31", "diseno_2009_2018"),
    ("2019-01-01", "2099-12-31", "prueba_2019_hoy"),
]


def load(data_dir):
    core = pd.read_csv(data_dir / "KN_US_Equity_Core_Returns_Daily.csv", index_col=0)["return"]
    core.index = pd.to_datetime(core.index)
    excess = pd.read_csv(data_dir / "KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv", index_col=0)
    excess.index = pd.to_datetime(excess.index)
    holdings = pd.read_csv(data_dir / "KN_US_Equity_Core_Holdings_Daily.csv", index_col=0)
    holdings.index = pd.to_datetime(holdings.index)
    dates = excess.index.intersection(core.index).intersection(holdings.index)
    tickers = excess.columns.intersection(holdings.columns)
    return (
        core.loc[dates],
        excess.loc[dates, tickers].astype("float32"),
        holdings.loc[dates, tickers].astype("float32"),
    )


def total_returns(core, excess, holdings):
    """Excess returns plus the bill rate implied by the index itself."""
    implied = core - (holdings.shift(1) * excess.fillna(0)).sum(axis=1)
    implied.iloc[0] = 0
    bill = implied.rolling(21, min_periods=1).median()
    return excess.add(bill, axis=0)


def signals(returns, holdings):
    log_cum = np.log1p(returns.fillna(0).clip(lower=-0.99)).cumsum()
    # Only the first 252 rows of the table lack a lagged value; there the window starts at the
    # first return available (251 days for the December 1999 signal, one short of 252).
    momentum = log_cum.shift(21) - log_cum.shift(252).fillna(0)
    has_history = returns.notna().rolling(252).sum() >= 240
    dates = returns.index
    month_ends = pd.Series(dates, index=dates).groupby([dates.year, dates.month]).max()
    picks = {}
    for signal_date in month_ends[month_ends >= FIRST_SIGNAL]:
        next_days = dates[dates > signal_date]
        if len(next_days) == 0:
            continue
        weights_today = holdings.loc[signal_date]
        eligible = weights_today[weights_today > 0].nlargest(UNIVERSE_SIZE).index
        scores = momentum.loc[signal_date, eligible][has_history.loc[signal_date, eligible]].dropna()
        if len(scores) >= N_STOCKS:
            picks[next_days[0]] = list(scores.nlargest(N_STOCKS).index)
    return picks


def write_weights(picks, out_dir):
    trade_dates = sorted(picks)
    tickers = sorted({CORE_ETF, *(t for names in picks.values() for t in names)})
    table = pd.DataFrame("0.000000", index=tickers, columns=[d.strftime("%Y-%m-%d") for d in trade_dates])
    for date in trade_dates:
        column = date.strftime("%Y-%m-%d")
        table.loc[CORE_ETF, column] = str(CORE_WEIGHT.quantize(Decimal("0.000001")))
        for name in picks[date]:
            table.loc[name, column] = str(STOCK_WEIGHT)
    total = CORE_WEIGHT + STOCK_WEIGHT * N_STOCKS
    assert total <= 1, total
    table.index.name = "Ticker"
    table.to_csv(out_dir / "weights.csv")
    first_use = {}
    for date in trade_dates:
        for name in picks[date]:
            first_use.setdefault(name, date)
    rows = [(CORE_ETF, trade_dates[0].date(), "ETF núcleo")]
    rows += [
        (name, first_use[name].date(), "revisar en Yahoo: termina en dígito" if name[-1].isdigit() else "")
        for name in sorted(first_use)
    ]
    pd.DataFrame(rows, columns=["ticker", "primer_uso", "nota"]).to_csv(
        out_dir / "tickers_para_curator.csv", index=False
    )
    return table


def simulate(picks, returns, core):
    dates = returns.index[returns.index >= min(picks)]
    satellite = pd.Series(0.0, index=dates)
    current = None
    for date in dates:
        if date in picks:
            new = pd.Series(1.0 / N_STOCKS, index=picks[date])
            old = current if current is not None else pd.Series(dtype=float)
            satellite.loc[date] -= COST * new.sub(old, fill_value=0).abs().sum()
            current = new
        day = returns.loc[date, current.index].fillna(0)
        satellite.loc[date] += (current * day).sum()
        current = current * (1 + day)
        current = current / current.sum()
    weight = float(1 - CORE_WEIGHT)
    return (1 - weight) * core.loc[dates] + weight * satellite, core.loc[dates]


def metrics(book, bench):
    years = len(book) / 252
    cagr = (1 + book).prod() ** (1 / years) - 1
    bench_cagr = (1 + bench).prod() ** (1 / years) - 1
    equity = (1 + book).cumprod()
    beta = np.cov(book, bench)[0, 1] / bench.var()
    active = book - bench
    tracking = active.std() * np.sqrt(252)
    return {
        "cagr": cagr,
        "cagr_kn_core": bench_cagr,
        "volatilidad": book.std() * np.sqrt(252),
        "caida_maxima": (equity / equity.cummax() - 1).min(),
        "beta": beta,
        "alfa_anual": (book.mean() - beta * bench.mean()) * 252,
        "tracking_error": tracking,
        "information_ratio": active.mean() * 252 / tracking,
    }


def reconstructed_history(data_dir, returns, holdings, core):
    """Prepend stock returns for the days before KaxaNuk's stock returns begin (1999).

    Between reconstitutions a cap-weighted index's weights move with prices, so a member's return
    is (weight today / weight yesterday) x (1 + index return) - 1. Checked on 2000 against the real
    returns: daily correlation 0.94, median absolute error 6 bp; the top 20 by momentum agree on 11
    of 20. Only the signals of 2000 lean on it; no simulated day uses it.
    """
    all_core = pd.read_csv(data_dir / "KN_US_Equity_Core_Returns_Daily.csv", index_col=0)["return"]
    all_core.index = pd.to_datetime(all_core.index)
    all_holdings = pd.read_csv(data_dir / "KN_US_Equity_Core_Holdings_Daily.csv", index_col=0)
    all_holdings.index = pd.to_datetime(all_holdings.index)
    early = all_holdings.index[(all_holdings.index < returns.index[0]) & all_holdings.index.isin(all_core.index)]
    weights = all_holdings.loc[:, returns.columns].astype("float32")
    ratio = (weights / weights.shift(1)).loc[early]
    early_returns = ratio.mul(1 + all_core.loc[early], axis=0) - 1
    early_returns = early_returns.where((weights.loc[early] > 0) & (weights.shift(1).loc[early] > 0))
    return (
        pd.concat([early_returns.astype("float32"), returns]),
        pd.concat([weights.loc[early], holdings]),
        pd.concat([all_core.loc[early], core]),
    )


def main():
    data_dir = Path(sys.argv[1])
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("resultados_nucleo_satelite")
    out_dir.mkdir(parents=True, exist_ok=True)
    global FIRST_SIGNAL
    if len(sys.argv) > 3:
        FIRST_SIGNAL = pd.Timestamp(sys.argv[3])
    core, excess, holdings = load(data_dir)
    returns = total_returns(core, excess, holdings)
    if len(sys.argv) > 4 and sys.argv[4] == "reconstruir-1999":
        returns, holdings, core = reconstructed_history(data_dir, returns, holdings, core)
    picks = signals(returns, holdings)
    table = write_weights(picks, out_dir)
    book, bench = simulate(picks, returns, core)
    rows = {label: metrics(book[a:b], bench[a:b]) for a, b, label in PERIODS}
    pd.DataFrame(rows).T.to_csv(out_dir / "metricas_exploratorias.csv", float_format="%.4f")
    sums = table.astype(float).sum()
    print(f"weights.csv: {table.shape[0]} tickers x {table.shape[1]} rebalanceos, "
          f"{table.columns[0]} -> {table.columns[-1]}, suma por fecha {sums.min():.6f}-{sums.max():.6f}")
    print(pd.DataFrame(rows).T.round(3).to_string())


if __name__ == "__main__":
    main()
