import datetime
from enum import StrEnum
from functools import cached_property
from pathlib import Path
from typing import Annotated, Literal, Self, Union

from annotated_types import Ge, Len, Lt
from pydantic import (
    BaseModel,
    Discriminator,
    EmailStr,
    Field,
    PlainSerializer,
    SecretStr,
    computed_field,
    field_serializer,
    model_validator,
)

from .types import DataCollectionType
from .utils import calculate_md5_base64_from_file

__all__ = [
    "ArcgisServiceCreateInput",
    "OIDCUserCreateInput",
    "HarvestServiceCreateInput",
    "HarvestServiceUpdateInput",
    "MetadataObject",
    "HarvestFieldMapping",
    "HarvestFieldMap",
    "HarvestFieldMapUpdate",
    "HarvestAuthInfo",
    "FieldMapsUpdateInput",
    "ArcGISFeatureServiceImageLayerOptions",
    "ArcGISFeatureServiceProjectLayerOptions",
    "OIDCUserUpdateInput",
    "ArcgisServiceUpdateInput",
    "ArcgisServiceCreateOptions",
    "PixelUploadFile",
    "PixelAttachmentUpload",
    "MetadataObject",
    "ImageMetadataFields",
    "RasterMetadataFields",
    "MetadataFieldsType",
    "ArcGISFeatureServiceOptions",
    "ListParams",
    "DataCollectionListParams",
    "NearblackOptions",
    "RasterInfo",
    "ImageUpdateInput",
    "RasterUpdateInput",
    "ArcGISImageServiceOptions",
    "ArcGISImageServiceWMSOptions",
]

CommaSeperatedString = str
CommaSeperatedInt = str


def _serialize_to_comma_sep_list(value: list | None) -> str | None:
    if not value:
        return None
    return ",".join(str(v) for v in value)


class OIDCUserCreateInput(BaseModel):
    """Input model for creating a new OIDC user."""

    first_name: str
    last_name: str
    email: EmailStr
    password: SecretStr
    enabled: bool = True
    user_type: Literal["creator", "superuser", "viewer"]

    @field_serializer("password", when_used="json")
    def dump_secret(self, v: SecretStr) -> str:
        """Serialize the password field to a string."""
        return v.get_secret_value()


class OIDCUserUpdateInput(BaseModel):
    """Input model for updating an OIDC user."""

    first_name: str | None = None
    last_name: str | None = None
    password: SecretStr | None = None
    enabled: bool = True
    user_type: Literal["creator", "superuser", "viewer"] | None = None

    @field_serializer("password", when_used="json")
    def dump_secret(self, v: SecretStr | None) -> str | None:
        """
        Serialize the password field to a string.
        """
        if v is None:
            return None
        return v.get_secret_value()


class PixelStatusEnum(StrEnum):
    """
    Enum for the status of a pixel task.
    """

    pending = "pending"
    submitted = "submitted"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class NearblackOptions(BaseModel):
    """
    Options for applying nearblack when optimizing raster images.
    """

    enabled: bool
    color: Literal["black", "white"] | Annotated[int, Ge(0), Lt(256)] = "black"
    algorithm: Literal["floodfill", "twopasses"] = "twopasses"


class ListParams(BaseModel):
    extended: bool | None = None
    name: str | None = None
    ids: (
        Annotated[list[int] | None, PlainSerializer(_serialize_to_comma_sep_list)]
        | None
    ) = None
    tags: Annotated[list[str] | None, PlainSerializer(_serialize_to_comma_sep_list)] = (
        None
    )
    offset: int | None = None
    limit: int | None = None


class DataCollectionListParams(ListParams):
    data_collection_type: DataCollectionType | None = None


class HarvestTaskListParams(ListParams):
    status: PixelStatusEnum | None = None
    get_new: bool | None = None


class ImageMetadataFields(BaseModel):
    fields_type: Literal["image"] = "image"
    image_type: str | None = None
    name: str | None = None
    location: dict | None = None
    cam_heading: float | None = None
    cam_pitch: float | None = None
    cam_roll: float | None = None
    hfov: float | None = None
    vfov: float | None = None
    far_dist: float | None = None
    near_dist: float | None = None
    capture_date: datetime.datetime | None = None
    cam_height: float | None = None
    img_rotation: float | None = None
    cam_orientation: str | None = None
    focal_length: float | None = None
    radial: str | None = None


class RasterMetadataFields(BaseModel):
    fields_type: Literal["raster"] = "raster"
    name: str | None = None
    capture_date: datetime.datetime | None = None


MetadataFieldsType = Annotated[
    Union[ImageMetadataFields, RasterMetadataFields], Discriminator("fields_type")
]


class MetadataObject(BaseModel):
    fields: MetadataFieldsType | None = None
    json_metadata: dict[str, str | float | int | None] | None = None


class PixelUploadFile(BaseModel):
    """
    Model for uploading a file to Pixel
    """

    file: Path
    support_files: list[Path] | None = None
    metadata: MetadataObject | None = None


class PixelAttachmentUpload(BaseModel):
    """
    Model for uploading an attachment to a Pixel object
    """

    file: Path = Field(exclude=True)
    name: str = ""
    description: str = ""

    @model_validator(mode="after")
    def fill_values(self) -> Self:
        if not self.name:
            # Set the name to the file name if not defined
            self.name = self.file.name
        return self

    @computed_field
    @cached_property
    def md5(self) -> str:
        return calculate_md5_base64_from_file(self.file)


class RasterInfo(BaseModel):
    """
    Model for raster information, used for creating a raster data collection.
    """

    srid: int | None = None
    format: str | None = None
    data_type: str | None = None
    cell_size: tuple[float, float] | None = None
    num_bands: int | None = None


class ApiKey(BaseModel):
    """
    Model for API key authentication
    """

    api_key: SecretStr
    api_key_item_id: str | None = None

    @field_serializer("api_key", when_used="json")
    def dump_secret(self, v: SecretStr) -> str:
        """
        Serialize the API key field to a string.
        """
        return v.get_secret_value()


class Credentials(BaseModel):
    """
    Model for credentials authentication
    """

    username: str
    password: SecretStr
    token_url: str | None = None

    @field_serializer("password", when_used="json")
    def dump_secret(self, v: SecretStr) -> str:
        """
        Serialize the password field to a string.
        """
        return v.get_secret_value()


class HarvestAuthInfo(BaseModel):
    """
    Model for harvest service authentication information.
    """

    credentials: Credentials | None = None
    api_key: ApiKey | None = None


class HarvestFieldMap(BaseModel):
    model: str
    field_name: str
    external_field: str


class HarvestFieldMapping(BaseModel):
    maps: list[HarvestFieldMap] | None = None
    extra_fields: list[str] | None = None


class HarvestServiceCreateInput(BaseModel):
    """
    Model for creating a new harvest service.
    """

    name: str
    description: str
    url: str
    auth: HarvestAuthInfo
    field_mappings: HarvestFieldMapping = Field(default_factory=HarvestFieldMapping)
    where_clause: str = "1=1"


class HarvestFieldMapUpdate(BaseModel):
    operation: Literal["add", "remove", "update"]
    model: str
    field_name: str
    external_field: str | None = None

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if self.operation in {"add", "update"} and self.external_field is None:
            raise ValueError("external_field must be defined for add/update operations")
        return self


class FieldMapsUpdateInput(BaseModel):
    maps: list[HarvestFieldMapUpdate] | None = None
    add_extra_fields: list[str] | None = None
    remove_extra_fields: list[str] | None = None


class HarvestServiceUpdateInput(BaseModel):
    name: str | None = None
    description: str | None = None
    url: str | None = None
    auth: HarvestAuthInfo | None = None
    where_clause: str | None = None
    field_mappings: FieldMapsUpdateInput | None = None


class ArcGISImageServiceWMSOptions(BaseModel):
    enable: bool = True
    supported_srids: list[int] | None = None
    abstract: str | None = None
    keywords: list[str] | None = None
    title: str | None = None


class ArcGISImageServiceOptions(BaseModel):
    # The default service spatial reference, must be defined from the user
    default_service_srid: int
    wms_options: ArcGISImageServiceWMSOptions | None = None


class ArcGISFeatureServiceImageLayerOptions(BaseModel):
    """
    Options for the image layer in an ArcGIS feature service.
    """

    include_fields: list[str] | None = None
    enable_oriented_imagery: bool = False
    enable_images_as_attachments: bool = False
    image_processed_type: Literal["original", "blurred"] = "blurred"


class ArcGISFeatureServiceProjectLayerOptions(BaseModel):
    """
    Options for the project layer in an ArcGIS feature service.
    """

    include_fields: list[str] | None = None


class ArcGISFeatureServiceOptions(BaseModel):
    """
    Options for creating an ArcGIS feature service.
    """

    image_layer: ArcGISFeatureServiceImageLayerOptions
    project_layer: ArcGISFeatureServiceProjectLayerOptions | None = None


class ArcgisServiceCreateOptions(BaseModel):
    """
    Options for creating an ArcGIS service.
    """

    gdo_users: list[str] | None = None
    feature_service_options: ArcGISFeatureServiceOptions | None = None
    image_service_options: ArcGISImageServiceOptions | None = None


class ArcgisServiceCreateInput(BaseModel):
    """
    Input model for creating a new ArcGIS service.
    """

    name: str
    description: str
    data_collection_ids: Annotated[list[int], Len(min_length=1)]
    options: ArcgisServiceCreateOptions


class ArcgisServiceUpdateInput(BaseModel):
    """
    Input model for updating an ArcGIS service.
    """

    name: str | None = None
    description: str | None = None
    data_collection_ids: Annotated[list[int], Len(min_length=1)] | None = None
    options: ArcgisServiceCreateOptions | None = None


class UpdateInputBase(BaseModel):
    """
    Base model for updating rasters and images
    """

    add_tags: list[str] | None = None
    remove_tags: list[str] | None = None
    json_metadata: dict[str, str | float | int | None] | None = None

    @model_validator(mode="after")
    def validate_model(self) -> Self:
        if all(getattr(self, field) is None for field in type(self).model_fields):
            raise ValueError("At least one field must be updated")
        return self


class ImageUpdateInput(UpdateInputBase):
    """
    Input model for updating an image.
    """

    fields: ImageMetadataFields | None = None


class RasterUpdateInput(UpdateInputBase):
    """
    Input model for updating a raster.
    """

    fields: RasterMetadataFields | None = None
