# Generated by Django 4.2.5 on 2023-09-13 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('all_charts', '0002_alter_dataforchart_parsed_file_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataforchart',
            name='parsed_file_path',
            field=models.FilePathField(blank=True, null=True),
        ),
    ]
