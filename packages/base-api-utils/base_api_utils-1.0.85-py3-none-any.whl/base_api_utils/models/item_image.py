from django.db import models
from model_utils.models import TimeStampedModel


class ItemImage(TimeStampedModel):
    file_name = models.CharField(max_length=256)

    def __str__(self):
        return self.file_name

    class Meta:
        app_label= 'api'
        abstract = True