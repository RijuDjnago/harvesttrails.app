# Generated by Django 5.0.6 on 2024-09-23 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field', '0003_alter_field_crop'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crop',
            name='code',
            field=models.CharField(editable=False, max_length=10, unique=True),
        ),
    ]