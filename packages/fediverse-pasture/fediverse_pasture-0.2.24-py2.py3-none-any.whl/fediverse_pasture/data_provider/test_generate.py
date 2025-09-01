# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import pytest
from .generate import generate_possible_actors


@pytest.mark.skip("SLOW")
def test_generate_possible_actors():
    result = generate_possible_actors()

    assert isinstance(result, list)
    assert len(result) > 0

    print(result)
