# Generated by Django 5.0.6 on 2024-09-06 06:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0018_alter_admincustomercontract_tax_percentage_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admincustomercontract',
            name='tax_percentage',
        ),
        migrations.RemoveField(
            model_name='adminprocessorcontract',
            name='tax_percentage',
        ),
    ]
