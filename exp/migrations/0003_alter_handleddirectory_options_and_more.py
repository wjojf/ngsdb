# Generated by Django 4.0.4 on 2022-09-20 15:32

from django.db import migrations, models
import django.db.models.deletion
import exp.models


class Migration(migrations.Migration):

    dependencies = [
        ('exp', '0002_alter_handleddirectory_directory_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='handleddirectory',
            options={'verbose_name_plural': 'Experiment Directories'},
        ),
        migrations.RemoveField(
            model_name='experiment',
            name='data_filepath',
        ),
        migrations.RemoveField(
            model_name='experiment',
            name='metadata_filepath',
        ),
        migrations.CreateModel(
            name='ExperimentFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_type', models.CharField(choices=[('nextseq', 'NextSeq'), ('deseq', 'Deseq'), ('count_matrix', 'CountMatrix')], max_length=150, verbose_name='File Type')),
                ('file_instance', models.FileField(upload_to=exp.models.experiment_data_filepath)),
                ('experiment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exp.experiment')),
            ],
        ),
    ]
