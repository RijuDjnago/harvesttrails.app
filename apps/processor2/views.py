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
import random
from django.core.mail import send_mail
from datetime import date
from django.db.models import Q
import csv
import pandas as pd
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
# Create your views here.


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
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        processor2 = ProcessorUser2.objects.all()
        context['processor'] = processor2
        return render(request, 'processor2/list_processor2.html',context)
    # Processor 
    if request.user.is_processor2 :
        pass

@login_required()
def add_processor2(request):
    context = {}
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
                processor2 = Processor2(fein=fein,entity_name=entity_name,billing_address=billing_address,shipping_address=shipping_address,main_number=main_number,main_fax=main_fax,website=website)
                processor2.save()
                
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
                for i in range(1,int(counter)+1):
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
                        user.role.add(Role.objects.get(role='Processor2'))
                        user.is_processor2=True
                        user.is_active=True
                        user.set_password(password)
                        user.password_raw = password
                        user.save()

                        # 20-04-23 Log Table
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
    # Processor 
    if request.user.is_processor2 :
        pass

@login_required()
def processor2_update(request,pk):
    context = {}
    # superadmin and others ................
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        obj_id = ProcessorUser2.objects.get(id=pk)
        context['p_user'] = obj_id
        processor2 = Processor2.objects.get(id=obj_id.processor2_id)
        context['form'] = ProcessorForm2(instance=processor2)
        processor_email = obj_id.contact_email
        user = User.objects.get(email=processor_email)
        if request.method == 'POST':
            form = ProcessorForm2( request.POST,instance=processor2)
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
        return redirect('login')


@login_required()
def processor2_delete(request,pk):
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
    return HttpResponse (1)

@login_required()
def processor2_change_password(request,pk):
    context={}
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        pp = ProcessorUser2.objects.get(id=pk)
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
    if request.user.is_processor2 :
        pass


@login_required()
def add_processor2_user(request,pk):
    context = {}
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
                    user.role.add(Role.objects.get(role='Processor2'))
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
        return redirect('login')


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
        return redirect('/')
    

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
def t2_classing_ewr_report_all_downlaod(request,p2_id,level):
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


@login_required()
def processor2_add_receive_delivery(request):
    if request.user.is_authenticated:
        context = {}
        status = ""
        
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            grower = LinkGrowerToProcessor.objects.all()
            grower_id = [i.grower_id for i in grower]
            get_grower = Grower.objects.filter(id__in = grower_id).order_by('name')
            context['get_grower'] = get_grower
            get_processor2 = Processor2.objects.all()
            context['get_processor2'] = get_processor2
            
            context['g_display'] = "none"
            context['p_display'] = "none"
            
            if request.method == 'POST':
                id_grower = request.POST.get('id_grower')
                processor_id = request.POST.get('processor_id')
                files = request.FILES.getlist('files')   #add file
                select_desti = request.POST.get('id_desti')   #add destination
                # print("select_desti================",select_desti)
                # if select_desti == 'Grower':
                if id_grower !='all':
                    selected_grower = Grower.objects.get(id=id_grower)
                    context['selected_grower'] = selected_grower

                    storage_obj = Storage.objects.filter(grower_id=id_grower)
                    context['storage'] = storage_obj

                    field_obj = Field.objects.filter(grower_id=id_grower) 
                    context['field'] = field_obj
                    context['g_display'] = "block"
                    context['p_display'] = "none"

                    
                    # # get_crop = Field.objects.filter(grower_id=id_grower).values('crop').distinct()
                    get_crop = Field.objects.filter(grower_id=id_grower, crop='RICE').values('crop').distinct()
                    # print("get_crop=================",get_crop)
                    # print("get_crop=================",get_crop[0]['crop'])
                    context['get_crop'] = get_crop[0]['crop'] 

                    id_storage = request.POST.get('id_storage')
                    id_field = request.POST.get('id_field')
                    module_number = request.POST.get('module_number')
                    
                    id_status = request.POST.get('id_status')
                    print("id_status=============================",id_status)

                    amount1 = request.POST.get('amount1')
                    amount2 = request.POST.get('amount2')
                    
                    id_unit1 = request.POST.get('id_unit1')
                    id_unit2= request.POST.get('id_unit2')

                    get_output= request.POST.get('get_output')
                    shipment_id = generate_shipment_id()
                    
                    recieved_weight= request.POST.get('recieved_weight')
                    sku_id = request.POST.get('sku_id')  #add sku
                    files = request.FILES.getlist('files')

                    ticket_number= request.POST.get('ticket_number')
                    approval_date= request.POST.get('approval_date')

                    reason_for_disapproval= request.POST.get('reason_for_disapproval')
                    moisture_level= request.POST.get('moisture_level')
                    fancy_count= request.POST.get('fancy_count')
                    head_count= request.POST.get('head_count')
                    bin_location_processor= request.POST.get('bin_location_processor')
                    
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
                        print("field=========",field)
                        crop = field.crop
                        if crop == "RICE":
                            status = ""
                        # if crop == "RICE":
                        #     status = "APPROVED"
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
                      
                        if id_status != None and id_status != "blank" and get_crop !='COTTON' :
                            if id_status == 'APPROVED' and recieved_weight :
                                print("recieved_weight---------------",recieved_weight)
                                shipment = GrowerShipment(status=id_status,total_amount=get_output,unit_type2=id_unit2,amount2=amount2,echelon_id=field.eschlon_id,
                                                        sustainability_score=surveyscore,amount=amount1,variety=field.variety,crop=field.crop,shipment_id=shipment_id,processor_id=processor_id,grower_id=selected_grower.id,
                                                        storage_id=id_storage,field_id=id_field,module_number=module_number,unit_type=id_unit1,received_amount =recieved_weight,sku = sku_id,token_id=ticket_number,approval_date = approval_date,moisture_level=moisture_level,fancy_count=fancy_count,head_count=head_count,bin_location_processor=bin_location_processor,sender = select_desti)
                                shipment.save()  
                                for file in files:
                                    new_file = GrowerShipmentFile.objects.create(file=file)
                                    shipment.files.add(new_file)
                                    
                                # shipment.status=id_status
                                # shipment.received_amount=recieved_weight
                                # shipment.sku=sku_id  #add sku
                                # shipment.token_id=ticket_number

                                # if approval_date :
                                #     shipment.approval_date = approval_date
                                # else:
                                #     shipment.approval_date= date.today()

                                # shipment.moisture_level=moisture_level
                                # shipment.fancy_count=fancy_count
                                # shipment.head_count=head_count
                                # shipment.bin_location_processor=bin_location_processor
                                
                                # shipment.save()
                                

                                msg_subject = 'Shipment is received as Approved'
                                msg_body = f'Dear Admin,\n\nA new shipment has been approved.\n\nThe details of the same are as below: \n\nShipment ID: {shipment.shipment_id} \nGrower: {shipment.grower.name} \nField: {shipment.field.name} \nReceived weight: {recieved_weight} LBS \nReceived date: {shipment.approval_date} \n\nRegards\nCustomer Service\nAgreeta'
                                from_email = 'techsupportUS@agreeta.com'
                                to_email = ['customerservice@agreeta.com']
                                # send_mail(
                                # msg_subject,
                                # msg_body,
                                # from_email,
                                # to_email,
                                # fail_silently=False,
                                # )

                            elif id_status == 'DISAPPROVED' and reason_for_disapproval :
                                pass
                                # shipment.status=id_status
                                # shipment.reason_for_disapproval=reason_for_disapproval
                                # shipment.moisture_level=moisture_level
                                # shipment.fancy_count=fancy_count
                                # shipment.head_count=head_count
                                # shipment.bin_location_processor=bin_location_processor
                                # shipment.approval_date= date.today()

                                # shipment.save()    
            
                # else: 
                #     if processor_id !='all': 
                #         pass 
                    
                        
            return render(request, 'processor2/add_p2_receive_delivery.html',context)
        else:
            return render(request, 'processor2/add_p2_receive_delivery.html',context)
    else:
        return redirect('login')

def processor2_receive_delivery(request):
    if request.user.is_authenticated:
        context = {}
        status = ""        
        if request.method == "POST":
            selected_source = request.POST.get('selected_source')
            if selected_source == "grower":
                if request.user.is_processor2:            
                    user_email = request.user.email
                    p = ProcessorUser2.objects.get(contact_email=user_email)
                    processor_id = Processor2.objects.get(id=p.processor_id).id
                    growers = LinkToProcessor2.objects.filter(processor2_id=processor_id)
                    growers_id = [i.grower_id for i in growers if i.grower]
                    get_growers = Grower.objects.filter(id__in=growers_id)
                    context["get_grower"] = get_growers
                if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                    growers = LinkToProcessor2.objects.all()
                    growers_id = [i.grower_id for i in growers if i.grower]
                    get_growers = Grower.objects.filter(id__in=growers_id)
                    context["get_grower"] = get_growers
                id_grower = request.POST.get("id_grower")
                if id_grower == 'all':
                    context["message"] = "Select any one grower."
                else:
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
                    files = request.FILES.getlist('files')
                    
                    recieved_weight= request.POST.get('recieved_weight')
                    sku_id = request.POST.get('sku_id')
                    ticket_number= request.POST.get('ticket_number')
                    approval_date= request.POST.get('approval_date')

                    moisture_level= request.POST.get('moisture_level')
                    fancy_count= request.POST.get('fancy_count')
                    head_count= request.POST.get('head_count')
                    bin_location_processor= request.POST.get('bin_location_processor')
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
                        # if crop == "RICE":
                        #     status = ""
                        if crop == "RICE":
                            status = "APPROVED"
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
                        # shipment = GrowerShipment(status=status,total_amount=get_output,unit_type2=id_unit2,amount2=amount2,echelon_id=field.eschlon_id,sustainability_score=surveyscore,amount=amount1,variety=field.variety,crop=field.crop,shipment_id=shipment_id,processor_id=processor_id,grower_id=selected_grower.id,storage_id=id_storage,field_id=id_field,module_number=module_number,unit_type=id_unit1)
                        # shipment.save()
                        
                        shipment = GrowerShipmentToProcessor2(status=status,total_amount=get_output,unit_type2=id_unit2,amount2=amount2,echelon_id=field.eschlon_id,
                                                        sustainability_score=surveyscore,amount=amount1,variety=field.variety,crop=field.crop,shipment_id=shipment_id,processor_id=processor_id,grower_id=selected_grower.id,
                                                        storage_id=id_storage,field_id=id_field,module_number=module_number,unit_type=id_unit1,received_amount =recieved_weight,sku = sku_id,token_id=ticket_number,
                                                        approval_date = approval_date,moisture_level=moisture_level,fancy_count=fancy_count,head_count=head_count,bin_location_processor=bin_location_processor)
                        shipment.save()
                        for file in files:
                            new_file = GrowerShipmentFile.objects.create(file=file)
                            shipment.files.add(new_file)
                        
                        
                        
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

                        return redirect('processor2_inbound_management')
            if selected_source == "processor":
                if request.user.is_processor2:            
                    user_email = request.user.email
                    p = ProcessorUser2.objects.get(contact_email=user_email)
                    processor_id = Processor2.objects.get(id=p.processor_id).id
                    processors = LinkToProcessor2.objects.filter(processor2_id=processor_id)
                    processors_id = [i.grower_id for i in processors if i.processor]
                    get_processors = Processor.objects.filter(id__in=processors_id)
                    context["get_processor"] = get_processors
                if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                    processors = LinkToProcessor2.objects.all()
                    processors_id = [i.grower_id for i in processors if i.processor]
                    get_processors = Processor.objects.filter(id__in=processors_id)
                    context["get_processor"] = get_processors
                id_processor = request.POST.get("id_processor")
                selected_processor = Processor.objects.filter(id=id_processor)
                context["selected_processor"] = selected_processor
        else:
            return render(request, "processor2/processor2_receive_delivery.html", context)
    else:
        return redirect('login')
                    



