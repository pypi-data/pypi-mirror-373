# crypticorn/cli.py

import click

from crypticorn.cli import init_group, version


@click.group()
def cli():
    """🧙 Crypticorn CLI — magic for our microservices."""
    pass


cli.add_command(init_group, name="init")
cli.add_command(version, name="version")

if __name__ == "__main__":
    cli()
