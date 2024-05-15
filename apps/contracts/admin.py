from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from . import models

"""Registering  all the field application models here to be viewed in django admin panel"""

admin.site.register(models.Contracts)
admin.site.register(models.SignedContracts)
admin.site.register(models.ContractsVerifiers)
admin.site.register(models.VerifiedSignedContracts)

