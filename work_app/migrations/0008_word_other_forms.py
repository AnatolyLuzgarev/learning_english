# Generated by Django 2.2.7 on 2020-05-02 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('work_app', '0007_remove_word_other_forms'),
    ]

    operations = [
        migrations.AddField(
            model_name='word',
            name='other_forms',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]