"""Views related to farm model"""
from django.http.response import HttpResponse
import pandas as pd
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.utils import IntegrityError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from apps.processor.models import Processor, ProcessorUser, Location, LinkGrowerToProcessor, GrowerShipment, ClassingReport, ProductionReport, BaleReportProducer, GinReportbyday, GinLoadBalebydate, BaleReportFarmField, CertificateCalc, ProductionManagement, ShipmentManagement
from apps.processor.forms import ProcessorForm, LocationForm, GrowerShipmentForm
from apps.accounts.models import User, Role, ShowNotification, LogTable
from apps.grower.models import Grower, Consultant
from apps.farms.models import Farm
from apps.processor2.models import *
from apps.growerpayments.models import GrowerPayments
from apps.field.models import Field, ShapeFileDataCo
from apps.storage.models import ShapeFileDataCo as StorageShapeFileDataCo, Storage
from apps.growersurvey.models import SustainabilitySurvey,TypeSurvey,NameSurvey
import string
import random
import shapefile
from django.core.mail import send_mail
from django.template.loader import render_to_string
from qrcode import *
from django.conf import settings
import time
import json
import copy
from django.http import FileResponse
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.utils import (dateformat, formats)
from datetime import date, datetime
import csv
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.db.models import Sum

characters = list(string.ascii_letters + string.digits + "@#$%")
def generate_random_password():
	length = 8

	random.shuffle(characters)

	password = []
	for i in range(length):
		password.append(random.choice(characters))

	return "".join(password)

characters2 = list(string.ascii_letters + string.digits)
def generate_shipment_id():
	length = 12

	random.shuffle(characters2)

	shipment_id = []
	for i in range(length):
		shipment_id.append(random.choice(characters2))

	return "".join(shipment_id)

characters3 = list(string.digits)
def generate_sku_id():
	length = 12

	random.shuffle(characters3)

	sku_id = []
	for i in range(length):
		sku_id.append(random.choice(characters3))

	return "".join(sku_id)

def AddProcessorView(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():

            form = ProcessorForm()
            context = {'form':form}
            if request.method == 'POST':
                form = ProcessorForm(request.POST)

                fein = request.POST.get('fein')
                entity_name = request.POST.get('entity_name')
                billing_address = request.POST.get('billing_address')
                shipping_address = request.POST.get('shipping_address')
                main_number = request.POST.get('main_number')
                main_fax = request.POST.get('main_fax')
                website = request.POST.get('website')
                # gin_id = request.POST.get('gin_id')
                pp = Processor(fein=fein,entity_name=entity_name,billing_address=billing_address,shipping_address=shipping_address,main_number=main_number,main_fax=main_fax,website=website)
                pp.save()
                # 10-04-23 Log Table
                log_type, log_status, log_device = "Processor", "Added", "Web"
                log_idd, log_name = pp.id, entity_name
                log_email = None
                log_details = f"fein = {fein} | entity_name= {entity_name} | billing_address = {billing_address} | shipping_address = {shipping_address} | main_number = {main_number} | main_fax = {main_fax} | website = {website}"
                action_by_userid = request.user.id
                userr = User.objects.get(pk=action_by_userid)
                user_role = userr.role.all()
                action_by_username = f'{userr.first_name} {userr.last_name}'
                action_by_email = userr.username
                if request.user.id == 1 :
                    action_by_role = "superuser"
                else:
                    action_by_role = str(','.join([str(i.role) for i in user_role]))
                logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                    action_by_userid=action_by_userid,action_by_username=action_by_username,
                                    action_by_email=action_by_email,action_by_role=action_by_role,log_email=log_email,
                                    log_details=log_details,log_device=log_device)
                logtable.save()
                
                p = Processor.objects.get(fein=fein,entity_name=entity_name,billing_address=billing_address,shipping_address=shipping_address,main_number=main_number,main_fax=main_fax,website=website)
                counter = request.POST.get('counter')
                for i in range(1,int(counter)+1):
                    contact_name = request.POST.get('contact_name{}'.format(i))

                    contact_email = request.POST.get('contact_email{}'.format(i))
                    contact_phone = request.POST.get('contact_phone{}'.format(i))
                    contact_fax = request.POST.get('contact_fax{}'.format(i))

                    # print('contact_name',contact_name,'contact_email',contact_email,'contact_phone',contact_phone,'contact_fax',contact_fax)
 
                    if User.objects.filter(email=contact_email).exists():
                        messages.error(request,'email already exists')
                    else:
                        password = generate_random_password()
                        
                        puser = ProcessorUser(processor_id = p.id,contact_name=contact_name,contact_email=contact_email,contact_phone=contact_phone,contact_fax=contact_fax,p_password_raw=password)
                        puser.save()
                        user = User.objects.create(email=contact_email, username=contact_email,first_name=contact_name)
                        user.role.add(Role.objects.get(role='Processor'))
                        user.is_processor=True
                        user.is_active=True
                        user.set_password(password)
                        user.password_raw = password
                        user.save()

                        # 07-04-23 Log Table
                        log_type, log_status, log_device = "ProcessorUser", "Added", "Web"
                        log_idd, log_name = puser.id, contact_name
                        log_email = contact_email
                        log_details = f"processor_id = {p.id} | processor = {p.entity_name} | contact_name= {contact_name} | contact_email = {contact_email} | contact_phone = {contact_phone} | contact_fax = {contact_fax} | p_password_raw = {password}"
                        action_by_userid = request.user.id
                        userr = User.objects.get(pk=action_by_userid)
                        user_role = userr.role.all()
                        action_by_username = f'{userr.first_name} {userr.last_name}'
                        action_by_email = userr.username
                        if request.user.id == 1 :
                            action_by_role = "superuser"
                        else:
                            action_by_role = str(','.join([str(i.role) for i in user_role]))
                        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                                            action_by_email=action_by_email,action_by_role=action_by_role,log_email=log_email,
                                            log_details=log_details,log_device=log_device)
                        logtable.save()
                return redirect('list-processor')
                
            return render(request, 'processor/add_processor.html',context)
    else:
        return redirect('login')

def add_processor_user(request,pk):
    if request.user.is_authenticated:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            processor_user = ProcessorUser.objects.get(id=pk)
            processor_id = processor_user.processor.id
            processor = Processor.objects.get(id=processor_id)
            context['processor'] = processor
            processor_user = ProcessorUser.objects.filter(processor_id = processor.id)
            context['processor_user'] = processor_user
            if request.method == 'POST':
                counter = request.POST.get('counter')
                for i in range(1,int(counter)+1):
                    contact_name = request.POST.get('contact_name{}'.format(i))

                    contact_email = request.POST.get('contact_email{}'.format(i))
                    contact_phone = request.POST.get('contact_phone{}'.format(i))
                    contact_fax = request.POST.get('contact_fax{}'.format(i))

                    # print('contact_name',contact_name,'contact_email',contact_email,'contact_phone',contact_phone,'contact_fax',contact_fax)

                    if User.objects.filter(email=contact_email).exists():
                        messages.error(request,'email already exists')
                    else:
                        password = generate_random_password()
                        
                        puser = ProcessorUser(processor_id = processor_id,contact_name=contact_name,contact_email=contact_email,contact_phone=contact_phone,contact_fax=contact_fax,p_password_raw=password)
                        puser.save()
                        user = User.objects.create(email=contact_email, username=contact_email,first_name=contact_name)
                        user.role.add(Role.objects.get(role='Processor'))
                        user.is_processor=True
                        user.is_active=True
                        user.set_password(password)
                        user.password_raw = password
                        user.save()

                        # 07-04-23 Log Table
                        log_type, log_status, log_device = "ProcessorUser", "Added", "Web"
                        log_idd, log_name = puser.id, contact_name
                        log_email = contact_email
                        log_details = f"processor_id = {processor_id} | processor = {processor.entity_name}  | contact_name= {contact_name} | contact_email = {contact_email} | contact_phone = {contact_phone} | contact_fax = {contact_fax}"
                        
                        action_by_userid = request.user.id
                        userr = User.objects.get(pk=action_by_userid)
                        user_role = userr.role.all()
                        action_by_username = f'{userr.first_name} {userr.last_name}'
                        action_by_email = userr.username
                        if request.user.id == 1 :
                            action_by_role = "superuser"
                        else:
                            action_by_role = str(','.join([str(i.role) for i in user_role]))
                        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                                            action_by_email=action_by_email,action_by_role=action_by_role,log_email=log_email,
                                            log_details=log_details,log_device=log_device)
                        logtable.save()

                return redirect('list-processor')
            return render(request, 'processor/add_processor_user.html',context)
    else:
        return redirect('login')


def ListProcessorView(request):
    if request.user.is_authenticated:
        context = {}
        # Grower ................................
        if 'Grower' in request.user.get_role() and not request.user.is_superuser:
            pass
        # consultant ..........................
        elif request.user.is_consultant:
            pass
        # superadmin and others ................
        elif request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            processor= ProcessorUser.objects.all()
            context['processor'] = processor
            return render(request, 'processor/list_processor.html',context)
    else:
        return redirect('login')
    
def ProcessorUpdate(request,pk):
    if request.user.is_authenticated:
        context = {}
        # Grower ................................
        if 'Grower' in request.user.get_role() and not request.user.is_superuser:
            pass
        # consultant ..........................
        elif request.user.is_consultant:
            pass
        # superadmin and others ................
        elif request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            obj_id = ProcessorUser.objects.get(id=pk)
            context['p_user'] = obj_id
            processor = Processor.objects.get(id=obj_id.processor_id)

            context['form'] = ProcessorForm(instance=processor)
            processor_email = obj_id.contact_email
            user = User.objects.get(email=processor_email)
            if request.method == 'POST':
                form = ProcessorForm( request.POST,instance=processor)
                if form.is_valid():
                    email_update = request.POST.get('contact_email1')
                    name_update = request.POST.get('contact_name1')
                    phone_update = request.POST.get('contact_phone1')
                    fax_update = request.POST.get('contact_fax1')
                    obj_id.contact_name = name_update
                    obj_id.contact_email = email_update
                    obj_id.contact_phone = phone_update
                    obj_id.contact_fax = fax_update
                    obj_id.save()
                    log_email = ''
                    if email_update != processor_email:
                        f_name = name_update
                        user.email = email_update
                        user.username = email_update
                        user.first_name = f_name
                        user.save()
                        form.save()
                        log_email = email_update
                    else :
                        f_name = name_update
                        user.first_name = f_name
                        user.save()
                        form.save()
                        log_email = obj_id.contact_email
                    # 07-04-23 Log Table
                    log_type, log_status, log_device = "ProcessorUser", "Edited", "Web"
                    log_idd, log_name = obj_id.id, name_update
                    log_details = f"processor_id = {obj_id.processor.id} | processor = {obj_id.processor.entity_name} | contact_name= {name_update} | contact_email = {email_update} | contact_phone = {phone_update} | contact_fax = {fax_update}"
                    action_by_userid = request.user.id
                    userr = User.objects.get(pk=action_by_userid)
                    user_role = userr.role.all()
                    action_by_username = f'{userr.first_name} {userr.last_name}'
                    action_by_email = userr.username
                    if request.user.id == 1 :
                        action_by_role = "superuser"
                    else:
                        action_by_role = str(','.join([str(i.role) for i in user_role]))
                    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                                        action_by_email=action_by_email,action_by_role=action_by_role,log_email=log_email,
                                        log_details=log_details,log_device=log_device)
                    logtable.save()
                    return redirect('list-processor')
            return render(request, 'processor/update_processor.html',context)
    else:
        return redirect('login')

@login_required()
def ProcessorDelete(request,pk):
    processor = ProcessorUser.objects.get(id=pk)
    user = User.objects.get(username=processor.contact_email)
    # 07-04-23
    log_type, log_status, log_device = "ProcessorUser", "Deleted", "Web"
    log_idd, log_name = processor.id, processor.contact_name
    log_email = processor.contact_email
    log_details = f"processor_id = {processor.processor.id} | processor = {processor.processor.entity_name} | contact_name= {processor.contact_name} | contact_email = {processor.contact_email} | contact_phone = {processor.contact_phone} | contact_fax = {processor.contact_fax}"
    action_by_userid = request.user.id
    userr = User.objects.get(pk=action_by_userid)
    user_role = userr.role.all()
    action_by_username = f'{userr.first_name} {userr.last_name}'
    action_by_email = userr.username
    if request.user.id == 1 :
        action_by_role = "superuser"
    else:
        action_by_role = str(','.join([str(i.role) for i in user_role]))
    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                        action_by_email=action_by_email,action_by_role=action_by_role,log_email=log_email,
                        log_details=log_details,log_device=log_device)
    logtable.save()
    processor.delete()
    user.delete()
    return HttpResponse (1)
    # return redirect('list-processor')

def addlocation(request):
    if request.user.is_authenticated:
        context ={}
        # Processor ....
        if request.user.is_processor :
            context = {}
            form = LocationForm()
            context['form']=form
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            processor_email =user.username

            p = ProcessorUser.objects.get(contact_email=processor_email)
            processor_obj = Processor.objects.get(id=p.processor_id)

            # processor_obj = Processor.objects.get(contact_email=processor_email)
            print(processor_obj.id)
            if request.method == 'POST':
                form = LocationForm(request.POST)
                name = request.POST.get('name')
                upload_type = request.POST.get('upload_type')
                processor = processor_obj.id
                if request.FILES.get('zip_file'):
                    zip_file = request.FILES.get('zip_file')
                    Location(processor_id=processor, name=name,upload_type=upload_type,shapefile_id=zip_file).save()
                    location_obj = Location.objects.filter(processor_id=processor).filter(name=name)        
                    location_var = [i.id for i in location_obj][0]
                    location_id = Location.objects.get(id=location_var)
                    sf = shapefile.Reader(location_id.shapefile_id.path)
                    features = sf.shapeRecords()
                    for feat in features:
                        eschlon_id = feat.record["id"]
                        location_id.eschlon_id = eschlon_id
                        location_id.save()

                if request.POST.get('latitude') and request.POST.get('longitude'):
                    latitude = request.POST.get('latitude')
                    longitude = request.POST.get('longitude')
                    Location(processor_id=processor, name=name,upload_type=upload_type,latitude=latitude,longitude=longitude).save()
                
                return redirect('list-location')

            return render(request, 'processor/add_location.html',context)
        # Super User ...
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            form = LocationForm()
            processor = Processor.objects.all()
            context['form']=form
            context['processor']=processor
            if request.method == 'POST':
                form = LocationForm(request.POST)
                name = request.POST.get('name')
                upload_type = request.POST.get('upload_type')
                processor = int(request.POST.get('processor_id'))  
                if request.FILES.get('zip_file'):
                    zip_file = request.FILES.get('zip_file')
                    Location(processor_id=processor, name=name,upload_type=upload_type,shapefile_id=zip_file).save()
                    location_obj = Location.objects.filter(name=name).filter(processor=processor)          
                    location_var = [i.id for i in location_obj][0]
                    location_id = Location.objects.get(id=location_var)
                    sf = shapefile.Reader(location_id.shapefile_id.path)
                    features = sf.shapeRecords()
                    for feat in features:
                        eschlon_id = feat.record["id"]
                        location_id.eschlon_id = eschlon_id
                        location_id.save()

                if request.POST.get('latitude') and request.POST.get('longitude'):
                    latitude = request.POST.get('latitude')
                    longitude = request.POST.get('longitude')
                    Location(processor_id=processor, name=name,upload_type=upload_type,latitude=latitude,longitude=longitude).save()
                    
                return redirect('list-location')
            return render(request, 'processor/add_location.html',context)
    else:
        return redirect('login')


def location_list(request):
    if request.user.is_authenticated:
        # processor ...
        if request.user.is_processor :
            context ={}
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor = Processor.objects.get(id=p.processor_id)
            location = Location.objects.filter(processor= processor)
            context['location'] = location
            return render(request, 'processor/location_list.html',context)

        # superuser ...
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context ={}
            location = Location.objects.all()
            processor = Processor.objects.all()
            context['location'] = location
            context['processor'] = processor
            if request.method == 'POST':
                value = request.POST.get('processor_id')
                print(value)
                if value == 'all' :
                    location = Location.objects.all()
                    processor = Processor.objects.all()
                    context['location'] = location
                    context['processor'] = processor
                    return render(request, 'processor/location_list.html',context)

                else:
                    processor_id = request.POST.get('processor_id')
                    processor = Processor.objects.all()
                    location = Location.objects.filter(processor_id=processor_id)
                    context['location'] = location
                    context['processor'] = processor
                    context['selectedprocessor'] = Processor.objects.get(id=processor_id)
                    return render(request, 'processor/location_list.html',context)
                   
            return render(request, 'processor/location_list.html',context)
    else:
        return redirect('login')


def location_edit(request,pk):
    if request.user.is_authenticated:
        # processor ...
        if request.user.is_processor :
            context = {}
            location = Location.objects.get(id=pk)
            form = LocationForm(instance=location)
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor = Processor.objects.filter(id=p.processor_id)
            context['form'] = form
            context['processor'] = processor
            context['selectedprocessor'] = location.processor_id
            context['uploadtypeselect'] = location.upload_type
            location = Location.objects.filter(id=pk)
            context['location'] = location
            if request.method == 'POST':
                name = request.POST.get('name')
                uploadtypeSelction = request.POST.get('uploadtypeSelction')
                shapefile_id = request.FILES.get('zip_file')
                latitude = request.POST.get('latitude')
                longitude = request.POST.get('longitude')
                location_update = Location.objects.get(id=pk)
                if uploadtypeSelction == 'shapefile':
                    if request.FILES.get('zip_file'):
                        location_update.name = name
                        location_update.upload_type = 'shapefile'
                        location_update.shapefile_id = shapefile_id
                        location_update.latitude = None
                        location_update.longitude = None
                        location_update.save()
                        
                        sf = shapefile.Reader(location_update.shapefile_id.path)
                        features = sf.shapeRecords()
                        for feat in features:
                            eschlon_id = feat.record["id"]
                            location_update.eschlon_id = eschlon_id
                            location_update.save()
                    
                else:
                    location_update.name = name
                    location_update.upload_type = 'coordinates'
                    location_update.shapefile_id = None
                    location_update.eschlon_id = None
                    location_update.latitude = latitude
                    location_update.longitude = longitude
                    location_update.save()

                return redirect('list-location')

            return render(request, 'processor/location_edit.html',context)
        # superuser ....
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context ={}
            location = Location.objects.get(id=pk)
            form = LocationForm(instance=location)
            processor = Processor.objects.all()
            context['form'] = form
            context['processor'] = processor
            context['selectedprocessor'] = location.processor_id
            context['uploadtypeselect'] = location.upload_type
            location = Location.objects.filter(id=pk)
            context['location'] = location
            if request.method == 'POST':
                name = request.POST.get('name')
                processorSelction = int(request.POST.get('processor_name'))
                uploadtypeSelction = request.POST.get('uploadtypeSelction')
                shapefile_id = request.FILES.get('zip_file')
                latitude = request.POST.get('latitude')
                longitude = request.POST.get('longitude')
                location_update = Location.objects.get(id=pk)
                location_update.name = name
                location_update.save()
                if uploadtypeSelction == 'shapefile':
                    if request.FILES.get('zip_file'):
                        location_update.name = name
                        location_update.processor_id = processorSelction
                        location_update.upload_type = 'shapefile'
                        location_update.shapefile_id = shapefile_id
                        location_update.latitude = None
                        location_update.longitude = None
                        location_update.save()
                        
                        sf = shapefile.Reader(location_update.shapefile_id.path)
                        features = sf.shapeRecords()
                        for feat in features:
                            eschlon_id = feat.record["id"]
                            location_update.eschlon_id = eschlon_id
                            location_update.save()

                else:
                    print(name)
                    location_update.name = name
                    location_update.processor_id = processorSelction
                    location_update.upload_type = 'coordinates'
                    location_update.shapefile_id = None
                    location_update.eschlon_id = None
                    location_update.latitude = latitude
                    location_update.longitude = longitude
                    location_update.save()
                return redirect('list-location')
            return render(request, 'processor/location_edit.html',context)
    else:
        return redirect('login')

    
@login_required()
def LocationDelete(request,pk):
    location = Location.objects.get(id=pk)
    location.delete()
    return HttpResponse (1)

    
def LinkGrowertoProcessor(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context ={}
            grower_processor = LinkGrowerToProcessor.objects.all()
            grower_id = [i.grower.id for i in grower_processor]
            # print(grower_id)
            grower = Grower.objects.exclude(id__in=grower_id).order_by('name')
            context['grower'] = grower
            processor = Processor.objects.all()
            context['processor'] = processor
            if request.method == 'POST':
                processor_id = request.POST.get('processor_id')
                counter = request.POST.get('counter')
                # 20-02-23
                if processor_id and int(counter) > 1 :
                    msg1 = f"#{int(counter)} of growers are assigned to you, kindly check your assigned grower section"
                    puser_id_all1 = ProcessorUser.objects.filter(processor_id=processor_id)
                    for j in puser_id_all1 :
                        p_user_id1 = User.objects.get(username=j.contact_email)
                        notification_reason1 = 'Many grower assigned'
                        redirect_url1 = "/processor/grower_processor_management"
                        save_notification = ShowNotification(user_id_to_show=p_user_id1.id,msg=msg1,status="UNREAD",redirect_url=redirect_url1,
                        notification_reason=notification_reason1)
                        save_notification.save()

                for i in range(1,int(counter)+1):
                    grower_id = request.POST.get('grower_id{}'.format(i))
                    lgpp = LinkGrowerToProcessor(processor_id=processor_id,grower_id=grower_id)
                    lgpp.save()
                    # 20-04-23 LogTable
                    log_type, log_status, log_device = "LinkGrowerToProcessor", "Added", "Web"
                    log_idd, log_name = lgpp.id, f"{lgpp.grower.name} - {lgpp.processor.entity_name}"
                    log_details = f"grower_name = {lgpp.grower.name} | grower_id = {lgpp.grower.id} | processor = {lgpp.processor.entity_name} | processor_id = {lgpp.processor.id} | "
                    action_by_userid = request.user.id
                    user = User.objects.get(pk=action_by_userid)
                    user_role = user.role.all()
                    action_by_username = f'{user.first_name} {user.last_name}'
                    action_by_email = user.username
                    if request.user.id == 1 :
                        action_by_role = "superuser"
                    else:
                        action_by_role = str(','.join([str(i.role) for i in user_role]))
                    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                                        action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                        log_device=log_device)
                    logtable.save()
                    # 20-02-23
                    puser_id_all = ProcessorUser.objects.filter(processor_id=processor_id)
                    if int(counter) == 1 :
                        for j in puser_id_all :
                            grower_name = Grower.objects.get(id=grower_id).name
                            msg = f"A new grower with name: {grower_name} is assigned to you"
                            p_user_id = User.objects.get(username=j.contact_email)
                            notification_reason = 'Grower Assigned'
                            redirect_url = "/processor/grower_processor_management"
                            save_notification = ShowNotification(user_id_to_show=p_user_id.id,msg=msg,status="UNREAD",redirect_url=redirect_url,
                            notification_reason=notification_reason)
                            save_notification.save()                           

                return redirect('grower_processor_management')

            return render(request, 'processor/link_grower_processor.html',context)
    else:
        return redirect('login')


def GrowerProcessorManagement(request):
    if request.user.is_authenticated:
        # Processor ...
        if request.user.is_processor :
            context = {}
            user_email = request.user.email


            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id

            grower_processor = LinkGrowerToProcessor.objects.filter(processor_id=processor_id)
            g_id =[]
            for i in grower_processor:
                g = i.grower.id
                g_id.append(g)
            
            grower = Grower.objects.filter(id__in=g_id).order_by('name')
            context['grower'] = grower
            
            context['grower_processor'] = grower_processor
            if request.method == 'POST':
                grower_id = request.POST.get('grower_id')
                if request.method == 'POST':
                    grower_id = request.POST.get('grower_id')
                    if grower_id == '0':
                        context['grower_processor'] = grower_processor
                    
                    elif grower_id != '0':
                        grower_processor = LinkGrowerToProcessor.objects.filter(grower_id=grower_id)
                        context['grower_processor'] = grower_processor
                        context['selectedGrower'] = Grower.objects.get(id=grower_id)                
                        context['grower'] = grower
                    return render(request, 'processor/grower_processor_management.html',context)
            return render(request, 'processor/grower_processor_management.html',context)
        # superuser ...
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context ={}
            grower_processor_all = LinkGrowerToProcessor.objects.all()
            context['grower_processor'] = grower_processor_all
                            
            return render(request, 'processor/grower_processor_management.html',context)
    else:
        return redirect('login')

@login_required()
def GrowerProcessorManagementDelete(request,pk):
    grower_processor = LinkGrowerToProcessor.objects.get(id=pk)
    # 20-04-23 LogTable
    log_type, log_status, log_device = "LinkGrowerToProcessor", "Deleted", "Web"
    log_idd, log_name = grower_processor.id, f"{grower_processor.grower.name} - {grower_processor.processor.entity_name}"
    log_details = f"grower_name = {grower_processor.grower.name} | grower_id = {grower_processor.grower.id} | processor = {grower_processor.processor.entity_name} | processor_id = {grower_processor.processor.id} | "
    action_by_userid = request.user.id
    user = User.objects.get(pk=action_by_userid)
    user_role = user.role.all()
    action_by_username = f'{user.first_name} {user.last_name}'
    action_by_email = user.username
    if request.user.id == 1 :
        action_by_role = "superuser"
    else:
        action_by_role = str(','.join([str(i.role) for i in user_role]))
    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                        action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                        log_device=log_device)
    logtable.save()
    grower_processor.delete()
    return HttpResponse (1)

def all_grower_map_to_processor(request):
    if request.user.is_authenticated:
        if request.user.is_processor :
            context = {}
            user_email = request.user.email

            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id

            grower_processor = LinkGrowerToProcessor.objects.filter(processor_id=processor_id)
            g_id =[]
            for i in grower_processor:
                g = i.grower.id
                g_id.append(g)
            
            get_growers = Grower.objects.filter(id__in=g_id).order_by('name')
            context['grower'] = get_growers
            farm_obj = Farm.objects.filter(grower__in=get_growers)
            field_obj = Field.objects.filter(farm__in=farm_obj)
            shape_obj1 = ShapeFileDataCo.objects.filter(field__in=field_obj)

            storage_obj = Storage.objects.filter(grower_id__in=get_growers)
            shape_obj = StorageShapeFileDataCo.objects.filter(storage__in=storage_obj)
            print(farm_obj)
            # Field shapFile ...........
            polydata_n1 = '<subdivisions>'
            for shape in shape_obj1:
                coordinates = shape.coordinates
                polydata_n1 += '<subdivision fieldId="' + \
                    str(shape.field.id) + '" name="' + \
                    shape.field.name.replace("'", "") + '">'

                for coord in coordinates:
                    polydata_n1 += '<coord lat="' + \
                        str(coord[0]) + '" lng="' + str(coord[1]) + '"/>'

                polydata_n1 += '</subdivision>'
            polydata_n1 += '<subdivisions>'

            # Storage Shapefile ...
            polydata_n = '<subdivisions>'
            for shape in shape_obj:
                coordinates = shape.coordinates
                polydata_n += '<subdivision storageId="' + \
                    str(shape.storage.id) + '" name="' + \
                    shape.storage.storage_name.replace("'", "") + '">'

                for coord in coordinates:
                    polydata_n += '<coord lat="' + \
                        str(coord[0]) + '" lng="' + str(coord[1]) + '"/>'

                polydata_n += '</subdivision>'
            polydata_n += '<subdivisions>'

            # adding farms + storage .......
            polydata_n2 = polydata_n1 + polydata_n
            
            # For Storage Latitude and Longitude .....
            storage_pin = []
            for item in storage_obj:
                if item.latitude != None:
                    storage_pin.append(item)
            
            polydata_n = '<subdivisions>'
            for shape in storage_pin:
                # coordinates = shape.coordinates
                polydata_n += '<subdivision pointerId="' + \
                    str(shape.id) + '" name="' + \
                    shape.storage_name.replace("'", "") + '">'

                for coord in storage_pin:
                    polydata_n += '<coord lat="' + \
                        str(coord.latitude) + '" lng="' + str(coord.longitude) + '"/>'

                polydata_n += '</subdivision>'
            polydata_n += '<subdivisions>'
            context['polydata_n'] = polydata_n2
            context['polydata_n1'] = polydata_n
            context['get_growers'] = get_growers
            # context['selected_grower'] = selected_grower
            
            return render(request, 'processor/all_grower_map_to_processor.html',context)
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context = {}
            grower_processor = LinkGrowerToProcessor.objects.all()
            g_id =[]
            for i in grower_processor:
                g = i.grower.id
                g_id.append(g)
            get_growers = Grower.objects.filter(id__in=g_id).order_by('name')
            context['grower'] = get_growers
            farm_obj = Farm.objects.filter(grower__in=get_growers)
            field_obj = Field.objects.filter(farm__in=farm_obj)
            shape_obj1 = ShapeFileDataCo.objects.filter(field__in=field_obj)

            storage_obj = Storage.objects.filter(grower_id__in=get_growers)
            shape_obj = StorageShapeFileDataCo.objects.filter(storage__in=storage_obj)
           
            # Field shapFile ...........
            polydata_n1 = '<subdivisions>'
            for shape in shape_obj1:
                coordinates = shape.coordinates
                polydata_n1 += '<subdivision fieldId="' + \
                    str(shape.field.id) + '" name="' + \
                    shape.field.name.replace("'", "") + '">'

                for coord in coordinates:
                    polydata_n1 += '<coord lat="' + \
                        str(coord[0]) + '" lng="' + str(coord[1]) + '"/>'

                polydata_n1 += '</subdivision>'
            polydata_n1 += '<subdivisions>'

            # Storage Shapefile ...
            polydata_n = '<subdivisions>'
            for shape in shape_obj:
                coordinates = shape.coordinates
                polydata_n += '<subdivision storageId="' + \
                    str(shape.storage.id) + '" name="' + \
                    shape.storage.storage_name.replace("'", "") + '">'

                for coord in coordinates:
                    polydata_n += '<coord lat="' + \
                        str(coord[0]) + '" lng="' + str(coord[1]) + '"/>'

                polydata_n += '</subdivision>'
            polydata_n += '<subdivisions>'

            # adding farms + storage .......
            polydata_n2 = polydata_n1 + polydata_n
            
            # For Storage Latitude and Longitude .....
            storage_pin = []
            for item in storage_obj:
                if item.latitude != None:
                    storage_pin.append(item)
            
            polydata_n = '<subdivisions>'
            for shape in storage_pin:
                # coordinates = shape.coordinates
                polydata_n += '<subdivision pointerId="' + \
                    str(shape.id) + '" name="' + \
                    shape.storage_name.replace("'", "") + '">'

                for coord in storage_pin:
                    polydata_n += '<coord lat="' + \
                        str(coord.latitude) + '" lng="' + str(coord.longitude) + '"/>'

                polydata_n += '</subdivision>'
            polydata_n += '<subdivisions>'
            context['polydata_n'] = polydata_n2
            context['polydata_n1'] = polydata_n
            context['get_growers'] = get_growers
                        
            return render(request, 'processor/all_grower_map_to_processor.html',context)
    else:
        return redirect('login')


def grower_map_to_processor(request,pk):
    if request.user.is_authenticated:
        if request.user.is_processor :
            context = {}
            user_email = request.user.email

            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id

            grower_processor = LinkGrowerToProcessor.objects.filter(processor_id=processor_id)
            selected_grower = Grower.objects.get(id=pk).id
            context['selected_grower'] = selected_grower
            g_id =[]
            for i in grower_processor:
                g = i.grower.id
                g_id.append(g)
            
            get_growers = Grower.objects.filter(id__in=g_id).order_by('name')
            get_growers_map = Grower.objects.filter(id=pk).order_by('name')
            context['grower'] = get_growers
            context['growers_map'] = get_growers_map
            farm_obj = Farm.objects.filter(grower__in=get_growers_map)
            field_obj = Field.objects.filter(farm__in=farm_obj)
            shape_obj1 = ShapeFileDataCo.objects.filter(field__in=field_obj)

            storage_obj = Storage.objects.filter(grower_id__in=get_growers_map)
            shape_obj = StorageShapeFileDataCo.objects.filter(storage__in=storage_obj)
            
            # Field shapFile ...........
            polydata_n1 = '<subdivisions>'
            for shape in shape_obj1:
                coordinates = shape.coordinates
                polydata_n1 += '<subdivision fieldId="' + \
                    str(shape.field.id) + '" name="' + \
                    shape.field.name.replace("'", "") + '">'

                for coord in coordinates:
                    polydata_n1 += '<coord lat="' + \
                        str(coord[0]) + '" lng="' + str(coord[1]) + '"/>'

                polydata_n1 += '</subdivision>'
            polydata_n1 += '<subdivisions>'

            # Storage Shapefile ...
            polydata_n = '<subdivisions>'
            for shape in shape_obj:
                coordinates = shape.coordinates
                polydata_n += '<subdivision storageId="' + \
                    str(shape.storage.id) + '" name="' + \
                    shape.storage.storage_name.replace("'", "") + '">'

                for coord in coordinates:
                    polydata_n += '<coord lat="' + \
                        str(coord[0]) + '" lng="' + str(coord[1]) + '"/>'

                polydata_n += '</subdivision>'
            polydata_n += '<subdivisions>'

            # adding farms + storage .......
            polydata_n2 = polydata_n1 + polydata_n
            
            # For Storage Latitude and Longitude .....
            storage_pin = []
            for item in storage_obj:
                if item.latitude != None:
                    storage_pin.append(item)
            
            polydata_n = '<subdivisions>'
            for shape in storage_pin:
                # coordinates = shape.coordinates
                polydata_n += '<subdivision pointerId="' + \
                    str(shape.id) + '" name="' + \
                    shape.storage_name.replace("'", "") + '">'

                for coord in storage_pin:
                    polydata_n += '<coord lat="' + \
                        str(coord.latitude) + '" lng="' + str(coord.longitude) + '"/>'

                polydata_n += '</subdivision>'
            polydata_n += '<subdivisions>'
            context['polydata_n'] = polydata_n2
            context['polydata_n1'] = polydata_n
            context['get_growers'] = get_growers
            # context['selected_grower'] = selected_grower
            
            return render(request, 'processor/grower_map_to_processor.html',context)
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context = {}
            grower_processor = LinkGrowerToProcessor.objects.all()
            selected_grower = Grower.objects.get(id=pk).id
            context['selected_grower'] = selected_grower
            g_id =[]
            for i in grower_processor:
                g = i.grower.id
                g_id.append(g)
            get_growers = Grower.objects.filter(id__in=g_id).order_by('name')
            get_growers_map = Grower.objects.filter(id=pk).order_by('name')
            context['grower'] = get_growers
            context['growers_map'] = get_growers_map
            farm_obj = Farm.objects.filter(grower__in=get_growers_map)
            field_obj = Field.objects.filter(farm__in=farm_obj)
            shape_obj1 = ShapeFileDataCo.objects.filter(field__in=field_obj)

            storage_obj = Storage.objects.filter(grower_id__in=get_growers_map)
            shape_obj = StorageShapeFileDataCo.objects.filter(storage__in=storage_obj)
            print(farm_obj)
            # Field shapFile ...........
            polydata_n1 = '<subdivisions>'
            for shape in shape_obj1:
                coordinates = shape.coordinates
                polydata_n1 += '<subdivision fieldId="' + \
                    str(shape.field.id) + '" name="' + \
                    shape.field.name.replace("'", "") + '">'

                for coord in coordinates:
                    polydata_n1 += '<coord lat="' + \
                        str(coord[0]) + '" lng="' + str(coord[1]) + '"/>'

                polydata_n1 += '</subdivision>'
            polydata_n1 += '<subdivisions>'

            # Storage Shapefile ...
            polydata_n = '<subdivisions>'
            for shape in shape_obj:
                coordinates = shape.coordinates
                polydata_n += '<subdivision storageId="' + \
                    str(shape.storage.id) + '" name="' + \
                    shape.storage.storage_name.replace("'", "") + '">'

                for coord in coordinates:
                    polydata_n += '<coord lat="' + \
                        str(coord[0]) + '" lng="' + str(coord[1]) + '"/>'

                polydata_n += '</subdivision>'
            polydata_n += '<subdivisions>'

            # adding farms + storage .......
            polydata_n2 = polydata_n1 + polydata_n
            
            # For Storage Latitude and Longitude .....
            storage_pin = []
            for item in storage_obj:
                if item.latitude != None:
                    storage_pin.append(item)
            
            polydata_n = '<subdivisions>'
            for shape in storage_pin:
                # coordinates = shape.coordinates
                polydata_n += '<subdivision pointerId="' + \
                    str(shape.id) + '" name="' + \
                    shape.storage_name.replace("'", "") + '">'

                for coord in storage_pin:
                    polydata_n += '<coord lat="' + \
                        str(coord.latitude) + '" lng="' + str(coord.longitude) + '"/>'

                polydata_n += '</subdivision>'
            polydata_n += '<subdivisions>'
            context['polydata_n'] = polydata_n2
            context['polydata_n1'] = polydata_n
            context['get_growers'] = get_growers
            # context['selected_grower'] = selected_grower
            
            return render(request, 'processor/grower_map_to_processor.html',context)
    else:
        return redirect('login')
    
def grower_shipment(request):
    if request.user.is_authenticated:
        status = ""
        if 'Grower' in request.user.get_role() and not request.user.is_superuser:
            context ={}
            form = GrowerShipmentForm()
            context['form'] =form
            grower_id= request.user.grower.id
            if LinkGrowerToProcessor.objects.filter(grower_id=grower_id).count() !=0:
                grower_processor = LinkGrowerToProcessor.objects.get(grower_id=grower_id)
                processor = grower_processor.processor.entity_name
                p_user = ProcessorUser.objects.filter(processor_id=grower_processor.processor.id)
                processor_id = grower_processor.processor.id
                context ['processor']=processor
                storage = Storage.objects.filter(grower_id=grower_id)
                context ['storage']=storage
                field = Field.objects.filter(grower_id=grower_id)
                context ['field']=field
                
                if request.method == 'POST':
                    id_storage = request.POST.get('id_storage')
                    module_number = request.POST.get('module_number')
                    id_field = request.POST.get('id_field')


                    amount1 = request.POST.get('amount1')
                    amount2 = request.POST.get('amount2')

                    id_unit1 = request.POST.get('id_unit1')
                    id_unit2= request.POST.get('id_unit2')
                    
                    get_output= request.POST.get('get_output')

                    sustain_data = SustainabilitySurvey.objects.filter(grower_id=grower_id,field_id=id_field)

                    if sustain_data.count() > 0:
                        Avg_Percentage_Score_data = sustain_data.aggregate(Avg('sustainabilityscore'))
                        surveyscore = int(Avg_Percentage_Score_data['sustainabilityscore__avg'])
                    else:
                        surveyscore = 0

                    if len(amount1) > 0 and len(amount2) == 0:
                        if id_unit1 == '1':
                            id_unit1 = 'LBS'
                            id_unit2 = ''
                        if id_unit1 == '38000':
                            id_unit1 = 'MODULES (8 ROLLS)'
                            id_unit2 = ''
                        if id_unit1 == '19000':
                            id_unit1 = 'SETS (4 ROLLS)'
                            id_unit2 = ''
                        if id_unit1 == '4750':
                            id_unit1 = 'ROLLS'
                            id_unit2 = ''
                    
                    if len(amount1) > 0 and len(amount2) > 0:
                        if id_unit1 == '1':
                            id_unit1 = 'LBS'
                        if id_unit1 == '38000':
                            id_unit1 = 'MODULES (8 ROLLS)'
                        if id_unit1 == '19000':
                            id_unit1 = 'SETS (4 ROLLS)'
                        if id_unit1 == '4750':
                            id_unit1 = 'ROLLS'
                        if id_unit2 == '1':
                            id_unit2 = 'LBS'
                        if id_unit2 == '38000':
                            id_unit2 = 'MODULES (8 ROLLS)'
                        if id_unit2 == '19000':
                            id_unit2 = 'SETS (4 ROLLS)'
                        if id_unit2 == '4750':
                            id_unit2 = 'ROLLS'

                    if id_field and module_number:
                        field = Field.objects.get(id=id_field)
                        field_eschlon_id = field.eschlon_id
                        crop = field.crop
                        if crop == "RICE":
                            status = ""
                        if crop == "WHEAT":
                            status = ""
                        if crop == "COTTON":
                            status = "APPROVED"
                        variety = field.variety 
                        shipment_id = generate_shipment_id()
                        
                        if id_storage == None :
                            id_storage = None
                            storage_name = ''
                        else:
                            id_storage = id_storage
                            s = Storage.objects.get(id=id_storage)
                            storage_name = s.storage_name
                        shipment = GrowerShipment(status=status,total_amount=get_output,unit_type2=id_unit2,amount2=amount2,shipment_id=shipment_id,processor_id=processor_id,grower_id=grower_id,storage_id=id_storage,field_id=id_field,crop=crop,variety=variety,amount=amount1,sustainability_score=surveyscore,echelon_id=field_eschlon_id,module_number=module_number,unit_type=id_unit1)
                        shipment.save()
                        # Sending Email
                        g = Grower.objects.get(id=grower_id)
                        
                        field_name = field.name
                        for i in p_user:
                            html_message = render_to_string('processor/shipment_processor_notifi.html',\
                                {'processor': processor, 'grower_name' :g.name, 'shipment_id' :shipment_id, 'crop' :crop, 'variety': variety, 'amount' :amount1,'field_name':field_name,'field_eschlon_id' :field_eschlon_id, 'storage' : storage_name,'surveyscore':surveyscore})
                            send_mail('Shipment Notification','email','techsupportUS@agreeta.com',[i.contact_email],fail_silently=False,html_message=html_message)
                        
                        # 07-04-23 Log Table
                        log_type, log_status, log_device = "GrowerShipment", "Added", "Web"
                        log_idd, log_name = shipment.id, shipment.shipment_id
                        log_details = f"status = {status} | total_amount = {get_output} | unit_type2 = {id_unit2} | amount2 = {amount2} | echelon_id = {field.eschlon_id} | sustainability_score = {surveyscore} | amount = {amount1} | variety = {field.variety} | crop = {field.crop} | shipment_id = {shipment_id} | processor_id = {processor_id} | grower_id = {grower_id} | storage_id = {id_storage} | field_id = {id_field} | module_number = {module_number} | unit_type = {id_unit1} | "
                        action_by_userid = request.user.id
                        user = User.objects.get(pk=action_by_userid)
                        user_role = user.role.all()
                        action_by_username = f'{user.first_name} {user.last_name}'
                        action_by_email = user.username
                        if request.user.id == 1 :
                            action_by_role = "superuser"
                        else:
                            action_by_role = str(','.join([str(i.role) for i in user_role]))
                        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                                            action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                            log_device=log_device)
                        logtable.save()
                        return redirect('grower_shipment_list')
            else:
                return render(request, 'processor/grower_shipment.html',context)
            return render(request, 'processor/grower_shipment.html',context)
        
        if request.user.is_consultant:
            context ={}
            form = GrowerShipmentForm()
            context['form'] =form
            consultant_id = Consultant.objects.get(email=request.user.email).id
            get_growers = Grower.objects.filter(consultant=consultant_id).order_by('name')
            grower_id = [i.id for i in get_growers]
            if LinkGrowerToProcessor.objects.filter(grower_id__in=grower_id).count() !=0:
                print("grower_id.............",grower_id)
                # grower_processor = LinkGrowerToProcessor.objects.get(grower_id=grower_id[0])
                # grower_processor = LinkGrowerToProcessor.objects.get(grower_id=662)
                # processor = grower_processor.processor.entity_name
                # context ['processor']=processor
                linked_grower_id = [i.grower_id for i in LinkGrowerToProcessor.objects.filter(grower_id__in=grower_id)]
                linked_grower = Grower.objects.filter(id__in = linked_grower_id).order_by('name')
                context ['linked_grower']=linked_grower
                if request.method == 'POST':
                    id_g = request.POST.get('id_g')
                    if id_g !='all':
                        selected_grower = Grower.objects.get(id=id_g)
                        context['selected_grower'] = selected_grower
 
                        storage_obj = Storage.objects.filter(grower_id=id_g)
                        context['storage_obj'] = storage_obj

                        field_obj = Field.objects.filter(grower_id=id_g)
                        context['field'] = field_obj

                        id_storage = request.POST.get('id_sto')
                        id_field = request.POST.get('id_field')
                        module_number = request.POST.get('module_number')

                        #code 
                        amount1 = request.POST.get('amount1')
                        amount2 = request.POST.get('amount2')

                        id_unit1 = request.POST.get('id_unit1')
                        id_unit2= request.POST.get('id_unit2')
                        get_output= request.POST.get('get_output')
                        if len(amount1) > 0 and len(amount2) == 0:
                            if id_unit1 == '1':
                                id_unit1 = 'LBS'
                                id_unit2 = ''
                            if id_unit1 == '38000':
                                id_unit1 = 'MODULES (8 ROLLS)'
                                id_unit2 = ''
                            if id_unit1 == '19000':
                                id_unit1 = 'SETS (4 ROLLS)'
                                id_unit2 = ''
                            if id_unit1 == '4750':
                                id_unit1 = 'ROLLS'
                                id_unit2 = ''
                        
                        if len(amount1) > 0 and len(amount2) > 0:
                            if id_unit1 == '1':
                                id_unit1 = 'LBS'
                            if id_unit1 == '38000':
                                id_unit1 = 'MODULES (8 ROLLS)'
                            if id_unit1 == '19000':
                                id_unit1 = 'SETS (4 ROLLS)'
                            if id_unit1 == '4750':
                                id_unit1 = 'ROLLS'
                            if id_unit2 == '1':
                                id_unit2 = 'LBS'
                            if id_unit2 == '38000':
                                id_unit2 = 'MODULES (8 ROLLS)'
                            if id_unit2 == '19000':
                                id_unit2 = 'SETS (4 ROLLS)'
                            if id_unit2 == '4750':
                                id_unit2 = 'ROLLS'
                        
                        shipment_id = generate_shipment_id()
                        
                        processor_id = LinkGrowerToProcessor.objects.get(grower_id=selected_grower.id).processor_id
                      
                        if id_field and module_number:
                            field = Field.objects.get(id=id_field)
                            crop = field.crop
                            if crop == "RICE":
                                status = ""
                            if crop == "WHEAT":
                                status = ""
                            if crop == "COTTON":
                                status = "APPROVED"
                            
                            sustain_data = SustainabilitySurvey.objects.filter(grower_id=selected_grower.id,field_id=id_field)

                            if sustain_data.count() > 0:
                                Avg_Percentage_Score_data = sustain_data.aggregate(Avg('sustainabilityscore'))
                                surveyscore = int(Avg_Percentage_Score_data['sustainabilityscore__avg'])
                            else:
                                surveyscore = 0

                            if id_storage == None :
                                id_storage = None
                                storage_name = ''
                            else:
                                id_storage = id_storage
                                s = Storage.objects.get(id=id_storage)
                                storage_name = s.storage_name
                            shipment = GrowerShipment(status=status,total_amount=get_output,unit_type2=id_unit2,amount2=amount2,echelon_id=field.eschlon_id,sustainability_score=surveyscore,amount=amount1,variety=field.variety,crop=field.crop,shipment_id=shipment_id,processor_id=processor_id,grower_id=selected_grower.id,storage_id=id_storage,field_id=id_field,module_number=module_number,unit_type=id_unit1)
                            shipment.save()
                            # Sending Mail ...
                            processor = Processor.objects.get(id=processor_id)
                            p_user = ProcessorUser.objects.filter(processor_id = processor.id)

                            processor_name = processor.entity_name
                      
                            g= Grower.objects.get(id=selected_grower.id)
                            for i in p_user: 
                                html_message = render_to_string('processor/shipment_processor_notifi.html',\
                                {'processor': processor_name, 'grower_name' :g.name, 'shipment_id' :shipment_id, 'crop' :field.crop, 'variety': field.variety, 'amount' :amount1,'field_name':field.name,'field_eschlon_id' :field.eschlon_id, 'storage' : storage_name,'surveyscore':surveyscore})
                                send_mail('Shipment Notification','email','techsupportUS@agreeta.com',[i.contact_email],fail_silently=False,html_message=html_message)
                            
                            # 07-04-23 Log Table
                            log_type, log_status, log_device = "GrowerShipment", "Added", "Web"
                            log_idd, log_name = shipment.id, shipment.shipment_id
                            log_details = f"status = {status} | total_amount = {get_output} | unit_type2 = {id_unit2} | amount2 = {amount2} | echelon_id = {field.eschlon_id} | sustainability_score = {surveyscore} | amount = {amount1} | variety = {field.variety} | crop = {field.crop} | shipment_id = {shipment_id} | processor_id = {processor_id} | grower_id = {selected_grower.id} | storage_id = {id_storage} | field_id = {id_field} | module_number = {module_number} | unit_type = {id_unit1} | "
                            action_by_userid = request.user.id
                            user = User.objects.get(pk=action_by_userid)
                            user_role = user.role.all()
                            action_by_username = f'{user.first_name} {user.last_name}'
                            action_by_email = user.username
                            if request.user.id == 1 :
                                action_by_role = "superuser"
                            else:
                                action_by_role = str(','.join([str(i.role) for i in user_role]))
                            logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                                action_by_userid=action_by_userid,action_by_username=action_by_username,
                                                action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                                log_device=log_device)
                            logtable.save()

                            return redirect('grower_shipment_list')

                            
                        # return render(request, 'processor/grower_shipment.html',context)
            return render(request, 'processor/grower_shipment.html',context)

    else:
        return redirect('login')

@login_required()
def grower_shipment_delete(request,pk):
    shipmemt = GrowerShipment.objects.get(id=pk)
    # 10-04-23 Log Table
    log_type, log_status, log_device = "GrowerShipment", "Deleted", "Web"
    log_idd, log_name = shipmemt.id, shipmemt.shipment_id
    log_email = None
    log_details = f"status = {shipmemt.status} | total_amount = {shipmemt.total_amount} | unit_type2 = {shipmemt.unit_type2} | amount2 = {shipmemt.amount2} | echelon_id = {shipmemt.echelon_id} | sustainability_score = {shipmemt.sustainability_score} | amount = {shipmemt.amount} | variety = {shipmemt.variety} | crop = {shipmemt.crop} | shipment_id = {shipmemt.shipment_id} | processor_id = {shipmemt.processor.id} | grower_id = {shipmemt.grower.id} | field_id = {shipmemt.field.id} | module_number = {shipmemt.module_number} | unit_type = {shipmemt.unit_type} | "
    action_by_userid = request.user.id
    userr = User.objects.get(pk=action_by_userid)
    user_role = userr.role.all()
    action_by_username = f'{userr.first_name} {userr.last_name}'
    action_by_email = userr.username
    if request.user.id == 1 :
        action_by_role = "superuser"
    else:
        action_by_role = str(','.join([str(i.role) for i in user_role]))
    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                        action_by_userid=action_by_userid,action_by_username=action_by_username,log_details=log_details,
                        action_by_email=action_by_email,action_by_role=action_by_role,log_email=log_email,log_device=log_device)
    logtable.save()
    shipmemt.delete()
    return HttpResponse (1)

def grower_shipment_list(request):
    if request.user.is_authenticated:
        if 'Grower' in request.user.get_role() and not request.user.is_superuser:
            context ={}
            grower_id= request.user.grower.id
            grower_shipment = GrowerShipment.objects.filter(grower_id=grower_id)
            context['grower_shipment'] = grower_shipment            
            return render(request, 'processor/grower_shipment_list.html',context)
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context ={}
            grower_shipment = GrowerShipment.objects.all()
            context['grower_shipment'] = grower_shipment
            grower_id = [i.grower_id for i in grower_shipment]
            grower = Grower.objects.filter(id__in=grower_id)
            context['grower'] = grower
            if request.method == 'POST':
                selectgrower_id = request.POST.get('selectgrower_id')
                if selectgrower_id !='0':
                    grower_shipment = GrowerShipment.objects.filter(grower_id=selectgrower_id)
                    context['grower_shipment'] = grower_shipment
                    context['grower'] = grower
                    context['selectedGrower'] = Grower.objects.get(id=selectgrower_id)
                    
                else:
                    context['grower_shipment'] = grower_shipment
                    context['grower'] = grower
                return render(request, 'processor/grower_shipment_list.html',context)
            return render(request, 'processor/grower_shipment_list.html',context)

            # consultant ....
        if request.user.is_consultant:
            context ={}
            consultant_id = Consultant.objects.get(email=request.user.email).id
            get_growers = Grower.objects.filter(consultant=consultant_id).order_by('name')
            grower_id = [i.id for i in get_growers]
            grower_shipment =GrowerShipment.objects.filter(grower_id__in = grower_id)
            context['grower_shipment'] = grower_shipment
            grower_id = [i.grower_id for i in grower_shipment]
            grower = Grower.objects.filter(id__in=grower_id)
            context['grower'] = grower
            if request.method == 'POST':
                selectgrower_id = request.POST.get('selectgrower_id')
                if selectgrower_id !='0':
                    grower_shipment = GrowerShipment.objects.filter(grower_id=selectgrower_id)
                    context['grower_shipment'] = grower_shipment
                    context['grower'] = grower
                    context['selectedGrower'] = Grower.objects.get(id=selectgrower_id)
                    
                else:
                    context['grower_shipment'] = grower_shipment
                    context['grower'] = grower
                return render(request, 'processor/grower_shipment_list.html',context)
            return render(request, 'processor/grower_shipment_list.html',context)
            
    else:
        return redirect('login')


def qr_code_view(request,pk):
    if request.user.is_authenticated:
        context = {}
        user_email = request.user.email
        grower_shipment1 = GrowerShipment.objects.get(id =pk)
        processor_name = grower_shipment1.processor.entity_name
        grower_name = grower_shipment1.grower.name

        if grower_shipment1.storage_id == None:
            storage_name = ''
        else:
            storage_name = grower_shipment1.storage.storage_name
        
        field_name = grower_shipment1.field.name
        crop_name = grower_shipment1.crop
        variety_name = grower_shipment1.variety
        echelon_number = grower_shipment1.echelon_id
        sustainability = grower_shipment1.sustainability_score
        shipment_id = grower_shipment1.shipment_id
        module_tag_no = grower_shipment1.module_number
        # status = grower_shipment1.status

        if grower_shipment1.amount2 == None:
            a1 = grower_shipment1.amount
            unit_type1 = grower_shipment1.unit_type
            amount1 = a1 + ' ' + unit_type1
            amount2 = 'Null'
            # total = amount1 + ' LBS'
            total = str(grower_shipment1.total_amount) + ' LBS'
        else:
            a1 = grower_shipment1.amount
            a2 = grower_shipment1.amount2
            
            unit_type1 = grower_shipment1.unit_type
            unit_type2 = grower_shipment1.unit_type2

            amount1 = a1 + ' ' + unit_type1
            amount2 = a2 + ' ' + unit_type2
            total = str(grower_shipment1.total_amount) + ' LBS'

        shipment_date = grower_shipment1.date_time.strftime("%m-%d-%Y %H:%M:%S")
        # data = f"amount1: {amount1} \namount2: {amount2} \ntotal: {total} \nshipment_id: {shipment_id} \nmodule_tag_no: {module_tag_no} \nprocessor_name: {processor_name} \ngrower_name: {grower_name} \nstorage_name: {storage_name} \nfield_name: {field_name} \ncrop_name: {crop_name} \nvariety_name: {variety_name} \nechelon_number: {echelon_number} \nsustainability: {sustainability} \nshipment_date: {shipment_date}"
        datapy = {"amount1": amount1,"amount2": amount2,"total_amount": total,"shipment_id": shipment_id,"module_tag_no": module_tag_no,
        "processor_name": processor_name,"grower_name": grower_name,"storage_name": storage_name,"field_name": field_name,
        "crop_name": crop_name,"variety_name": variety_name,"echelon_number": echelon_number,"sustainability": sustainability,
        "shipment_date": shipment_date}
        data=json.dumps(datapy)
        img = make(data)
        img_name = 'qr' + str(time.time()) + '.png'
        img.save(settings.MEDIA_ROOT + '/' + img_name)
        context['img_name'] = img_name

        img = open('media/{}'.format(img_name), 'rb')
        response = FileResponse(img)
        # return img_name
        return HttpResponse (img_name)
    else:
        return redirect('login')


def grower_shipment_view(request,pk):
    if request.user.is_authenticated:
        context ={}
        grower_shipment = GrowerShipment.objects.filter(id=pk)
        context['grower_shipment'] = grower_shipment

        grower_shipment1 = GrowerShipment.objects.get(id = pk)
        processor_name = grower_shipment1.processor.entity_name
        grower_name = grower_shipment1.grower.name
        # status = grower_shipment1.status

        if grower_shipment1.storage_id == None:
            storage_name = ''
        else:
            storage_name = grower_shipment1.storage.storage_name

        field_name = grower_shipment1.field.name
        crop_name = grower_shipment1.crop
        variety_name = grower_shipment1.variety
        echelon_number = grower_shipment1.echelon_id
        sustainability = grower_shipment1.sustainability_score
        shipment_id = grower_shipment1.shipment_id
        module_tag_no = grower_shipment1.module_number

        if grower_shipment1.amount2 == None:
            a1 = grower_shipment1.amount
            unit_type1 = grower_shipment1.unit_type
            amount1 = a1 + ' ' + unit_type1
            amount2 = 'Null'
            # total = amount1 + ' LBS'
            total = str(grower_shipment1.total_amount) + ' LBS'
        else:
            a1 = grower_shipment1.amount
            a2 = grower_shipment1.amount2
            
            unit_type1 = grower_shipment1.unit_type
            unit_type2 = grower_shipment1.unit_type2

            amount1 = a1 + ' ' + unit_type1
            amount2 = a2 + ' ' + unit_type2
            total = str(grower_shipment1.total_amount) + ' LBS'

        shipment_date = grower_shipment1.date_time.strftime("%m-%d-%Y %H:%M:%S")
        # data = f"amount1: {amount1} \namount2: {amount2} \ntotal: {total} \nshipment_id: {shipment_id} \nmodule_tag_no: {module_tag_no} \nprocessor_name: {processor_name} \ngrower_name: {grower_name} \nstorage_name: {storage_name} \nfield_name: {field_name} \ncrop_name: {crop_name} \nvariety_name: {variety_name} \nechelon_number: {echelon_number} \nsustainability: {sustainability} \nshipment_date: {shipment_date}"
        datapy = {"amount1": amount1,"amount2": amount2,"total_amount": total,"shipment_id": shipment_id,"module_tag_no": module_tag_no,
        "processor_name": processor_name,"grower_name": grower_name,"storage_name": storage_name,"field_name": field_name,
        "crop_name": crop_name,"variety_name": variety_name,"echelon_number": echelon_number,"sustainability": sustainability,
        "shipment_date": shipment_date}
        data=json.dumps(datapy)
        img = make(data)
        img_name = 'qr' + str(time.time()) + '.png'
        img.save(settings.MEDIA_ROOT + '/' + img_name)
        context['img_name'] = img_name
        return render(request, 'processor/grower_shipment_view.html',context)
    else:
        return redirect('login')

def processor_inbound_management(request):
    if request.user.is_authenticated:
        # Processor ..
        if request.user.is_processor:
            context = {}
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id
            shipment = GrowerShipment.objects.filter(processor_id = processor_id)
            var_id = []
            for i in range(len(shipment)):
                location = shipment[i].location
                if location == None:
                    var = shipment[i].id
                    var_id.append(var)

            grower_shipment = GrowerShipment.objects.filter(id__in = var_id).filter(status="APPROVED")
            
            grower_id = [i.grower_id for i in grower_shipment]
            grower = Grower.objects.filter(id__in=grower_id).order_by('name')
            context['grower'] = grower

            context['selectedGrower'] = 'All'
            selectgrower_id = request.GET.get('selectgrower_id')
            search_name = request.GET.get('search_name') 
            #========================================= |auto complete suggestion|==============================
            get_shipment_id = [f"{i.shipment_id}" for i in grower_shipment]
            get_module_no = [f"{i.module_number}" for i in grower_shipment]
            get_crop = [f"{i.crop}" for i in grower_shipment]
            get_variety = [f"{i.variety}" for i in grower_shipment]
            get_status = [f"{i.status}" for i in grower_shipment]
            get_date = [datetime.strftime(i.date_time,"%m/%d/%Y") for i in grower_shipment]
            context["get_date"] = get_date
            get_grower_name = [f"{i.name}" for i in Grower.objects.only('name')]
            get_field_name = [f"{i.name}" for i in Field.objects.only('name')]

            lst = list(set(get_shipment_id + get_module_no  + get_crop  + get_variety + get_status + get_grower_name + get_field_name  + get_date))
            select_search_json = json.dumps(lst)
            context['select_search_json'] = select_search_json 

            if selectgrower_id !='All' and selectgrower_id != None :
                grower_shipment = GrowerShipment.objects.filter(id__in = var_id).filter(status="APPROVED").filter(grower_id=selectgrower_id)
                var_id = []
                for i in range(len(grower_shipment)):
                    location = grower_shipment[i].location
                    if location == None:
                        var = grower_shipment[i].id
                        var_id.append(var)
                grower_shipment = GrowerShipment.objects.filter(id__in = var_id)
                context['selectedGrower'] = Grower.objects.get(id=selectgrower_id)
            elif search_name :
                check_grower = Grower.objects.filter(name__icontains=search_name)
                check_field = Field.objects.filter(name__icontains=search_name)
                check_processor = Processor.objects.filter(entity_name__icontains=search_name)

                if check_grower.exists() :
                    check_grower_id = [i.id for i in check_grower]
                    grower_shipment = grower_shipment.filter(grower_id__in=check_grower_id)
                    context['get_search_name'] = search_name

                elif check_field.exists() :
                    check_field_id = [i.id for i in check_field]
                    grower_shipment = grower_shipment.filter(field_id__in=check_field_id)
                    context['get_search_name'] = search_name

                elif check_processor.exists() :
                    check_processor_id = [i.id for i in check_processor]
                    grower_shipment = grower_shipment.filter(processor_id__in=check_processor_id)
                    context['get_search_name'] = search_name
                else:
                    if "/" in search_name :
                        try:
                            search_date = [datetime.strptime(search_name,"%m/%d/%Y")]
                        except:
                            search_date = []
                        grower_shipment = grower_shipment.filter(date_time__date__in=search_date)
                    else:
                        grower_shipment = grower_shipment.filter(status="APPROVED",processor_id = processor_id).filter(Q(shipment_id__icontains=search_name) | Q(date_time__icontains=search_name) | 
                        Q(module_number__icontains=search_name) | Q(crop__icontains=search_name) | Q(variety__icontains=search_name) | 
                        Q(approval_date__icontains=search_name) | Q(total_amount__icontains=search_name) )
                context['get_search_name'] = search_name    
            
            else:
                grower_shipment = grower_shipment
            
            paginator = Paginator(grower_shipment, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)

            context['grower_shipment'] = report
            return render(request, 'processor/processor_inbound_management.html',context)
        
        # SuperUser ..
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context = {}
            shipment = GrowerShipment.objects.all()
            var_id = []
            for i in range(len(shipment)):
                location = shipment[i].location
                if location == None:
                    var = shipment[i].id
                    var_id.append(var)

            grower_shipment = GrowerShipment.objects.filter(id__in = var_id)
            context['grower_shipment'] = grower_shipment
            grower_id = [i.grower_id for i in grower_shipment]
            grower = Grower.objects.filter(id__in=grower_id).order_by('name')
            context['grower'] = grower

            context['selectedGrower'] = 'All'
        
            selectgrower_id = request.GET.get('selectgrower_id')
            search_name = request.GET.get('search_name') 
            #========================================= |auto complete suggestion|==============================
            get_shipment_id = [f"{i.shipment_id}" for i in grower_shipment]
            get_module_no = [f"{i.module_number}" for i in grower_shipment]
            get_crop = [f"{i.crop}" for i in grower_shipment]
            get_variety = [f"{i.variety}" for i in grower_shipment]
            get_status = [f"{i.status}" for i in grower_shipment]
            get_date = [datetime.strftime(i.date_time,"%m/%d/%Y") for i in grower_shipment]
            context["get_date"] = get_date
            get_grower_name = [f"{i.name}" for i in Grower.objects.only('name')]
            get_field_name = [f"{i.name}" for i in Field.objects.only('name')]
            get_processor_nm = [f"{i.entity_name}" for i in Processor.objects.only('entity_name')]
                    
            lst = list(set(get_shipment_id + get_module_no  + get_crop  + get_variety + get_status + get_grower_name + get_field_name + get_processor_nm + get_date))
            select_search_json = json.dumps(lst)
            context['select_search_json'] = select_search_json 

            if selectgrower_id !='All' and selectgrower_id != None :
                grower_shipment = GrowerShipment.objects.filter(grower_id=selectgrower_id)
                var_id = []
                for i in range(len(grower_shipment)):
                    location = grower_shipment[i].location
                    if location == None:
                        var = grower_shipment[i].id
                        var_id.append(var)
                grower_shipment = GrowerShipment.objects.filter(id__in = var_id)
                context['selectedGrower'] = Grower.objects.get(id=selectgrower_id)
            
            elif search_name :
                check_grower = Grower.objects.filter(name__icontains=search_name)
                check_field = Field.objects.filter(name__icontains=search_name)
                check_processor = Processor.objects.filter(entity_name__icontains=search_name)

                if check_grower.exists() :
                    check_grower_id = [i.id for i in check_grower]
                    grower_shipment = grower_shipment.filter(grower_id__in=check_grower_id)
                    context['get_search_name'] = search_name

                elif check_field.exists() :
                    check_field_id = [i.id for i in check_field]
                    grower_shipment = grower_shipment.filter(field_id__in=check_field_id)
                    context['get_search_name'] = search_name

                elif check_processor.exists() :
                    check_processor_id = [i.id for i in check_processor]
                    grower_shipment = grower_shipment.filter(processor_id__in=check_processor_id)
                    context['get_search_name'] = search_name
                else:
                    if "/" in search_name :
                        try:
                            search_date = [datetime.strptime(search_name,"%m/%d/%Y")]
                        except:
                            search_date = []
                        grower_shipment = grower_shipment.filter(date_time__date__in=search_date)
                        
                    else:
                        grower_shipment = grower_shipment.filter(Q(shipment_id__icontains=search_name) | Q(date_time__icontains=search_name) | 
                        Q(module_number__icontains=search_name) | Q(crop__icontains=search_name) | Q(variety__icontains=search_name) | 
                        Q(approval_date__icontains=search_name) | Q(status__icontains=search_name) | Q(total_amount__icontains=search_name) | 
                        Q(amount__icontains=search_name) | Q(amount2__icontains=search_name) )
                context['get_search_name'] = search_name    
            
            else:
                grower_shipment = grower_shipment
            
            paginator = Paginator(grower_shipment, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)

            context['grower_shipment'] = report
            return render(request, 'processor/processor_inbound_management.html',context)

    else:
        return redirect('login')

def processor_upcoming_inbound_management(request):
    if request.user.is_authenticated:
        # Processor ..
        if request.user.is_processor:
            context = {}
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id
            shipment = GrowerShipment.objects.filter(processor_id = processor_id)
            var_id = []
            for i in range(len(shipment)):
                location = shipment[i].location
                if location == None:
                    var = shipment[i].id
                    var_id.append(var)

            grower_shipment = GrowerShipment.objects.filter(id__in = var_id).filter(status="")
            
            context['grower_shipment'] = grower_shipment
            grower_id = [i.grower_id for i in grower_shipment]
            grower = Grower.objects.filter(id__in=grower_id)
            context['grower'] = grower
            if request.method == 'POST':
                selectgrower_id = request.POST.get('selectgrower_id')
                if selectgrower_id !='0':
                    grower_shipment = GrowerShipment.objects.filter(grower_id=selectgrower_id).filter(status="")
                    var_id = []
                    for i in range(len(grower_shipment)):
                        location = grower_shipment[i].location
                        if location == None:
                            var = grower_shipment[i].id
                            var_id.append(var)
                    grower_shipment = GrowerShipment.objects.filter(id__in = var_id).filter(status="")
                    context['grower_shipment'] = grower_shipment
                    context['grower'] = grower
                    context['selectedGrower'] = Grower.objects.get(id=selectgrower_id)
                else:
                    context['grower_shipment'] = grower_shipment
                    context['grower'] = grower
                return render(request, 'processor/processor_upcoming_inbound_management.html',context)
            return render(request, 'processor/processor_upcoming_inbound_management.html',context)


def processor_inbound_management_view(request,pk):
    if request.user.is_authenticated:
        # Processor ..
        context = {}
        
        if request.user.is_processor:
            user_email = request.user.email    # add new logic for checking pk present in the processor's data or not
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor.id).id
            # Check if pk exists in the processor's data
            grower_shipment = GrowerShipment.objects.filter(processor_id=processor_id, id=pk)
            if grower_shipment.exists():
                grower_shipment = GrowerShipment.objects.filter(id=pk)
                context['grower_shipment'] = grower_shipment
                
                grower_shipment1 = GrowerShipment.objects.get(id = pk)
                processor_name = grower_shipment1.processor.entity_name
                grower_name = grower_shipment1.grower.name
                # status = grower_shipment1.status

                if grower_shipment1.storage_id == None:
                    storage_name = ''
                else:
                    storage_name = grower_shipment1.storage.storage_name
                # storage_name = grower_shipment1.storage.storage_name
                field_name = grower_shipment1.field.name
                crop_name = grower_shipment1.crop
                variety_name = grower_shipment1.variety
                echelon_number = grower_shipment1.echelon_id
                sustainability = grower_shipment1.sustainability_score

                if grower_shipment1.amount2 == None:
                    a1 = grower_shipment1.amount
                    unit_type1 = grower_shipment1.unit_type
                    amount1 = a1 + ' ' + unit_type1
                    amount2 = 'Null'
                    # total = amount1 + ' LBS'
                    total = str(grower_shipment1.total_amount) + ' LBS'
                else:
                    a1 = grower_shipment1.amount
                    a2 = grower_shipment1.amount2
                    
                    unit_type1 = grower_shipment1.unit_type
                    unit_type2 = grower_shipment1.unit_type2

                    amount1 = a1 + ' ' + unit_type1
                    amount2 = a2 + ' ' + unit_type2
                    total = str(grower_shipment1.total_amount) + ' LBS'
                shipment_date = grower_shipment1.date_time.strftime("%m-%d-%Y %H:%M:%S")
                shipment_id = grower_shipment1.shipment_id
                module_tag_no = grower_shipment1.module_number
                # data = f"amount1: {amount1} \namount2: {amount2} \ntotal: {total} \nprocessor_name: {processor_name} \ngrower_name: {grower_name} \nstorage_name: {storage_name} \nfield_name: {field_name} \ncrop_name: {crop_name} \nvariety_name: {variety_name} \nechelon_number: {echelon_number} \nsustainability: {sustainability}"
                datapy = {"amount1": amount1,"amount2": amount2,"total_amount": total,"shipment_id": shipment_id,"module_tag_no": module_tag_no,
                "processor_name": processor_name,"grower_name": grower_name,"storage_name": storage_name,"field_name": field_name,
                "crop_name": crop_name,"variety_name": variety_name,"echelon_number": echelon_number,"sustainability": sustainability,
                "shipment_date": shipment_date}
                data=json.dumps(datapy)
                img = make(data)
                img_name = 'qr' + str(time.time()) + '.png'
                # img.save(settings.MEDIA_ROOT + '/' + img_name)
                img.save(str(settings.MEDIA_ROOT) + '/' + img_name)
                context['img_name'] = img_name
                return render(request, 'processor/processor_inbound_management_view.html',context)
            else:
                return render(request, 'processor/processor_inbound_management_view.html',context)
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            grower_shipment = GrowerShipment.objects.filter(id=pk)
            context['grower_shipment'] = grower_shipment

            grower_shipment1 = GrowerShipment.objects.get(id = pk)
            processor_name = grower_shipment1.processor.entity_name
            grower_name = grower_shipment1.grower.name
            # status = grower_shipment1.status

            if grower_shipment1.storage_id == None:
                storage_name = ''
            else:
                storage_name = grower_shipment1.storage.storage_name
            # storage_name = grower_shipment1.storage.storage_name
            field_name = grower_shipment1.field.name
            crop_name = grower_shipment1.crop
            variety_name = grower_shipment1.variety
            echelon_number = grower_shipment1.echelon_id
            sustainability = grower_shipment1.sustainability_score
            if grower_shipment1.amount2 == None:
                a1 = grower_shipment1.amount
                unit_type1 = grower_shipment1.unit_type
                amount1 = a1 + ' ' + unit_type1
                amount2 = 'Null'
                # total = amount1 + ' LBS'
                total = str(grower_shipment1.total_amount) + ' LBS'
            else:
                a1 = grower_shipment1.amount
                a2 = grower_shipment1.amount2
                
                unit_type1 = grower_shipment1.unit_type
                unit_type2 = grower_shipment1.unit_type2

                amount1 = a1 + ' ' + unit_type1
                amount2 = a2 + ' ' + unit_type2
                total = str(grower_shipment1.total_amount) + ' LBS'
            shipment_date = grower_shipment1.date_time.strftime("%m-%d-%Y %H:%M:%S")
            shipment_id = grower_shipment1.shipment_id
            module_tag_no = grower_shipment1.module_number
            # data = f"amount1: {amount1} \namount2: {amount2} \ntotal: {total} \nprocessor_name: {processor_name} \ngrower_name: {grower_name} \nstorage_name: {storage_name} \nfield_name: {field_name} \ncrop_name: {crop_name} \nvariety_name: {variety_name} \nechelon_number: {echelon_number} \nsustainability: {sustainability}"
            datapy = {"amount1": amount1,"amount2": amount2,"total_amount": total,"shipment_id": shipment_id,"module_tag_no": module_tag_no,
            "processor_name": processor_name,"grower_name": grower_name,"storage_name": storage_name,"field_name": field_name,
            "crop_name": crop_name,"variety_name": variety_name,"echelon_number": echelon_number,"sustainability": sustainability,
            "shipment_date": shipment_date}
            data=json.dumps(datapy)
            img = make(data)
            img_name = 'qr' + str(time.time()) + '.png'
            # img.save(settings.MEDIA_ROOT + '/' + img_name)
            img.save(str(settings.MEDIA_ROOT) + '/' + img_name)
            context['img_name'] = img_name
            return render(request, 'processor/processor_inbound_management_view.html',context)
    else:
        return redirect('login')

@login_required()
def processor_inbound_management_delete(request,pk):
    shipment = GrowerShipment.objects.get(pk=pk)
    # 07-04-23
    log_type, log_status, log_device = "GrowerShipment", "Deleted", "Web"
    log_idd, log_name = shipment.id, shipment.shipment_id
    log_details = f"status = {shipment.status} | total_amount = {shipment.total_amount} | unit_type2 = {shipment.unit_type2} | amount2 = {shipment.amount2} | echelon_id = {shipment.echelon_id} | sustainability_score = {shipment.sustainability_score} | amount = {shipment.amount} | variety = {shipment.variety} | crop = {shipment.crop} | shipment_id = {shipment.shipment_id} | processor_id = {shipment.processor.id} | grower_id = {shipment.grower.id} | field_id = {shipment.field.id} | module_number = {shipment.module_number} | unit_type = {shipment.unit_type} | "
    action_by_userid = request.user.id
    user = User.objects.get(pk=action_by_userid)
    user_role = user.role.all()
    action_by_username = f'{user.first_name} {user.last_name}'
    action_by_email = user.username
    if request.user.id == 1 :
        action_by_role = "superuser"
    else:
        action_by_role = str(','.join([str(i.role) for i in user_role]))
    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                        action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                        log_device=log_device)
    logtable.save()

    shipment.delete()
    return HttpResponse (1)

def processor_inbound_management_edit(request,pk):
    if request.user.is_authenticated:
        context = {}
        # Processor Location Add ..
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            shipment = GrowerShipment.objects.get(pk=pk)
            selected_grower = shipment.grower
            id_grower = selected_grower.id
            # grower = LinkGrowerToProcessor.objects.all()
            # grower_id = [i.grower_id for i in grower]
            # get_grower = Grower.objects.filter(id__in = grower_id)
            # context['get_grower'] = get_grower
            context['selected_grower'] = selected_grower

            storage_obj = Storage.objects.filter(grower_id=id_grower)
            context['storage'] = storage_obj
            selected_storage = shipment.storage
            context['selected_storage'] = selected_storage

            field_obj = Field.objects.filter(grower_id=id_grower)
            context['field'] = field_obj
            selected_field = shipment.field
            context['selected_field'] = selected_field
            module_number = shipment.module_number
            context['module_number'] = module_number
            amount1 = shipment.amount
            context['amount1'] = amount1
            amount1 = shipment.amount
            context['amount1'] = amount1
            id_unit1 = shipment.unit_type
            context['id_unit1'] = id_unit1

            amount2 = shipment.amount2
            context['amount2'] = amount2
            id_unit2 = shipment.unit_type2
            context['id_unit2'] = id_unit2
            get_output = shipment.total_amount
            if get_output:
                get_output = shipment.total_amount
            else:
                get_output = shipment.received_amount
            # print('shipment.total_amount',shipment.total_amount)
            context['get_output'] = get_output
            get_status = shipment.status
            context['get_status'] = get_status

            recieved_weight = shipment.received_amount
            context['recieved_weight'] = recieved_weight

            ticket_number = shipment.token_id
            context['ticket_number'] = ticket_number
            get_crop = shipment.crop
            context['get_crop'] = get_crop

            aapproval_date = shipment.approval_date
            if aapproval_date :
                aapproval_date = str(aapproval_date)
            else:
                aapproval_date = ''
            context['approval_date'] = aapproval_date

            get_bin_location_processor = shipment.bin_location_processor
            if get_bin_location_processor :
                get_bin_location_processor = get_bin_location_processor
            else:
                get_bin_location_processor = ''
            context['reason_for_disapproval'] = shipment.reason_for_disapproval
            context['moisture_level'] = shipment.moisture_level
            context['fancy_count'] = shipment.fancy_count
            context['head_count'] = shipment.head_count
            context['bin_location_processor'] = get_bin_location_processor

            if request.method == 'POST':
                id_storage = request.POST.get('id_storage')
                id_field = request.POST.get('id_field')
                module_number = request.POST.get('module_number')
                amount1 = request.POST.get('amount1')
                amount2 = request.POST.get('amount2')
                id_unit1 = request.POST.get('id_unit1')
                id_unit2= request.POST.get('id_unit2')
                # code
                get_output= request.POST.get('get_output')
                id_status= request.POST.get('id_status')
                recieved_weight= request.POST.get('recieved_weight')
                ticket_number= request.POST.get('ticket_number')
                approval_date= request.POST.get('approval_date')

                reason_for_disapproval= request.POST.get('reason_for_disapproval')
                moisture_level= request.POST.get('moisture_level')
                fancy_count= request.POST.get('fancy_count')
                head_count= request.POST.get('head_count')
                bin_location_processor= request.POST.get('bin_location_processor')

                if id_status != None and id_status != "blank" and get_crop !='COTTON' :
                    if id_status == 'APPROVED' and recieved_weight :
                        shipment.status=id_status
                        shipment.received_amount=recieved_weight
                        shipment.token_id=ticket_number

                        if approval_date :
                            shipment.approval_date = approval_date
                        else:
                            shipment.approval_date= date.today()

                        shipment.moisture_level=moisture_level
                        shipment.fancy_count=fancy_count
                        shipment.head_count=head_count
                        shipment.bin_location_processor=bin_location_processor
                        
                        shipment.save()

                        msg_subject = 'Shipment is received as Approved'
                        msg_body = f'Dear Admin,\n\nA new shipment has been approved.\n\nThe details of the same are as below: \n\nShipment ID: {shipment.shipment_id} \nGrower: {shipment.grower.name} \nField: {shipment.field.name} \nReceived weight: {recieved_weight} LBS \nReceived date: {shipment.approval_date} \n\nRegards\nCustomer Service\nAgreeta'
                        from_email = 'techsupportUS@agreeta.com'
                        to_email = ['customerservice@agreeta.com']
                        send_mail(
                        msg_subject,
                        msg_body,
                        from_email,
                        to_email,
                        fail_silently=False,
                        )

                    elif id_status == 'DISAPPROVED' and reason_for_disapproval :
                        shipment.status=id_status
                        shipment.reason_for_disapproval=reason_for_disapproval
                        shipment.moisture_level=moisture_level
                        shipment.fancy_count=fancy_count
                        shipment.head_count=head_count
                        shipment.bin_location_processor=bin_location_processor
                        shipment.approval_date= date.today()

                        shipment.save()

                if len(amount1) > 0 and len(amount2) == 0:
                    if id_unit1 == '1':
                        id_unit1 = 'LBS'
                        id_unit2 = ''
                    if id_unit1 == '38000':
                        id_unit1 = 'MODULES (8 ROLLS)'
                        id_unit2 = ''
                    if id_unit1 == '19000':
                        id_unit1 = 'SETS (4 ROLLS)'
                        id_unit2 = ''
                    if id_unit1 == '4750':
                        id_unit1 = 'ROLLS'
                        id_unit2 = ''
                
                if len(amount1) > 0 and len(amount2) > 0:
                    if id_unit1 == '1':
                        id_unit1 = 'LBS'
                    if id_unit1 == '38000':
                        id_unit1 = 'MODULES (8 ROLLS)'
                    if id_unit1 == '19000':
                        id_unit1 = 'SETS (4 ROLLS)'
                    if id_unit1 == '4750':
                        id_unit1 = 'ROLLS'
                    if id_unit2 == '1':
                        id_unit2 = 'LBS'
                    if id_unit2 == '38000':
                        id_unit2 = 'MODULES (8 ROLLS)'
                    if id_unit2 == '19000':
                        id_unit2 = 'SETS (4 ROLLS)'
                    if id_unit2 == '4750':
                        id_unit2 = 'ROLLS'

                if id_storage == None :
                    id_storage = None
                    
                else:
                    id_storage = id_storage
                  
                if id_field and module_number:
                    field = Field.objects.get(id=id_field)

                    sustainabilitySurvey = SustainabilitySurvey.objects.filter(grower_id=selected_grower.id)
                    if len(sustainabilitySurvey) == 0:
                        surveyscore = 0
                    else:
                        surveyscore = [i.surveyscore for i in sustainabilitySurvey][0]
                    
                    if get_output:
                        shipment.total_amount=get_output
                    shipment.unit_type2=id_unit2
                    shipment.amount2=amount2
                    shipment.echelon_id=field.eschlon_id
                    shipment.sustainability_score=surveyscore
                    shipment.amount=amount1
                    shipment.variety=field.variety
                    shipment.crop=field.crop
                    shipment.storage_id=id_storage
                    shipment.field_id=id_field
                    shipment.module_number=module_number
                    shipment.unit_type=id_unit1

                    shipment.save()
                    # 07-04-23 Log Table
                    log_type, log_status, log_device = "GrowerShipment", "Edited", "Web"
                    log_idd, log_name = shipment.id, shipment.shipment_id
                    log_details = f"status = {id_status} | total_amount = {get_output} | unit_type2 = {id_unit2} | amount2 = {amount2} | echelon_id = {field.eschlon_id} | sustainability_score = {surveyscore} | amount = {amount1} | variety = {field.variety} | crop = {field.crop} | shipment_id = {shipment.shipment_id} | processor_id = {shipment.processor.id} | grower_id = {selected_grower.id} | storage_id = {id_storage} | field_id = {id_field} | module_number = {module_number} | unit_type = {id_unit1} | "
                    action_by_userid = request.user.id
                    user = User.objects.get(pk=action_by_userid)
                    user_role = user.role.all()
                    action_by_username = f'{user.first_name} {user.last_name}'
                    action_by_email = user.username
                    if request.user.id == 1 :
                        action_by_role = "superuser"
                    else:
                        action_by_role = str(','.join([str(i.role) for i in user_role]))
                    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                                        action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                        log_device=log_device)
                    logtable.save()
                    return redirect('processor_inbound_management')
            return render(request, 'processor/processor_inbound_management_edit.html',context)
    else:
        return redirect('login')
    

# def processor_location_assign(request,pk):
#     if request.user.is_authenticated:
#         # Processor Location Add ..
#         if request.user.is_processor:
#             context = {}
#             user_email = request.user.email

#             p = ProcessorUser.objects.get(contact_email=user_email)
#             processor_id = Processor.objects.get(id=p.processor_id).id

#             grower_shipment = GrowerShipment.objects.get(pk=pk)
#             context['grower_shipment'] = grower_shipment
#             location = Location.objects.filter(processor_id=processor_id)
#             context['location'] = location
#             if request.method == 'POST':
#                 id_location = request.POST.get('id_location')
#                 grower_shipment.location_id = id_location
#                 grower_shipment.save()
#                 return redirect ('processor_outbound_list')
#             return render(request, 'processor/processor_location_assign.html',context)
#         # SuperUser Location Add ..
#         if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
#             context = {}
#             grower_shipment = GrowerShipment.objects.get(pk=pk)
#             context['grower_shipment'] = grower_shipment
#             processor_id = grower_shipment.processor_id
#             location = Location.objects.filter(processor_id=processor_id)
#             context['location'] = location
#             if request.method == 'POST':
#                 id_location = request.POST.get('id_location')
#                 grower_shipment.location_id = id_location
#                 grower_shipment.save()
#                 return redirect ('processor_outbound_list')
#             return render(request, 'processor/processor_location_assign.html',context)
#     else:
#         return redirect('login')

def processor_outbound_list(request):
    if request.user.is_authenticated:
        # Processor Outbond List 
        if request.user.is_processor:
            context = {}
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id

            grower_shipment = GrowerShipment.objects.filter(processor_id=processor_id)
            grower_shipment_outbound = []
            for i in range(len(grower_shipment)):
                location = grower_shipment[i].location
                if location != None :
                    grower_shipment_outbound.append(grower_shipment[i].id)
            outbound_obj = GrowerShipment.objects.filter(id__in = grower_shipment_outbound)
            context['outbound_obj'] = outbound_obj
            grower_id = [i.grower_id for i in outbound_obj]
            grower = Grower.objects.filter(id__in=grower_id)
            context['grower'] = grower
            if request.method == 'POST':
                selectgrower_id = request.POST.get('grower_id')
                print(selectgrower_id)
                if selectgrower_id !='0':
                    grower_shipment = GrowerShipment.objects.filter(id__in = grower_shipment_outbound).filter(grower_id=selectgrower_id)
                    context['outbound_obj'] = grower_shipment
                    context['grower'] = grower
                    context['selectedGrower'] = Grower.objects.get(id=selectgrower_id)
                else:
                    context['outbound_obj'] = GrowerShipment.objects.filter(id__in = grower_shipment_outbound)
                    context['grower'] = grower
                return render(request, 'processor/processor_outbound_list.html',context)
            return render(request, 'processor/processor_outbound_list.html',context)
        
        # SuperUser Outbond List 
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context = {}
            grower_shipment = GrowerShipment.objects.all()
            grower_shipment_outbound = []
            for i in range(len(grower_shipment)):
                location = grower_shipment[i].location
                if location != None :
                    grower_shipment_outbound.append(grower_shipment[i].id)
            outbound_obj = GrowerShipment.objects.filter(id__in = grower_shipment_outbound)
            context['outbound_obj'] = outbound_obj
            grower_id = [i.grower_id for i in outbound_obj]
            grower = Grower.objects.filter(id__in=grower_id)
            context['grower'] = grower
            if request.method == 'POST':
                selectgrower_id = request.POST.get('grower_id')
                
                if selectgrower_id !='0':
                    grower_shipment = GrowerShipment.objects.filter(id__in = grower_shipment_outbound).filter(grower_id=selectgrower_id)
                    context['outbound_obj'] = grower_shipment
                    context['grower'] = grower
                    context['selectedGrower'] = Grower.objects.get(id=selectgrower_id)
                else:
                    context['outbound_obj'] = GrowerShipment.objects.filter(id__in = grower_shipment_outbound)
                    context['grower'] = grower
                return render(request, 'processor/processor_outbound_list.html',context)
            return render(request, 'processor/processor_outbound_list.html',context)
    else:
        return redirect('login')

@login_required()
def processor_outbound_delete(request,pk):
    shipment = GrowerShipment.objects.get(id= pk)
    shipment.location_id = None
    shipment.save()
    print(shipment)
    return HttpResponse (1)

def processor_process_material(request,pk):
    if request.user.is_authenticated:
        # Processor 
        context = {}
        if request.user.is_processor:
            grower_shipment = GrowerShipment.objects.filter(id=pk)
            context['grower_shipment'] = grower_shipment
            if request.method == 'POST':
                id_rolls = request.POST.get('id_rolls')
                id_date = request.POST.get('id_date')
                id_time = request.POST.get('id_time')
                id_sku = request.POST.get('id_sku')

                grower_shipment = GrowerShipment.objects.get(id=pk)
                grower_shipment.process_amount = id_rolls
                grower_shipment.process_date = id_date
                grower_shipment.process_time = id_time
                grower_shipment.sku = id_sku
                grower_shipment.save()

                return redirect ('processor_outbound_list')
            return render(request, 'processor/processor_process_material.html',context)
        # Superuser 
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            grower_shipment = GrowerShipment.objects.filter(id=pk)
            context['grower_shipment'] = grower_shipment
            if request.method == 'POST':
                id_rolls = request.POST.get('id_rolls')
                id_date = request.POST.get('id_date')
                id_time = request.POST.get('id_time')
                id_sku = request.POST.get('id_sku')

                grower_shipment = GrowerShipment.objects.get(id=pk)
                grower_shipment.process_amount = id_rolls
                grower_shipment.process_date = id_date
                grower_shipment.process_time = id_time
                grower_shipment.sku = id_sku
                grower_shipment.save()

                return redirect ('processor_outbound_list')
            return render(request, 'processor/processor_process_material.html',context)
    else:
        return redirect('login')


@login_required()
def processor_process_material_edit(request,pk):
    context = {}
    if request.user.is_processor:
        grower_shipment = GrowerShipment.objects.get(id=pk)
        context['grower_shipment'] = grower_shipment
        context['date_shipment'] = str(grower_shipment.process_date)
        context['time_shipment'] = str(grower_shipment.process_time)
        if request.method == 'POST':

            id_rolls = request.POST.get('id_rolls')
            id_date = request.POST.get('id_date')
            id_time = request.POST.get('id_time')
            id_sku = request.POST.get('id_sku')
            
            if id_rolls != None :
                grower_shipment.process_amount = id_rolls
                
            if id_date != None :
                grower_shipment.process_date = id_date
                
            if id_time != None :
                grower_shipment.process_time = id_time
                
            if id_sku != None :
                grower_shipment.sku = id_sku
            grower_shipment.save()

            return redirect ('processor_outbound_list')
        return render(request, 'processor/processor_process_material_edit.html',context)
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        grower_shipment = GrowerShipment.objects.get(id=pk)
        context['grower_shipment'] = grower_shipment
        context['date_shipment'] = str(grower_shipment.process_date)
        context['time_shipment'] = str(grower_shipment.process_time)
        if request.method == 'POST':

            id_rolls = request.POST.get('id_rolls')
            id_date = request.POST.get('id_date')
            id_time = request.POST.get('id_time')
            id_sku = request.POST.get('id_sku')
            
            if id_rolls != None :
                grower_shipment.process_amount = id_rolls
                
            if id_date != None :
                grower_shipment.process_date = id_date
                
            if id_time != None :
                grower_shipment.process_time = id_time
                
            if id_sku != None :
                grower_shipment.sku = id_sku
            grower_shipment.save()

            return redirect ('processor_outbound_list')
        return render(request, 'processor/processor_process_material_edit.html',context)


def processor_receive_delivery(request):
    if request.user.is_authenticated:
        context = {}
        status = ""
        # Processor 
        if request.user.is_processor:
            
            user_email = request.user.email

            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id

            grower = LinkGrowerToProcessor.objects.filter(processor_id=processor_id)
            grower_id = [i.grower_id for i in grower]
            get_grower = Grower.objects.filter(id__in = grower_id).order_by('name')

            context['get_grower'] = get_grower
            if request.method == 'POST':
                id_grower = request.POST.get('id_grower')
                if id_grower !='all':
                    selected_grower = Grower.objects.get(id=id_grower)
                    context['selected_grower'] = selected_grower

                    storage_obj = Storage.objects.filter(grower_id=id_grower)
                    context['storage'] = storage_obj

                    field_obj = Field.objects.filter(grower_id=id_grower)
                    context['field'] = field_obj

                    id_storage = request.POST.get('id_storage')
                    id_field = request.POST.get('id_field')
                    module_number = request.POST.get('module_number')


                    amount1 = request.POST.get('amount1')
                    amount2 = request.POST.get('amount2')

                    id_unit1 = request.POST.get('id_unit1')
                    id_unit2= request.POST.get('id_unit2')
                    
                    # code
                    shipment_id = generate_shipment_id()
                    get_output= request.POST.get('get_output')
                    
                    if len(amount1) > 0 and len(amount2) == 0:
                        if id_unit1 == '1':
                            id_unit1 = 'LBS'
                            id_unit2 = ''
                        if id_unit1 == '38000':
                            id_unit1 = 'MODULES (8 ROLLS)'
                            id_unit2 = ''
                        if id_unit1 == '19000':
                            id_unit1 = 'SETS (4 ROLLS)'
                            id_unit2 = ''
                        if id_unit1 == '4750':
                            id_unit1 = 'ROLLS'
                            id_unit2 = ''
                    
                    if len(amount1) > 0 and len(amount2) > 0:
                        if id_unit1 == '1':
                            id_unit1 = 'LBS'
                        if id_unit1 == '38000':
                            id_unit1 = 'MODULES (8 ROLLS)'
                        if id_unit1 == '19000':
                            id_unit1 = 'SETS (4 ROLLS)'
                        if id_unit1 == '4750':
                            id_unit1 = 'ROLLS'
                        if id_unit2 == '1':
                            id_unit2 = 'LBS'
                        if id_unit2 == '38000':
                            id_unit2 = 'MODULES (8 ROLLS)'
                        if id_unit2 == '19000':
                            id_unit2 = 'SETS (4 ROLLS)'
                        if id_unit2 == '4750':
                            id_unit2 = 'ROLLS'

                    if id_storage == None :
                        id_storage = None
                        
                    else:
                        id_storage = id_storage
                                            
                    if id_field and module_number:
                        field = Field.objects.get(id=id_field)
                        crop = field.crop
                        if crop == "RICE":
                            status = ""
                        if crop == "WHEAT":
                            status = ""
                        if crop == "COTTON":
                            status = "APPROVED"
                        # sustainabilitySurvey = SustainabilitySurvey.objects.filter(grower_id=selected_grower.id)
                        # if len(sustainabilitySurvey) == 0:
                        #     surveyscore = 0
                        # else:
                        #     surveyscore = [i.surveyscore for i in sustainabilitySurvey][0]
                        sustain_data = SustainabilitySurvey.objects.filter(grower_id=selected_grower.id,field_id=id_field)

                        if sustain_data.count() > 0:
                            Avg_Percentage_Score_data = sustain_data.aggregate(Avg('sustainabilityscore'))
                            surveyscore = int(Avg_Percentage_Score_data['sustainabilityscore__avg'])
                        else:
                            surveyscore = 0
                        shipment = GrowerShipment(status=status,total_amount=get_output,unit_type2=id_unit2,amount2=amount2,echelon_id=field.eschlon_id,sustainability_score=surveyscore,amount=amount1,variety=field.variety,crop=field.crop,shipment_id=shipment_id,processor_id=processor_id,grower_id=selected_grower.id,storage_id=id_storage,field_id=id_field,module_number=module_number,unit_type=id_unit1)
                        shipment.save()
                        
                        # 07-04-23 Log Table
                        log_type, log_status, log_device = "GrowerShipment", "Added", "Web"
                        log_idd, log_name = shipment.id, shipment.shipment_id
                        log_details = f"status = {status} | total_amount = {get_output} | unit_type2 = {id_unit2} | amount2 = {amount2} | echelon_id = {field.eschlon_id} | sustainability_score = {surveyscore} | amount = {amount1} | variety = {field.variety} | crop = {field.crop} | shipment_id = {shipment_id} | processor_id = {processor_id} | grower_id = {selected_grower.id} | storage_id = {id_storage} | field_id = {id_field} | module_number = {module_number} | unit_type = {id_unit1} | "
                        action_by_userid = request.user.id
                        user = User.objects.get(pk=action_by_userid)
                        user_role = user.role.all()
                        action_by_username = f'{user.first_name} {user.last_name}'
                        action_by_email = user.username
                        if request.user.id == 1 :
                            action_by_role = "superuser"
                        else:
                            action_by_role = str(','.join([str(i.role) for i in user_role]))
                        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                                            action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                            log_device=log_device)
                        logtable.save()

                        return redirect('processor_inbound_management')
                    
            return render(request, 'processor/processor_receive_delivery.html',context)
        # Superuser 
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            grower = LinkGrowerToProcessor.objects.all()
            grower_id = [i.grower_id for i in grower]
            get_grower = Grower.objects.filter(id__in = grower_id).order_by('name')
            context['get_grower'] = get_grower
            if request.method == 'POST':
                id_grower = request.POST.get('id_grower')
                if id_grower !='all':
                    selected_grower = Grower.objects.get(id=id_grower)
                    context['selected_grower'] = selected_grower

                    storage_obj = Storage.objects.filter(grower_id=id_grower)
                    context['storage'] = storage_obj

                    field_obj = Field.objects.filter(grower_id=id_grower)
                    context['field'] = field_obj

                    id_storage = request.POST.get('id_storage')
                    id_field = request.POST.get('id_field')
                    module_number = request.POST.get('module_number')


                    amount1 = request.POST.get('amount1')
                    amount2 = request.POST.get('amount2')
                    

                    id_unit1 = request.POST.get('id_unit1')
                    id_unit2= request.POST.get('id_unit2')

                    
                    get_output= request.POST.get('get_output')
                    shipment_id = generate_shipment_id()

                    if len(amount1) > 0 and len(amount2) == 0:
                        if id_unit1 == '1':
                            id_unit1 = 'LBS'
                            id_unit2 = ''
                        if id_unit1 == '38000':
                            id_unit1 = 'MODULES (8 ROLLS)'
                            id_unit2 = ''
                        if id_unit1 == '19000':
                            id_unit1 = 'SETS (4 ROLLS)'
                            id_unit2 = ''
                        if id_unit1 == '4750':
                            id_unit1 = 'ROLLS'
                            id_unit2 = ''
                    
                    if len(amount1) > 0 and len(amount2) > 0:
                        if id_unit1 == '1':
                            id_unit1 = 'LBS'
                        if id_unit1 == '38000':
                            id_unit1 = 'MODULES (8 ROLLS)'
                        if id_unit1 == '19000':
                            id_unit1 = 'SETS (4 ROLLS)'
                        if id_unit1 == '4750':
                            id_unit1 = 'ROLLS'
                        if id_unit2 == '1':
                            id_unit2 = 'LBS'
                        if id_unit2 == '38000':
                            id_unit2 = 'MODULES (8 ROLLS)'
                        if id_unit2 == '19000':
                            id_unit2 = 'SETS (4 ROLLS)'
                        if id_unit2 == '4750':
                            id_unit2 = 'ROLLS'
                    
                    if id_storage == None :
                        id_storage = None
                        
                    else:
                        id_storage = id_storage

                    processor_id = LinkGrowerToProcessor.objects.get(grower_id=selected_grower.id).processor_id
                    if id_field and module_number:
                        field = Field.objects.get(id=id_field)
                        crop = field.crop
                        if crop == "RICE":
                            status = ""
                        if crop == "WHEAT":
                            status = ""
                        if crop == "COTTON":
                            status = "APPROVED"

                        sustain_data = SustainabilitySurvey.objects.filter(grower_id=selected_grower.id,field_id=id_field)

                        if sustain_data.count() > 0:
                            Avg_Percentage_Score_data = sustain_data.aggregate(Avg('sustainabilityscore'))
                            surveyscore = int(Avg_Percentage_Score_data['sustainabilityscore__avg'])
                        else:
                            surveyscore = 0


                        shipment = GrowerShipment(status=status,total_amount=get_output,unit_type2=id_unit2,amount2=amount2,echelon_id=field.eschlon_id,sustainability_score=surveyscore,amount=amount1,variety=field.variety,crop=field.crop,shipment_id=shipment_id,processor_id=processor_id,grower_id=selected_grower.id,storage_id=id_storage,field_id=id_field,module_number=module_number,unit_type=id_unit1)
                        shipment.save()
                        # 07-04-23
                        log_type, log_status, log_device = "GrowerShipment", "Added", "Web"
                        log_idd, log_name = shipment.id, shipment.shipment_id
                        log_details = f"status = {status} | total_amount = {get_output} | unit_type2 = {id_unit2} | amount2 = {amount2} | echelon_id = {field.eschlon_id} | sustainability_score = {surveyscore} | amount = {amount1} | variety = {field.variety} | crop = {field.crop} | shipment_id = {shipment_id} | processor_id = {processor_id} | grower_id = {selected_grower.id} | storage_id = {id_storage} | field_id = {id_field} | module_number = {module_number} | unit_type = {id_unit1} | "
                        action_by_userid = request.user.id
                        user = User.objects.get(pk=action_by_userid)
                        user_role = user.role.all()
                        action_by_username = f'{user.first_name} {user.last_name}'
                        action_by_email = user.username
                        if request.user.id == 1 :
                            action_by_role = "superuser"
                        else:
                            action_by_role = str(','.join([str(i.role) for i in user_role]))
                        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                                            action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                            log_device=log_device)
                        logtable.save()

                        return redirect('processor_inbound_management')
            return render(request, 'processor/processor_receive_delivery.html',context)
    else:
        return redirect('login')


@login_required()
def classing_report_delete(request,pk):
    cr = ClassingReport.objects.get(id=pk)
    cr.delete()
    return HttpResponse(1)


def production_report_upload(request):
    if request.user.is_authenticated:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            grower = LinkGrowerToProcessor.objects.all()
            processor_id = [i.processor_id for i in grower]
            get_processor = Processor.objects.filter(id__in = processor_id)

            # processor = Processor.objects.all
            context['processor'] = get_processor
            if request.method == 'POST':
                processor_id = request.POST.get('processor_id')
                date = request.POST.get('date')
                csv_file = request.FILES.get('csv_file')
                mycsv = pd.read_csv(csv_file, skiprows=1)
                check = mycsv.columns[0]

                if str(check) == 'Load Report by Date':

                    if not date:
                        date = None
                    else:
                        date = date
                    productionlstid = ProductionReport(uploaded_date=date,processor_id=processor_id,csv_path=csv_file,executed='No')
                    productionlstid.save()
                    csv_path_read = productionlstid.csv_path.path
                    # below code for production csv import
                    df = pd.read_csv(csv_path_read, skiprows=3)
                    date = df.iloc[0, 0]
                    load_Id = df.iloc[1, 0]
                    GinReportbyday(
                        production_id = productionlstid.id,
                        date=date,
                        load_id=df.iloc[1, 0],
                        prod_id=df.iloc[1, 1],
                        farm_id=df.iloc[1, 2],
                        field_name=df.iloc[1, 3],
                        pk_num=df.iloc[1, 4],
                        variety=df.iloc[1, 5],
                        tm=df.iloc[1, 6],
                        module_amount=df.iloc[1, 7],
                        truck_id=df.iloc[1, 8],
                        made_date=df.iloc[1, 9],
                        delivery_date=df.iloc[1, 10],
                        gin_date=df.iloc[1, 11],
                        bc=df.iloc[1, 12],
                        cotton_seed=df.iloc[1, 13],
                        lint=df.iloc[1, 14],
                        seed=df.iloc[1, 15],
                        turnout=df.iloc[1, 16],
                    ).save()
                    df2 = df.iloc[4:-2]
                    drop_null_row = df2[df2['Load#'].isnull()].index
                    df2.drop(drop_null_row, inplace=True)
                    drop_bale_row = df2[df2['Load#'] == 'Bale#'].index
                    df2.drop(drop_bale_row, inplace=True)
                    df3 = df2.reset_index(drop=True)
                    char = df3[df3['Load#'].str.contains('Bales')].index
                    length_row = df3.shape[0]
                    if len(char) == 0:
                        first_loop = length_row
                    else:
                        first_loop = char[0]
                    # first bale netwt
                    champ = 0
                    gin_obj_lst = []
                    for i in range(length_row):
                        if i < first_loop:
                            # Validation 
                            bale_count = GinLoadBalebydate.objects.filter(bale_id=df3.iloc[i, 0]).count()
                            if bale_count > 0:
                                messages.error(request,'Duplicate Bale ID Found')
                                productionlstid.delete()
                                return render(request, 'processor/production_report_upload.html',context)
                                                                    
                            else:
                                GinLoadBalebydate(
                                    gin_date=date,
                                    load_id=load_Id,
                                    bale_id=df3.iloc[i, 0],
                                    net_wt=df3.iloc[i, 1]
                                ).save()
                        if len(char) == 0:
                            indexTemp = length_row
                        else:
                            indexTemp = char[champ]
                        target_row = int(indexTemp)+1
                        if i == target_row:
                            if champ < len(char):
                                load_new_id = df3.iloc[i, 0]
                                GinReportbyday(
                                    production_id = productionlstid.id,
                                    date=date,
                                    load_id=load_new_id,
                                    prod_id=df3.iloc[i, 1],
                                    farm_id=df3.iloc[i, 2],
                                    field_name=df3.iloc[i, 3],
                                    pk_num=df3.iloc[i, 4],
                                    variety=df3.iloc[i, 5],
                                    tm=df3.iloc[i, 6],
                                    module_amount=df3.iloc[i, 7],
                                    truck_id=df3.iloc[i, 8],
                                    made_date=df3.iloc[i, 9],
                                    delivery_date=df3.iloc[i, 10],
                                    gin_date=df3.iloc[i, 11],
                                    bc=df3.iloc[i, 12],
                                    cotton_seed=df3.iloc[i, 13],
                                    lint=df3.iloc[i, 14],
                                    seed=df3.iloc[i, 15],
                                    turnout=df3.iloc[i, 16],
                                ).save()
                                # print(df3.iloc[i, 0], df3.iloc[i, 1])

                                if champ == len(char) - 1:
                                    champ = champ
                                else:
                                    champ += 1
                                    for j in range(target_row + 1, char[champ]):
                                        bale_count = GinLoadBalebydate.objects.filter(bale_id=df3.iloc[j, 0]).count()
                                        if bale_count > 0:
                                            messages.error(request,'Duplicate Bale ID Found')
                                            # if len(gin_obj_lst) !=0:
                                            #     for i in gin_obj_lst:
                                            #         GinLoadBalebydate.objects.get(id = i).delete()
                                            gin = GinReportbyday.objects.filter(production_id = productionlstid.id)
                                            load_id = [i.load_id for i in gin]
                                            gg = GinLoadBalebydate.objects.filter(load_id__in = load_id)
                                            for i in gg:
                                                gg_id = i.id
                                                GinLoadBalebydate.objects.get(id = gg_id).delete()

                                                
                                            productionlstid.delete()
                                            return render(request, 'processor/production_report_upload.html',context)
                                        else:
                                            GinLoadBalebydate(
                                                gin_date=date,
                                                load_id=load_new_id,
                                                bale_id=df3.iloc[j, 0],
                                                net_wt=df3.iloc[j, 1]
                                            ).save()
                                            # gin_obj
                                            # gin_obj_lst.append(gin_obj.id)
                                        # print(df3.iloc[j, 0], df3.iloc[j, 1])
                            else:
                                break
                    return redirect ('production_report_list')
                else:
                    messages.error(request,"Please Upload A Valid Production Datewise CSV, (Ref : Load Report by Date) ")
                    return render(request, 'processor/production_report_upload.html',context)
            return render(request, 'processor/production_report_upload.html',context)
        elif request.user.is_processor:
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id
            if request.method == 'POST':
                date = request.POST.get('date')
                csv_file = request.FILES.get('csv_file')
                mycsv = pd.read_csv(csv_file, skiprows=1)
                check = mycsv.columns[0]

                if str(check) == 'Load Report by Date':
                    if not date:
                        date = None
                    else:
                        date = date
                
                    productionlstid = ProductionReport(uploaded_date=date,processor_id=processor_id,csv_path=csv_file,executed='No')
                    productionlstid.save()
                    csv_path_read = productionlstid.csv_path.path
                    # below code for production csv import
                    df = pd.read_csv(csv_path_read, skiprows=3)
                    date = df.iloc[0, 0]
                    load_Id = df.iloc[1, 0]
                    GinReportbyday(
                        production_id = productionlstid.id,
                        date=date,
                        load_id=df.iloc[1, 0],
                        prod_id=df.iloc[1, 1],
                        farm_id=df.iloc[1, 2],
                        field_name=df.iloc[1, 3],
                        pk_num=df.iloc[1, 4],
                        variety=df.iloc[1, 5],
                        tm=df.iloc[1, 6],
                        module_amount=df.iloc[1, 7],
                        truck_id=df.iloc[1, 8],
                        made_date=df.iloc[1, 9],
                        delivery_date=df.iloc[1, 10],
                        gin_date=df.iloc[1, 11],
                        bc=df.iloc[1, 12],
                        cotton_seed=df.iloc[1, 13],
                        lint=df.iloc[1, 14],
                        seed=df.iloc[1, 15],
                        turnout=df.iloc[1, 16],
                    ).save()
                    df2 = df.iloc[4:-2]
                    drop_null_row = df2[df2['Load#'].isnull()].index
                    df2.drop(drop_null_row, inplace=True)
                    drop_bale_row = df2[df2['Load#'] == 'Bale#'].index
                    df2.drop(drop_bale_row, inplace=True)
                    df3 = df2.reset_index(drop=True)
                    char = df3[df3['Load#'].str.contains('Bales')].index
                    length_row = df3.shape[0]
                    if len(char) == 0:
                        first_loop = length_row
                    else:
                        first_loop = char[0]
                    # first bale netwt
                    champ = 0
                    gin_obj_lst = []
                    for i in range(length_row):
                        indexTemp = char[champ]
                        target_row = int(indexTemp)+1
                        if i < first_loop:
                            bale_count = GinLoadBalebydate.objects.filter(bale_id=df3.iloc[i, 0]).count()
                            if bale_count > 0:
                                messages.error(request,'Duplicate Bale ID Found')
                                productionlstid.delete()
                                return render(request, 'processor/production_report_upload.html',context)
                            else:
                                GinLoadBalebydate(
                                    gin_date=date,
                                    load_id=load_Id,
                                    bale_id=df3.iloc[i, 0],
                                    net_wt=df3.iloc[i, 1]
                                ).save()
                                
                        if len(char) == 0:
                            indexTemp = length_row
                        else:
                            indexTemp = char[champ]
                        target_row = int(indexTemp)+1

                        if i == target_row:
                            if champ < len(char):
                                load_new_id = df3.iloc[i, 0]
                                GinReportbyday(
                                    production_id = productionlstid.id,
                                    date=date,
                                    load_id=load_new_id,
                                    prod_id=df3.iloc[i, 1],
                                    farm_id=df3.iloc[i, 2],
                                    field_name=df3.iloc[i, 3],
                                    pk_num=df3.iloc[i, 4],
                                    variety=df3.iloc[i, 5],
                                    tm=df3.iloc[i, 6],
                                    module_amount=df3.iloc[i, 7],
                                    truck_id=df3.iloc[i, 8],
                                    made_date=df3.iloc[i, 9],
                                    delivery_date=df3.iloc[i, 10],
                                    gin_date=df3.iloc[i, 11],
                                    bc=df3.iloc[i, 12],
                                    cotton_seed=df3.iloc[i, 13],
                                    lint=df3.iloc[i, 14],
                                    seed=df3.iloc[i, 15],
                                    turnout=df3.iloc[i, 16],
                                ).save()

                                if champ == len(char) - 1:
                                    champ = champ
                                else:
                                    champ += 1
                                    for j in range(target_row + 1, char[champ]):
                                        bale_count = GinLoadBalebydate.objects.filter(bale_id=df3.iloc[j, 0]).count()
                                        if bale_count > 0:
                                            messages.error(request,'Duplicate Bale ID Found')
                                            gin = GinReportbyday.objects.filter(production_id = productionlstid.id)
                                            load_id = [i.load_id for i in gin]
                                            gg = GinLoadBalebydate.objects.filter(load_id__in = load_id)
                                            for i in gg:
                                                gg_id = i.id
                                                GinLoadBalebydate.objects.get(id = gg_id).delete()

                                                
                                            productionlstid.delete()
                                            return render(request, 'processor/production_report_upload.html',context)
                                            
                                        else:
                                            gin_obj = GinLoadBalebydate(
                                                gin_date=date,
                                                load_id=load_new_id,
                                                bale_id=df3.iloc[j, 0],
                                                net_wt=df3.iloc[j, 1]
                                            ).save()
                                            
                            else:
                                break
                    return redirect ('production_report_list')
                else:
                    messages.error(request,"Please Upload A Valid Production Datewise CSV, (Ref : Load Report by Date) ")
                    return render(request, 'processor/production_report_upload.html',context)
            return render(request, 'processor/production_report_upload.html',context)
    else:
        return redirect('login')

def production_report_list(request):
    if request.user.is_authenticated:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            pr = ProductionReport.objects.all().order_by('uploaded_date')
            context['pr'] = pr
            return render(request, 'processor/production_report_list.html',context)
        elif request.user.is_processor:
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id
            pr = ProductionReport.objects.filter(processor_id=processor_id).order_by('uploaded_date')
            context['pr'] = pr
            return render(request, 'processor/production_report_list.html',context)
    else:
        return redirect('login')

@login_required()
def production_report_delete(request,pk):
    cr = ProductionReport.objects.get(id=pk)
    production_id = cr.id
    gin = GinReportbyday.objects.filter(production_id = production_id)
    load_id = [i.load_id for i in gin]
    gg = GinLoadBalebydate.objects.filter(load_id__in = load_id)
    for i in gg:
        gg_id = i.id
        GinLoadBalebydate.objects.get(id = gg_id).delete()
    cr.delete()
    return HttpResponse(1)

@login_required()
def classing_report_farmfield_delete(request,pk):
    cr = ClassingReport.objects.get(id=pk)
    cr.delete()
    return HttpResponse(1)

def classing_ewr_report_list(request):
    if request.user.is_authenticated:
        context = {}
        # Superuser 
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            report = BaleReportFarmField.objects.filter(id__isnull = False)
            processor = Processor.objects.all().order_by('entity_name')
            context['processor'] = processor
            levels = request.GET.get("levels")
            get_processor = request.GET.get("get_processor")

            if levels == None and get_processor == None :
                report = report
            else :
                if get_processor :
                    if get_processor != 'all' :
                        cr = ClassingReport.objects.filter(processor__id=int(get_processor))
                        cr_id = [i.id for i in cr]
                        report = report.filter(classing_id__in = cr_id)
                        selectedprocessor = Processor.objects.get(id=get_processor)
                        context['selectedprocessor'] = selectedprocessor
                    else:
                        report = report
                if levels :
                    if levels != 'all' :
                        report = report.filter(level = levels)
                        context['selected_level'] = levels
                    else:
                        report = report

            paginator = Paginator(report, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)
            
            context['report'] = report
            return render(request, 'processor/classing_ewr_report_list.html',context)
        # Processor 
        if request.user.is_processor:
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id
            cr = ClassingReport.objects.filter(processor_id=processor_id)
            rp = [i.id for i in cr]
            report = BaleReportFarmField.objects.filter(classing_id__in=rp)
            levels = request.GET.get("levels")

            if levels :
                if levels != 'all' :
                    report = report.filter(level = levels)
                    context['selected_level'] = levels
                else:
                    report = report

            paginator = Paginator(report, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)
            context['report'] = report
            return render(request, 'processor/classing_ewr_report_list.html',context)
    else:
        return redirect('login')


def classing_ewr_selectedlevel_selectedprocessor_downlaod(request,selectedprocessor,selected_level):
    if request.user.is_authenticated:
        context = {}
        # Superuser 
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            cr = ClassingReport.objects.filter(processor__id=selectedprocessor)
            cr_id = [i.id for i in cr]
            bale_r = BaleReportFarmField.objects.filter(classing_id__in = cr_id)
            report = bale_r.filter(level=selected_level)           
            report_name = Processor.objects.get(id=selectedprocessor)
            response = HttpResponse(content_type='text/plain')  
            current_date = date.today().strftime("%m-%d-%Y")
            response['Content-Disposition'] = 'attachment; filename="{}_{}_{}.txt"'.format(report_name,selected_level,current_date)

            for i in report:
                response.write("{}{}{}\n".format(i.warehouse_wh_id,i.bale_id,2022))

            return response
    else:
        return redirect('login')


def classing_ewr_selectedprocessor_downlaod(request,selectedprocessor):
    if request.user.is_authenticated:
        context = {}
        # Superuser 
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            cr = ClassingReport.objects.filter(processor__id=selectedprocessor)
            cr_id = [i.id for i in cr]
            report = BaleReportFarmField.objects.filter(classing_id__in = cr_id)
            report_name = Processor.objects.get(id=selectedprocessor)
            response = HttpResponse(content_type='text/plain')  
            current_date = date.today().strftime("%m-%d-%Y")
            response['Content-Disposition'] = 'attachment; filename="{}_{}.txt"'.format(report_name,current_date)

            for i in report:
                response.write("{}{}{}\n".format(i.warehouse_wh_id,i.bale_id,2022))

            return response
    else:
        return redirect('login')

def classing_ewr_selected_level_downlaod(request,selected_level):
    if request.user.is_authenticated:
        context = {}
        # Superuser 
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            check_report = BaleReportFarmField.objects.filter(level=selected_level)
            response = HttpResponse(content_type='text/plain')  
            current_date = date.today().strftime("%m-%d-%Y")
            response['Content-Disposition'] = 'attachment; filename="{}_{}.txt"'.format(selected_level,current_date)

            for i in check_report:
                response.write("{}{}{}\n".format(i.warehouse_wh_id,i.bale_id,2022))

            return response
        # Processor 
        if request.user.is_processor:
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id
            cr = ClassingReport.objects.filter(processor_id=processor_id)
            rp = [i.id for i in cr]
            report = BaleReportFarmField.objects.filter(classing_id__in=rp)
            check_report = report.filter(level=selected_level)
            response = HttpResponse(content_type='text/plain')  
            current_date = date.today().strftime("%m-%d-%Y")
            response['Content-Disposition'] = 'attachment; filename="{}_{}.txt"'.format(selected_level,current_date)

            for i in check_report:
                response.write("{}{}{}\n".format(i.warehouse_wh_id,i.bale_id,2022))

            return response
    else:
        return redirect('login')

def classing_ewr_report_all_downlaod(request):
    if request.user.is_authenticated:
        context = {}
        # Superuser 
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            report = BaleReportFarmField.objects.all()          
            response = HttpResponse(content_type='text/plain')  
            current_date = date.today().strftime("%m-%d-%Y")
            response['Content-Disposition'] = 'attachment; filename="All_{}.txt"'.format(current_date)

            for i in report:
                response.write("{}{}{}\n".format(i.warehouse_wh_id,i.bale_id,2022))

            return response
        # Processor 
        if request.user.is_processor:
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id
            cr = ClassingReport.objects.filter(processor_id=processor_id)
            rp = [i.id for i in cr]
            report = BaleReportFarmField.objects.filter(classing_id__in=rp)

            response = HttpResponse(content_type='text/plain')  
            current_date = date.today().strftime("%m-%d-%Y")
            response['Content-Disposition'] = 'attachment; filename="All_{}.txt"'.format(current_date)

            for i in report:
                response.write("{}{}{}\n".format(i.warehouse_wh_id,i.bale_id,2022))

            return response
    else:
        return redirect('login')

def production_report_csv_list(request):
    if request.user.is_authenticated:
        context = {}
        # Superuser 
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            report = GinReportbyday.objects.all()
            context['report'] = report
            return render(request, 'processor/production_report_csv_list.html',context)
        # Processor 
        if request.user.is_processor:
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor_id).id
            pp = ProductionReport.objects.filter(processor_id=processor_id)
            var = [i.id for i in pp]
            report = GinReportbyday.objects.filter(production_id__in = var)
            context['report'] = report
            return render(request, 'processor/production_report_csv_list.html',context)
    else:
        return redirect('login')

# def bale_report_list(request):
#     if request.user.is_authenticated:
#         context = {}
#         # Superuser 
#         if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
#             report = GinLoadBalebydate.objects.all()
#             context['report'] = report
#             return render(request, 'processor/bale_report_list.html',context)
#         # Processor 
#         if request.user.is_processor:
#             user_email = request.user.email
#             p = ProcessorUser.objects.get(contact_email=user_email)
#             processor_id = Processor.objects.get(id=p.processor_id).id
#             pp = ProductionReport.objects.filter(processor_id=processor_id)
#             var = [i.id for i in pp]
#             ginr = GinReportbyday.objects.filter(production_id__in = var)
#             ginr_loadid = [i.load_id for i in ginr]
#             report = GinLoadBalebydate.objects.filter(load_id__in = ginr_loadid)
#             context['report'] = report
#             return render(request, 'processor/bale_report_list.html',context)
#     else:
#         return redirect('login')


@login_required()
def bale_report_list(request):  #===========================|pagination + 4 search fields + autocomplete |===============================
    context = {}
    # Superuser 
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        report = GinLoadBalebydate.objects.all()
        context['report'] = report
            
        gin_date = request.GET.get('gin_date')
        load_id = request.GET.get('load_id')
        bale_id = request.GET.get('bale_id')
        net_wt = request.GET.get('net_wt')

        get_load_id = list(set([f"{i.load_id}" for i in report]))
        get_bale_id = list(set([f"{i.bale_id}" for i in report]))
        get_net_wt = list(set([f"{i.net_wt}" for i in report]))

        context['load_id_json'] = json.dumps(get_load_id)
        context['bale_id_json'] = json.dumps(get_bale_id)
        context['net_wt_json'] = json.dumps(get_net_wt)

        if gin_date:
            context['gin_date'] = str(gin_date)
            # new_gin_var = str(gin_date).split('-')
            # get_gin_var = f"{new_gin_var[1]}/{new_gin_var[2]}/{new_gin_var[0]}"
            report = report.filter(gin_date__icontains=str(gin_date))
                
        if load_id:
            context['load_id'] = load_id
            report = report.filter(load_id__icontains=load_id)
            
        if bale_id:
            context['bale_id'] = bale_id
            report = report.filter(bale_id__icontains=bale_id)
            
        if net_wt:
            context['net_wt'] = net_wt
            report = report.filter(net_wt__icontains=net_wt)
            
        paginator = Paginator(report,100)
        page_num = request.GET.get('page',1)
        page_obj = paginator.get_page(page_num)

        try:
            page_obj = paginator.page(page_num)      
        except PageNotAnInteger:
            # if page is not an integer, deliver the first page
            page_obj = paginator.page(1)
        except EmptyPage:
            # if the page is out of range, deliver the last page
            page_obj = paginator.page(paginator.num_pages)
    
        report_list = page_obj
        context['report'] = report_list
        return render(request, 'processor/bale_report_list.html',context)
    # Processor 
    elif request.user.is_processor:
        user_email = request.user.email
        p = ProcessorUser.objects.get(contact_email=user_email)
        processor_id = Processor.objects.get(id=p.processor_id).id
        pp = ProductionReport.objects.filter(processor_id=processor_id)
        var = [i.id for i in pp]
        ginr = GinReportbyday.objects.filter(production_id__in = var)
        ginr_loadid = [i.load_id for i in ginr]
        report = GinLoadBalebydate.objects.filter(load_id__in = ginr_loadid)
        context['report'] = report
        
        gin_date = request.GET.get('gin_date')
        load_id = request.GET.get('load_id')
        bale_id = request.GET.get('bale_id')
        net_wt = request.GET.get('net_wt')
        
        # get_gin_date = [f"{i.gin_date}" for i in report]
        get_load_id = list(set([f"{i.load_id}" for i in report]))
        get_bale_id = list(set([f"{i.bale_id}" for i in report]))
        get_net_wt = list(set([f"{i.net_wt}" for i in report]))
                
        context['load_id_json'] =  json.dumps(get_load_id)
        context['bale_id_json'] =  json.dumps(get_bale_id)
        context['net_wt_json'] =  json.dumps(get_net_wt)

        if gin_date:
            context['gin_date']=str(gin_date)
            # new_gin_var=str(gin_date).split('-')
            # get_gin_var=f"{new_gin_var[1]}/{new_gin_var[2]}/{new_gin_var[0]}"
            report=report.filter(gin_date__icontains=str(gin_date))
        if load_id:
            context['load_id']=load_id
            report=report.filter(load_id__icontains=load_id)
            
        if bale_id:
            context['bale_id']=bale_id
            report=report.filter(bale_id__icontains=bale_id)

        if net_wt:
            context['net_wt']=net_wt
            report=report.filter(net_wt__icontains=net_wt)

        paginator=Paginator(report,100)
        page_num=request.GET.get('page',1)
        page_obj=paginator.get_page(page_num)

        try:
            page_obj=paginator.page(page_num)
        except PageNotAnInteger:
            page_obj=paginator.page(1)  
        except EmptyPage:
            page_obj=paginator.page(paginator.num_pages) 

        report_list=page_obj
        context['report']=report_list
        return render(request, 'processor/bale_report_list.html',context)
    else:
        return redirect('dashboard')
    
@login_required()
def processor_change_password(request,pk):
    context={}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        pp = ProcessorUser.objects.get(id=pk)
        userr = User.objects.get(email=pp.contact_email)
        context["userr"] = userr
        if request.method == "POST":
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            if len(password1) != 0 and len(password2) != 0 and password1 != None and password2 != None and password1 == password2:
                # update_pass_user = User.objects.get(id=pk)
                password = make_password(password1)
                userr.password = password
                userr.password_raw = password1
                userr.save()
                pp.p_password_raw = password1
                pp.save()
                # 10-04-23 Log Table
                log_type, log_status, log_device = "ProcessorUser", "Password changed", "Web"
                log_idd, log_name = pp.id, pp.contact_name
                log_email = pp.contact_email
                log_details = f"processor_id = {pp.processor.id} | processor = {pp.processor.entity_name} | contact_name= {pp.contact_name} | contact_email = {pp.contact_email} | contact_phone = {pp.contact_phone} | contact_fax = {pp.contact_fax}"
                action_by_userid = request.user.id
                user = User.objects.get(pk=action_by_userid)
                user_role = user.role.all()
                action_by_username = f'{user.first_name} {user.last_name}'
                action_by_email = user.username
                if request.user.id == 1 :
                    action_by_role = "superuser"
                else:
                    action_by_role = str(','.join([str(i.role) for i in user_role]))
                logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                    action_by_userid=action_by_userid,action_by_username=action_by_username,
                                    action_by_email=action_by_email,action_by_role=action_by_role,log_email=log_email,
                                    log_details=log_details, log_device=log_device)
                logtable.save()
                messages.success(request,"Password changed successfully!")
        return render (request, 'processor/processor_change_password.html', context)
    else:
        return redirect('dashboard')

@login_required()
def classing_upload(request):
    context={}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        grower = LinkGrowerToProcessor.objects.all()
        processor_id = [i.processor_id for i in grower]
        grower_id = [i.grower_id for i in grower]
        get_processor = Processor.objects.filter(id__in = processor_id).order_by('entity_name')
        get_grower = Grower.objects.filter(id__in = grower_id).order_by('name')
        context['get_processor'] = get_processor
        if request.method == 'POST':
            processor_id = request.POST.get('processor_id')
            p = Processor.objects.get(id=processor_id)
            context['p'] = p
            var = LinkGrowerToProcessor.objects.filter(processor_id = p.id)
            grower_id = [i.grower_id for i in var]
            get_grower = Grower.objects.filter(id__in = grower_id).order_by('name')
            context['get_grower'] = get_grower
            if request.POST.get('grower_id') != None :
                grower_id = request.POST.get('grower_id')
                id_field = request.POST.get('id_field')
                csv_file = request.FILES.get('csv_file')

                field = Field.objects.filter(grower_id = grower_id)
                context['field'] = field

                selectedgrower = Grower.objects.get(id=grower_id)
                context['selectedgrower'] = selectedgrower

                if csv_file == None:
                    pass
                else:
                    grower_id = grower_id
                    grower_name = selectedgrower.name
                    if id_field :
                        field_id = id_field
                        fff = Field.objects.get(id=field_id)
                        field_name = fff.name
                        crop_variety = fff.variety
                    else:
                        field_name = None
                        crop_variety = None
                        field_id = None
                    mycsv = pd.read_csv(csv_file, skiprows=1)
                    check = mycsv.columns[0]
                    if str(check) == "Bale Report by Producer":
                        classing = ClassingReport(upload_date=date.today(),processor_id=p.id,grower_id=grower_id,csv_path=csv_file,executed='No',csv_type='Bale Report by Producer')
                        classing.save()
                        csv_path_read = classing.csv_path.path
                        # below code for insert csv data in database
                        df = pd.read_csv(csv_path_read, skiprows=3)
                        prod_Id = df.iloc[0, 0]
                        farm_name = df.iloc[0, 1]
                        df['Farm_name'] = farm_name
                        df['Prod_id'] = prod_Id
                        df2 = df.iloc[1:]
                        drop_row = df2[df2['Lf'].isnull()].index
                        df2.drop(drop_row, inplace=True)
                        length_row = df2.shape[0]
                        
                        for i in range(length_row):
                            try:
                                bale_id= int(df2.iloc[i, 1])
                            except:
                                bale_id= df2.iloc[i, 1]
                            
                            bale_count = BaleReportFarmField.objects.filter(bale_id=bale_id).count()
                            if bale_count > 0 :
                                pass
                            elif df2.iloc[i, 1] == 'Gin Data(x3)' or df2.iloc[i, 1] == 'Bale #' :
                                pass
                            else:
                                crg_raw = df2.iloc[i, 14]
                                if crg_raw == '31-Jan':
                                    cgr = '31-1'
                                elif crg_raw == '21-Jan':
                                    cgr = '21-1'
                                elif crg_raw == '21-Feb':
                                    cgr = '21-2'
                                elif crg_raw == '21-Mar':
                                    cgr = '21-3'
                                elif crg_raw == '21-Apr':
                                    cgr = '21-4'
                                elif crg_raw == '31-Mar':
                                    cgr = '31-3'
                                elif crg_raw == '1-Nov':
                                    cgr = '11-1'
                                elif crg_raw == '2-Nov':
                                    cgr = '11-2'
                                elif crg_raw == '3-Nov':
                                    cgr = '11-3'
                                elif crg_raw == '4-Nov':
                                    cgr = '11-4'
                                else:
                                    cgr = crg_raw
                                
                                # Color — CGR
                                check_lst = []
                                clr = f"{cgr}"
                                if clr != 'nan':
                                    # clr = int(float(clr[:2]))
                                    clr_var = clr.split('-')
                                    clr1 = int(float(clr_var[0]))
                                    #if clr1 >= 11 and clr1 <= 21 :
                                    if clr1 == 11 or clr1 == 21 :
                                        check_lst.append('gold')
                                    elif clr1 == 31 :
                                        check_lst.append('silver')
                                    elif clr1 == 41 :
                                        check_lst.append('bronze')
                                    else:
                                        check_lst.append('0')
                                else:
                                    clr = 'nan'
                                # Leaf — LF
                                llf = f"{df2.iloc[i, 8]}"
                                if llf != 'nan':
                                    llf = int(llf[0])
                                    if llf <= 2 :
                                        check_lst.append('gold')
                                    elif llf <= 3 and llf > 2 :
                                        check_lst.append('silver')
                                    elif llf <= 4 and llf > 3 :
                                        check_lst.append('bronze')
                                    else:
                                        check_lst.append('0')
                                else:
                                    llf = 'nan'
                                # Staple — MIC
                                stap = f"{df2.iloc[i, 9]}"
                                if stap != 'nan':
                                    stap = float(stap)
                                    if stap >= 43 :
                                        check_lst.append('Llano Super')
                                    elif stap >= 38 and stap < 43 :
                                        check_lst.append('gold')
                                    elif stap >= 37 and stap < 38 :
                                        check_lst.append('silver')
                                    elif stap >= 36 and stap < 37 :
                                        check_lst.append('bronze')
                                    else:
                                        check_lst.append('0')
                                else:
                                    stap = 'nan'
                                # Strength — STR
                                streng = f"{df2.iloc[i, 13]}"
                                if streng != 'nan':
                                    streng = float(streng)
                                    if streng >= 33 :
                                        check_lst.append('gold')
                                    elif streng >= 31 and streng < 33 :
                                        check_lst.append('silver')
                                    elif streng >= 29 and streng < 31 :
                                        check_lst.append('bronze')
                                    else:
                                        check_lst.append('0')
                                else:
                                    streng = 'nan'
                                # Mic — TR
                                trmic = f"{df2.iloc[i, 10]}"
                                if trmic !='nan':
                                    trmic = float(trmic)
                                    if trmic >= 3.7 and trmic <4.3 :
                                        check_lst.append('gold')
                                    else:
                                        check_lst.append('0')
                                else:
                                    trmic = 'nan'
                                # Uniformity  — UNIF
                                uniformi = f"{df2.iloc[i, 18]}"
                                if uniformi != 'nan':
                                    uniformi = float(uniformi)
                                    if uniformi >= 82 :
                                        check_lst.append('gold')
                                    elif uniformi >= 81 and uniformi < 82 :
                                        check_lst.append('silver')
                                    elif uniformi >= 80 and uniformi < 81 :
                                        check_lst.append('bronze')
                                    else:
                                        check_lst.append('0')
                                else:
                                    uniformi = 'nan'
                                lls = check_lst.count('Llano Super')
                                gg = check_lst.count('gold')
                                ss = check_lst.count('silver')
                                bb = check_lst.count('bronze')
                                zz = check_lst.count('0')

                                if df2.iloc[i, 11] and df2.iloc[i, 11] != '  ' :
                                    var_ex = str(df2.iloc[i, 11])
                                else:
                                    var_ex = df2.iloc[i, 11]

                                if df2.iloc[i, 12] and df2.iloc[i, 12] != '  ' :
                                    var_rm = str(df2.iloc[i, 12])
                                else:
                                    var_rm = df2.iloc[i, 12]

                                if var_rm != 'nan'  and df2.iloc[i, 12] != '  ' and  df2.iloc[i, 12] != None :
                                    level="None"
                                elif var_ex != 'nan'  and df2.iloc[i, 11] != '  ' and  df2.iloc[i, 11] != None :
                                    level="None"
                                else:
                                    if gg >= 3 and lls == 1 :
                                        level="Llano Super"
                                    elif gg >= 4 :
                                        level="Gold"
                                    elif lls+gg+ss >= 4:
                                        level="Silver"
                                    elif lls+gg+ss+bb >= 4:
                                        level="Bronze"
                                    else:
                                        level="None"
                                
                                balereport_save = BaleReportFarmField(
                                    classing_id = classing.id,
                                    bale_id=df2.iloc[i, 1],
                                    net_wt=df2.iloc[i, 2],
                                    farm_id=df2.iloc[i, 3],
                                    load_id=df2.iloc[i, 4],
                                    # field_name=df2.iloc[i, 5],
                                    field_name = field_name,
                                    pk_num=df2.iloc[i, 6],
                                    gr=df2.iloc[i, 7],
                                    lf=df2.iloc[i, 8],
                                    st=df2.iloc[i, 9],
                                    mic=df2.iloc[i, 10],
                                    ex=df2.iloc[i, 11],
                                    rm=df2.iloc[i, 12],
                                    str_no=df2.iloc[i, 13],
                                    cgr=cgr,
                                    rd=df2.iloc[i, 15],
                                    ob1=df2.iloc[i, 16],
                                    tr=df2.iloc[i, 17],
                                    unif=df2.iloc[i, 18],
                                    len_num=df2.iloc[i, 19],
                                    elong=df2.iloc[i, 20],
                                    value=df2.iloc[i, 21],
                                    farm_name=df2.iloc[i, 22],
                                    prod_id=df2.iloc[i, 23],
                                    level=level, 
                                    ob2 = grower_id,
                                    ob3 = grower_name,
                                    ob4 = field_id,
                                    crop_variety = crop_variety,
                                    upload_date=date.today()
                                )
                                balereport_save.save()
                                balereport_save_certificate = balereport_save.certificate()
                                balereport_save.ob5 = balereport_save_certificate
                                balereport_save.save()
                        # 07-04-23
                        log_type, log_status, log_device = "ClassingReport", "Added", "Web"
                        log_idd, log_name = classing.id, str(classing.csv_path).replace("processor_reports/","")
                        log_details = "Bale Report by Producer"
                        action_by_userid = request.user.id
                        user = User.objects.get(pk=action_by_userid)
                        user_role = user.role.all()
                        action_by_username = f'{user.first_name} {user.last_name}'
                        action_by_email = user.username
                        if request.user.id == 1 :
                            action_by_role = "superuser"
                        else:
                            action_by_role = str(','.join([str(i.role) for i in user_role]))
                        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                                            action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                            log_device=log_device)
                        logtable.save()

                        return redirect ('classing_list')
                    
                    if str(check) == "Bale Report by Farm/Field":
                        classing = ClassingReport(upload_date=date.today(),processor_id=p.id,grower_id=grower_id,csv_path=csv_file,executed='No',csv_type='Bale Report by Farm/Field')
                        classing.save()
                        csv_path_read = classing.csv_path.path
                        df=pd.read_csv(csv_path_read,skiprows=3)
                        prod_Id = df.iloc[0, 1]
                        farm_name = df.iloc[0, 2]
                        df2 = df.iloc[1:]
                        # drop_row = df2[df2['Bale #'] == farm_name].index
                        # drop_null_row = df2[df2['Bale #'].isnull()].index
                        drop_row_again = df2[df2['Lf'].isnull()].index

                        # df2.drop(drop_row, inplace=True)
                        # df2.drop(drop_null_row, inplace=True)
                        df2.drop(drop_row_again, inplace=True)
                        
                        df3 = df2.reset_index(drop=True)
                        length_row = df3.shape[0]
                        
                        for i in range(length_row):
                            try:
                                bale_id=int(df3.iloc[i, 2])
                            except:
                                bale_id=df3.iloc[i, 2]
                            bale_count = BaleReportFarmField.objects.filter(bale_id=bale_id).count()
                            
                            if bale_count > 0 :
                                pass
                            elif df3.iloc[i, 2] == 'Gin Data(x3)' or df3.iloc[i, 2] == 'Bale #' :
                                pass
                            else:
                                check_lst = []
                                crg_raw = df3.iloc[i, 14]
                                if crg_raw == '31-Jan':
                                    cgr = '31-1'
                                elif crg_raw == '21-Jan':
                                    cgr = '21-1'
                                elif crg_raw == '21-Feb':
                                    cgr = '21-2'
                                elif crg_raw == '21-Mar':
                                    cgr = '21-3'
                                elif crg_raw == '21-Apr':
                                    cgr = '21-4'
                                elif crg_raw == '31-Mar':
                                    cgr = '31-3'
                                elif crg_raw == '1-Nov':
                                    cgr = '11-1'
                                elif crg_raw == '2-Nov':
                                    cgr = '11-2'
                                elif crg_raw == '3-Nov':
                                    cgr = '11-3'
                                elif crg_raw == '4-Nov':
                                    cgr = '11-4'
                                else:
                                    cgr = crg_raw

                                # Color — CGR
                                
                                clr = f"{cgr}"
                                if clr != 'nan':
                                    # clr = int(float(clr[:2]))
                                    clr_var = clr.split('-')
                                    clr1 = int(float(clr_var[0]))
                                    #if clr1 >= 11 and clr1 <= 21 :
                                    if clr1 == 11 or clr1 == 21 :
                                        check_lst.append('gold')
                                    elif clr1 == 31 :
                                        check_lst.append('silver')
                                    elif clr1 == 41 :
                                        check_lst.append('bronze')
                                    else:
                                        check_lst.append('0')
                                else:
                                    clr = 'nan'
                                # Leaf — LF
                                llf = f"{df3.iloc[i, 8]}"
                                if llf != 'nan':
                                    llf = int(llf[0])
                                    if llf <= 2 :
                                        check_lst.append('gold')
                                    elif llf <= 3 and llf > 2 :
                                        check_lst.append('silver')
                                    elif llf <= 4 and llf > 3 :
                                        check_lst.append('bronze')
                                    else:
                                        check_lst.append('0')
                                else:
                                    llf = 'nan'
                                # Staple — MIC
                                stap = f"{df3.iloc[i, 9]}"
                                if stap != 'nan':
                                    stap = float(stap)
                                    if stap >= 43 :
                                        check_lst.append('Llano Super')
                                    elif stap >= 38 and stap < 43 :
                                        check_lst.append('gold')
                                    elif stap >= 37 and stap < 38 :
                                        check_lst.append('silver')
                                    elif stap >= 36 and stap < 37 :
                                        check_lst.append('bronze')
                                    else:
                                        check_lst.append('0')
                                else:
                                    stap = 'nan'
                                # Strength — STR
                                streng = f"{df3.iloc[i, 13]}"
                                if streng != 'nan':
                                    streng = float(streng)
                                    if streng >= 33 :
                                        check_lst.append('gold')
                                    elif streng >= 31 and streng < 33 :
                                        check_lst.append('silver')
                                    elif streng >= 29 and streng < 31 :
                                        check_lst.append('bronze')
                                    else:
                                        check_lst.append('0')
                                else:
                                    streng = 'nan'
                                # Mic — Mic
                                trmic = f"{df3.iloc[i, 10]}"
                                if trmic !='nan':
                                    trmic = float(trmic)
                                    if trmic >= 3.7 and trmic <4.3 :
                                        check_lst.append('gold')
                                    else:
                                        check_lst.append('0')
                                else:
                                    trmic = 'nan'
                                # Uniformity  — UNIF
                                uniformi = f"{df3.iloc[i, 18]}"
                                if uniformi != 'nan':
                                    uniformi = float(uniformi)
                                    if uniformi >= 82 :
                                        check_lst.append('gold')
                                    elif uniformi >= 81 and uniformi < 82 :
                                        check_lst.append('silver')
                                    elif uniformi >= 80 and uniformi < 81 :
                                        check_lst.append('bronze')
                                    else:
                                        check_lst.append('0')
                                else:
                                    uniformi = 'nan'
                                lls = check_lst.count('Llano Super')
                                gg = check_lst.count('gold')
                                ss = check_lst.count('silver')
                                bb = check_lst.count('bronze')
                                zz = check_lst.count('0')
                                
                                if df3.iloc[i, 11] and df3.iloc[i, 11] != '  ' :
                                    var_ex = str(df3.iloc[i, 11])
                                else:
                                    var_ex = df3.iloc[i, 11]

                                if df3.iloc[i, 12] and df3.iloc[i, 12] != '  ' :
                                    var_rm = str(df3.iloc[i, 12])
                                else:
                                    var_rm = df3.iloc[i, 12]

                                if var_rm != 'nan'  and df3.iloc[i, 12] != '  ' and  df3.iloc[i, 12] != None :
                                    level="None"
                                elif var_ex != 'nan'  and df3.iloc[i, 11] != '  ' and  df3.iloc[i, 11] != None :
                                    level="None"
                                else:
                                    if gg >= 3 and lls == 1 :
                                        level="Llano Super"
                                    elif gg >= 4 :
                                        level="Gold"
                                    elif lls+gg+ss >= 4:
                                        level="Silver"
                                    elif lls+gg+ss+bb >= 4:
                                        level="Bronze"
                                    else:
                                        level="None"
                                try:
                                    warehouse_wh_id = int(df3.iloc[i, 25])
                                except:
                                    warehouse_wh_id = df3.iloc[i, 25]
                                balereport_save = BaleReportFarmField(
                                    classing_id =  classing.id,
                                    bale_id = int(df3.iloc[i, 2]),
                                    prod_id = prod_Id,
                                    farm_name = farm_name,
                                    wt = df3.iloc[i, 3],
                                    net_wt = df3.iloc[i, 4],
                                    load_id = df3.iloc[i, 5],
                                    dt_class = df3.iloc[i, 6],
                                    gr = df3.iloc[i, 7],
                                    lf = df3.iloc[i, 8],
                                    st = df3.iloc[i, 9],
                                    mic = df3.iloc[i, 10],
                                    ex = df3.iloc[i, 11],
                                    rm = df3.iloc[i, 12],
                                    str_no = df3.iloc[i, 13],
                                    cgr = cgr,
                                    rd = df3.iloc[i, 15],
                                    ob1 = df3.iloc[i, 16],
                                    tr = df3.iloc[i, 17],
                                    unif = df3.iloc[i, 18],
                                    len_num = df3.iloc[i, 19],
                                    elong = df3.iloc[i, 20],
                                    cents_lb = df3.iloc[i, 21],
                                    loan_value = df3.iloc[i, 22],
                                    warehouse_wt = df3.iloc[i, 23],
                                    warehouse_bale_id = df3.iloc[i, 24],
                                    warehouse_wh_id = warehouse_wh_id,
                                    level = level,
                                    ob2 = grower_id,
                                    ob3 = grower_name,
                                    ob4 = field_id,
                                    field_name = field_name,
                                    crop_variety = crop_variety,
                                    upload_date=date.today()
                                )
                                balereport_save.save()
                                balereport_save_certificate = balereport_save.certificate()
                                balereport_save.ob5 = balereport_save_certificate
                                balereport_save.save()
                        # 07-04-23
                        log_type, log_status, log_device = "ClassingReport", "Added", "Web"
                        log_idd, log_name = classing.id, str(classing.csv_path).replace("processor_reports/","")
                        log_details = "Bale Report by Farm/Field"
                        action_by_userid = request.user.id
                        user = User.objects.get(pk=action_by_userid)
                        user_role = user.role.all()
                        action_by_username = f'{user.first_name} {user.last_name}'
                        action_by_email = user.username
                        if request.user.id == 1 :
                            action_by_role = "superuser"
                        else:
                            action_by_role = str(','.join([str(i.role) for i in user_role]))
                        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                                            action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                            log_device=log_device)
                        logtable.save()
                        return redirect ('classing_list')
                    
                    return render(request, 'processor/classing_upload.html',context)

        return render (request, 'processor/classing_upload.html', context)
    # This is for processor .....
    elif request.user.is_processor:
        user_email = request.user.email
        p = ProcessorUser.objects.get(contact_email=user_email)
        processor_id = Processor.objects.get(id=p.processor_id).id
        grower = LinkGrowerToProcessor.objects.filter(processor_id=processor_id)
        grower_id = [i.grower_id for i in grower]
        get_grower = Grower.objects.filter(id__in = grower_id).order_by('name')

        context['get_grower'] = get_grower
        if request.method == 'POST':
            grower_id = request.POST.get('grower_id')
            id_field = request.POST.get('id_field')
            csv_file = request.FILES.get('csv_file')
            field = Field.objects.filter(grower_id = grower_id)
            context['field'] = field
            selectedgrower = Grower.objects.get(id=grower_id)
            context['selectedgrower'] = selectedgrower

            if csv_file == None :
                pass
            else:
                grower_name = Grower.objects.get(id=grower_id).name
                if id_field :
                    field_id = id_field
                    fff = Field.objects.get(id=field_id)
                    field_name = fff.name
                    crop_variety = fff.variety
                else:
                    field_name = None
                    crop_variety = None
                    field_id = None
                grower_id = grower_id
                csv_file = request.FILES.get('csv_file')
                mycsv = pd.read_csv(csv_file, skiprows=1)
                check = mycsv.columns[0]
                if str(check) == "Bale Report by Producer":
                    classing = ClassingReport(upload_date=date.today(),processor_id=processor_id,grower_id=grower_id,csv_path=csv_file,executed='No',csv_type='Bale Report by Producer')
                    classing.save()
                    csv_path_read = classing.csv_path.path

                    # below code for insert csv data in database
                    df = pd.read_csv(csv_path_read, skiprows=3)
                    prod_Id = df.iloc[0, 0]
                    farm_name = df.iloc[0, 1]
                    df['Farm_name'] = farm_name
                    df['Prod_id'] = prod_Id
                    df2 = df.iloc[1:]
                    drop_row = df2[df2['Lf'].isnull()].index
                    df2.drop(drop_row, inplace=True)
                    length_row = df2.shape[0]
                    for i in range(length_row):
                        try:
                            bale_id= int(df2.iloc[i, 1])
                        except:
                            bale_id= df2.iloc[i, 1]
                        bale_count = BaleReportFarmField.objects.filter(bale_id=bale_id).count()
                        if bale_count > 0 :
                            pass
                        elif df2.iloc[i, 1] == 'Gin Data(x3)' or df2.iloc[i, 1] == 'Bale #' :
                            pass
                        else:
                            crg_raw = df2.iloc[i, 14]
                            if crg_raw == '31-Jan':
                                cgr = '31-1'
                            elif crg_raw == '21-Jan':
                                cgr = '21-1'
                            elif crg_raw == '21-Feb':
                                cgr = '21-2'
                            elif crg_raw == '21-Mar':
                                cgr = '21-3'
                            elif crg_raw == '21-Apr':
                                cgr = '21-4'
                            elif crg_raw == '31-Mar':
                                cgr = '31-3'
                            elif crg_raw == '1-Nov':
                                cgr = '11-1'
                            elif crg_raw == '2-Nov':
                                cgr = '11-2'
                            elif crg_raw == '3-Nov':
                                    cgr = '11-3'
                            elif crg_raw == '4-Nov':
                                cgr = '11-4'
                            else:
                                cgr = crg_raw
                            

                            # Color — CGR
                            check_lst = []
                            clr = f"{cgr}"
                            if clr != 'nan':
                                # clr = int(float(clr[:2]))
                                clr_var = clr.split('-')
                                clr1 = int(float(clr_var[0]))
                                #if clr1 >= 11 and clr1 <= 21 :
                                if clr1 == 11 or clr1 == 21 :
                                    check_lst.append('gold')
                                elif clr1 == 31 :
                                    check_lst.append('silver')
                                elif clr1 == 41 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                clr = 'nan'
                            # Leaf — LF
                            llf = f"{df2.iloc[i, 8]}"
                            if llf != 'nan':
                                llf = int(llf[0])
                                if llf <= 2 :
                                    check_lst.append('gold')
                                elif llf <= 3 and llf > 2 :
                                    check_lst.append('silver')
                                elif llf <= 4 and llf > 3 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                llf = 'nan'
                            # Staple — MIC
                            stap = f"{df2.iloc[i, 9]}"
                            if stap != 'nan':
                                stap = float(stap)
                                if stap >= 43 :
                                    check_lst.append('Llano Super')
                                elif stap >= 38 and stap < 43 :
                                    check_lst.append('gold')
                                elif stap >= 37 and stap < 38 :
                                    check_lst.append('silver')
                                elif stap >= 36 and stap < 37 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                stap = 'nan'
                            # Strength — STR
                            streng = f"{df2.iloc[i, 13]}"
                            if streng != 'nan':
                                streng = float(streng)
                                if streng >= 33 :
                                    check_lst.append('gold')
                                elif streng >= 31 and streng < 33 :
                                    check_lst.append('silver')
                                elif streng >= 29 and streng < 31 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                streng = 'nan'
                            # Mic — TR
                            trmic = f"{df2.iloc[i, 10]}"
                            if trmic !='nan':
                                trmic = float(trmic)
                                if trmic >= 3.7 and trmic <4.3 :
                                    check_lst.append('gold')
                                else:
                                    check_lst.append('0')
                            else:
                                trmic = 'nan'
                            # Uniformity  — UNIF
                            uniformi = f"{df2.iloc[i, 18]}"
                            if uniformi != 'nan':
                                uniformi = float(uniformi)
                                if uniformi >= 82 :
                                    check_lst.append('gold')
                                elif uniformi >= 81 and uniformi < 82 :
                                    check_lst.append('silver')
                                elif uniformi >= 80 and uniformi < 81 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                uniformi = 'nan'
                            lls = check_lst.count('Llano Super')
                            gg = check_lst.count('gold')
                            ss = check_lst.count('silver')
                            bb = check_lst.count('bronze')
                            zz = check_lst.count('0')
                            if df2.iloc[i, 11] and df2.iloc[i, 11] != '  ' :
                                var_ex = str(df2.iloc[i, 11])
                            else:
                                var_ex = df2.iloc[i, 11]

                            if df2.iloc[i, 12] and df2.iloc[i, 12] != '  ' :
                                var_rm = str(df2.iloc[i, 12])
                            else:
                                var_rm = df2.iloc[i, 12]

                            if var_rm != 'nan'  and df2.iloc[i, 12] != '  ' and  df2.iloc[i, 12] != None :
                                level="None"
                            elif var_ex != 'nan'  and df2.iloc[i, 11] != '  ' and  df2.iloc[i, 11] != None :
                                level="None"
                            else:
                                if gg>=3 and lls==1 :
                                    level="Llano Super"
                                elif gg>=4 :
                                    level="Gold"
                                elif lls+gg+ss>=4:
                                    level="Silver"
                                elif lls+gg+ss+bb>=4:
                                    level="Bronze"
                                else:
                                    level="None"

                            balereport_save = BaleReportFarmField(
                                classing_id = classing.id,
                                bale_id=df2.iloc[i, 1],
                                net_wt=df2.iloc[i, 2],
                                farm_id=df2.iloc[i, 3],
                                load_id=df2.iloc[i, 4],
                                # field_name=df2.iloc[i, 5],
                                field_name = field_name,
                                pk_num=df2.iloc[i, 6],
                                gr=df2.iloc[i, 7],
                                lf=df2.iloc[i, 8],
                                st=df2.iloc[i, 9],
                                mic=df2.iloc[i, 10],
                                ex=df2.iloc[i, 11],
                                rm=df2.iloc[i, 12],
                                str_no=df2.iloc[i, 13],
                                cgr=cgr,
                                rd=df2.iloc[i, 15],
                                ob1=df2.iloc[i, 16],
                                tr=df2.iloc[i, 17],
                                unif=df2.iloc[i, 18],
                                len_num=df2.iloc[i, 19],
                                elong=df2.iloc[i, 20],
                                value=df2.iloc[i, 21],
                                farm_name=df2.iloc[i, 22],
                                prod_id=df2.iloc[i, 23],
                                level=level, 
                                ob2 = grower_id,
                                ob3 = grower_name,
                                ob4 = field_id,
                                crop_variety = crop_variety,
                                upload_date=date.today()
                            )
                            balereport_save.save()
                            balereport_save_certificate = balereport_save.certificate()
                            balereport_save.ob5 = balereport_save_certificate
                            balereport_save.save()
                    # 07-04-23
                    log_type, log_status, log_device = "ClassingReport", "Added", "Web"
                    log_idd, log_name = classing.id, str(classing.csv_path).replace("processor_reports/","")
                    log_details = "Bale Report by Producer"
                    action_by_userid = request.user.id
                    user = User.objects.get(pk=action_by_userid)
                    user_role = user.role.all()
                    action_by_username = f'{user.first_name} {user.last_name}'
                    action_by_email = user.username
                    if request.user.id == 1 :
                        action_by_role = "superuser"
                    else:
                        action_by_role = str(','.join([str(i.role) for i in user_role]))
                    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                                        action_by_email=action_by_email,action_by_role=action_by_role,log_device=log_device)
                    logtable.save()
                    return redirect ('classing_list')

                if str(check) == "Bale Report by Farm/Field":
                    classing = ClassingReport(processor_id=processor_id,grower_id=grower_id,csv_path=csv_file,executed='No',csv_type='Bale Report by Farm/Field')
                    classing.save()
                    csv_path_read = classing.csv_path.path
                    df=pd.read_csv(csv_path_read,skiprows=3)
                    prod_Id = df.iloc[0, 1]
                    farm_name = df.iloc[0, 2]
                    # df['Farm_name'] = farm_name
                    # df['Prod_id'] = prod_Id
                    df2 = df.iloc[1:]
                    # drop_row = df2[df2['Bale #'] == farm_name].index
                    # drop_null_row = df2[df2['Bale #'].isnull()].index
                    drop_row_again = df2[df2['Lf'].isnull()].index
                    # df2.drop(drop_row, inplace=True)
                    # df2.drop(drop_null_row, inplace=True)
                    df2.drop(drop_row_again, inplace=True)
                    df3 = df2.reset_index(drop=True)
                    length_row = df3.shape[0]
                    for i in range(length_row):
                        try:
                            bale_id=int(df3.iloc[i, 2])
                        except:
                            bale_id=df3.iloc[i, 2]
                        bale_count = BaleReportFarmField.objects.filter(bale_id=bale_id).count() 
                        if bale_count > 0 :
                            pass
                        elif df3.iloc[i, 2] == 'Gin Data(x3)' or df3.iloc[i, 2] == 'Bale #' :
                            pass
                        else:
                            crg_raw = df3.iloc[i, 14]
                            if crg_raw == '31-Jan':
                                cgr = '31-1'
                            elif crg_raw == '21-Jan':
                                cgr = '21-1'
                            elif crg_raw == '21-Feb':
                                cgr = '21-2'
                            elif crg_raw == '21-Mar':
                                cgr = '21-3'
                            elif crg_raw == '21-Apr':
                                cgr = '21-4'
                            elif crg_raw == '31-Mar':
                                cgr = '31-3'
                            elif crg_raw == '1-Nov':
                                cgr = '11-1'
                            elif crg_raw == '2-Nov':
                                cgr = '11-2'
                            elif crg_raw == '3-Nov':
                                    cgr = '11-3'
                            elif crg_raw == '4-Nov':
                                cgr = '11-4'
                            else:
                                cgr = crg_raw
                            
                            # Color — CGR
                            check_lst = []
                            clr = f"{cgr}"
                            if clr != 'nan':
                                # clr = int(float(clr[:2]))
                                clr_var = clr.split('-')
                                clr1 = int(float(clr_var[0]))
                                #if clr1 >= 11 and clr1 <= 21 :
                                if clr1 == 11 or clr1 == 21 :
                                    check_lst.append('gold')
                                elif clr1 == 31 :
                                    check_lst.append('silver')
                                elif clr1 == 41 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                clr = 'nan'
                            # Leaf — LF
                            llf = f"{df3.iloc[i, 8]}"
                            if llf != 'nan':
                                llf = int(llf[0])
                                if llf <= 2 :
                                    check_lst.append('gold')
                                elif llf <= 3 and llf > 2 :
                                    check_lst.append('silver')
                                elif llf <= 4 and llf > 3 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                llf = 'nan'
                            # Staple — MIC
                            stap = f"{df3.iloc[i, 9]}"
                            if stap != 'nan':
                                stap = float(stap)
                                if stap >= 43 :
                                    check_lst.append('Llano Super')
                                elif stap >= 38 and stap < 43 :
                                    check_lst.append('gold')
                                elif stap >= 37 and stap < 38 :
                                    check_lst.append('silver')
                                elif stap >= 36 and stap < 37 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                stap = 'nan'
                            # Strength — ST
                            streng = f"{df3.iloc[i, 13]}"
                            if streng != 'nan':
                                streng = float(streng)
                                if streng >= 33 :
                                    check_lst.append('gold')
                                elif streng >= 31 and streng < 33 :
                                    check_lst.append('silver')
                                elif streng >= 29 and streng < 31 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                streng = 'nan'
                            # Mic — Mic
                            trmic = f"{df3.iloc[i, 10]}"
                            if trmic !='nan':
                                trmic = float(trmic)
                                if trmic >= 3.7 and trmic <4.3 :
                                    check_lst.append('gold')
                                else:
                                    check_lst.append('0')
                            else:
                                trmic = 'nan'
                            # Uniformity  — UNIF
                            uniformi = f"{df3.iloc[i, 18]}"
                            if uniformi != 'nan':
                                uniformi = float(uniformi)
                                if uniformi >= 82 :
                                    check_lst.append('gold')
                                elif uniformi >= 81 and uniformi < 82 :
                                    check_lst.append('silver')
                                elif uniformi >= 80 and uniformi < 81 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                uniformi = 'nan'
                            lls = check_lst.count('Llano Super')
                            gg = check_lst.count('gold')
                            ss = check_lst.count('silver')
                            bb = check_lst.count('bronze')
                            zz = check_lst.count('0')
                            if df3.iloc[i, 11] and df3.iloc[i, 11] != '  ' :
                                var_ex = str(df3.iloc[i, 11])
                            else:
                                var_ex = df3.iloc[i, 11]

                            if df3.iloc[i, 12] and df3.iloc[i, 12] != '  ' :
                                var_rm = str(df3.iloc[i, 12])
                            else:
                                var_rm = df3.iloc[i, 12]

                            if var_rm != 'nan'  and df3.iloc[i, 12] != '  ' and  df3.iloc[i, 12] != None :
                                level="None"
                            elif var_ex != 'nan'  and df3.iloc[i, 11] != '  ' and  df3.iloc[i, 11] != None :
                                level="None"
                            else:
                                if gg>=3 and lls==1 :
                                    level="Llano Super"
                                elif gg>=4 :
                                    level="Gold"
                                elif lls+gg+ss>=4:
                                    level="Silver"
                                elif lls+gg+ss+bb>=4:
                                    level="Bronze"
                                else:
                                    level="None"
                            try:
                                warehouse_wh_id = int(df3.iloc[i, 25])
                            except:
                                warehouse_wh_id = df3.iloc[i, 25]
                            balereport_save = BaleReportFarmField(
                                classing_id =  classing.id,
                                bale_id = int(df3.iloc[i, 2]),
                                prod_id = prod_Id,
                                farm_name = farm_name,
                                wt = df3.iloc[i, 3],
                                net_wt = df3.iloc[i, 4],
                                load_id = df3.iloc[i, 5],
                                dt_class = df3.iloc[i, 6],
                                gr = df3.iloc[i, 7],
                                lf = df3.iloc[i, 8],
                                st = df3.iloc[i, 9],
                                mic = df3.iloc[i, 10],
                                ex = df3.iloc[i, 11],
                                rm = df3.iloc[i, 12],
                                str_no = df3.iloc[i, 13],
                                cgr = cgr,
                                rd = df3.iloc[i, 15],
                                ob1 = df3.iloc[i, 16],
                                tr = df3.iloc[i, 17],
                                unif = df3.iloc[i, 18],
                                len_num = df3.iloc[i, 19],
                                elong = df3.iloc[i, 20],
                                cents_lb = df3.iloc[i, 21],
                                loan_value = df3.iloc[i, 22],
                                warehouse_wt = df3.iloc[i, 23],
                                warehouse_bale_id = df3.iloc[i, 24],
                                warehouse_wh_id = warehouse_wh_id,
                                level=level,
                                ob2 = grower_id,
                                ob3 = grower_name,
                                ob4 = field_id,
                                field_name = field_name,
                                crop_variety = crop_variety,
                                upload_date=date.today()
                            )
                            balereport_save.save()
                            balereport_save_certificate = balereport_save.certificate()
                            balereport_save.ob5 = balereport_save_certificate
                            balereport_save.save()
                    
                    # 07-04-23
                    log_type, log_status, log_device = "ClassingReport", "Added", "Web"
                    log_idd, log_name = classing.id, str(classing.csv_path).replace("processor_reports/","")
                    log_details = "Bale Report by Farm/Field"
                    action_by_userid = request.user.id
                    user = User.objects.get(pk=action_by_userid)
                    user_role = user.role.all()
                    action_by_username = f'{user.first_name} {user.last_name}'
                    action_by_email = user.username
                    if request.user.id == 1 :
                        action_by_role = "superuser"
                    else:
                        action_by_role = str(','.join([str(i.role) for i in user_role]))
                    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                                        action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                        log_device=log_device)
                    logtable.save()

                    return redirect ('classing_list')
        return render (request, 'processor/classing_upload.html', context)

@login_required()
def unassign_bale_processor2(request,bale_id):
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        del_bale_processor2 = AssignedBaleProcessor2.objects.get(assigned_bale=bale_id)
        # 20-04-23 LogTable
        log_type, log_status, log_device = "ClassingListTier2", "Deleted", "Web"
        log_idd, log_name = del_bale_processor2.id, del_bale_processor2.assigned_bale
        log_details = f"bale_id = {del_bale_processor2.bale.id} | assigned_bale = {del_bale_processor2.assigned_bale} | processor2 = {del_bale_processor2.processor2.entity_name} | farm_name = {del_bale_processor2.farm_name} | field_name = {del_bale_processor2.field_name} | grower_name = {del_bale_processor2.grower_name} | certificate = {del_bale_processor2.certificate} | variety = {del_bale_processor2.level} | "
        action_by_userid = request.user.id
        user = User.objects.get(pk=action_by_userid)
        user_role = user.role.all()
        action_by_username = f'{user.first_name} {user.last_name}'
        action_by_email = user.username
        if request.user.id == 1 :
            action_by_role = "superuser"
        else:
            action_by_role = str(','.join([str(i.role) for i in user_role]))
        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                            action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                            log_device=log_device)
        logtable.save()
        del_bale_processor2.delete()
        return HttpResponse (1)


@login_required()
def classing_csv_list(request):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        context = {}
        context['processor2'] = Processor2.objects.all()
               
        # save bale to processor2
        if request.method == 'POST' :
            processor2_id = request.POST.get('processor2_id')
            get_bale2 = request.POST.get('get_bale2')
            raw_id = request.POST.get('raw_id')
            mark_id = request.POST.get('mark_id')
            gin_id = request.POST.get('gin_id')
            if processor2_id and get_bale2 :
                check_bale2 = BaleReportFarmField.objects.filter(id=raw_id)
                if check_bale2.exists() :
                    # check_bale2_for_processor2 = AssignedBaleProcessor2.objects.filter(assigned_bale=get_bale2)
                    # if check_bale2_for_processor2.exists() :
                    #     assigned_bale_processor2 = AssignedBaleProcessor2.objects.get(assigned_bale=get_bale2)
                    #     assigned_bale_processor2.processor2_id = processor2_id
                    #     assigned_bale_processor2.mark_id = mark_id
                    #     assigned_bale_processor2.gin_id = gin_id
                    #     assigned_bale_processor2.save()
                    # else:
                        get_bale2_processor = BaleReportFarmField.objects.get(id=raw_id)
        
                        assigned_bale_processor2 = AssignedBaleProcessor2(processor2_id=processor2_id,bale_id=get_bale2_processor.id,assigned_bale=get_bale2,
                        prod_id=get_bale2_processor.prod_id,wt=get_bale2_processor.wt,net_wt=get_bale2_processor.net_wt,load_id=get_bale2_processor.load_id,
                        dt_class=get_bale2_processor.dt_class,gr=get_bale2_processor.gr,lf=get_bale2_processor.lf,st=get_bale2_processor.st,mic=get_bale2_processor.mic,
                        ex=get_bale2_processor.ex,rm=get_bale2_processor.rm,str_no=get_bale2_processor.str_no,cgr=get_bale2_processor.cgr,rd=get_bale2_processor.rd,
                        tr=get_bale2_processor.tr,unif=get_bale2_processor.unif,len_num=get_bale2_processor.len_num,elong=get_bale2_processor.elong,cents_lb=get_bale2_processor.cents_lb,
                        loan_value=get_bale2_processor.loan_value,warehouse_wt=get_bale2_processor.warehouse_wt,warehouse_bale_id=get_bale2_processor.warehouse_bale_id,
                        warehouse_wh_id=get_bale2_processor.warehouse_wh_id,farm_name=get_bale2_processor.farm_name,sale_status=get_bale2_processor.sale_status,
                        wh_id=get_bale2_processor.wh_id,ob1=get_bale2_processor.ob1,gin_date=get_bale2_processor.gin_date,farm_id=get_bale2_processor.farm_id,
                        field_name=get_bale2_processor.field_name,pk_num=get_bale2_processor.pk_num,grower_idd=get_bale2_processor.ob2,grower_name=get_bale2_processor.ob3,
                        field_idd=get_bale2_processor.ob4,certificate=get_bale2_processor.ob5,value=get_bale2_processor.value,level=get_bale2_processor.level,
                        crop_variety=get_bale2_processor.crop_variety,mark_id=mark_id,gin_id=gin_id)
                        assigned_bale_processor2.save()
                        # 20-04-23 LogTable
                        log_type, log_status, log_device = "ClassingListTier2", "Added", "Web"
                        log_idd, log_name = assigned_bale_processor2.id, assigned_bale_processor2.assigned_bale
                        log_details = f"bale_id = {assigned_bale_processor2.bale.id} | assigned_bale = {assigned_bale_processor2.assigned_bale} | processor2 = {assigned_bale_processor2.processor2.entity_name} | farm_name = {assigned_bale_processor2.farm_name} | field_name = {assigned_bale_processor2.field_name} | grower_name = {assigned_bale_processor2.grower_name} | certificate = {assigned_bale_processor2.certificate} | variety = {assigned_bale_processor2.level} | "
                        action_by_userid = request.user.id
                        user = User.objects.get(pk=action_by_userid)
                        user_role = user.role.all()
                        action_by_username = f'{user.first_name} {user.last_name}'
                        action_by_email = user.username
                        if request.user.id == 1 :
                            action_by_role = "superuser"
                        else:
                            action_by_role = str(','.join([str(i.role) for i in user_role]))
                        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                                            action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                            log_device=log_device)
                        logtable.save()
                        # Notification 
                        p2user_id_all1 = ProcessorUser2.objects.filter(processor2_id=processor2_id)
                        for j in p2user_id_all1 :
                            msg1 = 'New Bales are assigned to you '
                            p_user_id1 = User.objects.get(username=j.contact_email)
                            notification_reason1 = 'New Bale Assigned'
                            redirect_url1 = "/processor2/list_bale_processor2/"
                            save_notification = ShowNotification(user_id_to_show=p_user_id1.id,msg=msg1,status="UNREAD",redirect_url=redirect_url1,
                            notification_reason=notification_reason1)
                            save_notification.save()

        classing = ClassingReport.objects.all()
        report_data = BaleReportFarmField.objects.all().order_by('-id')
        growers_id = [i.grower.id for i in classing]
        growers = Grower.objects.filter(id__in=growers_id).order_by('name')
        context['growers'] = growers
        selectedGrower = ''
        # Search 
        get_bale_id = [f"{i.bale_id}" for i in report_data]
        get_field_nm = [f"{i.field_name}" for i in report_data]        
        get_farm_nm = [f"{i.farm_name}" for i in report_data]
        get_wh_id = [f"{i.warehouse_wh_id}" for i in report_data]
        
        lst = list(set(get_bale_id + get_field_nm + get_farm_nm + get_wh_id))
        select_search_json = json.dumps(lst)
        context['select_search_json'] = select_search_json

        search_name = request.GET.get('search_name')
        grower_id = request.GET.get('grower_id')
        cerSelction = request.GET.get('cerSelction')
        lelSelction = request.GET.get('lelSelction')    
        print(search_name,"..",grower_id,"..", cerSelction,"..",lelSelction,"..")
        # 24-08-23 custom filter
        if search_name :
            report_data = report_data.filter( Q(bale_id__icontains=search_name) | Q(field_name__icontains=search_name) |
                                              Q(farm_name__icontains=search_name) | Q(warehouse_wh_id__icontains=search_name)).distinct()
            context['search_get'] = search_name
        else:
            if grower_id :
                selectedGrower = Grower.objects.get(id=grower_id)
                context['selectedGrower'] = selectedGrower
                classing = classing.filter(grower_id=grower_id)
                classing_id = [i.id for i in classing]
                report_data = report_data.filter(classing_id__in=classing_id)
            if cerSelction :
                context['selectedCre'] = cerSelction
                if cerSelction == "null" :
                    report_data = report_data.filter(ob5=None)
                else:
                    report_data = report_data.filter(ob5=cerSelction)
            if lelSelction :
                context['selectedLel'] = lelSelction
                report_data = report_data.filter(level=lelSelction)

        # pagination
        paginator = Paginator(report_data, 100)
        page = request.GET.get('page')
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)

        context['report'] = report
        return render (request, 'processor/classing_csv_list_admin.html', context)
    # this is for processor
    elif request.user.is_processor:
        user_email = request.user.email
        p = ProcessorUser.objects.get(contact_email=user_email)
        processor_id = Processor.objects.get(id=p.processor.id).id
        cr = ClassingReport.objects.filter(processor_id=processor_id)
        rp = [i.id for i in cr]
        growers_id = [i.grower.id for i in cr]
        growers = Grower.objects.filter(id__in=growers_id).order_by('name')
        context['growers'] = growers
        report_data = BaleReportFarmField.objects.filter(classing_id__in=rp)
        
        get_bale_id = [f"{i.bale_id}" for i in report_data]
        get_field_nm = [f"{i.field_name}" for i in report_data]        
        get_farm_nm = [f"{i.farm_name}" for i in report_data]
        get_wh_id = [f"{i.warehouse_wh_id}" for i in report_data]
        
        lst = list(set(get_bale_id + get_field_nm + get_farm_nm + get_wh_id))
        select_search_json = json.dumps(lst)
        context['select_search_json'] = select_search_json

        search_name = request.GET.get('search_name')
        grower_id = request.GET.get('grower_id')
        cerSelction = request.GET.get('cerSelction')
        lelSelction = request.GET.get('lelSelction') 

        if search_name :
            report_data = report_data.filter(classing_id__in=rp).filter(
            Q(bale_id__icontains=search_name) | Q(field_name__icontains=search_name) | Q(farm_name__icontains=search_name) |
            Q(warehouse_wh_id__icontains=search_name)).distinct()
            context['search_get'] = search_name
        else:
            if grower_id :
                selectedGrower = Grower.objects.get(id=grower_id)
                context['selectedGrower'] = selectedGrower
                classing = ClassingReport.objects.filter(grower_id=grower_id)
                classing_id = [i.id for i in classing]
                report_data = report_data.filter(classing_id__in=classing_id)
                
            if cerSelction :
                context['selectedCre'] = cerSelction
                if cerSelction == "null" :
                    report_data = report_data.filter(ob5=None).filter(classing_id__in=rp)
                else:
                    report_data = report_data.filter(ob5=cerSelction).filter(classing_id__in=rp)
                
            if lelSelction :
                context['selectedLel'] = lelSelction
                report_data = report_data.filter(level=lelSelction).filter(classing_id__in=rp)       
        
        paginator = Paginator(report_data, 100)
        page = request.GET.get('page')
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)
        
        context['report'] = report
        return render (request, 'processor/classing_csv_list_admin.html', context)

@login_required()
def classing_csv_list_view(request,pk):
    report_data =  BaleReportFarmField.objects.get(id=pk)
    check_bale_assigned_processor2 = AssignedBaleProcessor2.objects.filter(assigned_bale=report_data.bale_id).filter(warehouse_wh_id=report_data.warehouse_wh_id)
    if check_bale_assigned_processor2.exists() :
        exist_processor2name = AssignedBaleProcessor2.objects.get(assigned_bale=report_data.bale_id).processor2.entity_name
        mark_id = AssignedBaleProcessor2.objects.get(assigned_bale=report_data.bale_id).mark_id
        gin_id = AssignedBaleProcessor2.objects.get(assigned_bale=report_data.bale_id).gin_id
    else:
        exist_processor2name = ''
        mark_id = ''
        gin_id = ''
    
    csv_name = str(report_data.classing.csv_path).split('/')[1]
    responce = {
        "raw_id":report_data.id,
        "prod_id":report_data.prod_id,
        "farm_name":report_data.farm_name,
        "grower_name":report_data.classing.grower.name,
        "wh_id":report_data.wh_id,
        "bale_id":report_data.bale_id,
        "warehouse_wt":report_data.warehouse_wh_id,
        "dt_class":report_data.dt_class,
        "net_wt":report_data.net_wt,
        "farm_id":report_data.farm_id,
        "load_id":report_data.load_id,
        "field_name":report_data.field_name,
        "crop_variety": report_data.crop_variety,
        "certificate":report_data.ob5,
        "level":report_data.level,
        "pk_num":report_data.pk_num,
        "gr":report_data.gr,
        "lf":report_data.lf,
        "st":report_data.st,
        "mic":report_data.mic,
        "ex":report_data.ex,
        "rm":report_data.rm,
        "str_no":report_data.str_no,
        "cgr":report_data.cgr,
        "rd":report_data.rd,
        "ob1":report_data.ob1,
        "tr":report_data.tr,
        "unif":report_data.unif,
        "len_num":report_data.len_num,
        "elong":report_data.elong,
        "value":report_data.value,
        "csv_type":report_data.classing.csv_type,
        "csv_name":csv_name,
        "exist_processor2name":exist_processor2name,
        "mark_id":mark_id,
        "gin_id":gin_id,
        }
    return JsonResponse(responce)


@login_required()
def classing_list(request):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        classing = ClassingReport.objects.all()
        class_list = []
        for i in classing :
            bale = BaleReportFarmField.objects.filter(classing_id = i.id)[:1]
            if bale :
                field_name = [i.field_name for i in bale][0]
            else:
                field_name = 'None'
            if i.upload_date :
                upload_date = i.upload_date
            else:
                upload_date = ''
            data = {
                "id":i.id,
                "entity_name":i.processor.entity_name,
                "grower_name":i.grower.name,
                "field_name":field_name,
                "csv_path":i.csv_path,
                "csv_type":i.csv_type,
                "csv_download_path":i.csv_path.url,
                "upload_date":upload_date,
            }
            class_list.append(data)
        context['cr'] = class_list
        return render (request, 'processor/classing_list.html', context)
    elif request.user.is_processor:
        user_email = request.user.email
        p = ProcessorUser.objects.get(contact_email=user_email)
        processor_id = Processor.objects.get(id=p.processor_id).id
        grower = LinkGrowerToProcessor.objects.filter(processor_id=processor_id)
        grower_id = [i.grower_id for i in grower]
        classing = ClassingReport.objects.filter(grower_id__in=grower_id)
        class_list = []
        for i in classing :
            bale = BaleReportFarmField.objects.filter(classing_id = i.id)[:1]
            if bale :
                field_name = [i.field_name for i in bale][0]
            else:
                field_name = 'None'
            if i.upload_date :
                upload_date = i.upload_date
            else:
                upload_date = ''
            data = {
                "id":i.id,
                "entity_name":i.processor.entity_name,
                "grower_name":i.grower.name,
                "field_name":field_name,
                "csv_path":i.csv_path,
                "csv_type":i.csv_type,
                "csv_download_path":i.csv_path.url,
                "upload_date":upload_date,
            }
            class_list.append(data)
        context['cr'] = class_list
        return render (request, 'processor/classing_list.html', context)

@login_required()
def classing_delete(request,pk):
    cr = ClassingReport.objects.get(id=pk)
    # 07-04-23 Log Table
    log_type, log_status, log_device = "ClassingReport", "Deleted", "Web"
    log_idd, log_name = cr.id, str(cr.csv_path).replace("processor_reports/","")
    log_details = f"csv_type = {cr.csv_type} | processor_id = {cr.processor.id} | processor = {cr.processor.entity_name} | grower_id = {cr.grower.id} | grower = {cr.grower.name}"
    action_by_userid = request.user.id
    user = User.objects.get(pk=action_by_userid)
    user_role = user.role.all()
    action_by_username = f'{user.first_name} {user.last_name}'
    action_by_email = user.username
    if request.user.id == 1 :
        action_by_role = "superuser"
    else:
        action_by_role = str(','.join([str(i.role) for i in user_role]))
    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                        action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                        log_device=log_device)
    logtable.save()
    cr.delete()
    return HttpResponse(1)

@login_required()
def classing_edit(request,pk):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        classing = ClassingReport.objects.get(id=pk)
        context['classing'] = classing
        field = Field.objects.filter(grower_id = classing.grower.id)
        context['field'] = field
        bale = BaleReportFarmField.objects.filter(classing_id = classing.id)
        if bale.exists() :
            fieldname = [i.field_name for i in bale][0]
        else:
            fieldname = ''

        if Field.objects.filter(name=fieldname).count() != 0 :
            selectedfield = Field.objects.get(name=fieldname)
        else:
            selectedfield = ''
        context['selectedfield'] = selectedfield
        if request.method == 'POST':
            id_field = request.POST.get('id_field')
            if id_field != None and id_field != '' :
                for i in bale:
                    bb = BaleReportFarmField.objects.get(id = i.id)
                    ff = Field.objects.get(id=id_field)
                    bb.ob2 = bb.classing.grower.id
                    bb.ob3 = bb.classing.grower.name
                    bb.field_name = ff.name
                    bb.ob4 = id_field
                    bb.save()
                
                # 07-04-23
                log_type, log_status, log_device = "ClassingReport", "Edited", "Web"
                log_idd, log_name = classing.id, str(classing.csv_path).replace("processor_reports/","")
                log_details = f"csv_type = {classing.csv_type} | processor_id = {classing.processor.id} | processor = {classing.processor.entity_name} | grower_id = {classing.grower.id} | grower = {classing.grower.name}"
   
                action_by_userid = request.user.id
                user = User.objects.get(pk=action_by_userid)
                user_role = user.role.all()
                action_by_username = f'{user.first_name} {user.last_name}'
                action_by_email = user.username
                if request.user.id == 1 :
                    action_by_role = "superuser"
                else:
                    action_by_role = str(','.join([str(i.role) for i in user_role]))
                logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                    action_by_userid=action_by_userid,action_by_username=action_by_username,
                                    action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                    log_device=log_device)
                logtable.save()
                return redirect ('classing_list') 
        return render (request, 'processor/classing_edit.html', context)

@login_required()
def classing_upload_via_dat(request):
    context={}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        grower = LinkGrowerToProcessor.objects.all()
        processor_id = [i.processor_id for i in grower]
        grower_id = [i.grower_id for i in grower]
        get_processor = Processor.objects.filter(id__in = processor_id).order_by('entity_name')
        get_grower = Grower.objects.filter(id__in = grower_id).order_by('name')
        context['get_processor'] = get_processor
        if request.method == 'POST':
            processor_id = request.POST.get('processor_id')
            p = Processor.objects.get(id=processor_id)
            context['p'] = p
            var = LinkGrowerToProcessor.objects.filter(processor_id = p.id)
            grower_id = [i.grower_id for i in var]
            get_grower = Grower.objects.filter(id__in = grower_id).order_by('name')
            context['get_grower'] = get_grower
            if request.POST.get('grower_id') != None :
                grower_id = request.POST.get('grower_id')
                field_id = request.POST.get('field_id')
                dat_file = request.FILES.get('dat_file')
                selectedgrower = Grower.objects.get(id = grower_id)
                grower_name = selectedgrower.name
                context['selectedgrower'] = selectedgrower
                get_field = Field.objects.filter(grower_id=grower_id)
                context['get_field'] = get_field
                               
                if dat_file != None :
                    ifile  = open(dat_file.temporary_file_path(), "r")
                    read = csv.reader(ifile)
                else:
                    read = ''
                
                if processor_id != None and grower_id != None and field_id != None and dat_file != None :
                    field_name = Field.objects.get(id=field_id).name
                    classing = ClassingReport(upload_date=date.today(),processor_id = processor_id,grower_id = grower_id,
                    csv_path = dat_file, csv_type = ".dat")
                    classing.save()
                
                    for row in read :
                        line = row[0]
                        gin_code_5 = line[4:9]
                        gin_tag_7 = line[9:16]
                        date_classed_mdy_6 = line[16:22]
                        module_trailer_no_5 = line[23:28]
                        module_trailer_bales_2 = line[28:30]
                        color_grade_2 = line[33:35]
                        staple_2 = line[35:37]
                        govt_mic_2 = line[37:39]
                        strength_4 = line[40:44]
                        leaf_grade_1 = line[44:45]
                        remarks_1 = line[45:47]
                        remarks_2 = line[47:49]
                        color_code_2 = line[50:52]
                        color_quadrant_1 = line[52:53]
                        color_rd_no_decimal_3 = line[53:56]
                        color_plusb_3 = line[56:59]
                        trash_meter_2 = line[60:62]
                        length_in_100_3 = line[63:66]
                        uniformity_3 = line[67:70]
                        cotton_type_1 = line[70:71]
                        class_type_1 = line[71:72]
                        Whse_code_6 = line[89:95]
                        Whse_tag_7 = line[95:102]
                        gross_weight_3 = line[102:105]
                        tare_weight_2 = line[105:107]
                        net_weight_3 = line[107:110]
                        storage_date_MMDDYYYY_8 = line[112:120]
                        ginning_date_MMDDYYYY_8 = line[120:128]
                        producer_account_no_6 = line[128:134]
                        producer_lot_no_2 = line[134:136]
                        farm_6 = line[141:147]
                        bale_check = BaleReportFarmField.objects.filter(bale_id=gin_tag_7)
                        if bale_check.exists() :
                            pass
                        else:
                            # load_id , gr , ex , rm , elong, ob1
                            cgr = "{}-{}".format(color_code_2,color_quadrant_1)
                            dt_class = "{}/{}/{}".format(date_classed_mdy_6[:2],date_classed_mdy_6[2:4],date_classed_mdy_6[4:6])
                            rd_new = "{}.{}".format(color_rd_no_decimal_3[:2],color_rd_no_decimal_3[2:3])
                            ob_new = "{}.{}".format(color_plusb_3[:1],color_plusb_3[1:3])
                            unif_new = "{}.{}".format(uniformity_3[:2],uniformity_3[2:3])
                            mic_new = "{}.{}".format(govt_mic_2[:1],govt_mic_2[1:2])
                            # rm = "{}{}".format(remarks_1,remarks_2) 

                            # Color — CGR
                            check_lst = []
                            clr = f"{cgr}"
                            if clr != 'nan':
                                # clr = int(float(clr[:2]))
                                clr_var = clr.split('-')
                                clr1 = int(float(clr_var[0]))
                                #if clr1 >= 11 and clr1 <= 21 :
                                if clr1 == 11 or clr1 == 21 :
                                    check_lst.append('gold')
                                elif clr1 == 31 :
                                    check_lst.append('silver')
                                elif clr1 == 41 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                clr = 'nan'
                            # Leaf — LF
                            llf = f"{leaf_grade_1}"
                            if llf != 'nan':
                                llf = int(llf[0])
                                if llf <= 2 :
                                    check_lst.append('gold')
                                elif llf <= 3 and llf > 2 :
                                    check_lst.append('silver')
                                elif llf <= 4 and llf > 3 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                llf = 'nan'
                            # Staple — ST
                            stap = f"{staple_2}"
                            if stap != 'nan':
                                stap = float(stap)
                                if stap >= 43 :
                                    check_lst.append('Llano Super')
                                elif stap >= 38 and stap < 43 :
                                    check_lst.append('gold')
                                elif stap >= 37 and stap < 38 :
                                    check_lst.append('silver')
                                elif stap >= 36 and stap < 37 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                stap = 'nan'
                            # Strength — STR
                            streng = f"{strength_4}"
                            if streng != 'nan':
                                streng = float(streng)
                                if streng >= 33 :
                                    check_lst.append('gold')
                                elif streng >= 31 and streng < 33 :
                                    check_lst.append('silver')
                                elif streng >= 29 and streng < 31 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                streng = 'nan'
                            # Mic — MIC
                            trmic = f"{mic_new}"
                            if trmic !='nan':
                                trmic = float(trmic)
                                if trmic >= 3.7 and trmic <4.3 :
                                    check_lst.append('gold')
                                else:
                                    check_lst.append('0')
                            else:
                                trmic = 'nan'
                            # Uniformity  — UNIF
                            uniformi = f"{unif_new}"
                            if uniformi != 'nan':
                                uniformi = float(uniformi)
                                if uniformi >= 82 :
                                    check_lst.append('gold')
                                elif uniformi >= 81 and uniformi < 82 :
                                    check_lst.append('silver')
                                elif uniformi >= 80 and uniformi < 81 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                uniformi = 'nan'
                            lls = check_lst.count('Llano Super')
                            gg = check_lst.count('gold')
                            ss = check_lst.count('silver')
                            bb = check_lst.count('bronze')
                            zz = check_lst.count('0')
                            if remarks_2 != 'nan'  and remarks_2 != '  ' and  remarks_2 != None :
                                level="None"
                            elif remarks_1 != 'nan'  and remarks_1 != '  ' and  remarks_1 != None :
                                level="None"
                            else:
                                if gg>=3 and lls==1 :
                                    level="Llano Super"
                                elif gg>=4 :
                                    level="Gold"
                                elif lls+gg+ss>=4:
                                    level="Silver"
                                elif lls+gg+ss+bb>=4:
                                    level="Bronze"
                                else:
                                    level="None"
                            bale = BaleReportFarmField(upload_date=date.today(),load_id = module_trailer_no_5,rm = remarks_2 ,wh_id = Whse_code_6, ex = remarks_1,
                            ob1 = ob_new, gr = color_grade_2,pk_num = module_trailer_no_5,field_name = field_name,classing_id = classing.id, 
                            prod_id = producer_account_no_6, farm_id = farm_6,bale_id = gin_tag_7, net_wt = net_weight_3, dt_class = dt_class,
                            lf = leaf_grade_1, st = staple_2, mic = mic_new, str_no = strength_4, cgr = cgr, rd = rd_new, tr = trash_meter_2, 
                            unif = unif_new, len_num = length_in_100_3,level=level, ob2 = grower_id, ob3 = grower_name, ob4 = field_id, warehouse_wh_id= Whse_code_6)
                            bale.save()
                            balereport_save_certificate = bale.certificate()
                            bale.ob5 = balereport_save_certificate
                            bale.save()
                    
                    # 07-04-23
                    log_type, log_status, log_device = "ClassingReport", "Added", "Web"
                    log_idd, log_name = classing.id, str(classing.csv_path).replace("processor_reports/","")
                    action_by_userid = request.user.id
                    user = User.objects.get(pk=action_by_userid)
                    user_role = user.role.all()
                    action_by_username = f'{user.first_name} {user.last_name}'
                    action_by_email = user.username
                    if request.user.id == 1 :
                        action_by_role = "superuser"
                    else:
                        action_by_role = str(','.join([str(i.role) for i in user_role]))
                    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                                        action_by_email=action_by_email,action_by_role=action_by_role,
                                        log_device=log_device)
                    logtable.save()

                    return redirect ('classing_list') 
            return render (request, 'processor/classing_upload_via_dat.html', context)
        return render (request, 'processor/classing_upload_via_dat.html', context)
    elif request.user.is_processor:
        user_email = request.user.email
        p = ProcessorUser.objects.get(contact_email=user_email)
        processor_id = Processor.objects.get(id=p.processor_id).id
        grower = LinkGrowerToProcessor.objects.filter(processor_id=processor_id)
        grower_id = [i.grower_id for i in grower]
        get_grower = Grower.objects.filter(id__in = grower_id).order_by('name')
        context['get_grower'] = get_grower
        if request.method == 'POST':
            grower_id = request.POST.get('grower_id')
            if grower_id != None :
                field_id = request.POST.get('field_id')
                dat_file = request.FILES.get('dat_file')
                
                selectedgrower = Grower.objects.get(id = grower_id)
                context['selectedgrower'] = selectedgrower
                get_field = Field.objects.filter(grower_id=grower_id)
                context['get_field'] = get_field
                                
                if dat_file != None :
                    ifile  = open(dat_file.temporary_file_path(), "r")
                    read = csv.reader(ifile)
                else:
                    read = ''
                
                if processor_id != None and grower_id != None and field_id != None and dat_file != None :
                    field_name = Field.objects.get(id=field_id).name
                    grower_name = selectedgrower.name
                    classing = ClassingReport(upload_date=date.today(),processor_id = processor_id,grower_id = grower_id,
                    csv_path = dat_file, csv_type = ".dat")
                    classing.save()
                    for row in read :
                        line = row[0]
                        gin_code_5 = line[4:9]
                        gin_tag_7 = line[9:16]
                        date_classed_mdy_6 = line[16:22]
                        module_trailer_no_5 = line[23:28]
                        module_trailer_bales_2 = line[28:30]
                        color_grade_2 = line[33:35]
                        staple_2 = line[35:37]
                        govt_mic_2 = line[37:39]
                        strength_4 = line[40:44]
                        leaf_grade_1 = line[44:45]
                        remarks_1 = line[45:47]
                        remarks_2 = line[47:49]
                        color_code_2 = line[50:52]
                        color_quadrant_1 = line[52:53]
                        color_rd_no_decimal_3 = line[53:56]
                        color_plusb_3 = line[56:59]
                        trash_meter_2 = line[60:62]
                        length_in_100_3 = line[63:66]
                        uniformity_3 = line[67:70]
                        cotton_type_1 = line[70:71]
                        class_type_1 = line[71:72]
                        Whse_code_6 = line[89:95]
                        Whse_tag_7 = line[95:102]
                        gross_weight_3 = line[102:105]
                        tare_weight_2 = line[105:107]
                        net_weight_3 = line[107:110]
                        storage_date_MMDDYYYY_8 = line[112:120]
                        ginning_date_MMDDYYYY_8 = line[120:128]
                        producer_account_no_6 = line[128:134]
                        producer_lot_no_2 = line[134:136]
                        farm_6 = line[141:147]
                        bale_check = BaleReportFarmField.objects.filter(bale_id=gin_tag_7)
                        if bale_check.exists() :
                            pass
                        else:
                            # load_id , gr , ex , rm , elong, ob1
                            cgr = "{}-{}".format(color_code_2,color_quadrant_1)
                            dt_class = "{}/{}/{}".format(date_classed_mdy_6[:2],date_classed_mdy_6[2:4],date_classed_mdy_6[4:6])
                            rm = "{}{}".format(remarks_1,remarks_2) 
                            rd_new = "{}.{}".format(color_rd_no_decimal_3[:2],color_rd_no_decimal_3[2:3])
                            ob_new = "{}.{}".format(color_plusb_3[:1],color_plusb_3[1:3])
                            unif_new = "{}.{}".format(uniformity_3[:2],uniformity_3[2:3])
                            mic_new = "{}.{}".format(govt_mic_2[:1],govt_mic_2[1:2])
                            # Color — CGR
                            check_lst = []
                            clr = f"{cgr}"
                            if clr != 'nan':
                                # clr = int(float(clr[:2]))
                                clr_var = clr.split('-')
                                clr1 = int(float(clr_var[0]))
                                #if clr1 >= 11 and clr1 <= 21 :
                                if clr1 == 11 or clr1 == 21 :
                                    check_lst.append('gold')
                                elif clr1 == 31 :
                                    check_lst.append('silver')
                                elif clr1 == 41 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                clr = 'nan'
                            # Leaf — LF
                            llf = f"{leaf_grade_1}"
                            if llf != 'nan':
                                llf = int(llf[0])
                                if llf <= 2 :
                                    check_lst.append('gold')
                                elif llf <= 3 and llf > 2 :
                                    check_lst.append('silver')
                                elif llf <= 4 and llf > 3 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                llf = 'nan'
                            # Staple — ST
                            stap = f"{staple_2}"
                            if stap != 'nan':
                                stap = float(stap)
                                if stap >= 43 :
                                    check_lst.append('Llano Super')
                                elif stap >= 38 and stap < 43 :
                                    check_lst.append('gold')
                                elif stap >= 37 and stap < 38 :
                                    check_lst.append('silver')
                                elif stap >= 36 and stap < 37 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                stap = 'nan'
                            # Strength — STR
                            streng = f"{strength_4}"
                            if streng != 'nan':
                                streng = float(streng)
                                if streng >= 33 :
                                    check_lst.append('gold')
                                elif streng >= 31 and streng < 33 :
                                    check_lst.append('silver')
                                elif streng >= 29 and streng < 31 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                streng = 'nan'
                            # Mic — MIC
                            trmic = f"{mic_new}"
                            if trmic !='nan':
                                trmic = float(trmic)
                                if trmic >= 3.7 and trmic <4.3 :
                                    check_lst.append('gold')
                                else:
                                    check_lst.append('0')
                            else:
                                trmic = 'nan'
                            # Uniformity  — UNIF
                            uniformi = f"{unif_new}"
                            if uniformi != 'nan':
                                uniformi = float(uniformi)
                                if uniformi >= 82 :
                                    check_lst.append('gold')
                                elif uniformi >= 81 and uniformi < 82 :
                                    check_lst.append('silver')
                                elif uniformi >= 80 and uniformi < 81 :
                                    check_lst.append('bronze')
                                else:
                                    check_lst.append('0')
                            else:
                                uniformi = 'nan'
                            lls = check_lst.count('Llano Super')
                            gg = check_lst.count('gold')
                            ss = check_lst.count('silver')
                            bb = check_lst.count('bronze')
                            zz = check_lst.count('0')
                            if remarks_2 != 'nan'  and remarks_2 != '  ' and  remarks_2 != None :
                                level="None"
                            elif remarks_1 != 'nan'  and remarks_1 != '  ' and  remarks_1 != None :
                                level="None"
                            else:
                                if gg>=3 and lls==1 :
                                    level="Llano Super"
                                elif gg>=4 :
                                    level="Gold"
                                elif lls+gg+ss>=4:
                                    level="Silver"
                                elif lls+gg+ss+bb>=4:
                                    level="Bronze"
                                else:
                                    level="None"
                            bale = BaleReportFarmField(upload_date=date.today(),load_id = module_trailer_no_5,rm = remarks_2 ,wh_id = Whse_code_6, ex = remarks_1,
                            ob1 = ob_new, gr = color_grade_2,pk_num = module_trailer_no_5,field_name = field_name,classing_id = classing.id,
                            prod_id = producer_account_no_6, farm_id = farm_6, bale_id = gin_tag_7, net_wt = net_weight_3, dt_class = dt_class, 
                            lf = leaf_grade_1,st = staple_2, mic = mic_new, str_no = strength_4, cgr = cgr, rd = rd_new,tr = trash_meter_2, 
                            unif = unif_new, len_num = length_in_100_3, level=level, ob2 = grower_id, ob3 = grower_name, ob4 = field_id, warehouse_wh_id= Whse_code_6)
                            bale.save()
                            balereport_save_certificate = bale.certificate()
                            bale.ob5 = balereport_save_certificate
                            bale.save()

                    # 07-04-23
                    log_type, log_status, log_device = "ClassingReport", "Added", "Web"
                    log_idd, log_name = classing.id, str(classing.csv_path).replace("processor_reports/","")
                    action_by_userid = request.user.id
                    user = User.objects.get(pk=action_by_userid)
                    user_role = user.role.all()
                    action_by_username = f'{user.first_name} {user.last_name}'
                    action_by_email = user.username
                    if request.user.id == 1 :
                        action_by_role = "superuser"
                    else:
                        action_by_role = str(','.join([str(i.role) for i in user_role]))
                    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                                        action_by_email=action_by_email,action_by_role=action_by_role,log_device=log_device)
                    logtable.save()
                    return redirect ('classing_list')
        return render (request, 'processor/classing_upload_via_dat.html', context)


@login_required()
def classing_csv_list_grower(request,pk):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        var = ClassingReport.objects.get(id=pk)
        grower_id = var.grower.id
        clas = ClassingReport.objects.filter(grower_id=grower_id)
        report = BaleReportFarmField.objects.filter(classing_id__in=clas)
        # 25-01-23
        processor_obj = Processor2.objects.all()
        context['processor2'] = processor_obj
        if request.method == 'POST' :
            search_name = request.POST.get('search_name')
            processor2_id = request.POST.get('processor2_id')
            get_bale2 = request.POST.get('get_bale2')
            raw_id = request.POST.get('raw_id')
            mark_id = request.POST.get('mark_id')
            gin_id = request.POST.get('gin_id')
            if processor2_id and get_bale2 :
                check_bale2 = BaleReportFarmField.objects.filter(bale_id=get_bale2).filter(id=raw_id)
                if check_bale2.exists() :
                    # check_bale2_for_processor2 = AssignedBaleProcessor2.objects.filter(assigned_bale=get_bale2)
                    # if check_bale2_for_processor2.exists() :
                    #     assigned_bale_processor2 = AssignedBaleProcessor2.objects.get(assigned_bale=get_bale2)
                    #     assigned_bale_processor2.processor2_id = processor2_id
                    #     assigned_bale_processor2.mark_id = mark_id
                    #     assigned_bale_processor2.gin_id = gin_id
                    #     assigned_bale_processor2.save()
                        
                    # else:
                    get_bale2_processor = BaleReportFarmField.objects.get(id=raw_id)
                    assigned_bale_processor2 = AssignedBaleProcessor2(processor2_id=processor2_id,bale_id=get_bale2_processor.id,assigned_bale=get_bale2,
                    prod_id=get_bale2_processor.prod_id,wt=get_bale2_processor.wt,net_wt=get_bale2_processor.net_wt,load_id=get_bale2_processor.load_id,
                    dt_class=get_bale2_processor.dt_class,gr=get_bale2_processor.gr,lf=get_bale2_processor.lf,st=get_bale2_processor.st,mic=get_bale2_processor.mic,
                    ex=get_bale2_processor.ex,rm=get_bale2_processor.rm,str_no=get_bale2_processor.str_no,cgr=get_bale2_processor.cgr,rd=get_bale2_processor.rd,
                    tr=get_bale2_processor.tr,unif=get_bale2_processor.unif,len_num=get_bale2_processor.len_num,elong=get_bale2_processor.elong,cents_lb=get_bale2_processor.cents_lb,
                    loan_value=get_bale2_processor.loan_value,warehouse_wt=get_bale2_processor.warehouse_wt,warehouse_bale_id=get_bale2_processor.warehouse_bale_id,
                    warehouse_wh_id=get_bale2_processor.warehouse_wh_id,farm_name=get_bale2_processor.farm_name,sale_status=get_bale2_processor.sale_status,
                    wh_id=get_bale2_processor.wh_id,ob1=get_bale2_processor.ob1,gin_date=get_bale2_processor.gin_date,farm_id=get_bale2_processor.farm_id,
                    field_name=get_bale2_processor.field_name,pk_num=get_bale2_processor.pk_num,grower_idd=get_bale2_processor.ob2,grower_name=get_bale2_processor.ob3,
                    field_idd=get_bale2_processor.ob4,certificate=get_bale2_processor.ob5,value=get_bale2_processor.value,level=get_bale2_processor.level,
                    crop_variety=get_bale2_processor.crop_variety,mark_id=mark_id,gin_id=gin_id)
                    assigned_bale_processor2.save()

                    # Notification 
                    p2user_id_all1 = ProcessorUser2.objects.filter(processor2_id=processor2_id)
                    for j in p2user_id_all1 :
                        msg1 = 'New Bales are assigned to you '
                        p_user_id1 = User.objects.get(username=j.contact_email)
                        notification_reason1 = 'New Bale Assigned'
                        redirect_url1 = "/processor2/list_bale_processor2/"
                        save_notification = ShowNotification(user_id_to_show=p_user_id1.id,msg=msg1,status="UNREAD",redirect_url=redirect_url1,
                        notification_reason=notification_reason1)
                        save_notification.save()
                        
            if search_name :
                report_data = BaleReportFarmField.objects.filter(classing_id__in=clas).filter(
                Q(bale_id__icontains=search_name) | Q(field_name__icontains=search_name) | Q(farm_name__icontains=search_name)
                ).distinct()
                search_get = search_name
                context['report'] = report_data
                context['report_grower_index'] = len(report_data)
                context['search_get'] = search_get
                return render (request, 'processor/classing_csv_list.html', context)
            else :
                pass
        context['report'] = report
        context['report_grower_index'] = len(report)
        return render (request, 'processor/classing_csv_list.html', context)
    elif request.user.is_processor:
        var = ClassingReport.objects.get(id=pk)
        grower_id = var.grower.id
        clas = ClassingReport.objects.filter(grower_id=grower_id)
        report = BaleReportFarmField.objects.filter(classing_id__in=clas)
        if request.method == 'POST' :
            search_name = request.POST.get('search_name')
            if search_name :
                report_data = BaleReportFarmField.objects.filter(classing_id__in=clas).filter(
                Q(bale_id__icontains=search_name) | Q(field_name__icontains=search_name) | Q(farm_name__icontains=search_name)
                ).distinct()
                search_get = search_name
                context['report'] = report_data
                context['report_grower_index'] = len(report_data)
                context['search_get'] = search_get
                return render (request, 'processor/classing_csv_list.html', context)
            else :
                pass
        context['report'] = report
        context['report_grower_index'] = len(report)
        return render (request, 'processor/classing_csv_list.html', context)

@login_required()
def classing_csv_all(request):
    # Create the HttpResponse object with the appropriate CSV header.
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        filename = 'Classing.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        bale_all = BaleReportFarmField.objects.all()
        search_name= request.GET.get('search_name')
        grower_id= request.GET.get('grower_id')
        cerSelction= request.GET.get('cerSelction')
        lelSelction= request.GET.get('lelSelction')
        if search_name :
            bale_all = bale_all.filter( Q(bale_id__icontains=search_name) | Q(field_name__icontains=search_name) |
                                              Q(farm_name__icontains=search_name) | Q(warehouse_wh_id__icontains=search_name)).distinct()
        else:
            if grower_id :
                classing = ClassingReport.objects.values('id','grower_id')
                classing = classing.filter(grower_id=grower_id)
                classing_id = [i['id'] for i in classing]
                bale_all = bale_all.filter(classing_id__in=classing_id)
            if cerSelction :
                if cerSelction == "null" :
                    bale_all = bale_all.filter(ob5=None)
                else:
                    bale_all = bale_all.filter(ob5=cerSelction)
            if lelSelction :
                bale_all = bale_all.filter(level=lelSelction)
        print(search_name)
        print(grower_id)
        print(cerSelction)
        print(lelSelction)
        writer = csv.writer(response)
        writer.writerow(['Prod Id', 'Farm Name', 'Grower Name', 'Bale Id','Warehouse Id','Date','Net Wt','Farm Id','Load Id','Variety','Field name','Certificate','Level',
        'gr','lf','st','mic','ex','rm','str_no','cgr','rd','tr','unif','len_num','elong','loan_value','B','payment'])

        for i in bale_all:
            
            if GrowerPayments.objects.filter(grower_id = i.ob2).filter(delivery_id=i.bale_id).exists() :
                payment = 'Paid'
            else:
                payment = 'Due'
            writer.writerow([i.prod_id, i.farm_name, i.ob3, i.bale_id, i.warehouse_wh_id, i.dt_class, i.net_wt, i.farm_id, i.load_id, i.crop_variety, i.field_name, i.ob5, i.level,
            i.gr,i.lf,i.st,i.mic,i.ex,i.rm,i.str_no,i.cgr,i.rd,i.tr,i.unif,i.len_num,i.elong,i.loan_value,i.ob1,payment])

        return response
    
    elif request.user.is_processor:
        user_email = request.user.email
        p = ProcessorUser.objects.get(contact_email=user_email)
        processor_id = Processor.objects.get(id=p.processor.id).id
        cr = ClassingReport.objects.filter(processor_id=processor_id)
        rp = [i.id for i in cr]
        bale_all = BaleReportFarmField.objects.filter(classing_id__in=rp)

        filename = 'Classing.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['Prod Id', 'Farm Name', 'Grower Name', 'Bale Id','Warehouse Id','Date','Net Wt','Farm Id','Load Id','Variety','Field name','Certificate','Level',
        'gr','lf','st','mic','ex','rm','str_no','cgr','rd','tr','unif','len_num','elong','loan_value','B'])

        for i in bale_all:
            
            # if GrowerPayments.objects.filter(grower_id = i.ob2).filter(delivery_id=i.bale_id).exists() :
            #     payment = 'Paid'
            # else:
            #     payment = 'Due'
            writer.writerow([i.prod_id, i.farm_name, i.ob3, i.bale_id, i.warehouse_wh_id, i.dt_class, i.net_wt, i.farm_id, i.load_id, i.crop_variety, i.field_name, i.ob5, i.level,
            i.gr,i.lf,i.st,i.mic,i.ex,i.rm,i.str_no,i.cgr,i.rd,i.tr,i.unif,i.len_num,i.elong,i.loan_value,i.ob1])

        return response

    else:
        return redirect('/')

def grower_field_yield_variance(request):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        field = Field.objects.filter(total_yield__isnull=False).order_by('name')
        yield_variance = []
        
        fields = Field.objects.filter(total_yield__isnull=False).order_by('name')
        f_id = [i.farm.id for i in fields]
        g_id = [i.grower.id for i in fields]
        farms = Farm.objects.filter(id__in = f_id).order_by('name')
        growers = Grower.objects.filter(id__in = g_id).order_by('name')
        context['farms'] = farms
        context['fields'] = fields
        context['growers'] = growers
        context['selectedCrop'] = 'all'
        context['selectedFarm'] = 'all'
        context['selectedFarm_id'] = 'all'
        context['selectedField'] = 'all'
        context['selectedField_id'] = 'all'
        context['selectedGrower'] = 'all'
        context['selectedGrower_id'] = 'all'

        grower_crop = request.GET.get('grower_crop')
        farm_id = request.GET.get('farm_id')
        field_id = request.GET.get('field_id')
        grower_id = request.GET.get('grower_id')

        if grower_crop == None and farm_id == None and field_id == None and grower_id == None :
            field = Field.objects.filter(total_yield__isnull=False).order_by('name')
        elif grower_crop == 'all' and farm_id == 'all' and field_id == 'all' and grower_id == 'all' :
            field = Field.objects.filter(total_yield__isnull=False).order_by('name')
        else:
            field = Field.objects.filter(total_yield__isnull=False).order_by('name')

            if grower_crop != None and grower_crop != 'all' :
                field = field.filter(crop=grower_crop)
                context['selectedCrop'] = grower_crop 
                ff = field

                gg_id = [i.grower.id for i in field]
                fa_id = [i.farm.id for i in field]
                gg = Grower.objects.filter(id__in=gg_id).order_by('name')
                fa = Farm.objects.filter(id__in = fa_id).order_by('name')
                context['farms'] = fa
                context['fields'] = ff
                context['growers'] = gg

            if grower_id != None and grower_id != 'all' :
                field = field.filter(grower_id=grower_id)
                context['selectedGrower'] = Grower.objects.get(id=grower_id)
                context['selectedGrower_id'] = Grower.objects.get(id=grower_id).id
                ff = field
                
                fa_id = [i.farm.id for i in field]
                fa = Farm.objects.filter(id__in = fa_id).order_by('name')
                context['fields'] = ff
                context['farms'] = fa
                # try:
                #     context['selectedCrop'] = [i.crop for i in field][0]
                # except:
                #     context['selectedCrop'] = ''
                

            if farm_id != None and farm_id != 'all' :
                field = field.filter(farm_id=farm_id)
                context['selectedFarm'] = Farm.objects.get(id=farm_id)
                context['selectedFarm_id'] = Farm.objects.get(id=farm_id).id
                context['fields'] = field

                
            if field_id != None and field_id != 'all' :
                field = field.filter(id=field_id)
                context['selectedField'] = Field.objects.get(id=field_id)
                context['selectedField_id'] = Field.objects.get(id=field_id).id
            

        for i in field :
            if i.crop == 'COTTON' :
                bale = BaleReportFarmField.objects.filter(ob4=i.id)
                if bale.exists() :
                    projected_yeild = i.total_yield
                    reported_yeild = []
                    for j in bale :
                        var_wt = j.net_wt.strip()
                        try:
                            cotton_net_wt = float(var_wt)
                        except:
                            cotton_net_wt = 0
                        reported_yeild.append(cotton_net_wt)
                    sum_ry = float(sum(reported_yeild))
                    data = {
                        "farm":i.farm.name,
                        "field":i.name,
                        "field_idd":i.id,
                        "crop":i.crop,
                        "projected_yeild":projected_yeild,
                        "reported_yeild":sum_ry,
                        "diff":  sum_ry - projected_yeild,
                        "variance": '{0:.2f}'.format(((sum_ry - projected_yeild) / projected_yeild) * 100) ,
                    }
                    yield_variance.append(data)
                else:
                    data = {
                        "farm":i.farm.name,
                        "field":i.name,
                        "field_idd":i.id,
                        "crop":i.crop,
                        "projected_yeild":i.total_yield,
                        "reported_yeild":'N/A',
                        "diff": 'N/A',
                        "variance": 'N/A',
                    }
                    yield_variance.append(data)
            elif i.crop == 'RICE' :
                shipment = GrowerShipment.objects.filter(field=i.id).filter(status='APPROVED')
                if shipment.exists() :
                    projected_yeild = i.total_yield
                    reported_yeild = []
                    for k in shipment :
                        var_wt = k.received_amount
                        try:
                            rice_net_wt = float(var_wt)
                        except:
                            rice_net_wt = 0
                        reported_yeild.append(rice_net_wt)
                    sum_ry = float(sum(reported_yeild))
                    data = {
                        "farm":i.farm.name,
                        "field":i.name,
                        "field_idd":i.id,
                        "crop":i.crop,
                        "projected_yeild":projected_yeild,
                        "reported_yeild":sum_ry,
                        "diff":  sum_ry - projected_yeild,
                        "variance": '{0:.2f}'.format(((sum_ry - projected_yeild) / projected_yeild) * 100) ,
                    }
                    yield_variance.append(data)
                else:
                    data = {
                        "farm":i.farm.name,
                        "field":i.name,
                        "field_idd":i.id,
                        "crop":i.crop,
                        "projected_yeild":i.total_yield,
                        "reported_yeild":'N/A',
                        "diff": 'N/A',
                        "variance": 'N/A',
                    }
                    yield_variance.append(data)
        
        context['all_record'] = yield_variance

        max_variance_lst = []
        for k in yield_variance :
            max_variance_obj = k.get('variance')
            
            if max_variance_obj != 'N/A' :
                try:
                    try_max_variance_obj = float(max_variance_obj)
                except:
                    try_max_variance_obj = 0
                max_variance_lst.append(try_max_variance_obj)
        # print("max_variance_obj",max_variance_obj)
        if len(max_variance_lst) != 0 :
            max_variance = max(max_variance_lst)
            min_variance = min(max_variance_lst)
        else:
            max_variance = 100
            min_variance = -100
        if abs(max_variance) > abs(min_variance) :
            context['max_min'] = max_variance * 1.2
        else:
            context['max_min'] = abs(min_variance) * 1.2

        paginator = Paginator(yield_variance, 100)
        page = request.GET.get('page')
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)
        context['yield_variance'] = report
        return render (request, 'processor/grower_field_yield_variance.html', context)

def grower_field_yield_variance_download(request,selectedCrop,selectedFarm_id,selectedField_id,selectedGrower_id):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        filename = 'Grower Yield Variance.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['FARM', 'FIELD', 'GROWER', 'CROP', 'PROJECTED YIELD (LBS)','REPORTED YIELD (LBS)','DIFFERENCE','DEVIATION %'])

        if selectedCrop == 'all' and selectedFarm_id == 'all' and selectedField_id == 'all' and selectedGrower_id == 'all' :
            field = Field.objects.filter(total_yield__isnull=False).order_by('name')

        else:
            field = Field.objects.filter(total_yield__isnull=False).order_by('name')

            if selectedCrop != None and selectedCrop != 'all' :
                field = field.filter(crop=selectedCrop)
                
            if selectedFarm_id != None and selectedFarm_id != 'all' :
                id_farm = Farm.objects.get(id=selectedFarm_id)
                field = field.filter(farm_id=id_farm.id)

            if selectedField_id != None and selectedField_id != 'all' :
                field = field.filter(id=selectedField_id)

            if selectedGrower_id != None and selectedGrower_id != 'all' :
                id_grower = Grower.objects.get(id=selectedGrower_id)
                field = field.filter(grower_id=id_grower.id)

        for i in field :
            if i.crop == 'COTTON' :
                bale = BaleReportFarmField.objects.filter(ob4=i.id)
                if bale.exists() :
                    projected_yeild = i.total_yield
                    reported_yeild = []
                    for j in bale :
                        var_wt = j.net_wt.strip()
                        try:
                            cotton_net_wt = float(var_wt)
                        except:
                            cotton_net_wt = 0
                        reported_yeild.append(cotton_net_wt)
                    sum_ry = float(sum(reported_yeild))

                    writer.writerow([i.farm.name, i.name, i.grower.name, i.crop, projected_yeild, sum_ry, sum_ry - projected_yeild, '{0:.2f}'.format(((sum_ry - projected_yeild) / projected_yeild) * 100)])
                else:
                    writer.writerow([i.farm.name, i.name, i.grower.name, i.crop, i.total_yield, 'N/A', 'N/A', 'N/A'])
            elif i.crop == 'RICE' :
                shipment = GrowerShipment.objects.filter(field=i.id).filter(status='APPROVED')
                if shipment.exists() :
                    projected_yeild = i.total_yield
                    reported_yeild = []
                    for k in shipment :
                        var_wt = k.received_amount
                        try:
                            rice_net_wt = float(var_wt)
                        except:
                            rice_net_wt = 0
                        reported_yeild.append(rice_net_wt)
                    sum_ry = float(sum(reported_yeild))
                    writer.writerow([i.farm.name, i.name, i.grower.name, i.crop, projected_yeild, sum_ry, sum_ry - projected_yeild, '{0:.2f}'.format(((sum_ry - projected_yeild) / projected_yeild) * 100)])
                else:

                    writer.writerow([i.farm.name, i.name, i.grower.name, i.crop, i.total_yield, 'N/A', 'N/A', 'N/A'])

        return response

def classing_csv_all_level_check(request):
    bale_all = BaleReportFarmField.objects.all()
    for i in bale_all:
        get_check = i.get_check()
        bale = BaleReportFarmField.objects.get(id=i.id)
        bale.level = get_check
        bale.save()
        
    return HttpResponse("Level Updated Successfully")

def classing_csv_all_certificate_check(request):
    sustain = Field.objects.all()
    for i in sustain :
        grower_id = i.grower.id
        field_id = i.id
        composite_score = i.get_composite_score()
        crop = i.crop
        if crop == 'RICE':
            if composite_score >= 70:
                certificate = "Pass"
            elif composite_score < 70 :
                certificate = "Fail"
            else:
                certificate = 'N/A'
        if crop == 'COTTON':
            if composite_score >= 75:
                certificate = "Pass"
            elif composite_score < 75 :
                certificate = "Fail"
            else:
                certificate = 'N/A'
        
        if len(CertificateCalc.objects.filter(grower_id=grower_id,field_id=field_id)) > 0 :
            cvar = CertificateCalc.objects.filter(grower_id=grower_id,field_id=field_id)
            cvar_id = [i.id for i in cvar][0]
            var2 = CertificateCalc.objects.get(id=cvar_id)
            var2.certificate = certificate
            var2.save()
        else:
            CertificateCalc(grower_id=grower_id,field_id=field_id,certificate=certificate).save()
        
        classing_cert = BaleReportFarmField.objects.filter(ob2=grower_id).filter(ob4=field_id)
        
        for j in classing_cert :
            var = BaleReportFarmField.objects.get(id = j.id)
            var.ob5 = certificate
            var.save()
    
    return HttpResponse("Certificate Updated Successfully")

# def classing_ajax_list(request):
#     context = {}
#     pt = BaleReportFarmField.objects.all()[:100]
#     lst = []
#     for i in pt:
#         bale = BaleReportFarmField.objects.get(id=i.id)
#         certificate = bale.certificate()
#         level = bale.get_check()
#         data = {
#             "iid":i.id,
#             "farm_name":i.farm_name,
#             "grower_name":i.classing.grower.name,
#             "bale_id":i.bale_id,
#             "warehouse_wt":i.warehouse_wt,
#             "dt_class":i.dt_class,
#             "net_wt":i.net_wt,
#             "field_name":i.field_name,
#             "certificate":certificate,
#             "level":level,
#             "value":i.value,
#             "csv_type":i.classing.csv_type,
#         }
#         lst.append(data)
#     responce = {"data":lst}
#     return JsonResponse(responce)
def classing_csv_all_crop_variety_check(request):
    bale = BaleReportFarmField.objects.all()
    for i in bale :
        field_id = i.ob4
        if field_id :
            ff = Field.objects.get(id=int(field_id))
            crop_variety = ff.variety
            update_c = BaleReportFarmField.objects.get(id=i.id)
            update_c.crop_variety = crop_variety
            update_c.save()
    return HttpResponse("Updated Crop ")

def classing_report_update(request):
    bale = BaleReportFarmField.objects.all()
    for i in bale :
        grower_id = i.classing.grower.id
        grower_name = i.classing.grower.name
        update_c = BaleReportFarmField.objects.get(id=i.id)
        update_c.ob2 = grower_id
        update_c.ob3 = grower_name
        update_c.save()
    return HttpResponse("Updated")


def classing_csv_all_warehouse_wh_id_update(request):
    bale = BaleReportFarmField.objects.filter(warehouse_wh_id__isnull = True).filter(wh_id__isnull = False)
    for i in bale :
        update_c = BaleReportFarmField.objects.get(id=i.id)
        update_c.warehouse_wh_id = i.wh_id
        update_c.save()
    return HttpResponse("Updated")

@login_required()
def inbound_production_mgmt(request):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        output = ProductionManagement.objects.all().order_by('processor_e_name','-id')
        p_id = [i.processor.id for i in output]
        processors = Processor.objects.filter(id__in = p_id).order_by('entity_name')
        context['processors'] = processors
        
        search_name = request.GET.get('search_name')
        selectprocessor_id = request.GET.get('selectprocessor_id')

        if search_name == None and selectprocessor_id == None :
            output = output
        else:
            output = ProductionManagement.objects.filter(id__isnull=False).order_by('processor_e_name','-id')
            if search_name and search_name != 'All':
                output = ProductionManagement.objects.filter(Q(processor_e_name__icontains=search_name) | Q(date_pulled__icontains=search_name) |
                Q(bin_location__icontains=search_name) | Q(milled_storage_bin__icontains=search_name) )
                context['search_name'] = search_name
            if selectprocessor_id and selectprocessor_id != 'All':
                output = output.filter(processor_id=selectprocessor_id)
                selectedProcessors = Processor.objects.get(id=selectprocessor_id)
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
        return render (request, 'processor/inbound_production_mgmt.html', context)
    elif request.user.is_processor :
        user_email = request.user.email
        p = ProcessorUser.objects.get(contact_email=user_email)
        processor_id = Processor.objects.get(id=p.processor.id).id
        output = ProductionManagement.objects.filter(processor_id=processor_id).order_by('processor_e_name','-id')
        search_name = request.GET.get('search_name')
        if search_name and search_name != 'All':
            output = ProductionManagement.objects.filter(Q(date_pulled__icontains=search_name) |
            Q(bin_location__icontains=search_name) | Q(milled_storage_bin__icontains=search_name) )
            context['search_name'] = search_name
        else:
            pass

        paginator = Paginator(output, 100)
        page = request.GET.get('page')
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)

        context['report'] = report
        return render (request, 'processor/inbound_production_mgmt.html', context)
    else:
        return redirect ('/')


@login_required()
def add_volume_pulled(request):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        get_processor = Processor.objects.all().order_by('entity_name')
        context['get_processor'] = get_processor
        if request.method == 'POST' :
            id_processor = request.POST.get('id_processor')
            if id_processor and id_processor != "all" :
                total_receive_weight = []
                total_volume_pulled_till_now = []
                shipment = GrowerShipment.objects.filter(processor_id = id_processor).filter(status ="APPROVED").filter(crop ="RICE").values('received_amount')
            
                if shipment.exists() :
                    for i in shipment :
                        try:
                            total_receive_weight.append(float(i['received_amount']))
                        except:
                            total_receive_weight.append(float(0))
                    total_receive_weight = sum(total_receive_weight)

                    volume_pulled_till_now = ProductionManagement.objects.filter(processor_id = id_processor).values('volume_pulled')
                    for i in volume_pulled_till_now :
                        total_volume_pulled_till_now.append(float(i['volume_pulled']))
                    
                    sum_volume_pulled_till_now = sum(total_volume_pulled_till_now)
                    final_total_volume = total_receive_weight - sum_volume_pulled_till_now
                else:
                    final_total_volume = 0
                    total_volume_pulled_till_now = 0
                    total_receive_weight = 0

                
                pp = Processor.objects.get(id=id_processor)
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
                    save_production_management=ProductionManagement(processor_id=id_processor,processor_e_name=pp.entity_name,
                    total_volume=final_total_volume,date_pulled=id_date,bin_location=bin_location,volume_pulled=volume_pulled,
                    milled_volume=milled_volume,volume_left=volume_left,milled_storage_bin=milled_storage_bin,editable_obj=True)
                    save_production_management.save()
                    # 20-04-23 LogTable
                    log_type, log_status, log_device = "ProductionManagement", "Added", "Web"
                    log_idd, log_name = save_production_management.id, save_production_management.milled_storage_bin
                    log_details = f"processor = {save_production_management.processor.entity_name} | processor_id = {save_production_management.processor.id} | total_volume = {save_production_management.total_volume} | date_pulled = {save_production_management.date_pulled} | bin_location = {save_production_management.bin_location} | volume_pulled = {save_production_management.volume_pulled} | milled_volume = {save_production_management.milled_volume} | volume_left = {save_production_management.volume_left} | milled_storage_bin = {save_production_management.milled_storage_bin} | editable_obj = {save_production_management.editable_obj} "
                    action_by_userid = request.user.id
                    user = User.objects.get(pk=action_by_userid)
                    user_role = user.role.all()
                    action_by_username = f'{user.first_name} {user.last_name}'
                    action_by_email = user.username
                    if request.user.id == 1 :
                        action_by_role = "superuser"
                    else:
                        action_by_role = str(','.join([str(i.role) for i in user_role]))
                    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                                        action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                        log_device=log_device)
                    logtable.save()

                    update_obj = ProductionManagement.objects.filter(processor_id=id_processor).exclude(id=save_production_management.id).values('id','editable_obj')
                    # 20-02-23 
                    puser_id_all1 = ProcessorUser.objects.filter(processor_id=id_processor)
                    for j in puser_id_all1 :
                        msg1 = f'Amount of {volume_pulled} lbs is pulled from {bin_location}. '
                        p_user_id1 = User.objects.get(username=j.contact_email)
                        notification_reason1 = 'Production Mgmt - New Volume Pulled'
                        redirect_url1 = "/processor/inbound_production_mgmt"
                        save_notification = ShowNotification(user_id_to_show=p_user_id1.id,msg=msg1,status="UNREAD",redirect_url=redirect_url1,
                        notification_reason=notification_reason1)
                        save_notification.save()

                    # save_noti = ShowNotification 
                    if update_obj.exists():
                        for i in update_obj :
                            get_obj = ProductionManagement.objects.get(id=i['id'])
                            get_obj.editable_obj = False
                            get_obj.save()
                    else:
                        pass
                    return redirect ('inbound_production_mgmt')
            else:
                pass
        return render (request, 'processor/add_volume_pulled.html', context)
    elif request.user.is_processor :
        user_email = request.user.email
        p = ProcessorUser.objects.get(contact_email=user_email)
        processor_id = Processor.objects.get(id=p.processor.id).id
        shipment = GrowerShipment.objects.filter(processor_id = processor_id).filter(status ="APPROVED").filter(crop ="RICE").values('received_amount')
        total_receive_weight = []
        total_volume_pulled_till_now = []
        if shipment.exists() :
            for i in shipment :
                try:
                    total_receive_weight.append(float(i['received_amount']))
                except:
                    total_receive_weight.append(float(0))
            total_receive_weight = sum(total_receive_weight)
        else:
            final_total_volume = 0
            total_volume_pulled_till_now = 0
            total_receive_weight = 0


        volume_pulled_till_now = ProductionManagement.objects.filter(processor_id = processor_id).values('volume_pulled')
        for i in volume_pulled_till_now :
            total_volume_pulled_till_now.append(float(i['volume_pulled']))
        
        try:
            sum_volume_pulled_till_now = sum(total_volume_pulled_till_now)
        except:
            sum_volume_pulled_till_now = 0
        
        final_total_volume = total_receive_weight - sum_volume_pulled_till_now
        context['total_receive_weight'] = f'{final_total_volume} LBS'
        context['total_receive_weight_java'] = final_total_volume
        
        id_date = request.POST.get('id_date')
        bin_location = request.POST.get('bin_location')
        volume_pulled = request.POST.get('volume_pulled')
        milled_volume = request.POST.get('milled_volume')
        milled_storage_bin = request.POST.get('milled_storage_bin')
        if volume_pulled and id_date and milled_volume :
            volume_left = float(final_total_volume) - float(volume_pulled)
            processor_e_name = Processor.objects.get(id=processor_id).entity_name
            save_production_management=ProductionManagement(processor_id=processor_id,processor_e_name=processor_e_name,
            total_volume=final_total_volume,date_pulled=id_date,bin_location=bin_location,volume_pulled=volume_pulled,
            milled_volume=milled_volume,volume_left=volume_left,milled_storage_bin=milled_storage_bin,editable_obj=True)
            save_production_management.save()
            # 20-04-23 LogTable
            log_type, log_status, log_device = "ProductionManagement", "Added", "Web"
            log_idd, log_name = save_production_management.id, save_production_management.milled_storage_bin
            log_details = f"processor = {save_production_management.processor.entity_name} | processor_id = {save_production_management.processor.id} | total_volume = {save_production_management.total_volume} | date_pulled = {save_production_management.date_pulled} | bin_location = {save_production_management.bin_location} | volume_pulled = {save_production_management.volume_pulled} | milled_volume = {save_production_management.milled_volume} | volume_left = {save_production_management.volume_left} | milled_storage_bin = {save_production_management.milled_storage_bin} | editable_obj = {save_production_management.editable_obj} "
            action_by_userid = request.user.id
            user = User.objects.get(pk=action_by_userid)
            user_role = user.role.all()
            action_by_username = f'{user.first_name} {user.last_name}'
            action_by_email = user.username
            if request.user.id == 1 :
                action_by_role = "superuser"
            else:
                action_by_role = str(','.join([str(i.role) for i in user_role]))
            logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                action_by_userid=action_by_userid,action_by_username=action_by_username,
                                action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                log_device=log_device)
            logtable.save()
            update_obj = ProductionManagement.objects.filter(processor_id=processor_id).exclude(id=save_production_management.id).values('id','editable_obj')
                    
            if update_obj.exists():
                for i in update_obj :
                    get_obj = ProductionManagement.objects.get(id=i['id'])
                    get_obj.editable_obj = False
                    get_obj.save()
            else:
                pass
            return redirect ('inbound_production_mgmt')
        return render (request, 'processor/add_volume_pulled.html', context)
    else:
        return redirect ('/')


@login_required()
def edit_volume_pulled(request,pk):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        get_obj = ProductionManagement.objects.get(id=pk)
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

                    # 20-04-23 LogTable
                    log_type, log_status, log_device = "ProductionManagement", "Edited", "Web"
                    log_idd, log_name = get_obj.id, get_obj.milled_storage_bin
                    log_details = f"processor = {get_obj.processor.entity_name} | processor_id = {get_obj.processor.id} | total_volume = {get_obj.total_volume} | date_pulled = {get_obj.date_pulled} | bin_location = {get_obj.bin_location} | volume_pulled = {get_obj.volume_pulled} | milled_volume = {get_obj.milled_volume} | volume_left = {get_obj.volume_left} | milled_storage_bin = {get_obj.milled_storage_bin} | editable_obj = {get_obj.editable_obj} "
                    action_by_userid = request.user.id
                    user = User.objects.get(pk=action_by_userid)
                    user_role = user.role.all()
                    action_by_username = f'{user.first_name} {user.last_name}'
                    action_by_email = user.username
                    if request.user.id == 1 :
                        action_by_role = "superuser"
                    else:
                        action_by_role = str(','.join([str(i.role) for i in user_role]))
                    logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                        action_by_userid=action_by_userid,action_by_username=action_by_username,
                                        action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                        log_device=log_device)
                    logtable.save()

                    # Notification
                    id_processor = get_obj.processor.id
                    puser_id_all1 = ProcessorUser.objects.filter(processor_id=id_processor)
                    for j in puser_id_all1 :
                        msg1 = f'Amount of {volume_pulled} lbs is edited in {bin_location}.'
                        p_user_id1 = User.objects.get(username=j.contact_email)
                        notification_reason1 = 'Production Mgmt - Volume Pulled Edited'
                        redirect_url1 = "/processor/inbound_production_mgmt"
                        save_notification = ShowNotification(user_id_to_show=p_user_id1.id,msg=msg1,status="UNREAD",redirect_url=redirect_url1,
                        notification_reason=notification_reason1)
                        save_notification.save()
                    return redirect ('inbound_production_mgmt')
        else:
            messages.error(request,'This is not a valid request')
        return render (request, 'processor/edit_volume_pulled.html', context)


@login_required()
def delete_volume_pulled(request,pk):
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        get_obj = ProductionManagement.objects.get(id=pk)
        volume_pulled = get_obj.volume_pulled
        bin_location = get_obj.bin_location
        processor_id = get_obj.processor_id
        # 20-04-23 LogTable
        log_type, log_status, log_device = "ProductionManagement", "Deleted", "Web"
        log_idd, log_name = get_obj.id, get_obj.milled_storage_bin
        log_details = f"processor = {get_obj.processor.entity_name} | processor_id = {get_obj.processor.id} | total_volume = {get_obj.total_volume} | date_pulled = {get_obj.date_pulled} | bin_location = {get_obj.bin_location} | volume_pulled = {get_obj.volume_pulled} | milled_volume = {get_obj.milled_volume} | volume_left = {get_obj.volume_left} | milled_storage_bin = {get_obj.milled_storage_bin} | editable_obj = {get_obj.editable_obj} "
        action_by_userid = request.user.id
        user = User.objects.get(pk=action_by_userid)
        user_role = user.role.all()
        action_by_username = f'{user.first_name} {user.last_name}'
        action_by_email = user.username
        if request.user.id == 1 :
            action_by_role = "superuser"
        else:
            action_by_role = str(','.join([str(i.role) for i in user_role]))
        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                            action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                            log_device=log_device)
        logtable.save()
        get_obj.delete()

        # Notification
        puser_id_all1 = ProcessorUser.objects.filter(processor_id=processor_id)
        for j in puser_id_all1 :
            msg1 = f'Amount of {volume_pulled} lbs of {bin_location} is deleted.'
            p_user_id1 = User.objects.get(username=j.contact_email)
            notification_reason1 = 'Production Mgmt - Volume Pulled Deleted'
            redirect_url1 = "/processor/inbound_production_mgmt"
            save_notification = ShowNotification(user_id_to_show=p_user_id1.id,msg=msg1,status="UNREAD",redirect_url=redirect_url1,
            notification_reason=notification_reason1)
            save_notification.save()

        update_obj = ProductionManagement.objects.filter(processor_id=processor_id).order_by('id').values('id')

        if update_obj.exists() :
            last_obj_id = [i['id'] for i in update_obj][-1]
            now_update_one = ProductionManagement.objects.get(id=last_obj_id)
            now_update_one.editable_obj = True
            now_update_one.save()

            now_update_all = ProductionManagement.objects.filter(processor_id=processor_id).exclude(id=last_obj_id)
            for i in now_update_all :
                make_uneditale = ProductionManagement.objects.get(id=i.id)
                make_uneditale.editable_obj = False
                make_uneditale.save()
        else:
            pass
        
        return HttpResponse (1)

@login_required()
def inbound_production_mgmt_csv_download(request):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        filename = 'PRODUCTION MANAGEMENT.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['PROCESSOR', 'DATE PULLED', 'BIN LOCATION', 'TOTAL VOLUME', 'VOLUME PULLED','MILLED VOLUME','VOLUME LEFT','MILLED STORAGE BIN'])
        output = ProductionManagement.objects.all()
        for i in output:
            
            writer.writerow([i.processor_e_name, i.date_pulled, i.bin_location, i.total_volume, i.volume_pulled, i.milled_volume, 
            i.volume_left, i.milled_storage_bin])
        return response

    elif request.user.is_processor :
        user_email = request.user.email
        p = ProcessorUser.objects.get(contact_email=user_email)
        processor_id = Processor.objects.get(id=p.processor.id).id
        entity_name = Processor.objects.get(id=processor_id).entity_name
        output = ProductionManagement.objects.filter(processor_id=processor_id)
        filename = f'PRODUCTION MANAGEMENT_{entity_name}.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['PROCESSOR', 'DATE PULLED', 'BIN LOCATION', 'TOTAL VOLUME', 'VOLUME PULLED','MILLED VOLUME','VOLUME LEFT','MILLED STORAGE BIN'])
        for i in output:
            
            writer.writerow([i.processor_e_name, i.date_pulled, i.bin_location, i.total_volume, i.volume_pulled, i.milled_volume, 
            i.volume_left, i.milled_storage_bin])
        return response



@login_required()
def outbound_shipment_mgmt(request):
    context ={}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        output = ShipmentManagement.objects.all().order_by('bin_location','id')
        
        p_id = [i.processor_idd for i in output]
        processors = Processor.objects.filter(id__in = p_id).order_by('entity_name')
        context['processors'] = processors

        search_name = request.GET.get('search_name')
        selectprocessor_id = request.GET.get('selectprocessor_id')

        if search_name == None and selectprocessor_id == None :
            output = output
        else:
            output = ShipmentManagement.objects.filter(id__isnull=False).order_by('bin_location','id')
            if search_name and search_name != 'All':
                output = ShipmentManagement.objects.filter(Q(processor_e_name__icontains=search_name) | Q(date_pulled__icontains=search_name) |
                Q(bin_location__icontains=search_name) | Q(equipment_type__icontains=search_name) | Q(equipment_id__icontains=search_name) | 
                Q(purchase_order_number__icontains=search_name) | Q(lot_number__icontains=search_name))
                context['search_name'] = search_name
            if selectprocessor_id and selectprocessor_id != 'All':
                output = output.filter(processor_idd=selectprocessor_id)
                selectedProcessors = Processor.objects.get(id=selectprocessor_id)
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
        return render (request, 'processor/outbound_shipment_mgmt.html', context)
    # this is for Processor
    elif request.user.is_processor :
        user_email = request.user.email
        p = ProcessorUser.objects.get(contact_email=user_email)
        processor_id = Processor.objects.get(id=p.processor.id).id
        output = ShipmentManagement.objects.filter(processor_idd=processor_id).order_by('bin_location')
        
        p_id = [i.processor_idd for i in output]
        # print("processor_id=================================",processor_id)
        processors = Processor.objects.filter(id__in =p_id ).order_by('entity_name')
        context['processors'] = processors
        selectprocessor_id = request.GET.get('selectprocessor_id')
        # print("selectprocessor_id=================================",selectprocessor_id)

        if selectprocessor_id != None:
            context['processors'] = processors
            context['selectedProcessors'] = Processor.objects.get(id=processor_id)
        else:
            context['processors'] = processors
            
        search_name = request.GET.get('search_name')
        if search_name == None :
            output = output
        else:
            output = output
            if search_name and search_name != 'All':
                output = output.filter(Q(processor_e_name__icontains=search_name) | Q(date_pulled__icontains=search_name) |
                Q(bin_location__icontains=search_name) | Q(equipment_type__icontains=search_name) | Q(equipment_id__icontains=search_name) | 
                Q(purchase_order_number__icontains=search_name) | Q(lot_number__icontains=search_name))
                context['search_name'] = search_name
            else:
                pass
        paginator = Paginator(output, 100)
        page = request.GET.get('page')
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)

        context['report'] = report
        return render (request, 'processor/outbound_shipment_mgmt.html', context)


@login_required()
def outbound_shipment_mgmt_view(request,pk):
    try:
        context ={}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            processor_id = Processor.objects.get(id=pk)
            output = ShipmentManagement.objects.filter(id=pk).order_by('bin_location')
            report = output
            context['report'] = report
            return render (request, 'processor/outbound_shipment_mgmt_view_page.html', context)
        
        # this is for Processor
        elif request.user.is_processor :
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor.id).id
            # Check if pk exists in the processor's data
            if ShipmentManagement.objects.filter(processor_idd=processor_id, id=pk).exists():
                output = ShipmentManagement.objects.filter(id=pk).order_by('bin_location')
                context['report'] = output
                return render(request, 'processor/outbound_shipment_mgmt_view_page.html', context)
            else:
                return render(request, 'processor/outbound_shipment_mgmt_view_page.html', context)
        else:
            return redirect('login')  
    except:
        return render (request, 'processor/outbound_shipment_mgmt_view_page.html')   



@login_required()
def add_outbound_shipment(request):
    try:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            
            processor= ProcessorUser.objects.all().values("processor__entity_name").order_by('processor__entity_name')
            # auto complete suggestion
            get_entity_nm = [i["processor__entity_name"] for i in processor]
            lst = list(set(get_entity_nm))
            # print("lst--------------------------------------",type(lst))
            select_search_json = json.dumps(lst)
            context['select_search_json'] = select_search_json
            
            if request.method == 'POST' :
                id_bin_location_pull = request.POST.get('id_bin_location_pull')
                # print("id_bin_location_pull==================",id_bin_location_pull)
                # get_bin_location = ProductionManagement.objects.filter(milled_storage_bin=id_bin_location_pull).values('milled_volume','id','processor_id','processor_e_name')
                get_bin_location = ProductionManagement.objects.filter(processor_e_name=id_bin_location_pull).values('milled_volume','id','processor_id','processor_e_name')
                # print("get_bin_location============================",get_bin_location)
                if id_bin_location_pull and get_bin_location.exists() :
                    total_bin_location_milled_volume = []
                    total_shiped_volume = []
                    for i in get_bin_location :
                        total_bin_location_milled_volume.append(float(i['milled_volume']))

                    shiped_volume = ShipmentManagement.objects.filter(bin_location=id_bin_location_pull).values('volume_shipped')
                    for i in shiped_volume :
                        total_shiped_volume.append(float(i['volume_shipped']))

                    sum_total__volume = sum(total_bin_location_milled_volume)
                    sum_shiped_volume = sum(total_shiped_volume)
                    sum_total_bin_location_milled_volume = float(sum_total__volume) - float(sum_shiped_volume)
                    context['id_bin_location_pull'] = id_bin_location_pull
                    context['sum_total_bin_location_milled_volume'] = f'{sum_total_bin_location_milled_volume} Lbs'
                    context['sum_total_bin_location_milled_volume_java'] = sum_total_bin_location_milled_volume
                    
                    id_date = request.POST.get('id_date')
                    equipment_type = request.POST.get('equipment_type')
                    equipment_id = request.POST.get('equipment_id')
                    storage_bin_id = request.POST.get('storage_bin_id')
                    weight_prod = request.POST.get('weight_prod')
                    exp_yield = request.POST.get('exp_yield')
                    moist_percentage = request.POST.get('moist_percentage')
                    weight_prod_unit_id = request.POST.get('weight_prod_unit_id')
                    exp_yield_unit_id = request.POST.get('exp_yield_unit_id')
                    purchase_number = request.POST.get('purchase_number')
                    lot_number = request.POST.get('lot_number')
                    volume_shipped = request.POST.get('volume_shipped')
                    
                    if id_date and volume_shipped and get_bin_location.exists() :
                        
                        bin_location = id_bin_location_pull
                        processor_id = [i['processor_id'] for i in get_bin_location][0]
                        processor_e_name = [i['processor_e_name'] for i in get_bin_location][0]
                        milled_volume = sum_total_bin_location_milled_volume
                        volume_left = float(milled_volume) - float(volume_shipped)
                        if equipment_type and equipment_type != "All" :
                            equipment_type = equipment_type
                        else:
                            equipment_type = None
                        if weight_prod_unit_id == "LBS" :
                            cal_weight = round(float(weight_prod),2)
                        if weight_prod_unit_id == "BU" :
                            cal_weight = round(float(weight_prod) * 45,2)
                        if exp_yield_unit_id == "LBS" :
                            cal_exp_yield = round(float(exp_yield),2)
                        if exp_yield_unit_id == "BU" :
                            cal_exp_yield = round(float(exp_yield) * 45,2)
                        save_shipment_management = ShipmentManagement(processor_idd=processor_id,processor_e_name=processor_e_name,bin_location=bin_location,
                        date_pulled=id_date,equipment_type=equipment_type,equipment_id=equipment_id,storage_bin=storage_bin_id,moisture_percent = moist_percentage,weight_of_product_raw = weight_prod,weight_of_product=cal_weight,weight_of_product_unit=weight_prod_unit_id, excepted_yield_raw = exp_yield,excepted_yield=cal_exp_yield,excepted_yield_unit=exp_yield_unit_id,   purchase_order_number=purchase_number,
                        lot_number=lot_number,volume_shipped=volume_shipped,milled_volume=milled_volume,volume_left=volume_left,editable_obj=True)
                        save_shipment_management.save()
                        
                        # 20-04-23 LogTable
                        log_type, log_status, log_device = "ShipmentManagement", "Added", "Web"
                        log_idd, log_name = save_shipment_management.id, save_shipment_management.bin_location
                        log_details = f"processor = {save_shipment_management.processor_e_name} | processor_id = {save_shipment_management.processor_idd} | date_pulled = {save_shipment_management.date_pulled} | bin_location = {save_shipment_management.bin_location} | milled_volume = {save_shipment_management.milled_volume} | equipment_type = {save_shipment_management.equipment_type} | equipment_id = {save_shipment_management.equipment_id} | purchase_order_number = {save_shipment_management.purchase_order_number} | lot_number = {save_shipment_management.lot_number} | volume_shipped = {save_shipment_management.volume_shipped} | volume_left = {save_shipment_management.volume_left} | editable_obj = {save_shipment_management.editable_obj} "
                        action_by_userid = request.user.id
                        user = User.objects.get(pk=action_by_userid)
                        user_role = user.role.all()
                        action_by_username = f'{user.first_name} {user.last_name}'
                        action_by_email = user.username
                        if request.user.id == 1 :
                            action_by_role = "superuser"
                        else:
                            action_by_role = str(','.join([str(i.role) for i in user_role]))
                        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                                            action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                            log_device=log_device)
                        logtable.save()
                        update_obj = ShipmentManagement.objects.filter(processor_idd=processor_id).exclude(id=save_shipment_management.id).values('id','editable_obj')
                            
                        if update_obj.exists():
                            for i in update_obj :
                                get_obj = ShipmentManagement.objects.get(id=i['id'])
                                get_obj.editable_obj = False
                                get_obj.save()
                        else:
                            pass
                        return redirect ('outbound_shipment_mgmt')

                else:
                    messages.error(request,"Bin Location Pulled from not exists")
                    context['id_bin_location_pull'] = id_bin_location_pull
                    context['sum_total_bin_location_milled_volume'] = f'0 Lbs'
                    context['sum_total_bin_location_milled_volume_java'] = 0

            return render (request, 'processor/add_outbound_shipment.html', context)
        elif request.user.is_processor :
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor.id).id
            check_p_entity_name = Processor.objects.get(id=p.processor.id).entity_name

            id_bin_location_pull = check_p_entity_name
            # print("id_bin_location_pull--------------------------------",id_bin_location_pull)
            context['id_bin_location_pull'] = id_bin_location_pull
            
            if request.method == 'POST'  and id_bin_location_pull != None :
                # id_bin_location_pull = request.POST.get('id_bin_location_pull')
                # context['id_bin_location_pull'] = id_bin_location_pull
                # get_bin_location = ProductionManagement.objects.filter(milled_storage_bin=id_bin_location_pull).values('milled_volume','id','processor_id','processor_e_name')
                get_bin_location = ProductionManagement.objects.filter(processor_e_name=id_bin_location_pull).values('milled_volume','id','processor_id','processor_e_name')
                if id_bin_location_pull and get_bin_location.exists() :
                    try:
                        check_p_bin_location  = [i['processor_e_name'] for i in get_bin_location][0]
                    except:
                        check_p_bin_location  = [i['processor_e_name'] for i in get_bin_location]
                    if get_bin_location.exists() and check_p_bin_location ==  check_p_entity_name :
                        total_bin_location_milled_volume = []
                        total_shiped_volume = []
                        for i in get_bin_location :
                            total_bin_location_milled_volume.append(float(i['milled_volume']))


                        shiped_volume = ShipmentManagement.objects.filter(bin_location=id_bin_location_pull).values('volume_shipped')
                        for i in shiped_volume :
                            total_shiped_volume.append(float(i['volume_shipped']))

                        sum_total__volume = sum(total_bin_location_milled_volume)
                        sum_shiped_volume = sum(total_shiped_volume)
                        sum_total_bin_location_milled_volume = float(sum_total__volume) - float(sum_shiped_volume)
            
                        context['sum_total_bin_location_milled_volume'] = f'{sum_total_bin_location_milled_volume} Lbs'
                        context['sum_total_bin_location_milled_volume_java'] = sum_total_bin_location_milled_volume

                        id_date = request.POST.get('id_date')
                        equipment_type = request.POST.get('equipment_type')
                        equipment_id = request.POST.get('equipment_id')
                        purchase_number = request.POST.get('purchase_number')
                        lot_number = request.POST.get('lot_number')
                        volume_shipped = request.POST.get('volume_shipped')
                        if id_date and volume_shipped and get_bin_location.exists() :
                        
                            bin_location = id_bin_location_pull
                            processor_id = [i['processor_id'] for i in get_bin_location][0]
                            processor_e_name = [i['processor_e_name'] for i in get_bin_location][0]
                            milled_volume = sum_total_bin_location_milled_volume
                            volume_left = float(milled_volume) - float(volume_shipped)
                            if equipment_type and equipment_type != "All" :
                                equipment_type = equipment_type
                            else:
                                equipment_type = None

                            save_shipment_management = ShipmentManagement(processor_idd=processor_id,processor_e_name=processor_e_name,bin_location=bin_location,
                            date_pulled=id_date,equipment_type=equipment_type,equipment_id=equipment_id,purchase_order_number=purchase_number,
                            lot_number=lot_number,volume_shipped=volume_shipped,milled_volume=milled_volume,volume_left=volume_left,editable_obj=True)
                            save_shipment_management.save()
                            # 20-04-23 LogTable
                            log_type, log_status, log_device = "ShipmentManagement", "Added", "Web"
                            log_idd, log_name = save_shipment_management.id, save_shipment_management.bin_location
                            log_details = f"processor = {save_shipment_management.processor_e_name} | processor_id = {save_shipment_management.processor_idd} | date_pulled = {save_shipment_management.date_pulled} | bin_location = {save_shipment_management.bin_location} | milled_volume = {save_shipment_management.milled_volume} | equipment_type = {save_shipment_management.equipment_type} | equipment_id = {save_shipment_management.equipment_id} | purchase_order_number = {save_shipment_management.purchase_order_number} | lot_number = {save_shipment_management.lot_number} | volume_shipped = {save_shipment_management.volume_shipped} | volume_left = {save_shipment_management.volume_left} | editable_obj = {save_shipment_management.editable_obj} "
                            action_by_userid = request.user.id
                            user = User.objects.get(pk=action_by_userid)
                            user_role = user.role.all()
                            action_by_username = f'{user.first_name} {user.last_name}'
                            action_by_email = user.username
                            if request.user.id == 1 :
                                action_by_role = "superuser"
                            else:
                                action_by_role = str(','.join([str(i.role) for i in user_role]))
                            logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                                action_by_userid=action_by_userid,action_by_username=action_by_username,
                                                action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                                log_device=log_device)
                            logtable.save()
                            update_obj = ShipmentManagement.objects.filter(processor_idd=processor_id).exclude(id=save_shipment_management.id).values('id','editable_obj')
                            
                            if update_obj.exists():
                                for i in update_obj :
                                    get_obj = ShipmentManagement.objects.get(id=i['id'])
                                    get_obj.editable_obj = False
                                    get_obj.save()
                            else:
                                pass
                            return redirect ('outbound_shipment_mgmt')

                    else:
                        messages.error(request,"Bin Location Pulled from not exists")
                        context['sum_total_bin_location_milled_volume'] = f'0 Lbs'
                        context['sum_total_bin_location_milled_volume_java'] = 0
                else:
                    messages.error(request,"Bin Location Pulled from not exists")
                    context['sum_total_bin_location_milled_volume'] = f'0 Lbs'
                    context['sum_total_bin_location_milled_volume_java'] = 0
            return render (request, 'processor/add_outbound_shipment.html', context)
        else:
            return redirect('login')  
    except:
        return render (request, 'processor/add_outbound_shipment.html') 


@login_required()
def edit_outbound_shipment(request,pk):
    try:
        context = {}
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            get_obj = ShipmentManagement.objects.get(id=pk)
            if get_obj.editable_obj == True :
                context['id_bin_location_pull'] = get_obj.bin_location
                context['sum_total_bin_location_milled_volume'] = get_obj.milled_volume
                context['sum_total_bin_location_milled_volume_java'] = get_obj.milled_volume
                context['id_date'] = str(get_obj.date_pulled)
                context['get_equipment_type'] = get_obj.equipment_type
                context['equipment_id'] = get_obj.equipment_id
                context['storage_bin_id'] = get_obj.storage_bin
                context['moist_percentage'] = get_obj.moisture_percent
                context['weight_prod_unit_id'] = get_obj.weight_of_product_unit
                context['exp_yield_unit_id'] = get_obj.excepted_yield_unit
                context['weight_prod'] = get_obj.weight_of_product
                context['exp_yield'] = get_obj.excepted_yield
                context['purchase_number'] = get_obj.purchase_order_number
                context['lot_number'] = get_obj.lot_number
                context['volume_shipped'] = get_obj.volume_shipped
                if request.method == 'POST' :
                    id_date = request.POST.get('id_date')
                    equipment_type = request.POST.get('equipment_type')
                    equipment_id = request.POST.get('equipment_id')
                    storage_bin_id = request.POST.get('storage_bin_id')
                    weight_prod_unit_id = request.POST.get('weight_prod_unit_id')
                    exp_yield_unit_id = request.POST.get('exp_yield_unit_id')
                    moist_percentage = request.POST.get('moist_percentage')
                    weight_prod = request.POST.get('weight_prod')
                    exp_yield = request.POST.get('exp_yield')
                    purchase_number = request.POST.get('purchase_number')
                    lot_number = request.POST.get('lot_number')
                    volume_shipped = request.POST.get('volume_shipped')
                    if id_date and volume_shipped :
                        milled_volume = float(get_obj.milled_volume)
                        volume_left = milled_volume - float(volume_shipped)
                        get_obj.date_pulled = id_date
                        get_obj.equipment_type = equipment_type
                        get_obj.equipment_id = equipment_id
                        get_obj.storage_bin = storage_bin_id
                        get_obj.weight_of_product_unit = weight_prod_unit_id
                        get_obj.excepted_yield_unit = exp_yield_unit_id
                        get_obj.moisture_percent = moist_percentage
                        get_obj.purchase_order_number = purchase_number
                        get_obj.lot_number = lot_number
                        get_obj.volume_shipped = volume_shipped
                        get_obj.volume_left = volume_left
                        
                        if weight_prod_unit_id == "LBS" :
                            cal_weight = round(float(weight_prod),2)
                        if weight_prod_unit_id == "BU" :
                            cal_weight = round(float(weight_prod) * 45,2)
                        if exp_yield_unit_id == "LBS" :
                            cal_exp_yield = round(float(exp_yield),2)
                        if exp_yield_unit_id == "BU" :
                            cal_exp_yield = round(float(exp_yield) * 45,2)
                        
                        get_obj.weight_of_product_raw = weight_prod
                        get_obj.weight_of_product=cal_weight 
                        get_obj.excepted_yield_raw = exp_yield
                        get_obj.excepted_yield=cal_exp_yield 
                        get_obj.save()
                        # 20-04-23 LogTable
                        log_type, log_status, log_device = "ShipmentManagement", "Edited", "Web"
                        log_idd, log_name = get_obj.id, get_obj.bin_location
                        log_details = f"processor = {get_obj.processor_e_name} | processor_id = {get_obj.processor_idd} | date_pulled = {get_obj.date_pulled} | bin_location = {get_obj.bin_location} | milled_volume = {get_obj.milled_volume} | equipment_type = {get_obj.equipment_type} | equipment_id = {get_obj.equipment_id} | purchase_order_number = {get_obj.purchase_order_number} | lot_number = {get_obj.lot_number} | volume_shipped = {get_obj.volume_shipped} | volume_left = {get_obj.volume_left} | editable_obj = {get_obj.editable_obj} "
                        action_by_userid = request.user.id
                        user = User.objects.get(pk=action_by_userid)
                        user_role = user.role.all()
                        action_by_username = f'{user.first_name} {user.last_name}'
                        action_by_email = user.username
                        if request.user.id == 1 :
                            action_by_role = "superuser"
                        else:
                            action_by_role = str(','.join([str(i.role) for i in user_role]))
                        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                                            action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                                            log_device=log_device)
                        logtable.save()
                        return redirect ('outbound_shipment_mgmt')
            else:
                messages.error(request,'This is not a valid request')
            return render (request, 'processor/edit_outbound_shipment.html', context)
    except:
        return render (request, 'processor/edit_outbound_shipment.html') 



@login_required()
def delete_outbound_shipment(request,pk):
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        get_obj = ShipmentManagement.objects.get(id=pk)
        mill_bin_location = get_obj.bin_location
        # 20-04-23 LogTable
        log_type, log_status, log_device = "ShipmentManagement", "Deleted", "Web"
        log_idd, log_name = get_obj.id, get_obj.bin_location
        log_details = f"processor = {get_obj.processor_e_name} | processor_id = {get_obj.processor_idd} | date_pulled = {get_obj.date_pulled} | bin_location = {get_obj.bin_location} | milled_volume = {get_obj.milled_volume} | equipment_type = {get_obj.equipment_type} | equipment_id = {get_obj.equipment_id} | purchase_order_number = {get_obj.purchase_order_number} | lot_number = {get_obj.lot_number} | volume_shipped = {get_obj.volume_shipped} | volume_left = {get_obj.volume_left} | editable_obj = {get_obj.editable_obj} "
        action_by_userid = request.user.id
        user = User.objects.get(pk=action_by_userid)
        user_role = user.role.all()
        action_by_username = f'{user.first_name} {user.last_name}'
        action_by_email = user.username
        if request.user.id == 1 :
            action_by_role = "superuser"
        else:
            action_by_role = str(','.join([str(i.role) for i in user_role]))
        logtable = LogTable(log_type=log_type,log_status=log_status,log_idd=log_idd,log_name=log_name,
                            action_by_userid=action_by_userid,action_by_username=action_by_username,
                            action_by_email=action_by_email,action_by_role=action_by_role,log_details=log_details,
                            log_device=log_device)
        logtable.save()
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
        return HttpResponse (1)


@login_required()
def outbound_shipment_mgmt_csv_download(request):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        filename = 'SHIPMENT MANAGEMENT.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['PROCESSOR', 'DATE PULLED', 'BIN LOCATION', 'MILLED VOLUME (LBS)', 'VOLUME SHIPPED (LBS)', 'BALANCE (LBS)', 'EQUIPMENT TYPE', 'EQUIPMENT ID', 'PURCHASE ORDER NUMBER', 'LOT NUMBER'])
        output = ShipmentManagement.objects.all().order_by('bin_location')
        for i in output:
            
            writer.writerow([i.processor_e_name, i.date_pulled, i.bin_location, i.milled_volume, i.volume_shipped, i.volume_left, 
            i.equipment_type, i.equipment_id, i.purchase_order_number, i.lot_number])
        return response
    
    elif request.user.is_processor :
        user_email = request.user.email
        p = ProcessorUser.objects.get(contact_email=user_email)
        processor_id = Processor.objects.get(id=p.processor.id).id
        entity_name = Processor.objects.get(id=processor_id).entity_name
        output = ShipmentManagement.objects.filter(processor_idd=processor_id).order_by('bin_location')
        filename = f'SHIPMENT MANAGEMENT_{entity_name}.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['PROCESSOR', 'DATE PULLED', 'BIN LOCATION', 'MILLED VOLUME (LBS)', 'VOLUME SHIPPED (LBS)', 'BALANCE (LBS)', 'EQUIPMENT TYPE', 'EQUIPMENT ID', 'PURCHASE ORDER NUMBER', 'LOT NUMBER'])
        for i in output:
            
            writer.writerow([i.processor_e_name, i.date_pulled, i.bin_location, i.milled_volume, i.volume_shipped, i.volume_left, 
            i.equipment_type, i.equipment_id, i.purchase_order_number, i.lot_number])
        return response
    

@login_required()
def rejected_shipments_csv_download(request) :
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        today_date = date.today()
        filename = f'Rejected Shipments CSV {today_date}.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['Shipment ID','Module Tag #','Shipment Date','Crop','Variety','Grower','Field','Processor','Total Weight (LBS)','Disapproval Date','Reason For Disapproval','Moisture Level',
                         'Fancy Count','Head Count', 'Bin Location Processor'])
        output = GrowerShipment.objects.filter(status='DISAPPROVED').order_by('-id').values('shipment_id','module_number','date_time','crop','variety',
                                                                                            'grower__name','field__name','processor__entity_name',
                                                                                            'total_amount','approval_date','reason_for_disapproval','moisture_level',
                                                                                            'fancy_count','head_count', 'bin_location_processor')
        for i in output:
            writer.writerow([i['shipment_id'], i['module_number'], i['date_time'].strftime("%m-%d-%Y"), i['crop'], i['variety'], i['grower__name'], i['field__name'], i['processor__entity_name'],
                             i['total_amount'], i['approval_date'], i['reason_for_disapproval'], i['moisture_level'], i['fancy_count'], i['head_count'], i['bin_location_processor']])
        return response
    else:
        return redirect ('dashboard')


@login_required()
def all_shipments_csv_download(request) :
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        today_date = date.today()
        filename = f'All Shipments CSV {today_date}.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['Shipment ID','Module Tag #','Shipment Date','Crop','Variety','Grower','Field','Processor','Total Weight (LBS)','Status Date','Status',
                         'Recieved Weight (LBS)','Ticket Number','Reason For Disapproval','Moisture Level','Fancy Count', 'Head Count','Bin Location Processor'])
        output = GrowerShipment.objects.all().order_by('-id').values('shipment_id','module_number','date_time','crop','variety',
                                                                                            'grower__name','field__name','processor__entity_name',
                                                                                            'total_amount','approval_date','status','received_amount',
                                                                                            'token_id','reason_for_disapproval','moisture_level','fancy_count',
                                                                                            'head_count','bin_location_processor')
        for i in output:
            writer.writerow([i['shipment_id'], i['module_number'], i['date_time'].strftime("%m-%d-%Y"), i['crop'], i['variety'], i['grower__name'], i['field__name'], i['processor__entity_name'],
                             i['total_amount'], i['approval_date'], i['status'], i['received_amount'], i['token_id'], i['reason_for_disapproval'], i['moisture_level'], i['fancy_count'], i['head_count'],
                             i['bin_location_processor']])
        return response
    else:
        return redirect ('dashboard')