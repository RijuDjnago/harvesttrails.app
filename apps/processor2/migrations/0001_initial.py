# Generated by Django 5.0 on 2024-04-11 11:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('processor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Processor2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fein', models.CharField(blank=True, max_length=250, null=True, verbose_name='FEIN')),
                ('entity_name', models.CharField(blank=True, max_length=250, null=True, verbose_name='Entity Name')),
                ('billing_address', models.TextField(blank=True, null=True, verbose_name='Billing Address')),
                ('shipping_address', models.TextField(blank=True, null=True, verbose_name='Shipping Address')),
                ('main_number', models.CharField(blank=True, max_length=250, null=True, verbose_name='Main Number')),
                ('main_fax', models.CharField(blank=True, max_length=250, null=True, verbose_name='Main Fax')),
                ('website', models.TextField(blank=True, null=True, verbose_name='Website')),
            ],
        ),
        migrations.CreateModel(
            name='AssignedBaleProcessor2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_bale', models.CharField(blank=True, max_length=250, null=True, verbose_name='Bale ID')),
                ('prod_id', models.CharField(blank=True, max_length=200, null=True)),
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
                ('grower_idd', models.CharField(blank=True, max_length=200, null=True, verbose_name='grower id')),
                ('grower_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='grower name')),
                ('field_idd', models.CharField(blank=True, max_length=200, null=True, verbose_name='field id')),
                ('certificate', models.CharField(blank=True, max_length=200, null=True, verbose_name='certificate')),
                ('value', models.CharField(blank=True, max_length=200, null=True)),
                ('level', models.CharField(blank=True, max_length=200, null=True)),
                ('crop_variety', models.CharField(blank=True, max_length=200, null=True)),
                ('mark_id', models.CharField(blank=True, max_length=200, null=True)),
                ('gin_id', models.CharField(blank=True, max_length=200, null=True)),
                ('bale', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor.balereportfarmfield', verbose_name='Select Bale')),
                ('processor2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor2.processor2', verbose_name='Select Processor2')),
            ],
        ),
        migrations.CreateModel(
            name='ProcessorUser2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_name', models.CharField(blank=True, max_length=250, null=True, verbose_name='Contact Name')),
                ('contact_email', models.CharField(blank=True, max_length=250, null=True, verbose_name='Contact Email')),
                ('contact_phone', models.CharField(blank=True, max_length=250, null=True, verbose_name='Contact Phone')),
                ('contact_fax', models.CharField(blank=True, max_length=250, null=True, verbose_name='Contact Fax')),
                ('p_password_raw', models.CharField(blank=True, max_length=250, null=True)),
                ('processor2', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='processor2.processor2', verbose_name='Select Processor2')),
            ],
        ),
    ]
