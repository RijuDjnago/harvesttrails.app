# Generated by Django 5.0.6 on 2024-09-12 10:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouseManagement', '0015_customerdocuments_document_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='billing_address',
            field=models.TextField(blank=True, null=True, verbose_name='Billing Address'),
        ),
        migrations.AddField(
            model_name='customer',
            name='shipping_address',
            field=models.TextField(blank=True, null=True, verbose_name='Shipping Address'),
        ),
    ]
