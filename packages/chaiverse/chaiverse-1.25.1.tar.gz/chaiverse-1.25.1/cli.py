import json
import click
from pydantic import Field

from chaiverse.cli_utils.login_cli import developer_login, developer_logout


@click.group()
def cli():
    pass


@cli.command(help="Login with your chai developer_key. If you don't have one, contact us!")
def login():
    return developer_login()


@cli.command(help="Logout and clear developer_key from cache")
def logout():
    return developer_logout()
