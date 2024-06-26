# Generated by Django 5.0 on 2024-04-11 11:01

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('field', '0001_initial'),
        ('grower', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('storage_name', models.CharField(max_length=200, verbose_name='Storage Name')),
                ('storage_uniqueid', models.CharField(blank=True, max_length=200, null=True, verbose_name='Storage ID')),
                ('crop', models.CharField(blank=True, max_length=200, null=True, verbose_name='Select crop')),
                ('upload_type', models.CharField(choices=[('shapefile', 'Shapefile'), ('coordinates', 'Coordinates')], max_length=11, verbose_name='Upload Type')),
                ('shapefile_id', models.FileField(blank=True, null=True, upload_to='shapefile', verbose_name='Shapefile ID')),
                ('latitude', models.CharField(blank=True, max_length=200, null=True, verbose_name='Latitude')),
                ('longitude', models.CharField(blank=True, max_length=200, null=True, verbose_name='Longitude')),
                ('eschlon_id', models.CharField(blank=True, max_length=200, null=True)),
                ('grower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='grower.grower', verbose_name='Grower Name')),
            ],
        ),
        migrations.CreateModel(
            name='ShapeFileDataCo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coordinates', models.JSONField(default=list)),
                ('storage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='storage.storage')),
            ],
        ),
        migrations.CreateModel(
            name='StorageFeedCsv',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csv_path', models.FileField(blank=True, null=True, upload_to='storage_feed/', verbose_name='Storage Feed CSV')),
                ('upload_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('upload_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Upload By')),
            ],
        ),
        migrations.CreateModel(
            name='StorageFeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('crop', models.CharField(blank=True, max_length=200, null=True, verbose_name='Select crop')),
                ('status', models.CharField(blank=True, choices=[('quantity_in', 'Quantity In'), ('quantity_out', 'Quantity Out')], max_length=200, null=True, verbose_name='Quantity Status')),
                ('quantity', models.CharField(blank=True, default=0, help_text='default unit is pound', max_length=200, null=True)),
                ('quantity_raw', models.CharField(blank=True, default=0, help_text='if unit is pound quantity_raw and quantity is same', max_length=200, null=True)),
                ('shipment_id', models.CharField(blank=True, max_length=200, null=True, verbose_name='Shipment ID')),
                ('unit', models.CharField(blank=True, choices=[('LBS', 'LBS'), ('BU', 'BU')], max_length=200, null=True, verbose_name='Unit')),
                ('final_quantity', models.CharField(blank=True, help_text='default unit is pound', max_length=200, null=True)),
                ('storage_feed_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Created By')),
                ('field', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='field.field')),
                ('grower', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='grower.grower', verbose_name='Grower Name')),
                ('storage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='storage.storage')),
                ('csv_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='storage.storagefeedcsv', verbose_name='Csv File')),
            ],
        ),
    ]
