# Create your models here.

from django.db import models


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
    user = models.ForeignKey(BinnyUser, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=255)
    content_type = models.CharField(max_length=255, null=True)
    blob = models.BinaryField()

    class Meta:
        db_table = "file"


class BinnyCollection(TimestampedModel):
    user = models.ForeignKey(
        BinnyUser,
        on_delete=models.DO_NOTHING,
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
    collection = models.ForeignKey(BinnyCollection, on_delete=models.DO_NOTHING)

    name = models.CharField(max_length=100)
    xp = models.BigIntegerField(default=0)

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
    user = models.ForeignKey(BinnyUser, on_delete=models.DO_NOTHING)
    file = models.ForeignKey(File, on_delete=models.DO_NOTHING, null=True)
    detection_result = models.ForeignKey(
        DetectionResult, on_delete=models.DO_NOTHING, null=True
    )

    binny = models.ForeignKey(
        Binny, on_delete=models.DO_NOTHING, default=None, null=True
    )
    is_binny_created = models.BooleanField(default=None, null=True)
    earned_xp = models.BigIntegerField(default=None, null=True)

    class Meta:
        db_table = "reward_history"
