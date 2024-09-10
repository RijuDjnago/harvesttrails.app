# Generated by Django 5.0.6 on 2024-09-08 06:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0022_customercontractcropdetails'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customercontractcropdetails',
            name='contract',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customerContractCrop', to='contracts.admincustomercontract'),
        ),
    ]