# Generated by Django 5.0.6 on 2024-06-13 07:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('processor2', '0015_processor_sku'),
    ]

    operations = [
        migrations.RenameField(
            model_name='processor_sku',
            old_name='processor1_id',
            new_name='processor1',
        ),
        migrations.RenameField(
            model_name='processor_sku',
            old_name='processor2_id',
            new_name='processor2',
        ),
    ]