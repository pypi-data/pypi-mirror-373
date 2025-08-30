# ruff: noqa: ARG001, PLC2701, RUF029
import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import ANY, AsyncMock, Mock, patch
from uuid import uuid4

import pytest
from httpx import HTTPStatusError, codes

from futurehouse_client.clients.data_storage_methods import (
    DataStorageCreationError,
    DataStorageError,
    DataStorageMethods,
    DataStorageRetrievalError,
    RestClientError,
)
from futurehouse_client.models.data_storage_methods import (
    DataStorageLocationPayload,
    DataStorageRequestPayload,
    DataStorageResponse,
    DirectoryManifest,
    ManifestEntry,
)


class MockDataStorageMethods(DataStorageMethods):
    """Mock implementation of DataStorageMethods for testing."""

    def __init__(self):
        self._client = Mock()
        self._async_client = AsyncMock()

    @property
    def client(self):
        return self._client

    @property
    def async_client(self):
        return self._async_client


class TestDataStorageMethods:
    """Test cases for DataStorageMethods class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.methods = MockDataStorageMethods()
        self.test_uuid = uuid4()
        self.test_project_id = uuid4()

    def _create_mock_response(
        self,
        storage_type="gcs",
        signed_url="https://example.com/signed-url",
        content=None,
    ):
        """Create a complete mock response with all required fields."""
        from datetime import datetime

        now = datetime.now().isoformat() + "Z"
        user_id = str(uuid4())
        storage_location_id = str(uuid4())

        return {
            "data_storage": {
                "id": str(self.test_uuid),
                "name": "test",
                "user_id": user_id,
                "created_at": now,
                "modified_at": now,
                "content": content,
            },
            "storage_locations": [
                {
                    "id": storage_location_id,
                    "data_storage_id": str(self.test_uuid),
                    "storage_config": {
                        "signed_url": signed_url,
                        "storage_type": storage_type,
                        "content_type": "application/octet-stream",
                    },
                    "created_at": now,
                }
            ],
        }

    def test_handle_http_errors_forbidden(self):
        """Test handling of 403 Forbidden errors."""
        mock_response = Mock()
        mock_response.status_code = codes.FORBIDDEN
        mock_response.text = "Access denied"

        error = HTTPStatusError("Forbidden", request=Mock(), response=mock_response)

        with pytest.raises(DataStorageError, match="not authorized"):
            self.methods._handle_http_errors(error, "creating")

    def test_handle_http_errors_unprocessable_entity(self):
        """Test handling of 422 Unprocessable Entity errors."""
        mock_response = Mock()
        mock_response.status_code = codes.UNPROCESSABLE_ENTITY
        mock_response.text = "Invalid payload"

        error = HTTPStatusError(
            "Unprocessable Entity", request=Mock(), response=mock_response
        )

        with pytest.raises(DataStorageError, match="Invalid request payload"):
            self.methods._handle_http_errors(error, "creating")

    def test_handle_http_errors_generic(self):
        """Test handling of generic HTTP errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"

        error = HTTPStatusError(
            "Internal Server Error", request=Mock(), response=mock_response
        )

        with pytest.raises(DataStorageError, match="500 - Internal server error"):
            self.methods._handle_http_errors(error, "creating")

    def test_validate_file_path_exists(self):
        """Test file path validation with existing file."""
        with tempfile.NamedTemporaryFile() as temp_file:
            result = self.methods._validate_file_path(temp_file.name)
            assert isinstance(result, Path)
            assert result.exists()

    def test_validate_file_path_not_exists(self):
        """Test file path validation with non-existent file."""
        with pytest.raises(DataStorageError, match="not found"):
            self.methods._validate_file_path("/nonexistent/file.txt")

    def test_build_zip_path_with_path(self):
        """Test building zip path with existing path."""
        result = self.methods._build_zip_path("test", "/some/path")

        # Verify path construction with existing path
        assert isinstance(result, str)
        assert result == "/some/path/test.zip"
        assert result.endswith(".zip")
        assert result.startswith("/some/path/")
        assert "test.zip" in result

    def test_build_zip_path_without_path(self):
        """Test building zip path without existing path."""
        result = self.methods._build_zip_path("test", None)

        # Verify path construction without existing path
        assert isinstance(result, str)
        assert result == "test.zip"
        assert result.endswith(".zip")
        assert result.startswith("test")
        assert len(result) == 8  # "test.zip" is 8 characters

    def test_build_zip_path_already_zip(self):
        """Test building zip path when name already has .zip extension."""
        result = self.methods._build_zip_path("test.zip", "/some/path")

        # Verify path construction handles existing .zip extension
        assert isinstance(result, str)
        assert result == "/some/path/test.zip"
        assert result.endswith(".zip")
        assert result.startswith("/some/path/")
        assert "test.zip" in result
        assert result.count(".zip") == 1  # Should not duplicate .zip extension

    def test_is_zip_file_true(self):
        """Test zip file detection with actual zip file."""
        with tempfile.NamedTemporaryFile(suffix=".zip") as temp_file:
            with zipfile.ZipFile(temp_file.name, "w") as zipf:
                zipf.writestr("test.txt", "test content")

            # Verify zip file detection works correctly
            result = self.methods._is_zip_file(Path(temp_file.name))
            assert isinstance(result, bool)
            assert result is True
            assert temp_file.name.endswith(".zip")
            assert Path(temp_file.name).exists()

    def test_is_zip_file_false(self):
        """Test zip file detection with non-zip file."""
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            temp_file.write(b"not a zip file")
            temp_file.flush()

            # Verify non-zip file detection works correctly
            result = self.methods._is_zip_file(Path(temp_file.name))
            assert isinstance(result, bool)
            assert result is False
            assert temp_file.name.endswith(".txt")
            assert Path(temp_file.name).exists()

    def test_extract_zip_file(self):
        """Test zip file extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "test.zip"

            # Create a test zip file
            with zipfile.ZipFile(zip_path, "w") as zipf:
                zipf.writestr("test.txt", "test content")
                zipf.writestr("subdir/file.txt", "subdir content")

            extract_to = Path(temp_dir) / "extract"
            extract_to.mkdir(exist_ok=True)
            result = self.methods._extract_zip_file(zip_path, extract_to)

            # Verify zip extraction creates the expected directory structure
            assert isinstance(result, Path)
            assert result.exists()
            assert result.is_dir()
            # The result path may include an "extracted" subdirectory
            assert extract_to in result.parents or result == extract_to
            assert (result / "test.txt").exists()
            assert (result / "subdir" / "file.txt").exists()
            assert (result / "subdir").is_dir()
            # Count the actual items in the extracted directory
            actual_items = list(result.iterdir())
            assert (
                len(actual_items) >= 2
            )  # Should have at least 2 items: test.txt and subdir

    @patch("futurehouse_client.clients.data_storage_methods.requests_lib.get")
    def test_download_from_gcs_success(self, mock_get):
        """Test successful GCS download."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-disposition": 'filename="test.txt"'}
        mock_response.iter_content.return_value = [b"test content"]
        mock_get.return_value.__enter__.return_value = mock_response

        result = self.methods._download_from_gcs("https://example.com/signed-url")

        # Verify GCS download creates the expected file
        assert isinstance(result, Path)
        assert result.exists()
        assert result.is_file()
        assert result.name == "test.txt"
        assert result.suffix == ".txt"
        assert result.stat().st_size > 0  # File should have content

    @patch("futurehouse_client.clients.data_storage_methods.requests_lib.get")
    def test_download_from_gcs_zip_file(self, mock_get):
        """Test GCS download of zip file with automatic extraction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = Path(temp_dir) / "test.zip"

            # Create a test zip file
            with zipfile.ZipFile(zip_path, "w") as zipf:
                zipf.writestr("test.txt", "test content")

            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.headers = {"content-disposition": 'filename="test.zip"'}
            mock_response.iter_content.return_value = [zip_path.read_bytes()]
            mock_get.return_value.__enter__.return_value = mock_response

            result = self.methods._download_from_gcs("https://example.com/signed-url")

            # Verify zip file download and extraction
            assert isinstance(result, Path)
            assert result.exists()
            # The result should be the extracted directory, not the zip file
            if result.is_dir():
                assert result.is_dir()
                assert (result / "test.txt").exists()
                assert (result / "test.txt").is_file()
                assert len(list(result.iterdir())) == 1  # Should have 1 file
            else:
                # If it's a single file, check the file itself
                assert result.is_file()
                assert result.name == "test.txt"
                assert result.suffix == ".txt"

    def test_prepare_single_file_upload_small_text(self):
        """Test preparation of small text file for upload."""
        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w") as temp_file:
            temp_file.write("small text content")
            temp_file.flush()

            file_size, payload = self.methods._prepare_single_file_upload(
                "test.txt", Path(temp_file.name), "Test description", None
            )

            assert file_size > 0
            assert payload is not None
            assert payload.content == "small text content"
            assert payload.name == "test.txt"

    def test_prepare_single_file_upload_large_file(self):
        """Test preparation of large file for upload."""
        with tempfile.NamedTemporaryFile(suffix=".bin") as temp_file:
            # Write enough data to exceed the small file threshold
            temp_file.write(b"0" * (11 * 1024 * 1024))  # 11MB
            temp_file.flush()

            file_size, payload = self.methods._prepare_single_file_upload(
                "large.bin", Path(temp_file.name), "Large file", None
            )

            assert file_size > 0
            assert payload is None  # Should not be sent as text content

    def test_create_data_storage_entry_sync(self):
        """Test synchronous data storage entry creation."""
        mock_response = Mock()
        mock_response.json.return_value = self._create_mock_response()
        mock_response.raise_for_status.return_value = None

        self.methods.client.post.return_value = mock_response

        payload = DataStorageRequestPayload(
            name="test", description="Test description", content="test content"
        )

        result = self.methods._create_data_storage_entry(payload)

        assert result.data_storage.id == self.test_uuid
        assert (
            result.storage_locations[0].storage_config.signed_url
            == "https://example.com/signed-url"
        )

    @pytest.mark.asyncio
    async def test_acreate_data_storage_entry_async(self):
        """Test asynchronous data storage entry creation."""
        mock_response = Mock()
        mock_response.json.return_value = self._create_mock_response()
        mock_response.raise_for_status.return_value = None

        # Make the post method return the mock response asynchronously
        self.methods.async_client.post = AsyncMock(return_value=mock_response)

        payload = DataStorageRequestPayload(
            name="test", description="Test description", content="test content"
        )

        result = await self.methods._acreate_data_storage_entry(payload)

        assert result.data_storage.id == self.test_uuid
        assert (
            result.storage_locations[0].storage_config.signed_url
            == "https://example.com/signed-url"
        )

    def test_generate_folder_description_from_files(self):
        """Test folder description generation from files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            (temp_path / "file1.txt").write_text("content1")
            (temp_path / "file2.txt").write_text("content2")

            manifest = DirectoryManifest()
            manifest.entries = {
                "file1.txt": ManifestEntry(description="First file"),
                "file2.txt": ManifestEntry(description="Second file"),
            }

            result = self.methods._generate_folder_description_from_files(
                temp_path, manifest
            )

            # Verify the generated description contains expected content
            assert isinstance(result, str)
            assert "file1.txt: First file" in result
            assert "file2.txt: Second file" in result
            assert result.startswith("Directory containing:")
            assert (
                len(result.split(", ")) == 2
            )  # Should have exactly 2 file descriptions

    def test_load_manifest_json(self):
        """Test loading JSON manifest file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.json"

            manifest_data = {
                "test_dir": {
                    "type": "directory",
                    "description": "Test directory",
                    "entries": {},
                }
            }

            with open(manifest_path, "w") as f:
                json.dump(manifest_data, f)

            result = self.methods._load_manifest(temp_path, "manifest.json")

            # Verify the manifest structure and content
            assert isinstance(result, DirectoryManifest)
            assert "test_dir" in result.entries
            assert result.entries["test_dir"].description == "Test directory"  # type: ignore[union-attr]
            assert len(result.entries) == 1  # Should have exactly one entry

    def test_load_manifest_yaml(self):
        """Test loading YAML manifest file."""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available")

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            manifest_path = temp_path / "manifest.yaml"

            manifest_data = {
                "test_dir": {
                    "type": "directory",
                    "description": "Test directory",
                    "entries": {},
                }
            }

            with open(manifest_path, "w") as f:
                yaml.dump(manifest_data, f)

            result = self.methods._load_manifest(temp_path, "manifest.yaml")

            # Verify the manifest structure and content
            assert isinstance(result, DirectoryManifest)
            assert "test_dir" in result.entries
            assert result.entries["test_dir"].description == "Test directory"  # type: ignore[union-attr]
            assert len(result.entries) == 1  # Should have exactly one entry

    def test_load_manifest_file_not_found(self):
        """Test loading manifest when file doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            with pytest.raises(DataStorageCreationError, match="not found"):
                self.methods._load_manifest(temp_path, "nonexistent.json")

    @patch("futurehouse_client.clients.data_storage_methods._create_directory_zip")
    @patch("futurehouse_client.clients.data_storage_methods._upload_file_with_progress")
    def test_upload_data_directory(self, mock_upload, mock_create_zip):
        """Test directory upload as zip collection."""
        mock_create_zip.return_value = 1024  # 1KB zip size

        mock_response = Mock()
        mock_response.json.return_value = self._create_mock_response()
        mock_response.raise_for_status.return_value = None

        self.methods.client.post.return_value = mock_response

        status_response = Mock()
        status_response.json.return_value = self._create_mock_response()
        status_response.json.return_value["data_storage"]["status"] = "active"
        status_response.raise_for_status.return_value = None

        self.methods.client.patch.return_value = status_response

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.txt").write_text("test content")

            result = self.methods._upload_data_directory(
                "test_dir", temp_path, "Test directory", None
            )

            assert result.data_storage.id == self.test_uuid
            mock_create_zip.assert_called_once_with(
                temp_path,
                ANY,
                None,
                ".gitignore",
            )
            mock_upload.assert_called_once_with(
                "https://example.com/signed-url",
                ANY,
                ANY,
                ANY,  # Use ANY for file size as it may vary
            )

            # Assert that the path endpoint is called
            self.methods.client.post.assert_called_once_with(
                "/v0.1/data-storage/data-entries",
                json={
                    "name": "test_dir",
                    "description": "Test directory",
                    "path": "test_dir.zip",  # The actual path includes .zip extension
                    "is_collection": True,
                },
            )

    @patch(
        "futurehouse_client.clients.data_storage_methods._aupload_file_with_progress"
    )
    @pytest.mark.asyncio
    async def test_aupload_data_directory(self, mock_upload):
        """Test asynchronous directory upload as zip collection."""
        mock_response = Mock()
        mock_response.json.return_value = self._create_mock_response()
        mock_response.raise_for_status.return_value = None

        # Make the post method return the mock response asynchronously
        self.methods.async_client.post = AsyncMock(return_value=mock_response)

        status_response = Mock()
        status_response.json.return_value = self._create_mock_response()
        status_response.json.return_value["data_storage"]["status"] = "active"
        status_response.raise_for_status.return_value = None

        self.methods.async_client.patch.return_value = status_response

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.txt").write_text("test content")

            result = await self.methods._aupload_data_directory(
                "test_dir", temp_path, "Test directory", None
            )

            assert result.data_storage.id == self.test_uuid
            mock_upload.assert_called_once_with(
                "https://example.com/signed-url",
                ANY,
                ANY,
                ANY,  # Use ANY for file size as it may vary
            )

            # Assert that the path endpoint is called
            self.methods.async_client.post.assert_called_once_with(
                "/v0.1/data-storage/data-entries",
                json={
                    "name": "test_dir",
                    "description": "Test directory",
                    "path": "test_dir.zip",  # The actual path includes .zip extension
                    "is_collection": True,
                },
            )

    def test_store_text_content_success(self):
        """Test successful text content storage."""
        mock_response = Mock()
        mock_response.json.return_value = self._create_mock_response(
            storage_type="raw_content", signed_url=None
        )
        mock_response.raise_for_status.return_value = None

        self.methods.client.post.return_value = mock_response

        result = self.methods.store_text_content(
            "test", "test content", "Test description", project_id=self.test_project_id
        )

        assert result.data_storage.id == self.test_uuid
        # Verify the API call was made with the correct endpoint and data
        self.methods.client.post.assert_called_once()
        call_args = self.methods.client.post.call_args
        assert call_args[0][0] == "/v0.1/data-storage/data-entries"

        # Verify the JSON payload contains the expected fields
        json_data = call_args[1]["json"]
        assert json_data["name"] == "test"
        assert json_data["content"] == "test content"
        assert json_data["description"] == "Test description"
        assert json_data["is_collection"] is False
        assert json_data["project_id"] == str(self.test_project_id)

    def test_store_text_content_http_error(self):
        """Test text content storage with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Access denied"

        error = HTTPStatusError("Forbidden", request=Mock(), response=mock_response)
        self.methods.client.post.side_effect = error

        with pytest.raises(DataStorageError, match="not authorized"):
            self.methods.store_text_content("test", "test content")

    @pytest.mark.asyncio
    async def test_astore_text_content_success(self):
        """Test successful asynchronous text content storage."""
        mock_response = Mock()
        mock_response.json.return_value = self._create_mock_response(
            storage_type="raw_content", signed_url=None
        )
        mock_response.raise_for_status.return_value = None

        # Make the post method return the mock response asynchronously
        self.methods.async_client.post = AsyncMock(return_value=mock_response)

        result = await self.methods.astore_text_content(
            "test", "test content", "Test description", project_id=self.test_project_id
        )

        assert result.data_storage.id == self.test_uuid
        # Verify the API call was made with the correct endpoint and data
        self.methods.async_client.post.assert_called_once()
        call_args = self.methods.async_client.post.call_args
        assert call_args[0][0] == "/v0.1/data-storage/data-entries"

        # Verify the JSON payload contains the expected fields
        json_data = call_args[1]["json"]
        assert json_data["name"] == "test"
        assert json_data["content"] == "test content"
        assert json_data["description"] == "Test description"
        assert json_data["is_collection"] is False
        assert json_data["project_id"] == str(self.test_project_id)

    @patch("futurehouse_client.clients.data_storage_methods._upload_file_with_progress")
    def test_store_file_content_single_file(self, mock_upload):
        """Test single file content storage."""
        mock_response = Mock()
        mock_response.json.return_value = self._create_mock_response()
        mock_response.raise_for_status.return_value = None

        self.methods.client.post.return_value = mock_response

        status_response = Mock()
        status_response.json.return_value = self._create_mock_response()
        status_response.json.return_value["data_storage"]["status"] = "active"
        status_response.raise_for_status.return_value = None

        self.methods.client.patch.return_value = status_response

        with tempfile.NamedTemporaryFile(suffix=".bin") as temp_file:
            temp_file.write(b"test binary content")
            temp_file.flush()

            result = self.methods.store_file_content(
                "test.bin", temp_file.name, "Test file", project_id=self.test_project_id
            )

            assert result.data_storage.id == self.test_uuid
            mock_upload.assert_called_once_with(
                "https://example.com/signed-url",
                ANY,
                ANY,
                ANY,
            )

    @patch("futurehouse_client.clients.data_storage_methods._upload_file_with_progress")
    def test_store_file_content_directory_collection(self, mock_upload):
        """Test directory content storage as collection."""
        mock_response = Mock()
        mock_response.json.return_value = self._create_mock_response()
        mock_response.raise_for_status.return_value = None

        self.methods.client.post.return_value = mock_response

        status_response = Mock()
        status_response.json.return_value = self._create_mock_response()
        status_response.json.return_value["data_storage"]["status"] = "active"
        status_response.raise_for_status.return_value = None

        self.methods.client.patch.return_value = status_response

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.txt").write_text("test content")

            result = self.methods.store_file_content(
                "test_dir",
                temp_path,
                "Test directory",
                as_collection=True,
                project_id=self.test_project_id,
            )

            assert result.data_storage.id == self.test_uuid
            mock_upload.assert_called_once_with(
                "https://example.com/signed-url",
                ANY,
                ANY,
                ANY,
            )

    def test_register_existing_data_source_success(self):
        """Test successful registration of existing data source."""
        mock_response = Mock()
        mock_response.json.return_value = self._create_mock_response(signed_url=None)
        mock_response.raise_for_status.return_value = None

        self.methods.client.post.return_value = mock_response

        existing_location = DataStorageLocationPayload(
            storage_type="gcs", content_type="file"
        )

        result = self.methods.register_existing_data_source(
            "test",
            existing_location,
            "Test description",
            project_id=self.test_project_id,
        )

        assert result.data_storage.id == self.test_uuid
        # Verify the API call was made with the correct endpoint and data
        self.methods.client.post.assert_called_once()
        call_args = self.methods.client.post.call_args
        assert call_args[0][0] == "/v0.1/data-storage/data-entries"

        # Verify the JSON payload contains the expected fields
        json_data = call_args[1]["json"]
        assert json_data["name"] == "test"
        assert json_data["description"] == "Test description"
        assert json_data["is_collection"] is False
        assert json_data["project_id"] == self.test_project_id
        assert "existing_location" in json_data
        assert json_data["existing_location"]["storage_type"] == "gcs"
        assert json_data["existing_location"]["content_type"] == "file"

    @pytest.mark.asyncio
    async def test_aregister_existing_data_source_success(self):
        """Test successful asynchronous registration of existing data source."""
        mock_response = Mock()
        mock_response.json.return_value = self._create_mock_response(signed_url=None)
        mock_response.raise_for_status.return_value = None

        # Make the post method return the mock response asynchronously
        self.methods.async_client.post = AsyncMock(return_value=mock_response)

        existing_location = DataStorageLocationPayload(
            storage_type="gcs", content_type="file"
        )

        result = await self.methods.aregister_existing_data_source(
            name="test",
            existing_location=existing_location,
            description="Test description",
            as_collection=False,
            project_id=self.test_project_id,
        )

        assert result.data_storage.id == self.test_uuid
        # Verify the API call was made with the correct endpoint and data
        self.methods.async_client.post.assert_called_once()
        call_args = self.methods.async_client.post.call_args
        assert call_args[0][0] == "/v0.1/data-storage/data-entries"

        # Verify the JSON payload contains the expected fields
        json_data = call_args[1]["json"]
        assert json_data["name"] == "test"
        assert json_data["description"] == "Test description"
        assert json_data["project_id"] == self.test_project_id
        assert "existing_location" in json_data
        assert json_data["existing_location"]["storage_type"] == "gcs"
        assert json_data["existing_location"]["content_type"] == "file"

    @patch("futurehouse_client.clients.data_storage_methods.requests_lib.get")
    def test_fetch_data_from_storage_gcs(self, mock_get):
        """Test fetching data from GCS storage."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {"content-disposition": 'filename="test.txt"'}
        mock_response.iter_content.return_value = [b"test content"]
        mock_get.return_value.__enter__.return_value = mock_response

        api_response = Mock()
        api_response.json.return_value = self._create_mock_response()
        api_response.raise_for_status.return_value = None

        self.methods.client.get.return_value = api_response

        result = self.methods.fetch_data_from_storage(self.test_uuid)

        # Verify GCS data fetching returns a valid file path
        assert result is not None
        assert isinstance(result, Path)
        assert result.name == "test.txt"
        assert result.suffix == ".txt"
        assert result.exists()  # File should exist after download

    def test_fetch_data_from_storage_raw_content(self):
        """Test fetching data from raw content storage."""
        api_response = Mock()
        api_response.json.return_value = self._create_mock_response(
            storage_type="raw_content", signed_url=None, content="test content"
        )
        api_response.raise_for_status.return_value = None

        self.methods.client.get.return_value = api_response

        result = self.methods.fetch_data_from_storage(self.test_uuid)

        # Verify raw content storage returns the content directly
        assert isinstance(result, str)
        assert result == "test content"
        assert len(result) == 12  # "test content" is 12 characters
        assert result.strip() == result  # No leading/trailing whitespace

    def test_fetch_data_from_storage_no_id(self):
        """Test fetching data without providing storage ID."""
        with pytest.raises(DataStorageRetrievalError, match="must be provided"):
            self.methods.fetch_data_from_storage(None)

    def test_fetch_data_from_storage_unsupported_type(self):
        """Test fetching data from unsupported storage type."""
        api_response = Mock()
        api_response.json.return_value = self._create_mock_response(
            storage_type="unsupported", signed_url=None
        )
        api_response.raise_for_status.return_value = None

        self.methods.client.get.return_value = api_response

        with pytest.raises(DataStorageRetrievalError, match="Unsupported storage type"):
            self.methods.fetch_data_from_storage(self.test_uuid)

    @pytest.mark.asyncio
    async def test_afetch_data_from_storage_gcs(self, monkeypatch):
        """Test asynchronous fetching data from GCS storage."""

        async def mock_download(*args, **kwargs):
            with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
                temp_file.write(b"test content")
                temp_file.flush()
                return Path(temp_file.name)

        monkeypatch.setattr(self.methods, "_adownload_from_gcs", mock_download)

        api_response = Mock()
        api_response.json.return_value = self._create_mock_response()
        api_response.raise_for_status.return_value = None

        # Make the get method return the mock response asynchronously
        self.methods.async_client.get = AsyncMock(return_value=api_response)

        result = await self.methods.afetch_data_from_storage(self.test_uuid)

        # Verify async GCS data fetching returns a valid file path
        assert result is not None
        assert isinstance(result, Path)
        assert result.suffix == ".txt"
        assert result.name.endswith(".txt")  # Should have .txt extension
        # Note: File existence check removed as it's a temporary file that may be cleaned up

    def test_upload_directory_hierarchically(self):
        """Test hierarchical directory upload."""
        mock_response = Mock()
        mock_response.json.return_value = self._create_mock_response(signed_url=None)
        mock_response.json.return_value["data_storage"]["dataset_id"] = str(uuid4())
        mock_response.raise_for_status.return_value = None

        self.methods.client.post.return_value = mock_response

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "file1.txt").write_text("content1")
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "file2.txt").write_text("content2")

            result = self.methods._upload_directory_hierarchically(
                "test_dir",
                temp_path,
                "Test description",
                project_id=self.test_project_id,
            )

            # Verify the result structure and content
            assert isinstance(result, list)
            assert len(result) >= 2  # Should have at least 2 responses
            assert all(isinstance(r, DataStorageResponse) for r in result)

            # Verify the responses have the expected structure
            for response in result:
                assert hasattr(response, "data_storage")
                assert hasattr(response.data_storage, "name")
                assert hasattr(response.data_storage, "description")
                assert hasattr(response.data_storage, "id")

    @pytest.mark.asyncio
    async def test_aupload_directory_hierarchically(self):
        """Test asynchronous hierarchical directory upload."""
        mock_response = Mock()
        mock_response.json.return_value = self._create_mock_response(signed_url=None)
        mock_response.json.return_value["data_storage"]["dataset_id"] = str(uuid4())
        mock_response.raise_for_status.return_value = None

        # Make the post method return the mock response asynchronously
        self.methods.async_client.post = AsyncMock(return_value=mock_response)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "file1.txt").write_text("content1")
            (temp_path / "subdir").mkdir()
            (temp_path / "subdir" / "file2.txt").write_text("content2")

            result = await self.methods._aupload_directory_hierarchically(
                "test_dir",
                temp_path,
                "Test description",
                project_id=self.test_project_id,
            )

            # Verify the result structure and content
            assert isinstance(result, list)
            assert len(result) >= 2  # Should have at least 2 responses
            assert all(isinstance(r, DataStorageResponse) for r in result)

            # Verify the responses have the expected structure
            for response in result:
                assert hasattr(response, "data_storage")
                assert hasattr(response.data_storage, "name")
                assert hasattr(response.data_storage, "description")
                assert hasattr(response.data_storage, "id")

    @pytest.mark.asyncio
    async def test_acreate_dataset_success(self):
        """Test successful asynchronous dataset creation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": str(self.test_uuid),
            "name": "test_dataset",
            "description": "Test dataset description",
            "user_id": "test_user_123",
        }
        mock_response.raise_for_status.return_value = None

        # Make the post method return the mock response asynchronously
        self.methods.async_client.post = AsyncMock(return_value=mock_response)

        result = await self.methods.acreate_dataset(
            name="test_dataset",
            description="Test dataset description",
        )

        # Verify the result structure and content
        assert result is not None
        # Verify the API call was made with the correct endpoint and data
        self.methods.async_client.post.assert_called_once()
        call_args = self.methods.async_client.post.call_args
        assert call_args[0][0] == "/v0.1/data-storage/datasets"

        # Verify the JSON payload contains the expected fields
        json_data = call_args[1]["json"]
        assert json_data["name"] == "test_dataset"
        assert json_data["description"] == "Test dataset description"
        assert "id" not in json_data  # Should not be included when None

    @pytest.mark.asyncio
    async def test_acreate_dataset_with_id_success(self):
        """Test successful asynchronous dataset creation with custom ID."""
        custom_dataset_id = uuid4()
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": str(custom_dataset_id),
            "name": "test_dataset",
            "description": "Test dataset description",
            "user_id": "test_user_123",
        }
        mock_response.raise_for_status.return_value = None

        # Make the post method return the mock response asynchronously
        self.methods.async_client.post = AsyncMock(return_value=mock_response)

        result = await self.methods.acreate_dataset(
            name="test_dataset",
            description="Test dataset description",
            dataset_id=custom_dataset_id,
        )

        # Verify the result structure and content
        assert result is not None
        # Verify the API call was made with the correct endpoint and data
        self.methods.async_client.post.assert_called_once()
        call_args = self.methods.async_client.post.call_args
        assert call_args[0][0] == "/v0.1/data-storage/datasets"

        # Verify the JSON payload contains the expected fields including custom ID
        json_data = call_args[1]["json"]
        assert json_data["name"] == "test_dataset"
        assert json_data["description"] == "Test dataset description"
        assert json_data["id"] == custom_dataset_id

    @pytest.mark.asyncio
    async def test_acreate_dataset_http_error(self):
        """Test dataset creation with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Access denied"

        error = HTTPStatusError("Forbidden", request=Mock(), response=mock_response)
        self.methods.async_client.post = AsyncMock(side_effect=error)

        with pytest.raises(DataStorageError, match="not authorized"):
            await self.methods.acreate_dataset(
                name="test_dataset",
                description="Test dataset description",
            )

    @pytest.mark.asyncio
    async def test_acreate_dataset_unexpected_error(self):
        """Test dataset creation with unexpected error."""
        unexpected_error = ValueError("Unexpected error")
        self.methods.async_client.post = AsyncMock(side_effect=unexpected_error)

        with pytest.raises(
            DataStorageCreationError, match="An unexpected error occurred"
        ):
            await self.methods.acreate_dataset(
                name="test_dataset",
                description="Test description",
            )

    @pytest.mark.asyncio
    async def test_adelete_dataset_success(self):
        """Test successful asynchronous dataset deletion."""
        # Make the delete method return successfully
        self.methods.async_client.delete = AsyncMock()

        dataset_id = uuid4()
        await self.methods.adelete_dataset(dataset_id)

        # Verify the API call was made with the correct endpoint
        self.methods.async_client.delete.assert_called_once_with(
            f"/v0.1/data-storage/datasets/{dataset_id}"
        )

    @pytest.mark.asyncio
    async def test_adelete_dataset_http_error(self):
        """Test dataset deletion with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Dataset not found"

        error = HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        self.methods.async_client.delete = AsyncMock(side_effect=error)

        dataset_id = uuid4()
        with pytest.raises(DataStorageError, match="Dataset not found"):
            await self.methods.adelete_dataset(dataset_id)

    @pytest.mark.asyncio
    async def test_adelete_dataset_unexpected_error(self):
        """Test dataset deletion with unexpected error."""
        unexpected_error = ValueError("Unexpected error")
        self.methods.async_client.delete = AsyncMock(side_effect=unexpected_error)

        dataset_id = uuid4()
        with pytest.raises(DataStorageError, match="An unexpected error occurred"):
            await self.methods.adelete_dataset(dataset_id)

    @pytest.mark.asyncio
    async def test_aget_dataset_success(self):
        """Test successful asynchronous dataset retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": str(self.test_uuid),
            "name": "test_dataset",
            "description": "Test dataset description",
            "user_id": "test_user_123",
            "created_at": "2024-01-01T00:00:00Z",
            "modified_at": "2024-01-01T00:00:00Z",
        }
        mock_response.raise_for_status.return_value = None

        # Make the get method return the mock response asynchronously
        self.methods.async_client.get = AsyncMock(return_value=mock_response)

        dataset_id = uuid4()
        result = await self.methods.aget_dataset(dataset_id)

        # Verify the result structure and content
        assert result is not None
        assert result["id"] == str(self.test_uuid)
        assert result["name"] == "test_dataset"
        assert result["description"] == "Test dataset description"
        assert result["user_id"] == "test_user_123"

        # Verify the API call was made with the correct endpoint
        self.methods.async_client.get.assert_called_once_with(
            f"/v0.1/data-storage/datasets/{dataset_id}"
        )

    @pytest.mark.asyncio
    async def test_aget_dataset_http_error(self):
        """Test dataset retrieval with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Dataset not found"

        error = HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        self.methods.async_client.get = AsyncMock(side_effect=error)

        dataset_id = uuid4()
        with pytest.raises(DataStorageError, match="Dataset not found"):
            await self.methods.aget_dataset(dataset_id)

    @pytest.mark.asyncio
    async def test_aget_dataset_unexpected_error(self):
        """Test dataset retrieval with unexpected error."""
        unexpected_error = ValueError("Unexpected error")
        self.methods.async_client.get = AsyncMock(side_effect=unexpected_error)

        dataset_id = uuid4()
        with pytest.raises(DataStorageError, match="An unexpected error occurred"):
            await self.methods.aget_dataset(dataset_id)

    @pytest.mark.asyncio
    async def test_adelete_data_storage_entry_success(self):
        """Test successful asynchronous data storage entry deletion."""
        # Make the delete method return successfully
        self.methods.async_client.delete = AsyncMock()

        entry_id = uuid4()
        await self.methods.adelete_data_storage_entry(entry_id)

        # Verify the API call was made with the correct endpoint
        self.methods.async_client.delete.assert_called_once_with(
            f"/v0.1/data-storage/data-entries/{entry_id}"
        )

    @pytest.mark.asyncio
    async def test_adelete_data_storage_entry_http_error(self):
        """Test data storage entry deletion with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Access denied"

        error = HTTPStatusError("Forbidden", request=Mock(), response=mock_response)
        self.methods.async_client.delete = AsyncMock(side_effect=error)

        entry_id = uuid4()
        with pytest.raises(DataStorageError, match="not authorized"):
            await self.methods.adelete_data_storage_entry(entry_id)

    @pytest.mark.asyncio
    async def test_adelete_data_storage_entry_unexpected_error(self):
        """Test data storage entry deletion with unexpected error."""
        unexpected_error = ValueError("Unexpected error")
        self.methods.async_client.delete = AsyncMock(side_effect=unexpected_error)

        entry_id = uuid4()
        with pytest.raises(DataStorageError, match="An unexpected error occurred"):
            await self.methods.adelete_data_storage_entry(entry_id)

    @pytest.mark.asyncio
    async def test_acreate_dataset_minimal_payload(self):
        """Test dataset creation with minimal required fields."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": str(self.test_uuid),
            "name": "minimal_dataset",
            "user_id": "test_user_123",
        }
        mock_response.raise_for_status.return_value = None

        # Make the post method return the mock response asynchronously
        self.methods.async_client.post = AsyncMock(return_value=mock_response)

        result = await self.methods.acreate_dataset(name="minimal_dataset")

        # Verify the result structure and content
        assert result is not None
        # Verify the API call was made with the correct endpoint and data
        self.methods.async_client.post.assert_called_once()
        call_args = self.methods.async_client.post.call_args
        assert call_args[0][0] == "/v0.1/data-storage/datasets"

        # Verify the JSON payload contains only the required fields
        json_data = call_args[1]["json"]
        assert json_data["name"] == "minimal_dataset"
        assert "description" not in json_data
        assert "id" not in json_data

    @pytest.mark.asyncio
    async def test_acreate_dataset_validation_error(self):
        """Test dataset creation with validation error."""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_response.text = "Validation failed"

        error = HTTPStatusError(
            "Unprocessable Entity", request=Mock(), response=mock_response
        )
        self.methods.async_client.post = AsyncMock(side_effect=error)

        with pytest.raises(DataStorageError, match="Invalid request payload"):
            await self.methods.acreate_dataset(
                name="",  # Invalid empty name
                description="Test description",
            )

    @pytest.mark.asyncio
    async def test_aget_dataset_empty_response(self):
        """Test dataset retrieval with empty response."""
        mock_response = Mock()
        mock_response.json.return_value = {}
        mock_response.raise_for_status.return_value = None

        # Make the get method return the mock response asynchronously
        self.methods.async_client.get = AsyncMock(return_value=mock_response)

        dataset_id = uuid4()
        result = await self.methods.aget_dataset(dataset_id)

        # Verify the result is an empty dict
        assert result == {}
        assert len(result) == 0

        # Verify the API call was made with the correct endpoint
        self.methods.async_client.get.assert_called_once_with(
            f"/v0.1/data-storage/datasets/{dataset_id}"
        )

    @pytest.mark.asyncio
    async def test_adelete_dataset_not_found(self):
        """Test dataset deletion when dataset doesn't exist."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Dataset not found"

        error = HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        self.methods.async_client.delete = AsyncMock(side_effect=error)

        dataset_id = uuid4()
        with pytest.raises(DataStorageError, match="Dataset not found"):
            await self.methods.adelete_dataset(dataset_id)

    @pytest.mark.asyncio
    async def test_adelete_data_storage_entry_not_found(self):
        """Test data storage entry deletion when entry doesn't exist."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Data storage entry not found"

        error = HTTPStatusError("Not Found", request=Mock(), response=mock_response)
        self.methods.async_client.delete = AsyncMock(side_effect=error)

        entry_id = uuid4()
        with pytest.raises(DataStorageError, match="Data storage entry not found"):
            await self.methods.adelete_data_storage_entry(entry_id)


class TestUtilityFunctions:
    """Test cases for utility functions."""

    def test_should_ignore_file_no_patterns(self):
        """Test file ignoring when no patterns are provided."""
        from futurehouse_client.clients.data_storage_methods import _should_ignore_file

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.txt"
            test_file.write_text("test")

            result = _should_ignore_file(test_file, temp_path, None)
            assert result is False

    def test_should_ignore_file_with_patterns(self):
        """Test file ignoring with specific patterns."""
        from futurehouse_client.clients.data_storage_methods import _should_ignore_file

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.txt"
            test_file.write_text("test")

            # Test ignoring by filename pattern
            result = _should_ignore_file(test_file, temp_path, ["*.txt"])
            assert result is True

            # Test ignoring by specific name
            result = _should_ignore_file(test_file, temp_path, ["test.txt"])
            assert result is True

    def test_read_ignore_file_exists(self):
        """Test reading ignore file when it exists."""
        from futurehouse_client.clients.data_storage_methods import _read_ignore_file

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            ignore_file = temp_path / ".gitignore"
            ignore_file.write_text("*.log\n*.tmp\nnode_modules/")

            result = _read_ignore_file(temp_path)

            # Verify the ignore patterns are correctly read
            assert isinstance(result, list)
            assert len(result) == 3  # Should have exactly 3 patterns
            assert "*.log" in result
            assert "*.tmp" in result
            assert "node_modules/" in result
            # Verify no empty lines or comments are included
            assert all(pattern.strip() for pattern in result)
            assert not any(pattern.startswith("#") for pattern in result)

    def test_read_ignore_file_not_exists(self):
        """Test reading ignore file when it doesn't exist."""
        from futurehouse_client.clients.data_storage_methods import _read_ignore_file

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            result = _read_ignore_file(temp_path)

            # Verify empty ignore file returns empty list
            assert isinstance(result, list)
            assert result == []
            assert len(result) == 0
            assert not result  # Should be falsy

    def test_collect_ignore_patterns(self):
        """Test collecting ignore patterns from multiple sources."""
        from futurehouse_client.clients.data_storage_methods import (
            _collect_ignore_patterns,
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            ignore_file = temp_path / ".gitignore"
            ignore_file.write_text("*.log\n*.tmp")

            result = _collect_ignore_patterns(temp_path, ["custom_pattern"])

            # Verify all expected patterns are collected
            assert isinstance(result, list)
            assert len(result) >= 5  # At least 2 from file + 1 custom + 2 default
            assert "*.log" in result
            assert "*.tmp" in result
            assert "custom_pattern" in result
            assert ".git" in result  # Default ignore
            assert "__pycache__" in result  # Default ignore

            # Verify patterns are unique and properly formatted
            assert len(result) == len(set(result))  # No duplicates
            assert all(isinstance(pattern, str) for pattern in result)

    def test_should_send_as_text_content_small_file(self):
        """Test text content detection for small files."""
        from futurehouse_client.clients.data_storage_methods import (
            _should_send_as_text_content,
        )

        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            temp_file.write(b"small content")
            temp_file.flush()

            file_path = Path(temp_file.name)
            file_size = file_path.stat().st_size

            result = _should_send_as_text_content(file_path, file_size)

            # Verify the file size threshold logic
            assert isinstance(result, bool)
            assert result is True
            assert file_size < 10 * 1024 * 1024  # Should be under 10MB threshold
            assert file_path.suffix.lower() in {
                ".txt",
                ".md",
                ".csv",
                ".json",
                ".yaml",
                ".yml",
            }

    def test_should_send_as_text_content_large_file(self):
        """Test text content detection for large files."""
        from futurehouse_client.clients.data_storage_methods import (
            _should_send_as_text_content,
        )

        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            # Write enough data to exceed the threshold
            temp_file.write(b"0" * (11 * 1024 * 1024))  # 11MB
            temp_file.flush()

            file_path = Path(temp_file.name)
            file_size = file_path.stat().st_size

            result = _should_send_as_text_content(file_path, file_size)

            # Verify the file size threshold logic for large files
            assert isinstance(result, bool)
            assert result is False
            assert file_size > 10 * 1024 * 1024  # Should be over 10MB threshold
            assert file_size == 11 * 1024 * 1024  # Exactly 11MB as written

    def test_should_send_as_text_content_unsupported_extension(self):
        """Test text content detection for unsupported file types."""
        from futurehouse_client.clients.data_storage_methods import (
            _should_send_as_text_content,
        )

        with tempfile.NamedTemporaryFile(suffix=".bin") as temp_file:
            temp_file.write(b"binary content")
            temp_file.flush()

            file_path = Path(temp_file.name)
            file_size = file_path.stat().st_size

            result = _should_send_as_text_content(file_path, file_size)

            # Verify unsupported file types are rejected regardless of size
            assert isinstance(result, bool)
            assert result is False
            assert file_path.suffix.lower() not in {
                ".txt",
                ".md",
                ".csv",
                ".json",
                ".yaml",
                ".yml",
            }
            assert file_path.suffix.lower() == ".bin"

    def test_extract_text_from_file_success(self):
        """Test successful text extraction from file."""
        from futurehouse_client.clients.data_storage_methods import (
            _extract_text_from_file,
        )

        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w") as temp_file:
            temp_file.write("test content")
            temp_file.flush()

            file_path = Path(temp_file.name)
            result = _extract_text_from_file(file_path)

            # Verify text extraction works correctly
            assert isinstance(result, str)
            assert result == "test content"
            assert len(result) == 12  # "test content" is 12 characters
            assert result.strip() == result  # No leading/trailing whitespace

    def test_extract_text_from_file_unsupported_extension(self):
        """Test text extraction from unsupported file type."""
        from futurehouse_client.clients.data_storage_methods import (
            _extract_text_from_file,
        )

        with tempfile.NamedTemporaryFile(suffix=".bin") as temp_file:
            temp_file.write(b"binary content")
            temp_file.flush()

            file_path = Path(temp_file.name)
            result = _extract_text_from_file(file_path)

            # Verify unsupported file types return None
            assert result is None
            assert file_path.suffix.lower() not in {
                ".txt",
                ".md",
                ".csv",
                ".json",
                ".yaml",
                ".yml",
            }
            assert file_path.suffix.lower() == ".bin"

    def test_extract_text_from_file_read_error(self):
        """Test text extraction when file read fails."""
        from futurehouse_client.clients.data_storage_methods import (
            _extract_text_from_file,
        )

        # Create a file path that will cause a read error
        file_path = Path("/nonexistent/file.txt")

        result = _extract_text_from_file(file_path)

        # Verify file read errors return None
        assert result is None
        assert not file_path.exists()  # File should not exist
        assert str(file_path) == "/nonexistent/file.txt"  # Verify the path


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_exception_inheritance(self):
        """Test exception class inheritance hierarchy."""
        # Verify the exception class hierarchy is correct
        assert issubclass(DataStorageError, RestClientError)
        assert issubclass(DataStorageCreationError, DataStorageError)
        assert issubclass(DataStorageRetrievalError, DataStorageError)
        assert issubclass(
            DataStorageError, Exception
        )  # Should inherit from base Exception
        assert DataStorageError != RestClientError  # Should be different classes

    def test_exception_creation(self):
        """Test exception creation and message."""
        error = DataStorageCreationError("Test error message")

        # Verify exception creation and string representation
        assert isinstance(error, DataStorageCreationError)
        assert isinstance(error, DataStorageError)
        assert isinstance(error, Exception)
        assert str(error) == "Test error message"
        assert len(str(error)) == 18  # "Test error message" is 18 characters
        assert "Test error message" in str(error)

    def test_exception_with_cause(self):
        """Test exception creation with cause."""
        original_error = ValueError("Original error")
        error = DataStorageCreationError("Test error")
        error.__cause__ = original_error

        # Verify exception cause is properly set
        assert error.__cause__ == original_error
        assert isinstance(error.__cause__, ValueError)
        assert str(error.__cause__) == "Original error"
        assert error.__cause__.__class__.__name__ == "ValueError"


class TestProgressWrapper:
    """Test cases for ProgressWrapper class."""

    def test_progress_wrapper_initialization(self):
        """Test ProgressWrapper initialization."""
        from futurehouse_client.clients.data_storage_methods import ProgressWrapper

        mock_file = Mock()
        mock_progress_bar = Mock()

        wrapper = ProgressWrapper(mock_file, mock_progress_bar)

        # Verify ProgressWrapper initialization
        assert isinstance(wrapper, ProgressWrapper)
        assert wrapper.file_obj == mock_file
        assert wrapper.progress_bar == mock_progress_bar
        assert wrapper.bytes_read == 0
        assert hasattr(wrapper, "read")
        assert hasattr(wrapper, "seek")
        assert hasattr(wrapper, "tell")
        assert callable(wrapper.read)
        assert callable(wrapper.seek)
        assert callable(wrapper.tell)

    def test_progress_wrapper_read(self):
        """Test ProgressWrapper read method."""
        from futurehouse_client.clients.data_storage_methods import ProgressWrapper

        mock_file = Mock()
        mock_file.read.return_value = b"test data"
        mock_file.tell.return_value = 9

        mock_progress_bar = Mock()
        mock_progress_bar.n = 0

        wrapper = ProgressWrapper(mock_file, mock_progress_bar)

        result = wrapper.read()

        # Verify read operation and progress tracking
        assert isinstance(result, bytes)
        assert result == b"test data"
        assert len(result) == 9
        assert wrapper.bytes_read == 9
        assert wrapper.bytes_read == len(result)
        mock_progress_bar.update.assert_called_once_with(9)

    def test_progress_wrapper_seek(self):
        """Test ProgressWrapper seek method."""
        from futurehouse_client.clients.data_storage_methods import ProgressWrapper

        mock_file = Mock()
        mock_file.seek.return_value = 5

        mock_progress_bar = Mock()

        wrapper = ProgressWrapper(mock_file, mock_progress_bar)

        result = wrapper.seek(5)

        # Verify seek operation delegates to underlying file
        assert isinstance(result, int)
        assert result == 5
        assert mock_file.seek.called
        mock_file.seek.assert_called_once_with(5, 0)

    def test_progress_wrapper_tell(self):
        """Test ProgressWrapper tell method."""
        from futurehouse_client.clients.data_storage_methods import ProgressWrapper

        mock_file = Mock()
        mock_file.tell.return_value = 10

        mock_progress_bar = Mock()

        wrapper = ProgressWrapper(mock_file, mock_progress_bar)

        result = wrapper.tell()

        # Verify tell operation delegates to underlying file
        assert isinstance(result, int)
        assert result == 10
        assert mock_file.tell.called
        mock_file.tell.assert_called_once_with()
