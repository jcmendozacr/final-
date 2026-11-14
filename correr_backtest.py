"""Corre el weights.csv de núcleo + satélite en el Backtest Engine de KaxaNuk.

La licencia se lee de la variable de entorno KNBE_API_KEY_KAXANUK; nunca se imprime.

Uso:
    .venv/bin/python correr_backtest.py <carpeta de precios> <carpeta del weights> <nombre del weights> \
        <salida> <inicio> <fin> <comisión pb> <slippage pb> [reserva de efectivo, 0.01]
"""

import datetime
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path

ENGINE_INSTALLED = importlib.util.find_spec("kaxanuk.backtest_engine") is not None
QUOTED = [
    "Annualized Return (CAGR)",
    "Annualized Volatility",
    "Portfolio Sharpe Ratio",
    "Portfolio Sortino Ratio",
    "Max Drawdown",
    "Alpha",
    "Information Ratio",
    "Total Commissions",
    "Total Slippage Costs",
]


def main():
    if not ENGINE_INSTALLED:
        print("El Backtest Engine no está instalado: no se corrió nada.")
        return
    if not os.environ.get("KNBE_API_KEY_KAXANUK"):
        print("Falta la licencia en KNBE_API_KEY_KAXANUK: no se corrió nada.")
        return
    import kaxanuk.backtest_engine
    import kaxanuk.backtest_engine.entities
    import kaxanuk.backtest_engine.input_handlers

    prices, portfolio_dir, portfolio_name = (sys.argv[1], sys.argv[2], sys.argv[3])
    out_dir = Path(sys.argv[4]).resolve()
    start, end = (datetime.date.fromisoformat(d) for d in sys.argv[5:7])
    commission, slippage = (float(x) for x in sys.argv[7:9])
    reserve = float(sys.argv[9]) if len(sys.argv) > 9 else 0.01
    out_dir.mkdir(parents=True, exist_ok=True)

    configuration = kaxanuk.backtest_engine.entities.Configuration(
        initial_capital=100_000,
        start_date=start,
        end_date=end,
        cash_reserve_percentage=reserve,
        commission_model="basis_points",
        commission_basis_points=commission,
        commission_cents=0.0,
        slippage_model="basis_points",
        slippage_basis_points=slippage,
        market_data_input_format="csv",
        portfolio_input_format="csv",
        input_market_data_directory=str(Path(prices).resolve()),
        input_portfolio_directory=str(Path(portfolio_dir).resolve()),
        portfolio_name=portfolio_name,
        benchmark_file_name="KN_US_Equity_Core,SPY",
        backtest_results_output_directory=str(out_dir.resolve()),
        user_column_date="m_date",
        user_column_commission_price="m_close_split_adjusted",
        user_column_trade_execution_price="m_close_dividend_and_split_adjusted",
        user_column_mark_to_market_price="m_close_dividend_and_split_adjusted",
        user_column_high="m_high_split_adjusted",
        user_column_low="m_low_split_adjusted",
        user_column_close="m_close_split_adjusted",
        user_column_volume="m_volume_split_adjusted",
        rebalance_date_handling="next_trading_day",
        delisted_position_handling="sell_at_last_price",
    )
    market_data = kaxanuk.backtest_engine.input_handlers.CsvInput(input_dir=str(Path(prices).resolve()))
    portfolio = kaxanuk.backtest_engine.input_handlers.CsvPortfolioInputHandler(str(Path(portfolio_dir).resolve()))
    os.chdir(tempfile.mkdtemp())
    result = kaxanuk.backtest_engine.main(
        configuration=configuration,
        input_handlers=[market_data],
        portfolio_handlers=[portfolio],
        logger_file=str(out_dir.resolve() / "motor.log"),
        launch_dashboard=False,
        dashboard_port=8050,
    )
    if not result.success:
        print(f"La corrida falló: {type(result.error).__name__}: {result.error}")
        return
    data = result.data
    stats = data["portfolio_stats"]
    summary = {
        "ventana_pedida": [start.isoformat(), end.isoformat()],
        "ventana_valuada": [str(data["start_date"]), str(data["end_date"])],
        "años_valuados": data["years"],
        "portafolio": {key: stats.get(key) for key in QUOTED},
        "benchmarks": {
            name: {key: values.get(key) for key in QUOTED[:5]}
            for name, values in (data.get("benchmarks_stats") or {}).items()
        },
        "tasa_libre_de_riesgo": data.get("Risk_free_rate"),
    }
    (out_dir / "resumen.json").write_text(json.dumps(summary, indent=2, default=str, ensure_ascii=False))
    daily = data["Daily_Weights"]
    getattr(daily, "to_pandas", lambda: daily)().to_csv(out_dir / "Daily_Weights.csv")
    register = data["Register_df"]
    getattr(register, "to_pandas", lambda: register)().to_csv(out_dir / "Register.csv")
    print(json.dumps(summary, indent=2, default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
