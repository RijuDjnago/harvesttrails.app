from rest_framework import serializers
from apps.processor.models import *
from apps.processor2.models import *
from apps.growerpayments.models import EntryFeeds , GrowerPayments
from apps.growerpayments.models import NasdaqApiData
from datetime import timedelta ,datetime ,date 

class GrowerPaymentsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = GrowerPayments
        fields = ['payment_amount', 'payment_date','payment_type','payment_confirmation']

class BaleReportFarmFieldSerializer(serializers.ModelSerializer):
    delivery_date = serializers.DateField(source='dt_class',read_only=True)
    delivery_id = serializers.CharField(source='bale_id', read_only=True)
    grower_name = serializers.CharField(source='ob3',read_only=True)
    grower_pmt = serializers.SerializerMethodField()
    delivery_lbs = serializers.DecimalField(max_digits=10, decimal_places=0, source='net_wt')

    class Meta:
        model = BaleReportFarmField
        fields = ['delivery_date', 'delivery_id', 'grower_name','crop','field_name','delivery_lbs','level','delivery_value','total_price','payment_due_date','grower_pmt']

    def get_grower_pmt(self, obj):
    
        grower_payments = GrowerPayments.objects.filter(delivery_id=obj.bale_id)
        return GrowerPaymentsSerializer(grower_payments, many=True).data
    
    def get_crop(self,obj):
        crop = "COTTON"
        return (crop)
    
    def get_payment_due_date(self, instance):
        if instance.level is not None:
            if instance.dt_class :
                date_str = str(instance.dt_class).split("/")
                dd = int(date_str[1])
                mm = int(date_str[0])
                yy = int(date_str[2])
                if len(str(yy)) == 2 : 
                    yyyy = int("20{}".format(yy))
                else:
                    yyyy = yy
                # specific_date = datetime(yyyy, mm, dd)
                # new_date = specific_date + timedelta(60)
                new_date = (datetime(yyyy, mm, dd)) + timedelta(60)
                payment_due_date = new_date.strftime("%m/%d/%y")
                return payment_due_date
            else:
              return "N/A"
        else:
            return "N/A"

    def get_delivery_value(self, instance):

        if instance.dt_class :
            str_date = str(instance.dt_class )
            if '-' in str_date :
                try :
                    str_date = str_date.split('-')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = date(int(yyyy), int(mm), int(dd))
                except :
                    pass
            elif '/' in str_date :
                try :
                    str_date = str_date.split('/')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = date(int(yyyy), int(mm), int(dd))
                except :
                    pass
            else:
                finale_date = ''
        else:
            pass

        check_entry = EntryFeeds.objects.filter(grower_id = instance.ob2)
        if len(check_entry) == 0 :
            pass
        if len(check_entry) == 1 :
            var = EntryFeeds.objects.get(grower_id = instance.ob2)
        if len(check_entry) > 1 :
            check_entry_with_date = EntryFeeds.objects.filter(grower_id = instance.ob2,from_date__lte=finale_date,to_date__gte=finale_date)
            check_entry_with_no_date = EntryFeeds.objects.filter(grower_id = instance.ob2,from_date__isnull=True,to_date__isnull=True)
            if check_entry_with_date.exists() :
                var = EntryFeeds.objects.get(id = [i.id for i in check_entry_with_date][0])
            elif check_entry_with_no_date.exists() :
                var = EntryFeeds.objects.get(id = [i.id for i in check_entry_with_no_date][0])
    
        cpb_lbs = var.contract_base_price
        if cpb_lbs :
            cpb_lbs = var.contract_base_price
        else:
            cpb_lbs = 0.0
        sp_lbs = var.sustainability_premium
        if sp_lbs :
            sp_lbs = var.sustainability_premium
        else:
            sp_lbs = 0.0
        if instance.level == 'Bronze' :
            qp_lbs = 0.00
        elif instance.level == "Silver":
            qp_lbs = 0.02
        elif instance.level == "Gold":
            qp_lbs = 0.04
        elif instance.level == "None":
            qp_lbs = 0.00
                                
        if instance.level is not None:
            total_price = float(cpb_lbs) + float(sp_lbs) + float(qp_lbs)
            delivered_value = float(instance.net_wt) * float(total_price)
            del_value= "{0:.4f}".format(delivered_value)
            return del_value
          
        else:
            delivered_value = 0.00
            return delivered_value 
            
    def get_total_price(self, instance):
        if instance.dt_class :
            str_date = str(instance.dt_class )
            if '-' in str_date :
                try :
                    str_date = str_date.split('-')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = date(int(yyyy), int(mm), int(dd))
                except :
                    pass
            elif '/' in str_date :
                try :
                    str_date = str_date.split('/')
                    mm = str_date[0]
                    dd = str_date[1]
                    yy = str_date[2]
                    yyyy = f'20{yy}' if len(yy) == 2 else yy
                    finale_date = date(int(yyyy), int(mm), int(dd))
                except :
                    pass
            else:
                finale_date = ''
        else:
            pass

        check_entry = EntryFeeds.objects.filter(grower_id = instance.ob2)
        if len(check_entry) == 0 :
            pass
        if len(check_entry) == 1 :
            var = EntryFeeds.objects.get(grower_id = instance.ob2)
        if len(check_entry) > 1 :
            check_entry_with_date = EntryFeeds.objects.filter(grower_id = instance.ob2,from_date__lte=finale_date,to_date__gte=finale_date)
            check_entry_with_no_date = EntryFeeds.objects.filter(grower_id = instance.ob2,from_date__isnull=True,to_date__isnull=True)
            if check_entry_with_date.exists() :
                var = EntryFeeds.objects.get(id = [i.id for i in check_entry_with_date][0])
            elif check_entry_with_no_date.exists() :
                var = EntryFeeds.objects.get(id = [i.id for i in check_entry_with_no_date][0])
    
        cpb_lbs = var.contract_base_price
        if cpb_lbs :
            cpb_lbs = var.contract_base_price
        else:
            cpb_lbs = 0.0
        sp_lbs = var.sustainability_premium
        if sp_lbs :
            sp_lbs = var.sustainability_premium
        else:
            sp_lbs = 0.0
        if instance.level == 'Bronze' :
            qp_lbs = 0.00
        elif instance.level == "Silver":
            qp_lbs = 0.02
        elif instance.level == "Gold":
            qp_lbs = 0.04
        elif instance.level == "None":
            qp_lbs = 0.00
                                
        if instance.level is not None:
            total_price = float(cpb_lbs) + float(sp_lbs) + float(qp_lbs)
            total_prc=  "{0:.5f}".format(total_price)
            return total_prc  
        else:
            total_price = 0.00
            return total_price

    crop = serializers.SerializerMethodField(method_name='get_crop')    
    payment_due_date = serializers.SerializerMethodField(method_name='get_payment_due_date')    
    delivery_value = serializers.SerializerMethodField(method_name='get_delivery_value')    
    total_price = serializers.SerializerMethodField(method_name='get_total_price')    

class GrowerShipmentSerializer(serializers.ModelSerializer):
   
    delivery_id = serializers.DateField(source='shipment_id',read_only=True)
    grower_pmt = serializers.SerializerMethodField()
    grower_name = serializers.CharField(source='grower.name',read_only=True) 
    field_name = serializers.CharField(source='field.name',read_only=True)
   
    class Meta:
        model = GrowerShipment
        fields = ['id','delivery_date','delivery_id', 'grower_name','crop', 'variety','field_name','level','delivery_lbs','total_price','delivery_value','payment_due_date','grower_pmt']
        
    def get_grower_pmt(self, obj):
        grower_payments = GrowerPayments.objects.filter(delivery_id=obj.shipment_id)
        return GrowerPaymentsSerializer(grower_payments, many=True).data
    
    def get_delivery_date(self, instance):
        if instance.approval_date is None:
            return instance.process_date.strftime("%m/%d/%y")
        else:
            return instance.approval_date.strftime("%m/%d/%y")

    def get_payment_due_date(self, instance):
        if instance.approval_date is None:
            new_date = instance.process_date + timedelta(60)
        else:
            new_date = instance.approval_date + timedelta(60)
        return new_date.strftime("%m/%d/%y")
    
    def get_delivery_lbs(self, instance):
        if instance.received_amount is not None:
            del_lbs = int(float(instance.received_amount))
            return del_lbs
        else:
            del_lbs = int(float(instance.total_amount))
            return del_lbs

    def get_class(self,obj):
        level = "-"
        return (level)
 
    def get_total_price(self, instance):       
        var = None
        if instance.approval_date is None:
            
            check_entry_with_date = EntryFeeds.objects.filter(grower_id = instance.grower_id,from_date__lte=instance.process_date,to_date__gte=instance.process_date)
            check_entry_with_no_date = EntryFeeds.objects.filter(grower_id = instance.grower_id,from_date__isnull=True,to_date__isnull=True)

            if check_entry_with_date.exists() :
                var = EntryFeeds.objects.get(id=[i.id for i in check_entry_with_date][0])
            elif check_entry_with_no_date.exists() :
                var = EntryFeeds.objects.get(id = [i.id for i in check_entry_with_no_date][0])

        else:
            check_entry_with_date = EntryFeeds.objects.filter(grower_id = instance.grower_id,from_date__lte=instance.approval_date,to_date__gte=instance.approval_date)
            check_entry_with_no_date = EntryFeeds.objects.filter(grower_id = instance.grower_id,from_date__isnull=True,to_date__isnull=True)
            if check_entry_with_date.exists() :
                var = EntryFeeds.objects.get(id=[i.id for i in check_entry_with_date][0])  
            elif check_entry_with_no_date.exists() :
                var = EntryFeeds.objects.get(id = [i.id for i in check_entry_with_no_date][0])

        if not var :
            return None
        if var.contracted_payment_option == 'Fixed Price' :
            cpb_lbs = var.contract_base_price
            sp_lbs = var.sustainability_premium
            total_price =  float(cpb_lbs) + float(sp_lbs)
            total_prc= "{0:.5f}".format(total_price)
            return total_prc
        elif var.contracted_payment_option == 'Acreage Release' :
            cpb_lbs = var.contract_base_price
            sp_lbs = var.sustainability_premium
            total_price = float(cpb_lbs) + float(sp_lbs)
            total_prc= "{0:.5f}".format(total_price)
            return total_prc
        else:
            calculation_date = instance.approval_date
            if NasdaqApiData.objects.filter(date_api=calculation_date).count() !=0 :
                total_price_init = NasdaqApiData.objects.get(date_api=calculation_date).close_value_api
            else:
                for l in range(1,10):
                    next_date = calculation_date - timedelta(l)
                    if NasdaqApiData.objects.filter(date_api=next_date).count() !=0 :
                        total_price_init = NasdaqApiData.objects.get(date_api=next_date).close_value_api
                        break
            total_price2 = float(total_price_init) / 100
            total_price = total_price2 + 0.04
            total_prc= "{0:.5f}".format(total_price)
            return total_prc
        
    def get_delivery_value(self, instance):
        var = None 
        if instance.approval_date is None:
            check_entry_with_date = EntryFeeds.objects.filter(grower_id = instance.grower_id,from_date__lte=instance.process_date,to_date__gte=instance.process_date)
            check_entry_with_no_date = EntryFeeds.objects.filter(grower_id = instance.grower_id,from_date__isnull=True,to_date__isnull=True)
            if check_entry_with_date.exists() :
                var = EntryFeeds.objects.get(id=[i.id for i in check_entry_with_date][0])
            elif check_entry_with_no_date.exists() :
                var = EntryFeeds.objects.get(id = [i.id for i in check_entry_with_no_date][0])
        else:
            check_entry_with_date = EntryFeeds.objects.filter(grower_id = instance.grower_id,from_date__lte=instance.approval_date,to_date__gte=instance.approval_date)
            check_entry_with_no_date = EntryFeeds.objects.filter(grower_id = instance.grower_id,from_date__isnull=True,to_date__isnull=True)
            if check_entry_with_date.exists() :
                var = EntryFeeds.objects.get(id=[i.id for i in check_entry_with_date][0])  
            elif check_entry_with_no_date.exists() :
                var = EntryFeeds.objects.get(id = [i.id for i in check_entry_with_no_date][0])
        if not var :
            return None
        if var.contracted_payment_option == 'Fixed Price' :
            cpb_lbs = var.contract_base_price
            sp_lbs = var.sustainability_premium
            total_price =  float(cpb_lbs) + float(sp_lbs)
    
        elif var.contracted_payment_option == 'Acreage Release' :
            cpb_lbs = var.contract_base_price
            sp_lbs = var.sustainability_premium
            total_price = float(cpb_lbs) + float(sp_lbs)
            
        else:
            calculation_date = instance.approval_date
            if NasdaqApiData.objects.filter(date_api=calculation_date).count() !=0 :
                total_price_init = NasdaqApiData.objects.get(date_api=calculation_date).close_value_api
            else:
                for l in range(1,10):
                    next_date = calculation_date - timedelta(l)
                    if NasdaqApiData.objects.filter(date_api=next_date).count() !=0 :
                        total_price_init = NasdaqApiData.objects.get(date_api=next_date).close_value_api
                        break
            total_price2 = float(total_price_init) / 100
            total_price = total_price2 + 0.04
            
        if instance. received_amount is not None:
            del_lbs = int(float(instance.received_amount))
            delivered_value = float(del_lbs) * total_price
            del_value = "{0:.4f}".format(delivered_value)
            return del_value
        else:
            del_lbs = int(float(instance.total_amount))
            delivered_value = float(del_lbs) * total_price
            return delivered_value

    delivery_date = serializers.SerializerMethodField(method_name='get_delivery_date')
    payment_due_date = serializers.SerializerMethodField(method_name='get_payment_due_date')
    delivery_lbs = serializers.SerializerMethodField(method_name='get_delivery_lbs')
    level = serializers.SerializerMethodField(method_name='get_class')
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    delivery_value = serializers.SerializerMethodField(method_name='get_delivery_value')

class ShipmentManagementFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ['url', 'name', 'type']

    def get_url(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url

    def get_name(self, obj):
        return obj.file.name

    def get_type(self, obj):
        return obj.file.name.split('.')[-1]

class ShipmentManagementSerializer(serializers.ModelSerializer):
    files = ShipmentManagementFileSerializer(many=True)

    class Meta:
        model = ShipmentManagement
        fields = "__all__"
        
class ProcessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Processor
        fields = '__all__'  # This will include all the fields of the Processor model

class ProcessorUserSerializer(serializers.ModelSerializer):
    processor = ProcessorSerializer()

    class Meta:
        model = ProcessorUser
        fields = '__all__' 

class Processor2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Processor2
        fields = '__all__'  # This will include all the fields of the Processor model

class ProcessorUser2Serializer(serializers.ModelSerializer):
    processor2 = Processor2Serializer()

    class Meta:
        model = ProcessorUser2
        fields = '__all__' 

















