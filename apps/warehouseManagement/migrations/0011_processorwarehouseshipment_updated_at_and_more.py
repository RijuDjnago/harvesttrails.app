# Generated by Django 5.0.6 on 2024-09-09 06:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouseManagement', '0010_processorshipmentlog_changes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='processorwarehouseshipment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='warehousecustomershipment',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='processorwarehouseshipment',
            name='border_back_leaving_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='processorwarehouseshipment',
            name='border_back_receive_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='processorwarehouseshipment',
            name='border_leaving_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='processorwarehouseshipment',
            name='border_receive_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='processorwarehouseshipment',
            name='distributor_leaving_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='processorwarehouseshipment',
            name='distributor_receive_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='processorwarehouseshipment',
            name='processor_receive_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehousecustomershipment',
            name='border_back_leaving_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehousecustomershipment',
            name='border_back_receive_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehousecustomershipment',
            name='border_leaving_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehousecustomershipment',
            name='border_receive_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehousecustomershipment',
            name='customer_leaving_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehousecustomershipment',
            name='customer_receive_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='warehousecustomershipment',
            name='warehouse_receive_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
