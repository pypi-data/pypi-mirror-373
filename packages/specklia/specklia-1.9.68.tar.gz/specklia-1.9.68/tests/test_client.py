"""Unit tests for the Specklia Client."""

import struct
from datetime import datetime
from http import HTTPStatus
from typing import Dict, List
from unittest.mock import MagicMock, call, patch

import geopandas as gpd
import pandas as pd
import pytest
from shapely import Polygon
from shapely.geometry import mapping

from specklia import Specklia, chunked_transfer

_QUERY_DATASET_DICT = {
    "dataset_id": "sheffield",
    "epsg4326_polygon": Polygon(((0, 0), (0, 1), (1, 1), (0, 0))),
    "min_timestamp": datetime(2000, 1, 1),
    "max_timestamp": datetime(2000, 1, 2),
    "columns_to_return": ["croissant"],
    "additional_filters": [
        {"column": "cheese", "operator": "<", "threshold": 6.57},
        {"column": "wine", "operator": ">=", "threshold": -23},
    ],
}


@pytest.fixture
def example_geodataframe() -> gpd.GeoDataFrame:
    return gpd.GeoDataFrame(
        {"geometry": gpd.points_from_xy([1, 2, 3, 4, 5], [0, 1, 2, 3, 4]), "timestamp": [2, 3, 4, 5, 6]},
        crs="EPSG:4326",
    )


@pytest.fixture
def example_datasets_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "columns": {
                    "description": "hobbit height in cm",
                    "max_value": "150",
                    "min_value": "0",
                    "name": "height",
                    "type": "int",
                    "unit": "centimetres",
                },
                "created_timestamp": "Sat, 1 Jan 2000 15:44:24",
                "dataset_id": "sauron",
                "dataset_name": "hobbit_height",
                "description": "The height of some hobbits",
                "epsg4326_coverage": mapping(Polygon(((0, 1), (1, 1), (1, 0)))),
                "last_modified_timestamp": "Sun, 2 Jan 2000 15:44:24",
                "last_queried_timestamp": "Sun, 2 Jan 2000 12:14:44",
                "max_timestamp": "Wed, 1 Dec 1999 12:10:54",
                "min_timestamp": "Mon, 1 Nov 1999 00:41:25",
                "owning_group_id": "pippin",
                "owning_group_name": "merry",
                "size_rows": 4,
                "size_uncompressed_bytes": 726,
            }
        ]
    )


@pytest.fixture
def example_usage_report() -> List[Dict]:
    return [
        {
            "total_billable_bytes_processed": 10,
            "total_increase_in_bytes_stored": 20,
            "user_id": "example_user",
            "year": 2023,
            "month": 11,
        }
    ]


@pytest.fixture
def test_client():
    with patch.object(Specklia, "_fetch_user_id"):
        return Specklia(auth_token="fake_token", url="https://localhost")


def test_create_client(test_client: Specklia) -> None:
    assert test_client is not None


def test_user_id(test_client: Specklia, patched_requests_with_response: Dict[str, MagicMock]) -> None:
    patched_requests_with_response["response"].json.return_value = "fake_user_id"
    test_client._fetch_user_id()
    patched_requests_with_response["requests"].post.assert_has_calls(
        [call("https://localhost/users", headers={"Authorization": "Bearer fake_token"})]
    )
    assert test_client.user_id == "fake_user_id"


def test_list_users(test_client: Specklia, patched_requests_with_response: Dict[str, MagicMock]) -> None:
    patched_requests_with_response["response"].json.return_value = [{"name": "fred", "email": "fred@fred.fred"}]
    test_client.list_users(group_id="hazbin")
    patched_requests_with_response["requests"].get.assert_has_calls(
        [call("https://localhost/users", headers={"Authorization": "Bearer fake_token"}, params={"group_id": "hazbin"})]
    )


def test_add_points_to_dataset(
    test_client: Specklia, example_geodataframe: gpd.GeoDataFrame, patched_requests_with_response: Dict[str, MagicMock]
) -> None:
    patched_requests_with_response["response"].json.return_value = {"chunk_set_uuid": "brian"}

    test_client.add_points_to_dataset(
        dataset_id="dummy_dataset", new_points=[{"source": {"reference": "cheese"}, "gdf": example_geodataframe}]
    )

    patched_requests_with_response["requests"].post.assert_has_calls(
        [
            call(
                "https://localhost/ingest",
                json={
                    "dataset_id": "dummy_dataset",
                    "new_points": [{"source": {"reference": "cheese"}, "chunk_set_uuid": "brian", "num_chunks": 1}],
                    "duplicate_source_behaviour": "error",
                },
                headers={"Authorization": "Bearer fake_token"},
            )
        ]
    )


def test_query_dataset(
    test_client: Specklia, example_geodataframe: gpd.GeoDataFrame, patched_requests_with_response: Dict[str, MagicMock]
) -> None:
    # mock the query response
    patched_requests_with_response["response"].json.return_value = {
        "chunk_set_uuid": "brian",
        "num_chunks": 1,
        "sources": [
            {
                "geospatial_coverage": mapping(Polygon()),
                "min_time": datetime.now().isoformat(),
                "max_time": datetime.now().isoformat(),
            }
        ],
    }

    # mock the chunked data transfer response
    mock_chunk_response = MagicMock(name="mock_chunk_response")
    mock_chunk_response.content = struct.pack("i", 1) + chunked_transfer.serialise_dataframe(example_geodataframe)
    mock_no_more_chunks_response = MagicMock(name="mock_no_more_chunks_response")
    mock_no_more_chunks_response.status_code = HTTPStatus.NO_CONTENT
    patched_requests_with_response["chunked_transfer_requests"].get.side_effect = [
        mock_chunk_response,
        mock_no_more_chunks_response,
    ]

    response = test_client.query_dataset(
        dataset_id="dummy_dataset",
        epsg4326_polygon=Polygon(((0, 0), (0, 1), (1, 1), (0, 0))),
        min_datetime=datetime(2020, 5, 6),
        max_datetime=datetime(2020, 5, 10),
        columns_to_return=["lat", "lon"],
        additional_filters=[
            {"column": "cheese", "operator": "<", "threshold": 6.57},
            {"column": "wine", "operator": ">=", "threshold": -23},
        ],
    )

    pd.testing.assert_frame_equal(response[0], example_geodataframe)


@pytest.mark.parametrize(
    ("invalid_json", "expected_exception", "expected_match"),
    # invalid espg4326_search_area type
    [
        (dict(_QUERY_DATASET_DICT, epsg4326_polygon="my back garden"), TypeError, "provide only Geometry objects"),
        # invalid min_datetime type
        (
            dict(_QUERY_DATASET_DICT, min_timestamp="a long time ago"),
            AttributeError,
            "object has no attribute 'timestamp'",
        ),
        # invalid max_datetime type
        (
            dict(_QUERY_DATASET_DICT, max_timestamp="the year 3000"),
            AttributeError,
            "object has no attribute 'timestamp'",
        ),
    ],
)
def test_query_dataset_invalid_request(
    test_client: Specklia, invalid_json: dict, expected_exception: type[Exception], expected_match: str
) -> None:
    with pytest.raises(expected_exception, match=expected_match):
        test_client.query_dataset(
            dataset_id=invalid_json["dataset_id"],
            epsg4326_polygon=invalid_json["epsg4326_polygon"],
            min_datetime=invalid_json["min_timestamp"],
            max_datetime=invalid_json["max_timestamp"],
            columns_to_return=invalid_json["columns_to_return"],
            additional_filters=invalid_json["additional_filters"],
        )


def test_list_all_groups(patched_requests_with_response: Dict[str, MagicMock]) -> None:
    patched_requests_with_response["response"].json.return_value = ["ducks"]
    Specklia(url="https://localhost", auth_token="fake_token").list_all_groups()
    patched_requests_with_response["requests"].get.assert_has_calls(
        [call("https://localhost/groups", headers={"Authorization": "Bearer fake_token"})]
    )


def test_create_group(patched_requests_with_response: Dict[str, MagicMock]) -> None:
    Specklia(url="https://localhost", auth_token="fake_token").create_group("ducks")
    patched_requests_with_response["requests"].post.assert_has_calls(
        [call("https://localhost/groups", json={"group_name": "ducks"}, headers={"Authorization": "Bearer fake_token"})]
    )


def test_update_group_name(patched_requests_with_response: Dict[str, MagicMock]) -> None:
    Specklia(url="https://localhost", auth_token="fake_token").update_group_name(
        group_id="ducks", new_group_name="pigeons"
    )
    patched_requests_with_response["requests"].put.assert_has_calls(
        [
            call(
                "https://localhost/groups",
                json={"group_id": "ducks", "new_group_name": "pigeons"},
                headers={"Authorization": "Bearer fake_token"},
            )
        ]
    )


def test_delete_group(patched_requests_with_response: Dict[str, MagicMock]) -> None:
    Specklia(url="https://localhost", auth_token="fake_token").delete_group(group_id="ducks")
    patched_requests_with_response["requests"].delete.assert_has_calls(
        [call("https://localhost/groups", headers={"Authorization": "Bearer fake_token"}, params={"group_id": "ducks"})]
    )


def test_list_groups(patched_requests_with_response: Dict[str, MagicMock]) -> None:
    patched_requests_with_response["response"].json.return_value = ["ducks"]
    Specklia(url="https://localhost", auth_token="fake_token").list_groups()
    patched_requests_with_response["requests"].get.assert_has_calls(
        [call("https://localhost/groupmembership", headers={"Authorization": "Bearer fake_token"})]
    )


def test_add_user_to_group(patched_requests_with_response: Dict[str, MagicMock]) -> None:
    Specklia(url="https://localhost", auth_token="fake_token").add_user_to_group(
        group_id="ducks", user_to_add_id="donald"
    )
    patched_requests_with_response["requests"].post.assert_has_calls(
        [
            call(
                "https://localhost/groupmembership",
                json={"group_id": "ducks", "user_to_add_id": "donald"},
                headers={"Authorization": "Bearer fake_token"},
            )
        ]
    )


def test_update_user_privileges(patched_requests_with_response: Dict[str, MagicMock]) -> None:
    Specklia(url="https://localhost", auth_token="fake_token").update_user_privileges(
        group_id="ducks", user_to_update_id="donald", new_privileges="ADMIN"
    )
    patched_requests_with_response["requests"].put.assert_has_calls(
        [
            call(
                "https://localhost/groupmembership",
                json={"group_id": "ducks", "user_to_update_id": "donald", "new_privileges": "ADMIN"},
                headers={"Authorization": "Bearer fake_token"},
            )
        ]
    )


def test_delete_user_from_group(patched_requests_with_response: Dict[str, MagicMock]) -> None:
    Specklia(url="https://localhost", auth_token="fake_token").delete_user_from_group(
        group_id="ducks", user_to_delete_id="donald"
    )
    patched_requests_with_response["requests"].delete.assert_has_calls(
        [
            call(
                "https://localhost/groupmembership",
                headers={"Authorization": "Bearer fake_token"},
                params={"group_id": "ducks", "user_to_delete_id": "donald"},
            )
        ]
    )


def test_list_datasets(
    patched_requests_with_response: Dict[str, MagicMock], example_datasets_dataframe: pd.DataFrame
) -> None:
    patched_requests_with_response["response"].json.return_value = example_datasets_dataframe.to_dict(orient="records")
    datasets = Specklia(url="https://localhost", auth_token="fake_token").list_datasets()
    assert type(datasets["epsg4326_coverage"][0]) is Polygon
    for column in datasets.columns:
        if "timestamp" in column:
            assert type(datasets[column][0]) is pd.Timestamp
    patched_requests_with_response["requests"].get.assert_has_calls(
        [call("https://localhost/metadata", headers={"Authorization": "Bearer fake_token"})]
    )


def test_create_dataset(patched_requests_with_response: Dict[str, MagicMock]) -> None:
    Specklia(url="https://localhost", auth_token="fake_token").create_dataset(
        dataset_name="am",
        description="wibble",
        columns=[
            {"name": "hobbits", "type": "halflings", "description": "concerning hobbits"},
            {"name": "cats", "type": "pets", "description": "concerning cats"},
        ],
    )

    patched_requests_with_response["requests"].post.assert_has_calls(
        [
            call(
                "https://localhost/metadata",
                json={
                    "dataset_name": "am",
                    "description": "wibble",
                    "columns": [
                        {"name": "hobbits", "type": "halflings", "description": "concerning hobbits"},
                        {"name": "cats", "type": "pets", "description": "concerning cats"},
                    ],
                    "storage_technology": "OLAP",
                },
                headers={"Authorization": "Bearer fake_token"},
            )
        ]
    )


def test_update_dataset_ownership(patched_requests_with_response: Dict[str, MagicMock]) -> None:
    Specklia(url="https://localhost", auth_token="fake_token").update_dataset_ownership(
        dataset_id="bside", new_owning_group_id="arctic monkeys"
    )
    patched_requests_with_response["requests"].put.assert_has_calls(
        [
            call(
                "https://localhost/metadata",
                json={"dataset_id": "bside", "new_owning_group_id": "arctic monkeys"},
                headers={"Authorization": "Bearer fake_token"},
            )
        ]
    )


def test_delete_dataset(patched_requests_with_response: Dict[str, MagicMock]) -> None:
    Specklia(url="https://localhost", auth_token="fake_token").delete_dataset(dataset_id="bside")
    patched_requests_with_response["requests"].delete.assert_has_calls(
        [
            call(
                "https://localhost/metadata",
                params={"dataset_id": "bside"},
                headers={"Authorization": "Bearer fake_token"},
            )
        ]
    )


def test_report_usage(patched_requests_with_response: Dict[str, MagicMock], example_usage_report: List[Dict]) -> None:
    patched_requests_with_response["response"].json.return_value = example_usage_report
    group_id = "beatles"
    results = Specklia(url="https://localhost", auth_token="fake_token").report_usage(group_id=group_id)
    patched_requests_with_response["requests"].get.assert_has_calls(
        [call("https://localhost/usage", params={"group_id": group_id}, headers={"Authorization": "Bearer fake_token"})]
    )
    assert len(results) == 1
    assert results[0]["user_id"] == "example_user"
