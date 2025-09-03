"""Utilities for handling HTTP responses."""

import http
import json

from requests import Response
import typer

from app.console import get_console


def handle_response(response: Response) -> None:
    """Prints custom error messages for 401, 403 and 422 statuses,
    otherwise raise_for_status().

    Args:
        response (Response): The response object to handle.
    """
    console = get_console()

    if response.status_code == http.HTTPStatus.UNAUTHORIZED:
        console.print(
            '[bold red]Error: Unauthorized.[/bold red] '
            'Please check your API key and try again.'
        )
        raise typer.Exit(code=response.status_code)
    elif response.status_code == http.HTTPStatus.FORBIDDEN:
        console.print(
            '[bold red]Error: Forbidden.[/bold red] '
            'You do not have permission to perform this action.'
        )
        raise typer.Exit(code=response.status_code)
    elif response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY:
        console.print(
            '[bold red]Error: Unprocessable Entity.[/bold red] '
            'The server could not process the request.'
        )
        console.print(response.json())
        raise typer.Exit(code=response.status_code)

    if response.status_code == http.HTTPStatus.OK:
        if response.content:
            try:
                data = response.json()
                if 'errors' in data:
                    for error in data['errors']:
                        console.print(
                            f"[bold red]Error:[/bold red] {error['message']}"
                        )
                    raise typer.Exit(code=1)
            except json.JSONDecodeError:
                pass

    response.raise_for_status()
