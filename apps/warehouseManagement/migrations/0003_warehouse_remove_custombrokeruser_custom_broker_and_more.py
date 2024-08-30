# Generated by Django 5.0.6 on 2024-08-26 12:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouseManagement', '0002_custombroker_processordistributorshipment_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('location', models.TextField(blank=True, null=True)),
                ('latitude', models.CharField(blank=True, max_length=255, null=True)),
                ('longitude', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='custombrokeruser',
            name='custom_broker',
        ),
        migrations.RemoveField(
            model_name='distributor',
            name='billing_address',
        ),
        migrations.RemoveField(
            model_name='distributor',
            name='entity_name',
        ),
        migrations.RemoveField(
            model_name='distributor',
            name='fein',
        ),
        migrations.RemoveField(
            model_name='distributor',
            name='gin_id',
        ),
        migrations.RemoveField(
            model_name='distributor',
            name='main_fax',
        ),
        migrations.RemoveField(
            model_name='distributor',
            name='main_number',
        ),
        migrations.RemoveField(
            model_name='distributor',
            name='shipping_address',
        ),
        migrations.RemoveField(
            model_name='distributor',
            name='website',
        ),
        migrations.AddField(
            model_name='distributor',
            name='latitude',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='distributor',
            name='location',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='distributor',
            name='longitude',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='distributor',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='distributor',
            name='warehouse',
            field=models.ManyToManyField(blank=True, to='warehouseManagement.warehouse'),
        ),
        migrations.CreateModel(
            name='WarehouseUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_name', models.CharField(blank=True, max_length=250, null=True, verbose_name='Contact Name')),
                ('contact_email', models.CharField(blank=True, max_length=250, null=True, verbose_name='Contact Email')),
                ('contact_phone', models.CharField(blank=True, max_length=250, null=True, verbose_name='Contact Phone')),
                ('contact_fax', models.CharField(blank=True, max_length=250, null=True, verbose_name='Contact Fax')),
                ('p_password_raw', models.CharField(blank=True, max_length=250, null=True)),
                ('warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='warehouse_user', to='warehouseManagement.warehouse')),
            ],
        ),
        migrations.DeleteModel(
            name='CustomBroker',
        ),
        migrations.DeleteModel(
            name='CustomBrokerUser',
        ),
    ]