# Generated by Django 2.1.2 on 2019-05-30 01:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('getImagesFromTwitter', '0002_auto_20190525_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='labeler',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
