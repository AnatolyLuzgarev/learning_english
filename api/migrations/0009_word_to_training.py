# Generated by Django 2.2.7 on 2020-07-03 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work_app', '0008_word_other_forms'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='to_training',
            field=models.BooleanField(default=False),
        ),
    ]
