from django.db import models
from django.contrib.auth.models import User


class Image(models.Model):
    created_at = models.DateTimeField(null=True)
    id_str = models.CharField(max_length=50)
    screen_name = models.CharField(max_length=100)
    media_id_str = models.CharField(max_length=50)
    media_url_https = models.URLField()
    text = models.TextField(blank=True)
    hashtags_text = models.CharField(max_length=50, blank=True)
    retweet_count = models.IntegerField()
    favorite_count = models.IntegerField()
    has_multiple_media = models.BooleanField()
    label = models.IntegerField(null=True)
    labeler = models.ForeignKey(
            User,
            on_delete=models.SET_NULL,
            null=True,
    )
    subdata1 = models.TextField(null=True)
    subdata2 = models.TextField(null=True)
    subdata3 = models.IntegerField(null=True)
