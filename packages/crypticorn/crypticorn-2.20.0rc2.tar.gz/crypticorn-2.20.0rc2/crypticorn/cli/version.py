import importlib.metadata

import click


@click.command("version")
def version():
    """Print the version of the crypticorn package"""
    click.echo(importlib.metadata.distribution("crypticorn").version)
