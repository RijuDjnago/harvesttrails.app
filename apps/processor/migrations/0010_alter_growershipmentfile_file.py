# Generated by Django 5.0.6 on 2024-05-20 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processor', '0009_remove_growershipment_lot_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='growershipmentfile',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='grower_shipment_file', verbose_name='Shipmentfile ID'),
        ),
    ]
