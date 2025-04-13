# Create your models here.

from django.db import models


class Binny(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table = "binny_buddy"
