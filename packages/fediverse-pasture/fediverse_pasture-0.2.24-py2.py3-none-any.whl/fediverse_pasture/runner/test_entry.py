# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from .entry import Entry


def test_from_result_list_empty():
    entry = Entry.from_result_list([])

    assert isinstance(entry, Entry)
    assert not entry.present_for("app")
    assert entry.applications == set()


def test_from_result_list_one_element():
    result = [{"application_name": "app", "data": "boo"}]
    entry = Entry.from_result_list(result)

    assert isinstance(entry, Entry)
    assert entry.present_for("app")
    assert entry.applications == {"app"}

    lines = entry.as_tabs(["app", "other"])

    expected = """=== "app"

    ```json title="app"
    {
      "data": "boo"
    }
    ```


=== "other"

    no result

"""

    assert "".join(lines) == expected


def test_from_result_list_one_element_as_grid():
    result = [{"application_name": "app", "data": "boo"}]
    entry = Entry.from_result_list(result)

    lines = entry.as_grid(["app", "other"])

    expected = """<div class="grid" markdown>

```json title="app"
{
  "data": "boo"
}
```


no result

</div>
"""

    assert "".join(lines) == expected
