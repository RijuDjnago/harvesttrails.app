from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Warehouse)
admin.site.register(WarehouseUser)
admin.site.register(ProcessorWarehouseShipment)
admin.site.register(Distributor)
admin.site.register(DistributorUser)
admin.site.register(Customer)
admin.site.register(CustomerUser)
