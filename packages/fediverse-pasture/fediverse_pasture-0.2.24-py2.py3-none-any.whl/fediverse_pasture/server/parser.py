# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

from typing import Tuple


def restrictions_for_actors_from_args(actor_names, args) -> Tuple[bool, dict]:
    only = {name: args.get(f"only_{name}") for name in actor_names}

    if any(only.get(name) for name in actor_names):
        return True, only

    return False, {}
