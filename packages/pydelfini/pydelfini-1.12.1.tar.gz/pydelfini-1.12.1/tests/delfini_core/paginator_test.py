from datetime import datetime

import pytest
from pydelfini.delfini_core import paginator
from pydelfini.delfini_core.api.collections import collections_get_collections


def test_paginate(httpx_mock, client):
    def make_collection(i):
        return {
            "id": i,
            "versionId": "LIVE",
            "name": i,
            "description": "",
            "metadata": {},
            "accessLevel": "private",
            "account_id": "aaa",
            "createdOn": datetime.now().isoformat(),
        }

    httpx_mock.add_response(
        url="https://delfini.test/api/v1/collections?page_size=50",
        json={
            "collections": [
                make_collection("a"),
                make_collection("b"),
                make_collection("c"),
                make_collection("d"),
                make_collection("e"),
            ],
            "pagination": {
                "items_per_page": 5,
                "total_items": 7,
                "next_page_url": "https://delfini.test/api/v1/collections?token=xyz",
            },
        },
    )
    httpx_mock.add_response(
        url="https://delfini.test/api/v1/collections?token=xyz",
        json={
            "collections": [
                make_collection("f"),
                make_collection("g"),
            ],
            "pagination": {
                "items_per_page": 5,
                "total_items": 7,
                "next_page_url": None,
            },
        },
    )

    pager = paginator.Paginator(collections_get_collections, client)
    p = pager.paginate()

    page_one = next(p)
    assert len(page_one.collections) == 5

    page_two = next(p)
    assert len(page_two.collections) == 2

    with pytest.raises(StopIteration):
        next(p)
