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
from apps.processor.models import BaleReportFarmField 
from apps.processor2.models import AssignedBaleProcessor2
from apps.growerpayments.models import *
import re


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
                message.error(request,'This email is already exists')
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
                            message.error(request,'This email is already exists')
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
        processor3 = ProcessorUser3.objects.all()
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
    
    
@login_required()  # show processor3 list
def check_riju(request):    
    # context={}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        # processor3 = ProcessorUser3.objects.all()
        # context['processor'] = processor3
        return render(request,'processor3/test.html')
    else:
        return redirect('login')   
    