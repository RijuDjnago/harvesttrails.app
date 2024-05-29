from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from apps.processor.models import *
from apps.accounts.models import *
import string
import random
from django.core.mail import send_mail
from datetime import date
from django.db.models import Q
import csv
import pandas as pd
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from apps.processor.models import * 
from apps.processor2.models import *
from apps.growerpayments.models import *
import re
from apps.processor.views import generate_shipment_id



# Create your views here.


characters = list(string.ascii_letters + string.digits + "@#$%")
def generate_random_password():
    length = 8
    
    random.shuffle(characters)
    password =[]
    
    for i in range(length):
        password.append(random.choice(characters))
    return "".join(password)    

characters2 = list(string.ascii_letters + string.digits)


@login_required()   #create processor3
def add_processor3(request):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        
        if request.method == "POST":
            fein = request.POST.get('fein')
            entity_name = request.POST.get('entity_name')
            billing_address = request.POST.get('billing_address')
            shipping_address = request.POST.get('shipping_address')
            main_number = request.POST.get('main_number')
            main_fax = request.POST.get('main_fax')
            website = request.POST.get('website')
            contact_name = request.POST.get('contact_name')
            contact_email = request.POST.get('contact_email')
            contact_phone = request.POST.get('contact_phone')
            contact_fax = request.POST.get('contact_fax')
            
            counter = request.POST.get('counter')
            p_password_raw = generate_random_password()
            processor3 = Processor3(fein=fein,entity_name=entity_name,billing_address=billing_address,shipping_address=shipping_address,main_number=main_number,main_fax=main_fax,website=website)
            processor3.save()
            
            if User.objects.filter(email = contact_email).exists():
                messages.error(request,'This email is already exists')
            else:
                processor3_user = ProcessorUser3(processor3_id = processor3.id ,contact_name=contact_name,contact_email=contact_email,contact_phone=contact_phone,contact_fax=contact_fax,p_password_raw =p_password_raw )
                processor3_user.save()
                user = User(email = contact_email ,username= contact_email ,first_name=contact_name)
                user.set_password(p_password_raw)
                user.password_raw = p_password_raw
                user.is_processor3=True
                user.is_active=True
                user.save()
                user.role.add(Role.objects.get(role ='Processor3'))
                
                if int(counter) > 0 :
                    for i in range(1,int(counter)+1):
                        contact_name = request.POST.get('contact_name{}'.format(i))
                        contact_email= request.POST.get('contact_email{}'.format(i))
                        contact_phone = request.POST.get('contact_phone{}'.format(i))
                        contact_fax = request.POST.get('contact_fax{}'.format(i))
                        if User.objects.filter(email = contact_email).exists():
                            messages.error(request,'This email is already exists')
                        else:
                            password = generate_random_password()
                            processor_user3 = ProcessorUser3(processor3_id = processor3.id ,contact_name =contact_name ,contact_email=contact_email,contact_phone=contact_phone,contact_fax=contact_fax,p_password_raw =password)  
                            processor_user3.save()
                            user = User(email = contact_email ,username= contact_email ,first_name = contact_name)
                            user.set_password(p_password_raw)
                            user.password_raw = (p_password_raw)
                            user.is_processor3=True
                            user.is_active=True
                            user.save()
                            user.role.add(Role.objects.get(role = 'Processor3'))
            messages.success(request,'New Tier 3 Processor Added Successfully')                   
            return redirect('list_processor3')                
        return render(request, 'processor3/add_processor3.html' , context)       
                
                        
@login_required()  # show processor3 list
def processor3_list(request):
    context={}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        processor3 = ProcessorUser2.objects.filter(processor2__processor_type__type_name="T3")
        context['processor'] = processor3
        return render(request,'processor3/list_processor3.html',context)
    else:
        return redirect('login')   
    
    # processor 3     
    if request.user.is_processor3:
        pass
        
    
@login_required()  # processor3 value edit
def processor3_update(request,pk):
    context={}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        obj_id  = ProcessorUser3.objects.get(id = pk)
        context['processor3'] = obj_id
        processor3 = Processor3.objects.get(id = obj_id.processor3_id )
        context['processor_3']  = processor3
        processor_email = obj_id.contact_email
        user = User.objects.get(email = processor_email)
        if request.method == 'POST':
            email_update = request.POST.get('contact_email1')
            name_update = request.POST.get('contact_name1')
            phone_update = request.POST.get('contact_phone1')
            fax_update = request.POST.get('contact_fax1')
            
            # obj_id.contact_email = email_update
            obj_id.contact_name = name_update
            obj_id.contact_phone = phone_update
            obj_id.contact_fax = fax_update
            obj_id.save()
            
            if email_update != processor_email:
                user.email = email_update
                user.username = email_update
                user.first_name = name_update
                user.save()
                obj_id.contact_email = email_update
                obj_id.save()
            else:
                user.first_name = name_update
                user.save()    
            messages.success(request,'Tire3 Processor Updated Successfully')  
            return redirect('list_processor3')
        return render(request , 'processor3/update_processor3.html', context)
    else:
        return redirect('list_processor3')       
    
 
@login_required()   #processor3 change password
def processor3_change_password(request,pk):
    context={}
    if request.user.is_superuser or 'SubAdmin' in  request.user.get_role() or 'SuperUser' in request.user.get_role():
        obj_processor3 = ProcessorUser3.objects.get(id = pk)
        user = User.objects.get(email = obj_processor3.contact_email)
        context["processor3"] = user
        
        if request.method == 'POST':
            password1= request.POST.get('password1')
            password2= request.POST.get('password2')
            if len(password1) != 0 and len(password2) != 0 and password1 != None and password2 != None and password1 == password2:
                password = make_password(password1)
                user.passowrd = password
                user.password_raw = password1
                user.save()
                obj_processor3.p_password_raw = password1
                obj_processor3.save()
                messages.success(request,'Password Changed Successfully')
        return render(request,'processor3/processor3_change_password.html',context)        
    else:
        return redirect('dashboard')            
    
    
@login_required()  #processor3 delete
def processor3_delete(request,pk):
    # obj_processor3 = ProcessorUser3.objects.get(id = pk)    
    # user = User.objects.get(email = obj_processor3.contact_email)
    # obj_processor3.delete()
    # user.delete()
    # return HttpResponse(1)
    obj_p3_user = ProcessorUser3.objects.get(id = pk)
    check_p3 = Processor3.objects.get(id = obj_p3_user.processor3.id)
    user = User.objects.get(email = obj_p3_user.contact_email)
    obj_p3_user.delete()
    check_p3.delete()
    user.delete()
    return HttpResponse(1)
      
      
@login_required()   #processor3 add processor3 user
def add_processor3_user(request,pk):
    context={}
    if request.user.is_superuser or 'SubAdmin' or request.user.get_role() or 'SuperUser' in request.user.get_role():
        processor3_user =  ProcessorUser3.objects.get(id = pk)
        processor3_id = processor3_user.processor3.id
        processor3 = Processor3.objects.get(id = processor3_id) 
        context['processor'] = processor3
        processor_user = ProcessorUser3.objects.filter(processor3_id = processor3.id)
        context['processor_user'] = processor_user
        if request.method == 'POST':
            counter = request.POST.get('counter')
            for i in range(1,int(counter)+ 1):
                contact_email = request.POST.get('contact_email{}'.format(i))
                contact_name = request.POST.get('contact_name{}'.format(i))
                contact_phone = request.POST.get('contact_phone{}'.format(i))
                contact_fax = request.POST.get('contact_fax{}'.format(i))
                if User.objects.filter(email = contact_email).exists():
                    messages.error(request,'email already exists')
                else:
                    p_password_raw = generate_random_password()
                    p_user = ProcessorUser3(processor3_id = processor3_id,contact_email = contact_email,contact_name = contact_name ,contact_phone = contact_phone ,contact_fax = contact_fax,p_password_raw = p_password_raw)   
                    p_user.save()
                    user = User(email = contact_email,username = contact_email ,first_name = contact_name )
                    user.set_password(p_password_raw)
                    user.password_raw = p_password_raw
                    user.save()
                    user.role.add(Role.objects.get(role = 'Processor3'))
            return redirect('list_processor3')       
        return render(request , 'processor3/add_processor3_user.html' ,context) 
    else:
        return redirect('login')
    
    
# @login_required()  # show processor3 list
# def check_riju(request):    
#     # context={}
#     if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
#         # processor3 = ProcessorUser3.objects.all()
#         # context['processor'] = processor3
#         return render(request,'processor3/test.html')
#     else:
#         return redirect('login')   
    
@login_required()
def inbound_shipment_list(request):
    try:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context["table_data"] = list(ShipmentManagement.objects.filter(receiver_processor_type="T3").values())
            context["processor3"] = Processor2.objects.filter(processor_type__type_name="T3")
            search_name = request.GET.get("search_name")
            print(type(search_name), "ewrewwwwwwwwwwwwwwwwwwwwwwww")
            if search_name == str(None) or not search_name:
                print("sdgffdgfghf")
                context["search_name"] = None
            else:
                context["search_name"] = search_name

            if request.GET.get("select_processor"):
                context["select_processor"] = int(request.GET.get("select_processor"))
            else:
                context["select_processor"] = None
            if context["select_processor"] == '0' or not context["select_processor"]:
                print("hit1", search_name, context["select_processor"])
                if search_name and search_name != "None":
                    context["table_data"] = list(ShipmentManagement.objects.filter(receiver_processor_type="T3").filter(Q(shipment_id__icontains = search_name)|Q(processor_e_name__icontains = search_name)).values())
                print(context)
                return render (request, 'processor3/inbound_management_table.html', context)
            else:
                if search_name and search_name != "None":
                    context["table_data"] = list(ShipmentManagement.objects.filter(receiver_processor_type="T3", processor2_idd=context["select_processor"]).filter(Q(shipment_id__icontains = search_name)|Q(processor_e_name__icontains = search_name)).values())
                else: 
                    context["table_data"] = list(ShipmentManagement.objects.filter(receiver_processor_type="T3", processor2_idd=context["select_processor"]).values())
            print(context)
            return render (request, 'processor3/inbound_management_table.html', context)
        elif request.user.is_processor2 :
            processor_email = request.user.email
            p = ProcessorUser2.objects.get(contact_email=processor_email)
            processor_id = Processor2.objects.get(id=p.processor2.id).id
            #inbound management list for processor
            context["table_data"] = list(ShipmentManagement.objects.filter(receiver_processor_type="T3", processor2_idd=processor_id).values())
            return render (request, 'processor3/inbound_management_table.html', context)
        else:
            return redirect('login')  
    except:
        return render (request, 'processor3/inbound_management_table.html') 

@login_required()
def inbound_shipment_view(request, pk):
    try:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role() or request.user.is_processor2:
            #inbound management list for admin
            context["shipment"] = list(ShipmentManagement.objects.filter(id=pk).values())
            files = ShipmentManagement.objects.filter(id=pk).first().files.all().values('file')
            files_data = []
            for j in files:
                file_name = {}
                file_name["file"] = j["file"]
                # print(j["file"])
                if j["file"] or j["file"] != "" or j["file"] != ' ':
                    file_name["name"] = j["file"].split("/")[-1]
                else:
                    file_name["name"] = None
                files_data.append(file_name)
            context["files"] = files_data
            return render (request, 'processor3/inbound_management_view.html', context)
        else:
            return redirect('login')  
    except:
        return render (request, 'processor3/inbound_management_view.html', context) 
    
@login_required()
def inbound_shipment_edit(request, pk):
    # try:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role() or request.user.is_processor2:
            #inbound management list for admin
            context["shipment"] = ShipmentManagement.objects.get(id=pk)
            files = ShipmentManagement.objects.filter(id=pk).first().files.all().values('file','id')
            files_data = []
            for j in files:
                file_name = {}
                file_name["file"] = j["file"]
                file_name["id"] = j["id"]
                # print(j["file"])
                if j["file"] or j["file"] != "" or j["file"] != ' ':
                    file_name["name"] = j["file"].split("/")[-1]
                else:
                    file_name["name"] = None
                files_data.append(file_name)
            context["files"] = files_data
            # print("context", context)
            if request.method == "POST":
                data = request.POST
                # print('post method called')
                button_value = request.POST.getlist('remove_files')
                # print(button_value)
                if button_value:
                    for file_id in button_value:
                        try:
                            file_obj = File.objects.get(id=file_id)
                            file_obj.delete()
                        except File.DoesNotExist:
                            pass
                status = data.get('status')
                approval_date = data.get('approval_date')
                received_weight = data.get('received_weight')
                ticket_number = data.get('ticket_number')
                storage_bin_recive = data.get('storage_bin_recive')
                reason_for_disapproval = data.get('reason_for_disapproval')
                moisture_percent = data.get('moist_percentage')
                ShipmentManagement.objects.filter(id=pk).update(status=status,moisture_percent=moisture_percent, recive_delivery_date=approval_date,
                                                                received_weight=received_weight,ticket_number=ticket_number,
                                                                storage_bin_recive=storage_bin_recive, reason_for_disapproval=reason_for_disapproval)
                files = request.FILES.getlist('new_files')
                shipment = ShipmentManagement.objects.get(id=pk)
                for file in files:
                    new_file = File.objects.create(file=file)
                    shipment.files.add(new_file)
                shipment.save()
                return redirect('inbound_shipment_list3')
            return render(request, 'processor3/inbound_management_edit.html', context)
        else:
            return redirect('login')  
    # except:
    #     return render(request, 'processor3/inbound_management_edit.html', context)


@login_required()
def inbound_shipment_delete_processor3(request,pk):
    print("hit------------------------------", pk)
    shipment = ShipmentManagement.objects.filter(id=pk).first()

    #print(shipment)
    shipment.delete()
    return redirect('inbound_shipment_list3')


@login_required()
def rejected_shipments_csv_download_for_t3(request) :  
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        today_date = date.today()
        filename = f'Rejected Shipments CSV {today_date}.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['Shipment ID','Lot Number #','Shipment Date', 'Send Processor','Recive Processor','Total Weight (LBS)','Disapproval Date','Reason For Disapproval','Moisture Level'])
        output = ShipmentManagement.objects.filter(status='DISAPPROVED', receiver_processor_type="T3").order_by('-id').values('shipment_id','lot_number','date_pulled','processor_e_name','processor2_name',
                                                                                            'weight_of_product','recive_delivery_date','reason_for_disapproval','moisture_percent')
        for i in output:
            writer.writerow([
                i['shipment_id'], 
                i['lot_number'], 
                i['date_pulled'].strftime("%m-%d-%Y"),
                i['processor_e_name'], 
                i['processor2_name'], 
                i['weight_of_product'],
                i['recive_delivery_date'], 
                i['reason_for_disapproval'], 
                i['moisture_percent']])
        return response
    else:
        return redirect ('dashboard')

@login_required()
def all_shipments_csv_download_for_t3(request):  
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        today_date = date.today()
        filename = f'All Shipments CSV {today_date}.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['Shipment ID','Lot Number #','Shipment Date', 'Send Processor','Recive Processor','Total Weight (LBS)','Disapproval Date','Reason For Disapproval','Moisture Level'])
        output = ShipmentManagement.objects.filter(receiver_processor_type="T3").order_by('-id').values('shipment_id','lot_number','date_pulled','processor_e_name','processor2_name',
                                                                                            'weight_of_product','recive_delivery_date','reason_for_disapproval','moisture_percent')
        for i in output:
            writer.writerow([
                i['shipment_id'], 
                i['lot_number'], 
                i['date_pulled'].strftime("%m-%d-%Y"),
                i['processor_e_name'], 
                i['processor2_name'], 
                i['weight_of_product'],
                i['recive_delivery_date'], 
                i['reason_for_disapproval'], 
                i['moisture_percent']])
        return response
    else:
        return redirect ('dashboard')


@login_required()
def receive_shipment(request):
    context = {}

    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        context["processor"] = list(Processor2.objects.filter(processor_type__type_name="T2").values("id", "entity_name"))
        
        context.update({
            "select_processor_name": None,
            "select_processor_id": None,
            "milled_value": "None",
        })

        if request.method == "POST":
            data = request.POST
            bin_pull = data.get("bin_pull")
            milled_value = data.get("milled_value")
            context.update({
                "select_processor_name": Processor2.objects.filter(id=int(bin_pull)).first().entity_name,
                "select_processor_id": bin_pull,
                "processor2_id": data.get("processor2_id"),
                "exp_yield": data.get("exp_yield"),
                "exp_yield_unit_id": data.get("exp_yield_unit_id"),
                "moist_percentage": data.get("moist_percentage"),
                "purchase_number": data.get("purchase_number"),
                "weight_prod_unit_id": data.get("weight_prod_unit_id"),
                "weight_prod": data.get("weight_prod"),
                "storage_bin_id": data.get("storage_bin_id"),
                "equipment_id": data.get("equipment_id"),
                "equipment_type": data.get("equipment_type"),
                "lot_number": data.get("lot_number"),
                "volume_shipped": data.get("volume_shipped"),
                # "files": data.get("files"),
                "status": data.get("status"),
                "receiver_sku_id": data.get("receiver_sku_id"),
                "received_weight": data.get("received_weight"),
                "ticket_number": data.get("ticket_number"),
                "approval_date": data.get("approval_date"),
                "milled_value":data.get('milled_value')
            })

            if bin_pull and not data.get("save"):
                list_get_bin_location = []
                get_bin_location = list(ProductionManagementProcessor2.objects.filter(processor_id=int(bin_pull)).values_list('milled_volume', flat=True))

                if get_bin_location:
                    for i in get_bin_location:
                        list_get_bin_location.append(float(i))

                total_shiped_volume = []
                shiped_volume = list(ShipmentManagement.objects.filter(bin_location=bin_pull).values_list('volume_shipped', flat=True))
                if shiped_volume:
                    for i in shiped_volume :
                        total_shiped_volume.append(float(i))

                sum_total_volume = sum(list_get_bin_location) if get_bin_location else 0
                sum_shiped_volume = sum(total_shiped_volume) if shiped_volume else 0
                
                context["milled_value"] =  float(sum_total_volume) - float(sum_shiped_volume)               
                
                processor3 = LinkProcessorToProcessor.objects.filter(processor_id=bin_pull, linked_processor__processor_type__type_name = "T3").values("linked_processor__id", "linked_processor__entity_name")
                processor4 = LinkProcessorToProcessor.objects.filter(processor_id=bin_pull, linked_processor__processor_type__type_name = "T4").values("linked_processor__id", "linked_processor__entity_name")
                context["processor3"] = processor3
                context["processor4"] = processor4
            
                return render(request, 'processor3/receive_delivery.html', context)
            else:
                print("okay piu")
                if context["weight_prod_unit_id"] == "LBS" :
                    cal_weight = round(float(context["weight_prod"]),2)
                if context["weight_prod_unit_id"] == "BU" :
                    cal_weight = round(float(context["weight_prod"]) * 45,2)
                if context["exp_yield_unit_id"] == "LBS" :
                    cal_exp_yield = round(float(context["exp_yield"]),2)
                if context["exp_yield_unit_id"] == "BU" :
                    cal_exp_yield = round(float(context["exp_yield"]) * 45,2)


                ### processor link part

                select_proc_id, processor_type = context["processor2_id"].split()
                
                if processor_type == 'T3':
                    select_destination_ = Processor2.objects.get(id=select_proc_id).entity_name
                    receiver_processor_type = "T3"
                    # print("select_destination_-----",select_destination_)
                elif processor_type == 'T4':
                    select_destination_ = Processor2.objects.get(id=select_proc_id).entity_name
                    receiver_processor_type = "T4"
               
                milled_volume = context["milled_value"]
                volume_left = float(context["milled_value"]) - float(context["volume_shipped"])
                shipment_id = generate_shipment_id()
                
                processor_e_name = Processor2.objects.filter(id=int(bin_pull)).first().entity_name
                save_shipment_management = ShipmentManagement(shipment_id=shipment_id,processor_idd=bin_pull,processor_e_name=processor_e_name, sender_processor_type="T2", bin_location=bin_pull,
                        equipment_type=context["equipment_type"],equipment_id=context["equipment_id"],storage_bin_send=context["storage_bin_id"],moisture_percent = context["moist_percentage"],weight_of_product_raw = context["weight_prod"],
                        weight_of_product=cal_weight,weight_of_product_unit=context["weight_prod_unit_id"], excepted_yield_raw =context["exp_yield"],excepted_yield=cal_exp_yield,excepted_yield_unit=context["exp_yield_unit_id"],recive_delivery_date=context["approval_date"],
                        purchase_order_number=context["purchase_number"],lot_number=context["lot_number"],volume_shipped=context["volume_shipped"],milled_volume=milled_volume,volume_left=volume_left,editable_obj=True,status=context["status"],
                        storage_bin_recive=context["receiver_sku_id"],ticket_number=context["ticket_number"],received_weight=context["received_weight"],processor2_idd=select_proc_id,processor2_name=select_destination_, receiver_processor_type=receiver_processor_type)
                save_shipment_management.save()
                files = request.FILES.getlist('files')
                for file in files:
                    new_file = File.objects.create(file=file)
                    save_shipment_management.files.add(new_file)
                save_shipment_management.save()
                
                return redirect('inbound_shipment_list3')
        return render(request, 'processor3/receive_delivery.html', context)
    else:
        return redirect('login')

@login_required
def add_outbound_shipment_processor3(request):
    context = {}

    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        # processor= Processor2.objects.filter(processor_type__type_name="T2").values("entity_name","id").order_by('entity_name')
        # processor3= Processor2.objects.filter(processor_type__type_name="T3").values("entity_name","id").order_by('entity_name')
        # processor4= Processor2.objects.filter(processor_type__type_name="T4").values("entity_name","id").order_by('entity_name')
        # context["processor3"] = processor3
        # context["processor4"] = processor4
        context["processor"] = list(Processor2.objects.filter(processor_type__type_name="T3").values("id", "entity_name"))
        
        context.update({
            "select_processor_name": None,
            "select_processor_id": None,
            "milled_value": "None",
        })

        if request.method == "POST":
            data = request.POST
            bin_pull = data.get("bin_pull")
            milled_value = data.get("milled_value")
            context.update({
                "select_processor_name": Processor2.objects.filter(id=int(bin_pull)).first().entity_name,
                "select_processor_id": bin_pull,
                "processor2_id": data.get("processor2_id"),
                "exp_yield": data.get("exp_yield"),
                "exp_yield_unit_id": data.get("exp_yield_unit_id"),
                "moist_percentage": data.get("moist_percentage"),
                "purchase_number": data.get("purchase_number"),
                "weight_prod_unit_id": data.get("weight_prod_unit_id"),
                "weight_prod": data.get("weight_prod"),
                "storage_bin_id": data.get("storage_bin_id"),
                "equipment_id": data.get("equipment_id"),
                "equipment_type": data.get("equipment_type"),
                "lot_number": data.get("lot_number"),
                "volume_shipped": data.get("volume_shipped"),
                # "files": data.get("files"),
                "milled_value":data.get('milled_value')
            })

            if bin_pull and not data.get("save"):
                list_get_bin_location = []
                get_bin_location = list(ProductionManagementProcessor2.objects.filter(processor_id=int(bin_pull)).values_list('milled_volume', flat=True))

                if get_bin_location:
                    for i in get_bin_location:
                        list_get_bin_location.append(float(i))

                total_shiped_volume = []
                shiped_volume = ShipmentManagement.objects.filter(bin_location=bin_pull).values('volume_shipped')
                if shiped_volume:
                    for i in shiped_volume :
                        total_shiped_volume.append(float(i['volume_shipped']))

                sum_total_volume = sum(list_get_bin_location) if get_bin_location else 0
                sum_shiped_volume = sum(total_shiped_volume) if shiped_volume else 0
                context["milled_value"] =  float(sum_total_volume) - float(sum_shiped_volume)
                
                processor3 = LinkProcessorToProcessor.objects.filter(processor_id=bin_pull, linked_processor__processor_type__type_name = "T3").values("linked_processor__id", "linked_processor__entity_name")
                processor4 = LinkProcessorToProcessor.objects.filter(processor_id=bin_pull, linked_processor__processor_type__type_name = "T4").values("linked_processor__id", "linked_processor__entity_name")
                context["processor3"] = processor3
                context["processor4"] = processor4
               
                return render(request, 'processor3/add_outbound_shipment_processor3.html', context)
            else:
                if context["weight_prod_unit_id"] == "LBS" :
                    cal_weight = round(float(context["weight_prod"]),2)
                if context["weight_prod_unit_id"] == "BU" :
                    cal_weight = round(float(context["weight_prod"]) * 45,2)
                if context["exp_yield_unit_id"] == "LBS" :
                    cal_exp_yield = round(float(context["exp_yield"]),2)
                if context["exp_yield_unit_id"] == "BU" :
                    cal_exp_yield = round(float(context["exp_yield"]) * 45,2)


                ### processor link part

                select_proc_id, processor_type = context["processor2_id"].split()
                
                if processor_type == 'T4':
                    select_destination_ = Processor2.objects.get(id=select_proc_id).entity_name
                    receiver_processor_type = "T4"
                
                milled_volume = context["milled_value"]
                volume_left = float(context["milled_value"]) - float(context["volume_shipped"])
                shipment_id = generate_shipment_id()
                
                processor_e_name = Processor2.objects.filter(id=int(bin_pull)).first().entity_name
                save_shipment_management = ShipmentManagement(shipment_id=shipment_id,processor_idd=bin_pull,processor_e_name=processor_e_name, sender_processor_type="T3", bin_location=bin_pull,
                        equipment_type=context["equipment_type"],equipment_id=context["equipment_id"],storage_bin_send=context["storage_bin_id"],moisture_percent = context["moist_percentage"],weight_of_product_raw = context["weight_prod"],
                        weight_of_product=cal_weight,weight_of_product_unit=context["weight_prod_unit_id"], excepted_yield_raw =context["exp_yield"],excepted_yield=cal_exp_yield,excepted_yield_unit=context["exp_yield_unit_id"],
                        purchase_order_number=context["purchase_number"],lot_number=context["lot_number"],volume_shipped=context["volume_shipped"],milled_volume=milled_volume,volume_left=volume_left,editable_obj=True,
                        processor2_idd=select_proc_id,processor2_name=select_destination_, receiver_processor_type=receiver_processor_type)
                save_shipment_management.save()
                files = request.FILES.getlist('files')
                for file in files:
                    new_file = File.objects.create(file=file)
                    save_shipment_management.files.add(new_file)
                save_shipment_management.save()
                return redirect('outbound_shipment_list_processor3')

        return render(request, 'processor3/add_outbound_shipment_processor3.html', context)

@login_required()
def outbound_shipment_list_processor3(request):  
    try:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            #inbound management list for admin
            output = ShipmentManagement.objects.filter(sender_processor_type="T3")
            p_id = [i.processor_idd for i in output]
            processors = Processor2.objects.filter(id__in = p_id).order_by('entity_name')
            context['processors'] = processors

            search_name = request.GET.get('search_name')
            selectprocessor_id = request.GET.get('selectprocessor_id')

            if search_name == None and selectprocessor_id == None :
                output = output
            else:
                output = ShipmentManagement.objects.filter(sender_processor_type="T3").order_by('bin_location','id')
                if search_name and search_name != 'All':
                    output = output.filter(Q(processor_e_name__icontains=search_name) | Q(date_pulled__icontains=search_name) |
                    Q(bin_location__icontains=search_name) | Q(equipment_type__icontains=search_name) | Q(equipment_id__icontains=search_name) | 
                    Q(purchase_order_number__icontains=search_name) | Q(lot_number__icontains=search_name))
                    context['search_name'] = search_name
                if selectprocessor_id and selectprocessor_id != 'All':
                    output = output.filter(processor_idd=selectprocessor_id)
                    selectedProcessors = Processor2.objects.get(id=selectprocessor_id)
                    context['selectedProcessors'] = selectedProcessors
            paginator = Paginator(output, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)
            context["table_data"] = report
            return render (request, 'processor3/outbound_shipment_list.html', context)
        elif request.user.is_processor2 :
            processor_email = request.user.email
            p = ProcessorUser2.objects.get(contact_email=processor_email)
            processor_id = Processor2.objects.get(id=p.processor2.id).id
            #inbound management list for processor
            output = ShipmentManagement.objects.filter(sender_processor_type="T3", processor_idd=processor_id)
            p_id = [i.processor_idd for i in output]
            processors = Processor2.objects.filter(id__in = p_id).order_by('entity_name')
            context['processors'] = processors

            search_name = request.GET.get('search_name')
            selectprocessor_id = request.GET.get('selectprocessor_id')

            if search_name == None and selectprocessor_id == None :
                output = output
            else:
                output = ShipmentManagement.objects.filter(sender_processor_type="T3", processor_idd=processor_id).order_by('bin_location','id')
                if search_name and search_name != 'All':
                    output = output.filter(Q(processor_e_name__icontains=search_name) | Q(date_pulled__icontains=search_name) |
                    Q(bin_location__icontains=search_name) | Q(equipment_type__icontains=search_name) | Q(equipment_id__icontains=search_name) | 
                    Q(purchase_order_number__icontains=search_name) | Q(lot_number__icontains=search_name))
                    context['search_name'] = search_name
                if selectprocessor_id and selectprocessor_id != 'All':
                    output = output.filter(processor_idd=selectprocessor_id)
                    selectedProcessors = Processor2.objects.get(id=selectprocessor_id)
                    context['selectedProcessors'] = selectedProcessors
            paginator = Paginator(output, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)
            context["table_data"] = report            
            return render (request, 'processor3/outbound_shipment_list.html', context)
        else:
            return redirect('login')  
    except:
        return render (request, 'processor3/outbound_shipment_list.html') 


@login_required()
def outbound_shipment_view_processor3(request,pk):   
    try:
        context ={}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            # processor_id = Processor.objects.get(id=pk)
            # print("processor_id==============",processor_id)
            output = ShipmentManagement.objects.filter(id=pk).order_by('bin_location')
            files = ShipmentManagement.objects.filter(id=pk).first().files.all().values('file')
            files_data = []
            for j in files:
                file_name = {}
                file_name["file"] = j["file"]
                # #print(j["file"])
                if j["file"] or j["file"] != "" or j["file"] != ' ':
                    file_name["name"] = j["file"].split("/")[-1]
                else:
                    file_name["name"] = None
                files_data.append(file_name)
            context["files"] = files_data
            context["report"] = output
           
            return render (request, 'processor3/outbound_shipment_view.html', context) 
        else:
            return redirect('login')  
    except:
        return render (request, 'processor3/outbound_shipment_view.html')


@login_required()
def outbound_shipment_delete_processor3(request,pk):  
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        get_obj = ShipmentManagement.objects.get(id=pk)
        mill_bin_location = get_obj.bin_location       
        get_obj.delete()
        update_obj = ShipmentManagement.objects.filter(bin_location=mill_bin_location).order_by('id').values('id')
        if update_obj.exists() :
            last_obj_id = [i['id'] for i in update_obj][-1]
            now_update_one = ShipmentManagement.objects.get(id=last_obj_id)
            now_update_one.editable_obj = True
            now_update_one.save()

            now_update_all = ShipmentManagement.objects.filter(bin_location=mill_bin_location).exclude(id=last_obj_id)
            for i in now_update_all :
                make_uneditale = ShipmentManagement.objects.get(id=i.id)
                make_uneditale.editable_obj = False
                make_uneditale.save()
        else:
            pass
        return redirect('outbound_shipment_list_processor3')



@login_required()
def processor3_processor_management(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context ={}
            processor3 = Processor2.objects.filter(processor_type__type_name="T3")  #24/04/2024
            context['Processor1'] = processor3
            link_processor_to_processor_all = LinkProcessorToProcessor.objects.filter(processor__processor_type__type_name="T3")
            context['link_processor_to_processor_all'] = link_processor_to_processor_all
            
            if request.method == 'POST':
                pro1_id = request.POST.get('pro1_id')
                if pro1_id != '0':
                    context['link_processor_to_processor_all'] = link_processor_to_processor_all.filter(processor1_id=int(pro1_id))
                    #then need to add T1/T2/T3
                    context['selectedpro1'] = int(pro1_id)             
            print(context)             
            return render(request, 'processor3/processor3_processor_management.html',context)
    else:
        return redirect('login')


@login_required
def link_processor_three(request):
    context = {}
    try:
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            processor2 = Processor2.objects.filter(processor_type__type_name="T3")           
            context["processor2"] = processor2
           
            context["processor4"] = []

            if request.method == "POST" :
                selected_processor = request.POST.get("processor_id")
                button_click = request.POST.get("save")
                if selected_processor and  not button_click:
                    context["selectedprocessor"] = int(selected_processor)
                    link_processor2 = list(LinkProcessorToProcessor.objects.filter(processor_id=selected_processor).values_list("linked_processor", flat = True))
                    processor_two = Processor2.objects.exclude(id__in=link_processor2)
                    
                    processor4 = processor_two.filter(processor_type__type_name="T4")
                   
                    context["processor4"] = processor4
                    return render(request, 'processor3/link_processor3.html', context)
                else:
                    select_processor2 = request.POST.getlist("select_processor2")
                    print(selected_processor, select_processor2)
                    for i in select_processor2:
                        pro_id , pro_type = i.split(" ")
                        link_pro = LinkProcessorToProcessor(processor_id = selected_processor, linked_processor_id = pro_id)
                        link_pro.save()
                    return redirect('processor3_processor_management')
                    # return render(request, 'processor2/link_processor.html', context)

            return render(request, 'processor3/link_processor3.html', context)
        else:
            return render(request, 'processor3/link_processor3.html', context) 
    except Exception as e:
        print(e)
        return render(request, 'processor3/link_processor3.html', context)


@login_required()
def delete_link_processor_three(request, pk):
    try:
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            link = LinkProcessorToProcessor.objects.filter(id=pk).first()
            link.delete()
        else:
            return redirect('login')
    except Exception as e:
        print(e)
        return HttpResponse(e)


@login_required()
def inbound_production_management_processor3(request): 
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        output = ProductionManagementProcessor2.objects.filter(processor__processor_type__type_name="T3").order_by('processor_e_name','-id')

        p_id = [i.processor.id for i in output]
        processors = Processor2.objects.filter(id__in = p_id).order_by('entity_name')
        context['processors'] = processors
        print(context)
        
        search_name = request.GET.get('search_name')
        selectprocessor_id = request.GET.get('selectprocessor_id')

        if search_name == None and selectprocessor_id == None :
            output = output
        else:
            output = ProductionManagementProcessor2.objects.filter(processor__processor_type__type_name="T3").order_by('processor_e_name','-id')
            if search_name and search_name != 'All':
                output = ProductionManagementProcessor2.objects.filter(Q(processor_e_name__icontains=search_name) | Q(date_pulled__icontains=search_name) |
                Q(bin_location__icontains=search_name) | Q(milled_storage_bin__icontains=search_name) )
                context['search_name'] = search_name
            if selectprocessor_id and selectprocessor_id != 'All':
                output = output.filter(processor_id=selectprocessor_id)
                selectedProcessors = Processor2.objects.get(id=selectprocessor_id)
                context['selectedProcessors'] = selectedProcessors
        paginator = Paginator(output, 100)
        page = request.GET.get('page')
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)

        context['report'] = report
        return render (request, 'processor3/inbound_production_management.html', context)
    
    else:
        return redirect ('login')


@login_required()
def add_volume_pulled_processor3(request):   
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        get_processor = Processor2.objects.filter(processor_type__type_name="T3").order_by('entity_name')
        context['get_processor'] = get_processor
        if request.method == 'POST' :
            id_processor = request.POST.get('id_processor')
            if id_processor and id_processor != "all" :
                total_receive_weight = []
                total_volume_pulled_till_now = []
                shipment = ShipmentManagement.objects.filter(processor2_idd = id_processor).filter(status ="APPROVED").values('volume_shipped')
            
                if shipment.exists() :
                    for i in shipment :
                        try:
                            total_receive_weight.append(float(i['volume_shipped']))
                        except:
                            total_receive_weight.append(float(0))
                    total_receive_weight = sum(total_receive_weight)

                    volume_pulled_till_now = ProductionManagementProcessor2.objects.filter(processor_id = id_processor).values('volume_pulled')
                    for i in volume_pulled_till_now :
                        total_volume_pulled_till_now.append(float(i['volume_pulled']))
                    
                    sum_volume_pulled_till_now = sum(total_volume_pulled_till_now)
                    final_total_volume = total_receive_weight - sum_volume_pulled_till_now
                else:
                    final_total_volume = 0
                    total_volume_pulled_till_now = 0
                    total_receive_weight = 0

                
                pp = Processor2.objects.get(id=id_processor)
                context['selectedProcessor'] = pp
                context['total_receive_weight'] = f'{final_total_volume} LBS'
                context['total_receive_weight_java'] = final_total_volume

                id_date = request.POST.get('id_date')
                bin_location = request.POST.get('bin_location')
                volume_pulled = request.POST.get('volume_pulled')
                milled_volume = request.POST.get('milled_volume')
                milled_storage_bin = request.POST.get('milled_storage_bin')
                
                if volume_pulled and id_date and milled_volume :
                    volume_left = final_total_volume - float(volume_pulled)
                    save_production_management=ProductionManagementProcessor2(processor_id=id_processor,processor_e_name=pp.entity_name,
                    total_volume=final_total_volume,date_pulled=id_date,bin_location=bin_location,volume_pulled=volume_pulled,
                    milled_volume=milled_volume,volume_left=volume_left,milled_storage_bin=milled_storage_bin,editable_obj=True)
                    save_production_management.save()
                    
                    update_obj = ProductionManagementProcessor2.objects.filter(processor_id=id_processor).exclude(id=save_production_management.id).values('id','editable_obj')
                    
                    if update_obj.exists():
                        for i in update_obj :
                            get_obj = ProductionManagementProcessor2.objects.get(id=i['id'])
                            get_obj.editable_obj = False
                            get_obj.save()
                    else:
                        pass
                    return redirect ('inbound_production_management_processor3')
            else:
                pass
        return render (request, 'processor3/add_volume_pulled.html', context)
    
    else:
        return redirect ('login')


@login_required()
def edit_volume_pulled_processor3(request,pk):   
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        get_obj = ProductionManagementProcessor2.objects.get(id=pk)
        if get_obj.editable_obj == True :
            context['name_processor'] = get_obj.processor_e_name
            context['total_receive_weight'] = get_obj.total_volume
            context['total_receive_weight_java'] = get_obj.total_volume
            context['id_date'] = str(get_obj.date_pulled)
            context['bin_location'] = get_obj.bin_location
            context['volume_pulled'] = get_obj.volume_pulled
            context['milled_volume'] = get_obj.milled_volume
            context['milled_storage_bin'] = get_obj.milled_storage_bin
            if request.method == 'POST' :
                id_date = request.POST.get('id_date')
                bin_location = request.POST.get('bin_location')
                volume_pulled = request.POST.get('volume_pulled')
                milled_volume = request.POST.get('milled_volume')
                milled_storage_bin = request.POST.get('milled_storage_bin')
                
                if volume_pulled and id_date and milled_volume :
                    final_total_volume = float(get_obj.total_volume)
                    volume_left = final_total_volume - float(volume_pulled)
                    get_obj.date_pulled = id_date
                    get_obj.bin_location = bin_location
                    get_obj.volume_pulled = volume_pulled
                    get_obj.milled_volume = milled_volume
                    get_obj.volume_left = volume_left
                    get_obj.milled_storage_bin = milled_storage_bin
                    get_obj.save()
                    return redirect ('inbound_production_management_processor3')
        else:
            messages.error(request,'This is not a valid request')
    
        return render (request, 'processor3/edit_volume_pulled.html', context)
    else:
        return redirect ('login')


@login_required()
def delete_volume_pulled_processor3(request,pk):  
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        get_obj = ProductionManagementProcessor2.objects.get(id=pk)
        volume_pulled = get_obj.volume_pulled
        bin_location = get_obj.bin_location
        processor_id = get_obj.processor_id
        
        get_obj.delete()
        update_obj = ProductionManagementProcessor2.objects.filter(processor_id=processor_id).order_by('id').values('id')

        if update_obj.exists() :
            last_obj_id = [i['id'] for i in update_obj][-1]
            now_update_one = ProductionManagementProcessor2.objects.get(id=last_obj_id)
            now_update_one.editable_obj = True
            now_update_one.save()

            now_update_all = ProductionManagementProcessor2.objects.filter(processor_id=processor_id).exclude(id=last_obj_id)
            for i in now_update_all :
                make_uneditale = ProductionManagementProcessor2.objects.get(id=i.id)
                make_uneditale.editable_obj = False
                make_uneditale.save()
        else:
            pass
        
        return redirect ('inbound_production_management_rpocessor3')
    else:        
        return redirect ('login')


    