from django.db import models
from apps.contracts.models import AdminProcessorContract

# Create your models here.
class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    location = models.TextField(null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

class WarehouseUser(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='warehouse_user')
    contact_name = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Name')
    contact_email = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Email')
    contact_phone = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Phone')
    contact_fax = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Fax')
    p_password_raw = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.contact_email


class Distributor(models.Model):
    """Database model for distributor"""
    entity_name = models.CharField(max_length=255, null=True, blank=True)
    warehouse = models.ManyToManyField(Warehouse, blank=True)
    location = models.TextField(null=True,blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.entity_name


class DistributorUser(models.Model):
    """Database model for distributor User"""
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, null=True, blank=True,verbose_name='Select Distributor')
    contact_name = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Name')
    contact_email = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Email')
    contact_phone = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Phone')
    contact_fax = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Fax')
    p_password_raw = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.contact_email


class Customer(models.Model):
    """Database model for Customer"""
    name = models.CharField(max_length=255, null=True, blank=True)    
    location = models.TextField(null=True,blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.entity_name


class CustomerUser(models.Model):
    """Database model for customer User"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True,verbose_name='Select Customer')
    contact_name = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Name')
    contact_email = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Email')
    contact_phone = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Phone')
    contact_fax = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Fax')
    p_password_raw = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.contact_email


Carrier_type = (
    ('Rail Car','Rail Car'),
    ('Truck/Trailer','Truck/Trailer'),
)

Outbound_type = (
    ('Domestic','Domestic'),
    ('International','International'),
)

Unit_choice = (
    ("LBS","LBS"),
    ("MT","MT"),
)

class WarehouseOrder(models.Model):
    contract = models.ForeignKey(AdminProcessorContract, on_delete=models.CASCADE, null=True, blank=True, related_name='contract_order')
    invoice_request_id = models.IntegerField(null=True, blank=True)
    invoice_date = models.DateTimeField(null=True, blank=True)
    processor_id = models.IntegerField(null=True, blank=True)
    sub_total = models.CharField(max_length=255, null=True, blank=True)
    tax = models.CharField(max_length=255, null=True, blank=True)
    final_total = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    received_date = models.DateTimeField(null=True, blank=True)
    quantity_received = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.invoice_request_id


class Product(models.Model):
    order = models.ForeignKey(WarehouseOrder, on_delete=models.CASCADE, related_name='ordered_item')
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    quantity = models.CharField(max_length=255, null=True, blank=True)
    weight_unit = models.CharField(max_length=10, choices=Unit_choice)
    per_unit_rate = models.CharField(max_length=255, null=True, blank=True)
    unit_total_cost = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class WarehouseStock(models.Model):
    order = models.ForeignKey(WarehouseOrder, on_delete=models.CASCADE, related_name='order_stock', null=True, blank=True)
    product_name = models.CharField(max_length=255, null=True, blank=True)
    final_stock = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'Order - {self.order.invoice_request_id} | product- {self.product_name} | stock- {self.final_stock}'

status_choices = (
    ('Released','Released'),
    ('At Border', 'At Border'),
    ('Crossed Border','Crossed Border'),
    ('Received','Received'),
    ('Released/Received','Released/Received'),
)

class ProcessorWarehouseShipment(models.Model):
    contract = models.ForeignKey(AdminProcessorContract, on_delete=models.CASCADE, null=True, blank=True, related_name='contract_delivery')
    order = models.ForeignKey(WarehouseOrder, on_delete=models.CASCADE, null=True, blank=True, related_name='order_delivery')

    processor_id = models.CharField(max_length=10, null=True, blank=True)
    processor_type = models.CharField(max_length=5, null=True, blank=True)
    processor_entity_name = models.CharField(max_length=255, null=True, blank=True)
    processor_sku_list = models.JSONField(null=True, blank=True)

    carrier_type = models.CharField(max_length=15, choices=Carrier_type)
    outbound_type = models.CharField(max_length=15, choices=Outbound_type)

    date_pulled= models.DateTimeField(auto_now_add=True)
    purchase_order_name = models.CharField(max_length=255, null=True, blank=True)
    purchase_order_number = models.CharField(max_length=255, null=True, blank=True)
    lot_number = models.CharField(max_length=255, null=True, blank=True)

    ship_quantity = models.PositiveIntegerField(null=True, blank=True)    
    gross_weight = models.CharField(max_length=255, null=True, blank=True)
    net_weight = models.CharField(max_length=255, null=True, blank=True)
    weight_unit = models.CharField(max_length=10, choices=Unit_choice)
    contract_weight_left = models.CharField(max_length=255, null=True, blank=True)   

    border_receive_date = models.DateField(null=True, blank=True)
    border_leaving_date = models.DateField(null=True, blank=True)

    distributor_receive_date = models.DateField(null=True, blank=True)
    distributor_leaving_date = models.DateField(null=True, blank=True)

    border_back_receive_date = models.DateField(null=True, blank=True)
    border_back_leaving_date = models.DateField(null=True, blank=True)

    processor_receive_date = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=255, choices=status_choices, null=True, blank=True)
    
    distributor_id = models.CharField(max_length=255, null=True, blank=True)
    distributor_entity_name = models.CharField(max_length=255, null=True, blank=True)

    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    warehouse_id = models.CharField(max_length=255, null=True, blank=True)
    warehouse_name = models.CharField(max_length=255, null=True, blank=True)
    warehouse_order_id = models.CharField(max_length=255, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.contract and self.contract_weight_left:
            # Convert contract_weight_left to float first, then to int
            left_amount_int = int(float(self.contract_weight_left))
            
            # Update the left_amount in the AdminProcessorContract model
            AdminProcessorContract.objects.filter(id=self.contract.id).update(left_amount=left_amount_int)
            
            super().save(*args, **kwargs)
   

    def __str__(self):
        return f'{self.processor_entity_name} - {self.contract.crop}'


class ProcessorWarehouseShipmentDocuments(models.Model):
    shipment = models.ForeignKey(ProcessorWarehouseShipment, on_delete=models.CASCADE)
    document_name = models.CharField(max_length=255, null=True, blank=True)
    document_file = models.FileField(upload_to='processor_distributor_shipment/file/', null=True, blank=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True)   

    def __str__(self):
        return f'Shipment documents for {self.document_name}'
    
class CarrierDetails(models.Model):
    shipment = models.ForeignKey(ProcessorWarehouseShipment, on_delete=models.CASCADE, related_name='shipment_carrier')
    carrier_id = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.shipment.carrier_type


