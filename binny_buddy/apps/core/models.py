# Create your models here.

from django.db import models


# class BinnyUser(models.Model):
#     username = models.CharField(max_length=255, unique=True)
#     password = models.CharField(max_length=255)
#
#     class Meta:
#         db_table = "binny_user"
#
#
# class BinnyLibrary(models.Model):
#     user = models.ForeignKey(BinnyUser, on_delete=models.DO_NOTHING)
#
#     class Meta:
#         db_table = "binny_library"
#
#
# class BinnyType(models.TextChoices):
#     takeout_cup = "TAKEOUT_CUP"
#     pet_bottle = "PET_BOTTLE"
#     bdyg = "BDYG"
#
#
# class Binny(models.Model):
#     binny_type = models.CharField(max_length=100, choices=BinnyType.choices)
#     library = models.ForeignKey(BinnyLibrary, on_delete=models.DO_NOTHING)
#     name = models.CharField(max_length=100)
#
#     class Meta:
#         db_table = "binny_buddy"
#
#
# class BinnyTexture(models.Model):
#     binny_type = models.CharField(max_length=100, choices=BinnyType.choices)
#
#     class Meta:
#         db_table = "binny_texture"
