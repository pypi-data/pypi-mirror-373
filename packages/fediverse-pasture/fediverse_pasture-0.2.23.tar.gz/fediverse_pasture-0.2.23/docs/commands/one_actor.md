<!--
SPDX-FileCopyrightText: 2023 Helge

SPDX-License-Identifier: CC-BY-4.0
-->

# One Actor server

The one actor server is intended to provide an ActivityPub actor
to run tests with (see [here](https://funfedi.dev/testing_tools/one_actor/)). For this, one runs the server via

```bash
python -mfediverse_pasture.one_actor --generate_config
```

Then one can use the actor from inside a python script via

```python
from fediverse_pasture.one_actor import bovine_actor_and_actor_object

bovine_actor, actor = bovine_actor_and_actor_object("http://localhost:2917/")
await bovine_actor.init(session=session)
```

where `session` represents an [aiohttp.ClientSession][aiohttp.ClientSession]. Furthermore,
`one_actor` exposes a page at `/` that displays objects received in
the inbox. Due to the simplistic implementation, one can only open the
page once, and the current content is lost on a refresh.

## Command line usage

::: mkdocs-click
    :module: fediverse_pasture.one_actor
    :command: one_actor
    :prog_name: python -m fediverse_pasture.one_actor
    :depth: 2

The domain name the actor objects return is interfered from the host
the request is made to. This means specifying the domain is only necessary,
when using the actor in an external application.

## Exported methods

::: fediverse_pasture.one_actor
    options:
        show_root_heading: true
        heading_level: 3

## Serving static files

Using the `--assets` parameter, a directory can be specified to be served
as static files. This is done using the method

::: fediverse_pasture.server.assets_blueprint_for_directory
    options:
        show_root_heading: true
        heading_level: 3
