"""FRB-API: COMMAND LINE INTERFACE."""

import click

from chime_frb_api.backends.frb_master import FRBMaster


@click.group()
def cli():
    """CHIME/FRB API CLI."""
    pass  # pragma: no cover


@cli.command(
    name="generate-tokens", help="Generate tokens for the CHIME/FRB API."
)
@click.option(
    "--username",
    "-u",
    default=None,
    required=True,
    type=click.STRING,
    help="Username for the API.",
)
@click.option(
    "--password", prompt=True, hide_input=True, confirmation_prompt=False
)
def generate_tokens(username: str, password: str):
    """Generate tokens for the API.

    Args:
        username: Username for the API.
        password: Password for the API.
    """
    master = FRBMaster()
    master.API.generate_token(username=username, password=password)
