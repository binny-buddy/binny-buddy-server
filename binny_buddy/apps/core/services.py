import json
import logging
import uuid
from typing import TypedDict

import requests
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import F, Value

from binny_buddy.apps.core.models import (
    BinnyUser,
    File,
    RewardHistory,
    DetectionResult,
    Binny,
    BinnyType,
)
from django.conf import settings


def get_level_by_xp(xp):
    xp_levels = [
        (0, 99),
        (100, 249),
        (250, 499),
        (500, 999),
        (1000, 1999),
        (2000, 3999),
        (4000, 6999),
        (7000, 9999),
        (10000, 14999),
        (15000, float("inf")),
    ]

    for level, (min_xp, max_xp) in enumerate(xp_levels, start=1):
        if min_xp <= xp <= max_xp:
            return level
    return 1


class DetectedObjectResponse(TypedDict):
    label: str
    confidence: float
    status: str
    how_to_recycle: str | None
    box_2d: list[float] | None


class DetectionResponse(TypedDict):
    success: bool
    objects: list[DetectedObjectResponse]
    total_objects: int


class ImageDetectionService:
    def detect_from_file(self, file: File) -> DetectionResponse:
        if settings.DEBUG:
            with open("mock.json") as f:
                return json.load(f)

        url = f"{settings.AI_SERVER_URL}/detect"
        files = {
            "image": (
                file.name,
                file.blob,
                file.content_type,
            )
        }

        response = requests.post(url, files=files)

        try:
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as exc:
            logging.error(
                f"[detect_from_uploaded_file] AI server responded with {exc.response.status_code}",
                exc_info=exc,
            )
            return {"success": False, "objects": [], "total_objects": 0}


class ImageGenerationService:
    def generate_texture_from_uploaded_file(
        self, model: str, asset_type: str, file: UploadedFile
    ):
        url = f"{settings.AI_SERVER_URL}/assets/create"
        files = {
            "file": (
                file.name,
                file.file,
                file.content_type,
            )
        }

        response = requests.post(
            url, files=files, params={"model": model, "asset_type": asset_type}
        )

        try:
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as exc:
            logging.error(
                f"[generate_texture_from_uploaded_file] AI server responded with {exc.response.status_code}",
                exc_info=exc,
            )
            return {"success": False, "file": None}

    def generate_texture(self, model: str, asset_type: str):
        url = f"{settings.AI_SERVER_URL}/assets"
        response = requests.get(url, params={"model": model, "asset_type": asset_type})

        try:
            response.raise_for_status()
            return response.json()

        except requests.HTTPError as exc:
            logging.error(
                f"[generate_texture] AI server responded with {exc.response.status_code}",
                exc_info=exc,
            )
            return {"success": False, "file": None}


image_detection_service = ImageDetectionService()
image_generation_service = ImageGenerationService()


class FileService:
    def create_file_from_uploaded_file(self, user: BinnyUser, file: UploadedFile):
        return File.objects.create(
            user=user,
            name=file.name,
            content_type=file.content_type,
            blob=file.read(),
            uuid=uuid.uuid4(),
        )


class RewardService:
    image_detection_service = image_detection_service
    image_generation_service = image_generation_service
    file_service = FileService()

    REWARD_XP = 500

    def request_reward_from_file(
        self, user: BinnyUser, uploaded_file: UploadedFile
    ) -> RewardHistory:
        file = self.file_service.create_file_from_uploaded_file(user, uploaded_file)
        reward_history = RewardHistory.objects.create(user=user, file=file)

        detection_response = image_detection_service.detect_from_file(file)

        if not detection_response["success"]:
            return reward_history

        detected_object = next(iter(detection_response["objects"] or []), None)

        if not detected_object:
            return reward_history

        with transaction.atomic():
            binny_type = BinnyType.from_value(detected_object["label"])
            detection_result = DetectionResult.objects.create(
                is_clean=detected_object["status"] == "clean",
                confidence=detected_object["confidence"],
                binny_type=binny_type,
                how_to_recycle=detected_object["how_to_recycle"],
            )

            if not detection_result.is_clean:
                reward_history.detection_result = detection_result
                reward_history.save(update_fields=["detection_result"])

            else:
                collection = user.collection_set.first()
                binny, is_created = Binny.objects.update_or_create(
                    binny_type=binny_type,
                    collection=collection,
                    defaults={"xp": F("xp") + Value(self.REWARD_XP)},
                    create_defaults={"name": "Binny", "xp": 0},
                )
                binny.refresh_from_db()
                earned_xp = 0 if is_created else self.REWARD_XP

                reward_history.binny = binny
                reward_history.detection_result = detection_result
                reward_history.is_binny_created = is_created
                reward_history.earned_xp = earned_xp
                reward_history.save(
                    update_fields=[
                        "detection_result",
                        "binny",
                        "earned_xp",
                        "is_binny_created",
                    ]
                )

        return reward_history


reward_service = RewardService()
