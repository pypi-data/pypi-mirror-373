"""Comando com subcomandos de trading."""

import click

from .buy import buy
from .cancel import cancel
from .orders import orders
from .pos import pos
from .sell import sell
from .zera import zera


@click.group()
@click.version_option(package_name="mtcli-trade")
def trade():
    """Gerencia operações no MetaTrader 5."""
    pass


trade.add_command(buy, name="buy")
trade.add_command(sell, name="sell")
trade.add_command(orders, name="orders")
trade.add_command(pos, name="pos")
trade.add_command(cancel, name="cancel")
trade.add_command(zera, name="zera")


if __name__ == "__main__":
    trade()
