# Generated by Django 2.2.7 on 2021-11-16 19:50

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('work_app', '0015_essaytheme_useressays'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserEssays',
            new_name='UserEssay',
        ),
    ]