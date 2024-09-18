from django.db import models
from apps.accounts.models import User
from decimal import Decimal
import secrets
import string
from datetime import datetime, timedelta
from apps.contracts.models import AdminProcessorContract, AdminCustomerContract, CropDetails, CustomerContractCropDetails

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

credit_term_choice = (
    (0,'Pay on invoice receipt'),
    (0,'Pay while ordering'),
    (30, '30 days'),
    (60, '60 days'),
    (90, '90 days'),
)
class Customer(models.Model):
    """Database model for Customer"""
    name = models.CharField(max_length=255, null=True, blank=True)    
    location = models.TextField(null=True,blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True,verbose_name='Billing Address')
    shipping_address = models.TextField(null=True, blank=True,verbose_name='Shipping Address')
    credit_terms = models.IntegerField(choices=credit_term_choice, default=30)
    is_tax_payable = models.BooleanField(default=False)
    tax_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name


class CustomerUser(models.Model):
    """Database model for customer User"""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True,verbose_name='Select Customer')
    contact_name = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Name')
    contact_email = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Email')
    contact_phone = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Phone')
    contact_fax = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Fax')
    p_password_raw = models.CharField(max_length=250, null=True, blank=True)
    stripe_id = models.CharField(max_length=50,unique=True, null=True, blank=True)

    def __str__(self):
        return self.contact_email
    

from django.utils import timezone
class CustomerDocuments(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    document_name = models.CharField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to='customer_documents/', null=True, blank=True)
    document_status = models.CharField(max_length=255, null=True, blank=True)
    uploaded_at = models.DateTimeField( default=timezone.now)

    def __str__(self):
        return f"Documents for customer - {self.customer.name}"


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

def generate_secret_key_shipment( length=32):
    """Generate a unique secret key with the format HT+date+random_number."""    
    random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    date_part = datetime.now().strftime("%Y%m%d")    
    random_number = secrets.randbelow(900) + 100  
    secret_key = f"HTSH{date_part}{random_number}"
    return secret_key

def generate_secret_key_invoice(length=32):
    """Generate a unique secret key with the format HT+date+random_number."""    
    random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))
    date_part = datetime.now().strftime("%Y%m%d")
    random_number = secrets.randbelow(900) + 100   
    secret_key = f"HTINV{date_part}{random_number}"
    return secret_key


class ProcessorWarehouseShipment(models.Model):
    shipment_id = models.CharField(max_length=255, unique=True)
    invoice_id = models.CharField(max_length=255, unique=True)
    contract = models.ForeignKey(AdminProcessorContract, on_delete=models.CASCADE, null=True, blank=True, related_name='contract_delivery')
    order = models.ForeignKey(WarehouseOrder, on_delete=models.CASCADE, null=True, blank=True, related_name='order_delivery')
    crop_id = models.CharField(max_length=255, null=True, blank=True)
    crop = models.CharField(max_length=255, null=True, blank=True)

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
    ship_weight = models.FloatField(max_length=255, null=True, blank=True)  
    gross_weight = models.FloatField(max_length=255, null=True, blank=True)
    net_weight = models.FloatField(max_length=255, null=True, blank=True)
    weight_unit = models.CharField(max_length=10, choices=Unit_choice)
    contract_weight_left = models.FloatField(max_length=255, null=True, blank=True)   

    border_receive_date = models.DateTimeField(null=True, blank=True)
    border_leaving_date = models.DateTimeField(null=True, blank=True)

    distributor_receive_date = models.DateTimeField(null=True, blank=True)
    distributor_leaving_date = models.DateTimeField(null=True, blank=True)

    border_back_receive_date = models.DateTimeField(null=True, blank=True)
    border_back_leaving_date = models.DateTimeField(null=True, blank=True)

    processor_receive_date = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=255, choices=status_choices, null=True, blank=True)
    
    distributor_id = models.CharField(max_length=255, null=True, blank=True)
    distributor_entity_name = models.CharField(max_length=255, null=True, blank=True)

    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)
    warehouse_id = models.CharField(max_length=255, null=True, blank=True)
    warehouse_name = models.CharField(max_length=255, null=True, blank=True)
    warehouse_order_id = models.CharField(max_length=255, null=True, blank=True)

    total_payment = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True) 
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    invoice_approval = models.BooleanField(default=False)
    approval_time = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
      
        if is_new:
            if not self.shipment_id:
                self.shipment_id = generate_secret_key_shipment()
            if not self.invoice_id:
                self.invoice_id = generate_secret_key_invoice()
      
        if self.contract and self.net_weight:
            contract_details = CropDetails.objects.filter(contract=self.contract).first()

            if contract_details:
                contract_unit = contract_details.amount_unit
                shipment_unit = self.weight_unit                
               
                if contract_unit == "LBS" and shipment_unit == "MT":
                    net_weight_in_contract_unit = float(self.net_weight) * 2204.62
                elif contract_unit == "MT" and shipment_unit == "LBS":
                    net_weight_in_contract_unit = float(self.net_weight) / 2204.62
                else:
                    net_weight_in_contract_unit = float(self.net_weight)
               
                if contract_details.per_unit_rate:
                    per_unit_rate = float(contract_details.per_unit_rate)
                    self.total_payment = (per_unit_rate * net_weight_in_contract_unit)
                
                if hasattr(self.contract, 'tax_percentage'):
                    tax_percentage = float(self.contract.tax_percentage)
                    total_payment_float = float(self.total_payment)
                    self.tax_amount = (total_payment_float * tax_percentage) / 100
       
        super().save(*args, **kwargs)
        contract_details = CropDetails.objects.filter(contract=self.contract).first()
        
        if self.contract and contract_details:
           
            left_amount = contract_details.left_amount if contract_details.left_amount else contract_details.contract_amount
            left_amount -= float(self.contract_weight_left)
            contract_details.left_amount = max(0, left_amount)
            contract_details.save()
     
        if is_new:
            log_entry = ProcessorShipmentLog(
                shipment=self,
                description=f"A new shipment was created from processor '{self.processor_entity_name}' of {self.net_weight}{self.weight_unit} {self.crop} under contract '{self.contract}'."
                
            )
            log_entry.save()

    def __str__(self):
        return f'{self.contract.secret_key} || {self.processor_entity_name} - {self.crop}'


class ProcessorWarehouseShipmentDocuments(models.Model):
    shipment = models.ForeignKey(ProcessorWarehouseShipment, on_delete=models.CASCADE)
    document_name = models.CharField(max_length=255, null=True, blank=True)
    document_file = models.FileField(upload_to='processor_distributor_shipment/file/', null=True, blank=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True)   

    def __str__(self):
        return f'Shipment documents for {self.shipment.id}'


class CarrierDetails(models.Model):
    shipment = models.ForeignKey(ProcessorWarehouseShipment, on_delete=models.CASCADE, related_name='shipment_carrier')
    carrier_id = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.shipment.carrier_type


class ProcessorShipmentLog(models.Model):
    shipment = models.ForeignKey(ProcessorWarehouseShipment, on_delete=models.CASCADE, related_name='shipment_log')    
    description = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Shipment - {self.shipment}, contract - {self.shipment.contract.secret_key}'
    

class WarehouseCustomerShipment(models.Model):
    shipment_id = models.CharField(max_length=255, unique=True)
    invoice_id = models.CharField(max_length=255, unique=True)
    contract = models.ForeignKey(AdminCustomerContract, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(WarehouseOrder, on_delete=models.CASCADE, null=True, blank=True)
    crop_id = models.CharField(max_length=255, null=True, blank=True)
    crop = models.CharField(max_length=255, null=True, blank=True)

    warehouse_id = models.CharField(max_length=255, null=True, blank=True)
    warehouse_name = models.CharField(max_length=255, null=True, blank=True)
    distributor_id = models.CharField(max_length=255, null=True, blank=True)
    distributor_name = models.CharField(max_length=255, null=True, blank=True)

    carrier_type = models.CharField(max_length=15, choices=Carrier_type)
    outbound_type = models.CharField(max_length=15, choices=Outbound_type)

    date_pulled= models.DateTimeField(auto_now_add=True)
    purchase_order_name = models.CharField(max_length=255, null=True, blank=True)
    purchase_order_number = models.CharField(max_length=255, null=True, blank=True)
    lot_number = models.CharField(max_length=255, null=True, blank=True)

    ship_quantity = models.PositiveIntegerField(null=True, blank=True)    
    ship_weight = models.FloatField(max_length=255, null=True, blank=True) 
    gross_weight = models.FloatField(max_length=255, null=True, blank=True)
    net_weight = models.FloatField(max_length=255, null=True, blank=True)
    weight_unit = models.CharField(max_length=10, choices=Unit_choice)
    contract_weight_left = models.FloatField(max_length=255, null=True, blank=True)   

    border_receive_date = models.DateTimeField(null=True, blank=True)
    border_leaving_date = models.DateTimeField(null=True, blank=True)

    customer_receive_date = models.DateTimeField(null=True, blank=True)
    customer_leaving_date = models.DateTimeField(null=True, blank=True)

    border_back_receive_date = models.DateTimeField(null=True, blank=True)
    border_back_leaving_date = models.DateTimeField(null=True, blank=True)

    warehouse_receive_date = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=255, choices=status_choices, null=True, blank=True)    

    customer_id = models.CharField(max_length=255, null=True, blank=True)
    customer_name = models.CharField(max_length=255, null=True, blank=True)

    total_payment = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)  
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  
    is_paid = models.BooleanField(default=False)
    invoice_approval = models.BooleanField(default=False)
    approval_time = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
      
        if is_new:
            if not self.shipment_id:
                self.shipment_id = generate_secret_key_shipment()
            if not self.invoice_id:
                self.invoice_id = generate_secret_key_invoice()
       
        if self.contract and self.net_weight:
            contract_details = CustomerContractCropDetails.objects.filter(contract=self.contract).first()

            if contract_details:
                contract_unit = contract_details.amount_unit
                shipment_unit = self.weight_unit                
                
                if contract_unit == "LBS" and shipment_unit == "MT":
                    net_weight_in_contract_unit = float(self.net_weight) * 2204.62
                elif contract_unit == "MT" and shipment_unit == "LBS":
                    net_weight_in_contract_unit = float(self.net_weight) / 2204.62
                else:
                    net_weight_in_contract_unit = float(self.net_weight)
               
                if contract_details.per_unit_rate:
                    per_unit_rate = float(contract_details.per_unit_rate)
                    self.total_payment = (per_unit_rate * net_weight_in_contract_unit)
                
                if self.contract:
                    customer = Customer.objects.filter(id=int(self.contract.customer_id)).first()
                    if customer.is_tax_payable == True:
                        tax_percentage = float(customer.tax_percentage)
                        total_payment_float = float(self.total_payment)
                        self.tax_amount = (total_payment_float * tax_percentage) / 100

        
        super().save(*args, **kwargs)
        contract_details = CustomerContractCropDetails.objects.filter(contract=self.contract).first()
        
        if self.contract and contract_details:        
            left_amount = contract_details.left_amount if contract_details.left_amount else contract_details.contract_amount
            left_amount -= float(self.contract_weight_left)
            contract_details.left_amount = max(0, left_amount) 
            contract_details.save()

        if is_new:
            log_entry = WarehouseShipmentLog(
                shipment=self,
                description=f"A new shipment was created from warehouse '{self.warehouse_name}' of {self.net_weight}{self.weight_unit} {self.crop} under contract '{self.contract}'."
            )
            log_entry.save()

    def __str__(self):
        return f'{self.contract.secret_key} || {self.warehouse_name} || {self.customer_name}'


class WarehouseCustomerShipmentDocuments(models.Model):
    shipment = models.ForeignKey(WarehouseCustomerShipment, on_delete=models.CASCADE)
    document_name = models.CharField(max_length=255, null=True, blank=True)
    document_file = models.FileField(upload_to='warehouse_shipment/file/', null=True, blank=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True)   

    def __str__(self):
        return f'Shipment documents for {self.shipment.id}'


class CarrierDetails2(models.Model):
    shipment = models.ForeignKey(WarehouseCustomerShipment, on_delete=models.CASCADE, related_name='customer_shipment_carrier')
    carrier_id = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.shipment.carrier_type


class WarehouseShipmentLog(models.Model):
    shipment = models.ForeignKey(WarehouseCustomerShipment, on_delete=models.CASCADE, related_name='shipmentLog')    
    description = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'Shipment - {self.shipment}, contract - {self.shipment.contract.secret_key}'

ReciveUserType = [
    ('Admin', 'Admin'),
    ('Processor1', 'Processor1'),
    ('Processor2', 'Processor2')
]

SenderUserType = [
    ('Admin', 'Admin'),
    ('Customer', 'Customer')
] 
shipment_type = (
    ('warehouse','warehouse'),
    ('processor', 'processor'),
)  

class PaymentForShipment(models.Model):
    warehouse_shipment = models.ForeignKey(WarehouseCustomerShipment, on_delete=models.CASCADE, null=True, blank=True)
    processor_shipment = models.ForeignKey(ProcessorWarehouseShipment, on_delete=models.CASCADE, null=True, blank=True)
    shipment_type = models.CharField(max_length=25, choices=shipment_type)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    currency = models.CharField(max_length=10)
    payment_id = models.CharField(max_length=90)
    payment_responce = models.JSONField(null=True, blank=True)
    payment_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_user")
    user_type = models.CharField(max_length=100, choices=SenderUserType)
    payment_recived_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reciver_user")
    payment_recived_user_type = models.CharField(max_length=100, choices=ReciveUserType)
    status = models.BooleanField(default=False)
    paid_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        shipment = self.warehouse_shipment.shipment_id if self.warehouse_shipment else self.processor_shipment.shipment_id
        return f"{shipment} || {self.payment_by.username}"


