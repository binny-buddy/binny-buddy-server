# Create your views here.

from ninja import NinjaAPI, Query
from ninja.files import UploadedFile

from binny_buddy.apps.core.schema import (
    DetectionResponse,
    GenerationForm,
)
from binny_buddy.apps.core.services import (
    image_detection_service,
    image_generation_service,
)

api = NinjaAPI()


@api.post("/detect")
def detect(request, file: UploadedFile) -> DetectionResponse:
    return image_detection_service.detect_from_uploaded_file(file)


@api.post("/generate")
def generate(
    request,
    form: Query[GenerationForm],
    file: UploadedFile | None = None,
) -> DetectionResponse:
    if file:
        return image_generation_service.generate_texture_from_uploaded_file(
            form.model, form.asset_type, file
        )

    return image_generation_service.generate_texture(form.model, form.asset_type)
