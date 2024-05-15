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