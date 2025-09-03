# Geodata Pixel Client

A Python client library for interacting with the Geodata Pixel API. Geodata Pixel is a SaaS solution for efficient image management, providing a centralized platform for uploading, storing, and structuring image data with geospatial information. This makes it easy to find and manage images based on time and location.

This client library provides a convenient interface for working with Geodata Pixel, allowing users to create projects, manage data collections, and upload and process various types of geospatial imagery including survey photos, drone imagery, 360° images, and raster data.

> Geodata Pixel er vår løsning for effektiv bildeforvaltning. Med Geodata Pixel får du et felles sted å laste opp, lagre og strukturere bildedata, noe som gjør det enkelt å finne bilder basert på tid og sted.

## Features

- **Dual API Support**: Both synchronous and asynchronous interfaces
- **Data Management**: Create and manage projects and data collections
- **Image Handling**: Upload and process image data with geolocation
- **Raster Data Handling**: Support for various raster data types (RGB, DTM, DSM)
- **ArcGIS Services**: Create and manage ArcGIS Feature and Image services
- **Harvest Services**: Automated data harvesting from ArcGIS Feature services
- **Authentication**: Integrated Keycloak authentication
- **Metadata Management**: Flexible metadata handling for uploaded files
- **Attachments**: Add and manage file attachments to resources

## Installation

> **Warning**
> This package is not yet available on PyPI. You can install it from the source code repository instead.

```bash
pip install pixel-client
```

## Requirements

- Python 3.11 or higher

## Authentication

The Pixel client requires authentication through Keycloak. You can provide authentication details through environment variables, a `.env` file, or directly in code:

```python
from pixel_client import get_client, PixelApiSettings

# Using environment variables
client = get_client()

# Using direct settings
settings = PixelApiSettings(
    PIXEL_API_URL="your_api_url",
    KEYCLOAK_SERVER_URL="your_keycloak_server_url",
    KEYCLOAK_CLIENT_ID="your_client_id",
    KEYCLOAK_REALM="your_realm",
    KEYCLOAK_USERNAME="your_username",
    KEYCLOAK_PASSWORD="your_password"
)
client = get_client(settings=settings)

# Using a .env file
settings = PixelApiSettings.from_env_file("my_env_file.env")
client = get_client(settings=settings)
```

## Quick Start

### Synchronous Usage

```python
from pixel_client import get_client
from geojson_pydantic import Polygon

# Initialize the client
client = get_client()

# Create a project
new_project = client.create_project(
    name="My New Project",
    description="A test project",
    area_of_interest=Polygon.model_validate({
        "type": "Polygon",
        "coordinates": [[[-10, 10], [-10, 20], [0, 20], [0, 10], [-10, 10]]]
    }),
    tags=["test", "example"]
)

# Create a data collection
data_collection = client.create_data_collection(
    project_id=new_project["id"],
    name="My Data Collection",
    description="An example data collection",
    data_collection_type="image",
    tags=["example", "images"]
)
```

### Asynchronous Usage

```python
import asyncio
from pixel_client import get_client
from geojson_pydantic import Polygon

async def main():
    # Initialize the async client
    client = get_client(async_=True)
    
    # Create a project
    new_project = await client.create_project(
        name="My Async Project",
        description="A test async project",
        area_of_interest=Polygon.model_validate({
            "type": "Polygon",
            "coordinates": [[[-10, 10], [-10, 20], [0, 20], [0, 10], [-10, 10]]]
        }),
        tags=["test", "async"]
    )
    
    # Create a data collection
    data_collection = await client.create_data_collection(
        project_id=new_project["id"],
        name="My Async Data Collection",
        description="An example async data collection",
        data_collection_type="image",
        tags=["example", "async"]
    )

asyncio.run(main())
```

## Uploading Data

### Image Data

```python
from pixel_client import get_client, PixelUploadFile, MetadataObject, ImageMetadataFields
from pathlib import Path

client = get_client()

# Upload images to a data collection
image_files = [
    PixelUploadFile(
        file=Path("path/to/image.jpg"),
        metadata=MetadataObject(
            fields=ImageMetadataFields(name="my_image"),
            json_metadata={"custom_field": "value"}
        )
    )
]

images, errors = client.upload_multiple_images(
    project_id=project_id,
    data_collection_id=data_collection_id,
    files=image_files
)
```

### Raster Data

The client supports various raster data types:
- `raster`: Generic raster data
- `RGB`: RGB raster data (3 or 4 bands, uint8)
- `DTM`: Digital Terrain Model data (single band, float32/float64)
- `DSM`: Digital Surface Model data (single band, float32/float64)

## Project Structure

The project is organized as follows:

- `src/`: Source code for the Pixel client library
    - `pixel_client/`: Core client library code
        - `__init__.py`: Main entry point and exports
        - `_base.py`: Asynchronous client implementation
        - `_sync.py`: Synchronous client wrapper
        - `auth.py`: Authentication handling
        - `models.py`: Data models
        - `settings.py`: Configuration settings
        - `exceptions.py`: Custom exceptions
        - `types.py`: Type definitions
        - `utils.py`: Utility functions
- `docs/`: Documentation
  - `usage/`: User guides and tutorials
  - `api/`: API reference documentation
  - `assets/`: Static assets for documentation
  - `code_snippets/`: Example code snippets
- `integration_tests/`: 
  - `data`: Sample data for integration tests
  - `__init__.py`: Initialization for integration tests
  - `conftest.py`: Configuration for pytest
  - `constants.py`: Constants used in tests
  - `test_smoke.py`: Smoketest for client functionality

## Documentation

This project uses MkDocs with the Material theme for documentation. The documentation includes:

- [Installation](docs/usage/installation.md): How to install the library
- [Getting Started](docs/usage/getting-started.md): Getting started with the library
- [Examples](docs/usage/examples.md): Code examples for common tasks
- [API Reference](docs/api/client.md): Detailed API documentation

To build the documentation locally:

```bash
# Install dependencies with uv
uv sync --group docs --group dev

# Build and serve the documentation
uv run mkdocs serve
```

## Development

### Setting Up Development Environment

Requires [uv package manager](https://docs.astral.sh/uv/).
To set up a development environment:

```bash
# Clone the repository
git clone "https://geonett@dev.azure.com/geonett/Geodata%20Pixel%20-%20Geodata%20Pixel/_git/pixel-client"
cd pixel-client

# Install development dependencies
uv sync --group dev

# Install documentation dependencies
uv sync --group docs --group dev
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. To set up pre-commit:

```bash
pre-commit install
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

When contributing, please:

1. Follow the existing code style
2. Add tests for new functionality
3. Update documentation as needed
4. Run pre-commit hooks before submitting changes

## License
See [LICENSE](LICENSE.txt) for details.
