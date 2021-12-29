# Generated by Django 2.2.7 on 2020-01-03 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=100)),
                ('translation', models.CharField(max_length=300)),
                ('first_letter', models.CharField(max_length=1)),
                ('transcription', models.CharField(max_length=100)),
            ],
        ),
    ]
