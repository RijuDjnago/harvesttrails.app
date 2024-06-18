from django.shortcuts import render,HttpResponse,redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from apps.processor.models import *
from apps.accounts.models import *
from apps.grower.models import *
from apps.farms.models import *
from apps.growerpayments.models import *
from apps.field.models import *
from apps.storage.models import *
from apps.growersurvey.models import *
import string
import random,time
from django.core.mail import send_mail
from datetime import date
from django.db.models import Q
import csv
import pandas as pd
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
import qrcode  # Ensure you have the qrcode library installed
from django.core.files.base import ContentFile
from apps.processor.views import calculate_milled_volume
# Create your views here.
from apps.processor.views import create_sku_list, get_sku_list


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


@login_required()
def list_processor2(request):    
    context = {}
    try:
        # Superuser.................
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            processor2 = ProcessorUser2.objects.filter(processor2__processor_type__type_name="T2")
            search_name = request.GET.get('search_name', '')
            if search_name:
                processor2 = processor2.filter(Q(contact_name__icontains=search_name) | Q(processor2__entity_name__icontains=search_name)| Q(processor2__fein__icontains=search_name)| Q(contact_email__icontains=search_name))

            # Pagination
            processor2 = processor2.order_by("-id")
            paginator = Paginator(processor2, 20) 
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['page_obj'] = page_obj
            context['get_search_name'] = search_name
            return render(request, 'processor2/list_processor2.html',context)
        else:
            return redirect("dashboard")
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'processor2/list_processor2.html',context)
        

@login_required()
def add_processor2(request):
    context = {}
    try:
        # Superuser.............
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            form = ProcessorForm2()
            context['form'] = form
            if request.method == 'POST':
                    fein = request.POST.get('fein')
                    entity_name = request.POST.get('entity_name')
                    billing_address = request.POST.get('billing_address')
                    shipping_address = request.POST.get('shipping_address')
                    main_number = request.POST.get('main_number')
                    main_fax = request.POST.get('main_fax')
                    website = request.POST.get('website')
                    counter = request.POST.get('counter')
                    processor_type = request.POST.getlist('processor_type')                
                    if not counter:
                        counter = 0      
                    processor2 = Processor2(fein=fein,entity_name=entity_name,billing_address=billing_address,shipping_address=shipping_address,main_number=main_number,main_fax=main_fax,website=website)
                    processor2.save()
                    for type in processor_type:
                        check_type = ProcessorType.objects.filter(id=type).first()
                        processor2.processor_type.add(check_type)
                    # 20-04-23 Log Table
                    log_type, log_status, log_device = "Processor2", "Added", "Web"
                    log_idd, log_name = processor2.id, entity_name
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
                    # counter = counter + 1
                    for i in range(1, int(counter)+1):
                        contact_name = request.POST.get('contact_name{}'.format(i))
                        contact_email = request.POST.get('contact_email{}'.format(i))
                        contact_phone = request.POST.get('contact_phone{}'.format(i))
                        contact_fax = request.POST.get('contact_fax{}'.format(i))
                        if User.objects.filter(email=contact_email).exists():
                            messages.error(request,'email already exists')
                        else:
                            password = generate_random_password()
                            processor_user = ProcessorUser2(processor2_id = processor2.id,contact_name=contact_name,contact_email=contact_email,contact_phone=contact_phone,contact_fax=contact_fax,p_password_raw=password)
                            processor_user.save()
                            user = User.objects.create(email=contact_email, username=contact_email,first_name=contact_name)
                            user.role.add(Role.objects.get(role='Processor'))
                            user.is_processor2=True
                            user.is_active=True
                            user.set_password(password)
                            user.password_raw = password
                            user.save()
                            log_type, log_status, log_device = "ProcessorUser2", "Added", "Web"
                            log_idd, log_name = processor_user.id , contact_name
                            log_email = contact_email
                            log_details = f"processor2_id = {processor2.id}| processor2 = {processor2.entity_name} | contact_name= {contact_name} | contact_email = {contact_email} | contact_phone = {contact_phone} | contact_fax = {contact_fax} | p_password_raw = {password}"
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
                    return redirect('list_processor2')
            return render(request, 'processor2/add_processor2.html',context)
        else:
            return redirect("dashboard")
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'processor2/add_processor2.html',context)


@login_required()
def processor2_update(request,pk):
    context = {}
    # try:        
        # superadmin and others ................
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        print("update view called")
        obj_id = ProcessorUser2.objects.get(id=pk)
        context['p_user'] = obj_id
        processor2 = Processor2.objects.get(id=obj_id.processor2_id)
        context['form'] = ProcessorForm2(instance=processor2)
        processor_email = obj_id.contact_email
        user = User.objects.get(email=processor_email)
        if request.method == 'POST':
            form = ProcessorForm2( request.POST,instance=processor2)
            print(form)
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
                log_type, log_status, log_device = "ProcessorUser2", "Edited", "Web"
                log_idd, log_name = obj_id.id, name_update
                log_details = f"processor2_id = {obj_id.processor2.id} | processor2 = {obj_id.processor2.entity_name} | contact_name= {name_update} | contact_email = {email_update} | contact_phone = {phone_update} | contact_fax = {fax_update}"
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
                return redirect('list_processor2')
        return render(request, 'processor2/update_processor2.html',context)
    else:
        return redirect('dashboard')
    # except Exception as e:
    #     context["error_messages"] = str(e)
    #     return render(request, 'processor2/update_processor2.html',context)


@login_required()
def processor2_delete(request,pk):
    try:
        # Superuser................
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            processor2 = ProcessorUser2.objects.get(id=pk)
            user = User.objects.get(username=processor2.contact_email)
            # 20-04-23 Log Table
            log_type, log_status, log_device = "ProcessorUser2", "Deleted", "Web"
            log_idd, log_name = processor2.id, processor2.contact_name
            log_email = processor2.contact_email
            log_details = f"processor_id = {processor2.processor2.id} | processor = {processor2.processor2.entity_name} | contact_name= {processor2.contact_name} | contact_email = {processor2.contact_email} | contact_phone = {processor2.contact_phone} | contact_fax = {processor2.contact_fax}"
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
            processor2.delete()
            user.delete()
            return redirect("list_processor2")
        else:
            return redirect('dashboard')
    except Exception as e:
        return HttpResponse (e)
    

@login_required()
def processor2_change_password(request,pk):
    context={}
    try:
        # Superuser......................        
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            pp = ProcessorUser2.objects.get(id=pk)
            userr = User.objects.get(email=pp.contact_email)
            context["userr"] = userr
            if request.method == "POST":
                password1 = request.POST.get("password1")
                password2 = request.POST.get("password2")
                if len(password1) != 0 and len(password2) != 0 and password1 != None and password2 != None and password1 == password2:
                 
                    password = make_password(password1)
                    userr.password = password
                    userr.password_raw = password1
                    userr.save()
                    pp.p_password_raw = password1
                    pp.save()
                    # 20-04-23 Log Table
                    log_type, log_status, log_device = "ProcessorUser2", "Password changed", "Web"
                    log_idd, log_name = pp.id, pp.contact_name
                    log_email = pp.contact_email
                    log_details = f"processor_id = {pp.processor2.id} | processor = {pp.processor2.entity_name} | contact_name= {pp.contact_name} | contact_email = {pp.contact_email} | contact_phone = {pp.contact_phone} | contact_fax = {pp.contact_fax}"
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
                    messages.success(request,"Password changed successfully!")
            return render (request, 'processor2/processor2_change_password.html', context)
        else:
            return redirect('dashboard')
    except:
        context["error_messages"] = str(e)
        return render (request, 'processor2/processor2_change_password.html', context)


@login_required()
def add_bale_processor2(request):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        get_processor2 = Processor2.objects.all()
        context['get_processor2'] = get_processor2
        if request.method == 'POST':
            processor2_id = request.POST.get('processor_id')
            csv_file = request.FILES.get('csv_file')
            if csv_file != None :
                df = pd.read_csv(csv_file)
            else:
                df = 0
            unassignedbale_id = []
            for i in range(len(df)) :
                line = df.iloc[i]
                bale_id = line[0]
                mark_id = line[1]
                gin_id = line[2]
                
                if bale_id and processor2_id :
                    bale_id = int(float(bale_id))
                    check_bale_id = BaleReportFarmField.objects.filter(bale_id=bale_id)
                    
                    check_assignedbale_id = AssignedBaleProcessor2.objects.filter(assigned_bale=bale_id)
                    
                    if check_bale_id.exists() and len(check_assignedbale_id) == 0 :
                        try:
                            get_bale_id = BaleReportFarmField.objects.get(bale_id=int(float(bale_id)))
                            assign_bale = AssignedBaleProcessor2(processor2_id=processor2_id, bale_id=get_bale_id.id, assigned_bale=bale_id,
                            prod_id=get_bale_id.prod_id, wt=get_bale_id.wt, net_wt=get_bale_id.net_wt, load_id=get_bale_id.load_id,
                            dt_class=get_bale_id.dt_class, gr=get_bale_id.gr, lf=get_bale_id.lf, st=get_bale_id.st, mic=get_bale_id.mic,
                            ex=get_bale_id.ex, rm=get_bale_id.rm, str_no=get_bale_id.str_no, cgr=get_bale_id.cgr, rd=get_bale_id.rd,
                            tr=get_bale_id.tr, unif=get_bale_id.unif, len_num=get_bale_id.len_num, elong=get_bale_id.elong, cents_lb=get_bale_id.cents_lb,
                            loan_value=get_bale_id.loan_value, warehouse_wt=get_bale_id.warehouse_wt, warehouse_bale_id=get_bale_id.warehouse_bale_id,
                            warehouse_wh_id=get_bale_id.warehouse_wh_id, farm_name=get_bale_id.farm_name, sale_status=get_bale_id.sale_status,
                            wh_id=get_bale_id.wh_id, ob1=get_bale_id.ob1, gin_date=get_bale_id.gin_date, farm_id=get_bale_id.farm_id,
                            field_name=get_bale_id.field_name, pk_num=get_bale_id.pk_num, grower_idd=get_bale_id.ob2, grower_name=get_bale_id.ob3,
                            field_idd=get_bale_id.ob4, certificate=get_bale_id.ob5, value=get_bale_id.value, level=get_bale_id.level, 
                            crop_variety=get_bale_id.crop_variety,mark_id=mark_id,gin_id=gin_id)
                            assign_bale.save()
                            # 20-04-23 LogTable
                            log_type, log_status, log_device = "ClassingListTier2", "Added", "Web"
                            log_idd, log_name = assign_bale.id, assign_bale.assigned_bale
                            log_details = f"bale_id = {assign_bale.bale.id} | assigned_bale = {assign_bale.assigned_bale} | processor2 = {assign_bale.processor2.entity_name} | farm_name = {assign_bale.farm_name} | field_name = {assign_bale.field_name} | grower_name = {assign_bale.grower_name} | certificate = {assign_bale.certificate} | variety = {assign_bale.level} | "
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

                        except:
                            unassignedbale_id.append(bale_id)

                    elif check_bale_id.exists() and len(check_assignedbale_id) != 0 :
                        try:
                            update_assign_bale = AssignedBaleProcessor2.objects.get(assigned_bale=bale_id)
                            update_assign_bale.mark_id = mark_id
                            update_assign_bale.gin_id = gin_id
                            update_assign_bale.save()
                            # 20-04-23 LogTable
                            log_type, log_status, log_device = "ClassingListTier2", "Edited", "Web"
                            log_idd, log_name = update_assign_bale.id, update_assign_bale.assigned_bale
                            log_details = f"bale_id = {update_assign_bale.bale.id} | assigned_bale = {update_assign_bale.assigned_bale} | processor2 = {update_assign_bale.processor2.entity_name} | farm_name = {update_assign_bale.farm_name} | field_name = {update_assign_bale.field_name} | grower_name = {update_assign_bale.grower_name} | certificate = {update_assign_bale.certificate} | variety = {update_assign_bale.level} | "
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
                        except:
                            unassignedbale_id.append(bale_id)

                    elif BaleReportFarmField.objects.filter(bale_id=f"0{bale_id}").exists() and len(AssignedBaleProcessor2.objects.filter(assigned_bale=f"0{bale_id}")) == 0 :
                        try:
                            get_bale_id = BaleReportFarmField.objects.get(bale_id=f"0{bale_id}")
                            assign_bale = AssignedBaleProcessor2(processor2_id=processor2_id, bale_id=get_bale_id.id, assigned_bale=get_bale_id.bale_id,
                            prod_id=get_bale_id.prod_id, wt=get_bale_id.wt, net_wt=get_bale_id.net_wt, load_id=get_bale_id.load_id,
                            dt_class=get_bale_id.dt_class, gr=get_bale_id.gr, lf=get_bale_id.lf, st=get_bale_id.st, mic=get_bale_id.mic,
                            ex=get_bale_id.ex, rm=get_bale_id.rm, str_no=get_bale_id.str_no, cgr=get_bale_id.cgr, rd=get_bale_id.rd,
                            tr=get_bale_id.tr, unif=get_bale_id.unif, len_num=get_bale_id.len_num, elong=get_bale_id.elong, cents_lb=get_bale_id.cents_lb,
                            loan_value=get_bale_id.loan_value, warehouse_wt=get_bale_id.warehouse_wt, warehouse_bale_id=get_bale_id.warehouse_bale_id,
                            warehouse_wh_id=get_bale_id.warehouse_wh_id, farm_name=get_bale_id.farm_name, sale_status=get_bale_id.sale_status,
                            wh_id=get_bale_id.wh_id, ob1=get_bale_id.ob1, gin_date=get_bale_id.gin_date, farm_id=get_bale_id.farm_id,
                            field_name=get_bale_id.field_name, pk_num=get_bale_id.pk_num, grower_idd=get_bale_id.ob2, grower_name=get_bale_id.ob3,
                            field_idd=get_bale_id.ob4, certificate=get_bale_id.ob5, value=get_bale_id.value, level=get_bale_id.level, 
                            crop_variety=get_bale_id.crop_variety,mark_id=mark_id,gin_id=gin_id)
                            assign_bale.save()
                            # 20-04-23 LogTable
                            log_type, log_status, log_device = "ClassingListTier2", "Added", "Web"
                            log_idd, log_name = assign_bale.id, assign_bale.assigned_bale
                            log_details = f"bale_id = {assign_bale.bale.id} | assigned_bale = {assign_bale.assigned_bale} | processor2 = {assign_bale.processor2.entity_name} | farm_name = {assign_bale.farm_name} | field_name = {assign_bale.field_name} | grower_name = {assign_bale.grower_name} | certificate = {assign_bale.certificate} | variety = {assign_bale.level} | "
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
                        except:
                            unassignedbale_id.append(bale_id)
                    elif BaleReportFarmField.objects.filter(bale_id=f"0{bale_id}").exists() and len(AssignedBaleProcessor2.objects.filter(assigned_bale=f"0{bale_id}")) != 0 :
                        try:
                            update_assign_bale = AssignedBaleProcessor2.objects.get(assigned_bale=f"0{bale_id}")
                            update_assign_bale.mark_id = mark_id
                            update_assign_bale.gin_id = gin_id
                            update_assign_bale.save()
                            # 20-04-23 LogTable
                            log_type, log_status, log_device = "ClassingListTier2", "Edited", "Web"
                            log_idd, log_name = update_assign_bale.id, update_assign_bale.assigned_bale
                            log_details = f"bale_id = {update_assign_bale.bale.id} | assigned_bale = {update_assign_bale.assigned_bale} | processor2 = {update_assign_bale.processor2.entity_name} | farm_name = {update_assign_bale.farm_name} | field_name = {update_assign_bale.field_name} | grower_name = {update_assign_bale.grower_name} | certificate = {update_assign_bale.certificate} | variety = {update_assign_bale.level} | "
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
                        except:
                            unassignedbale_id.append(bale_id)

                    else:
                        unassignedbale_id.append(bale_id)
                else:
                    pass
            if len(unassignedbale_id) == 0 :
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
                messages.success(request,"CSV uploaded successfully")
            else:
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
                messages.success(request,"CSV uploaded successfully")
                messages.error(request,f"The bale(s) are not assigned : {unassignedbale_id}")
        return render(request, 'processor2/add_bale_processor2.html',context)
    else:
        return redirect('dashboard')


@login_required()
def add_processor2_user(request,pk):    
    context = {}
    try:
        # Superuser..............
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            processor2_user = ProcessorUser2.objects.get(id=pk)
            processor2_id = processor2_user.processor2.id
            processor2 = Processor2.objects.get(id=processor2_id)
            context['processor'] = processor2
            processor_user = ProcessorUser2.objects.filter(processor2_id = processor2.id)
            context['processor_user'] = processor_user
            if request.method == 'POST':
                counter = request.POST.get('counter')
                for i in range(1,int(counter)+1):
                    contact_name = request.POST.get('contact_name{}'.format(i))
                    contact_email = request.POST.get('contact_email{}'.format(i))
                    contact_phone = request.POST.get('contact_phone{}'.format(i))
                    contact_fax = request.POST.get('contact_fax{}'.format(i))

                    if User.objects.filter(email=contact_email).exists():
                        messages.error(request,'email already exists')
                    else:
                        password = generate_random_password()
            
                        puser = ProcessorUser2(processor2_id = processor2_id,contact_name=contact_name,contact_email=contact_email,contact_phone=contact_phone,contact_fax=contact_fax,p_password_raw=password)
                        puser.save()
                        user = User.objects.create(email=contact_email, username=contact_email,first_name=contact_name)
                        user.role.add(Role.objects.get(role='Processor'))
                        user.is_processor2=True
                        user.is_active=True
                        user.set_password(password)
                        user.password_raw = password
                        user.save()
                        # 20-04-23 Log Table
                        log_type, log_status, log_device = "ProcessorUser2", "Added", "Web"
                        log_idd, log_name = puser.id , contact_name
                        log_email = contact_email
                        log_details = f"processor2_id = {processor2.id}| processor2 = {processor2.entity_name} | contact_name= {contact_name} | contact_email = {contact_email} | contact_phone = {contact_phone} | contact_fax = {contact_fax} | p_password_raw = {password}"
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
                return redirect('list_processor2')
            return render(request, 'processor2/add_processor2_user.html',context)
        else:
            return redirect('dashboard')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'processor2/add_processor2_user.html',context)


@login_required()
def list_bale_processor2(request):
    context = {}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        p_user = ProcessorUser2.objects.all()
        processors2_id = [i.processor2.id for i in p_user]
        processors2 = Processor2.objects.filter(id__in = processors2_id)
        processors2_id = request.GET.get('processors2_id')
        cerSelction = request.GET.get('cerSelction')
        lelSelction = request.GET.get('lelSelction')
        search_name = request.GET.get('search_name')

        context['selectedProcessors2'] = 'All'
        context['selectedCre'] = 'All'
        context['selectedLel'] = 'All'
 
        if processors2_id == None and cerSelction == None and lelSelction == None and search_name == None :
            report_data = AssignedBaleProcessor2.objects.all()
        elif search_name != None :
            report_data = AssignedBaleProcessor2.objects.filter(
            Q(assigned_bale__icontains=search_name) | Q(field_name__icontains=search_name) | Q(farm_name__icontains=search_name) |
            Q(warehouse_wh_id__icontains=search_name) | Q(mark_id__icontains=search_name)).distinct()
            context['search_get'] = search_name
        else:
            report_data = AssignedBaleProcessor2.objects.filter(id__isnull = False)
            if processors2_id != 'All' :
                report_data = report_data.filter(processor2_id=processors2_id)
                selectedProcessors2 = Processor2.objects.get(id=processors2_id)
                context['selectedProcessors2'] = selectedProcessors2
            if cerSelction != 'All' :
                if cerSelction == 'null' :
                    report_data = report_data.filter(certificate=None)
                    context['selectedCre'] = cerSelction
                else:
                    report_data = report_data.filter(certificate=cerSelction)
                    context['selectedCre'] = cerSelction
            if lelSelction != 'All' :
                report_data = report_data.filter(level=lelSelction)
                context['selectedLel'] = lelSelction
        paginator = Paginator(report_data, 100)
        page = request.GET.get('page')
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)
        context['report'] = report
        context['processors2'] = processors2
        return render(request, 'processor2/list_bale_processor2.html',context)
    if request.user.is_processor2 :
        user_email = request.user.email
        p = ProcessorUser2.objects.get(contact_email=user_email)
        processor2_id = Processor2.objects.get(id=p.processor2_id).id
        report_data = AssignedBaleProcessor2.objects.filter(processor2_id=processor2_id)
        cerSelction = request.GET.get('cerSelction')
        lelSelction = request.GET.get('lelSelction')
        search_name = request.GET.get('search_name')
        context['selectedProcessors2'] = 'All'
        context['selectedCre'] = 'All'
        context['selectedLel'] = 'All'

        if cerSelction == None and lelSelction == None and search_name == None :
            report_data = AssignedBaleProcessor2.objects.filter(processor2_id=processor2_id)
        elif search_name != None :
            report_data = AssignedBaleProcessor2.objects.filter(processor2_id=processor2_id).filter(
            Q(assigned_bale__icontains=search_name) | Q(field_name__icontains=search_name) | Q(farm_name__icontains=search_name) |
            Q(warehouse_wh_id__icontains=search_name) | Q(mark_id__icontains=search_name)).distinct()
            context['search_get'] = search_name
        else:
            report_data = AssignedBaleProcessor2.objects.filter(processor2_id=processor2_id)
            if cerSelction != 'All' :
                if cerSelction == 'null' :
                    report_data = report_data.filter(certificate=None)
                    context['selectedCre'] = cerSelction
                else:
                    report_data = report_data.filter(certificate=cerSelction)
                    context['selectedCre'] = cerSelction
            if lelSelction != 'All' :
                report_data = report_data.filter(level=lelSelction)
                context['selectedLel'] = lelSelction
        
        paginator = Paginator(report_data, 100)
        page = request.GET.get('page')
        try:
            report = paginator.page(page)
        except PageNotAnInteger:
            report = paginator.page(1)
        except EmptyPage:
            report = paginator.page(paginator.num_pages)
        context['report'] = report
        return render(request, 'processor2/list_bale_processor2.html',context)


@login_required()
def classing_csv_list_view2(request,pk):
    context = {}
    report_data =  BaleReportFarmField.objects.get(id=pk)
    # get_gin_id = report_data.classing.processor.gin_id
    csv_name = str(report_data.classing.csv_path).split('/')[1]
    check_payment_status = GrowerPayments.objects.filter(delivery_id=report_data.bale_id)
    if check_payment_status.exists() :
        get_payment_status = GrowerPayments.objects.get(delivery_id=report_data.bale_id)
        payment_status = 'Paid'
        payment_amount = get_payment_status.payment_amount
        payment_date = get_payment_status.payment_date
        payment_type = get_payment_status.payment_type
        payment_confirmation = get_payment_status.payment_confirmation
    else:
        payment_status = 'Not Paid'
        payment_amount = 'N/A'
        payment_date = 'N/A'
        payment_type = 'N/A'
        payment_confirmation = 'N/A'
    bale_id = report_data.bale_id
    try:
        get_mark_id = AssignedBaleProcessor2.objects.get(assigned_bale=bale_id).mark_id
        get_gin_id = AssignedBaleProcessor2.objects.get(assigned_bale=bale_id).gin_id
    except:
        get_mark_id = ''
        get_gin_id = ''
        
    responce = {
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
        # "csv_type":report_data.classing.csv_type,
        "csv_name":csv_name,
        "payment_status":payment_status,
        "payment_amount":payment_amount,
        "payment_date":payment_date,
        "payment_type":payment_type,
        "payment_confirmation":payment_confirmation,
        "get_gin_id":get_gin_id,
        "mark_id":get_mark_id,
        }
    return JsonResponse(responce)


@login_required()
def processor2_classing_csv_all2(request):
    # Create the HttpResponse object with the appropriate CSV header.
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        filename = 'ASSIGNED_BALE_LIST.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        bale_all = AssignedBaleProcessor2.objects.all()
        writer = csv.writer(response)
        writer.writerow(['Prod Id', 'Farm Name', 'Tier 2 Processor', 'Grower Name', 'Bale Id','Warehouse Id','Mark Id','Gin Id','Date','Net Wt','Farm Id','Load Id','Variety','Field name','Certificate','Level',
        'gr','lf','st','mic','ex','rm','str_no','cgr','rd','tr','unif','len_num','elong','loan_value','B','payment'])

        for i in bale_all:
            if GrowerPayments.objects.filter(grower_id = i.grower_idd).filter(delivery_id=i.assigned_bale).exists() :
                payment = 'Paid'
            else:
                payment = 'Due'
            writer.writerow([i.prod_id, i.farm_name, i.processor2.entity_name, i.grower_name, i.assigned_bale, i.warehouse_wh_id, i.mark_id, i.gin_id, i.dt_class, i.net_wt, i.farm_id, i.load_id, i.crop_variety, i.field_name, i.certificate, i.level,
            i.gr,i.lf,i.st,i.mic,i.ex,i.rm,i.str_no,i.cgr,i.rd,i.tr,i.unif,i.len_num,i.elong,i.loan_value,i.ob1,payment])

        return response
    
    elif request.user.is_processor2:
        user_email = request.user.email
        p = ProcessorUser2.objects.get(contact_email=user_email)
        processor2_id = Processor2.objects.get(id=p.processor2_id).id
        bale_all = AssignedBaleProcessor2.objects.filter(processor2_id=processor2_id)

        filename = 'ASSIGNED_BALE_LIST.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['Prod Id', 'Farm Name', 'Tier 2 Processor', 'Grower Name', 'Bale Id','Warehouse Id','Mark Id','Gin Id','Date','Net Wt','Farm Id','Load Id','Variety','Field name','Certificate','Level',
        'gr','lf','st','mic','ex','rm','str_no','cgr','rd','tr','unif','len_num','elong','loan_value','B','payment'])

        for i in bale_all:
            if GrowerPayments.objects.filter(grower_id = i.grower_idd).filter(delivery_id=i.assigned_bale).exists() :
                payment = 'Paid'
            else:
                payment = 'Due'
            writer.writerow([i.prod_id, i.farm_name, i.processor2.entity_name, i.grower_name, i.assigned_bale, i.warehouse_wh_id, i.mark_id, i.gin_id, i.dt_class, i.net_wt, i.farm_id, i.load_id, i.crop_variety, i.field_name, i.certificate, i.level,
            i.gr,i.lf,i.st,i.mic,i.ex,i.rm,i.str_no,i.cgr,i.rd,i.tr,i.unif,i.len_num,i.elong,i.loan_value,i.ob1,payment])

        return response

    else:
        return redirect('dashboard')
    

@login_required()
def t2_classing_ewr_report_list(request):
    context = {}    
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        context['p2_id'] = 'all'
        context['level'] = 'all'
        
        report = AssignedBaleProcessor2.objects.filter(id__isnull = False).order_by('-id')
        processor2 = Processor2.objects.all().order_by('entity_name')
        context['processor2'] = processor2
        levels = request.GET.get("levels")
        get_processor2 = request.GET.get("get_processor2")
        if levels == None and get_processor2 == None :
            report = report
        else :
            if get_processor2 :
                if get_processor2 != 'all' :
                    # cr = ClassingReport.objects.filter(processor2__id=int(get_processor2))
                    # cr_id = [i.id for i in cr]
                    report = report.filter(processor2__id = get_processor2)
                    selectedprocessor = Processor2.objects.get(id=get_processor2)
                    context['p2_id'] = selectedprocessor.id
                    context['selectedprocessor'] = selectedprocessor
                else:
                    report = report
            if levels :
                if levels != 'all' :
                    report = report.filter(level = levels)
                    context['selected_level'] = levels
                    context['level'] = levels
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
        return render(request, 'processor2/t2_classing_ewr_report_list.html',context)
    elif request.user.is_processor2:
        user_email = request.user.email
        p = ProcessorUser2.objects.get(contact_email=user_email)
        processor2_id = Processor2.objects.get(id=p.processor2_id).id
        context['p2_id'] = processor2_id
        context['level'] = 'all'
        levels = request.GET.get("levels")
        report = AssignedBaleProcessor2.objects.filter(processor2_id=processor2_id).order_by('-id')
        if levels :
            if levels != 'all' :
                report = report.filter(level = levels)
                context['selected_level'] = levels
                context['level'] = levels
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
        return render(request, 'processor2/t2_classing_ewr_report_list.html',context)
    else:
        return redirect ('dashboard')


@login_required()
def t2_classing_ewr_report_all_downlaod(request, p2_id,level):
    response = HttpResponse(content_type='text/plain') 
    current_date = date.today().strftime("%m-%d-%Y")
    report = ""

    if p2_id == 'all' and level == 'all' :
        report_name = "T2_EWR_All"
        report = AssignedBaleProcessor2.objects.all().order_by('-id')
    elif p2_id != 'all' and level == 'all' :
        processor2_name = Processor2.objects.get(id=p2_id).entity_name
        report_name = f"T2_EWR_{processor2_name}"
        report = AssignedBaleProcessor2.objects.filter(processor2_id=p2_id).order_by('-id')
    elif p2_id == 'all' and level != 'all' :
        report_name = f"T2_EWR_{level}"
        report = AssignedBaleProcessor2.objects.filter(level=level).order_by('-id')
    elif p2_id != 'all' and level != 'all' :
        processor2_name = Processor2.objects.get(id=p2_id).entity_name
        report_name = f"T2_EWR_{processor2_name}_{level}"
        report = AssignedBaleProcessor2.objects.filter(processor2_id=p2_id,level=level).order_by('-id')

    response['Content-Disposition'] = 'attachment; filename="{}_{}.txt"'.format(report_name,current_date)
    for i in report:
        response.write("{}{}{}\n".format(i.warehouse_wh_id,i.assigned_bale,2023))

    return response


import shapefile
@login_required()
def addlocation_processor2(request):
    context ={} 
    try:
        if request.user.is_authenticated:               
            # Super User ........
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                form = Processor2LocationForm()
                processor = Processor2.objects.filter(processor_type__type_name = "T2")
                #print(processor)
                context['form']=form
                context['processor']=processor
                if request.method == 'POST':
                    form = Processor2LocationForm(request.POST)
                    name = request.POST.get('name')
                    upload_type = request.POST.get('upload_type')
                    processor = int(request.POST.get('processor_id'))  
                    if request.FILES.get('zip_file'):
                        zip_file = request.FILES.get('zip_file')
                        Processor2Location(processor_id=processor, name=name,upload_type=upload_type,shapefile_id=zip_file).save()
                        location_obj = Processor2Location.objects.filter(name=name).filter(processor=processor)          
                        location_var = [i.id for i in location_obj][0]
                        location_id = Processor2Location.objects.get(id=location_var)
                        sf = shapefile.Reader(location_id.shapefile_id.path)
                        features = sf.shapeRecords()
                        for feat in features:
                            eschlon_id = feat.record["id"]
                            location_id.eschlon_id = eschlon_id
                            location_id.save()

                    if request.POST.get('latitude') and request.POST.get('longitude'):
                        latitude = request.POST.get('latitude')
                        longitude = request.POST.get('longitude')
                        Processor2Location(processor_id=processor, name=name,upload_type=upload_type,latitude=latitude,longitude=longitude).save()
                        
                    return redirect('location_list_processor2')
                return render(request, 'processor2/add_location_processor2.html',context)
            else:            
                return redirect("dashboard")
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'processor2/add_location_processor2.html',context)
    

@login_required()   
def location_list_processor2(request):
    context ={}
    try:
        if request.user.is_authenticated: 
            # superuser ......
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():            
                location = Processor2Location.objects.filter(processor__processor_type__type_name="T2")
                processor = Processor2.objects.filter(processor_type__type_name="T2")
                context['processor'] = processor
                
                value = request.GET.get('processor_id','')                   
                
                if value and value !="all":                    
                    location =location.filter(processor_id=int(value))
                    context['selectedprocessor'] = int(value)
                    
                location = location.order_by("-id")
                paginator = Paginator(location, 20)
                page = request.GET.get('page')
                try:
                    report = paginator.page(page)
                except PageNotAnInteger:
                    report = paginator.page(1)
                except EmptyPage:
                    report = paginator.page(paginator.num_pages)    
                context['location'] = report    
                return render(request, 'processor2/list_location.html',context)        
            else:
                return redirect("dashboard")
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'processor2/list_location.html',context)


@login_required()
def location_edit_processor2(request,pk):
    context = {}
    try:
        if request.user.is_authenticated:        
            # superuser .......
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():            
                location = Processor2Location.objects.get(id=pk)
                form = Processor2LocationForm(instance=location)
                processor = Processor2.objects.all()
                context['form'] = form
                context['processor'] = processor
                context['selectedprocessor'] = location.processor_id
                context['uploadtypeselect'] = location.upload_type
                location = Processor2Location.objects.filter(id=pk)
                context['location'] = location
                if request.method == 'POST':
                    name = request.POST.get('name')
                    processorSelction = int(request.POST.get('processor_name'))
                    uploadtypeSelction = request.POST.get('uploadtypeSelction')
                    shapefile_id = request.FILES.get('zip_file')
                    latitude = request.POST.get('latitude')
                    longitude = request.POST.get('longitude')
                    location_update = Processor2Location.objects.get(id=pk)
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
                        #print(name)
                        location_update.name = name
                        location_update.processor_id = processorSelction
                        location_update.upload_type = 'coordinates'
                        location_update.shapefile_id = None
                        location_update.eschlon_id = None
                        location_update.latitude = latitude
                        location_update.longitude = longitude
                        location_update.save()
                    return redirect('location_list_processor2')
                return render(request, 'processor2/location_edit.html',context)
            else:
                return redirect("dashboard")
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'processor2/location_edit.html',context)


@login_required()
def location_delete_processor2(request,pk):
    context = {}
    try:
        # Superuser............
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            location = Processor2Location.objects.get(id=pk)
            location.delete()
            return redirect('location_list_processor2')  
        else:
            return redirect("dashboard")
    except Exception as e:
        context["error_messages"] = str(e)
        return redirect('location_list_processor2', context)


@login_required
def add_outbound_shipment_processor2(request):
    context = {}
    try:
        # Superuser...................
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
                sku = data.get("storage_bin_id")
                milled_value = data.get("milled_value")
                context.update({
                    "select_processor_name": Processor2.objects.filter(id=int(bin_pull)).first().entity_name,
                    "select_processor_id": bin_pull,
                    "processor_type":"T2",
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
                    if sku:                   
                        context["milled_value"] =  calculate_milled_volume(int(bin_pull), "T2", sku) 
                        context["selected_sku"] = sku 
                    else:
                        context["milled_value"] =  calculate_milled_volume(int(bin_pull), "T2", sku)                   
                    processor3 = LinkProcessorToProcessor.objects.filter(processor_id=bin_pull, linked_processor__processor_type__type_name = "T3").values("linked_processor__id", "linked_processor__entity_name")
                    processor4 = LinkProcessorToProcessor.objects.filter(processor_id=bin_pull, linked_processor__processor_type__type_name = "T4").values("linked_processor__id", "linked_processor__entity_name")
                    context["processor3"] = processor3
                    context["processor4"] = processor4
                    context["sender_sku_id_list"] = get_sku_list(int(bin_pull),"T2")["data"]
                    return render(request, 'processor2/add_outbound_shipment_processor2.html', context)
                else:
                    if context["weight_prod_unit_id"] == "LBS" :
                        cal_weight = round(float(context["weight_prod"]),2)
                    if context["weight_prod_unit_id"] == "BU" :
                        cal_weight = round(float(context["weight_prod"]) * 45,2)
                    if context["exp_yield_unit_id"] == "LBS" :
                        cal_exp_yield = round(float(context["exp_yield"]),2)
                    if context["exp_yield_unit_id"] == "BU" :
                        cal_exp_yield = round(float(context["exp_yield"]) * 45,2)

                    select_proc_id, processor_type = context["processor2_id"].split()
                    if processor_type == 'T3':
                        select_destination_ = Processor2.objects.get(id=select_proc_id).entity_name
                        receiver_processor_type = "T3"
                       
                    elif processor_type == 'T4':
                        select_destination_ = Processor2.objects.get(id=select_proc_id).entity_name
                        receiver_processor_type = "T4"
                    
                    milled_volume = context["milled_value"]
                    volume_left = float(context["milled_value"]) - float(context["volume_shipped"])
                    shipment_id = generate_shipment_id()
                    
                    processor_e_name = Processor2.objects.filter(id=int(bin_pull)).first().entity_name
                    save_shipment_management = ShipmentManagement(shipment_id=shipment_id,processor_idd=bin_pull,processor_e_name=processor_e_name, sender_processor_type="T2", bin_location=bin_pull,
                            equipment_type=context["equipment_type"],equipment_id=context["equipment_id"],storage_bin_send=context["storage_bin_id"],moisture_percent = context["moist_percentage"],weight_of_product_raw = context["weight_prod"],
                            weight_of_product=cal_weight,weight_of_product_unit=context["weight_prod_unit_id"], excepted_yield_raw =context["exp_yield"],excepted_yield=cal_exp_yield,excepted_yield_unit=context["exp_yield_unit_id"],
                            purchase_order_number=context["purchase_number"],lot_number=context["lot_number"],volume_shipped=context["volume_shipped"],milled_volume=milled_volume,volume_left=volume_left,editable_obj=True,
                            processor2_idd=select_proc_id,processor2_name=select_destination_, receiver_processor_type=receiver_processor_type)
                    save_shipment_management.save()

                    processor2_id = Processor2.objects.filter(id=int(bin_pull)).first().id
                    create_sku_list(processor2_id, "T2", context["storage_bin_id"])
                    files = request.FILES.getlist('files')
                    for file in files:
                        new_file = File.objects.create(file=file)
                        save_shipment_management.files.add(new_file)
                    save_shipment_management.save()
                    # logtable.....
                    log_type, log_status, log_device = "ShipmentManagement", "Added", "Web"
                    log_idd, log_name = save_shipment_management.id, save_shipment_management.bin_location
                    log_details = f"processor2 = {save_shipment_management.processor_e_name} | processor2_id = {save_shipment_management.processor_idd} | date_pulled = {save_shipment_management.date_pulled} | bin_location = {save_shipment_management.bin_location} | milled_volume = {save_shipment_management.milled_volume} | equipment_type = {save_shipment_management.equipment_type} | equipment_id = {save_shipment_management.equipment_id} | purchase_order_number = {save_shipment_management.purchase_order_number} | lot_number = {save_shipment_management.lot_number} | volume_shipped = {save_shipment_management.volume_shipped} | volume_left = {save_shipment_management.volume_left} | editable_obj = {save_shipment_management.editable_obj} "
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
                    update_obj = ShipmentManagement.objects.filter(processor_idd=int(bin_pull)).exclude(id=save_shipment_management.id).values('id','editable_obj')
                    
                    if update_obj.exists():
                        for i in update_obj :
                            get_obj = ShipmentManagement.objects.get(id=i['id'])
                            get_obj.editable_obj = False
                            get_obj.save()
                    else:
                        pass
                    return redirect('outbound_shipment_list')

            return render(request, 'processor2/add_outbound_shipment_processor2.html', context)
        else:
            return redirect("dashboard")
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'processor2/add_outbound_shipment_processor2.html', context) 


@login_required()
def outbound_shipment_list(request):  
    context = {}
    try:   
        # Superuser.................     
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            output = ShipmentManagement.objects.filter(sender_processor_type="T2")
            p_id = [i.processor_idd for i in output]
            processors = Processor2.objects.filter(id__in = p_id).order_by('entity_name')
            context['processors'] = processors
            search_name = request.GET.get('search_name','')
            selectprocessor_id = request.GET.get('selectprocessor_id','')
            context['search_name'] = search_name
            context['selectedProcessors'] = selectprocessor_id
            
            if search_name and search_name != '':
                output = output.filter(Q(processor_e_name__icontains=search_name) | Q(date_pulled__icontains=search_name) |
                Q(bin_location__icontains=search_name) | Q(equipment_type__icontains=search_name) | Q(equipment_id__icontains=search_name) | 
                Q(purchase_order_number__icontains=search_name) | Q(lot_number__icontains=search_name))
                
            if selectprocessor_id and selectprocessor_id != 'All':
                output = output.filter(processor_idd=selectprocessor_id)                                      
                    
            output = output.order_by("-id")
            paginator = Paginator(output, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)
            context["table_data"] = report       
            return render (request, 'processor2/outbound_shipment_list.html', context)
        else:
            return redirect('dashboard')  
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'processor2/outbound_shipment_list.html', context)


@login_required()
def outbound_shipment_view(request,pk):  
    context ={} 
    try:
        # Superuser......................
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            output = ShipmentManagement.objects.filter(id=pk).order_by('bin_location')
            files = ShipmentManagement.objects.filter(id=pk).first().files.all().values('file')
            files_data = []
            for j in files:
                file_name = {}
                file_name["file"] = j["file"]                
                if j["file"] or j["file"] != "" or j["file"] != ' ':
                    file_name["name"] = j["file"].split("/")[-1]
                else:
                    file_name["name"] = None
                files_data.append(file_name)
            context["files"] = files_data
            context["report"] = output
           
            return render (request, 'processor2/outbound_shipment_view.html', context) 
        else:
            return redirect('dashboard')  
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'processor2/outbound_shipment_list.html', context)


@login_required()
def outbound_shipment_delete(request,pk):
    context = {} 
    try:
        # Superuser........... 
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            get_obj = ShipmentManagement.objects.get(id=pk)
            mill_bin_location = get_obj.bin_location 
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
            return redirect('outbound_shipment_list')
        else:
            return redirect("dashboard")
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'processor2/outbound_shipment_list.html', context)


@login_required()
def inbound_shipment_list(request):
    context = {}
    try:
        # Superuser.............
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():           
            context["processor2"] = Processor2.objects.filter(processor_type__type_name="T2")            
            search_name = request.GET.get("search_name", "")
            context["search_name"] = search_name  
            select_processor = request.GET.get("select_processor", "")         
            context["select_processor"] = select_processor
            queryset = ShipmentManagement.objects.filter(receiver_processor_type="T2")
            
            if select_processor and select_processor != 'All':
                queryset = queryset.filter(processor2_idd=int(select_processor))

            if search_name and search_name != "":
                queryset = queryset.filter(Q(shipment_id__icontains=search_name) | Q(processor_e_name__icontains=search_name))
            
            # Paginate the 
            queryset = queryset.order_by("-id")
            paginator = Paginator(queryset, 10) 
            page = request.GET.get('page')

            try:
                table_data = paginator.page(page)
            except PageNotAnInteger:
                table_data = paginator.page(1)
            except EmptyPage:
                table_data = paginator.page(paginator.num_pages)

            context["table_data"] = table_data
            return render(request, 'processor2/inbound_management_table.html', context)
        else:
            return redirect('dashboard') 
    except Exception as e:        
        context["error_messages"] = str(e)
        return render(request, 'processor2/inbound_management_table.html', context)


from io import BytesIO    
@login_required
def inbound_shipment_view(request, pk):
    context = {}
    try:
        # Superuser..............
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role() or request.user.is_processor2:
           
            shipment = ShipmentManagement.objects.filter(id=pk).first()
            if not shipment:
                return redirect('some_error_page') 
            shipment_date_str = shipment.date_pulled.strftime('%Y-%m-%dT%H:%M:%S') if shipment.date_pulled else None

            datapy = {
                "shipment_id": shipment.shipment_id,
                "send_processor_name": shipment.processor_e_name,
                "sustainability": "under development",
                "shipment_date": shipment_date_str,
            }
            data = json.dumps(datapy)           
            img = qrcode.make(data)
            img_name = 'qr1_' + str(int(time.time())) + '.png'         
           
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)            
            file = ContentFile(buffer.read(), name=img_name)

            shipment.qr_code_processor.save(img_name, file, save=True)
            img_name = shipment.qr_code_processor
            context["img_name"] = img_name
            context["shipment"] = list(ShipmentManagement.objects.filter(id=pk).values())

            files = ShipmentManagement.objects.filter(id=pk).first().files.all().values('file')
            files_data = []
            for j in files:
                file_name = {}
                file_name["file"] = j["file"]
                if j["file"]:
                    file_name["name"] = j["file"].split("/")[-1]
                else:
                    file_name["name"] = None
                files_data.append(file_name)
            context["files"] = files_data            
            return render(request, 'processor2/inbound_management_view.html', context)
        else:
            return redirect('dashboard')
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'processor2/inbound_management_view.html', context) 


@login_required()
def inbound_shipment_edit(request, pk):
    context = {}
    try: 
        # superuser...............       
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role() or request.user.is_processor2:
            shipment = ShipmentManagement.objects.get(id=pk)
            context["shipment"] = shipment
            context["receiver_sku_id_list"] = get_sku_list(int(shipment.processor2_idd), shipment.receiver_processor_type)["data"]
            files = ShipmentManagement.objects.filter(id=pk).first().files.all().values('file')
            files_data = []
            for j in files:
                file_name = {}
                file_name["file"] = j["file"]                
                if j["file"] or j["file"] != "" or j["file"] != ' ':
                    file_name["name"] = j["file"].split("/")[-1]
                else:
                    file_name["name"] = None
                files_data.append(file_name)
            context["files"] = files_data
            data = request.POST
            if request.method == "POST":
                button_value = request.POST.getlist('remove_files')                
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
                
                processor2_id = Processor2.objects.filter(id=int(shipment.processor2_idd)).first().id
                create_sku_list(processor2_id, shipment.receiver_processor_type, storage_bin_recive)
                files = request.FILES.getlist('new_files')
                shipment = ShipmentManagement.objects.get(id=pk)
                for file in files:
                    new_file = File.objects.create(file=file)
                    shipment.files.add(new_file)
                shipment.save()
                # logtable.........
                log_type, log_status, log_device = "ProcessorShipment", "Edited", "Web"
                log_idd, log_name = shipment.id, shipment.shipment_id
                log_details = f"status = {status} | total_amount = {shipment.volume_shipped} | shipment_id = {shipment.shipment_id} | receiver_processor_id = {shipment.processor2_idd} | sender_processor_id = {shipment.processor_idd} |"
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
                return redirect('inbound_shipment_list')
            return render(request, 'processor2/inbound_management_edit.html', context)
        else:
            return redirect('dashboard')  
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'processor2/inbound_management_edit.html', context)


@login_required()
def inbound_shipment_delete(request,pk):
    context = {}
    try:
        # superuser..............
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role(): 
            shipment = ShipmentManagement.objects.filter(id=pk).first()    
            shipment.delete()
            # logtable..
            log_type, log_status, log_device = "ProcessorShipment", "Deleted", "Web"
            log_idd, log_name = shipment.id, shipment.shipment_id
            log_details = f"status = {shipment.status} | shipment_id = {shipment.shipment_id} | sender_processor_id = {shipment.processor_idd} | receiver_processor_id = {shipment.processor2_idd} |"
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
            return redirect('inbound_shipment_list')
        else:
            return redirect("dashboard")
    except Exception as e:
        context["error_messages"] = str(e)
        return redirect('inbound_shipment_list', context)

    
@login_required()
def recive_shipment(request):
    context = {}
    try:
        # Superuser....................
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            context["processor"] = list(Processor.objects.all().values("id", "entity_name"))            
            context.update({
                "select_processor_name": None,
                "select_processor_id": None,
                "milled_value": "None",
                "selected_processor_sku_id_list":[],
                "selected_destination": None,
                "selected_processor_sku_id_list_processor2": []
            })
            if request.method == "POST":
                data = request.POST
                bin_pull = data.get("bin_pull")
                sku =data.get("storage_bin_id")
                milled_value = data.get("milled_value")                
                processor2_id = data.get("processor2_id")
                context.update({
                    "select_processor_name": Processor.objects.filter(id=int(bin_pull)).first().entity_name,
                    "select_processor_id": bin_pull,
                    "processor2_id": processor2_id,
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
                    sender_processor_type = "T1"
                    if sku:
                        context["milled_value"] =  calculate_milled_volume(int(bin_pull),sender_processor_type, sku)
                        context["selected_sku"] = sku
                    else:
                        context["milled_value"] =  calculate_milled_volume(int(bin_pull),sender_processor_type, sku)
                    processor2 = LinkProcessor1ToProcessor.objects.filter(processor1_id=bin_pull, processor2__processor_type__type_name = "T2").values("processor2__id", "processor2__entity_name")
                    context["processor2"] = processor2

                    context["selected_processor_sku_id_list"] = get_sku_list(int(bin_pull),sender_processor_type)["data"]
                    if processor2_id:                        
                        context["selected_destination"] = processor2_id.split()[0]
                        context["selected_destination_name"] = Processor2.objects.filter(id=processor2_id.split()[0]).first().entity_name
                        context["selected_processor_sku_id_list_processor2"] = get_sku_list(int(processor2_id.split()[0]),"T2")["data"]
                        
                    return render(request, 'processor2/recive_delevery.html', context)                
                    
                else:
                    try:
                        milled_value = float(context["milled_value"])
                    except ValueError:
                        context["error_messages"] = "Invalid input: milled_value is not a valid number."
                        return render(request, 'processor2/recive_delevery.html', context)
                    try:
                        volume_shipped = float(context["volume_shipped"])
                    except ValueError:
                        context["error_messages"] = "Invalid input: volume_shipped is not a valid number."
                        return render(request, 'processor2/recive_delevery.html', context)
                    if milled_value < volume_shipped:
                        context["error_messages"] = "Processor does not have the required milled volume."
                        return render(request, 'processor2/recive_delevery.html', context)
 
                    else:             
                        if context["weight_prod_unit_id"] == "LBS" :
                            cal_weight = round(float(context["weight_prod"]),2)
                        if context["weight_prod_unit_id"] == "BU" :
                            cal_weight = round(float(context["weight_prod"]) * 45,2)
                        if context["exp_yield_unit_id"] == "LBS" :
                            cal_exp_yield = round(float(context["exp_yield"]),2)
                        if context["exp_yield_unit_id"] == "BU" :
                            cal_exp_yield = round(float(context["exp_yield"]) * 45,2)

                        select_proc_id, processor_type = context["processor2_id"].split()
                        if processor_type == 'T2':
                            select_destination_ = Processor2.objects.get(id=select_proc_id).entity_name
                            receiver_processor_type = "T2"
                        
                        milled_volume = context["milled_value"]
                        volume_left = float(context["milled_value"]) - float(context["volume_shipped"])
                        shipment_id = generate_shipment_id()
                        
                        processor_e_name = Processor.objects.filter(id=int(bin_pull)).first().entity_name
                        save_shipment_management = ShipmentManagement(shipment_id=shipment_id,processor_idd=bin_pull,processor_e_name=processor_e_name, sender_processor_type="T1", bin_location=bin_pull,
                                equipment_type=context["equipment_type"],equipment_id=context["equipment_id"],storage_bin_send=context["storage_bin_id"],moisture_percent = context["moist_percentage"],weight_of_product_raw = context["weight_prod"],
                                weight_of_product=cal_weight,weight_of_product_unit=context["weight_prod_unit_id"], excepted_yield_raw =context["exp_yield"],excepted_yield=cal_exp_yield,excepted_yield_unit=context["exp_yield_unit_id"],recive_delivery_date=context["approval_date"],
                                purchase_order_number=context["purchase_number"],lot_number=context["lot_number"],volume_shipped=context["volume_shipped"],milled_volume=milled_volume,volume_left=volume_left,editable_obj=True,status=context["status"],
                                storage_bin_recive=context["receiver_sku_id"],ticket_number=context["ticket_number"],received_weight=context["received_weight"],processor2_idd=select_proc_id,processor2_name=select_destination_, receiver_processor_type=receiver_processor_type)
                        save_shipment_management.save()

                        processor1_id = Processor.objects.filter(id=int(bin_pull)).first().id
                        create_sku_list(processor1_id, save_shipment_management.sender_processor_type, save_shipment_management.storage_bin_send)
                        processor2_id = Processor2.objects.get(id=select_proc_id).id
                        create_sku_list(processor2_id, save_shipment_management.receiver_processor_type, save_shipment_management.storage_bin_recive)
                        files = request.FILES.getlist('files')
                        for file in files:
                            new_file = File.objects.create(file=file)
                            save_shipment_management.files.add(new_file)
                        save_shipment_management.save()
                        #logtable..........
                        log_type, log_status, log_device = "ShipmentManagement", "Added", "Web"
                        log_idd, log_name = save_shipment_management.id, save_shipment_management.bin_location
                        log_details = f"processor2 = {save_shipment_management.processor_e_name} | processor2_id = {save_shipment_management.processor_idd} | date_pulled = {save_shipment_management.date_pulled} | bin_location = {save_shipment_management.bin_location} | milled_volume = {save_shipment_management.milled_volume} | equipment_type = {save_shipment_management.equipment_type} | equipment_id = {save_shipment_management.equipment_id} | purchase_order_number = {save_shipment_management.purchase_order_number} | lot_number = {save_shipment_management.lot_number} | volume_shipped = {save_shipment_management.volume_shipped} | volume_left = {save_shipment_management.volume_left} | editable_obj = {save_shipment_management.editable_obj} "
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
                        update_obj = ShipmentManagement.objects.filter(processor_idd=int(bin_pull)).exclude(id=save_shipment_management.id).values('id','editable_obj')
                        
                        if update_obj.exists():
                            for i in update_obj :
                                get_obj = ShipmentManagement.objects.get(id=i['id'])
                                get_obj.editable_obj = False
                                get_obj.save()
                        else:
                            pass
                        return redirect('inbound_shipment_list')
            return render(request, 'processor2/recive_delevery.html', context)
        else:
            return redirect('dashboard')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'processor2/recive_delevery.html', context)


@login_required()
def rejected_shipments_csv_download_for_t2(request) :
    # superuser................  
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        today_date = date.today()
        filename = f'Rejected Shipments Tier2 CSV {today_date}.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['Shipment ID','Lot Number #','Shipment Date', 'Sender Processor','Receiver Processor','Volume Shipped (LBS)','Disapproval Date','Reason For Disapproval','Moisture Level'])
        output = ShipmentManagement.objects.filter(status='DISAPPROVED', receiver_processor_type="T2").order_by('-id').values('shipment_id','lot_number','date_pulled','processor_e_name','processor2_name',
                                                                                            'weight_of_product','recive_delivery_date','reason_for_disapproval','moisture_percent')
        for i in output:
            writer.writerow([
                i['shipment_id'], 
                i['lot_number'], 
                i['date_pulled'].strftime("%m-%d-%Y"),
                i['processor_e_name'], 
                i['processor2_name'], 
                i['volume_shipped'],
                i['recive_delivery_date'], 
                i['reason_for_disapproval'], 
                i['moisture_percent']])
        return response
    else:
        return redirect ('dashboard')


@login_required()
def all_shipments_csv_download_for_t2(request): 
    # superuser............... 
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        today_date = date.today()
        filename = f'All Shipments Tier2 CSV {today_date}.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        writer.writerow(['Shipment ID','Lot Number #','Shipment Date', 'Sender Processor','Receiver Processor','Purchase Order Number','Lot Number','Sender SKU Id','Receiver SKU Id','Volume Shipped','Weight Of Product','Expected Yield','Receiver Processor Type','Status','Received Weight','Ticket Number','Approval/Disapproval Date','Reason For Disapproval','Moisture Level'])
        output = ShipmentManagement.objects.filter(receiver_processor_type="T2").order_by('-id').values()
        for i in output:
            writer.writerow([
                i['shipment_id'], 
                i['lot_number'], 
                i['date_pulled'].strftime("%m-%d-%Y"),
                i['processor_e_name'], 
                i['processor2_name'], 
                i['purchase_order_number'],
                i['lot_number'],
                i['storage_bin_send'],
                i['storage_bin_recive'], 
                i['volume_shipped'],               
                i['weight_of_product'],
                i['excepted_yield'],
                i['receiver_processor_type'],
                i['status'],
                i['received_weight'],
                i['ticket_number'],
                i['recive_delivery_date'], 
                i['reason_for_disapproval'], 
                i['moisture_percent']])
        return response
    else:
        return redirect ('dashboard')


@login_required() 
def outbound_shipment_processor2_csv_download(request):  
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        filename = 'SHIPMENT MANAGEMENT TIER2.csv'
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="{}"'.format(filename)},
        )
        writer = csv.writer(response)
        # writer.writerow(['PROCESSOR', 'DATE PULLED', 'BIN LOCATION', 'MILLED VOLUME (LBS)', 'VOLUME SHIPPED (LBS)', 'BALANCE (LBS)', 'EQUIPMENT TYPE', 'EQUIPMENT ID', 'PURCHASE ORDER NUMBER', 'LOT NUMBER'])
        writer.writerow(['PROCESSOR', 'DATE PULLED', 'BIN LOCATION','SENDER SKU ID','RECEIVER SKU ID','WEIGHT OF PRODUCT','EXPECTED YIELD','MOISTURE PERCENTAGE','MILLED VOLUME (LBS)', 'VOLUME SHIPPED (LBS)', 'BALANCE (LBS)', 'EQUIPMENT TYPE', 'EQUIPMENT ID', 'PURCHASE ORDER NUMBER', 'LOT NUMBER','T2 PROCESSOR'])
        output = ShipmentManagement.objects.filter(sender_processor_type="T2").order_by('bin_location')
        for i in output:            
           
            writer.writerow([i.processor_e_name, i.date_pulled, i.bin_location,i.storage_bin_send,i.storage_bin_recive, i.weight_of_product ,i.excepted_yield,i.moisture_percent, i.milled_volume, i.volume_shipped, i.volume_left, 
            i.equipment_type, i.equipment_id, i.purchase_order_number, i.lot_number,i.processor2_name])
        return response   
    else:
        return redirect("dashboard")


@login_required()
def processor2_processor_management(request):
    context ={}
    try:
        if request.user.is_authenticated:
            # Superuser................
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                processor2 = Processor2.objects.filter(processor_type__type_name="T2")  #24/04/2024
                context['Processor1'] = processor2
                link_processor_to_processor_all = LinkProcessorToProcessor.objects.filter(processor__processor_type__type_name="T2")
                                        
                pro1_id = request.GET.get('pro1_id','')
                context['selectedpro1'] = pro1_id
                if pro1_id and pro1_id != 'All':
                    link_processor_to_processor_all  = link_processor_to_processor_all.filter(processor_id=int(pro1_id))
                
                paginator = Paginator(link_processor_to_processor_all, 20)
                page = request.GET.get('page')
                try:
                    report = paginator.page(page)
                except PageNotAnInteger:
                    report = paginator.page(1)
                except EmptyPage:
                    report = paginator.page(paginator.num_pages)
                context['link_processor_to_processor_all'] = report           
                            
                return render(request, 'processor2/processor2_processor_management.html',context)
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'processor2/processor2_processor_management.html',context)


@login_required
def link_processor_two(request):
    context = {}
    try:
        # Superuser....................
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            processor2 = Processor2.objects.filter(processor_type__type_name="T2")           
            context["processor2"] = processor2
            context["processor3"] = []
            context["processor4"] = []

            if request.method == "POST" :
                selected_processor = request.POST.get("processor_id")
                button_click = request.POST.get("save")
                if selected_processor and  not button_click:
                    context["selectedprocessor"] = int(selected_processor)
                    link_processor2 = list(LinkProcessorToProcessor.objects.filter(processor_id=selected_processor).values_list("linked_processor", flat = True))
                    processor_two = Processor2.objects.exclude(id__in=link_processor2)
                    processor3 = processor_two.filter(processor_type__type_name="T3")
                    processor4 = processor_two.filter(processor_type__type_name="T4")
                    context["processor3"] = processor3
                    context["processor4"] = processor4
                    return render(request, 'processor2/link_processor2.html', context)
                else:
                    select_processor2 = request.POST.getlist("select_processor2")
                    #print(selected_processor, select_processor2)
                    for i in select_processor2:
                        pro_id , pro_type = i.split(" ")
                        link_pro = LinkProcessorToProcessor(processor_id = selected_processor, linked_processor_id = pro_id)
                        link_pro.save()
                        # logtable.......
                        log_type, log_status, log_device = "LinkProcessorToProcessor", "Added", "Web"
                        log_idd, log_name = link_pro.id, f"{link_pro.processor.entity_name} - {link_pro.linked_processor.entity_name}"
                        log_details = f"tier2 processor id = {link_pro.processor.id} | linked processor id = {link_pro.linked_processor.id} | tier2 processor name= {link_pro.processor.entity_name} | linked processor name = {link_pro.linked_processor.entity_name} | "
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
                        # puser_id_all = ProcessorUser2.objects.filter(processor_id=pro_id)
                        # if int(counter) == 1 :
                        #     for j in puser_id_all :                                
                        #         msg = f"A new tier2 processor with name: {link_pro.processor.entity_name} is assigned to you"
                        #         p_user_id = User.objects.get(username=j.contact_email)
                        #         notification_reason = 'Processor Assigned'
                        #         redirect_url = "/processor2/processor2_processor_management"
                        #         save_notification = ShowNotification(user_id_to_show=p_user_id.id,msg=msg,status="UNREAD",redirect_url=redirect_url,
                        #         notification_reason=notification_reason)
                        #         save_notification.save()                           

                    return redirect('processor2_processor_management')                   

            return render(request, 'processor2/link_processor2.html', context)
        else:
            return redirect("dashboard") 
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'processor2/link_processor2.html', context)


@login_required()
def delete_link_processor_two(request, pk):
    context = {}
    try:
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            link = LinkProcessorToProcessor.objects.get(id=pk)
            LinkProcessorToProcessor.objects.filter(id=pk).delete()
            # logtable......
            log_type, log_status, log_device = "ProcessorToProcessorManagement", "Deleted", "Web"
            log_idd, log_name = link.id, f"{link.processor.entity_name} - {link.linked_processor.entity_name}"
            log_details = f"tier2_processor_name = {link.processor.entity_name} | tier2_processor_id = {link.processor.id} | Linked_processor_name = {link.linked_processor.entity_name} | Linked_processor_id = {link.linked_processor.id} | "
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
            return redirect('processor2_processor_management')
        else:
            return redirect('dashboard')
    except Exception as e:
        context["error_messages"] = str(e)
        return HttpResponse(e)


@login_required()
def inbound_production_management(request): 
    context = {}
    try:
        # Superuser..............
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            output = ProductionManagementProcessor2.objects.filter(processor__processor_type__type_name="T2").order_by('processor_e_name','-id')
            p_id = [i.processor.id for i in output]
            processors = Processor2.objects.filter(id__in = p_id).order_by('entity_name')
            context['processors'] = processors            
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
            return render (request, 'processor2/inbound_production_management.html', context)        
        else:
            return redirect ('dashboard')
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'processor2/inbound_production_management.html', context)


@login_required()
def add_volume_pulled_processor2(request):   
    context = {}
    try:
        # Superuser..............
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            get_processor = Processor2.objects.filter(processor_type__type_name="T2").order_by('entity_name')
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
                        return redirect ('inbound_production_management')
                else:
                    pass
            return render (request, 'processor2/add_volume_pulled.html', context)        
        else:
            return redirect ('dashboard')
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'processor2/add_volume_pulled.html', context)


@login_required()
def edit_volume_pulled_processor2(request,pk):   
    context = {}
    try:
        # superuser..............
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
                        return redirect ('inbound_production_management')
            else:
                messages.error(request,'This is not a valid request')
                return render (request, 'processor2/edit_volume_pulled.html', context)        
            return render (request, 'processor2/edit_volume_pulled.html', context)
        else:
            return redirect ('dashboard')
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'processor2/edit_volume_pulled.html', context)


@login_required()
def delete_volume_pulled_processor2(request,pk):
    context = {}
    try:  
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
            return redirect ('inbound_production_management')
        else:        
            return redirect ('dashboard')
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'processor2/inbound_production_management.html', context)


