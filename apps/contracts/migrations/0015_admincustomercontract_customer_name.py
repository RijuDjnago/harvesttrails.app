# Generated by Django 5.0.6 on 2024-09-03 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0014_adminprocessorcontract_left_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='admincustomercontract',
            name='customer_name',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]
