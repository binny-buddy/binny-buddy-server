import datetime
import enum
import uuid
from typing import List, Optional
from ninja import Schema


class BinnyTypeEnum(str, enum.Enum):
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
    label: BinnyTypeEnum
    confidence: float
    status: WasteStatusEnum
    how_to_recycle: Optional[str] = None
    box_2d: Optional[List[float]] = None


class DetectionResponse(Schema):
    success: bool
    objects: List[DetectedObject]
    total_objects: int


class GenerationForm(Schema):
    model: BinnyTypeEnum
    asset_type: AssetTypeEnum


class GeneratedFile(Schema):
    filename: str
    content_base64: str
    size: int | None


class GenerationResponse(Schema):
    success: bool
    file: GeneratedFile | None


class BinnyUserSchema(Schema):
    id: int
    username: str


class BinnySchema(Schema):
    id: int
    binny_type: BinnyTypeEnum
    name: str
    xp: int
    level: int

    created_at: datetime.datetime
    updated_at: datetime.datetime
    reward_count: int


class DetectionResultSchema(Schema):
    is_clean: bool
    confidence: float
    binny_type: BinnyTypeEnum
    how_to_recycle: str | None = None


class RewardHistorySchema(Schema):
    id: int
    user: BinnyUserSchema
    file_id: uuid.UUID
    detection_result: DetectionResultSchema | None

    binny: BinnySchema | None
    is_binny_created: bool | None
    earned_xp: int | None

    created_at: datetime.datetime
    updated_at: datetime.datetime

    is_level_up: bool | None


class BinnyCollectionSchema(Schema):
    id: int
    binny_list: list[BinnySchema]


class MeSchema(Schema):
    id: int
    username: str


class HomeSchema(Schema):
    user: BinnyUserSchema
    collection_id: int
    recent_reward_histories: list[RewardHistorySchema]


class FileSchema(Schema):
    uuid: uuid.UUID
    name: str
    content_type: str
    data: str
