# Generated by Django 5.0.6 on 2024-09-05 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouseManagement', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentforshipment',
            name='paid_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]