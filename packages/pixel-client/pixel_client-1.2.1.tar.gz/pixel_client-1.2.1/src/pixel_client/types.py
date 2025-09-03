from typing import Literal


AttachmentResourceType = Literal["project", "data_collection", "image"]
DataCollectionType = Literal["image", "raster", "RGB", "DTM", "DSM"]
OverviewResampling = Literal[
    "nearest",
    "bilinear",
    "cubic",
    "cubic_spline",
    "lanczos",
    "average",
    "mode",
    "gauss",
    "rms",
]
