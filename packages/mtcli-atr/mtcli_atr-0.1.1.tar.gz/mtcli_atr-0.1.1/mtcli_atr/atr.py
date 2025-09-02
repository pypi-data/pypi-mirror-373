"""Comando para calcular o indicador ATR."""

import click
import MetaTrader5 as mt5
from . import conf
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger

logger = setup_logger()


@click.command()
@click.option("--symbol", "-s", default="IBOV", help="Símbolo do ativo (default IBOV).")
@click.option(
    "--periodo", "-po", type=int, default=14, help="Período do ATR (default 14)."
)
@click.option("--timeframe", "-t", default="D1", help="Timeframe (ex: M1, H1, D1).")
def atr(symbol, periodo, timeframe):
    """Exibe o indicador ATR (Average True Range)"""
    conectar()

    tf = getattr(mt5, f"TIMEFRAME_{timeframe.upper()}", None)
    if tf is None:
        click.echo(f"❌ Timeframe inválido: {timeframe}")
        shutdown()
        return

    if not mt5.symbol_select(symbol, True):
        click.echo(f"❌ Erro ao selecionar símbolo {symbol}")
        shutdown()
        return

    rates = mt5.copy_rates_from_pos(symbol, tf, 0, periodo + 1)
    if rates is None or len(rates) < periodo + 1:
        click.echo("❌ Dados insuficientes para cálculo do ATR.")
        shutdown()
        return

    trs = []
    for i in range(1, len(rates)):
        high = rates[i]["high"]
        low = rates[i]["low"]
        prev_close = rates[i - 1]["close"]
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)

    atr_value = sum(trs) / periodo
    click.echo(
        f"ATR({periodo}) de {symbol} no timeframe {timeframe.upper()}: {atr_value:.{conf.digitos}f}"
    )
    shutdown()
