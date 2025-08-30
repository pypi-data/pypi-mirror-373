# Data Storage Methods

The FutureHouse client provides comprehensive data storage capabilities for managing
different types of data in the platform. This document covers the available methods,
data types, and usage patterns.

## Overview

The data storage system supports multiple storage types and content types:

- **Storage Types**: GCS (Google Cloud Storage), PG_TABLE (PostgreSQL), BIGQUERY, RAW_CONTENT, ELASTIC_SEARCH
- **Content Types**: TEXT, FILE, DIRECTORY, BQ_DATASET, BQ_TABLE, INDEX
- **Upload Modes**: Text content, file upload, directory collection, hierarchical structure
- **CRUD Operations**: Create, read, update, and delete datasets and data storage entries

## Core Methods

### 1. Text Content Storage

#### `store_text_content()` / `astore_text_content()`

Store raw text content directly in the database (PG_TABLE storage).

```python
# Synchronous
response = client.store_text_content(
    name="my_text_data",
    content="This is the text content to store",
    description="Sample text data for analysis",
    project_id=project_uuid,
)

# Asynchronous
response = await client.astore_text_content(
    name="my_text_data",
    content="This is the text content to store",
    description="Sample text data for analysis",
    dataset_id=dataset_uuid,
    project_id=project_uuid,
)
```

**Use Cases**: Small text data, configuration files, metadata, JSON strings

**Storage**: PostgreSQL table with direct content storage

**Limitations**: Content is limited by database field size

### 2. File Content Storage

#### `store_file_content()` / `astore_file_content()`

Automatically handles different file types and sizes with intelligent storage decisions.

```python
# Synchronous
response = client.store_file_content(
    name="my_file",
    file_path="/path/to/file.txt",
    description="Sample file upload",
    project_id=project_uuid,
)

# Asynchronous
response = await client.astore_file_content(
    name="my_file",
    file_path="/path/to/file.txt",
    description="Sample file upload",
    dataset_id=dataset_uuid,
    project_id=project_uuid,
)
```

#### File Type Handling

**Small Text Files (< 10MB)**

- **Supported formats**: `.txt`, `.md`, `.csv`, `.json`, `.yaml`, `.yml`
- **Storage**: Automatically converted to text content and stored in PostgreSQL
- **Benefits**: Fast retrieval, searchable, no download required

**Large/Binary Files (≥ 10MB)**

- **Storage**: Uploaded to Google Cloud Storage (GCS) via signed URLs
- **Process**:
  1. Creates data storage entry with PENDING status
  2. Returns signed URL for upload
  3. Uploads file to GCS
  4. Updates status to ACTIVE
- **Benefits**: Handles any file type, scalable storage

### 3. Directory Storage

#### Collection Mode (`as_collection=True`)

Uploads entire directory as a single zip file collection.

```python
response = client.store_file_content(
    name="my_project",
    file_path="/path/to/project_directory",
    description="Complete project files",
    as_collection=True,
    ignore_patterns=[".git", "node_modules", "*.pyc"],
    ignore_filename=".gitignore",
    project_id=project_uuid,
)
```

**Features**:

- Automatically zips directory contents
- Supports `.gitignore` patterns and custom ignore patterns
- Single data storage entry for entire directory
- Efficient for large directory uploads

#### Hierarchical Mode (`as_collection=False`)

Creates individual data storage entries for each file and subdirectory.

```python
response = client.store_file_content(
    name="my_project",
    file_path="/path/to/project_directory",
    description="Project with individual file tracking",
    as_collection=False,
    manifest_filename="manifest.json",
    project_id=project_uuid,
)
```

**Features**:

- Individual entries for each file and subdirectory
- Maintains directory structure
- Supports manifest files for metadata
- Better for file-level operations and tracking

### 4. Existing Data Source Registration

#### `register_existing_data_source()` / `aregister_existing_data_source()`

Register data that already exists in external systems without uploading.

```python
# Register GCS bucket
gcs_location = DataStorageLocationPayload(
    storage_type=DataStorageType.GCS,
    content_type=DataContentType.DIRECTORY,
    metadata={"bucket_name": "my-bucket", "prefix": "data/raw/"},
)

response = client.register_existing_data_source(
    name="existing_gcs_data",
    existing_location=gcs_location,
    description="Pre-existing GCS data",
    project_id=project_uuid,
)

# Register GCS collection (multiple files as a single entry)
gcs_collection_location = DataStorageLocationPayload(
    storage_type=DataStorageType.GCS,
    content_type=DataContentType.DIRECTORY,
    metadata={"bucket_name": "my-bucket", "prefix": "data/processed/"},
)

response = client.register_existing_data_source(
    name="gcs_data_collection",
    existing_location=gcs_collection_location,
    description="Collection of processed data files in GCS",
    project_id=project_uuid,
)

# Register Postgres entry
postgres_location = DataStorageLocationPayload(
    storage_type=DataStorageType.PG_TABLE,
    content_type=DataContentType.TEXT,
    metadata={
        "table_name": "trajectories",
        "row_id": "66cee0ed-fb4d-4390-ab81-d9640839aacb",
    },
)

response = client.register_existing_data_source(
    name="finch trajectory",
    existing_location=postgres_location,
    description="Finch trajectory from science2",
    project_id=project_uuid,
)
```

**Supported External Sources**:

- **GCS**: Buckets and prefixes
- **PostgreSQL**: Existing table rows
- **BigQuery**: Tables and datasets _(Not fully supported at the moment)_

**Metadata Validation**

For each registration basic validation is run on the payload to ensure
valid metadata has been passed and can be accessed by the
[backend](https://github.com/Future-House/crow-ecosystem/tree/dev/packages/crow-service).

**GCS Collection Behavior**

When registering GCS data sources, the system automatically handles collections:

- **Single File**: If the prefix points to a specific file, only that file is registered
- **Directory Collection**: If the prefix points to a directory, all files under that prefix are treated as a collection
- **Automatic Discovery**: The backend validates the GCS location by listing objects under the specified prefix
- **Collection Flag**: The `is_collection` field is automatically set to `True` when multiple files are
  found under the prefix

This allows you to register existing GCS directories as data collections without needing to manually specify
each individual file. When doing this, all files and sub dirs are registered under a single storage entry with
multiple locations mapping to the files in the dir.

```python
# GCS
metadata = {
    "bucket_name": "example_bucket",  # REQUIRED
    "prefix": "path/to/dir",  # OPTIONAL - if omitted, entire bucket is registered
}

# Postgres
metadata = {
    "table_name": "trajectories",  # REQUIRED
    "row_id": "cb4b822a-6022-4dca-a305-523f52330a70",  # REQUIRED
}

# Bigquery
metadata = {
    "project_id": "bigquery-public-data",  # REQUIRED
    "dataset_id": "samples",  # REQUIRED
    "table_id": "shakespeare",  # REQUIRED
}
```

_Note: at present only the trajectories table is supported but more can be added easily._

### 5. Data Retrieval

#### `fetch_data_from_storage()` / `afetch_data_from_storage()`

Retrieve stored data based on storage type.

```python
# Synchronous
data = client.fetch_data_from_storage(data_storage_id=entry_uuid)

# Asynchronous
data = await client.afetch_data_from_storage(data_storage_id=entry_uuid)
```

**Return Types**:

- **PG_TABLE/RAW_CONTENT**: String content
- **GCS**: Path to downloaded file (automatically unzipped if zip file)
- **BIGQUERY**: Metadata and connection info

### 6. Dataset Management

**Note**: All dataset management methods are asynchronous and must be called with `await`.

#### `acreate_dataset()`

Create a new dataset to organize related data storage entries.

```python
# Create dataset with minimal required fields
response = await client.acreate_dataset(
    user_id="user_123",
    name="ml_experiments",
)

# Create dataset with description
response = await client.acreate_dataset(
    user_id="user_123",
    name="ml_experiments",
    description="Machine learning experiment results and models",
)

# Create dataset with custom ID
custom_dataset_id = uuid4()
response = await client.acreate_dataset(
    user_id="user_123",
    name="ml_experiments",
    description="Machine learning experiment results and models",
    dataset_id=custom_dataset_id,
)
```

**Parameters**:

- `user_id` (str): ID of the user creating the dataset
- `name` (str): Name of the dataset
- `description` (str, optional): Description of the dataset
- `dataset_id` (UUID, optional): Custom UUID for the dataset (if not provided, one will be generated)

**Returns**: `CreateDatasetPayload` object with dataset information

**Use Cases**: Organizing related data storage entries, grouping experiments, project organization

#### `aget_dataset()`

Retrieve information about a specific dataset and its associated data storage entries.

```python
dataset_info = await client.aget_dataset(dataset_id=dataset_uuid)
```

**Parameters**:

- `dataset_id` (UUID): ID of the dataset to retrieve

**Returns**: Dictionary containing dataset information and linked data storage entries:

- **Dataset Metadata**: id, name, description, user_id, created_at, modified_at
- **Linked Data Storage Entries**: Array of data storage entry objects with
  their metadata (id, name, description, storage_type, content_type, etc.)

**Example Response Structure**:

```python
{
    "id": "dataset-uuid-123",
    "name": "ML Experiments 2024",
    "description": "Machine learning experiments and results",
    "user_id": "user_123",
    "created_at": "2024-01-01T00:00:00Z",
    "modified_at": "2024-01-01T00:00:00Z",
    "data_storage_entries": [
        {
            "id": "entry-uuid-1",
            "name": "training_data.csv",
            "description": "Training dataset",
            "storage_type": "gcs",
            "content_type": "file",
            "created_at": "2024-01-01T00:00:00Z",
        },
        {
            "id": "entry-uuid-2",
            "name": "model.pkl",
            "description": "Trained model",
            "storage_type": "gcs",
            "content_type": "file",
            "created_at": "2024-01-01T00:00:00Z",
        },
    ],
}
```

**Use Cases**: Getting dataset metadata, verifying dataset existence, displaying
dataset information, listing all files in a dataset, dataset inventory management

#### `adelete_dataset()`

Delete a dataset and all its associated data storage entries.

```python
await client.adelete_dataset(dataset_id=dataset_uuid)
```

**Parameters**:

- `dataset_id` (UUID): ID of the dataset to delete

**Returns**: None (raises exception on error)

**Use Cases**: Cleaning up old experiments, removing unused datasets, data lifecycle management

**Note**: This operation will also delete all data storage entries associated with the dataset.

### 7. Data Storage Entry Management

#### `adelete_data_storage_entry()`

Delete a specific data storage entry.

```python
await client.adelete_data_storage_entry(data_storage_entry_id=entry_uuid)
```

**Parameters**:

- `data_storage_entry_id` (UUID): ID of the data storage entry to delete

**Returns**: None (raises exception on error)

**Use Cases**: Removing individual files, cleaning up temporary data, data lifecycle management

### Dataset and Data Storage Entry Relationship

Datasets provide a way to organize and group related data storage entries:

- **One-to-Many**: A dataset can contain multiple data storage entries
- **Organization**: Use datasets to group related files, experiments, or projects
- **Lifecycle**: Datasets can be deleted to clean up entire groups of data
- **Metadata**: Datasets store metadata (name, description) separate from individual file metadata
- **Retrieval**: Use `aget_dataset()` to get both dataset metadata and all linked data storage entries in a single call

**Example Structure**:

```text
Dataset: "ML Experiments 2024"
├── Data Storage Entry: "training_data.csv"
├── Data Storage Entry: "model.pkl"
├── Data Storage Entry: "evaluation_results.json"
└── Data Storage Entry: "config.yaml"
```

### 8. Search _(tbc)_

## Data Type-Specific Behavior

### Text Data

- **Storage**: Raw content
- **Retrieval**: Direct string content
- **Best for**: Small text files, JSON data, configuration
- **Limitations**: Size constraints, no binary support

### (Larger) File Data

- **Storage**: Google Cloud Storage
- **Retrieval**: Download via signed URLs
- **Best for**: Large files, binary data, any file type
- **Features**: Automatic chunked uploads, progress bars, resume capability

### Directory Data

- **Collection Mode**: Single zip file in GCS
- **Hierarchical Mode**: Individual entries with parent-child relationships
- **Best for**: Project uploads, dataset collections, organized file structures

### External Data (Postgres & GCS)

- **Storage**: Metadata only (data remains in source system)
- **Retrieval**:
  - **Postgres**: Linked data is returned as a raw string
  - **GCS**: Files are downloaded to your file system in a temp directory
- **Collection Support**: GCS automatically detects and handles collections when registering directories
- **Best for**: Existing data sources, data lakes, external databases

### External Data (Bigquery)

- **Storage**: Metadata only (data remains in source system)
- **Retrieval**: Connection information and metadata
- **Best for**: Existing data sources, data lakes, external databases

## Advanced Features

### Manifest Files

Support for JSON/YAML manifest files to provide metadata for directory uploads.

```json
{
  "project_files": {
    "description": "Main project directory",
    "entries": {
      "src/": {
        "description": "Source code directory",
        "entries": {
          "main.py": "Main application entry point",
          "utils.py": "Utility functions"
        }
      },
      "data/": {
        "description": "Data files directory",
        "entries": {
          "config.json": "Configuration file",
          "sample.csv": "Sample dataset"
        }
      }
    }
  }
}
```

### Ignore Patterns

Gitignore-style pattern matching for excluding files during uploads.

```python
# Custom ignore patterns
ignore_patterns = ["*.log", "temp/*", "__pycache__", ".env"]

response = client.store_file_content(
    name="project",
    file_path="/path/to/project",
    as_collection=True,
    ignore_patterns=ignore_patterns,
)
```

### Progress Tracking

Automatic progress bars for file uploads with resumable upload support.

```python
# Progress bars are automatically displayed
response = client.store_file_content(
    name="large_file",
    file_path="/path/to/large_file.zip",
    description="Large file upload with progress tracking",
)
```

## Error Handling

All methods include comprehensive error handling with retry logic:

- **HTTP Errors**: Automatic retry with exponential backoff
- **Connection Errors**: Retry on network issues
- **Validation Errors**: Clear error messages for invalid inputs
- **Storage Errors**: Detailed error information for storage failures

### CRUD Method Error Handling

The new CRUD methods (`acreate_dataset`, `aget_dataset`, `adelete_dataset`,
`adelete_data_storage_entry`) include specific error handling:

- **403 Forbidden**: User not authorized to perform the operation
- **404 Not Found**: Dataset or data storage entry doesn't exist
- **422 Unprocessable Entity**: Invalid request payload (e.g., empty name, invalid user_id)
- **Unexpected Errors**: Generic error handling for unexpected issues

All CRUD methods use the `@retry` decorator with exponential backoff for network resilience.

## Best Practices

### 1. Choose the Right Method

- **Text content**: Use `store_text_content()` for small text data
- **Single files**: Use `store_file_content()` for individual files
- **Directories**: Use `as_collection=True` for simple uploads, `False` for detailed tracking
- **External data**: Use `register_existing_data_source()` for existing systems

### 2. File Size Considerations

- **< 10MB**: Automatically stored as text content (faster retrieval)
- **≥ 10MB**: Stored in GCS (scalable, handles any file type)

### 3. Directory Organization

- **Simple collections**: Use collection mode for quick uploads
- **Complex structures**: Use hierarchical mode with manifest files
- **Ignore patterns**: Leverage `.gitignore` and custom patterns

### 4. Metadata Management

- **Descriptions**: Provide meaningful descriptions for better organization
- **Manifests**: Use manifest files for complex directory structures
- **Tags**: Leverage tagging for categorization and search

### 5. Dataset Organization

- **Naming Convention**: Use consistent naming patterns for datasets (e.g., `project_experiment_date`)
- **Descriptions**: Always provide meaningful descriptions for datasets
- **Lifecycle Management**: Regularly clean up unused datasets and data storage entries
- **Hierarchy**: Use datasets to group related data storage entries logically

## Examples

**Note**: For the dataset management examples, you'll need to import the required models:

```python
from futurehouse_client.models.data_storage_methods import CreateDatasetPayload
from uuid import uuid4
```

### Complete Project Upload

```python
# Upload entire project with manifest and ignore patterns
response = client.store_file_content(
    name="ml_project_v1",
    file_path="/path/to/ml_project",
    description="Machine learning project with models and data",
    as_collection=False,
    manifest_filename="project_manifest.json",
    ignore_patterns=["*.pyc", "__pycache__", ".git", "venv/"],
    project_id=project_uuid,
)
```

### Dataset Management Workflow

```python
# 1. Create a dataset for organizing ML experiments
dataset = await client.acreate_dataset(
    user_id="user_123",
    name="ml_experiments_2024",
    description="Machine learning experiments and results from 2024",
)

# 2. Store data files associated with the dataset
training_data = await client.astore_file_content(
    name="training_dataset",
    file_path="/path/to/training_data.csv",
    description="Training dataset for model experiments",
    dataset_id=dataset.id,
)

model_file = await client.astore_file_content(
    name="trained_model",
    file_path="/path/to/model.pkl",
    description="Trained machine learning model",
    dataset_id=dataset.id,
)

# 3. Retrieve dataset information and list all associated files
dataset_info = await client.aget_dataset(dataset_id=dataset.id)
print(f"Dataset: {dataset_info['name']}")
print(f"Description: {dataset_info['description']}")
print(f"Created: {dataset_info['created_at']}")

# List all data storage entries in the dataset
print(f"\nFiles in dataset '{dataset_info['name']}':")
for entry in dataset_info.get("data_storage_entries", []):
    print(f"  - {entry['name']}: {entry['description']} ({entry['storage_type']})")
    print(f"    ID: {entry['id']}, Created: {entry['created_at']}")

# Access specific entry information
if dataset_info.get("data_storage_entries"):
    first_entry = dataset_info["data_storage_entries"][0]
    print(f"\nFirst file: {first_entry['name']} ({first_entry['content_type']})")

# 4. Clean up when experiments are complete
await client.adelete_data_storage_entry(
    data_storage_entry_id=training_data.data_storage.id
)
await client.adelete_dataset(dataset_id=dataset.id)
```

### Working with Linked Data Storage Entries

```python
# Get dataset with all linked entries
dataset_info = await client.aget_dataset(dataset_id=dataset_uuid)

# Check if dataset has any entries
if dataset_info.get("data_storage_entries"):
    print(f"Dataset contains {len(dataset_info['data_storage_entries'])} files:")

    # Group entries by storage type
    storage_types = {}
    for entry in dataset_info["data_storage_entries"]:
        storage_type = entry["storage_type"]
        if storage_type not in storage_types:
            storage_types[storage_type] = []
        storage_types[storage_type].append(entry)

    # Display summary by storage type
    for storage_type, entries in storage_types.items():
        print(f"\n{storage_type.upper()} files ({len(entries)}):")
        for entry in entries:
            print(f"  - {entry['name']}: {entry['description']}")

    # Find specific file types
    csv_files = [
        e for e in dataset_info["data_storage_entries"] if e["name"].endswith(".csv")
    ]
    print(f"\nCSV files found: {len(csv_files)}")

else:
    print("Dataset is empty - no data storage entries found")
```

### Text Data Storage

```python
# Store configuration data
config_data = {
    "model_type": "transformer",
    "epochs": 100,
    "batch_size": 32,
    "learning_rate": 0.001,
}

response = client.store_text_content(
    name="training_config",
    content=json.dumps(config_data, indent=2),
    description="Training configuration for transformer model",
    project_id=project_uuid,
)
```

### Large File Upload

```python
# Upload large dataset file
response = client.store_file_content(
    name="training_dataset",
    file_path="/path/to/large_dataset.csv",
    description="Training dataset with 1M+ samples",
    project_id=project_uuid,
)

# The method automatically:
# 1. Creates entry with PENDING status
# 2. Returns signed URL for upload
# 3. Uploads file with progress bar
# 4. Updates status to ACTIVE
```
