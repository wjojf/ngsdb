# Generated by Django 4.0.6 on 2022-09-01 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0002_handledurl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='handledurl',
            name='url',
            field=models.URLField(unique=True, verbose_name='Experiment folder url'),
        ),
    ]
