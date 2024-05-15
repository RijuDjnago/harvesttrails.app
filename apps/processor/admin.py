from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Processor)
admin.site.register(ProcessorUser)
admin.site.register(Location)
admin.site.register(LinkGrowerToProcessor)
admin.site.register(GrowerShipment)
admin.site.register(ShipmentManagement)
admin.site.register(GrowerShipmentFile)
admin.site.register(File)
