# Generated by Django 5.0.6 on 2024-09-09 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouseManagement', '0007_processorwarehouseshipment_crop_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='warehousecustomershipment',
            name='approval_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='warehousecustomershipment',
            name='invoice_approval',
            field=models.BooleanField(default=False),
        ),
    ]
