import logging

import requests
from django.core.files.uploadedfile import UploadedFile

from binny_buddy.django_project import settings


class ImageDetectionService:
    def detect_from_uploaded_file(self, file: UploadedFile):
        url = f"{settings.AI_SERVER_URL}/detect"
        files = {
            "image": (
                file.name,
                file.file,
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
