import asyncio
import click

from . import handle_send_to
from .modifier import ModifierBuilder


@click.command()
@click.option(
    "--domain",
    default="http://pasture-one-actor",
    help="Domain the actor is served one",
)
@click.option("--text", help="Content of the message to be send")
@click.option("--input_name", help="Name of the fediverse-pasture-input to use")
@click.option("--input_number", type=int, help="Id of the input to use")
@click.option(
    "--mention", is_flag=True, default=False, help="triggers mentioning the user"
)
@click.option(
    "--replace_https", is_flag=True, default=False, help="replace https:// with http://"
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="if true prints the resulting activity",
)
@click.argument("uri")
def send_to(
    domain,
    text,
    uri,
    input_name: str,
    input_number: int,
    mention: bool,
    replace_https: bool,
    verbose: bool,
):
    modifier = ModifierBuilder(
        text=text, input_name=input_name, input_number=input_number
    ).build()
    if not asyncio.run(
        handle_send_to(modifier, domain, uri, mention, replace_https, verbose)
    ):
        exit(1)

    if verbose:
        print("Activity send successfully`")


if __name__ == "__main__":
    send_to()
