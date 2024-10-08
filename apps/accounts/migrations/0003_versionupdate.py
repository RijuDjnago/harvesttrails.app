# Generated by Django 5.0.6 on 2024-07-12 06:43

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_user_is_processor3'),
    ]

    operations = [
        migrations.CreateModel(
            name='VersionUpdate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version', models.CharField(blank=True, max_length=5, null=True)),
                ('release_date', models.DateTimeField()),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.CharField(blank=True, max_length=50, null=True)),
                ('updated_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
