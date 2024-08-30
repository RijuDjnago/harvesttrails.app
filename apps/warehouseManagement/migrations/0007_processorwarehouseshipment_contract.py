# Generated by Django 5.0.6 on 2024-08-27 10:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0011_adminprocessorcontractdocuments_document_status'),
        ('warehouseManagement', '0006_warehouseorder_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='processorwarehouseshipment',
            name='contract',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='contract_delivery', to='contracts.adminprocessorcontract'),
            preserve_default=False,
        ),
    ]