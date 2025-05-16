# Create your views here.
import base64
import datetime

from django.conf import settings
from django.http import HttpRequest
from django.utils import timezone
from ninja import NinjaAPI
from ninja.errors import HttpError
from ninja.files import UploadedFile

from binny_buddy.apps.core.models import (
    BinnyUser,
    RewardHistory,
    BinnyCollection,
    Binny,
    File,
)
from binny_buddy.apps.core.schema import (
    FileSchema,
    HomeSchema,
    RewardHistorySchema,
    BinnyCollectionSchema,
    BinnySchema,
)
from binny_buddy.apps.core.services import (
    reward_service,
)
from ninja.security import SessionAuth


class BinnyBuddyAuth(SessionAuth):
    def authenticate(self, request, key):
        return BinnyUser.objects.get(username=settings.BINNY_USER_USERNAME)


class Request(HttpRequest):
    auth: BinnyUser


auth = BinnyBuddyAuth(csrf=False)

api = NinjaAPI(
    version="v1",
    title="Binny Buddy Public API",
    urls_namespace="public-api-v1",
    auth=auth,
)


@api.get("/home", response=HomeSchema)
def home(request: Request):
    collection_id = request.auth.collection_set.first().pk
    recent_reward_histories = (
        RewardHistory.objects.select_related("binny")
        .filter(created_at__gte=timezone.now() - datetime.timedelta(days=30))
        .order_by("-created_at")
    )
    return {
        "user": request.auth,
        "collection_id": collection_id,
        "recent_reward_histories": recent_reward_histories,
    }


@api.post("/request-reward", response=RewardHistorySchema)
def request_reward(request: Request, file: UploadedFile) -> RewardHistorySchema:
    return reward_service.request_reward_from_file(request.auth, file)


@api.get("/reward-history/{reward_history_id}", response=RewardHistorySchema)
def reward_history(request: Request, reward_history_id: int):
    reward_history = (
        RewardHistory.objects.select_related("binny")
        .filter(pk=reward_history_id, user=request.auth)
        .first()
    )

    if not reward_history:
        raise HttpError(404, "Not Found")

    return reward_history


@api.get("/file/{file_id}", response=FileSchema)
def file(request: Request, file_id: str):
    file = File.objects.filter(pk=file_id, user=request.auth).first()

    if not file:
        raise HttpError(404, "Not Found")

    return {
        "uuid": file.uuid,
        "name": file.name,
        "content_type": file.content_type,
        "data": base64.b64encode(file.blob).decode("utf-8"),
    }


@api.get("/collection/{collection_id}", response=BinnyCollectionSchema)
def collection(request: Request, collection_id: int):
    collection = BinnyCollection.objects.filter(
        pk=collection_id, user=request.auth
    ).first()

    if not collection:
        raise HttpError(404, "Not Found")

    binny_list = (
        Binny.objects.prefetch_related("rewardhistory_set")
        .filter(collection=collection)
        .order_by("-created_at")
    )

    return {"id": collection.pk, "binny_list": binny_list}


@api.get("/binny/{binny_id}", response=BinnySchema)
def binny(request: Request, binny_id: int):
    binny = (
        Binny.objects.prefetch_related("rewardhistory_set")
        .filter(pk=binny_id, collection__user=request.auth)
        .first()
    )

    if not binny:
        raise HttpError(404, "Not Found")

    return binny


@api.patch("/binny/{binny_id}", response=BinnySchema)
def binny_patch(request: Request, binny_id: int, name: str):
    binny = (
        Binny.objects.prefetch_related("rewardhistory_set")
        .filter(pk=binny_id, collection__user=request.auth)
        .first()
    )

    if not binny:
        raise HttpError(404, "Not Found")

    binny.name = name
    binny.save(update_fields=["name"])

    return binny
