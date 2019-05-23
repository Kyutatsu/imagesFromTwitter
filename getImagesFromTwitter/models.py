from django.db import models
from django.contrib.auth.models import User


class Image(models.Model):
    nushi = models.CharField(max_length=100)
    image = models.URLField()
    text = models.TextField()
    has_multiple_media = models.BooleanField()
    label = models.IntegerField()
    labeler = models.OneToOneField(
            User,
            on_delete=models.SET_NULL,
            null=True,
    )
