# Generated by Django 5.0.6 on 2024-09-23 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=10, unique=True)),
            ],
        ),
    ]