# Generated by Django 5.0.6 on 2024-08-28 06:00

import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0011_adminprocessorcontractdocuments_document_status'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='adminprocessorcontract',
            name='per_unit_rate',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.CreateModel(
            name='AdminCustomerContract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('secret_key', models.CharField(max_length=255, unique=True)),
                ('customer_id', models.CharField(max_length=255)),
                ('crop', models.CharField(choices=[('RICE', 'Rice'), ('WHEAT', 'Wheat'), ('PEANUT', 'Peanut'), ('BEANS', 'Beans')], max_length=10)),
                ('crop_type', models.CharField(blank=True, max_length=255, null=True)),
                ('contract_amount', models.PositiveBigIntegerField()),
                ('amount_unit', models.CharField(choices=[('LBS', 'LBS'), ('MT', 'MT')], max_length=10)),
                ('per_unit_rate', models.CharField(blank=True, max_length=255, null=True)),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('contract_start_date', models.DateField()),
                ('contract_period', models.PositiveIntegerField(help_text='Warranty period')),
                ('contract_period_choice', models.CharField(choices=[('Days', 'Days'), ('Months', 'Months'), ('Year', 'Year')], default='Days', max_length=10)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Contract Initiated', 'Contract Initiated'), ('Under Review', 'Under Review'), ('Active With Documentation Processing', 'Active With Documentation Processing'), ('Active With Documentation Completed', 'Active With Documentation Completed'), ('Completed', 'Completed'), ('Terminated', 'Terminated')], max_length=255)),
                ('reason_for_rejection', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_signed', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contractUSer', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AdminCustomerContractDocuments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('document', models.FileField(blank=True, null=True, upload_to='contracts/documents/')),
                ('document_status', models.TextField(blank=True, null=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customerContractDocuments', to='contracts.admincustomercontract')),
            ],
        ),
        migrations.CreateModel(
            name='AdminCustomerSignature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('signed_at', models.DateTimeField(auto_now_add=True)),
                ('signature', models.TextField(help_text='A textual or digital representation of the signature')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customerContractSignatures', to='contracts.admincustomercontract')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='customerContractingUser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]