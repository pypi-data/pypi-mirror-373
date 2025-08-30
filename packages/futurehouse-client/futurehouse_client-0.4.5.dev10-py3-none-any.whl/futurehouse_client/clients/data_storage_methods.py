import asyncio
import fnmatch
import json
import logging
import shutil
import tempfile
import zipfile
from os import PathLike
from pathlib import Path
from typing import Any, NoReturn
from uuid import UUID

import aiofiles
import aiohttp
import requests as requests_lib
from google.resumable_media import requests as resumable_requests
from httpx import AsyncClient, Client, HTTPStatusError, codes
from lmi.utils import gather_with_concurrency
from pydantic import HttpUrl
from requests.adapters import HTTPAdapter
from tenacity import (
    before_sleep_log,
    retry,
    stop_after_attempt,
    wait_exponential,
)
from tqdm import tqdm
from urllib3.util.retry import Retry

from futurehouse_client.models.data_storage_methods import (
    CreateDatasetPayload,
    DataContentType,
    DataStorageLocationPayload,
    DataStorageRequestPayload,
    DataStorageResponse,
    DataStorageType,
    DirectoryManifest,
    ManifestEntry,
)
from futurehouse_client.models.rest import (
    DataStorageSearchPayload,
    SearchCriterion,
)
from futurehouse_client.utils.general import retry_if_connection_error

# this is only required if they're using a yaml manifest
try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


logger = logging.getLogger(__name__)

# TODO: pdf support, unsure what package we want to use
SUPPORTED_FILE_TYPES_TO_TEXT_CONTENT = ["txt", "md", "csv", "json", "yaml", "yml"]
CHUNK_SIZE = 8 * 1024 * 1024  # 8MB
MAX_RETRIES = 3
SMALL_FILE_THRESHOLD_BYTES = 10 * 1024 * 1024  # 10MB
HTTP_RESUME_INCOMPLETE = 308
INITIATE_HEADERS = {
    "Content-Type": "application/octet-stream",
    "x-goog-resumable": "start",
    "Content-Length": "0",
}
DOWNLOAD_CONCURRENCY = 3


def _should_ignore_file(
    file_path: Path | PathLike,
    base_path: Path | PathLike,
    ignore_patterns: list[str] | None = None,
) -> bool:
    """Check if a file should be ignored based on ignore patterns.

    Args:
        file_path: Path to the file to check
        base_path: Base directory path
        ignore_patterns: List of ignore patterns (supports gitignore-style patterns)

    Returns:
        True if file should be ignored
    """
    if not ignore_patterns:
        return False

    try:
        file_path = Path(file_path)
        base_path = Path(base_path)
        rel_path = file_path.relative_to(base_path)
        rel_path_str = str(rel_path)

        for pattern in ignore_patterns:
            pattern = pattern.strip()
            if not pattern or pattern.startswith("#"):
                continue

            is_absolute_match = pattern.startswith("/") and rel_path_str.startswith(
                pattern[1:]
            )
            is_nested_match = "/" in pattern and pattern in rel_path_str
            is_name_match = fnmatch.fnmatch(file_path.name, pattern)
            is_part_match = pattern in rel_path.parts

            if is_absolute_match or is_nested_match or is_name_match or is_part_match:
                return True

    except ValueError:
        pass

    return False


def _read_ignore_file(dir_path: Path, ignore_filename: str = ".gitignore") -> list[str]:
    """Read ignore patterns from a file in the directory.

    Args:
        dir_path: Directory to look for ignore file
        ignore_filename: Name of ignore file to read

    Returns:
        List of ignore patterns
    """
    ignore_file = dir_path / ignore_filename
    if ignore_file.exists():
        try:
            with open(ignore_file, encoding="utf-8") as f:
                return [line.strip() for line in f]
        except Exception as e:
            logger.warning(f"Failed to read {ignore_filename}: {e}")
            return []
    else:
        return []


def _collect_ignore_patterns(
    dir_path: Path,
    ignore_patterns: list[str] | None = None,
    ignore_filename: str = ".gitignore",
) -> list[str]:
    """Collect all ignore patterns from multiple sources.

    Args:
        dir_path: Directory to check for ignore files
        ignore_patterns: Explicit ignore patterns
        ignore_filename: Name of ignore file to read from directory

    Returns:
        Combined list of ignore patterns
    """
    all_ignore_patterns = ignore_patterns or []
    file_patterns = _read_ignore_file(dir_path, ignore_filename)
    all_ignore_patterns.extend(file_patterns)

    default_ignores = [".git", "__pycache__", "*.pyc", ".DS_Store", "node_modules"]
    all_ignore_patterns.extend(default_ignores)

    return all_ignore_patterns


def _create_directory_zip(
    dir_path: Path,
    zip_path: Path,
    ignore_patterns: list[str] | None = None,
    ignore_filename: str = ".gitignore",
) -> int:
    """Create a zip file from a directory with ignore patterns.

    Args:
        dir_path: Directory to zip
        zip_path: Output zip file path
        ignore_patterns: Explicit ignore patterns
        ignore_filename: Name of ignore file to read from directory

    Returns:
        Size of created zip file in bytes
    """
    all_ignore_patterns = _collect_ignore_patterns(
        dir_path, ignore_patterns, ignore_filename
    )

    logger.debug(f"Creating zip with ignore patterns: {all_ignore_patterns}")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in dir_path.rglob("*"):
            if file_path.is_file() and not _should_ignore_file(
                file_path, dir_path, all_ignore_patterns
            ):
                arcname = file_path.relative_to(dir_path)
                zipf.write(file_path, arcname)
                logger.debug(f"Added to zip: {arcname}")

    zip_size = zip_path.stat().st_size
    logger.debug(f"Created zip file {zip_path} with size {zip_size:,} bytes")
    return zip_size


def _should_send_as_text_content(file_path: Path, file_size: int) -> bool:
    """Check if a file should be sent as text content instead of file upload.

    Args:
        file_path: Path to the file
        file_size: Size of file in bytes

    Returns:
        True if file should be sent as text content
    """
    # small files can be treated as raw text
    if file_size >= SMALL_FILE_THRESHOLD_BYTES:
        return False

    file_extension = file_path.suffix.lower().lstrip(".")
    return file_extension in SUPPORTED_FILE_TYPES_TO_TEXT_CONTENT


def _extract_text_from_file(file_path: Path) -> str | None:
    """Extract text content from a file.

    Args:
        file_path: Path to the file

    Returns:
        Extracted text content or None if extraction failed
    """
    file_extension = file_path.suffix.lower().lstrip(".")

    if file_extension in SUPPORTED_FILE_TYPES_TO_TEXT_CONTENT:
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.warning(f"Failed to extract text from {file_path}: {e}")
            return None
    else:
        return None


def _setup_upload_progress(file_path: Path, file_size: int, progress_bar: tqdm) -> None:
    """Common setup for upload progress tracking."""
    logger.debug(
        f"Starting resumable upload for file: {file_path} (size: {file_size:,} bytes)"
    )
    progress_bar.set_description(f"Uploading {file_path.name}")
    progress_bar.refresh()


async def _initiate_resumable_session(
    session: aiohttp.ClientSession, signed_url: str
) -> str:
    """Initiate resumable upload session and return session URI."""
    logger.debug("Initiating resumable upload session")
    async with session.post(signed_url, headers=INITIATE_HEADERS) as initiate_response:
        if initiate_response.status not in {200, 201}:
            error_text = await initiate_response.text()
            logger.error(
                f"Failed to initiate resumable session: {initiate_response.status}"
            )
            logger.error(f"Response: {error_text}")
            initiate_response.raise_for_status()

        return _validate_session_uri(initiate_response.headers.get("location"))


# TODO: temp
def _log_upload_debug(signed_url: str) -> None:
    """Common debug logging for uploads."""
    logger.debug(f"Signed URL: {signed_url[:100]}...")


# TODO: temp
def _validate_session_uri(session_uri: str | None) -> str:
    """Validate and return session URI or raise exception."""
    if not session_uri:
        raise DataStorageError(
            "No session URI returned from resumable upload initiation"
        )
    logger.debug(f"Resumable session initiated. Session URI: {session_uri[:100]}...")
    return session_uri


async def _upload_chunk_with_retry(
    session: aiohttp.ClientSession,
    session_uri: str,
    chunk_data: bytes,
    range_start: int,
    file_size: int,
    progress_bar: tqdm,
) -> int:
    """Upload a single chunk with retry logic."""
    range_end = range_start + len(chunk_data) - 1
    chunk_headers = {
        "Content-Type": "application/octet-stream",
        "Content-Length": str(len(chunk_data)),
        "Content-Range": f"bytes {range_start}-{range_end}/{file_size}",
    }

    for attempt in range(MAX_RETRIES):
        try:
            async with session.put(
                session_uri, data=chunk_data, headers=chunk_headers
            ) as chunk_response:
                if chunk_response.status == HTTP_RESUME_INCOMPLETE:
                    progress_bar.update(len(chunk_data))
                    logger.debug(f"Uploaded chunk: {range_end + 1}/{file_size} bytes")
                    return len(chunk_data)
                if chunk_response.status in {200, 201}:
                    progress_bar.update(len(chunk_data))
                    logger.debug(
                        f"Upload completed successfully. Final response: {chunk_response.status}"
                    )
                    return len(chunk_data)

                error_text = await chunk_response.text()
                logger.warning(
                    f"Chunk upload failed (attempt {attempt + 1}/{MAX_RETRIES}): {chunk_response.status}"
                )
                logger.warning(f"Response: {error_text}")
                if attempt == MAX_RETRIES - 1:
                    chunk_response.raise_for_status()

        except (TimeoutError, aiohttp.ClientError) as e:
            logger.warning(
                f"Chunk upload error (attempt {attempt + 1}/{MAX_RETRIES}): {e}"
            )
            if attempt == MAX_RETRIES - 1:
                raise
            await asyncio.sleep(2**attempt)

    return 0


async def _aupload_file_with_progress(
    signed_url: str, file_path: Path, progress_bar: tqdm, file_size: int
) -> None:
    """Upload a file asynchronously using aiohttp with signed URL initiation."""
    _setup_upload_progress(file_path, file_size, progress_bar)
    _log_upload_debug(signed_url)

    try:
        retry_config = aiohttp.ClientTimeout(
            total=max(600.0, file_size / (512 * 1024)), connect=30, sock_read=30
        )
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)

        async with aiohttp.ClientSession(
            connector=connector, timeout=retry_config
        ) as session:
            session_uri = await _initiate_resumable_session(session, signed_url)

            async with aiofiles.open(file_path, "rb") as file_obj:
                bytes_uploaded = 0

                while bytes_uploaded < file_size:
                    remaining = file_size - bytes_uploaded
                    current_chunk_size = min(CHUNK_SIZE, remaining)
                    chunk_data = await file_obj.read(current_chunk_size)

                    if not chunk_data:
                        break

                    uploaded_bytes = await _upload_chunk_with_retry(
                        session,
                        session_uri,
                        chunk_data,
                        bytes_uploaded,
                        file_size,
                        progress_bar,
                    )
                    bytes_uploaded += uploaded_bytes

                    if bytes_uploaded >= file_size:
                        break

                logger.debug("Upload completed successfully")

    except Exception as e:
        logger.error(f"Async resumable upload error: {type(e).__name__}: {e}")
        raise


def _upload_file_with_progress(
    signed_url: str, file_path: Path, progress_bar: tqdm, file_size: int
) -> None:
    """Upload a file synchronously using google.resumable_media with signed URL initiation."""
    _setup_upload_progress(file_path, file_size, progress_bar)
    _log_upload_debug(signed_url)

    try:
        session = requests_lib.Session()
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "PUT", "PATCH"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        logger.debug("Initiating resumable upload session")
        initiate_response = session.post(
            signed_url, headers=INITIATE_HEADERS, timeout=30
        )

        if initiate_response.status_code not in {200, 201}:
            logger.error(
                f"Failed to initiate resumable session: {initiate_response.status_code}"
            )
            logger.error(f"Response: {initiate_response.text}")
            initiate_response.raise_for_status()

        session_uri = _validate_session_uri(initiate_response.headers.get("location"))

        with open(file_path, "rb") as file_obj:
            upload = resumable_requests.ResumableUpload(
                upload_url=signed_url, chunk_size=CHUNK_SIZE
            )

            upload._resumable_url = session_uri
            upload._stream = file_obj
            upload._total_bytes = file_size

            wrapped_file = ProgressWrapper(file_obj, progress_bar)
            upload._stream = wrapped_file

            while not upload.finished:
                try:
                    upload.transmit_next_chunk(session)
                except Exception as e:
                    logger.error(f"Chunk upload failed: {e}")
                    raise

            logger.debug("Upload completed successfully using resumable_media library")

    except Exception as e:
        logger.error(f"Sync resumable upload error: {type(e).__name__}: {e}")
        raise


class RestClientError(Exception):
    """Base exception for REST client errors."""


class DataStorageError(RestClientError):
    """Base exception for data storage operations."""


class DataStorageCreationError(DataStorageError):
    """Raised when there's an error creating a data storage entry."""


class DataStorageRetrievalError(DataStorageError):
    """Raised when there's an error retrieving a data storage entry."""


class ProgressWrapper:
    """Common progress wrapper for file uploads."""

    def __init__(self, file_obj, progress_bar):
        self.file_obj = file_obj
        self.progress_bar = progress_bar
        self.bytes_read = 0

    def read(self, size=-1):
        data = self.file_obj.read(size)
        if data:
            self.bytes_read += len(data)
            current_pos = self.file_obj.tell()
            if current_pos > self.progress_bar.n:
                self.progress_bar.update(current_pos - self.progress_bar.n)
        return data

    def seek(self, offset, whence=0):
        return self.file_obj.seek(offset, whence)

    def tell(self):
        return self.file_obj.tell()


class DataStorageMethods:
    """Data storage methods for RestClient.

    This class contains methods for interacting with the data storage API endpoints.
    """

    # needed for mypy `NoReturn`
    def _handle_http_errors(self, e: HTTPStatusError, operation: str) -> NoReturn:
        """Handle common HTTP errors for data storage operations."""
        if e.response.status_code == codes.FORBIDDEN:
            raise DataStorageError(
                f"Error {operation} data storage entry, not authorized"
            ) from e
        if e.response.status_code == codes.UNPROCESSABLE_ENTITY:
            raise DataStorageError(f"Invalid request payload: {e.response.text}") from e
        raise DataStorageError(
            f"Error {operation} data storage entry: {e.response.status_code} - {e.response.text}"
        ) from e

    def _validate_file_path(self, file_path: str | Path) -> Path:
        """Validate file path exists and return Path object."""
        file_path = Path(file_path)
        if not file_path.exists():
            raise DataStorageError(f"File or directory not found: {file_path}")
        return file_path

    def _build_zip_path(self, name: str, path: str | None) -> str:
        """Build GCS path for zip file."""
        zip_filename = name if name.endswith(".zip") else f"{name}.zip"
        if path:
            return f"{path.rstrip('/')}/{zip_filename}"
        return zip_filename

    # TODO: methods in here need to be moved to fh tools
    # =====================================
    def _is_zip_file(self, file_path: Path) -> bool:
        """Check if a file is a zip file by checking its magic bytes."""
        try:
            with open(file_path, "rb") as f:
                magic = f.read(2)
                return magic == b"PK"
        except Exception:
            return False

    def _extract_zip_file(self, zip_path: Path, extract_to: Path) -> Path:
        """Extract a zip file and return the path to the extracted content.

        Args:
            zip_path: Path to the zip file
            extract_to: Directory to extract to

        Returns:
            Path to the extracted content (directory or single file)
        """
        extract_dir = extract_to / "extracted"
        extract_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_dir)
        extracted_items = list(extract_dir.iterdir())

        if len(extracted_items) == 1:
            return extracted_items[0]
        return extract_dir

    async def _adownload_from_gcs(
        self, signed_url: str, file_name: str | None = None
    ) -> Path:
        """Download file from GCS using signed URL and handle unzipping if needed.

        Args:
            signed_url: The signed URL to download from
            file_name: The name of the file to download

        Returns:
            Path to the downloaded file (or unzipped directory if it was a zip)
        """
        file_name = file_name or "downloaded_file"

        try:
            with tempfile.TemporaryDirectory() as temp_dir_str:
                temp_dir = Path(temp_dir_str)
                temp_file = temp_dir / file_name

                async with self.async_client.stream("GET", signed_url) as response:
                    response.raise_for_status()

                    content_disposition = response.headers.get(
                        "content-disposition", ""
                    )
                    filename = file_name
                    if "filename=" in content_disposition:
                        filename = content_disposition.split("filename=")[-1].strip('"')

                    if filename != file_name:
                        temp_file = temp_dir / filename

                    async with aiofiles.open(temp_file, "wb") as f:
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            await f.write(chunk)

                    logger.debug(
                        f"Downloaded file to {temp_file} (size: {temp_file.stat().st_size:,} bytes)"
                    )

                    if self._is_zip_file(temp_file):
                        logger.debug(f"File {temp_file} is a zip file, extracting...")
                        extracted_path = self._extract_zip_file(temp_file, temp_dir)

                        final_temp_dir = Path(tempfile.mkdtemp())
                        final_path = final_temp_dir / extracted_path.name

                        if extracted_path.is_dir():
                            shutil.copytree(extracted_path, final_path)
                        else:
                            shutil.copy2(extracted_path, final_path)

                        return final_path
                    final_temp_dir = Path(tempfile.mkdtemp())
                    final_file = final_temp_dir / temp_file.name
                    shutil.copy2(temp_file, final_file)
                    return final_file

        except Exception as e:
            raise DataStorageError(f"Failed to download from GCS: {e}") from e

    def _download_from_gcs(self, signed_url: str, file_name: str | None = None) -> Path:
        """Download file from GCS using signed URL and handle unzipping if needed (sync version).

        Args:
            signed_url: The signed URL to download from
            file_name: The name of the file to download
        Returns:
            Path to the downloaded file (or unzipped directory if it was a zip)
        """
        file_name = file_name or "downloaded_file"

        try:
            with tempfile.TemporaryDirectory() as temp_dir_str:
                temp_dir = Path(temp_dir_str)
                temp_file = temp_dir / file_name

                with requests_lib.get(signed_url, stream=True, timeout=30) as response:
                    response.raise_for_status()

                    content_disposition = response.headers.get(
                        "content-disposition", ""
                    )
                    filename = file_name
                    if "filename=" in content_disposition:
                        filename = content_disposition.split("filename=")[-1].strip('"')

                    if filename != file_name:
                        temp_file = temp_dir / filename

                    with open(temp_file, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    logger.debug(
                        f"Downloaded file to {temp_file} (size: {temp_file.stat().st_size:,} bytes)"
                    )

                    if self._is_zip_file(temp_file):
                        logger.debug(f"File {temp_file} is a zip file, extracting...")
                        extracted_path = self._extract_zip_file(temp_file, temp_dir)

                        final_temp_dir = Path(tempfile.mkdtemp())
                        final_path = final_temp_dir / extracted_path.name

                        if extracted_path.is_dir():
                            shutil.copytree(extracted_path, final_path)
                        else:
                            shutil.copy2(extracted_path, final_path)

                        return final_path
                    final_temp_dir = Path(tempfile.mkdtemp())
                    final_file = final_temp_dir / temp_file.name
                    shutil.copy2(temp_file, final_file)
                    return final_file

        except Exception as e:
            raise DataStorageError(f"Failed to download from GCS: {e}") from e

    def _prepare_single_file_upload(
        self, name: str, file_path: Path, description: str | None, path: str | None
    ) -> tuple[int, DataStorageRequestPayload | None]:
        """Prepare single file for upload, return file size and payload if text content."""
        file_size = file_path.stat().st_size
        logger.debug(
            f"Starting upload of single file: {file_path} (size: {file_size:,} bytes)"
        )

        if _should_send_as_text_content(file_path, file_size):
            logger.debug(
                f"Small text file ({file_size:,} bytes) - sending as text content"
            )
            text_content = _extract_text_from_file(file_path)
            if text_content is not None:
                return file_size, DataStorageRequestPayload(
                    name=name,
                    description=description,
                    content=text_content,
                    path=path,
                    is_collection=False,
                )
            logger.warning(
                "Could not extract text content, falling back to file upload"
            )

        return file_size, None

    def _create_data_storage_entry(
        self, payload: DataStorageRequestPayload
    ) -> DataStorageResponse:
        """Create data storage entry via API (sync version)."""
        response = self.client.post(
            "/v0.1/data-storage/data-entries",
            json=payload.model_dump(mode="json", exclude_none=True),
        )
        response.raise_for_status()
        return DataStorageResponse.model_validate(response.json())

    async def _acreate_data_storage_entry(
        self, payload: DataStorageRequestPayload
    ) -> DataStorageResponse:
        """Create data storage entry via API (async version)."""
        response = await self.async_client.post(
            "/v0.1/data-storage/data-entries",
            json=payload.model_dump(mode="json", exclude_none=True),
        )
        response.raise_for_status()
        return DataStorageResponse.model_validate(response.json())

    def _generate_folder_description_from_files(
        self, dir_path: Path, manifest: DirectoryManifest
    ) -> str:
        """Generate folder description by concatenating descriptions of top-level files."""
        descriptions = []

        # Get top-level files only (not recursive)
        for item in dir_path.iterdir():
            if item.is_file():
                # Try to get description from manifest first
                file_desc = manifest.get_entry_description(item.name)

                if file_desc:
                    descriptions.append(f"{item.name}: {file_desc}")
                else:
                    descriptions.append(item.name)

        if descriptions:
            return f"Directory containing: {', '.join(descriptions)}"
        return f"Directory: {dir_path.name}"

    def _load_manifest(
        self, dir_path: Path, manifest_filename: str | None
    ) -> DirectoryManifest:
        """Load and parse a manifest file (JSON or YAML) into a structured model."""
        if not manifest_filename:
            return DirectoryManifest()

        manifest_path = dir_path / manifest_filename
        if not manifest_path.exists():
            logger.error(f"Manifest file not found at {manifest_path}")
            raise DataStorageCreationError(
                f"Manifest file {manifest_filename} not found in directory {dir_path}. Ensure the manifest exists and is correctly named, or do not pass it as an argument."
            )

        try:
            with open(manifest_path, encoding="utf-8") as f:
                data = {}
                if manifest_filename.lower().endswith(".json"):
                    data = json.load(f)
                elif manifest_filename.lower().endswith((".yaml", ".yml")):
                    if yaml is None:
                        raise ImportError(
                            "pyyaml is required to parse .yaml manifest files. "
                            "Please install it with `pip install pyyaml`."
                        )
                    data = yaml.safe_load(f)
                else:
                    logger.warning(
                        f"Unsupported manifest file extension: {manifest_filename}"
                    )
                    return DirectoryManifest()

                return DirectoryManifest.from_dict(data or {})

        except Exception as e:
            logger.warning(f"Failed to load manifest {manifest_filename}: {e}")

        return DirectoryManifest()

    def _upload_data_directory(
        self,
        name: str,
        dir_path: Path,
        description: str | None,
        path: str | None = None,
        ignore_patterns: list[str] | None = None,
        ignore_filename: str = ".gitignore",
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Upload a directory as a single zip file collection.

        Args:
            name: Name for the directory collection
            dir_path: Path to directory to zip and upload
            description: Description for the collection
            path: Optional GCS path for the zip file
            ignore_patterns: List of patterns to ignore when zipping
            ignore_filename: Name of ignore file to read from directory
            project_id: ID of the project this data storage entry belongs to

        Returns:
            DataStorageResponse for the uploaded zip file
        """
        logger.debug(f"Uploading directory as zip: {dir_path}")

        with tempfile.NamedTemporaryFile(suffix=".zip") as temp_file:
            temp_zip_path = Path(temp_file.name)

            zip_size = _create_directory_zip(
                dir_path, temp_zip_path, ignore_patterns, ignore_filename
            )

            zip_gcs_path = self._build_zip_path(name, path)
            payload = DataStorageRequestPayload(
                name=name,
                description=description,
                path=zip_gcs_path,
                is_collection=True,
                project_id=project_id,
            )

            logger.debug(
                f"Creating data storage entry for zip: {payload.model_dump(exclude_none=True)}"
            )
            data_storage_response = self._create_data_storage_entry(payload)

            for storage_location in data_storage_response.storage_locations:
                if not storage_location.storage_config.signed_url:
                    raise DataStorageCreationError(
                        "No signed URL returned for zip upload"
                    )

                with tqdm(
                    total=zip_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"Uploading {dir_path.name} (zipped)",
                    miniters=1,
                    mininterval=0.1,
                ) as pbar:
                    _upload_file_with_progress(
                        storage_location.storage_config.signed_url,
                        temp_zip_path,
                        pbar,
                        zip_size,
                    )

            status_response = self.client.patch(
                f"/v0.1/data-storage/data-entries/{data_storage_response.data_storage.id}",
                json={"status": "active"},
            )
            status_response.raise_for_status()

            logger.debug(
                f"Successfully uploaded directory {dir_path.name} as zip ({zip_size:,} bytes)"
            )
            return DataStorageResponse.model_validate(status_response.json())

    async def _aupload_data_directory(
        self,
        name: str,
        dir_path: Path,
        description: str | None,
        path: str | None = None,
        ignore_patterns: list[str] | None = None,
        ignore_filename: str = ".gitignore",
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Asynchronously upload a directory as a single zip file.

        Args:
            name: Name for the directory collection
            dir_path: Path to directory to zip and upload
            description: Description for the collection
            path: Optional GCS path for the zip file
            ignore_patterns: List of patterns to ignore when zipping
            ignore_filename: Name of ignore file to read from directory
            project_id: ID of the project this data storage entry belongs to

        Returns:
            DataStorageResponse for the uploaded zip file
        """
        logger.debug(f"Async uploading directory as zip: {dir_path}")

        with tempfile.NamedTemporaryFile(suffix=".zip") as temp_file:
            temp_zip_path = Path(temp_file.name)

            zip_size = _create_directory_zip(
                dir_path, temp_zip_path, ignore_patterns, ignore_filename
            )

            zip_gcs_path = self._build_zip_path(name, path)
            payload = DataStorageRequestPayload(
                name=name,
                description=description,
                path=zip_gcs_path,
                is_collection=True,
                project_id=project_id,
            )

            data_storage_response = await self._acreate_data_storage_entry(payload)

            for storage_location in data_storage_response.storage_locations:
                if not storage_location.storage_config.signed_url:
                    raise DataStorageCreationError(
                        "No signed URL returned for zip upload"
                    )

                with tqdm(
                    total=zip_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"Uploading {dir_path.name} (zipped)",
                    miniters=1,
                    mininterval=0.1,
                ) as pbar:
                    await _aupload_file_with_progress(
                        storage_location.storage_config.signed_url,
                        temp_zip_path,
                        pbar,
                        zip_size,
                    )

            status_response = await self.async_client.patch(
                f"/v0.1/data-storage/data-entries/{data_storage_response.data_storage.id}",
                json={"status": "active"},
            )
            status_response.raise_for_status()

            logger.debug(
                f"Successfully uploaded directory {dir_path.name} as zip ({zip_size:,} bytes)"
            )
            return DataStorageResponse.model_validate(status_response.json())

    def _upload_data_single_file(
        self,
        name: str,
        file_path: Path,
        description: str | None,
        path: str | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Upload a single file."""
        file_size = file_path.stat().st_size
        logger.debug(
            f"Starting upload of single file: {file_path} (size: {file_size:,} bytes)"
        )

        if _should_send_as_text_content(file_path, file_size):
            logger.debug(
                f"Small text file ({file_size:,} bytes) - sending as text content"
            )

            text_content = _extract_text_from_file(file_path)
            if text_content is not None:
                payload = DataStorageRequestPayload(
                    name=name,
                    description=description,
                    content=text_content,
                    path=path,
                    is_collection=False,
                    project_id=project_id,
                )

                logger.debug("Sending file as text content")
                return self._create_data_storage_entry(payload)
            logger.warning(
                "Could not extract text content, falling back to file upload"
            )

        logger.debug(
            f"Large/binary file ({file_size:,} bytes) - requesting signed URL for upload"
        )
        payload = DataStorageRequestPayload(
            name=name,
            description=description,
            path=path,
            is_collection=False,
            project_id=project_id,
        )

        logger.debug(
            f"Requesting signed URL with payload: {payload.model_dump(exclude_none=True)}"
        )

        data_storage_response = self._create_data_storage_entry(payload)

        for storage_location in data_storage_response.storage_locations:
            if not storage_location.storage_config.signed_url:
                raise DataStorageCreationError("No signed URL returned from server")

            with tqdm(
                total=file_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=f"Uploading {file_path.name}",
                miniters=1,
                mininterval=0.1,
            ) as pbar:
                try:
                    _upload_file_with_progress(
                        storage_location.storage_config.signed_url,
                        file_path,
                        pbar,
                        file_size,
                    )
                    logger.debug("File upload to signed URL completed successfully")
                except Exception as e:
                    logger.error(f"Failed to upload file to signed URL: {e}")
                    raise

        logger.debug("Updating data storage status to active")
        status_response = self.client.patch(
            f"/v0.1/data-storage/data-entries/{data_storage_response.data_storage.id}",
            json={"status": "active"},
        )
        status_response.raise_for_status()
        logger.debug("Data storage status updated successfully")

        return DataStorageResponse.model_validate(status_response.json())

    async def _aupload_data_single_file(
        self,
        name: str,
        file_path: Path,
        description: str | None,
        path: str | None = None,
        dataset_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Asynchronously upload a single file."""
        file_size, text_payload = self._prepare_single_file_upload(
            name, file_path, description, path
        )

        if text_payload:
            logger.debug("Sending file as text content")
            text_payload.dataset_id = dataset_id
            return await self._acreate_data_storage_entry(text_payload)

        logger.debug(
            f"Large/binary file ({file_size:,} bytes) - requesting signed URL for upload"
        )
        payload = DataStorageRequestPayload(
            name=name,
            description=description,
            path=path,
            is_collection=False,
            dataset_id=dataset_id,
            project_id=project_id,
        )

        data_storage_response = await self._acreate_data_storage_entry(payload)

        for location in data_storage_response.storage_locations:
            if not location.storage_config.signed_url:
                raise DataStorageCreationError(
                    f"No signed URL returned from server for location: {location.id}"
                )

            with tqdm(
                total=file_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=f"Uploading {file_path.name}",
                miniters=1,
                mininterval=0.1,
                leave=False,
            ) as pbar:
                await _aupload_file_with_progress(
                    location.storage_config.signed_url, file_path, pbar, file_size
                )

        status_response = await self.async_client.patch(
            f"/v0.1/data-storage/data-entries/{data_storage_response.data_storage.id}",
            json={"status": "active"},
        )
        status_response.raise_for_status()

        return DataStorageResponse.model_validate(status_response.json())

    def _upload_data_single_file_with_parent(
        self,
        name: str,
        file_path: Path,
        description: str | None,
        path: str | None,
        parent_id: UUID | None,
        dataset_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Upload a single file with a parent ID (sync version)."""
        file_size, text_payload = self._prepare_single_file_upload(
            name, file_path, description, path
        )

        if text_payload:
            logger.debug("Sending file as text content with parent_id")
            text_payload.parent_id = parent_id
            text_payload.dataset_id = dataset_id
            text_payload.project_id = project_id
            return self._create_data_storage_entry(text_payload)

        logger.debug(
            f"Large/binary file ({file_size:,} bytes) - requesting signed URL for upload"
        )
        payload = DataStorageRequestPayload(
            name=name,
            description=description,
            path=path,
            is_collection=False,
            parent_id=parent_id,
            dataset_id=dataset_id,
            project_id=project_id,
        )
        data_storage_response = self._create_data_storage_entry(payload)

        for location in data_storage_response.storage_locations:
            if not location.storage_config.signed_url:
                raise DataStorageCreationError("No signed URL returned from server")

            with tqdm(
                total=file_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                desc=f"Uploading {file_path.name}",
                miniters=1,
                mininterval=0.1,
                leave=False,
            ) as pbar:
                _upload_file_with_progress(
                    location.storage_config.signed_url, file_path, pbar, file_size
                )

        status_response = self.client.patch(
            f"/v0.1/data-storage/data-entries/{data_storage_response.data_storage.id}",
            json={"status": "active"},
        )
        status_response.raise_for_status()

        return DataStorageResponse.model_validate(status_response.json())

    def _process_file_item(
        self,
        item: Path,
        dir_manifest: DirectoryManifest,
        current_parent_id: UUID,
        dataset_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse | None:
        """Process a single file item for upload."""
        try:
            manifest_desc = dir_manifest.get_entry_description(item.name)
            file_description = manifest_desc or f"File: {item.name}"

            logger.debug(
                f"Processing file {item.name} with description: '{file_description}'"
            )

            return self._upload_data_single_file_with_parent(
                name=item.name,
                file_path=item,
                description=file_description,
                path=None,
                parent_id=current_parent_id,
                dataset_id=dataset_id,
                project_id=project_id,
            )
        except Exception as e:
            logger.error(f"Failed to upload file {item}: {e}")
            return None

    def _upload_directory_hierarchically(
        self,
        name: str,
        dir_path: Path,
        description: str | None = None,
        manifest_filename: str | None = None,
        parent_id: UUID | None = None,
        ignore_patterns: list[str] | None = None,
        ignore_filename: str = ".gitignore",
        base_dir: Path | None = None,
        dir_manifest: DirectoryManifest | None = None,
        dataset_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> list[DataStorageResponse]:
        """Upload a directory with single dataset and individual file storage entries."""
        responses = []
        if parent_id is None:
            base_dir = dir_path
            all_ignore_patterns = _collect_ignore_patterns(
                base_dir, ignore_patterns, ignore_filename
            )

            payload = DataStorageRequestPayload(
                name=name,
                description=description,
                parent_id=None,
                dataset_id=None,
                is_collection=False,
                project_id=project_id,
            )

            dir_response = self._create_data_storage_entry(payload)
            responses.append(dir_response)
            current_parent_id = dir_response.data_storage.id
            current_dataset_id = dir_response.data_storage.dataset_id

            dir_manifest = self._load_directory_manifest(
                manifest_filename, parent_id, dir_path
            )
        else:
            all_ignore_patterns = ignore_patterns or []
            current_parent_id = parent_id
            current_dataset_id = dataset_id

        for item in dir_path.iterdir():
            if base_dir and _should_ignore_file(item, base_dir, all_ignore_patterns):
                continue

            if item.is_dir():
                subdir_manifest = DirectoryManifest()
                if dir_manifest:
                    entry = dir_manifest.entries.get(item.name)
                    if isinstance(entry, DirectoryManifest):
                        subdir_manifest = entry
                    elif isinstance(entry, ManifestEntry):
                        # Convert single entry to manifest
                        subdir_manifest = DirectoryManifest(entries={item.name: entry})

                subdir_description = subdir_manifest.get_entry_description(item.name)
                if not subdir_description:
                    subdir_description = self._generate_folder_description_from_files(
                        item, subdir_manifest
                    )

                subdir_payload = DataStorageRequestPayload(
                    name=item.name,
                    description=subdir_description,
                    parent_id=current_parent_id,
                    dataset_id=current_dataset_id,
                    is_collection=False,
                    project_id=project_id,
                )
                subdir_response = self._create_data_storage_entry(subdir_payload)
                responses.append(subdir_response)

                subdir_responses = self._upload_directory_hierarchically(
                    name=item.name,
                    dir_path=item,
                    description=None,
                    manifest_filename=None,
                    parent_id=subdir_response.data_storage.id,
                    ignore_patterns=all_ignore_patterns,
                    ignore_filename=ignore_filename,
                    base_dir=base_dir,
                    dir_manifest=subdir_manifest,
                    dataset_id=current_dataset_id,
                    project_id=project_id,
                )
                responses.extend(subdir_responses)
            elif item.is_file():
                file_response = self._process_file_item(
                    item,
                    dir_manifest or DirectoryManifest(),
                    current_parent_id,
                    current_dataset_id,
                )
                if file_response:
                    responses.append(file_response)

        return responses

    def _load_directory_manifest(
        self,
        manifest_filename: str | None,
        parent_id: UUID | None,
        dir_path: Path,
    ) -> DirectoryManifest:
        """Load directory manifest if available."""
        if manifest_filename and not parent_id:
            manifest_data = self._load_manifest(Path.cwd(), manifest_filename)
            dir_name = dir_path.name
            logger.debug(
                f"Loaded manifest entries: {list(manifest_data.entries.keys())}"
            )
            logger.debug(
                f"Looking for manifest entry with directory name: '{dir_name}'"
            )

            entry = manifest_data.entries.get(dir_name)
            if isinstance(entry, DirectoryManifest):
                return entry
            if isinstance(entry, ManifestEntry):
                return DirectoryManifest(entries={dir_name: entry})
            logger.debug(
                f"No manifest entry found for '{dir_name}', available keys: {list(manifest_data.entries.keys())}"
            )
            return DirectoryManifest()
        return DirectoryManifest()

    async def _aupload_data_single_file_with_parent(
        self,
        name: str,
        file_path: Path,
        description: str | None,
        path: str | None,
        parent_id: UUID | None,
        dataset_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Asynchronously upload a single file with a parent ID."""
        file_size, text_payload = self._prepare_single_file_upload(
            name, file_path, description, path
        )

        if text_payload:
            logger.debug("Sending file as text content with parent_id")
            text_payload.parent_id = parent_id
            text_payload.dataset_id = dataset_id
            text_payload.project_id = project_id
            return await self._acreate_data_storage_entry(text_payload)

        logger.debug(
            f"Large/binary file ({file_size:,} bytes) - requesting signed URL for upload"
        )
        payload = DataStorageRequestPayload(
            name=name,
            description=description,
            path=path,
            is_collection=False,
            parent_id=parent_id,
            dataset_id=dataset_id,
            project_id=project_id,
        )
        data_storage_response = await self._acreate_data_storage_entry(payload)

        storage_location = data_storage_response.storage_locations[0]

        if not storage_location.storage_config.signed_url:
            raise DataStorageCreationError("No signed URL returned from server")

        with tqdm(
            total=file_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            desc=f"Uploading {file_path.name}",
            miniters=1,
            mininterval=0.1,
        ) as pbar:
            await _aupload_file_with_progress(
                storage_location.storage_config.signed_url, file_path, pbar, file_size
            )

        status_response = await self.async_client.patch(
            f"/v0.1/data-storage/data-entries/{data_storage_response.data_storage.id}",
            json={"status": "active"},
        )
        status_response.raise_for_status()

        return DataStorageResponse.model_validate(status_response.json())

    async def _aprocess_file_item(
        self,
        item: Path,
        dir_manifest: DirectoryManifest,
        current_parent_id: UUID,
        dataset_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse | None:
        """Asynchronously process a single file item for upload."""
        try:
            manifest_desc = dir_manifest.get_entry_description(item.name)
            file_description = manifest_desc or f"File: {item.name}"

            logger.debug(
                f"Processing file {item.name} with description: '{file_description}'"
            )

            return await self._aupload_data_single_file_with_parent(
                name=item.name,
                file_path=item,
                description=file_description,
                path=None,
                parent_id=current_parent_id,
                dataset_id=dataset_id,
                project_id=project_id,
            )
        except Exception as e:
            logger.error(f"Failed to upload file {item}: {e}")
            return None

    async def _aupload_directory_hierarchically(
        self,
        name: str,
        dir_path: Path,
        description: str | None = None,
        manifest_filename: str | None = None,
        parent_id: UUID | None = None,
        ignore_patterns: list[str] | None = None,
        ignore_filename: str = ".gitignore",
        base_dir: Path | None = None,
        dir_manifest: DirectoryManifest | None = None,
        dataset_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> list[DataStorageResponse]:
        """Upload a directory with single dataset and individual file storage entries (async)."""
        responses = []

        if parent_id is None:
            base_dir = dir_path
            all_ignore_patterns = _collect_ignore_patterns(
                base_dir, ignore_patterns, ignore_filename
            )

            payload = DataStorageRequestPayload(
                name=name,
                description=description,
                parent_id=None,
                dataset_id=None,
                is_collection=False,
                project_id=project_id,
            )

            dir_response = await self._acreate_data_storage_entry(payload)
            responses.append(dir_response)
            current_parent_id = dir_response.data_storage.id
            current_dataset_id = dir_response.data_storage.dataset_id

            dir_manifest = self._load_directory_manifest(
                manifest_filename, parent_id, dir_path
            )
        else:
            all_ignore_patterns = ignore_patterns or []
            current_parent_id = parent_id
            current_dataset_id = dataset_id

        for item in dir_path.iterdir():
            if base_dir and _should_ignore_file(item, base_dir, all_ignore_patterns):
                continue

            if item.is_dir():
                subdir_manifest = DirectoryManifest()
                if dir_manifest:
                    entry = dir_manifest.entries.get(item.name)
                    if isinstance(entry, DirectoryManifest):
                        subdir_manifest = entry
                    elif isinstance(entry, ManifestEntry):
                        subdir_manifest = DirectoryManifest(entries={item.name: entry})

                subdir_description = subdir_manifest.get_entry_description(item.name)
                if not subdir_description:
                    subdir_description = self._generate_folder_description_from_files(
                        item, subdir_manifest
                    )

                subdir_payload = DataStorageRequestPayload(
                    name=item.name,
                    description=subdir_description,
                    parent_id=current_parent_id,
                    dataset_id=current_dataset_id,
                    is_collection=False,
                    project_id=project_id,
                )
                subdir_response = await self._acreate_data_storage_entry(subdir_payload)
                responses.append(subdir_response)

                subdir_responses = await self._aupload_directory_hierarchically(
                    name=item.name,
                    dir_path=item,
                    description=None,
                    manifest_filename=None,
                    parent_id=subdir_response.data_storage.id,
                    ignore_patterns=all_ignore_patterns,
                    ignore_filename=ignore_filename,
                    base_dir=base_dir,
                    dir_manifest=subdir_manifest,
                    dataset_id=current_dataset_id,
                    project_id=project_id,
                )
                responses.extend(subdir_responses)
            elif item.is_file():
                file_response = await self._aprocess_file_item(
                    item,
                    dir_manifest or DirectoryManifest(),
                    current_parent_id,
                    current_dataset_id,
                )
                if file_response:
                    responses.append(file_response)

        return responses

    @property
    def client(self) -> Client:
        raise NotImplementedError("client property must be implemented by subclass")

    @property
    def async_client(self) -> AsyncClient:
        raise NotImplementedError(
            "async_client property must be implemented by subclass"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def store_text_content(
        self,
        name: str,
        content: str,
        description: str | None = None,
        path: str | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Store content as a string in the data storage system.

        Args:
            name: Name of the data storage entry
            content: Content to store as a string
            description: Optional description of the data storage entry
            path: Optional path for the data storage entry
            project_id: ID of the project this data storage entry belongs to

        Returns:
            DataStorageResponse containing the created data storage entry and storage locations

        Raises:
            DataStorageCreationError: If there's an error creating the data storage entry
        """
        try:
            payload = DataStorageRequestPayload(
                name=name,
                content=content,
                description=description,
                path=path,
                project_id=project_id,
            )
            return self._create_data_storage_entry(payload)
        except HTTPStatusError as e:
            self._handle_http_errors(e, "creating")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def astore_text_content(
        self,
        name: str,
        content: str,
        description: str | None = None,
        path: str | None = None,
        dataset_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Asynchronously store content as a string in the data storage system.

        Args:
            name: Name of the data storage entry
            content: Content to store as a string
            description: Optional description of the data storage entry
            path: Optional path for the data storage entry
            dataset_id: Optional dataset ID to add entry to, or None to create new dataset
            project_id: ID of the project this data storage entry belongs to

        Returns:
            DataStorageResponse containing the created data storage entry and storage locations

        Raises:
            DataStorageCreationError: If there's an error creating the data storage entry
        """
        try:
            payload = DataStorageRequestPayload(
                name=name,
                content=content,
                description=description,
                path=path,
                dataset_id=dataset_id,
                project_id=project_id,
            )
            return await self._acreate_data_storage_entry(payload)
        except HTTPStatusError as e:
            self._handle_http_errors(e, "creating")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def astore_link(
        self,
        name: str,
        url: HttpUrl,
        description: str,
        instructions: str,
        api_key: str | None = None,
        metadata: dict[str, Any] | None = None,
        dataset_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Asynchronously store a link/URL in the data storage system.

        Args:
            name: Name of the link entry
            url: The URL/link to store
            description: Searchable details of the link
            instructions: Instructions for how to consume the link or api
            api_key: Any authentication key to access the api. If this is included, you should also include
                details of how the key should be consumed in the instructions.
            metadata: Any additional metadata about the link
            dataset_id: Optional dataset ID to add entry to, or None to create new dataset
            project_id: ID of the project this data storage entry belongs to

        Returns:
            DataStorageResponse containing the created link storage entry

        Raises:
            DataStorageCreationError: If there's an error creating the link storage entry
        """
        try:
            link_metadata = metadata.copy() if metadata else {}
            link_metadata["instructions"] = instructions
            if api_key:
                link_metadata["api_key"] = api_key

            existing_location = DataStorageLocationPayload(
                storage_type=DataStorageType.LINK,
                content_type=DataContentType.TEXT,
                location=str(url),
                metadata=link_metadata or None,
            )

            payload = DataStorageRequestPayload(
                name=name,
                content=str(url),
                description=description,
                dataset_id=dataset_id,
                project_id=project_id,
                existing_location=existing_location,
            )
            return await self._acreate_data_storage_entry(payload)
        except HTTPStatusError as e:
            self._handle_http_errors(e, "creating")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred: {e!r}"
            ) from e

    def store_link(
        self,
        name: str,
        url: HttpUrl,
        description: str,
        instructions: str,
        api_key: str | None = None,
        metadata: dict[str, Any] | None = None,
        dataset_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Store a link/URL in the data storage system.

        Args:
            name: Name of the link entry
            url: The URL/link to store
            description: Searchable details of the link
            instructions: Instructions for how to consume the link or api
            api_key: Any authentication key to access the api. If this is included, you should also include
                details of how the key should be consumed in the instructions.
            metadata: Any additional metadata about the link
            dataset_id: Optional dataset ID to add entry to, or None to create new dataset
            project_id: ID of the project this data storage entry belongs to

        Returns:
            DataStorageResponse containing the created link storage entry

        Raises:
            DataStorageCreationError: If there's an error creating the link storage entry
        """
        try:
            link_metadata = metadata.copy() if metadata else {}
            link_metadata["instructions"] = instructions
            if api_key:
                link_metadata["api_key"] = api_key

            existing_location = DataStorageLocationPayload(
                storage_type=DataStorageType.LINK,
                content_type=DataContentType.TEXT,
                location=str(url),
                metadata=link_metadata or None,
            )

            payload = DataStorageRequestPayload(
                name=name,
                content=str(url),
                description=description,
                dataset_id=dataset_id,
                project_id=project_id,
                existing_location=existing_location,
            )
            return self._create_data_storage_entry(payload)
        except HTTPStatusError as e:
            self._handle_http_errors(e, "creating")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def store_file_content(
        self,
        name: str,
        file_path: str | Path,
        description: str | None = None,
        path: str | None = None,
        as_collection: bool = False,
        manifest_filename: str | None = None,
        ignore_patterns: list[str] | None = None,
        ignore_filename: str = ".gitignore",
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Store file or directory content in the data storage system.

        For files: Small text files (< 10MB, supported formats) are sent as text content,
        larger/binary files are uploaded via signed URL.

        For directories: Zipped as a single file with ignore pattern support and uploaded
        as a collection.

        Args:
            name: Name of the data storage entry
            file_path: Path to file or directory to upload
            description: Optional description of the data storage entry
            path: Optional path for the data storage entry
            as_collection: If true, upload directories as a single zip file collection.
            manifest_filename: Name of manifest file
            ignore_patterns: List of patterns to ignore when zipping directories
            ignore_filename: Name of ignore file to read from directory (default: .gitignore)
            project_id: ID of the project this data storage entry belongs to

        Returns:
            DataStorageResponse containing the final data storage entry

        Raises:
            DataStorageCreationError: If there's an error in the process
        """
        file_path = self._validate_file_path(file_path)

        try:
            if file_path.is_dir() and as_collection:
                return self._upload_data_directory(
                    name,
                    file_path,
                    description,
                    path,
                    ignore_patterns,
                    ignore_filename,
                    project_id,
                )
            if file_path.is_dir() and not as_collection:
                responses = self._upload_directory_hierarchically(
                    name=name,
                    dir_path=file_path,
                    description=description,
                    manifest_filename=manifest_filename,
                    ignore_patterns=ignore_patterns,
                    ignore_filename=ignore_filename,
                    project_id=project_id,
                )
                if not responses:
                    raise DataStorageCreationError(
                        "No data storage entries were created"
                    )
                return responses[0]
            return self._upload_data_single_file(
                name, file_path, description, path, project_id
            )

        except HTTPStatusError as e:
            self._handle_http_errors(e, "creating")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred during file upload: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def astore_file_content(
        self,
        name: str,
        file_path: str | Path,
        description: str | None = None,
        path: str | None = None,
        as_collection: bool = False,
        manifest_filename: str | None = None,
        ignore_patterns: list[str] | None = None,
        ignore_filename: str = ".gitignore",
        dataset_id: UUID | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Asynchronously store file or directory content in the data storage system.

        Args:
            name: Name of the data storage entry.
            file_path: Path to the file or directory to upload.
            description: Optional description for the entry.
            path: Optional GCS path for the entry.
            as_collection: If uploading a directory, `True` zips it into a single collection,
                           `False` uploads it as a hierarchical structure of individual objects.
            manifest_filename: Optional manifest file for hierarchical uploads.
            ignore_patterns: List of patterns to ignore when zipping.
            ignore_filename: Name of ignore file to read (default: .gitignore).
            dataset_id: Optional dataset ID to add entry to, or None to create new dataset.
            project_id: ID of the project this data storage entry belongs to

        Returns:
            The `DataStorageResponse` for the created entry. For hierarchical uploads,
            this is the response for the root directory entry.
        """
        file_path = self._validate_file_path(file_path)

        try:
            if file_path.is_dir():
                if as_collection:
                    return await self._aupload_data_directory(
                        name,
                        file_path,
                        description,
                        path,
                        ignore_patterns,
                        ignore_filename,
                        project_id,
                    )
                responses = await self._aupload_directory_hierarchically(
                    name=name,
                    dir_path=file_path,
                    description=description,
                    manifest_filename=manifest_filename,
                    ignore_patterns=ignore_patterns,
                    ignore_filename=ignore_filename,
                    dataset_id=dataset_id,
                    project_id=project_id,
                )
                if not responses:
                    raise DataStorageCreationError(
                        "No data storage entries were created"
                    )
                return responses[0]
            return await self._aupload_data_single_file(
                name, file_path, description, path, dataset_id, project_id
            )

        except HTTPStatusError as e:
            self._handle_http_errors(e, "creating")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred during async file upload: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def register_existing_data_source(
        self,
        name: str,
        existing_location: DataStorageLocationPayload,
        description: str | None = None,
        as_collection: bool = False,
        path: str | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Store content as a string in the data storage system.

        Args:
            name: Name of the data storage entry
            existing_location: Describes the existing data source location to register
            description: Optional description of the data storage entry
            as_collection: If uploading a directory, `True` creates a single storage entry for
                the whole directory and multiple storage locations for each file, `False` assumes
                you are uploading a single file.
            path: Optional path for the data storage entry
            project_id: ID of the project this data storage entry belongs to

        Returns:
            DataStorageResponse containing the created data storage entry and storage locations

        Raises:
            DataStorageCreationError: If there's an error creating the data storage entry
        """
        try:
            payload = DataStorageRequestPayload(
                name=name,
                description=description,
                path=path,
                existing_location=existing_location,
                project_id=project_id,
                is_collection=as_collection,
            )
            response = self.client.post(
                "/v0.1/data-storage/data-entries",
                json=payload.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            return DataStorageResponse.model_validate(response.json())
        except HTTPStatusError as e:
            self._handle_http_errors(e, "creating")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def aregister_existing_data_source(
        self,
        name: str,
        existing_location: DataStorageLocationPayload,
        as_collection: bool = False,
        description: str | None = None,
        path: str | None = None,
        project_id: UUID | None = None,
    ) -> DataStorageResponse:
        """Store content as a string in the data storage system.

        Args:
            name: Name of the data storage entry
            existing_location: Describes the existing data source location to register
            description: Optional description of the data storage entry
            as_collection: If uploading a directory, `True` creates a single storage entry for
                the whole directory and multiple storage locations for each file, `False` assumes
                you are uploading a single file.
            path: Optional path for the data storage entry
            project_id: ID of the project this data storage entry belongs to

        Returns:
            DataStorageResponse containing the created data storage entry and storage locations

        Raises:
            DataStorageCreationError: If there's an error creating the data storage entry
        """
        try:
            payload = DataStorageRequestPayload(
                name=name,
                description=description,
                path=path,
                existing_location=existing_location,
                project_id=project_id,
                is_collection=as_collection,
            )
            response = await self.async_client.post(
                "/v0.1/data-storage/data-entries",
                json=payload.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            return DataStorageResponse.model_validate(response.json())
        except HTTPStatusError as e:
            self._handle_http_errors(e, "creating")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def search_data_storage(
        self,
        criteria: list[SearchCriterion] | None = None,
        size: int = 10,
    ) -> list[dict]:
        """Search data storage objects using structured criteria.

        Args:
            criteria: List of search criteria (SearchCriterion objects with field, operator, value)
            size: Number of results to return (1-100)

        Returns:
            List of search results with scores and data storage information

        Raises:
            DataStorageCreationError: If there's an error searching data storage entries

        Example:
            from futurehouse_client.models.rest import SearchCriterion, SearchOperator
            criteria = [
                SearchCriterion(field="name", operator=SearchOperator.CONTAINS, value="document"),
                SearchCriterion(field="project_id", operator=SearchOperator.EQUALS, value="my-project-id"),
                SearchCriterion(field="status", operator=SearchOperator.EQUALS, value="active"),
            ]
            results = client.search_data_storage(criteria=criteria, size=20)
        """
        try:
            payload = DataStorageSearchPayload(
                criteria=criteria or [],
                size=max(1, min(100, size)),  # Clamp between 1-100
            )

            response = self.client.post(
                "/v0.1/data-storage/search",
                json=payload.model_dump(mode="json"),
            )
            response.raise_for_status()
            return response.json()

        except HTTPStatusError as e:
            if e.response.status_code == codes.SERVICE_UNAVAILABLE:
                raise DataStorageCreationError(
                    "Search functionality is currently unavailable"
                ) from e
            self._handle_http_errors(e, "searching")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred during search: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def asearch_data_storage(
        self,
        criteria: list[SearchCriterion] | None = None,
        size: int = 10,
    ) -> list[dict]:
        """Asynchronously search data storage objects using structured criteria.

        Args:
            criteria: List of search criteria (SearchCriterion objects with field, operator, value)
            size: Number of results to return (1-100)

        Returns:
            List of search results with scores and data storage information

        Raises:
            DataStorageCreationError: If there's an error searching data storage entries

        Example:
            from futurehouse_client.models.rest import SearchCriterion, SearchOperator
            criteria = [
                SearchCriterion(field="name", operator=SearchOperator.CONTAINS, value="document"),
                SearchCriterion(field="project_id", operator=SearchOperator.EQUALS, value="my-project-id"),
                SearchCriterion(field="status", operator=SearchOperator.EQUALS, value="active"),
            ]
            results = await client.asearch_data_storage(criteria=criteria, size=20)
        """
        try:
            payload = DataStorageSearchPayload(
                criteria=criteria or [],
                size=max(1, min(100, size)),  # Clamp between 1-100
            )

            response = await self.async_client.post(
                "/v0.1/data-storage/search",
                json=payload.model_dump(mode="json"),
            )
            response.raise_for_status()
            return response.json()

        except HTTPStatusError as e:
            if e.response.status_code == codes.SERVICE_UNAVAILABLE:
                raise DataStorageCreationError(
                    "Search functionality is currently unavailable"
                ) from e
            self._handle_http_errors(e, "searching")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred during async search: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def similarity_search_data_storage(
        self,
        embedding: list[float],
        size: int = 10,
        min_score: float = 0.7,
        dataset_id: UUID | None = None,
        tags: list[str] | None = None,
        user_id: str | None = None,
        project_id: str | None = None,
    ) -> list[dict]:
        """Search data storage objects using vector similarity.

        Args:
            embedding: Embedding vector for similarity search
            size: Number of results to return (1-100)
            min_score: Minimum similarity score (0.0-1.0)
            dataset_id: Optional dataset ID filter
            tags: Optional list of tags to filter by
            user_id: Optional user ID filter (admin only)
            project_id: Optional project ID filter

        Returns:
            List of search results with similarity scores and data storage information

        Raises:
            DataStorageCreationError: If there's an error performing similarity search
        """
        try:
            # Validate inputs
            if not embedding:
                raise DataStorageCreationError("Embedding vector is required")

            if not all(isinstance(x, int | float) for x in embedding):
                raise DataStorageCreationError("Embedding must be a list of numbers")

            size = max(1, min(100, size))  # Clamp between 1-100
            min_score = max(0.0, min(1.0, min_score))  # Clamp between 0.0-1.0

            # Build request payload
            payload = {
                "embedding": embedding,
                "size": size,
                "min_score": min_score,
            }

            # Add optional filters
            if dataset_id is not None:
                payload["dataset_id"] = str(dataset_id)
            if tags is not None:
                payload["tags"] = tags
            if user_id is not None:
                payload["user_id"] = user_id
            if project_id is not None:
                payload["project_id"] = project_id

            response = self.client.post(
                "/v0.1/data-storage/similarity-search", json=payload
            )
            response.raise_for_status()
            return response.json()

        except HTTPStatusError as e:
            if e.response.status_code == codes.SERVICE_UNAVAILABLE:
                raise DataStorageCreationError(
                    "Similarity search functionality is currently unavailable"
                ) from e
            self._handle_http_errors(e, "performing similarity search")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred during similarity search: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def asimilarity_search_data_storage(
        self,
        embedding: list[float],
        size: int = 10,
        min_score: float = 0.7,
        dataset_id: UUID | None = None,
        tags: list[str] | None = None,
        user_id: str | None = None,
        project_id: str | None = None,
    ) -> list[dict]:
        """Asynchronously search data storage objects using vector similarity.

        Args:
            embedding: Embedding vector for similarity search
            size: Number of results to return (1-100)
            min_score: Minimum similarity score (0.0-1.0)
            dataset_id: Optional dataset ID filter
            tags: Optional list of tags to filter by
            user_id: Optional user ID filter (admin only)
            project_id: Optional project ID filter

        Returns:
            List of search results with similarity scores and data storage information

        Raises:
            DataStorageCreationError: If there's an error performing similarity search
        """
        try:
            # Validate inputs
            if not embedding:
                raise DataStorageCreationError("Embedding vector is required")

            if not all(isinstance(x, int | float) for x in embedding):
                raise DataStorageCreationError("Embedding must be a list of numbers")

            size = max(1, min(100, size))  # Clamp between 1-100
            min_score = max(0.0, min(1.0, min_score))  # Clamp between 0.0-1.0

            # Build request payload
            payload = {
                "embedding": embedding,
                "size": size,
                "min_score": min_score,
            }

            # Add optional filters
            if dataset_id is not None:
                payload["dataset_id"] = str(dataset_id)
            if tags is not None:
                payload["tags"] = tags
            if user_id is not None:
                payload["user_id"] = user_id
            if project_id is not None:
                payload["project_id"] = project_id

            response = await self.async_client.post(
                "/v0.1/data-storage/similarity-search", json=payload
            )
            response.raise_for_status()
            return response.json()

        except HTTPStatusError as e:
            if e.response.status_code == codes.SERVICE_UNAVAILABLE:
                raise DataStorageCreationError(
                    "Similarity search functionality is currently unavailable"
                ) from e
            self._handle_http_errors(e, "performing similarity search")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred during async similarity search: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def fetch_data_from_storage(
        self,
        data_storage_id: UUID | None = None,
    ) -> str | Path | list[Path] | None:
        """Fetch data from the storage system (sync version).

        Args:
            data_storage_id: ID of the data storage entry to fetch

        Returns:
            For PG_TABLE storage: string content
            For GCS storage: Path to downloaded file (may be unzipped if it was a zip)
            For multi-location entries: dict of location IDs to dicts with signed URL and file name
            None if not found or error occurred
        """
        if not data_storage_id:
            raise DataStorageRetrievalError(
                "data_storage_id must be provided at this time"
            )

        try:
            response = self.client.get(
                f"/v0.1/data-storage/data-entries/{data_storage_id}", timeout=100
            )
            response.raise_for_status()
            result = DataStorageResponse.model_validate(response.json())

            if len(result.storage_locations) > 1:
                return [
                    self._download_from_gcs(
                        location.storage_config.signed_url or "",
                        (location.storage_config.location or "").split("/")[-1],
                    )
                    for location in result.storage_locations
                ]

            # Most scenarios will only have one location
            storage_location = result.storage_locations[0]
            storage_type = storage_location.storage_config.storage_type

            if storage_type == "gcs":
                if not storage_location.storage_config.signed_url:
                    raise DataStorageRetrievalError(
                        "No signed URL available for GCS download"
                    )

                return self._download_from_gcs(
                    storage_location.storage_config.signed_url
                )

            if storage_type in {"raw_content", "pg_table"}:
                content = result.data_storage.content
                if content is None:
                    logger.warning(
                        f"No content found for data storage entry {data_storage_id}"
                    )
                    return None
                return content

            raise DataStorageRetrievalError(f"Unsupported storage type: {storage_type}")

        except HTTPStatusError as e:
            self._handle_http_errors(e, "retrieving")
        except Exception as e:
            raise DataStorageRetrievalError(
                f"An unexpected error occurred: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def afetch_data_from_storage(
        self,
        data_storage_id: UUID | None = None,
    ) -> str | Path | list[Path] | None:
        """Fetch data from the storage system.

        Args:
            data_storage_id: ID of the data storage entry to fetch

        Returns:
            For PG_TABLE storage: string content
            For GCS storage: Path to downloaded file (may be unzipped if it was a zip)
            For multi-location entries: dict of location IDs to dicts with signed URL and file name
            None if not found or error occurred
        """
        if not data_storage_id:
            raise DataStorageRetrievalError(
                "data_storage_id must be provided at this time"
            )

        try:
            response = await self.async_client.get(
                f"/v0.1/data-storage/data-entries/{data_storage_id}", timeout=100
            )
            response.raise_for_status()
            result = DataStorageResponse.model_validate(response.json())

            if len(result.storage_locations) > 1:
                return await gather_with_concurrency(
                    DOWNLOAD_CONCURRENCY,
                    [
                        self._adownload_from_gcs(
                            location.storage_config.signed_url or "",
                            (location.storage_config.location or "").split("/")[-1],
                        )
                        for location in result.storage_locations
                    ],
                )

            # Most scenarios will only have one location
            storage_location = result.storage_locations[0]
            storage_type = storage_location.storage_config.storage_type

            if storage_type == "gcs":
                if not storage_location.storage_config.signed_url:
                    raise DataStorageRetrievalError(
                        "No signed URL available for GCS download"
                    )

                return await self._adownload_from_gcs(
                    storage_location.storage_config.signed_url
                )

            if storage_type in {"raw_content", "pg_table"}:
                content = result.data_storage.content
                if content is None:
                    logger.warning(
                        f"No content found for data storage entry {data_storage_id}"
                    )
                    return None
                return content

            raise DataStorageRetrievalError(f"Unsupported storage type: {storage_type}")

        except HTTPStatusError as e:
            self._handle_http_errors(e, "retrieving")
        except Exception as e:
            raise DataStorageRetrievalError(
                f"An unexpected error occurred: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def acreate_dataset(
        self,
        name: str,
        description: str | None = None,
        dataset_id: UUID | None = None,
    ):
        try:
            payload = CreateDatasetPayload(
                name=name,
                description=description,
                id=dataset_id,
            )
            response = await self.async_client.post(
                "/v0.1/data-storage/datasets",
                json=payload.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            return CreateDatasetPayload.model_validate(response.json())
        except HTTPStatusError as e:
            self._handle_http_errors(e, "creating")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def create_dataset(
        self,
        name: str,
        description: str | None = None,
        dataset_id: UUID | None = None,
    ):
        try:
            payload = CreateDatasetPayload(
                name=name,
                description=description,
                id=dataset_id,
            )
            response = self.client.post(
                "/v0.1/data-storage/datasets",
                json=payload.model_dump(exclude_none=True),
            )
            response.raise_for_status()
            return CreateDatasetPayload.model_validate(response.json())
        except HTTPStatusError as e:
            self._handle_http_errors(e, "creating")
        except Exception as e:
            raise DataStorageCreationError(
                f"An unexpected error occurred: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def adelete_dataset(self, dataset_id: UUID):
        """Delete a dataset.

        Note: This will delete all data storage entries associated with the dataset.

        Args:
            dataset_id: ID of the dataset to delete

        Raises:
            DataStorageError: If there's an error deleting the dataset
        """
        try:
            await self.async_client.delete(f"/v0.1/data-storage/datasets/{dataset_id}")
        except HTTPStatusError as e:
            self._handle_http_errors(e, "deleting")
        except Exception as e:
            raise DataStorageError(f"An unexpected error occurred: {e!r}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def delete_dataset(self, dataset_id: UUID):
        """Delete a dataset.

        Note: This will delete all data storage entries associated with the dataset.

        Args:
            dataset_id: ID of the dataset to delete

        Raises:
            DataStorageError: If there's an error deleting the dataset
        """
        try:
            self.client.delete(f"/v0.1/data-storage/datasets/{dataset_id}")
        except HTTPStatusError as e:
            self._handle_http_errors(e, "deleting")
        except Exception as e:
            raise DataStorageError(f"An unexpected error occurred: {e!r}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def aget_dataset(self, dataset_id: UUID):
        try:
            response = await self.async_client.get(
                f"/v0.1/data-storage/datasets/{dataset_id}"
            )
            response.raise_for_status()

            return response.json()
        except HTTPStatusError as e:
            self._handle_http_errors(e, "retrieving")
        except Exception as e:
            raise DataStorageError(f"An unexpected error occurred: {e!r}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def get_dataset(self, dataset_id: UUID):
        try:
            response = self.client.get(f"/v0.1/data-storage/datasets/{dataset_id}")
            response.raise_for_status()

            return response.json()
        except HTTPStatusError as e:
            self._handle_http_errors(e, "retrieving")
        except Exception as e:
            raise DataStorageError(f"An unexpected error occurred: {e!r}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def get_data_storage_entry(self, data_storage_id: UUID) -> DataStorageResponse:
        """Get a data storage entry with all details including storage locations and metadata.

        Args:
            data_storage_id: ID of the data storage entry to retrieve

        Returns:
            DataStorageResponse with entry details and storage locations

        Raises:
            DataStorageRetrievalError: If there's an error retrieving the entry
        """
        try:
            response = self.client.get(
                f"/v0.1/data-storage/data-entries/{data_storage_id}", timeout=100
            )
            response.raise_for_status()
            return DataStorageResponse.model_validate(response.json())
        except HTTPStatusError as e:
            self._handle_http_errors(e, "retrieving")
        except Exception as e:
            raise DataStorageRetrievalError(
                f"An unexpected error occurred: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def aget_data_storage_entry(
        self, data_storage_id: UUID
    ) -> DataStorageResponse:
        """Get a data storage entry with all details including storage locations and metadata.

        Args:
            data_storage_id: ID of the data storage entry to retrieve

        Returns:
            DataStorageResponse with entry details and storage locations

        Raises:
            DataStorageRetrievalError: If there's an error retrieving the entry
        """
        try:
            response = await self.async_client.get(
                f"/v0.1/data-storage/data-entries/{data_storage_id}", timeout=100
            )
            response.raise_for_status()
            return DataStorageResponse.model_validate(response.json())
        except HTTPStatusError as e:
            self._handle_http_errors(e, "retrieving")
        except Exception as e:
            raise DataStorageRetrievalError(
                f"An unexpected error occurred: {e!r}"
            ) from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    async def adelete_data_storage_entry(self, data_storage_entry_id: UUID):
        try:
            await self.async_client.delete(
                f"/v0.1/data-storage/data-entries/{data_storage_entry_id}"
            )
        except HTTPStatusError as e:
            self._handle_http_errors(e, "deleting")
        except Exception as e:
            raise DataStorageError(f"An unexpected error occurred: {e!r}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_connection_error,
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )
    def delete_data_storage_entry(self, data_storage_entry_id: UUID):
        try:
            self.client.delete(
                f"/v0.1/data-storage/data-entries/{data_storage_entry_id}"
            )
        except HTTPStatusError as e:
            self._handle_http_errors(e, "deleting")
        except Exception as e:
            raise DataStorageError(f"An unexpected error occurred: {e!r}") from e
