from django.db import models
from apps.processor.models import *
# from apps.processor.models import BaleReportFarmField

# Create your models here.

class Processor2(models.Model):
    """Database model for processor"""
    fein = models.CharField(max_length=250, null=True, blank=True,verbose_name='FEIN')
    entity_name = models.CharField(max_length=250, null=True, blank=True,verbose_name='Entity Name')
    billing_address = models.TextField(null=True, blank=True,verbose_name='Billing Address')
    shipping_address = models.TextField(null=True, blank=True,verbose_name='Shipping Address')
    main_number = models.CharField(max_length=250, null=True, blank=True,verbose_name='Main Number')
    main_fax = models.CharField(max_length=250, null=True, blank=True,verbose_name='Main Fax')
    website = models.TextField(null=True, blank=True,verbose_name='Website')

    def __str__(self):
        return self.entity_name

class ProcessorUser2(models.Model):
    """Database model for processor User"""
    processor2 = models.ForeignKey(Processor2, on_delete=models.CASCADE, null=True, blank=True,verbose_name='Select Processor2')
    contact_name = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Name')
    contact_email = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Email')
    contact_phone = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Phone')
    contact_fax = models.CharField(max_length=250, null=True, blank=True,verbose_name='Contact Fax')
    p_password_raw = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.contact_email

class AssignedBaleProcessor2(models.Model):
    processor2 = models.ForeignKey(Processor2, on_delete=models.CASCADE, null=True, blank=True,verbose_name='Select Processor2')
    bale = models.ForeignKey(BaleReportFarmField, on_delete=models.CASCADE, null=True, blank=True,verbose_name='Select Bale')
    assigned_bale = models.CharField(max_length=250, null=True, blank=True,verbose_name='Bale ID')
    prod_id = models.CharField(max_length=200, null=True, blank=True)
    wt = models.CharField(max_length=200, null=True, blank=True)
    net_wt = models.CharField(max_length=200, null=True, blank=True)
    load_id = models.CharField(max_length=200, null=True, blank=True)
    dt_class = models.CharField(max_length=200, null=True, blank=True)
    gr = models.CharField(max_length=200, null=True, blank=True)
    lf = models.CharField(max_length=200, null=True, blank=True)
    st = models.CharField(max_length=200, null=True, blank=True)
    mic = models.CharField(max_length=200, null=True, blank=True)
    ex = models.CharField(max_length=200, null=True, blank=True)
    rm = models.CharField(max_length=200, null=True, blank=True)
    str_no = models.CharField(max_length=200, null=True, blank=True)
    cgr = models.CharField(max_length=200, null=True, blank=True)
    rd = models.CharField(max_length=200, null=True, blank=True)
    tr = models.CharField(max_length=200, null=True, blank=True)
    unif = models.CharField(max_length=200, null=True, blank=True)
    len_num = models.CharField(max_length=200, null=True, blank=True)
    elong = models.CharField(max_length=200, null=True, blank=True)
    cents_lb = models.CharField(max_length=200, null=True, blank=True)
    loan_value = models.CharField(max_length=200, null=True, blank=True)
    warehouse_wt = models.CharField(max_length=200, null=True, blank=True)
    warehouse_bale_id = models.CharField(max_length=200, null=True, blank=True)
    warehouse_wh_id = models.CharField(max_length=200, null=True, blank=True)

    farm_name = models.CharField(max_length=200, null=True, blank=True)
    sale_status = models.CharField(max_length=200, null=True, blank=True)
    wh_id = models.CharField(max_length=200, null=True, blank=True)
    ob1 = models.CharField(max_length=200, null=True, blank=True)
    gin_date = models.DateField(null=True, blank=True)
    farm_id = models.CharField(max_length=200, null=True, blank=True)
    field_name = models.CharField(max_length=200, null=True, blank=True)
    pk_num = models.CharField(max_length=200, null=True, blank=True)
    grower_idd = models.CharField(max_length=200, null=True, blank=True, verbose_name='grower id')
    grower_name = models.CharField(max_length=200, null=True, blank=True, verbose_name='grower name')
    field_idd = models.CharField(max_length=200, null=True, blank=True, verbose_name='field id')
    certificate = models.CharField(max_length=200, null=True, blank=True, verbose_name='certificate')
    value = models.CharField(max_length=200, null=True, blank=True)
    level = models.CharField(max_length=200, null=True, blank=True)
    crop_variety = models.CharField(max_length=200, null=True, blank=True)
    mark_id = models.CharField(max_length=200, null=True, blank=True)
    gin_id = models.CharField(max_length=200, null=True, blank=True)


class LinkToProcessor2(models.Model):    
    grower = models.ForeignKey(Grower, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Select grower")
    processor1 = models.ForeignKey(Processor, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Select processor")
    processor2 = models.ForeignKey(Processor2, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Select processor2")


class GrowerShipmentToProcessor2(models.Model):
    processor = models.ForeignKey(Processor2, on_delete=models.CASCADE, null=True, blank=True,verbose_name='Select Processor')
    grower = models.ForeignKey(Grower, on_delete=models.CASCADE, null=True, blank=True,verbose_name='Select Grower')
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE, null=True, blank=True,verbose_name='Select Storage')
    field = models.ForeignKey(Field, on_delete=models.CASCADE, null=True, blank=True,verbose_name='Select Field')
    crop = models.CharField(max_length=200, null=True, blank=True,verbose_name='Select Item')
    variety = models.CharField(max_length=200, null=True, blank=True,verbose_name='Select Variety')
    amount = models.CharField(max_length=200, null=True, blank=True,verbose_name='Amount')
    amount2 = models.CharField(max_length=200, null=True, blank=True,verbose_name='Amount2')
    sustainability_score = models.CharField(max_length=200, null=True, blank=True,verbose_name='Sustainability Score')
    echelon_id = models.CharField(max_length=200, null=True, blank=True,verbose_name='Echelon Id')
    date_time = models.DateTimeField(auto_created=True, auto_now_add=True,verbose_name='Shipment Date')
    shipment_id = models.CharField(max_length=200, null=True, blank=True,verbose_name='Shipment Id')
    qr_code = models.TextField(null=True, blank=True,verbose_name='QR code')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True,verbose_name='Select Location')
    date_time_location = models.DateTimeField(auto_created=True, auto_now_add=True,verbose_name='Location Date')
    process_amount = models.CharField(max_length=200, null=True, blank=True,verbose_name='Processed Amount')
    process_date = models.DateField(auto_created=True, auto_now_add=True,verbose_name='Processed Date')
    process_time = models.TimeField(auto_created=True, auto_now_add=True,verbose_name='Processed Time')
    sku = models.CharField(max_length=200, null=True, blank=True,verbose_name='SKU ID')
    module_number = models.CharField(max_length=200, null=True, blank=True,verbose_name='Module Tag #')
    unit_type = models.CharField(max_length=200, null=True, blank=True,verbose_name='Unit Type')
    unit_type2 = models.CharField(max_length=200, null=True, blank=True,verbose_name='Unit Type2')
    total_amount = models.CharField(max_length=200, null=True, blank=True,verbose_name='Total Amount')
    received_amount = models.CharField(max_length=200, null=True, blank=True,verbose_name='Received Amount')
    token_id = models.CharField(max_length=200, null=True, blank=True,verbose_name='Token Id')
    approval_date = models.DateField(verbose_name='Approval Date', null=True, blank=True)
    status = models.CharField(max_length=200,choices=STATUS_CHOICES,default="")
    #30-02-23
    reason_for_disapproval = models.CharField(max_length=200, null=True, blank=True,verbose_name='Reason For Disapproval')
    moisture_level = models.CharField(max_length=200, null=True, blank=True,verbose_name='Moisture Level')
    fancy_count = models.CharField(max_length=200, null=True, blank=True,verbose_name='Fancy Count')
    head_count = models.CharField(max_length=200, null=True, blank=True,verbose_name='Head Count')
    bin_location_processor = models.CharField(max_length=200, null=True, blank=True,verbose_name='Bin Location at Processor')
    files = models.ManyToManyField(GrowerShipmentFile, related_name='growershipmentfile', blank=True)
    processor2_idd = models.CharField(max_length=200, null=True, blank=True)
    processor2_name = models.CharField(max_length=250, null=True, blank=True)
    qr_code = models.FileField(upload_to='qr_code/',null=True, blank=True)
    # lot_number = models.CharField(max_length=200, null=True, blank=True)
    # volume_shipped = models.CharField(max_length=200, null=True, blank=True)
    # sender = models.CharField(max_length=200,choices=SENDER_CHOICES,default="")
    
    class Meta:
        ordering = ('-date_time',)

    def __str__(self):
        return f"Shipment Id = {self.shipment_id}, Grower = {self.grower.name}, Processor = {self.processor.entity_name}"
