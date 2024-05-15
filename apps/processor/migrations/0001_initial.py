# Generated by Django 5.0 on 2024-04-11 11:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('field', '0001_initial'),
        ('grower', '0001_initial'),
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateCalc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grower_id', models.CharField(blank=True, max_length=200, null=True)),
                ('field_id', models.CharField(blank=True, max_length=200, null=True)),
                ('certificate', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='GinLoadBalebydate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gin_date', models.CharField(blank=True, max_length=200, null=True)),
                ('load_id', models.CharField(blank=True, max_length=200, null=True)),
                ('bale_id', models.CharField(blank=True, max_length=200, null=True)),
                ('net_wt', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Processor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fein', models.CharField(blank=True, max_length=250, null=True, verbose_name='FEIN')),
                ('entity_name', models.CharField(blank=True, max_length=250, null=True, verbose_name='Entity Name')),
                ('billing_address', models.TextField(blank=True, null=True, verbose_name='Billing Address')),
                ('shipping_address', models.TextField(blank=True, null=True, verbose_name='Shipping Address')),
                ('main_number', models.CharField(blank=True, max_length=250, null=True, verbose_name='Main Number')),
                ('main_fax', models.CharField(blank=True, max_length=250, null=True, verbose_name='Main Fax')),
                ('website', models.TextField(blank=True, null=True, verbose_name='Website')),
                ('gin_id', models.CharField(blank=True, max_length=250, null=True, verbose_name='Gin Id')),
            ],
        ),
        migrations.CreateModel(
            name='ClassingReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csv_path', models.FileField(blank=True, null=True, upload_to='processor_reports', verbose_name='Classing Report CSV')),
                ('executed', models.CharField(blank=True, default='No', max_length=200, null=True)),
                ('csv_type', models.CharField(blank=True, max_length=200, null=True)),
                ('upload_date', models.DateField(blank=True, null=True)),
                ('grower', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='grower.grower')),
                ('processor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.processor')),
            ],
        ),
        migrations.CreateModel(
            name='BaleReportProducer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prod_id', models.CharField(blank=True, max_length=200, null=True)),
                ('farm_name', models.CharField(blank=True, max_length=200, null=True)),
                ('sale_status', models.CharField(blank=True, max_length=200, null=True)),
                ('wh_id', models.CharField(blank=True, max_length=200, null=True)),
                ('bale_id', models.CharField(blank=True, max_length=200, null=True)),
                ('gin_date', models.DateField(blank=True, null=True)),
                ('net_wt', models.CharField(blank=True, max_length=200, null=True)),
                ('farm_id', models.CharField(blank=True, max_length=200, null=True)),
                ('load_id', models.CharField(blank=True, max_length=200, null=True)),
                ('field_name', models.CharField(blank=True, max_length=200, null=True)),
                ('pk_num', models.CharField(blank=True, max_length=200, null=True)),
                ('gr', models.CharField(blank=True, max_length=200, null=True)),
                ('lf', models.CharField(blank=True, max_length=200, null=True)),
                ('st', models.CharField(blank=True, max_length=200, null=True)),
                ('mic', models.CharField(blank=True, max_length=200, null=True)),
                ('ex', models.CharField(blank=True, max_length=200, null=True)),
                ('rm', models.CharField(blank=True, max_length=200, null=True)),
                ('str_no', models.CharField(blank=True, max_length=200, null=True)),
                ('cgr', models.CharField(blank=True, max_length=200, null=True)),
                ('rd', models.CharField(blank=True, max_length=200, null=True)),
                ('ob1', models.CharField(blank=True, max_length=200, null=True)),
                ('tr', models.CharField(blank=True, max_length=200, null=True)),
                ('unif', models.CharField(blank=True, max_length=200, null=True)),
                ('len_num', models.CharField(blank=True, max_length=200, null=True)),
                ('elong', models.CharField(blank=True, max_length=200, null=True)),
                ('ob2', models.CharField(blank=True, max_length=200, null=True)),
                ('ob3', models.CharField(blank=True, max_length=200, null=True)),
                ('ob4', models.CharField(blank=True, max_length=200, null=True)),
                ('ob5', models.CharField(blank=True, max_length=200, null=True)),
                ('value', models.CharField(blank=True, max_length=200, null=True)),
                ('classing', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.classingreport')),
            ],
        ),
        migrations.CreateModel(
            name='BaleReportFarmField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prod_id', models.CharField(blank=True, max_length=200, null=True)),
                ('bale_id', models.CharField(blank=True, max_length=200, null=True)),
                ('wt', models.CharField(blank=True, max_length=200, null=True)),
                ('net_wt', models.CharField(blank=True, max_length=200, null=True)),
                ('load_id', models.CharField(blank=True, max_length=200, null=True)),
                ('dt_class', models.CharField(blank=True, max_length=200, null=True)),
                ('gr', models.CharField(blank=True, max_length=200, null=True)),
                ('lf', models.CharField(blank=True, max_length=200, null=True)),
                ('st', models.CharField(blank=True, max_length=200, null=True)),
                ('mic', models.CharField(blank=True, max_length=200, null=True)),
                ('ex', models.CharField(blank=True, max_length=200, null=True)),
                ('rm', models.CharField(blank=True, max_length=200, null=True)),
                ('str_no', models.CharField(blank=True, max_length=200, null=True)),
                ('cgr', models.CharField(blank=True, max_length=200, null=True)),
                ('rd', models.CharField(blank=True, max_length=200, null=True)),
                ('tr', models.CharField(blank=True, max_length=200, null=True)),
                ('unif', models.CharField(blank=True, max_length=200, null=True)),
                ('len_num', models.CharField(blank=True, max_length=200, null=True)),
                ('elong', models.CharField(blank=True, max_length=200, null=True)),
                ('cents_lb', models.CharField(blank=True, max_length=200, null=True)),
                ('loan_value', models.CharField(blank=True, max_length=200, null=True)),
                ('warehouse_wt', models.CharField(blank=True, max_length=200, null=True)),
                ('warehouse_bale_id', models.CharField(blank=True, max_length=200, null=True)),
                ('warehouse_wh_id', models.CharField(blank=True, max_length=200, null=True)),
                ('farm_name', models.CharField(blank=True, max_length=200, null=True)),
                ('sale_status', models.CharField(blank=True, max_length=200, null=True)),
                ('wh_id', models.CharField(blank=True, max_length=200, null=True)),
                ('ob1', models.CharField(blank=True, max_length=200, null=True)),
                ('gin_date', models.DateField(blank=True, null=True)),
                ('farm_id', models.CharField(blank=True, max_length=200, null=True)),
                ('field_name', models.CharField(blank=True, max_length=200, null=True)),
                ('pk_num', models.CharField(blank=True, max_length=200, null=True)),
                ('ob2', models.CharField(blank=True, max_length=200, null=True, verbose_name='grower id')),
                ('ob3', models.CharField(blank=True, max_length=200, null=True, verbose_name='grower name')),
                ('ob4', models.CharField(blank=True, max_length=200, null=True, verbose_name='field id')),
                ('ob5', models.CharField(blank=True, max_length=200, null=True, verbose_name='certificate')),
                ('value', models.CharField(blank=True, max_length=200, null=True)),
                ('level', models.CharField(blank=True, max_length=200, null=True)),
                ('crop_variety', models.CharField(blank=True, max_length=200, null=True)),
                ('upload_date', models.DateField(blank=True, null=True)),
                ('classing', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.classingreport')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=250, null=True, verbose_name='Location Name')),
                ('upload_type', models.CharField(choices=[('shapefile', 'Shapefile'), ('coordinates', 'Coordinates')], max_length=11, verbose_name='Upload Type')),
                ('shapefile_id', models.FileField(blank=True, null=True, upload_to='processor_shapefile', verbose_name='Shapefile ID')),
                ('latitude', models.CharField(blank=True, max_length=200, null=True, verbose_name='Latitude')),
                ('longitude', models.CharField(blank=True, max_length=200, null=True, verbose_name='Longitude')),
                ('eschlon_id', models.CharField(blank=True, max_length=200, null=True)),
                ('processor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.processor', verbose_name='Select Processor')),
            ],
        ),
        migrations.CreateModel(
            name='LinkGrowerToProcessor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grower', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='grower.grower', verbose_name='Select Grower')),
                ('processor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.processor', verbose_name='Select Processor')),
            ],
        ),
        migrations.CreateModel(
            name='GrowerShipment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('process_time', models.TimeField(auto_created=True, auto_now_add=True, verbose_name='Processed Time')),
                ('process_date', models.DateField(auto_created=True, auto_now_add=True, verbose_name='Processed Date')),
                ('date_time_location', models.DateTimeField(auto_created=True, auto_now_add=True, verbose_name='Location Date')),
                ('date_time', models.DateTimeField(auto_created=True, auto_now_add=True, verbose_name='Shipment Date')),
                ('crop', models.CharField(blank=True, max_length=200, null=True, verbose_name='Select Item')),
                ('variety', models.CharField(blank=True, max_length=200, null=True, verbose_name='Select Variety')),
                ('amount', models.CharField(blank=True, max_length=200, null=True, verbose_name='Amount')),
                ('amount2', models.CharField(blank=True, max_length=200, null=True, verbose_name='Amount2')),
                ('sustainability_score', models.CharField(blank=True, max_length=200, null=True, verbose_name='Sustainability Score')),
                ('echelon_id', models.CharField(blank=True, max_length=200, null=True, verbose_name='Echelon Id')),
                ('shipment_id', models.CharField(blank=True, max_length=200, null=True, verbose_name='Shipment Id')),
                ('qr_code', models.TextField(blank=True, null=True, verbose_name='QR code')),
                ('process_amount', models.CharField(blank=True, max_length=200, null=True, verbose_name='Processed Amount')),
                ('sku', models.CharField(blank=True, max_length=200, null=True, verbose_name='SKU')),
                ('module_number', models.CharField(blank=True, max_length=200, null=True, verbose_name='Module Tag #')),
                ('unit_type', models.CharField(blank=True, max_length=200, null=True, verbose_name='Unit Type')),
                ('unit_type2', models.CharField(blank=True, max_length=200, null=True, verbose_name='Unit Type2')),
                ('total_amount', models.CharField(blank=True, max_length=200, null=True, verbose_name='Total Amount')),
                ('received_amount', models.CharField(blank=True, max_length=200, null=True, verbose_name='Received Amount')),
                ('token_id', models.CharField(blank=True, max_length=200, null=True, verbose_name='Token Id')),
                ('approval_date', models.DateField(blank=True, null=True, verbose_name='Approval Date')),
                ('status', models.CharField(choices=[('APPROVED', 'APPROVED'), ('DISAPPROVED', 'DISAPPROVED'), ('', '')], default='', max_length=200)),
                ('reason_for_disapproval', models.CharField(blank=True, max_length=200, null=True, verbose_name='Reason For Disapproval')),
                ('moisture_level', models.CharField(blank=True, max_length=200, null=True, verbose_name='Moisture Level')),
                ('fancy_count', models.CharField(blank=True, max_length=200, null=True, verbose_name='Fancy Count')),
                ('head_count', models.CharField(blank=True, max_length=200, null=True, verbose_name='Head Count')),
                ('bin_location_processor', models.CharField(blank=True, max_length=200, null=True, verbose_name='Bin Location at Processor')),
                ('field', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='field.field', verbose_name='Select Field')),
                ('grower', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='grower.grower', verbose_name='Select Grower')),
                ('storage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='storage.storage', verbose_name='Select Storage')),
                ('location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.location', verbose_name='Select Location')),
                ('processor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.processor', verbose_name='Select Processor')),
            ],
            options={
                'ordering': ('-date_time',),
            },
        ),
        migrations.CreateModel(
            name='ProcessorUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_name', models.CharField(blank=True, max_length=250, null=True, verbose_name='Contact Name')),
                ('contact_email', models.CharField(blank=True, max_length=250, null=True, verbose_name='Contact Email')),
                ('contact_phone', models.CharField(blank=True, max_length=250, null=True, verbose_name='Contact Phone')),
                ('contact_fax', models.CharField(blank=True, max_length=250, null=True, verbose_name='Contact Fax')),
                ('p_password_raw', models.CharField(blank=True, max_length=250, null=True)),
                ('processor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.processor', verbose_name='Select Processor')),
            ],
        ),
        migrations.CreateModel(
            name='ProductionManagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('processor_e_name', models.CharField(blank=True, max_length=200, null=True)),
                ('total_volume', models.CharField(blank=True, max_length=200, null=True)),
                ('inbound', models.CharField(blank=True, max_length=200, null=True)),
                ('date_pulled', models.DateField(blank=True, null=True)),
                ('bin_location', models.CharField(blank=True, max_length=200, null=True)),
                ('volume_pulled', models.CharField(blank=True, max_length=200, null=True)),
                ('milled_volume', models.CharField(blank=True, max_length=200, null=True)),
                ('volume_left', models.CharField(blank=True, max_length=200, null=True)),
                ('milled_storage_bin', models.CharField(blank=True, max_length=200, null=True)),
                ('editable_obj', models.BooleanField(blank=True, null=True)),
                ('processor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.processor')),
            ],
        ),
        migrations.CreateModel(
            name='ProductionReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uploaded_date', models.DateField(blank=True, null=True)),
                ('csv_path', models.FileField(blank=True, null=True, upload_to='processor_reports', verbose_name='Classing Report CSV')),
                ('executed', models.CharField(blank=True, default='No', max_length=200, null=True)),
                ('processor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.processor', verbose_name='Select Processor')),
            ],
            options={
                'ordering': ('-uploaded_date',),
            },
        ),
        migrations.CreateModel(
            name='GinReportbyday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(blank=True, max_length=200, null=True)),
                ('load_id', models.CharField(blank=True, max_length=200, null=True)),
                ('prod_id', models.CharField(blank=True, max_length=200, null=True)),
                ('farm_id', models.CharField(blank=True, max_length=200, null=True)),
                ('field_name', models.CharField(blank=True, max_length=200, null=True)),
                ('pk_num', models.CharField(blank=True, max_length=200, null=True)),
                ('variety', models.CharField(blank=True, max_length=200, null=True)),
                ('tm', models.CharField(blank=True, max_length=200, null=True)),
                ('module_amount', models.CharField(blank=True, max_length=200, null=True)),
                ('truck_id', models.CharField(blank=True, max_length=200, null=True)),
                ('made_date', models.CharField(blank=True, max_length=200, null=True)),
                ('delivery_date', models.CharField(blank=True, max_length=200, null=True)),
                ('gin_date', models.CharField(blank=True, max_length=200, null=True)),
                ('bc', models.CharField(blank=True, max_length=200, null=True)),
                ('cotton_seed', models.CharField(blank=True, max_length=200, null=True)),
                ('lint', models.CharField(blank=True, max_length=200, null=True)),
                ('seed', models.CharField(blank=True, max_length=200, null=True)),
                ('turnout', models.CharField(blank=True, max_length=200, null=True)),
                ('bale_tot', models.CharField(blank=True, max_length=200, null=True)),
                ('production', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.productionreport')),
            ],
        ),
        migrations.CreateModel(
            name='ShipmentManagement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('processor_idd', models.CharField(blank=True, max_length=200, null=True)),
                ('processor_e_name', models.CharField(blank=True, max_length=200, null=True)),
                ('bin_location', models.CharField(blank=True, max_length=200, null=True, verbose_name='MILLED STORAGE BIN')),
                ('date_pulled', models.DateField(blank=True, null=True)),
                ('milled_volume', models.CharField(blank=True, max_length=200, null=True)),
                ('equipment_type', models.CharField(blank=True, choices=[('Truck', 'Truck'), ('Hopper Car', 'Hopper Car'), ('Rail Car', 'Rail Car')], max_length=200, null=True)),
                ('equipment_id', models.CharField(blank=True, max_length=200, null=True)),
                ('purchase_order_number', models.CharField(blank=True, max_length=200, null=True)),
                ('lot_number', models.CharField(blank=True, max_length=200, null=True)),
                ('volume_shipped', models.CharField(blank=True, max_length=200, null=True)),
                ('volume_left', models.CharField(blank=True, max_length=200, null=True)),
                ('editable_obj', models.BooleanField(blank=True, null=True)),
                ('storage_bin', models.CharField(blank=True, max_length=200, null=True, verbose_name='Storage Bin ID')),
                ('weight_of_product', models.CharField(blank=True, default=0, help_text='default unit is pound', max_length=200, null=True)),
                ('weight_of_product_raw', models.CharField(blank=True, default=0, help_text='if unit is pound, then weight_of_product_raw and weight_of_product is same', max_length=200, null=True)),
                ('weight_of_product_unit', models.CharField(blank=True, choices=[('LBS', 'LBS'), ('BU', 'BU')], max_length=200, null=True, verbose_name='Unit')),
                ('excepted_yield', models.CharField(blank=True, default=0, help_text='default unit is pound', max_length=200, null=True)),
                ('excepted_yield_raw', models.CharField(blank=True, default=0, help_text='if unit is pound, then excepted_yield_raw and excepted_yield is same', max_length=200, null=True)),
                ('excepted_yield_unit', models.CharField(blank=True, choices=[('LBS', 'LBS'), ('BU', 'BU')], max_length=200, null=True, verbose_name='Unit')),
                ('moisture_percent', models.CharField(blank=True, max_length=200, null=True)),
                ('production_management', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.productionmanagement')),
            ],
        ),
    ]
