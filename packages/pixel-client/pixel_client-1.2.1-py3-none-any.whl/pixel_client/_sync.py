from pathlib import Path
from typing import Literal, Iterator
from geojson_pydantic import Polygon
from typing import Self
from pixel_client.models import (
    ArcgisServiceCreateInput,
    ArcgisServiceUpdateInput,
    HarvestServiceCreateInput,
    HarvestServiceUpdateInput,
    HarvestTaskListParams,
    ListParams,
    OIDCUserCreateInput,
    OIDCUserUpdateInput,
    PixelUploadFile,
    RasterInfo,
    NearblackOptions,
    PixelAttachmentUpload,
    DataCollectionListParams,
    ImageUpdateInput,
    RasterUpdateInput,
)
from .types import AttachmentResourceType, OverviewResampling
from .exceptions import PixelUploadJobError
from .utils import run_sync, iter_over_async
from ._base import (
    PixelClientAsync,
    PixelApiSettings,
)


class PixelClient:
    """
    Synchronous client for the Pixel API.

    This client provides methods for working with projects, data collections, images,
    rasters, and other resources in the Pixel system. It handles authentication,
    request management, and provides high-level operations for common tasks.
    """

    def __init__(self, async_client: PixelClientAsync):
        """
        Initialize the synchronous Pixel client with an asynchronous client.

        Args:
            async_client: An instance of PixelClientAsync to handle asynchronous operations.
        """
        self._async_client = async_client

    @classmethod
    def from_settings(cls, settings: PixelApiSettings, **kwargs) -> Self:
        """
        Instantiate the client from settings.

        Args:
            settings: PixelApiSettings object containing API configuration.
            **kwargs: Additional keyword arguments to pass to the client constructor.

        Returns:
            PixelClient: A new client instance configured with the provided settings.
        """
        return cls(PixelClientAsync.from_settings(settings, **kwargs))

    def __enter__(self) -> Self:
        """
        Enter the context manager, returning the client instance.

        Returns:
            PixelClient: The client instance itself.
        """
        run_sync(self._async_client.__aenter__())
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """
        Exit the context manager, cleaning up resources.

        Args:
            exc_type: The type of exception raised, if any.
            exc_value: The value of the exception raised, if any.
            traceback: The traceback object, if any.
        """
        run_sync(self._async_client.__aexit__(exc_type, exc_value, traceback))

    def me(self, extended: bool = False) -> dict:
        """
        Get information about the authenticated user.

        Args:
            extended: If True, returns extended user information including projects user is a member of

        Returns:
            dict: User information including username, email, and other profile details.
        """
        return run_sync(self._async_client.me(extended))

    def get_plugins(self) -> list[dict]:
        """
        Retrieve a list of available plugins for the pixel tenant.
        Possible plugins include:
        * 'optimized_raster' - Optimize Raster capability
        * 'image_service' - Image Service capability, dependent on the 'optimize_raster' plugin.

        Returns:
            list[dict]: A list of plugin objects with their details.
        """
        return run_sync(self._async_client.get_plugins())

    def create_project(
        self,
        name: str,
        description: str,
        area_of_interest: Polygon,
        parent_project_id: int | None = None,
        tags: list[str] | None = None,
    ) -> dict:
        """
        Create a new project in the Pixel system.

        Args:
            name: The name of the project.
            description: A description of the project.
            area_of_interest: A GeoJSON polygon defining the project's geographic area of interest.
            parent_project_id: Optional ID of a parent project. If provided, this project will be created as a child of that project.
            tags: Optional list of tags to associate with the project.

        Returns:
            dict: The created project object.
        """
        return run_sync(
            self._async_client.create_project(
                name, description, area_of_interest, parent_project_id, tags
            )
        )

    def update_project(
        self,
        project_id: int,
        name: str | None = None,
        description: str | None = None,
        area_of_interest: Polygon | None = None,
        add_tags: list[str] | None = None,
        remove_tags: list[str] | None = None,
    ) -> dict:
        """
        Update an existing project with new values.

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
        return run_sync(
            self._async_client.update_project(
                project_id, name, description, area_of_interest, add_tags, remove_tags
            )
        )

    def get_project(self, project_id: int, extended: bool = False) -> dict:
        """Retrieve a project by its ID.

        Args:
            project_id: The ID of the project to retrieve.
            extended: If True, returns extended project information including child projects and data collections.

        Returns:
            dict: The project object with its details.
        """
        return run_sync(self._async_client.get_project(project_id, extended))

    def delete_project(self, project_id: int) -> dict:
        """Delete a project by its ID.

        Args:
            project_id: The ID of the project to delete.

        Returns:
            dict: The response confirming deletion.
        """
        return run_sync(self._async_client.delete_project(project_id))

    def restore_project(self, project_id: int) -> dict:
        """Restore a deleted project by its ID.

        Args:
            project_id: The ID of the project to restore.

        Returns:
            dict: The restored project object.
        """
        return run_sync(self._async_client.restore_project(project_id))

    def list_projects(self, params: ListParams | None = None, **kwargs) -> list[dict]:
        """List projects with optional filtering.

        Args:
            params: Optional ListParams object containing filtering parameters such as offset, limit, search, etc.
            **kwargs: Alternative way to provide filtering parameters. Ignored if params is provided.

        Returns:
            list[dict]: A list of project objects matching the filter criteria.
        """
        return run_sync(self._async_client.list_projects(params, **kwargs))

    def list_deleted_projects(
        self, params: ListParams | None = None, **kwargs
    ) -> list[dict]:
        """List deleted projects in the Pixel system.

        Args:
            params: Optional ListParams object containing filtering parameters such as offset, limit, search, etc.
            **kwargs: Alternative way to provide filtering parameters. Ignored if params is provided.

        Returns:
            list[dict]: A list of deleted project objects.
        """
        return run_sync(self._async_client.list_deleted_projects(params, **kwargs))

    def move_project(
        self, project_id: int, new_parent_project_id: int | None = None
    ) -> dict:
        """Move a project to a new parent project or to the root level.

        Args:
            project_id: The ID of the project to move.
            new_parent_project_id: Optional ID of the new parent project. If None, the project will be moved to the root level.

        Returns:
            dict: The updated project object.
        """
        return run_sync(
            self._async_client.move_project(project_id, new_parent_project_id)
        )

    def create_data_collection(
        self,
        project_id: int,
        name: str,
        description: str,
        data_collection_type: Literal["image", "raster", "RGB", "DTM", "DSM"],
        tags: list[str] | None = None,
        raster_info: RasterInfo | None = None,
    ) -> dict:
        """
        Create a new data collection within a project.

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

        return run_sync(
            self._async_client.create_data_collection(
                project_id, name, description, data_collection_type, tags, raster_info
            )
        )

    def update_data_collection(
        self,
        project_id: int,
        data_collection_id: int,
        name: str | None = None,
        description: str | None = None,
        add_tags: list[str] | None = None,
        remove_tags: list[str] | None = None,
    ) -> dict:
        """
        Update an existing data collection with new values.

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

        return run_sync(
            self._async_client.update_data_collection(
                project_id, data_collection_id, name, description, add_tags, remove_tags
            )
        )

    def get_data_collection(self, project_id: int, data_collection_id: int) -> dict:
        """
        Retrieve a data collection by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to retrieve.

        Returns:
            dict: The data collection object with its details.
        """
        return run_sync(
            self._async_client.get_data_collection(project_id, data_collection_id)
        )

    def list_data_collections(
        self, project_id: int, params: DataCollectionListParams | None = None, **kwargs
    ) -> list[dict]:
        """
        List data collections within a project with optional filtering.

        Args:
            project_id: The ID of the project to list data collections from.
            params: Optional DataCollectionListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters. Ignored if params is provided.

        Returns:
            list[dict]: A list of data collection objects matching the filter criteria.
        """
        return run_sync(
            self._async_client.list_data_collections(project_id, params, **kwargs)
        )

    def list_deleted_data_collections(
        self, project_id: int, params: DataCollectionListParams | None = None, **kwargs
    ) -> list[dict]:
        """List deleted data collections within a project.

        Args:
            project_id: The ID of the project to list deleted data collections from.

        Returns:
            list[dict]: A list of deleted data collection objects.
        """
        return run_sync(
            self._async_client.list_deleted_data_collections(
                project_id, params, **kwargs
            )
        )

    def delete_data_collection(self, project_id: int, data_collection_id: int) -> dict:
        """
        Delete a data collection by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to delete.

        Returns:
            dict: The response confirming deletion.
        """
        return run_sync(
            self._async_client.delete_data_collection(project_id, data_collection_id)
        )

    def restore_data_collection(self, project_id: int, data_collection_id: int) -> dict:
        """Restore a deleted data collection by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to restore.

        Returns:
            dict: The restored data collection object.
        """
        return run_sync(
            self._async_client.restore_data_collection(project_id, data_collection_id)
        )

    def move_data_collection(
        self, project_id: int, data_collection_id: int, new_project_id: int
    ) -> dict:
        """
        Move a data collection to a different project.

        Args:
            project_id: The ID of the project currently containing the data collection.
            data_collection_id: The ID of the data collection to move.
            new_project_id: The ID of the project to move the data collection to.

        Returns:
            dict: The updated data collection object.
        """
        return run_sync(
            self._async_client.move_data_collection(
                project_id, data_collection_id, new_project_id
            )
        )

    def get_images(
        self,
        project_id: int,
        data_collection_id: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> dict:
        """
        Retrieve images from a data collection with optional filtering.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the images.
            params: Optional ListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters.

        Returns:
            dict: A list of image objects matching the filter criteria.
        """
        return run_sync(
            self._async_client.get_images(
                project_id, data_collection_id, params, **kwargs
            )
        )

    def paginate_images(
        self,
        project_id: int,
        data_collection_id: int,
        page_size: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> Iterator[dict]:
        """
        Paginate through images in a data collection with optional filtering.

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
        return iter_over_async(
            self._async_client.paginate_images(
                project_id,
                data_collection_id,
                page_size,
                params,
                **kwargs,
            )
        )

    def get_image(
        self, project_id: int, data_collection_id: int, image_id: int
    ) -> dict:
        """
        Retrieve a specific image by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the image.
            image_id: The ID of the image to retrieve.

        Returns:
            dict: The image object with its details.
        """
        return run_sync(
            self._async_client.get_image(project_id, data_collection_id, image_id)
        )

    def get_image_metadata(
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
        return run_sync(
            self._async_client.get_image_metadata(
                project_id, data_collection_id, image_id
            )
        )

    def update_image(
        self,
        project_id: int,
        data_collection_id: int,
        image_id: int,
        update_input: ImageUpdateInput,
    ) -> dict:
        """
        Update an existing image with new values.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the image.
            image_id: The ID of the image to update.
            update_input: ImageUpdateInput object containing the fields to update.

        Returns:
            dict: The updated image object.
        """
        return run_sync(
            self._async_client.update_image(
                project_id, data_collection_id, image_id, update_input
            )
        )

    def delete_image(
        self, project_id: int, data_collection_id: int, image_id: int
    ) -> dict:
        """
        Delete a specific image by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the image.
            image_id: The ID of the image to delete.

        Returns:
            dict: The response confirming deletion.
        """
        return run_sync(
            self._async_client.delete_image(project_id, data_collection_id, image_id)
        )

    def get_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> dict:
        """
        Retrieve rasters from a data collection with optional filtering.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the rasters.
            params: Optional ListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters.

        Returns:
            dict: A list of raster objects matching the filter criteria.
        """
        return run_sync(
            self._async_client.get_rasters(
                project_id, data_collection_id, params, **kwargs
            )
        )

    def paginate_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        page_size: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> Iterator[dict]:
        """
        Paginate through rasters in a data collection with optional filtering.

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
        return iter_over_async(
            self._async_client.paginate_rasters(
                project_id,
                data_collection_id=data_collection_id,
                page_size=page_size,
                params=params,
                **kwargs,
            )
        )

    def get_raster(
        self, project_id: int, data_collection_id: int, raster_id: int
    ) -> dict:
        """
        Retrieve a specific raster by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the raster.
            raster_id: The ID of the raster to retrieve.

        Returns:
            dict: The raster object with its details.
        """
        return run_sync(
            self._async_client.get_raster(project_id, data_collection_id, raster_id)
        )

    def update_raster(
        self,
        project_id: int,
        data_collection_id: int,
        raster_id: int,
        update_input: RasterUpdateInput,
    ) -> dict:
        """
        Update an existing raster with new values.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the raster.
            raster_id: The ID of the raster to update.
            update_input: RasterUpdateInput object containing the fields to update.

        Returns:
            dict: The updated raster object.
        """
        return run_sync(
            self._async_client.update_raster(
                project_id, data_collection_id, raster_id, update_input
            )
        )

    def delete_raster(
        self, project_id: int, data_collection_id: int, raster_id: int
    ) -> dict:
        """
        Delete a specific raster by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the raster.
            raster_id: The ID of the raster to delete.

        Returns:
            dict: The response confirming deletion.
        """

        return run_sync(
            self._async_client.delete_raster(project_id, data_collection_id, raster_id)
        )

    def get_upload_jobs(
        self,
        project_id: int,
        data_collection_id: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> list[dict]:
        """
        Retrieve upload jobs for a data collection with optional filtering.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to list upload jobs for.
            params: Optional ListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters. Ignored if params is provided.

        Returns:
            list[dict]: A list of upload job objects matching the filter criteria.
        """
        return run_sync(
            self._async_client.get_upload_jobs(
                project_id, data_collection_id, params, **kwargs
            )
        )

    def upload_image(
        self,
        project_id: int,
        data_collection_id: int,
        file_path: Path,
        metadata: dict | None = None,
        support_files: list[Path] | None = None,
        multipart: bool = False,
        multipart_part_size: int | None = None,
    ) -> dict:
        """
        Upload an image file to an image data collection.

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
        return run_sync(
            self._async_client.upload_image(
                project_id,
                data_collection_id,
                file_path,
                metadata,
                support_files,
                multipart,
                multipart_part_size,
            )
        )

    def upload_multiple_images(
        self,
        project_id: int,
        data_collection_id: int,
        files: list[PixelUploadFile],
        multipart: bool = False,
        multipart_part_size: int | None = None,
    ) -> tuple[list[dict], list[PixelUploadJobError]]:
        """
        Upload multiple image files to an image data collection.

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
        return run_sync(
            self._async_client.upload_multiple_images(
                project_id, data_collection_id, files, multipart, multipart_part_size
            )
        )

    def upload_raster(
        self,
        project_id: int,
        data_collection_id: int,
        file_path: Path,
        support_files: list[Path] | None = None,
        multipart: bool = False,
        multipart_part_size: int | None = None,
    ) -> dict:
        """
        Upload a raster file to a raster data collection.

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
        return run_sync(
            self._async_client.upload_raster(
                project_id,
                data_collection_id,
                file_path,
                support_files,
                multipart,
                multipart_part_size,
            )
        )

    def upload_multiple_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        files: list[PixelUploadFile],
        multipart: bool = False,
        multipart_part_size: int | None = None,
    ) -> tuple[list[dict], list[PixelUploadJobError]]:
        """
        Upload multiple raster files to a raster data collection.

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
        return run_sync(
            self._async_client.upload_multiple_rasters(
                project_id, data_collection_id, files, multipart, multipart_part_size
            )
        )

    def create_optimized_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        raster_ids: list[int] | None,
        profile: str | None = None,
        nearblack: NearblackOptions | None = None,
        overview_resampling: OverviewResampling = "average",
    ) -> list[dict]:
        """
        Create optimized raster objects in the database.

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
        return run_sync(
            self._async_client.create_optimized_rasters(
                project_id,
                data_collection_id,
                raster_ids,
                profile,
                nearblack,
                overview_resampling,
            )
        )

    def get_optimized_rasters(
        self, project_id: int, data_collection_id: int, params: ListParams, **kwargs
    ) -> list[dict]:
        """
        Retrieve optimized rasters from a data collection with optional filtering.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the optimized rasters.
            params: Optional ListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters.

        Returns:
            list[dict]: A list of optimized raster objects matching the filter criteria.
        """
        return run_sync(
            self._async_client.get_optimized_rasters(
                project_id, data_collection_id, params, **kwargs
            )
        )

    def delete_optimized_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        raster_id: int,
        profile: str | None = None,
    ) -> list[dict]:
        """
        Delete optimized rasters associated with a specific raster.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the raster.
            raster_id: The ID of the raster whose optimized versions should be deleted.
            profile: Optional profile name to filter which optimized rasters to delete.
                    If None, all optimized versions of the raster will be deleted.

        Returns:
            list[dict]: A list of the deleted optimized raster objects.
        """
        return run_sync(
            self._async_client.delete_optimized_rasters(
                project_id, data_collection_id, raster_id, profile
            )
        )

    def optimize_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        raster_ids: list[int] | None = None,
        profile: str | None = None,
        nearblack: NearblackOptions | None = None,
        overview_resampling: OverviewResampling = "average",
    ) -> list[dict]:
        """
        Create and run optimization on rasters in a data collection.

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
        return run_sync(
            self._async_client.optimize_rasters(
                project_id,
                data_collection_id,
                raster_ids,
                profile,
                nearblack,
                overview_resampling,
            )
        )

    def run_optimize_rasters(
        self,
        project_id: int,
        data_collection_id: int,
        optimize_raster_ids: list[int] | None,
        retry_failed: bool = False,
    ) -> dict:
        """
        Run the optimization process on optimized raster objects.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the optimized rasters.
            optimize_raster_ids: Optional list of optimized raster IDs to process. If None, all optimized rasters in the collection will be processed.
            retry_failed: If True, retry previously failed optimization jobs.

        Returns:
            dict: The group job object representing the optimization process.
        """
        return run_sync(
            self._async_client.run_optimize_rasters(
                project_id, data_collection_id, optimize_raster_ids, retry_failed
            )
        )

    def get_job(self, job_id: int) -> dict:
        """
        Retrieve information about a specific job.

        Args:
            job_id: The ID of the job to retrieve.

        Returns:
            dict: The job object with its details.
        """
        return run_sync(self._async_client.get_job(job_id))

    def get_job_group(self, job_id: int) -> dict:
        """
        Retrieve information about a specific job group.

        Args:
            job_id: The ID of the job group to retrieve.

        Returns:
            dict: The job group object with its details.
        """
        return run_sync(self._async_client.get_job_group(job_id))

    def wait_for_job(self, job_id: int, timeout: int = 600) -> dict:
        """
        Wait for a job to complete, polling its status at regular intervals.

        Args:
            job_id: The ID of the job to wait for.
            timeout: Maximum time to wait in seconds before raising a TimeoutError. Default is 600 seconds (10 minutes).

        Returns:
            dict: The completed job object.

        Raises:
            TimeoutError: If the job does not complete within the specified timeout period.
        """
        return run_sync(self._async_client.wait_for_job(job_id, timeout))

    def wait_for_group_job(self, group_job_id: int, timeout: int = 1200) -> dict:
        """
        Wait for a group job to complete, polling its status at regular intervals.

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
        return run_sync(self._async_client.wait_for_group_job(group_job_id, timeout))

    def list_gdo_users(self) -> list[str]:
        """
        Retrieve a list of GDO (GeoData Online) users.

        Returns:
            list[dict]: A list of GDO user names.
        """
        return run_sync(self._async_client.list_gdo_users())

    def create_arcgis_service(
        self,
        service_type: Literal["Feature", "Image"],
        create_input: ArcgisServiceCreateInput,
    ) -> dict:
        """
        Create a new ArcGIS service.

        Args:
            service_type: The type of service to create, either "Feature" or "Image".
            create_input: ArcgisServiceCreateInput object containing the service configuration.

        Returns:
            dict: The created ArcGIS service object.

        Raises:
            AssertionError: If the create_input does not contain the appropriate service options for the specified service_type.
        """
        return run_sync(
            self._async_client.create_arcgis_service(service_type, create_input)
        )

    def list_arcgis_services(
        self,
        service_type: Literal["Feature", "Image"],
        params: ListParams | None = None,
        **kwargs,
    ) -> list[dict]:
        """
        List ArcGIS services of a specific type with optional filtering.

        Args:
            service_type: The type of services to list, either "Feature" or "Image".
            params: Optional ListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters.

        Returns:
            list[dict]: A list of ArcGIS service objects matching the filter criteria.
        """
        return run_sync(
            self._async_client.list_arcgis_services(service_type, params, **kwargs)
        )

    def get_arcgis_service(
        self, service_type: Literal["Feature", "Image"], service_id: int
    ) -> dict:
        """
        Retrieve a specific ArcGIS service by its ID.

        Args:
            service_type: The type of service, either "Feature" or "Image".
            service_id: The ID of the service to retrieve.

        Returns:
            dict: The ArcGIS service object with its details.
        """
        return run_sync(self._async_client.get_arcgis_service(service_type, service_id))

    def delete_arcgis_service(
        self, service_type: Literal["Feature", "Image"], service_id: int
    ) -> dict:
        """
        Delete a specific ArcGIS service by its ID.

        Args:
            service_type: The type of service, either "Feature" or "Image".
            service_id: The ID of the service to delete.

        Returns:
            dict: The response confirming deletion.
        """
        return run_sync(
            self._async_client.delete_arcgis_service(service_type, service_id)
        )

    def update_arcgis_service(
        self,
        service_type: Literal["Feature", "Image"],
        service_id: int,
        update_input: ArcgisServiceUpdateInput,
    ) -> dict:
        """
        Update an existing ArcGIS service with new values.

        Args:
            service_type: The type of service, either "Feature" or "Image".
            service_id: The ID of the service to update.
            update_input: ArcgisServiceUpdateInput object containing the fields to update.

        Returns:
            dict: The updated ArcGIS service object.
        """
        return run_sync(
            self._async_client.update_arcgis_service(
                service_type, service_id, update_input
            )
        )

    def start_arcgis_service(
        self,
        service_type: Literal["Feature", "Image"],
        service_id: int,
        wait: bool = True,
    ) -> dict:
        """
        Start a specific ArcGIS service.

        Args:
            service_type: The type of service, either "Feature" or "Image".
            service_id: The ID of the service to start.
            wait: If True, wait for the start operation to complete before returning.
                 If False, return immediately after initiating the start operation.

        Returns:
            dict: A response object containing job information and, if wait is True,
                 the updated service object after starting.
        """
        return run_sync(
            self._async_client.start_arcgis_service(service_type, service_id, wait)
        )

    def stop_arcgis_service(
        self,
        service_type: Literal["Feature", "Image"],
        service_id: int,
        wait: bool = True,
    ) -> dict:
        """
        Stop a specific ArcGIS service.

        Args:
            service_type: The type of service, either "Feature" or "Image".
            service_id: The ID of the service to stop.
            wait: If True, wait for the stop operation to complete before returning.
                 If False, return immediately after initiating the stop operation.

        Returns:
            dict: A response object containing job information and, if wait is True,
                 the updated service object after stopping.
        """
        return run_sync(
            self._async_client.stop_arcgis_service(service_type, service_id, wait)
        )

    def refresh_arcgis_service(
        self,
        service_type: Literal["Feature", "Image"],
        service_id: int,
        refresh_data: bool = False,
        wait: bool = True,
    ) -> dict:
        """
        Refresh a specific ArcGIS service, optionally refreshing its data.

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
        return run_sync(
            self._async_client.refresh_arcgis_service(
                service_type, service_id, refresh_data, wait
            )
        )

    def create_harvest_service(
        self,
        project_id: int,
        data_collection_id: int,
        create_input: HarvestServiceCreateInput,
    ) -> dict:
        """
        Create a new harvest service for a data collection.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to create the harvest service for.
            create_input: HarvestServiceCreateInput object containing the service configuration.

        Returns:
            dict: The created harvest service object.
        """

        return run_sync(
            self._async_client.create_harvest_service(
                project_id, data_collection_id, create_input
            )
        )

    def list_harvest_services(
        self,
        project_id: int,
        data_collection_id: int,
        params: ListParams | None = None,
        **kwargs,
    ) -> list[dict]:
        """
        List harvest services for a data collection with optional filtering.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection to list harvest services for.
            params: Optional ListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters. Ignored if params is provided.

        Returns:
            list[dict]: A list of harvest service objects matching the filter criteria.
        """

        return run_sync(
            self._async_client.list_harvest_services(
                project_id, data_collection_id, params, **kwargs
            )
        )

    def get_harvest_service(
        self, project_id: int, data_collection_id: int, service_id: int
    ) -> dict:
        """
        Retrieve a specific harvest service by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the harvest service.
            service_id: The ID of the harvest service to retrieve.

        Returns:
            dict: The harvest service object with its details.
        """

        return run_sync(
            self._async_client.get_harvest_service(
                project_id, data_collection_id, service_id
            )
        )

    def update_harvest_service(
        self,
        project_id: int,
        data_collection_id: int,
        service_id: int,
        update_input: HarvestServiceUpdateInput,
    ) -> dict:
        """
        Update an existing harvest service with new values.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the harvest service.
            service_id: The ID of the harvest service to update.
            update_input: HarvestServiceUpdateInput object containing the fields to update.

        Returns:
            dict: The updated harvest service object.
        """

        return run_sync(
            self._async_client.update_harvest_service(
                project_id, data_collection_id, service_id, update_input
            )
        )

    def delete_harvest_service(
        self, project_id: int, data_collection_id: int, service_id: int
    ) -> dict:
        """
        Delete a specific harvest service by its ID.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the harvest service.
            service_id: The ID of the harvest service to delete.

        Returns:
            dict: The response confirming deletion.
        """
        return run_sync(
            self._async_client.delete_harvest_service(
                project_id, data_collection_id, service_id
            )
        )

    def get_harvest_service_tasks(
        self,
        project_id: int,
        data_collection_id: int,
        service_id: int,
        params: HarvestTaskListParams,
        **kwargs,
    ) -> list[dict]:
        """
        Retrieve tasks for a specific harvest service with optional filtering.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the harvest service.
            service_id: The ID of the harvest service to retrieve tasks for.
            params: HarvestTaskListParams object containing filtering parameters.
            **kwargs: Alternative way to provide filtering parameters. Ignored if params is provided.

        Returns:
            list[dict]: A list of harvest task objects matching the filter criteria.
        """

        return run_sync(
            self._async_client.get_harvest_service_tasks(
                project_id, data_collection_id, service_id, params, **kwargs
            )
        )

    def start_harvest_service(
        self, project_id: int, data_collection_id: int, service_id: int
    ) -> dict:
        """
        Start a specific harvest service.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the harvest service.
            service_id: The ID of the harvest service to start.

        Returns:
            dict: The response confirming the service has been started.
        """

        return run_sync(
            self._async_client.start_harvest_service(
                project_id, data_collection_id, service_id
            )
        )

    def stop_harvest_service(
        self, project_id: int, data_collection_id: int, service_id: int
    ) -> dict:
        """
        Stop a specific harvest service.

        Args:
            project_id: The ID of the project containing the data collection.
            data_collection_id: The ID of the data collection containing the harvest service.
            service_id: The ID of the harvest service to stop.

        Returns:
            dict: The response confirming the service has been stopped.
        """

        return run_sync(
            self._async_client.stop_harvest_service(
                project_id, data_collection_id, service_id
            )
        )

    def create_oidc_user(self, create_input: OIDCUserCreateInput) -> dict:
        """
        Create a new OIDC user in the system.

        Args:
            create_input: OIDCUserCreateInput object containing the user information.

        Returns:
            dict: The created user object.

        Note:
            This method handles the extraction of the password from the SecretStr field
            in the create_input object.
        """

        return run_sync(self._async_client.create_oidc_user(create_input))

    def update_oidc_user(self, user_id: int, update_input: OIDCUserUpdateInput) -> dict:
        """
        Update an existing OIDC user with new values.

        Args:
            user_id: The ID of the user to update.
            update_input: OIDCUserUpdateInput object containing the fields to update.

        Returns:
            dict: The updated user object.

        Note:
            This method handles the extraction of the password from the SecretStr field
            in the update_input object if provided.
        """

        return run_sync(self._async_client.update_oidc_user(user_id, update_input))

    def list_attachments(
        self,
        resource_type: AttachmentResourceType,
        resource_id: int,
        status: Literal["Pending", "Completed"] | None = None,
    ) -> list[dict]:
        """
        List attachments for a specific resource with optional status filtering.

        Args:
            resource_type: The type of resource the attachments belong to.
            resource_id: The ID of the resource to list attachments for.
            status: Optional filter for attachment status, either "Pending" or "Completed".

        Returns:
            list[dict]: A list of attachment objects matching the filter criteria.
        """

        return run_sync(
            self._async_client.list_attachments(resource_type, resource_id, status)
        )

    def add_attachments(
        self,
        resource_type: AttachmentResourceType,
        resource_id: int,
        files: list[PixelAttachmentUpload | Path]
        | list[Path]
        | list[PixelAttachmentUpload],
    ) -> list[dict]:
        """
        Add one or more file attachments to a resource.

        Args:
            resource_type: The type of resource to attach files to.
            resource_id: The ID of the resource to attach files to.
            files: List of files to attach, which can be Path objects or PixelAttachmentUpload objects.

        Returns:
            list[dict]: A list of the created attachment objects.

        Raises:
            AssertionError: If any attachment names are not unique.
        """

        return run_sync(
            self._async_client.add_attachments(resource_type, resource_id, files)
        )

    def move_attachment(
        self,
        resource_type: AttachmentResourceType,
        resource_id: int,
        attachment_id: int,
        new_resource_type: AttachmentResourceType,
        new_resource_id: int,
    ) -> dict:
        """
        Move an attachment from one resource to another.

        Args:
            resource_type: The current resource type of the attachment.
            resource_id: The current resource ID the attachment belongs to.
            attachment_id: The ID of the attachment to move.
            new_resource_type: The target resource type to move the attachment to.
            new_resource_id: The target resource ID to move the attachment to.

        Returns:
            dict: The updated attachment object.
        """

        return run_sync(
            self._async_client.move_attachment(
                resource_type,
                resource_id,
                attachment_id,
                new_resource_type,
                new_resource_id,
            )
        )

    def delete_attachment(
        self,
        resource_type: AttachmentResourceType,
        resource_id: int,
        attachment_id: int,
    ) -> dict:
        """
        Delete a specific attachment from a resource.

        Args:
            resource_type: The resource type the attachment belongs to.
            resource_id: The resource ID the attachment belongs to.
            attachment_id: The ID of the attachment to delete.

        Returns:
            dict: The response confirming deletion.
        """

        return run_sync(
            self._async_client.delete_attachment(
                resource_type, resource_id, attachment_id
            )
        )
