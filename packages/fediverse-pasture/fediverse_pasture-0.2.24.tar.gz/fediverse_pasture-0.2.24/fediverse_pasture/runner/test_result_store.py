# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from .result_store import with_store
from .entry import Entry


async def test_with_store():
    async with with_store(db_url="sqlite://:memory:") as store:
        await store.add_result("test", "app1", {})
        await store.add_result("test", "app1", {"a": "b"})
        await store.add_result("test", "app2", {})
        await store.add_result("other", "app1", {})

        result = await store.results_for_test("test")

        assert len(result) == 2


async def test_delete():
    async with with_store(db_url="sqlite://:memory:") as store:
        await store.add_result("test", "app1", {})
        await store.delete_record("test", "app1")

        result = await store.results_for_test("test")

        assert len(result) == 0


async def test_with_store_to_entry():
    async with with_store(db_url="sqlite://:memory:") as store:
        await store.add_result("test", "app1", {})
        await store.add_result("test", "app1", {"a": "b"})
        await store.add_result("test", "app2", {})

        result = await store.entry_for_test("test")

        assert isinstance(result, Entry)

        print(result.entry)


async def test_with_store_as_list():
    async with with_store(db_url="sqlite://:memory:") as store:
        await store.add_result("test1", "app1", {"a": "b"})
        await store.add_result("test1", "app2", {"a": 1})

        await store.add_result("test2", "app1", {"a": "b"})
        await store.add_result("test2", "app2", {"a": 2})

        result = await store.as_list()

        assert isinstance(result, list)

        assert len(result) == 4
