# Generated by Django 5.0.6 on 2024-09-05 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0017_admincustomercontract_tax_percentage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='admincustomercontract',
            name='tax_percentage',
            field=models.DecimalField(decimal_places=2, default=7.0, max_digits=5),
        ),
        migrations.AlterField(
            model_name='adminprocessorcontract',
            name='tax_percentage',
            field=models.DecimalField(decimal_places=2, default=7.0, max_digits=5),
        ),
    ]
