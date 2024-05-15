from datetime import datetime
from django.db import models
from django.urls import reverse
from django.utils import timezone
import uuid

class Contracts(models.Model):
    """Database model for field"""
    name = models.CharField(unique=True, max_length=200)
    envelope_id = models.CharField(max_length=200, null=True)
    is_signed = models.BooleanField(default=False)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Created Date')
    modified_date = models.DateTimeField(auto_now=True, verbose_name='Modified Date')
    contract_doc = models.FileField(upload_to='demo_documents/', verbose_name='Contract Document', blank=True)

    def __str__(self):
        """Returns string representation of farm"""
        # return f'{self.id}:{self.name}'
        return f'{self.name}'

    def get_fields(self):
        """This method return all the field name and their value of all objects of field model."""
        return [(contract.name, contract.value_from_object(self)) for contract in self.__class__._meta.contracts]


class GrowerContracts(models.Model):
    """Database model for field"""
    contract = models.ForeignKey('contracts.Contracts', on_delete=models.CASCADE, null=False, blank=False)
    contract_url = models.TextField()
    grower = models.ForeignKey('grower.Grower', on_delete=models.CASCADE, null=False, blank=False)
    is_signed = models.BooleanField(default=False)
    envelope_id = models.CharField(max_length=200, null=True)
    envelope_uri = models.URLField(null=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Created Date')
    modified_date = models.DateTimeField(auto_now=True, verbose_name='Modified Date')

    def __str__(self):
        """Returns string representation of farm"""
        # return f'{self.id}:{self.name}'
        return f'contract : {self.contract}, grower : {self.grower}, contract_url: {self.contract_url}'


class SignedContracts(models.Model):
    """Database model for field"""
    signature = models.TextField()
    contract = models.ForeignKey('contracts.Contracts', on_delete=models.CASCADE, null=False, blank=False)
    grower = models.ForeignKey('grower.Grower', on_delete=models.CASCADE, null=False, blank=False)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Created Date')

    def __str__(self):
        """Returns string representation of farm"""
        # return f'{self.id}:{self.name}'
        return f'{self.id}'


class ContractsVerifiers(models.Model):
    """Database model for field"""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    contract = models.ForeignKey(
        'contracts.Contracts',
        on_delete=models.CASCADE,
        related_name="contract_verifiers",
        null=False,
        blank=False
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Created Date')

    def __str__(self):
        """Returns string representation of farm"""
        # return f'{self.id}:{self.name}'
        return f'{self.name}'


class VerifiedSignedContracts(models.Model):
    """Database model for field"""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    signature = models.TextField(
        null=True,
        blank=True
    )
    signed_contracts = models.ForeignKey(
        'contracts.SignedContracts',
        on_delete=models.CASCADE,
        related_name="signedcontracts",
        null=False,
        blank=False
    )
    is_verified = models.BooleanField(default=False)
    verified_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Created Date')

    def __str__(self):
        """Returns string representation of farm"""
        # return f'{self.id}:{self.name}'
        return f'{self.name}'
