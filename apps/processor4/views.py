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
@login_required()
def inbound_shipment_list(request):
    try:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            #inbound management list for admin
            context["table_data"] = list(ShipmentManagement.objects.filter(receiver_processor_type="T4").values())
            print(context)
            return render (request, 'processor4/inbound_management_table.html', context)
        elif request.user.is_processor2 :
            processor_email = request.user.email
            p = ProcessorUser2.objects.get(contact_email=processor_email)
            processor_id = Processor2.objects.get(id=p.processor2.id).id
            #inbound management list for processor
            context["table_data"] = list(ShipmentManagement.objects.filter(receiver_processor_type="T4", processor2_idd=processor_id).values())
            return render (request, 'processor4/inbound_management_table.html', context)
        else:
            return redirect('login')  
    except:
        return render (request, 'processor4/inbound_management_table.html') 

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
            return render (request, 'processor4/inbound_management_view.html', context)
        else:
            return redirect('login')  
    except:
        return render (request, 'processor4/inbound_management_view.html', context) 
    
@login_required()
def inbound_shipment_edit(request, pk):
    try:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role() or request.user.is_processor2:
            #inbound management list for admin
            context["shipment"] = ShipmentManagement.objects.get(id=pk)
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
            data = request.POST
            if request.method == "POST":
                button_value = request.POST.getlist('remove_files')
                print(button_value)
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
                return redirect('inbound_shipment_list_processor4')
            return render(request, 'processor4/inbound_management_edit.html', context)
        else:
            return redirect('login')  
    except:
        return render(request, 'processor4/inbound_management_edit.html', context)

@login_required()
def inbound_shipment_delete_processor4(request,pk):
    print("hit------------------------------", pk)
    shipment = ShipmentManagement.objects.filter(id=pk).first()

    #print(shipment)
    shipment.delete()
    return redirect('inbound_shipment_list4')

@login_required()
def receive_shipment(request):
    context = {}

    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
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
                
                
                processor4 = LinkProcessorToProcessor.objects.filter(processor_id=bin_pull, linked_processor__processor_type__type_name = "T4").values("linked_processor__id", "linked_processor__entity_name")
                
                context["processor4"] = processor4
            
                return render(request, 'processor4/receive_delivery.html', context)
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
                
                if processor_type == 'T4':
                    select_destination_ = Processor2.objects.get(id=select_proc_id).entity_name
                    receiver_processor_type = "T4"
               
                milled_volume = context["milled_value"]
                volume_left = float(context["milled_value"]) - float(context["volume_shipped"])
                shipment_id = generate_shipment_id()
                
                processor_e_name = Processor2.objects.filter(id=int(bin_pull)).first().entity_name
                save_shipment_management = ShipmentManagement(shipment_id=shipment_id,processor_idd=bin_pull,processor_e_name=processor_e_name, sender_processor_type="T1", bin_location=bin_pull,
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
                
                return redirect('inbound_shipment_list_processor4')
        return render(request, 'processor4/receive_delivery.html', context)
    else:
        return redirect('login')
    

@login_required()
def inbound_production_management_processor4(request): 
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        output = ProductionManagementProcessor2.objects.filter(processor__processor_type__type_name="T4").order_by('processor_e_name','-id')

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
        return render (request, 'processor4/inbound_production_management.html', context)
    
    else:
        return redirect ('login')


@login_required()
def add_volume_pulled_processor4(request):   
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        get_processor = Processor2.objects.filter(processor_type__type_name="T4").order_by('entity_name')
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
                    return redirect ('inbound_production_management_processor4')
            else:
                pass
        return render (request, 'processor4/add_volume_pulled.html', context)
    
    else:
        return redirect ('login')


@login_required()
def edit_volume_pulled_processor4(request,pk):   
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
                    return redirect ('inbound_production_management_processor4')
        else:
            messages.error(request,'This is not a valid request')
    
        return render (request, 'processor4/edit_volume_pulled.html', context)
    else:
        return redirect ('login')


@login_required()
def delete_volume_pulled_processor4(request,pk):  
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
        
        return redirect ('inbound_production_management_rpocessor4')
    else:        
        return redirect ('login')

@login_required()  # show processor3 list
def processor4_list(request):
    context={}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        processor3 = ProcessorUser2.objects.filter(processor2__processor_type__type_name="T4")
        context['processor'] = processor3
        return render(request,'processor4/list_processor4.html',context)
    else:
        return redirect('login')   
    
    
        
  
    