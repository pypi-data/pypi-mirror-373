"""Comando para executar venda a mercado ou pendente."""

import click
import MetaTrader5 as mt5
from mtcli.conecta import shutdown
from mtcli.logger import setup_logger

from .ordem import inicializar, criar_ordem, enviar_ordem

log = setup_logger()


@click.command()
@click.option(
    "--symbol", "-s", default="WINV25", help="Símbolo do ativo (default WINV25)."
)
@click.option(
    "--lot",
    type=float,
    default=1.0,
    help="Quantidade de contratos (default =1.0)",
)
@click.option(
    "-sl", type=float, default=150, help="Stop loss (em pontos) (default 150)."
)
@click.option("-tp", type=float, default=300, help="Take profit (em pontos)")
@click.option("--limit", "-l", is_flag=True, help="Envia ordem limit (sell limit)")
@click.option("--preco", "-pr", type=float, default=None, help="Preço da ordem limit")
def sell(symbol, lot, sl, tp, limit, preco):
    """Venda a mercado ou pendente com sl e tp."""
    tick = inicializar(symbol)
    if not tick:
        return

    if limit:
        if preco is None:
            click.echo("❌ Para ordens pendentes, defina o --preco")
            shutdown()
            return
        price = preco
        order_type = mt5.ORDER_TYPE_SELL_LIMIT
    else:
        price = tick.bid
        order_type = mt5.ORDER_TYPE_SELL

    ordem = criar_ordem(symbol, lot, sl, tp, price, order_type, limit)
    enviar_ordem(ordem, limit)
    shutdown()


if __name__ == "__main__":
    sell()
