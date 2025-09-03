import asyncio
import json
import logging
from functools import partial
from pathlib import Path
from typing import Any, AsyncGenerator, Literal, TypeVar, Self, TypedDict, Unpack
from uuid import uuid4

import httpx
from geojson_pydantic import Polygon
from tqdm import tqdm

from .auth import KeyCloakAuth
from .exceptions import (
    PixelBadRequestError,
    PixelMultipleUploadJobError,
    PixelUploadJobError,
)
from .models import (
    ArcgisServiceCreateInput,
    ArcgisServiceUpdateInput,
    DataCollectionListParams,
    HarvestServiceCreateInput,
    HarvestTaskListParams,
    ListParams,
    NearblackOptions,
    OIDCUserCreateInput,
    OIDCUserUpdateInput,
    PixelAttachmentUpload,
    PixelUploadFile,
    RasterInfo,
    ImageUpdateInput,
    HarvestServiceUpdateInput,
    RasterUpdateInput,
)
from .settings import PixelApiSettings
from .types import AttachmentResourceType, DataCollectionType, OverviewResampling
from .utils import (
    calculate_md5_base64_from_file,
    chunks,
    iter_file_parts,
    silence_logger,
)


logger = logging.getLogger(__name__)


T = TypeVar("T")

DEFAULT_PIXEL_TIMEOUT = httpx.Timeout(
    10.0,
    write=15.0,
)
DEFAULT_UPLOAD_TIMEOUT = httpx.Timeout(
    10.0,
    write=300.0,  # Increased write timeout for uploads
)


class PixelClientKwargs(TypedDict, total=False):
    """TypedDict for PixelClient constructor arguments."""

    timeout_pixel: httpx.Timeout
    """Timeout configuration for Pixel API requests. Defaults to DEFAULT_PIXEL_TIMEOUT."""

    timeout_upload: httpx.Timeout
    """Timeout configuration for file uploads. Defaults to DEFAULT_UPLOAD_TIMEOUT"""


class PixelClientAsync:
    """Asynchronous client for interacting with the Pixel API.

    This client provides methods for working with projects, data collections, images,
    rasters, and other resources in the Pixel system. It handles authentication,
    request management, and provides high-level operations for common tasks.
    """

    def __init__(
        self,
        url: str,
        keycloak_server_url: str,
        realm: str,
        client_id: str,
        username: str,
        password: str,
        timeout_pixel: httpx.Timeout = DEFAULT_PIXEL_TIMEOUT,
        timeout_upload: httpx.Timeout = DEFAULT_UPLOAD_TIMEOUT,
    ):
        """Initialize a new Pixel API client.

        Args:
            url: Base URL of the Pixel API.
            keycloak_server_url: URL of the Keycloak authentication server.
            realm: Keycloak realm name.
            client_id: Keycloak client ID.
            username: Username for authentication.
            password: Password for authentication.
            timeout_pixel: Optional timeout configuration for Pixel API requests.
            timeout_upload: Optional timeout configuration for file uploads. If not provided, defaults to the same as `timeout_pixel`.
        """
        self.url: str = url
        self._timeout_pixel = timeout_pixel
        self._timeout_upload = timeout_upload
        self.auth = KeyCloakAuth(
            keycloak_server_url, realm, client_id, username, password
        )
        self.pixel_client = httpx.AsyncClient(
            base_url=self.url, auth=self.auth, timeout=self._timeout_pixel
        )
        self._internal_client = httpx.AsyncClient(
            timeout=self._timeout_upload,  # Use a separate client for uploads
        )  # For s3 uploads

    @classmethod
    def from_settings(
        cls, settings: PixelApiSettings, **kwargs: Unpack[PixelClientKwargs]
    ) -> Self:
        """Instantiate the client from settings.

        Args:
            settings: PixelApiSettings object containing API configuration.
            **kwargs: Additional keyword arguments to pass to the client constructor.

        Returns:
            PixelClientAsync: A new client instance configured with the provided settings.
        """
        return cls(
            url=settings.PIXEL_API_URL,
            keycloak_server_url=settings.KEYCLOAK_SERVER_URL,
            client_id=settings.KEYCLOAK_CLIENT_ID,
            username=settings.KEYCLOAK_USERNAME,
            password=settings.KEYCLOAK_PASSWORD.get_secret_value(),
            realm=settings.KEYCLOAK_REALM.get_secret_value(),
            **kwargs,
        )

    async def __aenter__(self):
        await self.pixel_client.__aenter__()
        await self._internal_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.pixel_client.__aexit__(exc_type, exc_value, traceback)
        await self._internal_client.__aexit__(exc_type, exc_value, traceback)

    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make an HTTP request to the Pixel API with error handling.

        Args:
            method: The HTTP method to use (GET, POST, PUT, DELETE).
            url: The URL to request, relative to the base URL.
            **kwargs: Additional arguments to pass to the request method.

        Returns:
            httpx.Response: The HTTP response object.

        Raises:
            PixelBadRequestError: If the server returns a 4xx client error with JSON response.
            httpx.HTTPStatusError: For other HTTP errors.
        """
        sensitive_content = kwargs.pop("sensitive_content", False)
        headers = kwargs.pop("headers", {})
        if "X-Request-ID" not in headers:
            headers["X-Request-ID"] = str(uuid4())
        kwargs["headers"] = headers
        response = await self.pixel_client.request(method, url, **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(f"Error in request {method} {url}: {e}")
            if e.response.is_client_error:
                try:
                    response_json = e.response.json()
                except json.JSONDecodeError:
                    raise e  # If the response is not JSON, raise the original exception
                raise PixelBadRequestError(
                    response_json=response_json,
                    status_code=e.response.status_code,
                    method=method,
                    url=str(e.request.url),
                    request_id=e.response.headers.get("X-Request-ID"),
                    body=e.request.content.decode() if not sensitive_content else None,
                ) from e
            raise e
        return response

    async def _get(self, url: str, **kwargs) -> httpx.Response:
        """Make a GET request to the Pixel API.

        Args:
            url: The URL to request, relative to the base URL.
            **kwargs: Additional arguments to pass to the request method.

        Returns:
            httpx.Response: The HTTP response object.
        """
        return await self._make_request("GET", url, **kwargs)

    async def _post(self, url: str, **kwargs) -> httpx.Response:
        """Make a POST request to the Pixel API.

        Args:
            url: The URL to request, relative to the base URL.
            **kwargs: Additional arguments to pass to the request method.

        Returns:
            httpx.Response: The HTTP response object.
        """
        return await self._make_request("POST", url, **kwargs)

    async def _put(self, url: str, **kwargs) -> httpx.Response:
        """Make a PUT request to the Pixel API.

        Args:
            url: The URL to request, relative to the base URL.
            **kwargs: Additional arguments to pass to the request method.

        Returns:
            httpx.Response: The HTTP response object.
        """
        return await self._make_request("PUT", url, **kwargs)

    async def _delete(self, url: str, **kwargs) -> httpx.Response:
        """Make a DELETE request to the Pixel API.

        Args:
            url: The URL to request, relative to the base URL.
            **kwargs: Additional arguments to pass to the request method.

        Returns:
            httpx.Response: The HTTP response object.
        """
        return await self._make_request("DELETE", url, **kwargs)

    async def _paginate(
        self, url: str, page_size: int, **kwargs
    ) -> AsyncGenerator[dict, None]:
        """Internal helper function for paginating through API results.

        Args:
            url: The API endpoint URL to paginate through.
            page_size: Number of items to fetch per page.
            **kwargs: Additional parameters to pass to the GET request.

        Yields:
            dict: Individual items from the paginated results, one at a time.
        """
        params = kwargs.pop("params", {})
        offset = params.get("offset", 0)
        limit = page_size
        while True:
            response = await self._get(
                url, params={**params, "offset": offset, "limit": limit}
            )
            data = response.json()
            for item in data:
                yield item
            if (
                len(data) < page_size
            ):  # If the number of items is less than the page size, we are done
                break
            offset += limit

    async def me(self, extended: bool = False) -> dict:
        """Get information about the authenticated user.

        Args:
            extended: If True, returns extended user information including projects user is a member of

        Returns:
            dict: User information including username, email, and other profile details.
        """
        response = await self._get("/users/me", params={"extended": extended})
        return response.json()

    async def get_plugins(self) -> list[dict]:
        """Retrieve a list of available plugins for the pixel tenant.
        Possible plugins include:
        * 'optimized_raster' - Optimize Raster capability
        * 'image_service' - Image Service capability, dependent on the 'optimize_raster' plugin.

        Returns:
            list[dict]: A list of plugin objects with their details.
        """
        response = await self._get("/plugins/")
        return response.json()

    async def create_project(
        self,
        name: str,
        description: str,
        area_of_interest: Polygon,
        parent_project_id: int | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        """Create a new project in the Pixel system.

        Args:
            name: The name of the project.
            description: A description of the project.
            area_of_interest: A GeoJSON polygon defining the project's geographic area of interest.
            parent_project_id: Optional ID of a parent project. If provided, this project will be created as a child of that project.
            tags: Optional list of tags to associate with the project.

        Returns:
            dict: The created project object.
        """
        body = {
            "name": name,
            "description": description,
            "area_of_interest": area_of_interest.__geo_interface__,
        }
        if parent_project_id:
            body["parent_project_id"] = parent_project_id
        if tags:
            body["tags"] = tags
        response = await self._post("/projects/", json=body)
        return response.json()

    async def list_projects(
        self, params: ListParams | None = None, **kwargs
    ) -> list[dict]:
        """List projects with optional filtering.

        Args:
            params: Optional ListParams object containing filtering parameters such as offset, limit, search, etc.
            **kwargs: Alternative way to provide filtering parameters. Ignored if params is provided.

        Returns:
            list[dict]: A list of project objects matching the filter criteria.
        """
        if params and kwargs:
            logger.warning("Ignoring kwargs when params is provided")
        params_dict = (
            params.model_dump(exclude_none=True)
            if params
            else ListParams.model_validate(kwargs).model_dump(exclude_none=True)
        )
        response = await self._get("/projects/", params=params_dict)
        return response.json()

    async def list_deleted_projects(
        self, params: ListParams | None = None, **kwargs
    ) -> list[dict]:
        """List deleted projects in the Pixel system.

        Args:
            params: Optional ListParams object containing filtering parameters such as offset, limit, search, etc.
            **kwargs: Alternative way to provide filtering parameters. Ignored if params is provided.

        Returns:
            list[dict]: A list of deleted project objects.
        """
        if params and kwargs:
            logger.warning("Ignoring kwargs when params is provided")
        params_dict = (
            params.model_dump(exclude_none=True)
            if params
            else ListParams.model_validate(kwargs).model_dump(exclude_none=True)
        )
        response = await self._get("/projects/deleted", params=params_dict)
        return response.json()

    async def get_project(self, project_id: int, extended: bool = False) -> dict:
        """Retrieve a project by its ID.

        Args:
            project_id: The ID of the project to retrieve.
            extended: If True, returns extended project information including child projects and data collections.

        Returns:
            dict: The project object with its details.
        """
        response = await self._get(
            f"/projects/{project_id}", params={"extended": extended}
        )
        return response.json()

    async def update_project(
        self,
        project_id: int,
        name: str | None = None,
        description: str | None = None,
        area_of_interest: Polygon | None = None,
        add_tags: list[str] | None = None,
        remove_tags: list[str] | None = None,
    ) -> dict:
        """Update an existing project with new values.

        Args:
            project_id: The ID of the project to update.
            name: Optional new name for the project.
            description: Optional new description for the project.
            area_of_interest: Optional new GeoJSON polygon defining the project's geographic area of interest.
            add_tags: Optional list of tags to add to the project.
            remove_tags: Optional list of tags to remove from the project.

        Returns:
            dict: The updated project object.

        Raises:
            ValueError: If no update parameters are provided.
        """
        body = {}
        for param_name, value in {
            "name": name,
            "description": description,
            "area_of_interest": area_of_interest.__geo_interface__
            if area_of_interest
            else None,
            "add_tags": add_tags,
            "remove_tags": remove_tags,
        }.items():
            if value is not None:
                body[param_name] = value
        if not body:
            raise ValueError("No update parameters provided")
        response = await self._put(f"/projects/{project_id}", json=body)
        return response.json()

    async def delete_project(self, project_id: int) -> dict:
        """Delete a project by its ID.

        Args:
            project_id: The ID of the project to delete.

        Returns:
            dict: The response confirming deletion.
        """
        response = await self._delete(f"/projects/{project_id}")
        return response.json()

    async def restore_project(self, project_id: int) -> dict:
        """Restore a deleted project by its ID.

        Args:
            project_id: The ID of the project to restore.

        Returns:
            dict: The restored project object.
        """
        response = await self._post(f"/projects/{project_id}/restore")
        return response.json()

    async def move_project(
        self, project_id: int, new_parent_project_id: int | None = None
    ) -> dict:
        """Move a project to a new parent project or to the root level.

        Args:
            project_id: The ID of the project to move.
            new_parent_project_id: Optional ID of the new parent project. If None, the project will be moved to the root level.

        Returns:
            dict: The updated project object.
        """
        # If None is provided, set to -1 to move to root
        new_parent_project_id = new_parent_project_id or -1
        response = await self._put(
            f"/projects/{project_id}",
            params={"new_parent_id": new_parent_project_id},
        )
        return response.json()

    async def create_data_collection(
        self,
        project_id: int,
        name: str,
        description: str,
        data_collection_type: DataCollectionType,
        tags: list[str] | None = None,
        raster_info: RasterInfo | None = None,
    ) -> dict:
        """Create a new data collection within a project.

        Args:
            project_id: The ID of the project to create the data collection in.
            name: The name of the data collection.
            description: A description of the data collection.
            data_collection_type: The type of data collection (e.g., "image", "raster", "RGB", "DTM", "DSM").
            tags: Optional list of tags to associate with the data collection.
            raster_info: Optional RasterInfo object containing raster-specific configuration.

        Returns:
            dict: The created data collection object.
        """
        body: dict[str, Any] = {
            "name": name,
            "description": description,
            "data_collection_type": data_collection_type,
        }
        if tags:
            body["tags"] = tags
        if raster_info:
            body["raster_info"] = raster_info.model_dump(exclude_none=True, mode="json")
        response = await self._post(
            f"/projects/{project_id}/data_collections/", json=body
        )
        return response.json()

    async def list_data_collections(
        self, project_id: int, params: DataCollectionListParams | None = None, **kwargs
    ) -> list[dict]:
        """List data collections within a project with optional filtering.

        Args:
            project_id: The ID of the project to list data collections from.
            params: Optional DataCollectionListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters. Ignored if params is provided.

        Returns:
            list[dict]: A list of data collection objects matching the filter criteria.
        """
        if params and kwargs:
            logger.warning("Ignoring kwargs when params is provided")
        params_dict = (
            params.model_dump(exclude_none=True)
            if params
            else DataCollectionListParams.model_validate(kwargs).model_dump(
                exclude_none=True
            )
        )
        response = await self._get(
            f"/projects/{project_id}/data_collections/", params=params_dict
        )
        return response.json()

    async def list_deleted_data_collections(
        self, project_id: int, params: DataCollectionListParams | None = None, **kwargs
    ) -> list[dict]:
        """List deleted data collections within a project.

        Args:
            project_id: The ID of the project to list deleted data collections from.

        Returns:
            list[dict]: A list of deleted data collection objects.
        """
        if params and kwargs:
            logger.warning("Ignoring kwargs when params is provided")
        params_dict = (
            params.model_dump(exclude_none=True)
            if params
            else DataCollectionListParams.model_validate(kwargs).model_dump(
                exclude_none=True
            )
        )
        response = await self._get(
            f"/projects/{project_id}/data_collections/deleted", params=params_dict
        )
        return response.json()

    async def get_data_collection(
        self, project_id: int, data_collection_id: int
    ) -> dict:
        """Retrieve a data collection by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to retrieve.

        Returns:
            dict: The data collection object with its details.
        """
        response = await self._get(
            f"/projects/{project_id}/data_collections/{data_collection_id}"
        )
        return response.json()

    async def update_data_collection(
        self,
        project_id: int,
        data_collection_id: int,
        name: str | None = None,
        description: str | None = None,
        add_tags: list[str] | None = None,
        remove_tags: list[str] | None = None,
    ) -> dict:
        """Update an existing data collection with new values.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to update.
            name: Optional new name for the data collection.
            description: Optional new description for the data collection.
            add_tags: Optional list of tags to add to the data collection.
            remove_tags: Optional list of tags to remove from the data collection.

        Returns:
            dict: The updated data collection object.

        Raises:
            ValueError: If no update parameters are provided.
        """
        body = {}
        for param_name, value in {
            "name": name,
            "description": description,
            "add_tags": add_tags,
            "remove_tags": remove_tags,
        }.items():
            if value is not None:
                body[param_name] = value
        if not body:
            raise ValueError("No update parameters provided")
        response = await self._put(
            f"/projects/{project_id}/data_collections/{data_collection_id}", json=body
        )
        return response.json()

    async def move_data_collection(
        self, project_id: int, data_collection_id: int, new_project_id: int
    ) -> dict:
        """Move a data collection to a different project.

        Args:
            project_id: The ID of the project currently containing the data collection.
            data_collection_id: The ID of the data collection to move.
            new_project_id: The ID of the project to move the data collection to.

        Returns:
            dict: The updated data collection object.
        """
        response = await self._put(
            f"/projects/{project_id}/data_collections/{data_collection_id}",
            params={"new_project_id": new_project_id},
        )
        return response.json()

    async def delete_data_collection(
        self, project_id: int, data_collection_id: int
    ) -> dict:
        """Delete a data collection by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to delete.

        Returns:
            dict: The response confirming deletion.
        """
        response = await self._delete(
            f"/projects/{project_id}/data_collections/{data_collection_id}"
        )
        return response.json()

    async def restore_data_collection(
        self, project_id: int, data_collection_id: int
    ) -> dict:
        """Restore a deleted data collection by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to restore.

        Returns:
            dict: The restored data collection object.
        """
        response = await self._post(
            f"/projects/{project_id}/data_collections/{data_collection_id}/restore"
        )
        return response.json()

    async def get_images(
        self,
        project_id: int,
        data_collection_id: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> dict:
        """Retrieve images from a data collection with optional filtering.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the images.
            params: Optional ListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters.

        Returns:
            dict: A list of image objects matching the filter criteria.
        """
        params_dict = params.model_dump(exclude_none=True) if params else {}
        params_dict.update(kwargs)
        response = await self._get(
            f"/projects/{project_id}/data_collections/{data_collection_id}/images/",
            params=params_dict,
        )
        return response.json()

    async def paginate_images(
        self,
        project_id: int,
        data_collection_id: int,
        page_size: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> AsyncGenerator[dict, None]:
        """Paginate through images in a data collection with optional filtering.

        This method returns an async generator that yields images one at a time,
        automatically handling pagination in the background.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the images.
            page_size: The number of images to fetch per page.
            params: Optional ListParams object containing filtering parameters (excluding offset and limit).
            **kwargs: Alternative way to provide filtering parameters.

        Yields:
            dict: Image objects matching the filter criteria, one at a time.
        """
        params_dict = (
            params.model_dump(exclude_none=True, exclude={"offset", "limit"})
            if params
            else {}
        )
        params_dict.update(kwargs)
        url = f"/projects/{project_id}/data_collections/{data_collection_id}/images/"
        async for item in self._paginate(url, page_size, params=params_dict):
            yield item

    async def get_image(
        self,
        project_id: int,
        data_collection_id: int,
        image_id: int,
    ) -> dict:
        """Retrieve a specific image by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the image.
            image_id: The ID of the image to retrieve.

        Returns:
            dict: The image object with its details.
        """
        response = await self._get(
            f"/projects/{project_id}/data_collections/{data_collection_id}/images/{image_id}"
        )
        return response.json()

    async def get_image_metadata(
        self, project_id: int, data_collection_id: int, image_id: int
    ) -> dict:
        """
        Retrieve metadata for a specific image by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the image.
            image_id: The ID of the image to retrieve metadata for.

        Returns:
            dict: The image metadata object with its details.
        """
        response = await self._get(
            f"/projects/{project_id}/data_collections/{data_collection_id}/images/{image_id}/metadata"
        )
        return response.json()

    async def update_image(
        self,
        project_id: int,
        data_collection_id: int,
        image_id: int,
        update_input: ImageUpdateInput,
    ) -> dict:
        """Update an existing image with new values.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the image.
            image_id: The ID of the image to update.
            update_input: ImageUpdateInput object containing the fields to update.

        Returns:
            dict: The updated image object.
        """

        response = await self._put(
            f"/projects/{project_id}/data_collections/{data_collection_id}/images/{image_id}",
            json=update_input.model_dump(mode="json", exclude_none=True),
        )
        return response.json()

    async def delete_image(
        self,
        project_id: int,
        data_collection_id: int,
        image_id: int,
    ) -> dict:
        """Delete a specific image by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the image.
            image_id: The ID of the image to delete.

        Returns:
            dict: The response confirming deletion.
        """
        response = await self._delete(
            f"/projects/{project_id}/data_collections/{data_collection_id}/images/{image_id}"
        )
        return response.json()

    async def get_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> dict:
        """Retrieve rasters from a data collection with optional filtering.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the rasters.
            params: Optional ListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters.

        Returns:
            dict: A list of raster objects matching the filter criteria.
        """
        params_dict = params.model_dump(exclude_none=True) if params else {}
        params_dict.update(kwargs)
        response = await self._get(
            f"/projects/{project_id}/data_collections/{data_collection_id}/rasters/",
            params=params_dict,
        )
        return response.json()

    async def paginate_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        page_size: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> AsyncGenerator[dict, None]:
        """Paginate through rasters in a data collection with optional filtering.

        This method returns an async generator that yields rasters one at a time,
        automatically handling pagination in the background.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the rasters.
            page_size: The number of rasters to fetch per page.
            params: Optional ListParams object containing filtering parameters (excluding offset and limit).
            **kwargs: Alternative way to provide filtering parameters.

        Yields:
            dict: Raster objects matching the filter criteria, one at a time.
        """
        params_dict = (
            params.model_dump(exclude_none=True, exclude={"offset", "limit"})
            if params
            else {}
        )
        params_dict.update(kwargs)
        url = f"/projects/{project_id}/data_collections/{data_collection_id}/rasters/"
        async for item in self._paginate(url, page_size, params=params_dict):
            yield item

    async def get_raster(
        self,
        project_id: int,
        data_collection_id: int,
        raster_id: int,
    ) -> dict:
        """Retrieve a specific raster by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the raster.
            raster_id: The ID of the raster to retrieve.

        Returns:
            dict: The raster object with its details.
        """
        response = await self._get(
            f"/projects/{project_id}/data_collections/{data_collection_id}/rasters/{raster_id}"
        )
        return response.json()

    async def update_raster(
        self,
        project_id: int,
        data_collection_id: int,
        raster_id: int,
        update_input: RasterUpdateInput,
    ) -> dict:
        """Update an existing raster with new values.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the raster.
            raster_id: The ID of the raster to update.
            update_input: RasterUpdateInput object containing the fields to update.

        Returns:
            dict: The updated raster object.

        """
        response = await self._put(
            f"/projects/{project_id}/data_collections/{data_collection_id}/rasters/{raster_id}",
            json=update_input.model_dump(mode="json", exclude_none=True),
        )
        return response.json()

    async def delete_raster(
        self,
        project_id: int,
        data_collection_id: int,
        raster_id: int,
    ) -> dict:
        """Delete a specific raster by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the raster.
            raster_id: The ID of the raster to delete.

        Returns:
            dict: The response confirming deletion.
        """
        response = await self._delete(
            f"/projects/{project_id}/data_collections/{data_collection_id}/rasters/{raster_id}"
        )
        return response.json()

    async def get_upload_jobs(
        self,
        project_id: int,
        data_collection_id: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> list[dict]:
        """Retrieve upload jobs for a data collection with optional filtering.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to list upload jobs for.
            params: Optional ListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters. Ignored if params is provided.

        Returns:
            list[dict]: A list of upload job objects matching the filter criteria.
        """
        if params and kwargs:
            logger.warning("Ignoring kwargs when params is provided")
        params_dict = (
            params.model_dump(exclude_none=True)
            if params
            else ListParams.model_validate(kwargs).model_dump(exclude_none=True)
        )
        response = await self._get(
            f"/projects/{project_id}/data_collections/{data_collection_id}/upload_jobs/",
            params=params_dict,
        )
        return response.json()

    async def _create_upload_jobs(
        self,
        project_id: int,
        data_collection_id: int,
        multipart: bool,
        files: list[dict],
    ) -> list[dict]:
        """Internal helper to create upload job objects in the API.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to create upload jobs for.
            multipart: If True, create multipart upload jobs for large files.
            files: List of file objects containing metadata for the upload jobs.

        Returns:
            list[dict]: The created upload job objects.
        """
        url = (
            f"/projects/{project_id}/data_collections/{data_collection_id}/upload_jobs/"
        )
        if multipart:
            url += "multipart"
        body = {"files": files}
        response = await self._post(url, json=body)
        return response.json()

    def _create_support_file_file(
        self,
        file_path: Path,
    ) -> dict:
        """Create a file object for a support file to be included in an upload job.

        Args:
            file_path: Path to the support file.

        Returns:
            dict: A file object containing the file name and MD5 hash.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} not found")
        return {
            "name": file_path.name,
            "md5": calculate_md5_base64_from_file(file_path),
        }

    def _create_single_part_upload_job_from_file(
        self,
        file_path: Path,
        support_files: list[Path] | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Create a file object for a single-part upload job.

        Args:
            file_path: Path to the file to upload.
            support_files: Optional list of support file paths to include with the upload.
            metadata: Optional metadata to associate with the file.

        Returns:
            dict: A file object containing the file name, MD5 hash, and optional metadata and support files.
        """
        body: dict[str, Any] = {
            "name": file_path.name,
            "md5": calculate_md5_base64_from_file(file_path),
        }
        if metadata:
            body["metadata"] = metadata
        if support_files:
            body["support_files"] = [
                self._create_support_file_file(f) for f in support_files
            ]
        return body

    def _create_multipart_upload_job_from_file(
        self,
        file_path: Path,
        part_size: int,
        support_files: list[Path] | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Create a file object for a multipart upload job.

        Args:
            file_path: Path to the file to upload.
            part_size: Size of each part in bytes.
            support_files: Optional list of support file paths to include with the upload.
            metadata: Optional metadata to associate with the file.

        Returns:
            dict: A file object containing the file name, parts information, and optional metadata and support files.
        """
        parts = []
        for part_number, (content_length, md5, _) in enumerate(
            iter_file_parts(file_path, part_size), start=1
        ):
            parts.append(
                {
                    "part_number": part_number,
                    "md5": md5,
                    "content_length": content_length,
                }
            )
        file_body = {
            "name": file_path.name,
            "parts": parts,
        }
        if metadata:
            file_body["metadata"] = metadata
        if support_files:
            file_body["support_files"] = [
                self._create_support_file_file(f) for f in support_files
            ]
        return file_body

    async def _upload_singlepart_to_s3(
        self,
        upload_job: dict,
        file_path: Path,
    ):
        """Upload a file to S3 using a single part upload.

        Args:
            upload_job: Upload job object containing the S3 URL and upload fields.
            file_path: Path to the file to upload.

        Returns:
            None: This method returns None on success.

        Raises:
            httpx.HTTPStatusError: If the upload fails.
        """
        response = await self._internal_client.post(
            upload_job["url"],
            files={"file": file_path.read_bytes()},
            data=upload_job["upload_fields"],
        )
        response.raise_for_status()
        return None

    async def _upload_part_to_s3(
        self,
        part: dict,
        part_data: bytes,
    ):
        """Upload a part of a file to S3 as part of a multipart upload.

        Args:
            part: Part object containing the S3 URL and headers.
            part_data: Binary data for this part of the file.

        Returns:
            None: This method returns None on success.

        Raises:
            httpx.HTTPStatusError: If the upload fails.
        """
        response = await self._internal_client.put(
            part["url"], content=part_data, headers=part["headers"]
        )
        response.raise_for_status()
        return None

    async def _upload_multipart_to_s3(
        self,
        upload_job: dict,
        file_path: Path,
        multipart_part_size: int,
    ):
        """Upload all parts of a file to S3 using a multipart upload.

        Args:
            upload_job: Upload job object containing the parts information.
            file_path: Path to the file to upload.
            multipart_part_size: Size of each part in bytes.

        Returns:
            None: This method returns None on success.
        """
        parts = sorted(upload_job["upload_parts"], key=lambda p: p["part_number"])
        upload_iterator = zip(iter_file_parts(file_path, multipart_part_size), parts)
        await asyncio.gather(
            *[
                self._upload_part_to_s3(part, part_data)
                for (_, _, part_data), part in upload_iterator
            ]
        )
        return None

    async def _upload_to_s3(
        self,
        file: Path,
        support_files: list[Path] | None,
        upload_job: dict,
        multipart: bool,
        multipart_part_size: int | None,
    ):
        """Upload a file and its support files to S3.

        Args:
            file: Path to the main file to upload.
            support_files: Optional list of support file paths to upload with the main file.
            upload_job: Upload job object containing the upload information.
            multipart: If True, use multipart upload for the main file.
            multipart_part_size: Required size of each part in bytes when using multipart upload.

        Returns:
            None: This method returns None on success.

        Raises:
            AssertionError: If multipart is True but multipart_part_size is not provided,
                           or if support_files are required but not provided.
        """
        logger.info(f"Uploading {file} to S3 with upload job {upload_job['id']}")
        if multipart:
            assert multipart_part_size, (
                "multipart_part_size must be provided for multipart upload"
            )
            await self._upload_multipart_to_s3(upload_job, file, multipart_part_size)
        else:
            await self._upload_singlepart_to_s3(upload_job, file)
        if upload_job.get("support_files"):
            assert support_files, "Support files must be provided for upload job"
            # Sort the support file by name
            support_files = sorted(support_files, key=lambda f: f.name)
            upload_job_support_files = sorted(
                upload_job["support_files"], key=lambda f: f["name"]
            )
            await asyncio.gather(
                *[
                    self._upload_singlepart_to_s3(uj_sp, sp_path)
                    for uj_sp, sp_path in zip(upload_job_support_files, support_files)
                ]
            )
        logger.info(f"Upload job {upload_job['id']} with {file} completed upload")
        return None

    async def _upload_file_finished(
        self,
        project_id: int,
        data_collection_id: int,
        upload_job_id: int,
    ) -> dict:
        """Signal to the API that a file upload has completed.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the upload job.
            upload_job_id: The ID of the upload job to mark as finished.

        Returns:
            dict: The response containing job information for the validation process.
        """
        response = await self._put(
            f"/projects/{project_id}/data_collections/{data_collection_id}/upload_jobs/{upload_job_id}/uploadFinished"
        )
        return response.json()

    async def _multiple_upload_file_finished(
        self,
        project_id: int,
        data_collection_id: int,
        upload_job_ids: list[int],
    ) -> dict:
        """Signal to the API that multiple file uploads have completed.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the upload jobs.
            upload_job_ids: List of upload job IDs to mark as finished.

        Returns:
            dict: The response containing group job information and updated upload jobs.
        """
        response = await self._put(
            f"/projects/{project_id}/data_collections/{data_collection_id}/upload_jobs/multiple_uploadFinished",
            json={"job_ids": upload_job_ids},
        )
        return response.json()

    async def _wait_for_multiple_upload_jobs(
        self,
        project_id: int,
        data_collection_id: int,
        group_job_id: int,
        upload_job_ids: list[int],
    ) -> tuple[list[dict], list[PixelUploadJobError]]:
        """Wait for multiple upload jobs to complete validation and processing.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the upload jobs.
            group_job_id: The ID of the group job managing the upload jobs.
            upload_job_ids: List of upload job IDs to wait for.

        Returns:
            tuple: A tuple containing:
                - list[dict]: List of successfully completed upload jobs.
                - list[PixelUploadJobError]: List of errors for failed upload jobs.
        """
        _ = await self.wait_for_group_job(group_job_id=group_job_id)
        upload_jobs = await self.get_upload_jobs(
            project_id,
            data_collection_id,
            ids=upload_job_ids,
            limit=len(upload_job_ids),
        )
        while any(
            uj["status"] in ("lobby", "validating", "submitted", "validated")
            for uj in upload_jobs
        ):
            upload_jobs = await self.get_upload_jobs(
                project_id,
                data_collection_id,
                ids=upload_job_ids,
                limit=len(upload_job_ids),
            )
            await asyncio.sleep(1)
        # Collect any errors
        errors = []
        finished_upload_jobs = []
        for uj in upload_jobs:
            try:
                if uj["status"] != "validated_and_moved":
                    raise PixelUploadJobError(
                        job_id=uj["id"], status=uj["status"], detail=uj["detail"]
                    )
            except PixelUploadJobError as e:
                errors.append(e)
            else:
                finished_upload_jobs.append(uj)
        return finished_upload_jobs, errors

    async def _wait_for_upload_job(
        self, project_id: int, data_collection_id: int, upload_job_id: int, job_id: int
    ) -> dict:
        """Wait for a single upload job to complete validation and processing.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the upload job.
            upload_job_id: The ID of the upload job to wait for.
            job_id: The ID of the job managing the upload job validation.

        Returns:
            dict: The completed upload job object.

        Raises:
            PixelUploadJobError: If the upload job fails validation or processing.
        """
        await self.wait_for_job(job_id)
        upload_jobs = await self.get_upload_jobs(
            project_id, data_collection_id, ids=[upload_job_id], limit=1
        )
        upload_job = upload_jobs[0]
        if upload_job["status"] == "validated_and_moved":
            return upload_job
        if upload_job["status"] != "validated_and_moved":
            raise PixelUploadJobError(
                job_id=upload_job_id,
                status=upload_job["status"],
                detail=upload_job["detail"],
            )
        return upload_job

    async def _resources_from_upload_jobs(
        self, project_id: int, data_collection_id: int, upload_jobs: list[dict]
    ) -> list[dict]:
        """Retrieve the created resources (images or rasters) from completed upload jobs.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the resources.
            upload_jobs: List of completed upload job objects.

        Returns:
            list[dict]: List of resource objects (images or rasters) created from the upload jobs.
        """
        # Chunk up the resources ids
        chunk_size = 50
        image_resource_ids: list[int] = []
        raster_resource_ids: list[int] = []
        image_resources: list[dict] = []
        raster_resources: list[dict] = []
        for upload_job in upload_jobs:
            if upload_job["result"]["resource_name"] == "image":
                image_resource_ids.append(upload_job["result"]["resource_id"])
            if upload_job["result"]["resource_name"] == "raster":
                raster_resource_ids.append(upload_job["result"]["resource_id"])
        for chunk in chunks(image_resource_ids, chunk_size):
            image_resources.extend(
                await self.get_images(
                    project_id,
                    data_collection_id,
                    params=ListParams(ids=chunk, limit=len(chunk)),
                )
            )
        for chunk in chunks(raster_resource_ids, chunk_size):
            raster_resources.extend(
                await self.get_rasters(
                    project_id,
                    data_collection_id,
                    params=ListParams(ids=chunk, limit=len(chunk)),
                )
            )
        resources = image_resources + raster_resources
        return resources

    async def _resource_from_upload_job(
        self, project_id: int, data_collection_id: int, upload_job: dict
    ) -> dict:
        """Retrieve the created resource (image or raster) from a completed upload job.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the resource.
            upload_job: The completed upload job object.

        Returns:
            dict: The resource object (image or raster) created from the upload job.

        Raises:
            ValueError: If the resource type in the upload job result is unknown.
        """
        if upload_job["result"]["resource_name"] == "image":
            return await self.get_image(
                project_id, data_collection_id, upload_job["result"]["resource_id"]
            )
        if upload_job["result"]["resource_name"] == "raster":
            return await self.get_raster(
                project_id, data_collection_id, upload_job["result"]["resource_id"]
            )
        raise ValueError(
            f"Unknown resource name in upload job result: {upload_job['result']}"
        )

    async def _upload_multiple_files(
        self,
        project_id: int,
        data_collection_id: int,
        files: list[PixelUploadFile],
        multipart: bool,
        multipart_part_size: int | None,
        raise_on_error: bool = False,
    ) -> tuple[list[dict], list[PixelUploadJobError]]:
        """Upload multiple files to a data collection.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to upload to.
            files: List of PixelUploadFile objects containing the files to upload.
            multipart: If True, use multipart upload for large files.
            multipart_part_size: Required size of each part in bytes when using multipart upload.
            raise_on_error: If True, raise a PixelMultipleUploadJobError if any uploads fail.

        Returns:
            tuple: A tuple containing:
                - list[dict]: List of created resource objects (images or rasters).
                - list[PixelUploadJobError]: List of errors for failed uploads.

        Raises:
            ValueError: If any files have duplicate names.
            PixelMultipleUploadJobError: If raise_on_error is True and any uploads fail.
        """

        # Chunk the operation into 200 files at a time (maximum for API)
        all_resources: list[dict] = []
        all_errors: list[PixelUploadJobError] = []

        create_body_func = (
            partial(
                self._create_multipart_upload_job_from_file,
                part_size=multipart_part_size,  # type: ignore
            )
            if multipart
            else self._create_single_part_upload_job_from_file
        )
        # Assert unique file names
        file_names = [f.file.name for f in files]
        if len(file_names) != len(set(file_names)):
            raise ValueError("All files must have unique names")
        for files_chunk in chunks(files, 200):
            logger.info("Uploading chunk of %d files", len(files_chunk))
            file_bodies = [
                create_body_func(
                    file.file,
                    support_files=file.support_files,
                    metadata=file.metadata.model_dump(mode="json", exclude_none=True)
                    if file.metadata
                    else None,
                )
                for file in files_chunk
            ]
            upload_jobs = await self._create_upload_jobs(
                project_id, data_collection_id, multipart, file_bodies
            )
            # sort the upload jobs by the file name
            upload_jobs = sorted(upload_jobs, key=lambda uj: uj["name"])
            files = sorted(files, key=lambda f: f.file.name)
            await asyncio.gather(
                *[
                    self._upload_to_s3(
                        file.file,
                        file.support_files,
                        upload_job,
                        multipart,
                        multipart_part_size,
                    )
                    for upload_job, file in zip(upload_jobs, files)
                ]
            )
            upload_finished = await self._multiple_upload_file_finished(
                project_id, data_collection_id, [uj["id"] for uj in upload_jobs]
            )
            group_job = upload_finished["group_job"]
            upload_jobs = upload_finished["upload_jobs"]
            upload_jobs, errors = await self._wait_for_multiple_upload_jobs(
                project_id,
                data_collection_id,
                group_job["group_id"],
                [uj["id"] for uj in upload_jobs],
            )
            resources = await self._resources_from_upload_jobs(
                project_id, data_collection_id, upload_jobs
            )
            all_resources.extend(resources)
            all_errors.extend(errors)

        if raise_on_error and all_errors:
            raise PixelMultipleUploadJobError(errors)
        return all_resources, all_errors

    async def _upload_file(
        self,
        project_id: int,
        data_collection_id: int,
        file_path: Path,
        support_files: list[Path] | None = None,
        metadata: dict | None = None,
        multipart: bool = False,
        multipart_part_size: int | None = None,
    ) -> dict:
        """Upload a single file to a data collection.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to upload to.
            file_path: Path to the file to upload.
            support_files: Optional list of support file paths to upload with the file.
            metadata: Optional dictionary of metadata to associate with the file.
            multipart: If True, use multipart upload for large files.
            multipart_part_size: Required size of each part in bytes when using multipart upload.

        Returns:
            dict: The created resource object (image or raster).

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If multipart is True but multipart_part_size is not provided.
            PixelUploadJobError: If the upload job fails validation or processing.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} not found")
        if multipart and not multipart_part_size:
            raise ValueError(
                "multipart_part_size must be provided for multipart upload"
            )
        if multipart:
            assert multipart_part_size
            file_body = self._create_multipart_upload_job_from_file(
                file_path,
                multipart_part_size,
                support_files=support_files,
                metadata=metadata,
            )
        else:
            file_body = self._create_single_part_upload_job_from_file(
                file_path,
                support_files=support_files,
                metadata=metadata,
            )
        upload_jobs = await self._create_upload_jobs(
            project_id, data_collection_id, multipart, [file_body]
        )
        upload_job = upload_jobs[0]
        await self._upload_to_s3(
            file_path,
            support_files,
            upload_job,
            multipart,
            multipart_part_size,
        )
        upload_job_finished = await self._upload_file_finished(
            project_id, data_collection_id, upload_job["id"]
        )
        job = upload_job_finished["job"]
        upload_job = await self._wait_for_upload_job(
            project_id, data_collection_id, upload_job["id"], job["job_id"]
        )
        return await self._resource_from_upload_job(
            project_id, data_collection_id, upload_job
        )

    async def upload_image(
        self,
        project_id: int,
        data_collection_id: int,
        file_path: Path,
        metadata: dict | None = None,
        support_files: list[Path] | None = None,
        multipart: bool = False,
        multipart_part_size: int | None = None,
    ) -> dict:
        """Upload an image file to an image data collection.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the image data collection to upload to.
            file_path: Path to the image file to upload.
            metadata: Optional dictionary of metadata to associate with the image.
            support_files: Optional list of support file paths to upload with the image.
            multipart: If True, use multipart upload for large files.
            multipart_part_size: Required size of each part in bytes when using multipart upload.

        Returns:
            dict: The created image object.

        Raises:
            ValueError: If the data collection is not an image data collection.
            FileNotFoundError: If the file does not exist.
            ValueError: If multipart is True but multipart_part_size is not provided.
        """
        dc = await self.get_data_collection(project_id, data_collection_id)
        if dc["data_collection_type"] != "image":
            raise ValueError("Data collection is not an image data collection")
        return await self._upload_file(
            project_id,
            data_collection_id,
            file_path,
            support_files=support_files,
            metadata=metadata,
            multipart=multipart,
            multipart_part_size=multipart_part_size,
        )

    async def upload_multiple_images(
        self,
        project_id: int,
        data_collection_id: int,
        files: list[PixelUploadFile],
        multipart: bool = False,
        multipart_part_size: int | None = None,
    ) -> tuple[list[dict], list[PixelUploadJobError]]:
        """Upload multiple image files to an image data collection.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the image data collection to upload to.
            files: List of PixelUploadFile objects containing the files to upload.
            multipart: If True, use multipart upload for large files.
            multipart_part_size: Required size of each part in bytes when using multipart upload.

        Returns:
            tuple: A tuple containing:
                - list[dict]: List of created image objects.
                - list[PixelUploadJobError]: List of errors that occurred during upload.

        Raises:
            ValueError: If the data collection is not an image data collection.
            ValueError: If any files have duplicate names.
            ValueError: If multipart is True but multipart_part_size is not provided.
        """
        dc = await self.get_data_collection(project_id, data_collection_id)
        if dc["data_collection_type"] != "image":
            raise ValueError("Data collection is not an image data collection")
        return await self._upload_multiple_files(
            project_id,
            data_collection_id,
            files,
            multipart,
            multipart_part_size,
        )

    async def upload_multiple_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        files: list[PixelUploadFile],
        multipart: bool = False,
        multipart_part_size: int | None = None,
    ) -> tuple[list[dict], list[PixelUploadJobError]]:
        """Upload multiple raster files to a raster data collection.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the raster data collection to upload to.
            files: List of PixelUploadFile objects containing the files to upload.
            multipart: If True, use multipart upload for large files.
            multipart_part_size: Required size of each part in bytes when using multipart upload.

        Returns:
            tuple: A tuple containing:
                - list[dict]: List of created raster objects.
                - list[PixelUploadJobError]: List of errors that occurred during upload.

        Raises:
            ValueError: If the data collection is not a raster data collection.
            ValueError: If any files have duplicate names.
            ValueError: If multipart is True but multipart_part_size is not provided.
        """
        dc = await self.get_data_collection(project_id, data_collection_id)
        if dc["data_collection_type"] not in ("raster", "RGB", "DTM", "DSM"):
            raise ValueError("Data collection is not a raster data collection")
        return await self._upload_multiple_files(
            project_id,
            data_collection_id,
            files,
            multipart,
            multipart_part_size,
        )

    async def upload_raster(
        self,
        project_id: int,
        data_collection_id: int,
        file_path: Path,
        support_files: list[Path] | None = None,
        multipart: bool = False,
        multipart_part_size: int | None = None,
    ) -> dict:
        """Upload a raster file to a raster data collection.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the raster data collection to upload to.
            file_path: Path to the raster file to upload.
            support_files: Optional list of support file paths to upload with the raster.
            multipart: If True, use multipart upload for large files.
            multipart_part_size: Required size of each part in bytes when using multipart upload.

        Returns:
            dict: The created raster object.

        Raises:
            ValueError: If the data collection is not a raster data collection.
            FileNotFoundError: If the file does not exist.
            ValueError: If multipart is True but multipart_part_size is not provided.
        """
        dc = await self.get_data_collection(project_id, data_collection_id)
        if dc["data_collection_type"] not in ("raster", "RGB", "DTM", "DSM"):
            raise ValueError("Data collection is not a raster data collection")
        return await self._upload_file(
            project_id,
            data_collection_id,
            file_path,
            support_files=support_files,
            multipart=multipart,
            multipart_part_size=multipart_part_size,
        )

    async def create_optimized_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        raster_ids: list[int] | None,
        profile: str | None = None,
        nearblack: NearblackOptions | None = None,
        overview_resampling: OverviewResampling = "average",
    ) -> list[dict]:
        """Create optimized raster objects in the database.

        This function creates optimized raster objects but does not run the actual optimization process.
        To run the optimization, use the run_optimize_rasters function with the returned optimized raster IDs.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the rasters.
            raster_ids: Optional list of raster IDs to optimize. If None, all rasters in the collection will be optimized.
            profile: Optional profile name to use for optimization.
            nearblack: Optional NearblackOptions object for configuring the nearblack process.
            overview_resampling: The resampling method to use for creating overviews. Default is "average".

        Returns:
            list[dict]: List of created optimized raster objects.
        """
        body: dict = {
            "creation_options": {
                "nearblack_options": nearblack.model_dump(
                    exclude_none=True, mode="json"
                )
                if nearblack
                else NearblackOptions(enabled=False).model_dump(
                    exclude_none=True, mode="json"
                ),
                "overview_resampling": overview_resampling,
            }
        }
        if raster_ids:
            body["raster_ids"] = raster_ids
        if profile:
            body["profile"] = profile
        response = await self._post(
            f"/projects/{project_id}/data_collections/{data_collection_id}/rasters/optimized/",
            json=body,
        )
        return response.json()

    async def run_optimize_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        optimize_raster_ids: list[int] | None,
        retry_failed: bool = False,
    ) -> dict:
        """Run the optimization process on optimized raster objects.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the optimized rasters.
            optimize_raster_ids: Optional list of optimized raster IDs to process. If None, all optimized rasters in the collection will be processed.
            retry_failed: If True, retry previously failed optimization jobs.

        Returns:
            dict: The group job object representing the optimization process.
        """
        body: dict = {"retry_failed": retry_failed}
        if optimize_raster_ids:
            body["optimized_raster_ids"] = optimize_raster_ids
        response = await self._post(
            f"/projects/{project_id}/data_collections/{data_collection_id}/rasters/optimized/run",
            json=body,
        )
        response_json = response.json()

        job = await self.wait_for_group_job(response_json["group_job"]["group_id"])
        return job

    async def get_job(
        self,
        job_id: int,
    ) -> dict:
        """Retrieve information about a specific job.

        Args:
            job_id: The ID of the job to retrieve.

        Returns:
            dict: The job object with its details.
        """
        response = await self._get(f"/jobs/{job_id}")
        return response.json()

    async def get_job_group(
        self,
        job_id: int,
    ) -> dict:
        """Retrieve information about a specific job group.

        Args:
            job_id: The ID of the job group to retrieve.

        Returns:
            dict: The job group object with its details.
        """
        response = await self._get(f"/jobs/groups/{job_id}")
        return response.json()

    async def wait_for_job(
        self,
        job_id: int,
        timeout: int = 600,
    ) -> dict:
        """Wait for a job to complete, polling its status at regular intervals.

        Args:
            job_id: The ID of the job to wait for.
            timeout: Maximum time to wait in seconds before raising a TimeoutError. Default is 600 seconds (10 minutes).

        Returns:
            dict: The completed job object.

        Raises:
            TimeoutError: If the job does not complete within the specified timeout period.
        """
        job = await self.get_job(job_id)
        with silence_logger(logging.getLogger("httpx")):
            while not job["completed"]:
                job = await self.get_job(job_id)
                job_name = job["name"] or "unnamed"
                logger.info(f"Job {job_name} {job_id} status: {job['status']}")
                await asyncio.sleep(3)
                timeout -= 5
                if timeout <= 0:
                    raise TimeoutError("Timed out waiting for job")
        logger.info(f"Job {job_id} finished with status {job['status']}")
        return job

    async def wait_for_group_job(
        self,
        group_job_id: int,
        timeout: int = 1200,
    ) -> dict:
        """Wait for a group job to complete, polling its status at regular intervals.

        A group job consists of multiple individual jobs. This method displays a progress bar
        showing the completion status of all jobs in the group.

        Args:
            group_job_id: The ID of the group job to wait for.
            timeout: Maximum time to wait in seconds before raising a TimeoutError. Default is 1200 seconds (20 minutes).

        Returns:
            dict: The completed group job object.

        Raises:
            TimeoutError: If the group job does not complete within the specified timeout period.
        """
        job = await self.get_job_group(group_job_id)
        num_jobs = job["total_jobs"]
        with (
            silence_logger(logging.getLogger("httpx")),
            tqdm(total=num_jobs, desc=f"Running group job {group_job_id}") as pbar,
        ):
            while not job["completed"]:
                job = await self.get_job_group(group_job_id)
                num_failed = job["failed_count"]
                num_success = job["success_count"]
                num_finished = num_failed + num_success
                pbar.n = num_finished
                pbar.refresh()
                await asyncio.sleep(3)
                timeout -= 5
                if timeout <= 0:
                    raise TimeoutError("Timed out waiting for optimize rasters job")
        logger.info(
            f"Group job {group_job_id} finished {job['total_jobs']} jobs, with {num_failed} failures and {num_success} successes"
        )
        return job

    async def get_optimized_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> list[dict]:
        """Retrieve optimized rasters from a data collection with optional filtering.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the optimized rasters.
            params: Optional ListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters.

        Returns:
            list[dict]: A list of optimized raster objects matching the filter criteria.
        """
        params_dict = (
            params.model_dump(exclude_none=True)
            if params
            else ListParams.model_validate(kwargs).model_dump(exclude_none=True)
        )
        response = await self._get(
            f"/projects/{project_id}/data_collections/{data_collection_id}/rasters/optimized/",
            params=params_dict,
        )
        return response.json()

    async def delete_optimized_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        raster_id: int,
        profile: str | None = None,
    ) -> list[dict]:
        """Delete optimized rasters associated with a specific raster.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the raster.
            raster_id: The ID of the raster whose optimized versions should be deleted.
            profile: Optional profile name to filter which optimized rasters to delete.
                    If None, all optimized versions of the raster will be deleted.

        Returns:
            list[dict]: A list of the deleted optimized raster objects.
        """
        params = {}
        if profile:
            params["profile"] = profile
        response = await self._delete(
            f"/projects/{project_id}/data_collections/{data_collection_id}/rasters/{raster_id}/optimized",
            params=params,
        )
        return response.json()

    async def optimize_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        raster_ids: list[int] | None = None,
        profile: str | None = None,
        nearblack: NearblackOptions | None = None,
        overview_resampling: OverviewResampling = "average",
    ) -> list[dict]:
        """Create and run optimization on rasters in a data collection.

        This is a convenience method that combines create_optimized_rasters and run_optimize_rasters
        into a single operation.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the rasters.
            raster_ids: Optional list of raster IDs to optimize. If None, all rasters in the collection will be optimized.
            profile: Optional profile name to use for optimization.
            nearblack: Optional NearblackOptions object for configuring the nearblack process.
            overview_resampling: The resampling method to use for creating overviews. Default is "average".

        Returns:
            list[dict]: List of optimized raster objects after the optimization process has completed.
        """
        optimized_rasters = await self.create_optimized_rasters(
            project_id,
            data_collection_id,
            raster_ids,
            profile,
            nearblack=nearblack,
            overview_resampling=overview_resampling,
        )
        await self.run_optimize_rasters(
            project_id, data_collection_id, [r["id"] for r in optimized_rasters]
        )
        optimized_rasters = await self.get_optimized_rasters(
            project_id,
            data_collection_id,
            params=ListParams(
                ids=[r["id"] for r in optimized_rasters], limit=len(optimized_rasters)
            ),
        )
        return optimized_rasters

    async def list_gdo_users(self) -> list[str]:
        """Retrieve a list of GDO (GeoData Online) users.

        Returns:
            list[dict]: A list of GDO user names.
        """
        response = await self._get("/arcgis_services/gdo-users")
        return response.json()

    async def create_arcgis_service(
        self,
        service_type: Literal["Feature", "Image"],
        create_input: ArcgisServiceCreateInput,
    ) -> dict:
        """Create a new ArcGIS service.

        Args:
            service_type: The type of service to create, either "Feature" or "Image".
            create_input: ArcgisServiceCreateInput object containing the service configuration.

        Returns:
            dict: The created ArcGIS service object.

        Raises:
            AssertionError: If the create_input does not contain the appropriate service options for the specified service_type.
        """
        assert (
            getattr(
                create_input.options, f"{service_type.lower()}_service_options", None
            )
            is not None
        ), (
            f"Service options for {service_type} service must be provided in the create input"
        )
        response = await self._post(
            f"/arcgis_services/{service_type}/",
            json=create_input.model_dump(mode="json"),
        )
        return response.json()

    async def list_arcgis_services(
        self,
        service_type: Literal["Feature", "Image"],
        params: ListParams | None = None,
        **kwargs,
    ) -> list[dict]:
        """List ArcGIS services of a specific type with optional filtering.

        Args:
            service_type: The type of services to list, either "Feature" or "Image".
            params: Optional ListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters.

        Returns:
            list[dict]: A list of ArcGIS service objects matching the filter criteria.
        """
        params_dict = (
            params.model_dump(exclude_none=True)
            if params
            else ListParams.model_validate(kwargs).model_dump(exclude_none=True)
        )
        response = await self._get(
            f"/arcgis_services/{service_type}/", params=params_dict
        )
        return response.json()

    async def get_arcgis_service(
        self, service_type: Literal["Feature", "Image"], service_id: int
    ) -> dict:
        """Retrieve a specific ArcGIS service by its ID.

        Args:
            service_type: The type of service, either "Feature" or "Image".
            service_id: The ID of the service to retrieve.

        Returns:
            dict: The ArcGIS service object with its details.
        """
        response = await self._get(f"/arcgis_services/{service_type}/{service_id}")
        return response.json()

    async def delete_arcgis_service(
        self, service_type: Literal["Feature", "Image"], service_id: int
    ) -> dict:
        """Delete a specific ArcGIS service by its ID.

        Args:
            service_type: The type of service, either "Feature" or "Image".
            service_id: The ID of the service to delete.

        Returns:
            dict: The response confirming deletion.
        """
        response = await self._delete(f"/arcgis_services/{service_type}/{service_id}")
        return response.json()

    async def update_arcgis_service(
        self,
        service_type: Literal["Feature", "Image"],
        service_id: int,
        update_input: ArcgisServiceUpdateInput,
    ) -> dict:
        """Update an existing ArcGIS service with new values.

        Args:
            service_type: The type of service, either "Feature" or "Image".
            service_id: The ID of the service to update.
            update_input: ArcgisServiceUpdateInput object containing the fields to update.

        Returns:
            dict: The updated ArcGIS service object.
        """
        response = await self._put(
            f"/arcgis_services/{service_type}/{service_id}",
            json=update_input.model_dump(mode="json"),
        )
        return response.json()

    async def start_arcgis_service(
        self,
        service_type: Literal["Feature", "Image"],
        service_id: int,
        wait: bool = True,
    ) -> dict:
        """Start a specific ArcGIS service.

        Args:
            service_type: The type of service, either "Feature" or "Image".
            service_id: The ID of the service to start.
            wait: If True, wait for the start operation to complete before returning.
                 If False, return immediately after initiating the start operation.

        Returns:
            dict: A response object containing job information and, if wait is True,
                 the updated service object after starting.
        """
        response = await self._put(
            f"/arcgis_services/{service_type}/{service_id}/start"
        )
        resp = response.json()
        job = resp["job"]
        if wait and job:
            job = await self.wait_for_job(job["job_id"], timeout=1000)
            resp["job"] = job
            resp["arcgis_service"] = await self.get_arcgis_service(
                service_type, service_id
            )
        return resp

    async def stop_arcgis_service(
        self,
        service_type: Literal["Feature", "Image"],
        service_id: int,
        wait: bool = True,
    ) -> dict:
        """Stop a specific ArcGIS service.

        Args:
            service_type: The type of service, either "Feature" or "Image".
            service_id: The ID of the service to stop.
            wait: If True, wait for the stop operation to complete before returning.
                 If False, return immediately after initiating the stop operation.

        Returns:
            dict: A response object containing job information and, if wait is True,
                 the updated service object after stopping.
        """
        response = await self._put(f"/arcgis_services/{service_type}/{service_id}/stop")
        resp = response.json()
        job = resp["job"]
        if wait and job:
            job = await self.wait_for_job(job["job_id"], timeout=1000)
            resp["job"] = job
            resp["arcgis_service"] = await self.get_arcgis_service(
                service_type, service_id
            )
        return resp

    async def refresh_arcgis_service(
        self,
        service_type: Literal["Feature", "Image"],
        service_id: int,
        refresh_data: bool = False,
        wait: bool = True,
    ) -> dict:
        """Refresh a specific ArcGIS service, optionally refreshing its data.

        Args:
            service_type: The type of service, either "Feature" or "Image".
            service_id: The ID of the service to refresh.
            refresh_data: If True, also refresh the data used by the service.
            wait: If True, wait for the refresh operation to complete before returning.
                 If False, return immediately after initiating the refresh operation.

        Returns:
            dict: A response object containing job information and, if wait is True,
                 the updated service object after refreshing.
        """
        response = await self._put(
            f"/arcgis_services/{service_type}/{service_id}/refresh",
            params={"refresh_data": refresh_data},
        )
        resp = response.json()
        job = resp["job"]
        if wait and job:
            job = await self.wait_for_job(job["job_id"], timeout=1000)
            resp["job"] = job
            resp["arcgis_service"] = await self.get_arcgis_service(
                service_type, service_id
            )
        return resp

    async def create_harvest_service(
        self,
        project_id: int,
        data_collection_id: int,
        create_input: HarvestServiceCreateInput,
    ) -> dict:
        """Create a new harvest service for a data collection.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to create the harvest service for.
            create_input: HarvestServiceCreateInput object containing the service configuration.

        Returns:
            dict: The created harvest service object.
        """
        response = await self._post(
            f"/projects/{project_id}/data_collections/{data_collection_id}/harvest_services/",
            json=create_input.model_dump(mode="json"),
            sensitive_content=True,
        )
        return response.json()

    async def list_harvest_services(
        self,
        project_id: int,
        data_collection_id: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> list[dict]:
        """List harvest services for a data collection with optional filtering.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to list harvest services for.
            params: Optional ListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters. Ignored if params is provided.

        Returns:
            list[dict]: A list of harvest service objects matching the filter criteria.
        """
        if params and kwargs:
            logger.warning("Ignoring kwargs when params is provided")
        params_dict = (
            params.model_dump(exclude_none=True)
            if params
            else ListParams.model_validate(kwargs).model_dump(exclude_none=True)
        )
        response = await self._get(
            f"/projects/{project_id}/data_collections/{data_collection_id}/harvest_services/",
            params=params_dict,
        )
        return response.json()

    async def get_harvest_service(
        self, project_id: int, data_collection_id: int, service_id: int
    ) -> dict:
        """Retrieve a specific harvest service by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the harvest service.
            service_id: The ID of the harvest service to retrieve.

        Returns:
            dict: The harvest service object with its details.
        """
        response = await self._get(
            f"/projects/{project_id}/data_collections/{data_collection_id}/harvest_services/{service_id}"
        )
        return response.json()

    async def update_harvest_service(
        self,
        project_id: int,
        data_collection_id: int,
        service_id: int,
        update_input: HarvestServiceUpdateInput,
    ) -> dict:
        """Update an existing harvest service with new values.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the harvest service.
            service_id: The ID of the harvest service to update.
            update_input: HarvestServiceUpdateInput object containing the fields to update.

        Returns:
            dict: The updated harvest service object.
        """
        response = await self._put(
            f"/projects/{project_id}/data_collections/{data_collection_id}/harvest_services/{service_id}",
            json=update_input.model_dump(mode="json", exclude_none=True),
            sensitive_content=True,
        )
        return response.json()

    async def delete_harvest_service(
        self, project_id: int, data_collection_id: int, service_id: int
    ) -> dict:
        """Delete a specific harvest service by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the harvest service.
            service_id: The ID of the harvest service to delete.

        Returns:
            dict: The response confirming deletion.
        """
        response = await self._delete(
            f"/projects/{project_id}/data_collections/{data_collection_id}/harvest_services/{service_id}"
        )
        return response.json()

    async def get_harvest_service_tasks(
        self,
        project_id: int,
        data_collection_id: int,
        service_id: int,
        params: HarvestTaskListParams,
        **kwargs,
    ) -> list[dict]:
        """Retrieve tasks for a specific harvest service with optional filtering.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the harvest service.
            service_id: The ID of the harvest service to retrieve tasks for.
            params: HarvestTaskListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters. Ignored if params is provided.

        Returns:
            list[dict]: A list of harvest task objects matching the filter criteria.
        """
        params_dict = (
            params.model_dump(exclude_none=True)
            if params
            else ListParams.model_validate(kwargs).model_dump(exclude_none=True)
        )
        response = await self._get(
            f"/projects/{project_id}/data_collections/{data_collection_id}/harvest_services/{service_id}/",
            params=params_dict,
        )
        return response.json()

    async def start_harvest_service(
        self, project_id: int, data_collection_id: int, service_id: int
    ) -> dict:
        """Start a specific harvest service.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the harvest service.
            service_id: The ID of the harvest service to start.

        Returns:
            dict: The response confirming the service has been started.
        """
        response = await self._post(
            f"/projects/{project_id}/data_collections/{data_collection_id}/harvest_services/{service_id}/start"
        )
        return response.json()

    async def stop_harvest_service(
        self, project_id: int, data_collection_id: int, service_id: int
    ) -> dict:
        """Stop a specific harvest service.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the harvest service.
            service_id: The ID of the harvest service to stop.

        Returns:
            dict: The response confirming the service has been stopped.
        """
        response = await self._post(
            f"/projects/{project_id}/data_collections/{data_collection_id}/harvest_services/{service_id}/stop"
        )
        return response.json()

    async def create_oidc_user(self, create_input: OIDCUserCreateInput) -> dict:
        """Create a new OIDC user in the system.

        Args:
            create_input: OIDCUserCreateInput object containing the user information.

        Returns:
            dict: The created user object.

        Note:
            This method handles the extraction of the password from the SecretStr field
            in the create_input object.
        """
        model_dump = create_input.model_dump(mode="json")
        response = await self._post(
            "/users/oidc/", json=model_dump, sensitive_content=True
        )
        return response.json()

    async def update_oidc_user(
        self, user_id: int, update_input: OIDCUserUpdateInput
    ) -> dict:
        """Update an existing OIDC user with new values.

        Args:
            user_id: The ID of the user to update.
            update_input: OIDCUserUpdateInput object containing the fields to update.

        Returns:
            dict: The updated user object.

        Note:
            This method handles the extraction of the password from the SecretStr field
            in the update_input object if provided.
        """
        model_dump = update_input.model_dump(mode="json")
        response = await self._put(
            f"/users/oidc/{user_id}/", json=model_dump, sensitive_content=True
        )
        return response.json()

    async def _upload_attachment_to_s3(
        self,
        resource_type: AttachmentResourceType,
        resource_id: int,
        attachment: dict,
        file_path: Path,
    ) -> dict:
        """Upload an attachment file to S3 and mark it as completed.

        Args:
            resource_type: The type of resource the attachment belongs to.
            resource_id: The ID of the resource the attachment belongs to.
            attachment: The attachment object containing upload parameters.
            file_path: Path to the attachment file to upload.

        Returns:
            dict: The updated attachment object.

        Raises:
            AssertionError: If the attachment status is not "Pending".
            httpx.HTTPStatusError: If the upload fails.
        """
        assert attachment["status"] == "Pending", "Attachment status must be pending"
        response = await self._internal_client.post(
            attachment["upload_file_params"]["url"],
            files={"file": file_path.read_bytes()},
            data=attachment["upload_file_params"]["fields"],
        )
        response.raise_for_status()
        # Update the status to completed
        resp = await self._put(
            "/attachments/update",
            params={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "attachment_id": attachment["id"],
                "status": "Completed",
            },
        )
        return resp.json()

    async def list_attachments(
        self,
        resource_type: AttachmentResourceType,
        resource_id: int,
        status: Literal["Pending", "Completed"] | None = None,
    ) -> list[dict]:
        """List attachments for a specific resource with optional status filtering.

        Args:
            resource_type: The type of resource the attachments belong to.
            resource_id: The ID of the resource to list attachments for.
            status: Optional filter for attachment status, either "Pending" or "Completed".

        Returns:
            list[dict]: A list of attachment objects matching the filter criteria.
        """
        params = {"resource_type": resource_type, "resource_id": resource_id}
        if status:
            params["status"] = status
        response = await self._get(
            "/attachments/",
            params=params,
        )
        return response.json()

    async def add_attachments(
        self,
        resource_type: AttachmentResourceType,
        resource_id: int,
        files: list[PixelAttachmentUpload | Path]
        | list[Path]
        | list[PixelAttachmentUpload],
    ) -> list[dict]:
        """Add one or more file attachments to a resource.

        Args:
            resource_type: The type of resource to attach files to.
            resource_id: The ID of the resource to attach files to.
            files: List of files to attach, which can be Path objects or PixelAttachmentUpload objects.

        Returns:
            list[dict]: A list of the created attachment objects.

        Raises:
            AssertionError: If any attachment names are not unique.
        """
        pixel_attachments = [
            PixelAttachmentUpload(
                file=f,
            )
            if isinstance(f, Path)
            else f
            for f in files
        ]
        assert len(set(pa.name for pa in pixel_attachments)) == len(
            pixel_attachments
        ), "Attachment names must be unique"
        response = await self._post(
            "/attachments/",
            params={"resource_type": resource_type, "resource_id": resource_id},
            json={"files": [pa.model_dump(mode="json") for pa in pixel_attachments]},
        )
        attachments = response.json()
        sorted_attachments = sorted(attachments, key=lambda a: a["name"])
        sorted_files = sorted(pixel_attachments, key=lambda f: f.name)
        attachments = await asyncio.gather(
            *[
                self._upload_attachment_to_s3(resource_type, resource_id, a, pa.file)
                for a, pa in zip(sorted_attachments, sorted_files)
            ]
        )
        return attachments

    async def move_attachment(
        self,
        resource_type: AttachmentResourceType,
        resource_id: int,
        attachment_id: int,
        new_resource_type: AttachmentResourceType,
        new_resource_id: int,
    ) -> dict:
        """Move an attachment from one resource to another.

        Args:
            resource_type: The current resource type of the attachment.
            resource_id: The current resource ID the attachment belongs to.
            attachment_id: The ID of the attachment to move.
            new_resource_type: The target resource type to move the attachment to.
            new_resource_id: The target resource ID to move the attachment to.

        Returns:
            dict: The updated attachment object.
        """
        resp = await self._put(
            "/attachments/move",
            params={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "attachment_id": attachment_id,
                "new_resource_type": new_resource_type,
                "new_resource_id": new_resource_id,
            },
        )
        return resp.json()

    async def delete_attachment(
        self,
        resource_type: AttachmentResourceType,
        resource_id: int,
        attachment_id: int,
    ) -> dict:
        """Delete a specific attachment from a resource.

        Args:
            resource_type: The resource type the attachment belongs to.
            resource_id: The resource ID the attachment belongs to.
            attachment_id: The ID of the attachment to delete.

        Returns:
            dict: The response confirming deletion.
        """
        resp = await self._delete(
            "/attachments/",
            params={
                "resource_type": resource_type,
                "resource_id": resource_id,
                "attachment_id": attachment_id,
            },
        )
        return resp.json()
