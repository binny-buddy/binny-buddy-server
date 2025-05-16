# Create your models here.

from django.db import models

from binny_buddy.apps.core.utils import get_level_by_xp


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BinnyType(models.TextChoices):
    cup = "cup"
    bottle = "bottle"
    container = "container"

    @classmethod
    def from_value(cls, value):
        if value == "cup":
            return cls.cup
        if value == "bottle":
            return cls.bottle
        if value == "container":
            return cls.container
        raise ValueError


class BinnyUser(TimestampedModel):
    username = models.CharField(max_length=255, unique=True)
    # password = models.CharField(max_length=255)

    class Meta:
        db_table = "binny_user"


class File(TimestampedModel):
    uuid = models.UUIDField(primary_key=True)
    user = models.ForeignKey(BinnyUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255, null=True)
    blob = models.BinaryField()

    class Meta:
        db_table = "file"


class BinnyCollection(TimestampedModel):
    user = models.ForeignKey(
        BinnyUser,
        on_delete=models.CASCADE,
        related_name="collection_set",
        related_query_name="collection",
    )

    class Meta:
        db_table = "binny_library"


class BinnyTexture(TimestampedModel):
    binny_type = models.CharField(max_length=100, choices=BinnyType.choices)

    class Meta:
        db_table = "binny_texture"


class Binny(TimestampedModel):
    binny_type = models.CharField(max_length=100, choices=BinnyType.choices)
    collection = models.ForeignKey(BinnyCollection, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    xp = models.BigIntegerField(default=0)

    @property
    def level(self) -> int:
        return get_level_by_xp(self.xp)

    @property
    def reward_count(self):
        return len(
            [
                reward_history
                for reward_history in self.rewardhistory_set.all()
                if reward_history.is_binny_created or reward_history.earned_xp
            ]
        )

    class Meta:
        db_table = "binny_buddy"


class DetectionResult(TimestampedModel):
    is_clean = models.BooleanField()
    confidence = models.FloatField()
    binny_type = models.CharField(max_length=100, choices=BinnyType.choices)
    how_to_recycle = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "detection_result"


class RewardHistory(TimestampedModel):
    user = models.ForeignKey(BinnyUser, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True)
    detection_result = models.ForeignKey(
        DetectionResult, on_delete=models.CASCADE, null=True
    )

    binny = models.ForeignKey(Binny, on_delete=models.CASCADE, default=None, null=True)
    is_binny_created = models.BooleanField(default=None, null=True)
    earned_xp = models.BigIntegerField(default=None, null=True)

    @property
    def is_level_up(self) -> bool | None:
        if not self.binny or self.earned_xp is None:
            return None
        return self.binny.level > get_level_by_xp(self.binny.xp - self.earned_xp)

    class Meta:
        db_table = "reward_history"
