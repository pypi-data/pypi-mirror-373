# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

import asyncio
import click

from .helper import activity_runner


@click.group
def group(): ...


async def send_message(application, verify=False):
    async with activity_runner(application) as runner:
        runner.skip_fetch = not verify

        return await runner.run_for_modifier(lambda x: {**x, "content": "Hello World"})


@group.command("hello", help="Sends hello world to the application")
@click.argument("application")
def message(application):
    asyncio.run(send_message(application))


@group.command("verify", help="Verifies the application works correctly")
@click.argument("application")
def verify(application):
    result = asyncio.run(send_message(application, verify=True))

    if not result:
        click.echo("Failed to retrieve message")
        exit(1)


if __name__ == "__main__":
    group()
