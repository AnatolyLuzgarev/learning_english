# Generated by Django 2.2.7 on 2021-12-14 06:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work_app', '0021_auto_20211126_2106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlog',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 14, 9, 15, 15, 410843), editable=False),
        ),
    ]
