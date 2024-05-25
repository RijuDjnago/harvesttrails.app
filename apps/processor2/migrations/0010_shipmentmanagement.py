# Generated by Django 5.0.6 on 2024-05-24 08:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processor', '0015_remove_shipmentmanagement_files_and_more'),
        ('processor2', '0009_delete_shipmentmanagement'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShipmentManagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shipment_id', models.CharField(blank=True, max_length=200, null=True)),
                ('processor_idd', models.CharField(blank=True, max_length=200, null=True)),
                ('processor_e_name', models.CharField(blank=True, max_length=200, null=True)),
                ('sender_processor_type', models.CharField(blank=True, choices=[('T1', 'T1'), ('T2', 'T2'), ('T3', 'T3'), ('T4', 'T4'), ('Buyer', 'Buyer')], max_length=5, null=True)),
                ('bin_location', models.CharField(blank=True, max_length=200, null=True, verbose_name='MILLED STORAGE BIN')),
                ('date_pulled', models.DateTimeField(auto_now_add=True)),
                ('milled_volume', models.CharField(blank=True, max_length=200, null=True)),
                ('equipment_type', models.CharField(blank=True, choices=[('Truck', 'Truck'), ('Hopper Car', 'Hopper Car'), ('Rail Car', 'Rail Car')], max_length=200, null=True)),
                ('equipment_id', models.CharField(blank=True, max_length=200, null=True)),
                ('purchase_order_number', models.CharField(blank=True, max_length=200, null=True)),
                ('lot_number', models.CharField(blank=True, max_length=200, null=True)),
                ('volume_shipped', models.CharField(blank=True, max_length=200, null=True)),
                ('volume_left', models.CharField(blank=True, max_length=200, null=True)),
                ('editable_obj', models.BooleanField(blank=True, null=True)),
                ('storage_bin_send', models.CharField(blank=True, max_length=200, null=True, verbose_name='Storage Bin ID(SKU ID)(storage_bin_send)')),
                ('storage_bin_recive', models.CharField(blank=True, max_length=200, null=True, verbose_name='Storage Bin ID(SKU ID)(storage_bin_recive)')),
                ('weight_of_product', models.CharField(blank=True, default=0, help_text='default unit is pound', max_length=200, null=True)),
                ('weight_of_product_raw', models.CharField(blank=True, default=0, help_text='if unit is pound, then weight_of_product_raw and weight_of_product is same', max_length=200, null=True)),
                ('weight_of_product_unit', models.CharField(blank=True, choices=[('LBS', 'LBS'), ('BU', 'BU')], max_length=200, null=True, verbose_name='Unit')),
                ('excepted_yield', models.CharField(blank=True, default=0, help_text='default unit is pound', max_length=200, null=True)),
                ('excepted_yield_raw', models.CharField(blank=True, default=0, help_text='if unit is pound, then excepted_yield_raw and excepted_yield is same', max_length=200, null=True)),
                ('excepted_yield_unit', models.CharField(blank=True, choices=[('LBS', 'LBS'), ('BU', 'BU')], max_length=200, null=True, verbose_name='Unit')),
                ('moisture_percent', models.CharField(blank=True, max_length=200, null=True)),
                ('receiver_processor_type', models.CharField(blank=True, choices=[('T1', 'T1'), ('T2', 'T2'), ('T3', 'T3'), ('T4', 'T4'), ('Buyer', 'Buyer')], max_length=200, null=True)),
                ('processor2_idd', models.CharField(blank=True, max_length=200, null=True)),
                ('processor2_name', models.CharField(blank=True, max_length=250, null=True)),
                ('recive_delivery_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('APPROVED', 'APPROVED'), ('DISAPPROVED', 'DISAPPROVED'), ('', '')], max_length=20, null=True)),
                ('files', models.ManyToManyField(blank=True, related_name='shipments', to='processor.file')),
                ('prod_mgmt_processor2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor2.productionmanagementprocessor2')),
                ('production_management', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.productionmanagement')),
            ],
        ),
    ]
