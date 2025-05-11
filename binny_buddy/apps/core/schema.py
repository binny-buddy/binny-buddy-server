import enum
from typing import List, Optional
from ninja import Schema


# Assuming you already have these defined elsewhere
class PlasticTypeEnum(str, enum.Enum):
    CUP = "cup"
    BOTTLE = "bottle"
    CONTAINER = "container"


class AssetTypeEnum(str, enum.Enum):
    TEXTURE = "texture"
    ACCESSORY = "accessory"


class WasteStatusEnum(str, enum.Enum):
    CLEAN = "clean"
    DIRTY = "dirty"


class DetectedObject(Schema):
    label: PlasticTypeEnum
    confidence: float
    status: WasteStatusEnum
    how_to_recycle: Optional[str] = None
    box_2d: Optional[List[float]] = None


class DetectionResponse(Schema):
    success: bool
    objects: List[DetectedObject]
    total_objects: int


class GenerationForm(Schema):
    model: PlasticTypeEnum
    asset_type: AssetTypeEnum


class GeneratedFile(Schema):
    filename: str
    content_base64: str
    size: int | None


class GenerationResponse(Schema):
    success: bool
    file: GeneratedFile | None
