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
    # try:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context["table_data"] = list(ShipmentManagement.objects.filter(receiver_processor_type="T4").values())
            context["processor4"] = Processor2.objects.filter(processor_type__type_name="T4")
            search_name = request.GET.get("search_name")
            context["search_name"] = search_name
            if request.GET.get("select_processor"):
                context["select_processor"] = int(request.GET.get("select_processor"))
            else:
                context["select_processor"] = None
            if context["select_processor"] == '0' or not context["select_processor"]:
                if search_name:
                    context["table_data"] = list(ShipmentManagement.objects.filter(receiver_processor_type="T4").filter(Q(shipment_id__icontains = search_name)|Q(processor_e_name__icontains = search_name)).values())
                return render (request, 'processor4/inbound_management_table.html', context)
            else:
                if search_name:
                    # print("hit", search, search_name)
                    context["table_data"] = list(ShipmentManagement.objects.filter(receiver_processor_type="T4", processor2_idd=context["select_processor"]).filter(Q(shipment_id__icontains = search_name)|Q(processor_e_name__icontains = search_name)).values())
                else:   
                    context["table_data"] = list(ShipmentManagement.objects.filter(receiver_processor_type="T4", processor2_idd=context["select_processor"]).values())
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
    # except:
    #     return render (request, 'processor4/inbound_management_table.html') 


@login_required()
def rejected_shipments_csv_download_for_t4(request) :  
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        today_date = date.today()
        filename = f'Rejected Shipments CSV {today_date}.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['Shipment ID','Lot Number #','Shipment Date', 'Send Processor','Recive Processor','Total Weight (LBS)','Disapproval Date','Reason For Disapproval','Moisture Level'])
        output = ShipmentManagement.objects.filter(status='DISAPPROVED', receiver_processor_type="T4").order_by('-id').values('shipment_id','lot_number','date_pulled','processor_e_name','processor2_name',
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
def all_shipments_csv_download_for_t4(request):  
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        today_date = date.today()
        filename = f'All Shipments CSV {today_date}.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['Shipment ID','Lot Number #','Shipment Date', 'Send Processor','Recive Processor','Total Weight (LBS)','Disapproval Date','Reason For Disapproval','Moisture Level'])
        output = ShipmentManagement.objects.filter(receiver_processor_type="T4").order_by('-id').values('shipment_id','lot_number','date_pulled','processor_e_name','processor2_name',
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