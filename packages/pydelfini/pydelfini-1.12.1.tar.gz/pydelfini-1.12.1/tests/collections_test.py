from datetime import datetime

import pandas as pd
import pytest
from pydelfini.collections import DelfiniCollection
from pydelfini.delfini_core.models import Collection


@pytest.fixture
def collection(client):
    m = Collection(
        access_level="private",
        account_id="zzz",
        created_on=datetime.now(),
        description="",
        id="xyz",
        name="XYZ",
        version_id="LIVE",
        metadata={},
    )
    return DelfiniCollection(m, client)


def test_list_folder(httpx_mock, collection):
    # list top level
    httpx_mock.add_response(
        url="https://delfini.test/api/v1/collections/xyz/LIVE/items?in_folder=ROOT",
        json={
            "items": [
                {
                    "id": "f",
                    "name": "foo",
                    "path": "foo",
                    "type": "file",
                    "createdOn": datetime.now().isoformat(),
                },
                {
                    "id": "b",
                    "name": "bar",
                    "path": "bar",
                    "type": "link",
                    "createdOn": datetime.now().isoformat(),
                },
                {
                    "id": "z",
                    "name": "baz",
                    "path": "baz",
                    "type": "folder",
                    "createdOn": datetime.now().isoformat(),
                },
            ],
            "pagination": {
                "total_items": 3,
                "items_per_page": 50,
                "next_page_url": None,
            },
        },
    )
    assert [i.name for i in collection] == ["foo", "bar", "baz"]


def test_get_and_list_folder(httpx_mock, collection):
    # go down a folder and list it
    httpx_mock.add_response(
        url=(
            "https://delfini.test/api/v1/collections/xyz/LIVE"
            "/items?in_folder=ROOT&name=baz&type=folder"
        ),
        json={
            "items": [
                {
                    "id": "z",
                    "name": "baz",
                    "path": "baz",
                    "type": "folder",
                    "createdOn": datetime.now().isoformat(),
                },
            ],
            "pagination": {
                "total_items": 1,
                "items_per_page": 50,
                "next_page_url": None,
            },
        },
    )
    httpx_mock.add_response(
        url="https://delfini.test/api/v1/collections/xyz/LIVE/items?in_path=baz",
        json={
            "items": [
                {
                    "id": "1",
                    "name": "one",
                    "path": "one",
                    "type": "file",
                    "createdOn": datetime.now().isoformat(),
                },
                {
                    "id": "2",
                    "name": "two",
                    "path": "two",
                    "type": "file",
                    "createdOn": datetime.now().isoformat(),
                },
            ],
            "pagination": {
                "total_items": 2,
                "items_per_page": 50,
                "next_page_url": None,
            },
        },
    )

    f = collection.folder("baz")
    assert f.name == "baz"
    assert [i.name for i in f] == ["one", "two"]
    assert [i.in_folder for i in f] == [f, f]


def test_walk_folder(httpx_mock, collection):
    # walk all items
    httpx_mock.add_response(
        url="https://delfini.test/api/v1/collections/xyz/LIVE/items?in_folder=ROOT",
        json={
            "items": [
                {
                    "id": "f",
                    "name": "foo",
                    "path": "foo",
                    "type": "file",
                    "createdOn": datetime.now().isoformat(),
                },
                {
                    "id": "b",
                    "name": "bar",
                    "path": "bar",
                    "type": "link",
                    "createdOn": datetime.now().isoformat(),
                },
                {
                    "id": "z",
                    "name": "baz",
                    "path": "baz",
                    "type": "folder",
                    "createdOn": datetime.now().isoformat(),
                },
            ],
            "pagination": {
                "total_items": 3,
                "items_per_page": 50,
                "next_page_url": None,
            },
        },
    )
    httpx_mock.add_response(
        url="https://delfini.test/api/v1/collections/xyz/LIVE/items?in_path=baz",
        json={
            "items": [
                {
                    "id": "1",
                    "name": "one",
                    "path": "one",
                    "type": "file",
                    "createdOn": datetime.now().isoformat(),
                },
                {
                    "id": "2",
                    "name": "two",
                    "path": "two",
                    "type": "file",
                    "createdOn": datetime.now().isoformat(),
                },
            ],
            "pagination": {
                "total_items": 2,
                "items_per_page": 50,
                "next_page_url": None,
            },
        },
    )
    assert [i.name for i in collection.walk()] == ["foo", "bar", "baz", "one", "two"]
    assert [i.path for i in collection.walk()] == [
        "foo",
        "bar",
        "baz",
        "baz/one",
        "baz/two",
    ]


def test_getitem_folder(httpx_mock, collection):
    httpx_mock.add_response(
        url=(
            "https://delfini.test/api/v1/collections/xyz/LIVE"
            "/items?name=foo&in_folder=ROOT"
        ),
        json={
            "items": [
                {
                    "id": "f",
                    "name": "foo",
                    "path": "foo",
                    "type": "file",
                    "createdOn": datetime.now().isoformat(),
                }
            ],
            "pagination": {
                "total_items": 1,
                "items_per_page": 50,
                "next_page_url": None,
            },
        },
    )
    assert collection["foo"].name == "foo"

    httpx_mock.add_response(
        url=(
            "https://delfini.test/api/v1/collections/xyz/LIVE"
            "/items?name=baz&type=folder&in_folder=ROOT"
        ),
        json={
            "items": [
                {
                    "id": "z",
                    "name": "baz",
                    "path": "baz",
                    "type": "folder",
                    "createdOn": datetime.now().isoformat(),
                }
            ],
            "pagination": {
                "total_items": 1,
                "items_per_page": 50,
                "next_page_url": None,
            },
        },
    )
    httpx_mock.add_response(
        url=(
            "https://delfini.test/api/v1/collections/xyz/LIVE"
            "/items?name=one&in_path=baz"
        ),
        json={
            "items": [
                {
                    "id": "1",
                    "name": "one",
                    "path": "one",
                    "type": "file",
                    "createdOn": datetime.now().isoformat(),
                }
            ],
            "pagination": {
                "total_items": 1,
                "items_per_page": 50,
                "next_page_url": None,
            },
        },
    )
    assert collection["baz/one"].name == "one"


def test_get_table(httpx_mock, collection):
    httpx_mock.add_response(
        url=(
            "https://delfini.test/api/v1/collections/xyz/LIVE"
            "/items?name=foo&in_folder=ROOT"
        ),
        json={
            "items": [
                {
                    "id": "f",
                    "name": "foo",
                    "path": "foo",
                    "type": "file",
                    "createdOn": datetime.now().isoformat(),
                }
            ],
            "pagination": {
                "total_items": 1,
                "items_per_page": 50,
                "next_page_url": None,
            },
        },
    )
    httpx_mock.add_response(
        url=(
            "https://delfini.test/api/v1/collections/xyz/LIVE"
            "/tables/f/data?page_size=10000"
        ),
        json={
            "errors": [],
            "pagination": {
                "total_items": 5,
                "items_per_page": 10000,
                "next_page_url": None,
            },
            "data": [
                {"a": 1, "b": 1, "c": 1},
                {"a": 2, "b": 4, "c": 8},
                {"a": 3, "b": 9, "c": 27},
                {"a": 4, "b": 16, "c": 64},
                {"a": 5, "b": 25, "c": 125},
            ],
            "data_model": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                    "c": {"type": "number"},
                },
            },
        },
    )
    df = collection.get_table("foo")
    assert len(df) == 5


def test_write_table(httpx_mock, collection):
    httpx_mock.add_response(
        method="POST",
        url="https://delfini.test/api/v1/collections/xyz/LIVE/items",
        status_code=201,
        json={
            "id": "b",
            "name": "bar",
            "path": "bar",
            "type": "file",
            "createdOn": datetime.now().isoformat(),
        },
    )
    df = pd.DataFrame({"A": [1, 2, 3], "B": [1, 4, 9]})
    collection.write_table("bar", df)

    request = httpx_mock.get_request()
    request.read()
    assert b'{"name": "csv"}' in request.content
    assert b"A,B\n1,1\n2,4\n3,9\n" in request.content
