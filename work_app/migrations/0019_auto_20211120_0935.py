# Generated by Django 2.2.7 on 2021-11-20 06:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work_app', '0018_auto_20211120_0810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlog',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 20, 9, 35, 46, 537495), editable=False),
        ),
        migrations.AlterModelTable(
            name='wordpicture',
            table='wordpicture',
        ),
    ]
