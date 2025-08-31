"""kabukit CLI."""

from __future__ import annotations

from typing import Annotated

import typer
from httpx import HTTPStatusError
from typer import Argument, Exit, Option, Typer

from .jquants.client import JQuantsClient

app = Typer(add_completion=False)


@app.command()
def auth(
    mailaddress: Annotated[str, Argument(help="J-Quants mail address.")],
    password: Annotated[str, Option(prompt=True, hide_input=True)],
) -> None:
    """Authenticate and save/refresh tokens."""
    client = JQuantsClient()

    try:
        client.auth(mailaddress, password)
    except HTTPStatusError as e:
        typer.echo(f"Authentication failed: {e}")
        raise Exit(1) from None

    client = JQuantsClient()
    typer.echo(f"refreshToken: {client.refresh_token[:30]}...")
    typer.echo(f"idToken: {client.id_token[:30]}...")


@app.command()
def version() -> None:
    """Show kabukit version."""
    from importlib.metadata import version

    typer.echo(f"kabukit version: {version('kabukit')}")
