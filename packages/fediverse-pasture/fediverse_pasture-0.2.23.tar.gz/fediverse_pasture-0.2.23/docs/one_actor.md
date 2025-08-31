<!--
SPDX-FileCopyrightText: 2023 Helge

SPDX-License-Identifier: CC-BY-4.0
-->

# One Actor Server

`pasture_one_actor` is meant as a simple application with exactly
one actor, that can be used for other applications. The simplest use however
to just capture all messages arriving at the inbox.

## Getting started

You can install the Fediverse pasture via

```bash
git clone https://codeberg.org/helge/funfedidev.git
cd funfedidev/fediverse-pasture
```

Then in your Fediverse Pasture installation, run

```bash
docker compose --file pasture.yml up pasture_one_actor
```

Now by opening [http://localhost:2917](http://localhost:2917)
you can view the inbox content. One should note that the page
will be infinitely loading, as new content is streamed to it.

If you now send a message to `@actor@pasture_one_actor`, you
will see it show up in the inbox.

## Using together with pasture_runner

First, we start the `pasture_runner`. The following command, will drop
us to `/bin/sh`.

```bash
docker compose --file pasture.yml run pasture_runner
```

Then running `ipython` will drop us into a python command line.
Then by running

```python
from fediverse_pasture.one_actor import bovine_actor_and_actor_object
bovine_actor, actor = bovine_actor_and_actor_object("http://pasture_one_actor/")
await bovine_actor.init()
await bovine_actor.get('http://mastodon42web/users/hippo')
```

one can retrieve the profile form a mastodon server.
