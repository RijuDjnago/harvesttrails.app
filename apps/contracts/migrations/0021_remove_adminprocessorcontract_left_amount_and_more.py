# Generated by Django 5.0.6 on 2024-09-06 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0020_remove_adminprocessorcontract_amount_unit_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adminprocessorcontract',
            name='left_amount',
        ),
        migrations.AddField(
            model_name='cropdetails',
            name='left_amount',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]