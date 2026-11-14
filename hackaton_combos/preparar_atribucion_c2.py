"""Entradas de Attribution Analysis para el modelo principal v2 (C2 confirmada).

Igual que preparar_atribucion.py, con una diferencia: el modelo tiene ETF sectoriales en vez de SPY.
- Cada ETF sectorial se abre en las acciones del KN US Equity Core de su sector KN ese día, con sus
  pesos del índice: XLK→Technology, XLF→Financials, XLE→Energy, XLY→Consumer_Discretionary,
  XLI→Industrials, XLB→Materials (aproximación: los SPDR y los sectores de KN no son idénticos).
- SPY, si apareciera, se abre en todo el KN Core.
- Los refugios (SHY, IEF, TIP) y la reserva quedan como efectivo.
- Pesos movidos un día (el peso al cierre de t−1 gana el rendimiento de t).

Uso:
    python hackaton_combos/preparar_atribucion_c2.py <KN> <KN_sectores> <Daily_Weights.csv> <salida>
"""

import sys
from pathlib import Path

import pandas as pd

FACTORS = [
    "Market", "Size", "Value", "Momentum", "Beta", "Residual_Volatility",
    "Energy", "Materials", "Industrials", "Consumer_Discretionary", "Consumer_Staples",
    "Health_Care", "Financials", "Technology", "Communication", "Utilities", "Real_Estate",
]
ETF_SECTOR = {"XLK": "Technology", "XLF": "Financials", "XLE": "Energy",
              "XLY": "Consumer_Discretionary", "XLI": "Industrials", "XLB": "Materials"}
CASH_LIKE = {"SHY", "IEF", "TIP", "CASH_RESERVE", "KN_US_Equity_Core"}


def read_dated(path):
    frame = pd.read_csv(path, index_col=0)
    frame.index = pd.to_datetime(frame.index)
    return frame


def main():
    kn_dir, sect_dir, daily_file, out_dir = (Path(p) for p in sys.argv[1:5])
    factor_dir = kn_dir if (kn_dir / "KN_US_Equity_Factor_Market_Daily.csv").exists() else sect_dir
    inputs = out_dir / "Input"
    for sub in ["Portfolios", "Benchmark_Portfolios", "Data", "Factor_Models"]:
        (inputs / sub).mkdir(parents=True, exist_ok=True)

    book = read_dated(daily_file)
    book = book[[c for c in book.columns if not str(c).startswith("Unnamed")]].fillna(0)
    dates = book.index
    start = dates[0] - pd.Timedelta(days=10)
    holdings = read_dated(kn_dir / "KN_US_Equity_Core_Holdings_Daily.csv")[start:dates[-1]]
    holdings = holdings.loc[:, (holdings > 0).any()]
    core = read_dated(kn_dir / "KN_US_Equity_Core_Returns_Daily.csv")["return"]

    stocks = [c for c in book.columns if c not in CASH_LIKE | set(ETF_SECTOR) | {"SPY"}]
    tickers = sorted(set(holdings.columns) | set(stocks))
    raw = holdings.reindex(index=dates, columns=tickers).fillna(0)
    held = raw.div(raw.sum(axis=1), axis=0) * (1 - 1e-5)

    portfolio = book[stocks].reindex(columns=tickers).fillna(0)
    if "SPY" in book.columns:
        portfolio += held.mul(book["SPY"], axis=0)
    for etf, sector in ETF_SECTOR.items():
        if etf not in book.columns or not (book[etf] > 0).any():
            continue
        member = read_dated(sect_dir / f"KN_US_Equity_Factor_{sector}_Daily.csv")
        member = member.reindex(index=dates, columns=tickers).notna()
        w = raw.where(member, 0)
        w = w.div(w.sum(axis=1).replace(0, float("nan")), axis=0).fillna(0)
        portfolio += w.mul(book[etf], axis=0)
        print(f"{etf} → {sector}: días con peso {(book[etf] > 0).sum()}", flush=True)

    portfolio_held = portfolio.shift(1).iloc[1:]
    benchmark_held = held.shift(1).iloc[1:]
    for frame, name, folder in [(portfolio_held, "portfolio_daily_weights.csv", "Portfolios"),
                                (benchmark_held, "benchmark_daily_weights.csv", "Benchmark_Portfolios")]:
        written = frame.round(8)
        written["CASH"] = (1 - written.sum(axis=1)).round(8).clip(lower=0)
        written.index = written.index.strftime("%Y-%m-%d")
        written.index.name = "date_column"
        written.to_csv(inputs / folder / name, float_format="%.8f")

    returns_file = pd.DataFrame({"KN_US_Equity_Core": core.reindex(portfolio_held.index)})
    returns_file.index = returns_file.index.strftime("%Y-%m-%d")
    returns_file.index.name = "date_column"
    returns_file.to_csv(inputs / "Benchmark_Portfolios" / "benchmark_returns.csv")

    excess = read_dated(kn_dir / "KN_US_Equity_Factor_Total_Excess_Returns_Daily.csv")
    all_h = read_dated(kn_dir / "KN_US_Equity_Core_Holdings_Daily.csv")
    shared = excess.columns.intersection(all_h.columns)
    common = excess.index.intersection(core.index).intersection(all_h.index)
    implied = core.loc[common] - (all_h.loc[common, shared].shift(1) * excess.loc[common, shared].fillna(0)).sum(axis=1)
    bill = implied.rolling(21, min_periods=1).median()
    window = excess.loc[start:dates[-1]]
    missing = []
    for t in tickers:
        if t not in window.columns:
            missing.append(t)
            continue
        s = (window[t] + bill.reindex(window.index)).dropna()
        if s.empty:
            missing.append(t)
            continue
        level = 100 * (1 + s).cumprod()
        pd.DataFrame({"m_date": level.index.strftime("%Y-%m-%d"),
                      "m_close_dividend_and_split_adjusted": level.values}).to_csv(inputs / "Data" / f"{t}.csv", index=False)
    del excess, all_h

    for factor in FACTORS:
        f = read_dated(factor_dir / f"KN_US_Equity_Factor_{factor}_Daily.csv")
        f = f.loc[start:dates[-1], f.columns.intersection(tickers)]
        f.index = f.index.strftime("%Y-%m-%d")
        f.index.name = "date"
        f.to_csv(inputs / "Factor_Models" / f"f_{factor.lower()}.csv", float_format="%.10g")

    sums = portfolio_held.sum(axis=1)
    print(f"tickers {len(tickers)} | días {len(portfolio_held)} | {portfolio_held.index[0].date()} -> {portfolio_held.index[-1].date()}")
    print(f"suma de pesos en acciones: {sums.min():.4f}-{sums.max():.4f} (el resto es efectivo/refugios)")
    held_wo = [t for t in missing if (portfolio_held[t] > 0).any() or (benchmark_held[t] > 0).any()]
    print(f"sin precios: {len(missing)}; con peso y sin precios: {held_wo[:15]}")
    unused = [t for t in missing if t not in held_wo]
    if unused:
        for name in ["Portfolios/portfolio_daily_weights.csv", "Benchmark_Portfolios/benchmark_daily_weights.csv"]:
            table = pd.read_csv(inputs / name, index_col=0)
            table.drop(columns=unused).to_csv(inputs / name, float_format="%.8f")
        for factor in FACTORS:
            path = inputs / "Factor_Models" / f"f_{factor.lower()}.csv"
            table = pd.read_csv(path, index_col=0)
            table.drop(columns=[t for t in unused if t in table.columns]).to_csv(path, float_format="%.10g")


if __name__ == "__main__":
    main()
