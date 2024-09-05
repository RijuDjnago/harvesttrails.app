# Generated by Django 5.0.6 on 2024-09-05 06:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0016_admincustomercontract_left_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='admincustomercontract',
            name='tax_percentage',
            field=models.FloatField(default=8.0, help_text='Enter the sales tax percenteage'),
        ),
        migrations.AddField(
            model_name='adminprocessorcontract',
            name='tax_percentage',
            field=models.FloatField(default=8.0, help_text='Enter the sales tax percenteage'),
        ),
    ]
