"""Comando para exibir todas as posições."""

import click
import MetaTrader5 as mt5
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger

from . import conf

log = setup_logger()


@click.command()
@click.option("--symbol", "-s", default=None, help="Símbolo do ativo (opcional)")
def pos(symbol):
    """Lista todas as posições abertas (ou de um símbolo)"""
    conectar()

    posicoes = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()

    if not posicoes:
        msg = (
            f"Nenhuma posição aberta para {symbol}."
            if symbol
            else "Nenhuma posição aberta encontrada."
        )
        click.echo(f"{msg}")
        log.info(f"{msg}")
        shutdown()
        return

    click.echo(f"Posições abertas{' para ' + symbol if symbol else ''}:\n")
    for p in posicoes:
        tipo = "COMPRA" if p.type == mt5.POSITION_TYPE_BUY else "VENDA"
        click.echo(
            f"{tipo} {p.symbol} {p.volume:.2f} {p.price_open:.{conf.digitos}f} lucro {p.profit:.2f}"
        )
        log.info(
            f"{tipo} | {p.symbol} | volume: {p.volume:.2f} | preço: {p.price_open:.{conf.digitos}f} | lucro: {p.profit:.2f}."
        )

    shutdown()


if __name__ == "__main__":
    pos()
