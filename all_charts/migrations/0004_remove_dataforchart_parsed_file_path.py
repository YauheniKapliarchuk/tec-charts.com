# Generated by Django 4.2.5 on 2023-09-13 17:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('all_charts', '0003_alter_dataforchart_parsed_file_path'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataforchart',
            name='parsed_file_path',
        ),
    ]
