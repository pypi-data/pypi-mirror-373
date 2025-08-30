import json
import os
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import HttpUrl

from futurehouse_client.clients.data_storage_methods import DataStorageError
from futurehouse_client.clients.rest_client import (
    RestClient,
)
from futurehouse_client.models.app import (
    Stage,
)
from futurehouse_client.models.data_storage_methods import (
    DataContentType,
    DataStorageLocationPayload,
    DataStorageType,
)

ADMIN_API_KEY = os.environ["PLAYWRIGHT_ADMIN_API_KEY"]


@pytest.fixture(name="admin_client")
def fixture_admin_client():
    """Create a RestClient for testing; using a admin user key with full access."""
    return RestClient(
        stage=Stage.DEV,
        api_key=ADMIN_API_KEY,
    )


@pytest.mark.timeout(300)
def test_store_raw_content_sync(admin_client: RestClient):
    test_content = "This is random content for the sync test"
    # Store the text content
    response = admin_client.store_text_content(
        name=f"E2E test entry text: {uuid4()}",
        content=test_content,
        description="Here is some description",
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    fetch_response = admin_client.fetch_data_from_storage(response.data_storage.id)

    assert fetch_response is not None
    assert fetch_response == test_content

    admin_client.delete_data_storage_entry(response.data_storage.id)

    with pytest.raises(DataStorageError, match="Data storage entry not found"):
        admin_client.fetch_data_from_storage(response.data_storage.id)


@pytest.mark.timeout(300)
@pytest.mark.asyncio
async def test_store_raw_content_async(admin_client: RestClient):
    test_content = "This is random content for the async test"
    response = await admin_client.astore_text_content(
        name=f"E2E test entry text: {uuid4()}",
        content=test_content,
        description="Here is some description",
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    fetch_response = await admin_client.afetch_data_from_storage(
        response.data_storage.id
    )

    assert fetch_response is not None
    assert fetch_response == test_content

    await admin_client.adelete_data_storage_entry(response.data_storage.id)

    with pytest.raises(DataStorageError, match="Data storage entry not found"):
        await admin_client.afetch_data_from_storage(response.data_storage.id)


@pytest.mark.timeout(300)
def test_store_file_content_sync(admin_client: RestClient):
    response = admin_client.store_file_content(
        name=f"E2E test entry file: {uuid4()}",
        file_path=Path("packages/futurehouse-client/tests/test_data/test_file.txt"),
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    fetch_response = admin_client.fetch_data_from_storage(response.data_storage.id)

    assert fetch_response is not None
    assert (
        fetch_response
        == "Here is some random text that shall immortalize Eddie's brain in code.\n"
    )

    admin_client.delete_data_storage_entry(response.data_storage.id)


@pytest.mark.timeout(300)
def test_store_dir_content_sync(admin_client: RestClient):
    response = admin_client.store_file_content(
        name=f"E2E test entry dir: {uuid4()}",
        file_path=Path("packages/futurehouse-client/tests/test_data"),
        as_collection=True,
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    fetch_response = admin_client.fetch_data_from_storage(response.data_storage.id)

    assert isinstance(fetch_response, Path)
    assert fetch_response.exists()

    admin_client.delete_data_storage_entry(response.data_storage.id)


@pytest.mark.timeout(300)
@pytest.mark.asyncio
async def test_store_file_content_async(admin_client: RestClient):
    response = await admin_client.astore_file_content(
        name=f"E2E test entry file: {uuid4()}",
        file_path=Path("packages/futurehouse-client/tests/test_data/test_file.txt"),
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    fetch_response = await admin_client.afetch_data_from_storage(
        response.data_storage.id
    )

    assert fetch_response is not None
    assert (
        fetch_response
        == "Here is some random text that shall immortalize Eddie's brain in code.\n"
    )

    await admin_client.adelete_data_storage_entry(response.data_storage.id)


@pytest.mark.timeout(300)
@pytest.mark.asyncio
async def test_store_dir_content_async(admin_client: RestClient):
    response = await admin_client.astore_file_content(
        name=f"E2E test entry dir: {uuid4()}",
        file_path=Path("packages/futurehouse-client/tests/test_data"),
        as_collection=True,
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    fetch_response = await admin_client.afetch_data_from_storage(
        response.data_storage.id
    )

    assert isinstance(fetch_response, Path)
    assert fetch_response.exists()

    await admin_client.adelete_data_storage_entry(response.data_storage.id)


@pytest.mark.timeout(300)
@pytest.mark.asyncio
async def test_store_dir_with_manifest_async(admin_client: RestClient):
    response = await admin_client.astore_file_content(
        name=f"E2E test dir: {uuid4()}",
        file_path=Path("packages/futurehouse-client/tests/test_data"),
        manifest_filename="packages/futurehouse-client/tests/test_data/test_manifest.yaml",
        as_collection=True,
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    fetch_response = await admin_client.afetch_data_from_storage(
        response.data_storage.id
    )

    assert isinstance(fetch_response, Path)
    assert fetch_response.exists()

    await admin_client.adelete_data_storage_entry(response.data_storage.id)


@pytest.mark.timeout(300)
def test_register_existing_content_gcs_sync_collection(admin_client: RestClient):
    response = admin_client.register_existing_data_source(
        name=f"E2E test entry gcs dir: {uuid4()}",
        description="This is data that already exists",
        as_collection=True,
        existing_location=DataStorageLocationPayload(
            storage_type=DataStorageType.GCS,
            content_type=DataContentType.DIRECTORY,
            metadata={"bucket_name": "fh-pubmed-data", "prefix": "oa_package/00/00"},
        ),
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    fetch_response = admin_client.fetch_data_from_storage(response.data_storage.id)

    assert isinstance(fetch_response, list)
    assert isinstance(fetch_response[0], Path)
    assert fetch_response[0].exists()

    admin_client.delete_data_storage_entry(response.data_storage.id)


@pytest.mark.timeout(300)
@pytest.mark.asyncio
async def test_register_existing_content_gcs_async_collection(admin_client: RestClient):
    response = await admin_client.aregister_existing_data_source(
        name=f"E2E test entry gcs dir: {uuid4()}",
        description="This is data that already exists",
        as_collection=True,
        existing_location=DataStorageLocationPayload(
            storage_type=DataStorageType.GCS,
            content_type=DataContentType.DIRECTORY,
            metadata={"bucket_name": "fh-pubmed-data", "prefix": "oa_package/00/00"},
        ),
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    fetch_response = await admin_client.afetch_data_from_storage(
        response.data_storage.id
    )

    assert isinstance(fetch_response, list)
    assert isinstance(fetch_response[0], Path)
    assert fetch_response[0].exists()

    await admin_client.adelete_data_storage_entry(response.data_storage.id)


# @pytest.mark.timeout(300)
# @pytest.mark.asyncio
# async def test_register_existing_content_gcs_async_single(admin_client: RestClient):
#     response = await admin_client.aregister_existing_data_source(
#         name=f"E2E test entry gcs dir: {uuid4()}",
#         description="This is data that already exists",
#         as_collection=False,
#         existing_location=DataStorageLocationPayload(
#             storage_type=DataStorageType.GCS,
#             content_type=DataContentType.DIRECTORY,
#             metadata={"bucket_name": "fh-pubmed-data"},
#             location="oa_package/00/00/PMC10054724.tar.gz",
#         ),
#     )

#     assert response is not None
#     assert response.data_storage.id is not None
#     assert len(response.storage_locations) > 0

#     fetch_response = await admin_client.afetch_data_from_storage(
#         response.data_storage.id
#     )

#     assert isinstance(fetch_response, Path)
#     assert fetch_response.exists()


# @pytest.mark.timeout(300)
# def test_register_existing_content_gcs_sync_single(admin_client: RestClient):
#     response = admin_client.register_existing_data_source(
#         name=f"E2E test entry gcs dir: {uuid4()}",
#         description="This is data that already exists",
#         as_collection=False,
#         existing_location=DataStorageLocationPayload(
#             storage_type=DataStorageType.GCS,
#             content_type=DataContentType.DIRECTORY,
#             metadata={"bucket_name": "fh-pubmed-data"},
#             location="oa_package/00/00/PMC10054724.tar.gz",
#         ),
#     )

#     assert response is not None
#     assert response.data_storage.id is not None
#     assert len(response.storage_locations) > 0

#     fetch_response = admin_client.fetch_data_from_storage(response.data_storage.id)

#     assert isinstance(fetch_response, Path)
#     assert fetch_response.exists()


# @pytest.mark.timeout(300)
# @pytest.mark.asyncio
# async def test_register_existing_content_gcs_async_single_with_prefix(
#     admin_client: RestClient,
# ):
#     with pytest.raises(
#         DataStorageError,
#         match="Prefix is not allowed for single file GCS storage",
#     ):
#         await admin_client.aregister_existing_data_source(
#             name=f"E2E test entry gcs dir: {uuid4()}",
#             description="This is data that already exists",
#             as_collection=False,
#             existing_location=DataStorageLocationPayload(
#                 storage_type=DataStorageType.GCS,
#                 content_type=DataContentType.DIRECTORY,
#                 metadata={
#                     "bucket_name": "fh-pubmed-data",
#                     "prefix": "oa_package/00/00",
#                 },
#                 location="oa_package/00/00/PMC10054724.tar.gz",
#             ),
#         )


@pytest.mark.timeout(300)
def test_register_existing_content_postgres_sync(admin_client: RestClient):
    test_trajectory_id = "39510f66-c2ee-41c7-94de-64eb142c3f2a"

    response = admin_client.register_existing_data_source(
        name=f"E2E test entry postgres row: {uuid4()}",
        description="This is data that already exists",
        existing_location=DataStorageLocationPayload(
            storage_type=DataStorageType.PG_TABLE,
            content_type=DataContentType.TEXT,
            metadata={
                "table_name": "trajectories",
                "row_id": test_trajectory_id,
            },
        ),
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    fetch_response = admin_client.fetch_data_from_storage(response.data_storage.id)

    assert isinstance(fetch_response, str)
    assert json.loads(fetch_response).get("id") == test_trajectory_id

    admin_client.delete_data_storage_entry(response.data_storage.id)


@pytest.mark.timeout(300)
@pytest.mark.asyncio
async def test_register_existing_content_postgres_async(admin_client: RestClient):
    test_trajectory_id = "39510f66-c2ee-41c7-94de-64eb142c3f2a"

    response = await admin_client.aregister_existing_data_source(
        name=f"E2E test entry postgres row: {uuid4()}",
        description="This is data that already exists",
        existing_location=DataStorageLocationPayload(
            storage_type=DataStorageType.PG_TABLE,
            content_type=DataContentType.TEXT,
            metadata={
                "table_name": "trajectories",
                "row_id": test_trajectory_id,
            },
        ),
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    fetch_response = await admin_client.afetch_data_from_storage(
        response.data_storage.id
    )

    assert isinstance(fetch_response, str)
    assert json.loads(fetch_response).get("id") == test_trajectory_id

    await admin_client.adelete_data_storage_entry(response.data_storage.id)


@pytest.mark.timeout(300)
def test_register_existing_content_bigquery_sync(admin_client: RestClient):
    response = admin_client.register_existing_data_source(
        name=f"E2E test entry bigquery table: {uuid4()}",
        description="This is data that already exists",
        existing_location=DataStorageLocationPayload(
            storage_type=DataStorageType.BIGQUERY,
            content_type=DataContentType.TEXT,
            metadata={
                "project_id": "bigquery-public-data",
                "dataset_id": "samples",
                "table_id": "shakespeare",
            },
        ),
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    admin_client.delete_data_storage_entry(response.data_storage.id)


@pytest.mark.timeout(300)
@pytest.mark.asyncio
async def test_register_existing_content_bigquery_async(admin_client: RestClient):
    response = await admin_client.aregister_existing_data_source(
        name=f"E2E test entry bigquery table: {uuid4()}",
        description="This is data that already exists",
        existing_location=DataStorageLocationPayload(
            storage_type=DataStorageType.BIGQUERY,
            content_type=DataContentType.TEXT,
            metadata={
                "project_id": "bigquery-public-data",
                "dataset_id": "samples",
                "table_id": "shakespeare",
            },
        ),
    )

    assert response is not None
    assert response.data_storage.id is not None
    assert len(response.storage_locations) > 0

    await admin_client.adelete_data_storage_entry(response.data_storage.id)


@pytest.mark.timeout(300)
@pytest.mark.asyncio
async def test_dataset_async(admin_client: RestClient):
    dataset_name_id = uuid4()
    create_response = await admin_client.acreate_dataset(
        name=f"E2E test dataset: {dataset_name_id}",
        description="This is a test dataset",
    )

    assert create_response is not None
    assert create_response.id is not None
    assert create_response.name == f"E2E test dataset: {dataset_name_id}"
    assert create_response.description == "This is a test dataset"

    get_response = await admin_client.aget_dataset(dataset_id=create_response.id)

    assert get_response is not None
    assert get_response["dataset"]["id"] == str(create_response.id)
    assert get_response["data_storage_entries"] == []

    await admin_client.adelete_dataset(dataset_id=create_response.id)

    with pytest.raises(DataStorageError, match="Failed to get dataset"):
        await admin_client.aget_dataset(dataset_id=create_response.id)


@pytest.mark.timeout(300)
def test_dataset_sync(admin_client: RestClient):
    dataset_name_id = uuid4()
    create_response = admin_client.create_dataset(
        name=f"E2E test dataset: {dataset_name_id}",
        description="This is a test dataset",
    )

    assert create_response is not None
    assert create_response.id is not None
    assert create_response.name == f"E2E test dataset: {dataset_name_id}"

    get_response = admin_client.get_dataset(dataset_id=create_response.id)

    assert get_response is not None
    assert get_response["dataset"]["id"] == str(create_response.id)
    assert get_response["data_storage_entries"] == []

    admin_client.delete_dataset(dataset_id=create_response.id)

    with pytest.raises(DataStorageError, match="Failed to get dataset"):
        admin_client.get_dataset(dataset_id=create_response.id)


@pytest.mark.asyncio
async def test_astore_link_success(admin_client: RestClient):
    """Test successful asynchronous link storage."""
    result = await admin_client.astore_link(
        name="Test API Link",
        url=HttpUrl("https://xyz.api.futurehouse.org"),
        description="Test link to xyz.api.futurehouse.org",
        instructions="this is a test api which you can call without authentication",
        api_key="test_key_123",
    )

    assert result.data_storage.id is not None
    assert result.data_storage.name == "Test API Link"
    assert result.data_storage.description == "Test link to xyz.api.futurehouse.org"
    assert result.data_storage.content == "https://xyz.api.futurehouse.org/"
    assert len(result.storage_locations) > 0
    assert result.storage_locations[0].storage_config.storage_type == "link"
    assert (
        result.storage_locations[0].storage_config.location
        == "https://xyz.api.futurehouse.org/"
    )
