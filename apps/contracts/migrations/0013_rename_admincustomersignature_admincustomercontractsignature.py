# Generated by Django 5.0.6 on 2024-08-28 06:08

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0012_adminprocessorcontract_per_unit_rate_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AdminCustomerSignature',
            new_name='AdminCustomerContractSignature',
        ),
    ]