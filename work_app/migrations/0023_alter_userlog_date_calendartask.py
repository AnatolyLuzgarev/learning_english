# Generated by Django 4.0 on 2022-01-01 10:24

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('work_app', '0022_auto_20211214_0915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlog',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 1, 1, 13, 24, 29, 570387), editable=False),
        ),
        migrations.CreateModel(
            name='CalendarTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('training', models.CharField(max_length=100)),
                ('amount', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
    ]
