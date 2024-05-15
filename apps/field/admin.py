from django.contrib import admin

from import_export import resources
from import_export.admin import ImportExportModelAdmin

from . import models

"""Registering  all the field application models here to be viewed in django admin panel"""

admin.site.register(models.Field, ImportExportModelAdmin)
admin.site.register(models.CsvToField)
admin.site.register(models.ShapeFileDataCo)
admin.site.register(models.FieldUpdated)

class FieldResource(resources.ModelResource):
    class Meta:
        model = models.Field
        import_id_fields = ('id',)
        exclude = ('id', 'farm', 'grower', )
