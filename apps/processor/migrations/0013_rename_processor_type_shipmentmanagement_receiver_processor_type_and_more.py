# Generated by Django 5.0.6 on 2024-05-24 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('processor', '0012_alter_file_file_linkprocessor1toprocessor'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shipmentmanagement',
            old_name='processor_type',
            new_name='receiver_processor_type',
        ),
        migrations.RemoveField(
            model_name='shipmentmanagement',
            name='production_management',
        ),
        migrations.AddField(
            model_name='shipmentmanagement',
            name='sender_processor_type',
            field=models.CharField(blank=True, choices=[('T1', 'T1'), ('T2', 'T2'), ('T3', 'T3'), ('T4', 'T4'), ('Buyer', 'Buyer')], max_length=5, null=True),
        ),
    ]