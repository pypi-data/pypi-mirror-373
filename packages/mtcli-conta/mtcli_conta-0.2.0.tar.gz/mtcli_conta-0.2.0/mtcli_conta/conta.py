"""Exibe informações da conta conectada no MetaTrader 5."""

import click
import MetaTrader5 as mt5
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger

log = setup_logger()


@click.command()
@click.version_option(package_name="mtcli-conta")
def conta():
    """Exibe informações da conta conectada no MetaTrader 5."""
    conectar()

    info = mt5.account_info()
    if info is None:
        msg = "❌ Não foi possível obter informações da conta"
        click.echo(msg)
        log.error(msg)
        shutdown()
        return

    click.echo("Informações da Conta:")
    click.echo(f"Login: {info.login}")
    click.echo(f"Nome: {info.name}")
    click.echo(f"Servidor: {info.server}")
    click.echo(f"Moeda: {info.currency}")
    click.echo(f"Saldo: {info.balance}")
    click.echo(f"Patrimonio: {info.equity}")
    click.echo(f"Margem Livre: {info.margin_free}")
    click.echo(f"Margem Usada: {info.margin}")
    click.echo(f"Nível de Margem: {info.margin_level:.2f}%")
    click.echo(f"Lucro: {info.profit}")

    shutdown()
