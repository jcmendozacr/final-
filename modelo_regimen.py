"""Modelo de régimen M2: identifica el estado del mercado y aplica la estrategia de ese estado.

Señales, a fin de mes:
- Tendencia (Faber, 2007): SPY por encima o igual a su promedio de 10 cierres de fin de mes.
- Canario (Keller y Keuning): momentum 13612 de TIP >= 0, el promedio de sus rendimientos a 1, 3,
  6 y 12 meses.

Regímenes y estrategia:
- Alcista (tendencia arriba y canario OK): 40% SPY + 60% en las 20 acciones de mayor momentum 12-1
  entre las 300 de mayor peso del KN US Equity Core (3% cada una).
- Mixto (solo una señal en alerta): 70% SPY + 30% en esas 20 acciones (1.5% cada una).
- Caída (las dos en alerta): 100% en el mejor de SHY o IEF según su momentum 13612.

Se opera el día hábil siguiente a la señal. Las acciones se eligen con nucleo_satelite.signals().

Uso:
    .venv/bin/python modelo_regimen.py <CSV de KaxaNuk> <carpeta de precios ETF> <carpeta de salida> \
        [umbral de volatilidad, p. ej. 0.35, o "no"] [número de acciones, 20] [% en acciones en alcista, 0.60]

La carpeta de precios ETF necesita SPY.csv, TIP.csv, SHY.csv e IEF.csv del Data Curator.
Escribe weights.csv (horizontal, Ticker + una columna por fecha), regimenes.csv y
tickers_para_curator.csv.
"""

import sys
from decimal import ROUND_DOWN, Decimal
from pathlib import Path

import pandas as pd

import nucleo_satelite

FIRST_SIGNAL = pd.Timestamp("2006-01-31")
PRICE = "m_close_dividend_and_split_adjusted"
STOCKS = 20
WEIGHTS = {
    "alcista": (Decimal("0.40"), Decimal("0.60")),
    "mixto": (Decimal("0.70"), Decimal("0.30")),
}


def momentum_13612(month_end_prices):
    """Average of the 1, 3, 6 and 12 month total returns."""
    return sum(month_end_prices / month_end_prices.shift(k) - 1 for k in (1, 3, 6, 12)) / 4


def scaled(base, exposure):
    """The regime's book with its stock part (SPY and the 20 stocks) at `exposure`, the rest in SHY."""
    if exposure == 1:
        return dict(base)
    weights = {t: w for t, w in base.items() if t in ("SHY", "IEF") and len(base) == 1}
    if weights:
        return weights
    return {"SHY": Decimal("1.000000")}


def add_volatility_switch(book, spy, dates, threshold):
    """Daily switch: when SPY's 20-day volatility, annualised, closes above `threshold`, the next
    trading day the stock part of the book goes to SHY; when it closes back at or below, the next
    trading day the regime's book comes back. Volatility managed portfolios: Moreira and Muir (2017).
    """
    volatility = spy.pct_change().rolling(20).std() * (252 ** 0.5)
    monthly = sorted(book)
    switched = {}
    events = []
    exposure = 1
    pending = None
    base = None
    for day in dates[dates >= monthly[0]]:
        if day in book:
            base = book[day]
            if pending is not None:
                exposure, pending = pending, None
            switched[day] = scaled(base, exposure)
        elif pending is not None:
            exposure, pending = pending, None
            if not (len(base) == 1 and next(iter(base)) in ("SHY", "IEF")):
                switched[day] = scaled(base, exposure)
                events.append((day.date(), "sale a SHY" if exposure == 0 else "regresa"))
        wanted = 0 if volatility.loc[day] > threshold else 1
        if wanted != exposure:
            pending = wanted
    return switched, events


def main():
    kn_dir, etf_dir, out_dir = (Path(p) for p in sys.argv[1:4])
    out_dir.mkdir(parents=True, exist_ok=True)
    nucleo_satelite.FIRST_SIGNAL = FIRST_SIGNAL
    core, excess, holdings = nucleo_satelite.load(kn_dir)
    returns = nucleo_satelite.total_returns(core, excess, holdings)
    global STOCKS
    if len(sys.argv) > 5:
        STOCKS = int(sys.argv[5])
    if len(sys.argv) > 6:
        satellite = Decimal(sys.argv[6])
        WEIGHTS["alcista"] = (Decimal(1) - satellite, satellite)
    nucleo_satelite.N_STOCKS = STOCKS
    picks = nucleo_satelite.signals(returns, holdings)

    prices = pd.concat(
        {t: pd.read_csv(etf_dir / f"{t}.csv", index_col=0, parse_dates=True)[PRICE] for t in ["SPY", "TIP", "SHY", "IEF"]},
        axis=1,
    )
    dates = returns.index.intersection(prices.index)
    month_ends = pd.Series(dates, index=dates).groupby([dates.year, dates.month]).max()
    monthly = prices.reindex(month_ends.values)
    momentum = momentum_13612(monthly)
    trend = monthly["SPY"].rolling(10).mean()

    rows = []
    book = {}
    for signal_date in month_ends.values:
        later = dates[dates > signal_date]
        if len(later) == 0 or later[0] not in picks:
            continue
        trade_date = later[0]
        signals = momentum.loc[signal_date]
        if pd.isna(signals[["TIP", "SHY", "IEF"]]).any() or pd.isna(trend.loc[signal_date]):
            continue
        up = monthly.loc[signal_date, "SPY"] >= trend.loc[signal_date]
        canary_ok = signals["TIP"] >= 0
        regime = "alcista" if up and canary_ok else ("caida" if not up and not canary_ok else "mixto")
        if regime == "caida":
            refuge = "IEF" if signals["IEF"] > signals["SHY"] else "SHY"
            weights = {refuge: Decimal("1.000000")}
        else:
            core_weight, satellite_weight = WEIGHTS[regime]
            each = (satellite_weight / STOCKS).quantize(Decimal("0.000001"), ROUND_DOWN)
            weights = {"SPY": core_weight, **{name: each for name in picks[trade_date]}}
        assert sum(weights.values()) <= 1
        book[trade_date] = weights
        rows.append((pd.Timestamp(signal_date).date(), trade_date.date(), regime, bool(up), bool(canary_ok)))

    switch = float(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] != "no" else None
    switches = []
    if switch is not None:
        book, switches = add_volatility_switch(book, prices["SPY"].reindex(dates), dates, switch)

    columns = sorted(book)
    tickers = sorted({t for weights in book.values() for t in weights})
    table = pd.DataFrame("0.000000", index=tickers, columns=[d.strftime("%Y-%m-%d") for d in columns])
    for date in columns:
        for ticker, weight in book[date].items():
            table.loc[ticker, date.strftime("%Y-%m-%d")] = str(weight.quantize(Decimal("0.000001")))
    table.index.name = "Ticker"
    table.to_csv(out_dir / "weights.csv")
    pd.DataFrame(rows, columns=["señal", "operación", "régimen", "tendencia_arriba", "canario_ok"]).to_csv(
        out_dir / "regimenes.csv", index=False
    )
    first_use = {}
    for date in columns:
        for ticker in book[date]:
            first_use.setdefault(ticker, date.date())
    pd.DataFrame(sorted(first_use.items()), columns=["ticker", "primer_uso"]).assign(nota="").to_csv(
        out_dir / "tickers_para_curator.csv", index=False
    )
    if switch is not None:
        pd.DataFrame(switches, columns=["fecha", "interruptor"]).to_csv(out_dir / "interruptor.csv", index=False)
        print(f"interruptor de volatilidad {switch:.0%}: {len(switches)} cambios intermensuales")
    counts = pd.Series([r[2] for r in rows]).value_counts().to_dict()
    sums = table.astype(float).sum()
    print(f"weights.csv: {len(tickers)} tickers x {len(columns)} rebalanceos, {table.columns[0]} -> {table.columns[-1]}, "
          f"suma {sums.min():.6f}-{sums.max():.6f} | meses por régimen {counts}")


if __name__ == "__main__":
    main()
