from __future__ import annotations

from omero_quay.core.http_handler import parse_mongo_query


class Mock_req:
    query_arguments = {  # noqa:RUF012
        "filter": [b'{"_id": "man_660e125c-37a3-11f0-a5c2-f4c88a41c68e"}'],
        "limit": [b"1"],
    }


def test_parse_mongo_query():
    req = Mock_req()
    kwargs = parse_mongo_query(req)
    assert "filter" in kwargs
