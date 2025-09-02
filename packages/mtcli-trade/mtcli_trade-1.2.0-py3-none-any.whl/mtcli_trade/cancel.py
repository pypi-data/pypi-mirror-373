"""Cancela todas as órdens pendentes."""

import click
import MetaTrader5 as mt5
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger

log = setup_logger()


@click.command()
@click.option("--symbol", "-s", default=None, help="Símbolo do ativo (opcional)")
def cancel(symbol):
    """Cancela todas as ordens pendentes (ou de um símbolo)."""
    conectar()

    ordens = mt5.orders_get(symbol=symbol) if symbol else mt5.orders_get()

    if not ordens:
        msg = (
            f"Nenhuma ordem pendente para {symbol}"
            if symbol
            else "Nenhuma ordem pendente encontrada."
        )
        click.echo(f"{msg}")
        log.info(f"{msg}")
        shutdown()
        return

    click.echo(f"Cancelando {len(ordens)} ordem(ns)...")

    for ordem in ordens:
        req = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": ordem.ticket,
            "symbol": ordem.symbol,
            "magic": 1000,
            "comment": "Cancelamento via CLI",
        }

        res = mt5.order_send(req)
        if res.retcode == mt5.TRADE_RETCODE_DONE:
            click.echo(f"Ordem cancelada {ordem.ticket} {ordem.symbol}")
            log.info(f"Ordem cancelada: ticket {ordem.ticket} ({ordem.symbol})")
        else:
            msg = f"❌ Falha ao cancelar {ordem.ticket} código {res.retcode}"
            click.echo(msg)
            log.error(msg)

    shutdown()


if __name__ == "__main__":
    cancel()
