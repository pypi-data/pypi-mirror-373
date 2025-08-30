# ruff: noqa: ARG001
# ruff: noqa: SIM117

import asyncio
import os
import tempfile
import time
import types
from pathlib import Path
from typing import cast
from unittest.mock import MagicMock, Mock, mock_open, patch
from uuid import UUID, uuid4

import pytest
from httpx import (
    CloseError,
    ConnectError,
    ConnectTimeout,
    HTTPStatusError,
    NetworkError,
    ReadError,
    ReadTimeout,
    RemoteProtocolError,
)
from pytest_subtests import SubTests
from requests.exceptions import RequestException, Timeout

from futurehouse_client.clients import (
    JobNames,
)
from futurehouse_client.clients.rest_client import (
    FileUploadError,
    ProjectError,
    RestClient,
    RestClientError,
    UserAgentRequestCreationError,
    UserAgentRequestFetchError,
)
from futurehouse_client.models.app import (
    PhoenixTaskResponse,
    PQATaskResponse,
    Stage,
    TaskRequest,
    TaskResponseVerbose,
)
from futurehouse_client.models.rest import (
    ExecutionStatus,
    UserAgentRequestPostPayload,
    UserAgentRequestStatus,
    UserAgentResponsePayload,
    WorldModel,
)
from futurehouse_client.utils.general import create_retry_if_connection_error

ADMIN_API_KEY = os.environ.get("PLAYWRIGHT_ADMIN_API_KEY", "")
PUBLIC_API_KEY = os.environ.get("PLAYWRIGHT_PUBLIC_API_KEY", "")
TEST_MAX_POLLS = 100


@pytest.fixture(name="admin_client")
def fixture_admin_client():
    """Create a RestClient for testing; using an admin key."""
    return RestClient(
        stage=Stage.DEV,
        api_key=ADMIN_API_KEY,
    )


@pytest.fixture(name="pub_client")
def fixture_pub_client():
    """Create a RestClient for testing; using a public user key with limited access."""
    return RestClient(
        stage=Stage.DEV,
        api_key=PUBLIC_API_KEY,
    )


@pytest.fixture(name="task_req")
def fixture_task_req():
    """Create a sample task request."""
    return TaskRequest(
        name=JobNames.from_string("dummy"),
        query="How many moons does earth have?",
    )


@pytest.fixture(name="pqa_task_req")
def fixture_pqa_task_req():
    return TaskRequest(
        name=JobNames.from_string("crow"),
        query="How many moons does earth have?",
    )


@pytest.fixture(name="phoenix_task_req")
def fixture_phoenix_task_req():
    return TaskRequest(
        name=JobNames.from_string("phoenix"),
        query="What is the molecular weight of ascorbic acids?",
    )


@pytest.fixture(name="running_trajectory_id")
def fixture_running_trajectory_id(
    admin_client: RestClient, task_req: TaskRequest
) -> str:
    return admin_client.create_task(task_req)


@pytest.mark.timeout(300)
@pytest.mark.flaky(reruns=3)
def test_futurehouse_dummy_env_crow(admin_client: RestClient, task_req: TaskRequest):
    admin_client.create_task(task_req)
    while (task_status := admin_client.get_task().status) in {"queued", "in progress"}:
        time.sleep(5)
    assert task_status == "success"


def test_insufficient_permissions_request(
    pub_client: RestClient, task_req: TaskRequest
):
    # Create a new instance so that cached credentials aren't reused
    with pytest.raises(PermissionError) as exc_info:
        pub_client.create_task(task_req)

    assert "Error creating task" in str(exc_info.value)


@pytest.mark.timeout(300)
@pytest.mark.asyncio
async def test_job_response(  # noqa: PLR0915
    subtests: SubTests,
    admin_client: RestClient,
    pqa_task_req: TaskRequest,
    phoenix_task_req: TaskRequest,
):
    task_id = admin_client.create_task(pqa_task_req)
    atask_id = await admin_client.acreate_task(pqa_task_req)
    phoenix_task_id = admin_client.create_task(phoenix_task_req)
    aphoenix_task_id = await admin_client.acreate_task(phoenix_task_req)

    with subtests.test("Test TaskResponse with queued task"):
        task_response = admin_client.get_task(task_id)
        assert task_response.status in {"queued", "in progress"}
        assert task_response.job_name == pqa_task_req.name
        assert task_response.query == pqa_task_req.query
        task_response = await admin_client.aget_task(atask_id)
        assert task_response.status in {"queued", "in progress"}
        assert task_response.job_name == pqa_task_req.name
        assert task_response.query == pqa_task_req.query

    for _ in range(TEST_MAX_POLLS):
        task_response = admin_client.get_task(task_id)
        if task_response.status in ExecutionStatus.terminal_states():
            break
        await asyncio.sleep(5)

    for _ in range(TEST_MAX_POLLS):
        task_response = await admin_client.aget_task(atask_id)
        if task_response.status in ExecutionStatus.terminal_states():
            break
        await asyncio.sleep(5)

    with subtests.test("Test PQA job response"):
        task_response = admin_client.get_task(task_id)
        assert isinstance(task_response, PQATaskResponse)
        # assert it has general fields
        assert task_response.status == "success"
        assert task_response.task_id is not None
        assert pqa_task_req.name in task_response.job_name
        assert pqa_task_req.query in task_response.query
        # assert it has PQA specific fields
        assert task_response.answer is not None
        # assert it's not verbose
        assert not hasattr(task_response, "environment_frame")
        assert not hasattr(task_response, "agent_state")

    with subtests.test("Test async PQA job response"):
        task_response = await admin_client.aget_task(atask_id)
        assert isinstance(task_response, PQATaskResponse)
        # assert it has general fields
        assert task_response.status == "success"
        assert task_response.task_id is not None
        assert pqa_task_req.name in task_response.job_name
        assert pqa_task_req.query in task_response.query
        # assert it has PQA specific fields
        assert task_response.answer is not None
        # assert it's not verbose
        assert not hasattr(task_response, "environment_frame")
        assert not hasattr(task_response, "agent_state")

    with subtests.test("Test Phoenix job response"):
        task_response = admin_client.get_task(phoenix_task_id)
        assert isinstance(task_response, PhoenixTaskResponse)
        assert task_response.status == "success"
        assert task_response.task_id is not None
        assert phoenix_task_req.name in task_response.job_name
        assert phoenix_task_req.query in task_response.query

    with subtests.test("Test async Phoenix job response"):
        task_response = await admin_client.aget_task(aphoenix_task_id)
        assert isinstance(task_response, PhoenixTaskResponse)
        assert task_response.status == "success"
        assert task_response.task_id is not None
        assert phoenix_task_req.name in task_response.job_name
        assert phoenix_task_req.query in task_response.query

    with subtests.test("Test task response with verbose"):
        task_response = admin_client.get_task(task_id, verbose=True)
        assert isinstance(task_response, TaskResponseVerbose)
        assert task_response.status == "success"
        assert task_response.environment_frame is not None
        assert task_response.agent_state is not None

    with subtests.test("Test task async response with verbose"):
        task_response = await admin_client.aget_task(atask_id, verbose=True)
        assert isinstance(task_response, TaskResponseVerbose)
        assert task_response.status == "success"
        assert task_response.environment_frame is not None
        assert task_response.agent_state is not None


@pytest.mark.timeout(300)
@pytest.mark.flaky(reruns=3)
def test_run_until_done_futurehouse_dummy_env_crow(
    admin_client: RestClient, task_req: TaskRequest
):
    tasks_to_do = [task_req, task_req]

    results = admin_client.run_tasks_until_done(tasks_to_do)

    assert len(results) == len(tasks_to_do), "Should return 2 tasks."
    assert all(task.status == "success" for task in results)


@pytest.mark.timeout(300)
@pytest.mark.flaky(reruns=3)
@pytest.mark.asyncio
async def test_arun_until_done_futurehouse_dummy_env_crow(
    admin_client: RestClient, task_req: TaskRequest
):
    tasks_to_do = [task_req, task_req]

    results = await admin_client.arun_tasks_until_done(tasks_to_do)

    assert len(results) == len(tasks_to_do), "Should return 2 tasks."
    assert all(task.status == "success" for task in results)


@pytest.mark.timeout(300)
@pytest.mark.flaky(reruns=3)
@pytest.mark.asyncio
async def test_timeout_run_until_done_futurehouse_dummy_env_crow(
    admin_client: RestClient, task_req: TaskRequest
):
    tasks_to_do = [task_req, task_req]

    results = await admin_client.arun_tasks_until_done(
        tasks_to_do, verbose=True, timeout=5, progress_bar=True
    )

    assert len(results) == len(tasks_to_do), "Should return 2 tasks."
    assert all(task.status != "success" for task in results), "Should not be success."
    assert all(not isinstance(task, PQATaskResponse) for task in results), (
        "Should be verbose."
    )

    results = admin_client.run_tasks_until_done(
        tasks_to_do, verbose=True, timeout=5, progress_bar=True
    )

    assert len(results) == len(tasks_to_do), "Should return 2 tasks."
    assert all(task.status != "success" for task in results), "Should not be success."
    assert all(not isinstance(task, PQATaskResponse) for task in results), (
        "Should be verbose."
    )


@pytest.mark.timeout(300)
@pytest.mark.flaky(reruns=3)
def test_cancel_task(admin_client: RestClient):
    """Test successful task cancellation using MagicMock."""
    task_id = "1c28bb94-efbf-442f-954c-f0d8ddb0cff5"

    with (
        patch.object(admin_client.client, "post") as mock_post,
        patch.object(admin_client, "get_task") as mock_get_task,
    ):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        mock_task_response_running = MagicMock()
        mock_task_response_running.status = "in progress"

        mock_task_response_cancelled = MagicMock()
        mock_task_response_cancelled.status = ExecutionStatus.CANCELLED.value

        mock_get_task.side_effect = [
            mock_task_response_running,
            mock_task_response_cancelled,
        ]

        result = admin_client.cancel_task(task_id)

        assert result is True

        expected_url = f"/v0.1/trajectories/{task_id}/cancel"
        mock_post.assert_called_once_with(expected_url)

        assert mock_get_task.call_count == 2


class TestParallelChunking:
    """Test suite for parallel chunk upload functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock RestClient for testing."""
        # we don't need a real RestClient auth here
        client = MagicMock(spec=RestClient)
        client.CHUNK_SIZE = 16 * 1024 * 1024  # 16MB
        client.MAX_CONCURRENT_CHUNKS = 12
        client.multipart_client = MagicMock()

        # Set up the real methods we want to test by properly binding them
        client._upload_chunks_parallel = types.MethodType(
            RestClient._upload_chunks_parallel, client
        )
        client._upload_single_chunk = types.MethodType(
            RestClient._upload_single_chunk, client
        )
        client._upload_single_file = types.MethodType(
            RestClient._upload_single_file, client
        )
        client._upload_directory = types.MethodType(
            RestClient._upload_directory, client
        )
        client.upload_file = types.MethodType(RestClient.upload_file, client)
        client._wait_for_all_assemblies_completion = MagicMock(return_value=True)

        return client

    @pytest.fixture
    def large_file_content(self):
        """Create content for a large file that will be chunked."""
        # Create content larger than CHUNK_SIZE (16MB)
        chunk_size = 16 * 1024 * 1024
        return b"A" * (chunk_size * 2 + 1000)  # ~32MB + 1000 bytes

    @pytest.fixture
    def small_file_content(self):
        """Create content for a small file that won't be chunked."""
        return b"Small file content"

    def test_upload_small_file_no_chunking(self, mock_client):
        """Test uploading a small file that doesn't require chunking."""
        job_name = "test-job"
        file_content = b"Small file content"

        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status_url": "http://test.com/status"}
        mock_client.multipart_client.post.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

            try:
                # Mock assembly completion
                with patch.object(
                    mock_client,
                    "_wait_for_all_assemblies_completion",
                    return_value=True,
                ):
                    upload_id = mock_client.upload_file(job_name, temp_path)

                # Verify upload was called once (single chunk)
                assert mock_client.multipart_client.post.call_count == 1
                assert upload_id is not None

                # Verify the post call was made with correct endpoint
                call_args = mock_client.multipart_client.post.call_args
                assert f"/v0.1/crows/{job_name}/upload-chunk" in call_args[0][0]
            finally:
                temp_path.unlink()

    def test_upload_large_file_with_chunking(self, mock_client, large_file_content):
        """Test uploading a large file that requires chunking and parallel uploads."""
        job_name = "test-job"

        # Mock successful responses for all chunks
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status_url": "http://test.com/status"}
        mock_response.status_code = 200
        mock_client.multipart_client.post.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(large_file_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

            try:
                # Mock assembly completion
                with patch.object(
                    mock_client,
                    "_wait_for_all_assemblies_completion",
                    return_value=True,
                ):
                    upload_id = mock_client.upload_file(job_name, temp_path)

                # Verify multiple chunks were uploaded
                # File size: ~32MB + 1000 bytes, chunk size: 16MB
                # Expected chunks: 3 (16MB + 16MB + 1000 bytes)
                expected_chunks = 3
                assert mock_client.multipart_client.post.call_count == expected_chunks
                assert upload_id is not None

                # Verify all calls were to the upload-chunk endpoint
                for call in mock_client.multipart_client.post.call_args_list:
                    assert f"/v0.1/crows/{job_name}/upload-chunk" in call[0][0]
            finally:
                temp_path.unlink()

    def test_upload_chunks_parallel_batch_processing(self, mock_client):
        """Test that chunks are processed in parallel batches."""
        job_name = "test-job"
        file_path = Path("test_file.txt")
        file_name = "test_file.txt"
        upload_id = "test-upload-id"
        num_regular_chunks = 5  # Smaller number for easier testing
        total_chunks = 6

        # Mock file content for final chunk
        chunk_content = b"A" * 1000

        # Mock final chunk response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status_url": "http://test.com/status"}
        mock_client.multipart_client.post.return_value = mock_response

        # Use patch to mock the _upload_single_chunk method and file operations
        with patch.object(mock_client, "_upload_single_chunk") as mock_upload_chunk:
            with patch("builtins.open", mock_open(read_data=chunk_content)):
                with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
                    mock_temp_file.return_value.__enter__.return_value.name = (
                        "temp_chunk"
                    )

                    # Call the method - it should use ThreadPoolExecutor internally
                    mock_client._upload_chunks_parallel(
                        job_name,
                        file_path,
                        file_name,
                        upload_id,
                        total_chunks,
                    )

            # Verify all regular chunks were processed by checking the call count
            assert mock_upload_chunk.call_count == num_regular_chunks

            # Verify the calls were made with correct parameters
            for call_idx, call in enumerate(mock_upload_chunk.call_args_list):
                args = call[0]
                assert args[0] == job_name
                assert args[1] == file_path
                assert args[2] == file_name
                assert args[3] == upload_id
                assert args[4] == call_idx  # chunk_index
                assert args[5] == total_chunks

    def test_upload_single_chunk_success(self, mock_client):
        """Test successful upload of a single chunk."""
        job_name = "test-job"
        file_path = Path("test_file.txt")
        file_name = "test_file.txt"
        upload_id = "test-upload-id"
        chunk_index = 0
        total_chunks = 5

        # Mock file content
        chunk_content = b"A" * mock_client.CHUNK_SIZE

        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_client.multipart_client.post.return_value = mock_response

        with patch("builtins.open", mock_open(read_data=chunk_content)):
            with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
                # Setup mock temporary file
                mock_temp_file.return_value.__enter__.return_value.name = "temp_chunk"

                mock_client._upload_single_chunk(
                    job_name, file_path, file_name, upload_id, chunk_index, total_chunks
                )

                # Verify the upload was called with correct parameters
                mock_client.multipart_client.post.assert_called_once()
                call_args = mock_client.multipart_client.post.call_args

                # Check endpoint
                assert f"/v0.1/crows/{job_name}/upload-chunk" in call_args[0][0]

                # Check data parameters
                data = call_args[1]["data"]
                assert data["file_name"] == file_name
                assert data["chunk_index"] == chunk_index
                assert data["total_chunks"] == total_chunks
                assert data["upload_id"] == upload_id

    def test_upload_chunks_parallel_retry_on_conflict(self, mock_client):
        """Test final chunk upload with retry logic for missing chunks (409 conflict)."""
        job_name = "test-job"
        file_path = Path("test_file.txt")
        file_name = "test_file.txt"
        upload_id = "test-upload-id"
        total_chunks = 1

        # Mock file content
        chunk_content = b"A" * 1000

        # Create mock responses: first returns 409 (conflict), second succeeds
        mock_response_conflict = MagicMock()
        mock_response_conflict.status_code = 409  # CONFLICT
        mock_response_conflict.raise_for_status.side_effect = None

        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.raise_for_status.return_value = None
        mock_response_success.json.return_value = {
            "status_url": "http://test.com/status"
        }

        mock_client.multipart_client.post.side_effect = [
            mock_response_conflict,
            mock_response_success,
        ]

        with patch("builtins.open", mock_open(read_data=chunk_content)):
            with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
                with patch("time.sleep") as mock_sleep:  # Speed up test
                    mock_temp_file.return_value.__enter__.return_value.name = (
                        "temp_chunk"
                    )

                    status_url = mock_client._upload_chunks_parallel(
                        job_name,
                        file_path,
                        file_name,
                        upload_id,
                        total_chunks,
                    )

                    # Verify retry was attempted
                    assert mock_client.multipart_client.post.call_count == 2
                    assert status_url == "http://test.com/status"
                    mock_sleep.assert_called_once()  # Verify sleep was called for retry

    def test_upload_chunks_parallel_final_chunk_max_retries_exceeded(self, mock_client):
        """Test final chunk upload fails after max retries."""
        job_name = "test-job"
        file_path = Path("test_file.txt")
        file_name = "test_file.txt"
        upload_id = "test-upload-id"
        total_chunks = 1

        # Mock file content
        chunk_content = b"A" * 1000

        # Create a side effect that simulates an exception on every attempt
        def side_effect(*args, **kwargs):
            raise Exception("Simulated upload failure")  # noqa: TRY002

        mock_client.multipart_client.post.side_effect = side_effect

        from httpx import codes

        with patch("builtins.open", mock_open(read_data=chunk_content)):
            with patch("tempfile.NamedTemporaryFile") as mock_temp_file:
                with patch("time.sleep"):  # Speed up test
                    # Set up the code constant correctly
                    with patch("futurehouse_client.clients.rest_client.codes", codes):
                        mock_temp_file.return_value.__enter__.return_value.name = (
                            "temp_chunk"
                        )

                        with pytest.raises(
                            FileUploadError, match="Error uploading final chunk"
                        ):
                            mock_client._upload_chunks_parallel(
                                job_name,
                                file_path,
                                file_name,
                                upload_id,
                                total_chunks,
                            )

                # Verify that retries were attempted (should be 3 attempts total)
                assert mock_client.multipart_client.post.call_count == 3

    def test_upload_directory_recursive(self, mock_client):
        """Test uploading a directory with nested files."""
        job_name = "test-job"

        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status_url": "http://test.com/status"}
        mock_client.multipart_client.post.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create nested directory structure
            (temp_path / "subdir").mkdir()
            (temp_path / "file1.txt").write_text("content1")
            (temp_path / "file2.txt").write_text("content2")
            (temp_path / "subdir" / "file3.txt").write_text("content3")

            # Mock assembly completion
            with patch.object(
                mock_client, "_wait_for_all_assemblies_completion", return_value=True
            ):
                upload_id_result = mock_client.upload_file(job_name, temp_path)

            # Verify files were uploaded (3 files total)
            assert mock_client.multipart_client.post.call_count == 3
            # Just check that we got some upload_id back (it will be a UUID)
            assert upload_id_result is not None
            assert len(upload_id_result) > 0

            # Verify calls were made to upload-chunk endpoint
            for call in mock_client.multipart_client.post.call_args_list:
                assert f"/v0.1/crows/{job_name}/upload-chunk" in call[0][0]

    def test_upload_file_assembly_failure(self, mock_client):
        """Test upload_file raises error when assembly fails."""
        job_name = "test-job"
        file_content = b"test content"

        # Mock successful upload but failed assembly
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status_url": "http://test.com/status"}
        mock_client.multipart_client.post.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

            try:
                # Mock assembly failure
                with (
                    patch.object(
                        mock_client,
                        "_wait_for_all_assemblies_completion",
                        return_value=False,
                    ),
                    pytest.raises(
                        RestClientError, match="Assembly failed or timed out"
                    ),
                ):
                    mock_client.upload_file(job_name, temp_path)
            finally:
                temp_path.unlink()

    def test_upload_file_skip_assembly_wait(self, mock_client):
        """Test upload_file with wait_for_assembly=False."""
        job_name = "test-job"
        file_content = b"test content"

        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"status_url": "http://test.com/status"}
        mock_client.multipart_client.post.return_value = mock_response

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file.flush()
            temp_path = Path(temp_file.name)

            try:
                with patch.object(
                    mock_client, "_wait_for_all_assemblies_completion"
                ) as mock_wait:
                    upload_id = mock_client.upload_file(
                        job_name, temp_path, wait_for_assembly=False
                    )

                    # Verify assembly wait was not called
                    mock_wait.assert_not_called()
                    assert upload_id is not None
            finally:
                temp_path.unlink()

    def test_max_concurrent_chunks_constant(self, mock_client):
        """Test that MAX_CONCURRENT_CHUNKS constant is properly set."""
        assert mock_client.MAX_CONCURRENT_CHUNKS == 12
        assert isinstance(mock_client.MAX_CONCURRENT_CHUNKS, int)
        assert mock_client.MAX_CONCURRENT_CHUNKS > 0

    def test_upload_empty_file_handled(self, mock_client):
        """Test that empty files are handled gracefully."""
        job_name = "test-job"

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            # Create empty file
            temp_file.flush()
            temp_path = Path(temp_file.name)

            try:
                # Mock assembly completion
                with patch.object(
                    mock_client,
                    "_wait_for_all_assemblies_completion",
                    return_value=True,
                ):
                    upload_id = mock_client.upload_file(job_name, temp_path)

                # Should not call post since empty files are skipped
                assert mock_client.multipart_client.post.call_count == 0
                assert upload_id is not None
            finally:
                temp_path.unlink()

    def test_chunk_size_calculation(self, mock_client):
        """Test that chunk size calculation works correctly."""
        file_size = 32 * 1024 * 1024 + 1000  # 32MB + 1000 bytes
        chunk_size = mock_client.CHUNK_SIZE  # 16MB

        expected_total_chunks = (file_size + chunk_size - 1) // chunk_size
        assert expected_total_chunks == 3  # 16MB + 16MB + ~1000 bytes

        # Test edge cases
        assert (
            (chunk_size - 1) + chunk_size - 1
        ) // chunk_size == 1  # Just under 1 chunk
        assert (chunk_size + chunk_size - 1) // chunk_size == 1  # Exactly 1 chunk
        assert (
            (chunk_size + 1) + chunk_size - 1
        ) // chunk_size == 2  # Just over 1 chunk


@pytest.mark.asyncio
async def test_world_model_acreate_and_aget(admin_client: RestClient):
    model = WorldModel(
        content="test content",
        name="Test Model",
        description="This is a test model.",
    )
    model_id = await admin_client.acreate_world_model(model)

    # try getting the newly created model by id
    model_by_id = await admin_client.aget_world_model(model_id)

    assert str(model_by_id.id) == str(model_id)
    assert model_by_id.content == model.content

    updated_model = WorldModel(
        content="updated test content",
        prior=model_id,
    )

    updated_model_id = await admin_client.acreate_world_model(updated_model)

    # try getting the newly created model by id
    updated_model_by_id = await admin_client.aget_world_model(updated_model_id)

    assert updated_model_by_id.name == model.name
    assert updated_model_by_id.content != model.content


def test_world_model_create_and_get(admin_client: RestClient):
    model = WorldModel(
        content="test content",
        name="Test Model",
        description="This is a test model.",
    )
    model_id = admin_client.create_world_model(model)

    # try getting the newly created model by id
    model_by_id = admin_client.get_world_model(model_id)

    assert str(model_by_id.id) == str(model_id)
    assert model_by_id.content == model.content

    updated_model = WorldModel(
        content="updated test content",
        prior=model_id,
    )

    updated_model_id = admin_client.create_world_model(updated_model)

    # try getting the newly created model by id
    updated_model_by_id = admin_client.get_world_model(updated_model_id)

    assert updated_model_by_id.name == model.name
    assert updated_model_by_id.content != model.content


class TestProjectOperations:
    @pytest.fixture
    def test_project_name(self):
        return f"test-project-{uuid4()}"

    def test_create_project_success(
        self, admin_client: RestClient, test_project_name: str
    ):
        project_id = admin_client.create_project(test_project_name)
        assert isinstance(project_id, str)
        UUID(project_id)

    def test_get_project_by_name_success(
        self, admin_client: RestClient, test_project_name: str
    ):
        created_project_id = admin_client.create_project(test_project_name)
        retrieved_project_id = admin_client.get_project_by_name(test_project_name)
        assert str(retrieved_project_id) == created_project_id

    def test_get_project_by_name_not_found(self, admin_client: RestClient):
        with pytest.raises(ProjectError, match="No project found with name"):
            admin_client.get_project_by_name("non-existent-project-12345")

    def test_get_project_by_name_multiple_found(self, admin_client: RestClient):
        with patch.object(admin_client.client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = [
                {"id": str(uuid4()), "name": "test"},
                {"id": str(uuid4()), "name": "test"},
            ]
            mock_get.return_value = mock_response

            projects = admin_client.get_project_by_name("test")
            assert isinstance(projects, list)
            assert len(projects) == 2

    def test_add_task_to_project_success(
        self, admin_client: RestClient, test_project_name: str, task_req: TaskRequest
    ):
        project_id = admin_client.create_project(test_project_name)
        trajectory_id = admin_client.create_task(task_req)
        admin_client.add_task_to_project(UUID(project_id), trajectory_id)

    def test_add_task_to_project_not_found(self, admin_client: RestClient):
        fake_project_id = uuid4()
        fake_trajectory_id = str(uuid4())

        with patch.object(admin_client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = Exception("404 Not Found")
            mock_post.return_value = mock_response

            with pytest.raises(
                ProjectError, match="Error adding trajectory to project"
            ):
                admin_client.add_task_to_project(fake_project_id, fake_trajectory_id)

    def test_create_project_with_http_error(self, admin_client: RestClient):
        with patch.object(admin_client.client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = Exception("400 Bad Request")
            mock_response.status_code = 400
            mock_response.text = "Invalid project name"
            mock_post.return_value = mock_response

            with pytest.raises(ProjectError, match="Error creating project"):
                admin_client.create_project("invalid project name")


class TestAsyncProjectOperations:
    @pytest.fixture
    def test_project_name(self):
        return f"test-async-project-{uuid4()}"

    @pytest.mark.asyncio
    async def test_acreate_project_success(
        self, admin_client: RestClient, test_project_name: str
    ):
        project_id = await admin_client.acreate_project(test_project_name)
        assert isinstance(project_id, str)
        UUID(project_id)

    @pytest.mark.asyncio
    async def test_aget_project_by_name_success(
        self, admin_client: RestClient, test_project_name: str
    ):
        created_project_id = await admin_client.acreate_project(test_project_name)
        retrieved_project_id = await admin_client.aget_project_by_name(
            test_project_name
        )
        assert str(retrieved_project_id) == created_project_id

    @pytest.mark.asyncio
    async def test_aget_project_by_name_not_found(self, admin_client: RestClient):
        with pytest.raises(ProjectError, match="No project found with name"):
            await admin_client.aget_project_by_name("non-existent-async-project-12345")

    @pytest.mark.asyncio
    async def test_aadd_task_to_project_success(
        self, admin_client: RestClient, test_project_name: str, task_req: TaskRequest
    ):
        project_id = await admin_client.acreate_project(test_project_name)
        trajectory_id = await admin_client.acreate_task(task_req)
        await admin_client.aadd_task_to_project(UUID(project_id), trajectory_id)

    @pytest.mark.asyncio
    async def test_aadd_task_to_project_permission_denied(
        self, admin_client: RestClient
    ):
        fake_project_id = uuid4()
        fake_trajectory_id = str(uuid4())

        with patch.object(admin_client.async_client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = Exception("403 Forbidden")
            mock_response.status_code = 403
            mock_post.return_value = mock_response

            with pytest.raises(
                ProjectError, match="Error adding trajectory to project: 403 Forbidden"
            ):
                await admin_client.aadd_task_to_project(
                    fake_project_id, fake_trajectory_id
                )


@pytest.mark.timeout(300)
@pytest.mark.flaky(reruns=3)
def test_get_tasks_with_project_filter(admin_client: RestClient, task_req: TaskRequest):
    """Test retrieving trajectories filtered by project_id using real API calls."""
    project_name = f"e2e-trajectories-fetch-{uuid4()}"
    project_id = admin_client.create_project(project_name)

    trajectory_id = admin_client.create_task(task_req)
    admin_client.add_task_to_project(UUID(project_id), trajectory_id)

    while (task_status := admin_client.get_task(trajectory_id).status) in {
        "queued",
        "in progress",
    }:
        time.sleep(5)

    trajectories = admin_client.get_tasks(project_id=UUID(project_id))

    trajectory_ids = [t["id"] for t in trajectories]
    assert trajectory_id in trajectory_ids


@pytest.mark.timeout(300)
@pytest.mark.flaky(reruns=3)
@pytest.mark.asyncio
async def test_aget_tasks_with_project_filter(
    admin_client: RestClient, task_req: TaskRequest
):
    """Test async retrieving trajectories filtered by project_id using real API calls."""
    project_name = f"e2e-trajectories-async-fetch-{uuid4()}"
    project_id = await admin_client.acreate_project(project_name)

    trajectory_id = await admin_client.acreate_task(task_req)
    await admin_client.aadd_task_to_project(UUID(project_id), trajectory_id)

    while True:
        task = await admin_client.aget_task(trajectory_id)
        if task.status not in {"queued", "in progress"}:
            break
        await asyncio.sleep(5)

    trajectories = await admin_client.aget_tasks(project_id=UUID(project_id))

    trajectory_ids = [t["id"] for t in trajectories]
    assert trajectory_id in trajectory_ids


class TestUserAgentRequestOperations:
    """Test suite for synchronous User Agent Request operations."""

    @pytest.mark.flaky(reruns=3)
    def test_e2e_user_agent_request_flow(
        self,
        admin_client: RestClient,
        running_trajectory_id: str,
    ):
        """Tests the full lifecycle: create, get, list, and respond."""
        payload = UserAgentRequestPostPayload(
            trajectory_id=running_trajectory_id,
            request={"question": "Do you approve?"},
            notify_user={"email": False, "sms": False},  # avoid sending notifications
        )
        request_id = admin_client.create_user_agent_request(payload)
        assert isinstance(request_id, UUID)

        # 2. GET the created request
        retrieved_req = admin_client.get_user_agent_request(request_id)
        assert retrieved_req.id == request_id
        assert str(retrieved_req.trajectory_id) == str(payload.trajectory_id)
        assert retrieved_req.status == UserAgentRequestStatus.PENDING
        assert retrieved_req.request == payload.request

        # 3. LIST requests and find the created one
        request_list = admin_client.list_user_agent_requests(
            trajectory_id=UUID(running_trajectory_id),
            request_status=UserAgentRequestStatus.PENDING,
        )
        assert isinstance(request_list, list)
        assert any(req.id == request_id for req in request_list)

        # 4. RESPOND to the request
        response_payload = UserAgentResponsePayload(response={"answer": "Yes"})
        admin_client.respond_to_user_agent_request(request_id, response_payload)

        # 5. GET the request again to verify the response
        responded_req = admin_client.get_user_agent_request(request_id)
        assert responded_req.status == UserAgentRequestStatus.RESPONDED
        assert responded_req.response == response_payload.response

    def test_get_nonexistent_request_fails(self, admin_client: RestClient):
        """Verifies that fetching a non-existent request raises an error."""
        non_existent_id = uuid4()
        with pytest.raises(UserAgentRequestFetchError):
            admin_client.get_user_agent_request(non_existent_id)

    def test_unauthorized_access_fails(self, pub_client: RestClient):
        """Ensures a client with insufficient permissions cannot perform actions."""
        # Using a public client that shouldn't have access
        with pytest.raises((UserAgentRequestCreationError, PermissionError)):  # noqa: PT012
            payload = UserAgentRequestPostPayload(
                trajectory_id=uuid4(),
                request={"data": "test"},
            )
            pub_client.create_user_agent_request(payload)

        with pytest.raises((UserAgentRequestFetchError, PermissionError)):
            # Attempt to fetch a request that the user doesn't own
            pub_client.get_user_agent_request(uuid4())


class TestAsyncUserAgentRequestOperations:
    """Test suite for asynchronous User Agent Request operations."""

    @pytest.mark.asyncio
    async def test_async_expiring_e2e_user_agent_request_flow(
        self,
        admin_client: RestClient,
        running_trajectory_id: str,
    ):
        """Tests the full async lifecycle: acreate, aget, alist, and arespond."""
        payload = UserAgentRequestPostPayload(
            trajectory_id=running_trajectory_id,
            request={"question": "Async: Do you approve?"},
            user_response_task=TaskRequest(
                name=JobNames.from_string("dummy"),
                query="Why would I follow up on this query?",
            ).model_dump(mode="json"),
            expires_in_seconds=10,
            notify_user={"email": False, "sms": False},  # avoid sending notifications
        )

        request_id = await admin_client.acreate_user_agent_request(payload)
        assert isinstance(request_id, UUID)

        retrieved_req = await admin_client.aget_user_agent_request(request_id)
        assert retrieved_req.id == request_id
        assert str(retrieved_req.trajectory_id) == str(payload.trajectory_id)
        assert retrieved_req.status == UserAgentRequestStatus.PENDING

        request_list = await admin_client.alist_user_agent_requests(
            trajectory_id=UUID(running_trajectory_id)
        )
        assert isinstance(request_list, list)
        assert any(req.id == request_id for req in request_list)

        # ensure we allow it to expire so auto response can happen
        await asyncio.sleep(10)

        # now this should be expired
        retrieved_req = await admin_client.aget_user_agent_request(request_id)
        assert retrieved_req.status == UserAgentRequestStatus.EXPIRED

        # we should also see the job having started -- along with the registration of the job in the
        job_data = await admin_client.aget_task(
            cast(str, retrieved_req.response_trajectory_id)
        )
        assert job_data.status in {"queued", "in progress"}

        # 4. RESPOND to the request -- ensure nothing changes
        ignored_response = {"answer": "Async Yes"}
        response_payload = UserAgentResponsePayload(response=ignored_response)
        await admin_client.arespond_to_user_agent_request(request_id, response_payload)

        retrieved_req = await admin_client.aget_user_agent_request(request_id)
        assert retrieved_req.response != ignored_response

    @pytest.mark.asyncio
    async def test_async_e2e_user_agent_request_flow(
        self,
        admin_client: RestClient,
        running_trajectory_id: str,
    ):
        """Tests the full async lifecycle: acreate, aget, alist, and arespond."""
        # 1. CREATE a request
        payload = UserAgentRequestPostPayload(
            trajectory_id=running_trajectory_id,
            request={"question": "Async: Do you approve?"},
            user_response_task=TaskRequest(
                name=JobNames.from_string("dummy"),
                query="Why would I follow up on this query?",
            ).model_dump(mode="json"),
            notify_user={"email": False, "sms": False},  # avoid sending notifications
        )

        request_id = await admin_client.acreate_user_agent_request(payload)
        assert isinstance(request_id, UUID)

        # 2. GET the created request
        retrieved_req = await admin_client.aget_user_agent_request(request_id)
        assert retrieved_req.id == request_id
        assert str(retrieved_req.trajectory_id) == str(payload.trajectory_id)
        assert retrieved_req.status == UserAgentRequestStatus.PENDING

        # 3. LIST requests and find the created one
        request_list = await admin_client.alist_user_agent_requests(
            trajectory_id=UUID(running_trajectory_id)
        )
        assert isinstance(request_list, list)
        assert any(req.id == request_id for req in request_list)

        # 4. RESPOND to the request
        response_payload = UserAgentResponsePayload(response={"answer": "Async Yes"})
        await admin_client.arespond_to_user_agent_request(request_id, response_payload)

        # 5. GET the request again to verify the response
        responded_req = await admin_client.aget_user_agent_request(request_id)
        assert responded_req.status == UserAgentRequestStatus.RESPONDED
        assert responded_req.response == response_payload.response

    @pytest.mark.asyncio
    async def test_aget_nonexistent_request_fails(self, admin_client: RestClient):
        """Verifies fetching a non-existent request asynchronously raises an error."""
        non_existent_id = uuid4()
        with pytest.raises(UserAgentRequestFetchError):
            await admin_client.aget_user_agent_request(non_existent_id)

    @pytest.mark.asyncio
    async def test_async_unauthorized_access_fails(self, pub_client: RestClient):
        """Ensures an unauthorized client fails on async methods."""
        with pytest.raises((UserAgentRequestCreationError, PermissionError)):  # noqa: PT012
            payload = UserAgentRequestPostPayload(
                trajectory_id=uuid4(),
                request={"data": "test"},
            )
            await pub_client.acreate_user_agent_request(payload)

        with pytest.raises((UserAgentRequestFetchError, PermissionError)):
            await pub_client.aget_user_agent_request(uuid4())


def create_mock_http_status_error(message: str, status_code: int) -> HTTPStatusError:
    """Create a properly mocked HTTPStatusError for testing."""
    mock_request = Mock()
    mock_response = Mock()
    mock_response.status_code = status_code

    return HTTPStatusError(message, request=mock_request, response=mock_response)


@pytest.mark.parametrize(
    ("exception", "should_retry", "test_description"),
    [
        (ConnectionError("Connection failed"), True, "connection error"),
        (Timeout("Request timed out"), True, "timeout error"),
        (RequestException("Request exception"), True, "request exception"),
        (ConnectError("Connect error"), True, "httpx connect error"),
        (ConnectTimeout("Connect timeout"), True, "httpx connect timeout"),
        (ReadTimeout("Read timeout"), True, "httpx read timeout"),
        (ReadError("Read error"), True, "httpx read error"),
        (NetworkError("Network error"), True, "httpx network error"),
        (RemoteProtocolError("Protocol error"), True, "httpx protocol error"),
        (CloseError("Close error"), True, "httpx close error"),
        (FileUploadError("Upload failed"), True, "custom FileUploadError"),
        (
            create_mock_http_status_error("Too many requests", 429),
            True,
            "429 too many requests",
        ),
        (
            create_mock_http_status_error("Internal server error", 500),
            True,
            "500 internal server error",
        ),
        (create_mock_http_status_error("Bad gateway", 502), True, "502 bad gateway"),
        (
            create_mock_http_status_error("Service unavailable", 503),
            True,
            "503 service unavailable",
        ),
        (
            create_mock_http_status_error("Gateway timeout", 504),
            True,
            "504 gateway timeout",
        ),
        (create_mock_http_status_error("Bad request", 400), False, "400 bad request"),
        (create_mock_http_status_error("Unauthorized", 401), False, "401 unauthorized"),
        (create_mock_http_status_error("Forbidden", 403), False, "403 forbidden"),
        (create_mock_http_status_error("Not found", 404), False, "404 not found"),
        (ValueError("Invalid value"), False, "value error"),
        (KeyError("Missing key"), False, "key error"),
        (RuntimeError("Runtime error"), False, "runtime error"),
    ],
)
def test_retry_logic_conditions(exception, should_retry, test_description):
    retry_condition = create_retry_if_connection_error(FileUploadError)

    mock_retry_state = Mock()
    mock_retry_state.outcome = Mock()
    mock_retry_state.outcome.exception.return_value = exception

    result = retry_condition(mock_retry_state)

    assert result == should_retry, (
        f"Expected {should_retry} for {test_description}, got {result}"
    )
