"""Corre Attribution Analysis (Brinson-Fachler y el modelo de factores de KaxaNuk).

La licencia se lee de la variable de entorno KNAA_API_KEY_KAXANUK; nunca se imprime.

Uso:
    .venv/bin/python correr_atribucion.py <carpeta datos_atribucion>
"""

import importlib.util
import logging
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

LIBRARY_INSTALLED = importlib.util.find_spec("kaxanuk.attribution_analysis") is not None


def main():
    if not LIBRARY_INSTALLED:
        print("Attribution Analysis no está instalado: no se corrió nada.")
        return
    if not os.environ.get("KNAA_API_KEY_KAXANUK"):
        print("Falta la licencia en KNAA_API_KEY_KAXANUK: no se corrió nada.")
        return
    import kaxanuk.attribution_analysis.entities.configuration
    import kaxanuk.attribution_analysis.performance_attribution
    import kaxanuk.attribution_analysis.services.configuration_logger

    base = Path(sys.argv[1]).resolve()
    kaxanuk.attribution_analysis.services.configuration_logger.configure_logger(
        logger_name="kaxanuk.attribution_analysis",
        logger_level=logging.INFO,
        logger_format="[%(levelname)s] %(message)s",
        logger_file=str(base / "atribucion.log"),
    )
    configuration = kaxanuk.attribution_analysis.entities.configuration.Configuration(
        input_directory=str(base / "Input"),
        weights_portfolio_directory="Portfolios",
        weights_benchmark_directory="Benchmark_Portfolios",
        benchmark_returns_directory="Benchmark_Portfolios",
        investable_assets_directory=str(base / "Input" / "Data"),
        factor_returns_by_factor_directory=str(base / "Input" / "Factor_Models"),
        portfolio_file_name="portfolio_daily_weights.csv",
        benchmark_file_name="benchmark_daily_weights.csv",
        benchmark_return_file_name="benchmark_returns.csv",
        user_column_date="m_date",
        user_column_price="m_close_dividend_and_split_adjusted",
        market_data_input_format="csv",
        portfolio_input_format="csv",
        start_date="auto",
        end_date="auto",
        brinson_fachler_method=True,
        factor_model_method=True,
        active_factor_model=True,
        output_directory=str(base / "Output"),
    )
    result = kaxanuk.attribution_analysis.performance_attribution.main(
        configuration,
        launch_dashboard=False,
        dashboard_port=8050,
    )
    print("ATRIBUTOS:", [name for name in dir(result) if not name.startswith("_")])
    import pickle
    with open(base / "resultado.pkl", "wb") as handle:
        pickle.dump(result, handle)


if __name__ == "__main__":
    main()
