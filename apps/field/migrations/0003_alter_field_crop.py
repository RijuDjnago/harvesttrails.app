# Generated by Django 5.0.6 on 2024-09-23 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field', '0002_crop'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='crop',
            field=models.CharField(blank=True, choices=[], max_length=255, null=True),
        ),
    ]
