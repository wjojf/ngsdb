# Generated by Django 4.0.4 on 2022-07-30 17:13

from django.db import migrations, models
import exp.models


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0004_expconditions_alter_descriptormap_content_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='experiment',
            name='metadata_filepath',
            field=models.FileField(default='Not Avaliable', upload_to=exp.models.experiment_data_filepath, verbose_name='Metadata file'),
        ),
        migrations.AlterField(
            model_name='experiment',
            name='data_filepath',
            field=models.FileField(default='Not Avaliable', upload_to=exp.models.experiment_data_filepath, verbose_name='Results file'),
        ),
    ]
