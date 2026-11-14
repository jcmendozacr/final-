"""Descarga con el Data Curator (Yahoo Finance) los precios que pide el weights.csv.

Uso:
    .venv/bin/python descargar_precios.py <tickers.csv> <carpeta de salida> [inicio] [fin]

Escribe un <TICKER>.csv por identificador y, al final, la lista de los que no se escribieron.
"""

import datetime
import logging
import sys
from pathlib import Path

import pandas as pd

import kaxanuk.data_curator
import kaxanuk.data_curator.data_blocks.market_daily
import kaxanuk.data_curator.entities
import kaxanuk.data_curator.output_handlers
import kaxanuk.data_curator_extensions.yahoo_finance

COLUMNS = (
    "m_date",
    "m_open_split_adjusted",
    "m_high_split_adjusted",
    "m_low_split_adjusted",
    "m_close_split_adjusted",
    "m_volume_split_adjusted",
    "m_close_dividend_and_split_adjusted",
)
BATCH = 25


class Collector(logging.Handler):
    """Keep every error the curator logs, since main() returns normally after a refused batch."""

    def __init__(self):
        super().__init__(level=logging.ERROR)
        self.messages = []

    def emit(self, record):
        self.messages.append(record.getMessage())


def main():
    tickers_file = Path(sys.argv[1])
    out_dir = Path(sys.argv[2])
    start = datetime.date.fromisoformat(sys.argv[3] if len(sys.argv) > 3 else "2018-01-01")
    end = datetime.date.fromisoformat(sys.argv[4] if len(sys.argv) > 4 else datetime.date.today().isoformat())
    out_dir.mkdir(parents=True, exist_ok=True)
    tickers = list(dict.fromkeys(pd.read_csv(tickers_file)["ticker"].astype(str)))
    pending = [t for t in tickers if not (out_dir / f"{t}.csv").exists()]
    collector = Collector()
    logging.getLogger("kaxanuk").addHandler(collector)
    provider = kaxanuk.data_curator_extensions.yahoo_finance.YahooFinance()
    market_block = kaxanuk.data_curator.data_blocks.market_daily.MarketDailyDataBlock
    for first in range(0, len(pending), BATCH):
        batch = tuple(pending[first:first + BATCH])
        configuration = kaxanuk.data_curator.entities.Configuration(
            start_date=start,
            end_date=end,
            period="annual",
            identifiers=batch,
            columns=COLUMNS,
        )
        kaxanuk.data_curator.main(
            configuration=configuration,
            data_block_providers={market_block: provider},
            master_clock_data_block=market_block,
            output_handlers=[kaxanuk.data_curator.output_handlers.CsvOutput(output_base_dir=str(out_dir))],
            custom_calculation_modules=[],
            logger_level=logging.WARNING,
        )
        print(f"lote {first // BATCH + 1}: {len(batch)} identificadores", flush=True)
    missing = [t for t in tickers if not (out_dir / f"{t}.csv").exists()]
    pd.Series(missing, name="ticker").to_csv(out_dir.parent / "tickers_sin_precios.csv", index=False)
    print(f"escritos {len(tickers) - len(missing)} de {len(tickers)}; sin precios: {', '.join(missing) or 'ninguno'}")
    if collector.messages:
        print(f"errores registrados: {len(collector.messages)}; el primero: {collector.messages[0][:300]}")


if __name__ == "__main__":
    main()
