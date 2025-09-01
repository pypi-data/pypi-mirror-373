# SPDX-FileCopyrightText: 2024 Helge
#
# SPDX-License-Identifier: MIT

import pytest

from .parser import restrictions_for_actors_from_args


def test_restrictions_for_actors_from_args_base():
    restriction, only = restrictions_for_actors_from_args([], {})

    assert restriction is False


@pytest.mark.parametrize(
    "args",
    [{"only_alice": True}, {"only_bob": True}, {"only_alice": True, "only_bob": True}],
)
def test_restrictions_for_actors_from_args(args):
    restriction, only = restrictions_for_actors_from_args(["alice", "bob"], args)

    assert restriction
    assert set(only.keys()) == {"alice", "bob"}
