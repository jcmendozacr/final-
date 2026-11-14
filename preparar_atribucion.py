"""Arma las cuatro entradas de Attribution Analysis a partir del backtest de núcleo + satélite.

- Portafolio diario: Daily_Weights del Backtest Engine, el SPY abierto en las acciones del KN US
  Equity Core (sus pesos del día), ampliado a todos los miembros del benchmark con peso 0, y movido
  un día (el peso al cierre de t-1 gana el rendimiento de t).
- Benchmark diario: los pesos del KN US Equity Core, movidos un día igual.
- Rendimientos del benchmark: la serie oficial del KN US Equity Core.
- Precios: un índice de rendimiento total por acción, desde los datos de KaxaNuk.
- Factores: los 16 del KN US Equity Factor Model (mercado, 5 estilos, 11 sectores), uno por archivo.

Uso:
    .venv/bin/python preparar_atribucion.py <carpeta con CSV de KaxaNuk> <Daily_Weights.csv> <salida>
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

FACTORS = [
    "Market", "Size", "Value", "Momentum", "Beta", "Residual_Volatility",
    "Energy", "Materials", "Industrials", "Consumer_Discretionary", "Consumer_Staples",
    "Health_Care", "Financials", "Technology", "Communication", "Utilities", "Real_Estate",
]
NOT_STOCKS = {"SPY", "KN_US_Equity_Core", "CASH_RESERVE"}


def read_dated(path, **kwargs):
    frame = pd.read_csv(path, index_col=0, **kwargs)
    frame.index = pd.to_datetime(frame.index)

    return frame


def main():
    kn_dir, daily_file, out_dir = (Path(p) for p in sys.argv[1:4])
    inputs = out_dir / "Input"
    for sub in ["Portfolios", "Benchmark_Portfolios", "Data", "Factor_Models"]:
        (inputs / sub).mkdir(parents=True, exist_ok=True)

    book = read_dated(daily_file)
    book = book[[c for c in book.columns if not str(c).startswith("Unnamed")]]
    dates = book.index
    start = dates[0] - pd.Timedelta(days=10)

    holdings = read_dated(kn_dir / "KN_US_Equity_Core_Holdings_Daily.csv")[start:dates[-1]]
    holdings = holdings.loc[:, (holdings > 0).any()]
    core = read_dated(kn_dir / "KN_US_Equity_Core_Returns_Daily.csv")["return"]

    stocks = [c for c in book.columns if c not in NOT_STOCKS]
    tickers = sorted(set(holdings.columns) | set(stocks))
    raw_held = holdings.reindex(index=dates, columns=tickers).fillna(0)
    # The index's weights are rounded to six places, so a day can sum to 1.00001; scale each day
    # to just under one so neither table reads as leveraged once written to eight places.
    held = raw_held.div(raw_held.sum(axis=1), axis=0) * (1 - 1e-5)

    look_through = held.mul(book["SPY"].fillna(0), axis=0)
    satellite = book[stocks].reindex(columns=tickers).fillna(0)
    portfolio = look_through + satellite

    portfolio_held = portfolio.shift(1).iloc[1:]
    benchmark_held = held.shift(1).iloc[1:]
    for frame, name in [(portfolio_held, "portfolio_daily_weights.csv"), (benchmark_held, "benchmark_daily_weights.csv")]:
        folder = "Portfolios" if name.startswith("portfolio") else "Benchmark_Portfolios"
        written = frame.round(8)
        # The remainder of each day is held as explicit cash, so both tables sum to one once rounded.
        written["CASH"] = (1 - written.sum(axis=1)).round(8).clip(lower=0)
        written.index = written.index.strftime("%Y-%m-%d")
        written.index.name = "date_column"
        written.to_csv(inputs / folder / name, float_format="%.8f")

    returns_file = pd.DataFrame({"KN_US_Equity_Core": core.reindex(portfolio_held.index)})
    returns_file.index = returns_file.index.strftime("%Y-%m-%d")
    returns_file.index.name = "date_column"
    returns_file.to_csv(inputs / "Benchmark_Portfolios" / "benchmark_returns.csv")

    excess = read_dated(kn_dir / "KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv")
    all_holdings = read_dated(kn_dir / "KN_US_Equity_Core_Holdings_Daily.csv")
    shared = excess.columns.intersection(all_holdings.columns)
    common = excess.index.intersection(core.index).intersection(all_holdings.index)
    implied = core.loc[common] - (all_holdings.loc[common, shared].shift(1) * excess.loc[common, shared].fillna(0)).sum(axis=1)
    bill = implied.rolling(21, min_periods=1).median()
    window = excess.loc[start:dates[-1]]
    missing_prices = []
    for ticker in tickers:
        if ticker not in window.columns:
            missing_prices.append(ticker)
            continue
        series = (window[ticker] + bill.reindex(window.index)).dropna()
        if series.empty:
            missing_prices.append(ticker)
            continue
        level = 100 * (1 + series).cumprod()
        pd.DataFrame({
            "m_date": level.index.strftime("%Y-%m-%d"),
            "m_close_dividend_and_split_adjusted": level.values,
        }).to_csv(inputs / "Data" / f"{ticker}.csv", index=False)
    del excess, all_holdings

    for factor in FACTORS:
        frame = read_dated(kn_dir / f"KN_US_Equity_Factor_{factor}_Daily.csv")
        frame = frame.loc[start:dates[-1], frame.columns.intersection(tickers)]
        frame.index = frame.index.strftime("%Y-%m-%d")
        frame.index.name = "date"
        frame.to_csv(inputs / "Factor_Models" / f"f_{factor.lower()}.csv", float_format="%.10g")
        print(f"factor {factor}: {frame.shape[1]} de {len(tickers)} tickers", flush=True)

    sums = portfolio_held.sum(axis=1)
    print(f"tickers {len(tickers)} | días {len(portfolio_held)} | {portfolio_held.index[0].date()} -> {portfolio_held.index[-1].date()}")
    print(f"suma de pesos del portafolio: {sums.min():.4f}-{sums.max():.4f} | benchmark: {benchmark_held.sum(axis=1).min():.4f}-{benchmark_held.sum(axis=1).max():.4f}")
    print(f"sin precios: {len(missing_prices)} {missing_prices[:15]}")
    held_without_price = [t for t in missing_prices if (portfolio_held[t] > 0).any() or (benchmark_held[t] > 0).any()]
    print(f"con peso y sin precios: {held_without_price[:15]}")
    # A name never held by either table and with no price is dropped, so every column has a file.
    unused = [t for t in missing_prices if t not in held_without_price]
    if unused:
        for name in ["Portfolios/portfolio_daily_weights.csv", "Benchmark_Portfolios/benchmark_daily_weights.csv"]:
            table = pd.read_csv(inputs / name, index_col=0)
            table.drop(columns=unused).to_csv(inputs / name, float_format="%.8f")
        for factor in FACTORS:
            path = inputs / "Factor_Models" / f"f_{factor.lower()}.csv"
            table = pd.read_csv(path, index_col=0)
            table.drop(columns=[t for t in unused if t in table.columns]).to_csv(path, float_format="%.10g")
        print(f"quitados por no tener peso ni precio: {unused}")


if __name__ == "__main__":
    main()
