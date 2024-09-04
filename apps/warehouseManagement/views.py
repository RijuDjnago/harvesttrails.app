import string
import random
from django.shortcuts import render, redirect
from apps.warehouseManagement.models import *
from apps.warehouseManagement.forms import *
from apps.processor.models import Processor, ProcessorUser
from apps.processor2.models import Processor2, ProcessorUser2
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from apps.accounts.models import User, Role, ShowNotification, LogTable
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from apps.processor.views import calculate_milled_volume, get_sku_list
# Create your views here.

characters = list(string.ascii_letters + string.digits + "@#$%")
def generate_random_password():
	length = 8
	random.shuffle(characters)
	password = []
	for i in range(length):
		password.append(random.choice(characters))
	return "".join(password)


@login_required()
def add_distributor(request):
    context = {}
    try:
        if request.user.is_authenticated:
            # superuser.................
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                form = DistributorForm()
                context["form"] = form
                if request.method == 'POST':
                    form = DistributorForm(request.POST)                   
                    entity_name = request.POST.get('entity_name')
                    warehouse_ids  = request.POST.getlist('warehouse')
                    location = request.POST.get('location')
                    latitude  = request.POST.get('latitude ')
                    longitude = request.POST.get('longitude')                    
                
                    distributor = Distributor.objects.create(entity_name=entity_name,location=location,latitude =latitude ,longitude=longitude)
                    for warehouse_id in warehouse_ids:
                        try:
                            warehouse = Warehouse.objects.get(id=warehouse_id)
                            distributor.warehouse.add(warehouse)
                        except Warehouse.DoesNotExist:
                            pass  # Handle error or continue as per your need
                                
                    log_type, log_status, log_device = "Distributor", "Added", "Web"
                    log_idd, log_name = distributor.id, entity_name
                    log_email = None
                    log_details = (f"entity_name = {entity_name} | location = {location} | "
                           f"latitude = {latitude} | longitude = {longitude}")
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
                    
                    dis = Distributor.objects.get(entity_name=entity_name,location=location,latitude =latitude ,longitude=longitude)
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
                            
                            distributor_user = DistributorUser.objects.create(distributor_id = dis.id,contact_name=contact_name,contact_email=contact_email,contact_phone=contact_phone,contact_fax=contact_fax,p_password_raw=password)
                            
                            user = User.objects.create(email=contact_email, username=contact_email,first_name=contact_name)
                            user.role.add(Role.objects.get(role='Distributor'))
                            user.is_distributor=True
                            user.is_active=True
                            user.set_password(password)
                            user.password_raw = password
                            user.save()
                            
                            log_type, log_status, log_device = "DistributorUser", "Added", "Web"
                            log_idd, log_name = distributor_user.id, contact_name
                            log_email = contact_email
                            log_details = f"distributor_id = {dis.id} | distributor = {dis.entity_name} | contact_name= {contact_name} | contact_email = {contact_email} | contact_phone = {contact_phone} | contact_fax = {contact_fax} | p_password_raw = {password}"
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
                    return redirect('list-distributor')                    
                return render(request, 'distributor/add_distributor.html',context)
            else:
                messages.error(request, "Not a valid request.")
                return redirect("dashboard")
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/add_distributor.html',context)


@login_required()
def add_distributor_user(request,pk):
    context = {}
    try:
        if request.user.is_authenticated:        
            # superuser..............
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                distributor_user = DistributorUser.objects.get(id=pk)
                distributor_id = distributor_user.distributor.id
                distributor = Distributor.objects.get(id=distributor_id)
                context['distributor'] = distributor
                distributor_user = DistributorUser.objects.filter(distributor_id = distributor.id)
                context['distributor_user'] = distributor_user
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
                            
                            dis_user = DistributorUser(distributor_id = distributor_id,contact_name=contact_name,contact_email=contact_email,contact_phone=contact_phone,contact_fax=contact_fax,p_password_raw=password)
                            dis_user.save()
                            user = User.objects.create(email=contact_email, username=contact_email,first_name=contact_name)
                            user.role.add(Role.objects.get(role='Distributor'))
                            user.is_distributor=True
                            user.is_active=True
                            user.set_password(password)
                            user.password_raw = password
                            user.save()

                            # 07-04-23 Log Table
                            log_type, log_status, log_device = "DistributorUser", "Added", "Web"
                            log_idd, log_name = dis_user.id, contact_name
                            log_email = contact_email
                            log_details = f"distributor_id = {distributor_id} | distributor = {distributor.entity_name}  | contact_name= {contact_name} | contact_email = {contact_email} | contact_phone = {contact_phone} | contact_fax = {contact_fax}"
                            
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

                    return redirect('list-distributor')
                return render(request, 'distributor/add_distributor_user.html',context)
            # processor ..............
            elif request.user.is_distributor:
                distributor_user = DistributorUser.objects.get(id=pk)
                distributor_id = distributor_user.distributor.id
                distributor = Distributor.objects.get(id=distributor_id)
                context['distributor'] = distributor
                distributor_user = DistributorUser.objects.filter(distributor_id = distributor.id)
                context['distributor_user'] = distributor_user
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
                            
                            dis_user = DistributorUser(distributor_id = distributor_id,contact_name=contact_name,contact_email=contact_email,contact_phone=contact_phone,contact_fax=contact_fax,p_password_raw=password)
                            dis_user.save()
                            user = User.objects.create(email=contact_email, username=contact_email,first_name=contact_name)
                            user.role.add(Role.objects.get(role='Distributor'))
                            user.is_distributor=True
                            user.is_active=True
                            user.set_password(password)
                            user.password_raw = password
                            user.save()

                            # 07-04-23 Log Table
                            log_type, log_status, log_device = "DistributorUser", "Added", "Web"
                            log_idd, log_name = dis_user.id, contact_name
                            log_email = contact_email
                            log_details = f"distributor_id = {distributor_id} | distributor = {distributor.entity_name}  | contact_name= {contact_name} | contact_email = {contact_email} | contact_phone = {contact_phone} | contact_fax = {contact_fax}"
                            
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

                    return redirect('list-distributor')
                return render(request, 'distributor/add_distributor_user.html',context)
            
            else:
                messages.error(request, "Not a valid request")
                return redirect("dashboard")
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/add_distributor_user.html',context)


@login_required()
def distributor_list(request):
    context = {}
    try:
        if request.user.is_authenticated:
            distributor = []
            search_name = request.GET.get('search_name', '')
            if 'Grower' in request.user.get_role() and not request.user.is_superuser:
                pass
            elif request.user.is_consultant:
                pass
            elif request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                distributor = DistributorUser.objects.all()
                if search_name:
                    distributor = distributor.filter(Q(contact_name__icontains=search_name) | Q(distributor__entity_name__icontains=search_name)| Q(contact_email__icontains=search_name))
                    context['search_name'] = search_name
            elif request.user.is_distributor:
                dis = DistributorUser.objects.filter(contact_email=request.user.email).first()
                entity_name = dis.distributor
                distributor = DistributorUser.objects.filter(distributor=entity_name)
                if search_name:
                    distributor = distributor.filter(Q(contact_name__icontains=search_name) | Q(distributor__entity_name__icontains=search_name)| Q(contact_email__icontains=search_name))
                    context['search_name'] = search_name
            else:
                messages.error(request, "Not a valid request")
                return redirect("dashboard")

            # Pagination
            distributor = distributor.order_by("-id")
            paginator = Paginator(distributor, 20) 
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['page_obj'] = page_obj            

            return render(request, 'distributor/list_distributor.html', context)
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/list_distributor.html', context)


@login_required()
def distributor_update(request,pk):
    context = {}
    try:
        if request.user.is_authenticated:        
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                obj_id = DistributorUser.objects.get(id=pk)
                print(obj_id)
                context['p_user'] = obj_id
                distributor = Distributor.objects.get(id=obj_id.distributor.id)

                context['form'] = DistributorForm(instance=distributor)
                distributor_email = obj_id.contact_email
                user = User.objects.get(email=distributor_email)
                if request.method == 'POST':                   
                    form = DistributorForm( request.POST,instance=distributor)                    
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
                        if email_update != distributor_email:
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
                        log_type, log_status, log_device = "DistributorUser", "Edited", "Web"
                        log_idd, log_name = obj_id.id, name_update
                        log_details = f"distributor_id = {distributor.id} | distributor = {distributor.entity_name}  | contact_name= {name_update} | contact_email = {email_update} | contact_phone = {phone_update} | contact_fax = {fax_update}"
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
                        return redirect('list-distributor')
                return render(request, 'distributor/update_distributor.html',context)
            # distributor..........
            elif request.user.is_distributor:
                obj_id = DistributorUser.objects.get(id=pk)
                context['p_user'] = obj_id
                distributor = Distributor.objects.get(id=obj_id.distributor.id)

                context['form'] = DistributorForm(instance=distributor)
                distributor_email = obj_id.contact_email
                user = User.objects.get(email=distributor_email)
                if request.method == 'POST':
                    form = DistributorForm( request.POST,instance=distributor)
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
                        if email_update != distributor_email:
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
                        log_type, log_status, log_device = "DistributorUser", "Edited", "Web"
                        log_idd, log_name = obj_id.id, name_update
                        log_details = f"distributor_id = {distributor.id} | distributor = {distributor.entity_name}  | contact_name= {name_update} | contact_email = {email_update} | contact_phone = {phone_update} | contact_fax = {fax_update}"
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
                        return redirect('list-distributor')
                return render(request, 'distributor/update_distributor.html',context)
            else:
                messages.error(request, "Not a valid request")
                return redirect("dashboard")
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/update_distributor.html',context)


@login_required()
def distributor_change_password(request,pk):
    context={}
    try:
        # Superuser..............
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            dist = DistributorUser.objects.get(id=pk)
            user = User.objects.get(email=dist.contact_email)
            context["userr"] = user
            if request.method == "POST":
                password1 = request.POST.get("password1")
                password2 = request.POST.get("password2")
                if len(password1) != 0 and len(password2) != 0 and password1 != None and password2 != None and password1 == password2:
                    # update_pass_user = User.objects.get(id=pk)
                    password = make_password(password1)
                    user.password = password
                    user.password_raw = password1
                    user.save()
                    dist.p_password_raw = password1
                    dist.save()
                    # 10-04-23 Log Table
                    log_type, log_status, log_device = "DistributorUser", "Password changed", "Web"
                    log_idd, log_name = dist.id, dist.contact_name
                    log_email = dist.contact_email
                    log_details = f"distributor_id = {dist.distributor.id} | distributor = {dist.distributor.entity_name} | contact_name= {dist.contact_name} | contact_email = {dist.contact_email} | contact_phone = {dist.contact_phone} | contact_fax = {dist.contact_fax}"
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
            return render (request, 'distributor/distributor_change_password.html', context)
        # Distributor...............
        elif request.user.is_distributor:
            dist = DistributorUser.objects.get(id=pk)
            user = User.objects.get(email=dist.contact_email)
            context["userr"] = user
            if request.method == "POST":
                password1 = request.POST.get("password1")
                password2 = request.POST.get("password2")
                if len(password1) != 0 and len(password2) != 0 and password1 != None and password2 != None and password1 == password2:
                    # update_pass_user = User.objects.get(id=pk)
                    password = make_password(password1)
                    user.password = password
                    user.password_raw = password1
                    user.save()
                    dist.p_password_raw = password1
                    dist.save()
                    # 10-04-23 Log Table
                    log_type, log_status, log_device = "DistributorUser", "Password changed", "Web"
                    log_idd, log_name = dist.id, dist.contact_name
                    log_email = dist.contact_email
                    log_details = f"distributor_id = {dist.distributor.id} | distributor = {dist.distributor.entity_name} | contact_name= {dist.contact_name} | contact_email = {dist.contact_email} | contact_phone = {dist.contact_phone} | contact_fax = {dist.contact_fax}"
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
        
        else:
            return redirect('dashboard')
        return render (request, 'distributor/distributor_change_password.html', context)
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'distributor/distributor_change_password.html', context)


@login_required()
def add_warehouse(request):
    context = {}
    try:
        if request.user.is_authenticated:
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role() or request.user.is_distributor:
                form = WarehouseForm()
                context["form"] = form
                if request.method == 'POST':
                    form = WarehouseForm(request.POST)
                    
                    name = request.POST.get('name')
                    location = request.POST.get('location')
                    latitude = request.POST.get('latitude')
                    longitude = request.POST.get('longitude')
                    status = request.POST.get('status')
                    distributor = request.POST.get('distributor')

                    # Check if a warehouse with the same name already exists
                    if Warehouse.objects.filter(name=name).exists():
                        messages.error(request, "A warehouse with this name already exists.")
                        return render(request, 'distributor/add_warehouse.html', context)

                    # Create the warehouse
                    warehouse = Warehouse.objects.create(
                        name=name,
                        location=location,
                        latitude=latitude,
                        longitude=longitude,
                        status=status
                    )
                    check_distributor = Distributor.objects.filter(id=distributor)
                    if check_distributor:
                        get_distributor = check_distributor.first()
                        get_distributor.warehouse.add(warehouse)

                    # Log the action
                    log_type, log_status, log_device = "Warehouse", "Added", "Web"
                    log_idd, log_name = warehouse.id, name
                    log_email = None
                    log_details = (f"name = {name} | location = {location} | "
                                    f"latitude = {latitude} | longitude = {longitude} | status = {status}")
                    action_by_userid = request.user.id
                    userr = User.objects.get(pk=action_by_userid)
                    user_role = userr.role.all()
                    action_by_username = f'{userr.first_name} {userr.last_name}'
                    action_by_email = userr.username
                    action_by_role = "superuser" if request.user.id == 1 else str(','.join([str(i.role) for i in user_role]))
                    logtable = LogTable(
                        log_type=log_type, log_status=log_status, log_idd=log_idd, log_name=log_name,
                        action_by_userid=action_by_userid, action_by_username=action_by_username,
                        action_by_email=action_by_email, action_by_role=action_by_role, log_email=log_email,
                        log_details=log_details, log_device=log_device
                    )
                    logtable.save()

                    # Add the single warehouse user
                    user_name = request.POST.get('user_name')
                    user_email = request.POST.get('user_email')
                    user_phone = request.POST.get('user_phone')
                    user_fax = request.POST.get('user_fax')
                    print(user_name, user_email, user_phone, user_fax)

                    if WarehouseUser.objects.filter(warehouse=warehouse).exists():                       
                        messages.error(request, "A user is already associated with this warehouse.")
                        return render(request, 'distributor/add_warehouse.html', context)

                    if User.objects.filter(email=user_email).exists():                        
                        messages.error(request, f'Email {user_email} already exists.')
                    else:
                        password = generate_random_password()                        
                        warehouse_user = WarehouseUser.objects.create(
                            warehouse=warehouse,
                            contact_name=user_name,
                            contact_email=user_email,
                            contact_phone=user_phone,
                            contact_fax=user_fax,
                            p_password_raw=password
                        )                    
                        user = User.objects.create(email=user_email, username=user_email,first_name=user_name)
                        user.role.add(Role.objects.get(role='WarehouseManager'))
                        user.is_warehouse_manager=True
                        user.is_active=True
                        user.set_password(password)
                        user.password_raw = password
                        user.save()

                        # Log the action for user creation
                        log_type, log_status, log_device = "WarehouseManager", "Added", "Web"
                        log_idd, log_name = warehouse_user.id, user_name
                        log_email = user_email
                        log_details = (f"warehouse_id = {warehouse.id} | warehouse = {warehouse.name} | "
                                        f"user_name= {user_name} | user_email = {user_email} | "
                                        f"user_phone = {user_phone} | user_fax = {user_fax} | password_raw = {password}")
                        logtable = LogTable(
                            log_type=log_type, log_status=log_status, log_idd=log_idd, log_name=log_name,
                            action_by_userid=action_by_userid, action_by_username=action_by_username,
                            action_by_email=action_by_email, action_by_role=action_by_role, log_email=log_email,
                            log_details=log_details, log_device=log_device
                        )
                        logtable.save()

                    return redirect('list-warehouse')                

                return render(request, 'distributor/add_warehouse.html', context)
            else:
                messages.error(request, "Not a valid request.")
                return redirect("dashboard")
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/add_warehouse.html', context)


@login_required()
def list_warehouse(request):
    context = {}
    try:
        if request.user.is_authenticated:
            warehouse = []
            search_name = request.GET.get('search_name', '')
            if 'Grower' in request.user.get_role() and not request.user.is_superuser:
                pass
            elif request.user.is_consultant:
                pass
            elif request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                warehouse = WarehouseUser.objects.all().select_related('warehouse').prefetch_related('warehouse__distributor_set')
                if search_name:
                    warehouse = warehouse.filter(Q(contact_name__icontains=search_name) | Q(warehouse__name__icontains=search_name)| Q(contact_email__icontains=search_name))
                    context['search_name'] = search_name
            elif request.user.is_warehouse_manager:
                warehouse_user= WarehouseUser.objects.filter(contact_email=request.user.email).select_related('warehouse').prefetch_related('warehouse__distributor_set').first()
                entity_name = warehouse_user.warehouse
                warehouse = WarehouseUser.objects.filter(warehouse=entity_name).select_related('warehouse').prefetch_related('warehouse__distributor_set')
                if search_name:
                    warehouse = warehouse.filter(Q(contact_name__icontains=search_name) | Q(warehouse__name__icontains=search_name)| Q(contact_email__icontains=search_name))
                    context['search_name'] = search_name

            elif request.user.is_distributor:
                distributor_user = DistributorUser.objects.filter(contact_email=request.user.email).select_related('distributor').first()
                warehouse_queryset = distributor_user.distributor.warehouse.all()  # Get the warehouses
                warehouse = WarehouseUser.objects.filter(warehouse__in=warehouse_queryset).select_related('warehouse').prefetch_related('warehouse__distributor_set')
                print(warehouse)

                # Optionally, filter based on the search criteria
                if search_name:
                    warehouse = warehouse.filter(
                        Q(name__icontains=search_name) |
                        Q(location__icontains=search_name) |
                        Q(warehouse_user__contact_name__icontains=search_name) |
                        Q(warehouse_user__contact_email__icontains=search_name)
            )
                    context['search_name'] = search_name
            else:
                messages.error(request, "Not a valid request")
                return redirect("dashboard")

            # Pagination
            warehouse = warehouse.order_by("-id")
            paginator = Paginator(warehouse, 20) 
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['page_obj'] = page_obj          

            return render(request, 'distributor/list_warehouse.html', context)
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/list_warehouse.html', context)


@login_required()
def warehouse_update(request,pk):
    context = {}
    try:
        if request.user.is_authenticated:        
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                obj_id = WarehouseUser.objects.get(id=pk)
                print(obj_id)
                context['p_user'] = obj_id
                warehouse = Warehouse.objects.get(id=obj_id.warehouse.id)

                context['form'] = WarehouseForm(instance=warehouse)
                warehouse_email = obj_id.contact_email
                user = User.objects.get(email=warehouse_email)
                if request.method == 'POST':                   
                    form = WarehouseForm( request.POST,instance=warehouse)                    
                    if form.is_valid(): 
                        distributor = request.POST.get('distributor')                       
                                            
                        email_update = request.POST.get('contact_email1')
                        name_update = request.POST.get('contact_name1')
                        phone_update = request.POST.get('contact_phone1')
                        fax_update = request.POST.get('contact_fax1')
                        
                        obj_id.contact_name = name_update
                        obj_id.contact_email = email_update
                        obj_id.contact_phone = phone_update
                        obj_id.contact_fax = fax_update
                        obj_id.save()
                        check_distributor = Distributor.objects.filter(id=distributor)
                        if check_distributor:
                            get_distributor = check_distributor.first()
                            get_distributor.warehouse.add(warehouse)
                        log_email = ''
                        if email_update != warehouse_email:
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
                        log_type, log_status, log_device = "WarehouseUser", "Edited", "Web"
                        log_idd, log_name = obj_id.id, name_update
                        log_details = f"warehouse_id = {warehouse.id} | warehouse = {warehouse.name}  | contact_name= {name_update} | contact_email = {email_update} | contact_phone = {phone_update} | contact_fax = {fax_update}"
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
                        return redirect('list-warehouse')
                return render(request, 'distributor/update_warehouse.html',context)
            # warehouse manager..........
            elif request.user.is_warehouse_manager:
                obj_id = WarehouseUser.objects.get(id=pk)
                print(obj_id)
                context['p_user'] = obj_id
                warehouse = Warehouse.objects.get(id=obj_id.warehouse.id)

                context['form'] = WarehouseForm(instance=warehouse)
                warehouse_email = obj_id.contact_email
                user = User.objects.get(email=warehouse_email)
                if request.method == 'POST':                   
                    form = WarehouseForm( request.POST,instance=warehouse)                    
                    if form.is_valid(): 
                        distributor = request.POST.get('distributor')    
                                           
                        email_update = request.POST.get('contact_email1')
                        name_update = request.POST.get('contact_name1')
                        phone_update = request.POST.get('contact_phone1')
                        fax_update = request.POST.get('contact_fax1')
                        
                        obj_id.contact_name = name_update
                        obj_id.contact_email = email_update
                        obj_id.contact_phone = phone_update
                        obj_id.contact_fax = fax_update
                        obj_id.save()
                        check_distributor = Distributor.objects.filter(id=distributor)
                        if check_distributor:
                            get_distributor = check_distributor.first()
                            get_distributor.warehouse.add(warehouse)
                        log_email = ''
                        if email_update != warehouse_email:
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
                        log_type, log_status, log_device = "WarehouseUser", "Edited", "Web"
                        log_idd, log_name = obj_id.id, name_update
                        log_details = f"warehouse_id = {warehouse.id} | warehouse = {warehouse.name}  | contact_name= {name_update} | contact_email = {email_update} | contact_phone = {phone_update} | contact_fax = {fax_update}"
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
                        return redirect('list-warehouse')
                return render(request, 'distributor/update_warehouse.html',context)
            else:
                messages.error(request, "Not a valid request")
                return redirect("dashboard")
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/update_warehouse.html',context)


@login_required()
def warehouse_change_password(request,pk):
    context={}
    try:
        # Superuser..............
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            warehouse = WarehouseUser.objects.get(id=pk)
            user = User.objects.get(email=warehouse.contact_email)
            context["userr"] = user
            if request.method == "POST":
                password1 = request.POST.get("password1")
                password2 = request.POST.get("password2")
                if len(password1) != 0 and len(password2) != 0 and password1 != None and password2 != None and password1 == password2:
                    # update_pass_user = User.objects.get(id=pk)
                    password = make_password(password1)
                    user.password = password
                    user.password_raw = password1
                    user.save()
                    warehouse.p_password_raw = password1
                    warehouse.save()
                    # 10-04-23 Log Table
                    log_type, log_status, log_device = "WarehouseUser", "Password changed", "Web"
                    log_idd, log_name = warehouse.id, warehouse.contact_name
                    log_email = warehouse.contact_email
                    log_details = f"warehouse_id = {warehouse.warehouse.id} | warehouse = {warehouse.warehouse.name} | contact_name= {warehouse.contact_name} | contact_email = {warehouse.contact_email} | contact_phone = {warehouse.contact_phone} | contact_fax = {warehouse.contact_fax}"
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
            return render (request, 'distributor/warehouse_change_password.html', context)
        # Distributor...............
        elif request.user.is_warehouse_manager:
            warehouse = WarehouseUser.objects.get(id=pk)
            user = User.objects.get(email=warehouse.contact_email)
            context["userr"] = user
            if request.method == "POST":
                password1 = request.POST.get("password1")
                password2 = request.POST.get("password2")
                if len(password1) != 0 and len(password2) != 0 and password1 != None and password2 != None and password1 == password2:
                    # update_pass_user = User.objects.get(id=pk)
                    password = make_password(password1)
                    user.password = password
                    user.password_raw = password1
                    user.save()
                    warehouse.p_password_raw = password1
                    warehouse.save()
                    # 10-04-23 Log Table
                    log_type, log_status, log_device = "WarehouseUser", "Password changed", "Web"
                    log_idd, log_name = warehouse.id, warehouse.contact_name
                    log_email = warehouse.contact_email
                    log_details = f"warehouse_id = {warehouse.warehouse.id} | warehouse = {warehouse.warehouse.name} | contact_name= {warehouse.contact_name} | contact_email = {warehouse.contact_email} | contact_phone = {warehouse.contact_phone} | contact_fax = {warehouse.contact_fax}"
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
        
        else:
            return redirect('dashboard')
        return render (request, 'distributor/warehouse_change_password.html', context)
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'distributor/warehouse_change_password.html', context)


@login_required()
def add_customer(request):
    context = {}
    try:
        if request.user.is_authenticated:
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role() or request.user.is_distributor:
                form = CustomerForm()
                context["form"] = form
                if request.method == 'POST':
                    form = CustomerForm(request.POST)
                    
                    name = request.POST.get('name')
                    location = request.POST.get('location')
                    latitude = request.POST.get('latitude')
                    longitude = request.POST.get('longitude')                   

                    # Check if a customer with the same name already exists
                    if Customer.objects.filter(name=name).exists():
                        messages.error(request, "A customer with this name already exists.")
                        return render(request, 'distributor/add_customer.html', context)

                    # Create the customer
                    customer = Customer.objects.create(
                        name=name,
                        location=location,
                        latitude=latitude,
                        longitude=longitude
                        
                    )

                    # Log the action
                    log_type, log_status, log_device = "Customer", "Added", "Web"
                    log_idd, log_name = customer.id, name
                    log_email = None
                    log_details = (f"name = {name} | location = {location} | "
                                    f"latitude = {latitude} | longitude = {longitude}")
                    action_by_userid = request.user.id
                    userr = User.objects.get(pk=action_by_userid)
                    user_role = userr.role.all()
                    action_by_username = f'{userr.first_name} {userr.last_name}'
                    action_by_email = userr.username
                    action_by_role = "superuser" if request.user.id == 1 else str(','.join([str(i.role) for i in user_role]))
                    logtable = LogTable(
                        log_type=log_type, log_status=log_status, log_idd=log_idd, log_name=log_name,
                        action_by_userid=action_by_userid, action_by_username=action_by_username,
                        action_by_email=action_by_email, action_by_role=action_by_role, log_email=log_email,
                        log_details=log_details, log_device=log_device
                    )
                    logtable.save()

                    # Add the single customer user
                    user_name = request.POST.get('user_name')
                    user_email = request.POST.get('user_email')
                    user_phone = request.POST.get('user_phone')
                    user_fax = request.POST.get('user_fax')
                    print(user_name, user_email, user_phone, user_fax)

                    if CustomerUser.objects.filter(customer=customer).exists():                       
                        messages.error(request, "A user is already associated with this customer.")
                        return render(request, 'distributor/add_customer.html', context)

                    if User.objects.filter(email=user_email).exists():                        
                        messages.error(request, f'Email {user_email} already exists.')
                    else:
                        password = generate_random_password()                        
                        customer_user = CustomerUser.objects.create(
                            customer=customer,
                            contact_name=user_name,
                            contact_email=user_email,
                            contact_phone=user_phone,
                            contact_fax=user_fax,
                            p_password_raw=password
                        )                    
                        user = User.objects.create(email=user_email, username=user_email,first_name=user_name)
                        user.role.add(Role.objects.get(role='Customer'))
                        user.is_customer=True
                        user.is_active=True
                        user.set_password(password)
                        user.password_raw = password
                        user.save()

                        # Log the action for user creation
                        log_type, log_status, log_device = "CustomerUser", "Added", "Web"
                        log_idd, log_name = customer_user.id, user_name
                        log_email = user_email
                        log_details = (f"customer_id = {customer.id} | customer = {customer.name} | "
                                        f"user_name= {user_name} | user_email = {user_email} | "
                                        f"user_phone = {user_phone} | user_fax = {user_fax} | password_raw = {password}")
                        logtable = LogTable(
                            log_type=log_type, log_status=log_status, log_idd=log_idd, log_name=log_name,
                            action_by_userid=action_by_userid, action_by_username=action_by_username,
                            action_by_email=action_by_email, action_by_role=action_by_role, log_email=log_email,
                            log_details=log_details, log_device=log_device
                        )
                        logtable.save()

                    return redirect('list-customer')                

                return render(request, 'distributor/add_customer.html', context)
            else:
                messages.error(request, "Not a valid request.")
                return redirect("dashboard")
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/add_customer.html', context)


@login_required()
def list_customer(request):
    context = {}
    try:
        if request.user.is_authenticated:
            customer = []
            search_name = request.GET.get('search_name', '')
            if 'Grower' in request.user.get_role() and not request.user.is_superuser:
                pass
            elif request.user.is_consultant:
                pass
            elif request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                customer = CustomerUser.objects.all()
                if search_name:
                    customer = customer.filter(Q(contact_name__icontains=search_name) | Q(customer__name__icontains=search_name)| Q(contact_email__icontains=search_name))
                    context['search_name'] = search_name
            elif request.user.is_customer:
                customer_user= CustomerUser.objects.filter(contact_email=request.user.email).first()
                entity_name = customer_user.customer
                customer = CustomerUser.objects.filter(customer=entity_name)
                if search_name:
                    customer = customer.filter(Q(contact_name__icontains=search_name) | Q(customer__name__icontains=search_name)| Q(contact_email__icontains=search_name))
                    context['search_name'] = search_name
            else:
                messages.error(request, "Not a valid request")
                return redirect("dashboard")

            # Pagination
            customer = customer.order_by("-id")
            paginator = Paginator(customer, 20) 
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context['page_obj'] = page_obj            

            return render(request, 'distributor/list_customer.html', context)
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/list_customer.html', context)



@login_required()
def customer_update(request,pk):
    context = {}
    try:
        if request.user.is_authenticated:        
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                obj_id = CustomerUser.objects.get(id=pk)
                print(obj_id)
                context['p_user'] = obj_id
                customer = Customer.objects.get(id=obj_id.customer.id)

                context['form'] = CustomerForm(instance=customer)
                customer_email = obj_id.contact_email
                user = User.objects.get(email=customer_email)
                if request.method == 'POST':                   
                    form = CustomerForm( request.POST,instance=customer)                    
                    if form.is_valid():  
                        print('000000000000')                     
                        email_update = request.POST.get('contact_email1')
                        name_update = request.POST.get('contact_name1')
                        phone_update = request.POST.get('contact_phone1')
                        fax_update = request.POST.get('contact_fax1')
                        
                        obj_id.contact_name = name_update
                        obj_id.contact_email = email_update
                        obj_id.contact_phone = phone_update
                        obj_id.contact_fax = fax_update
                        obj_id.save()
                        print(obj_id)
                        log_email = ''
                        if email_update != customer_email:
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
                        log_type, log_status, log_device = "CustomerUser", "Edited", "Web"
                        log_idd, log_name = obj_id.id, name_update
                        log_details = f"customer_id = {customer.id} | customer = {customer.name}  | contact_name= {name_update} | contact_email = {email_update} | contact_phone = {phone_update} | contact_fax = {fax_update}"
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
                        return redirect('list-customer')
                return render(request, 'distributor/update_customer.html',context)
            # customer..........
            elif request.user.is_customer:
                obj_id = CustomerUser.objects.get(id=pk)
                context['p_user'] = obj_id
                customer = Customer.objects.get(id=obj_id.customer.id)

                context['form'] = CustomerForm(instance=customer)
                customer_email = obj_id.contact_email
                user = User.objects.get(email=customer_email)
                if request.method == 'POST':
                    form = CustomerForm( request.POST,instance=customer)
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
                        if email_update != customer_email:
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
                        log_type, log_status, log_device = "CustomerUser", "Edited", "Web"
                        log_idd, log_name = obj_id.id, name_update
                        log_details = f"customer_id = {customer.id} | customer = {customer.name}  | contact_name= {name_update} | contact_email = {email_update} | contact_phone = {phone_update} | contact_fax = {fax_update}"
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
                        return redirect('list-customer')
                return render(request, 'distributor/update_customer.html',context)
            else:
                messages.error(request, "Not a valid request")
                return redirect("dashboard")
        else:
            return redirect('login')
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/update_customer.html',context)


@login_required()
def customer_change_password(request,pk):
    context={}
    try:
        # Superuser..............
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            customer = CustomerUser.objects.get(id=pk)
            user = User.objects.get(email=customer.contact_email)
            context["userr"] = user
            if request.method == "POST":
                password1 = request.POST.get("password1")
                password2 = request.POST.get("password2")
                if len(password1) != 0 and len(password2) != 0 and password1 != None and password2 != None and password1 == password2:
                    # update_pass_user = User.objects.get(id=pk)
                    password = make_password(password1)
                    user.password = password
                    user.password_raw = password1
                    user.save()
                    customer.p_password_raw = password1
                    customer.save()
                    # 10-04-23 Log Table
                    log_type, log_status, log_device = "CustomerUser", "Password changed", "Web"
                    log_idd, log_name = customer.id, customer.contact_name
                    log_email = customer.contact_email
                    log_details = f"customer_id = {customer.customer.id} | customer = {customer.customer.name} | contact_name= {customer.contact_name} | contact_email = {customer.contact_email} | contact_phone = {customer.contact_phone} | contact_fax = {customer.contact_fax}"
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
            return render (request, 'distributor/customer_change_password.html', context)
        # Distributor...............
        elif request.user.is_customer:
            customer = CustomerUser.objects.get(id=pk)
            user = User.objects.get(email=customer.contact_email)
            context["userr"] = user
            if request.method == "POST":
                password1 = request.POST.get("password1")
                password2 = request.POST.get("password2")
                if len(password1) != 0 and len(password2) != 0 and password1 != None and password2 != None and password1 == password2:
                    # update_pass_user = User.objects.get(id=pk)
                    password = make_password(password1)
                    user.password = password
                    user.password_raw = password1
                    user.save()
                    customer.p_password_raw = password1
                    customer.save()
                    # 10-04-23 Log Table
                    log_type, log_status, log_device = "CustomerUser", "Password changed", "Web"
                    log_idd, log_name = customer.id, customer.contact_name
                    log_email = customer.contact_email
                    log_details = f"customer_id = {customer.customer.id} | customer = {customer.customer.name} | contact_name= {customer.contact_name} | contact_email = {customer.contact_email} | contact_phone = {customer.contact_phone} | contact_fax = {customer.contact_fax}"
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
        
        else:
            return redirect('dashboard')
        return render (request, 'distributor/customer_change_password.html', context)
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'distributor/customer_change_password.html', context)


@login_required()
def create_processor_shipment(request):
    context = {}
    try:
        if request.user.is_authenticated:
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                contracts = AdminProcessorContract.objects.all().values('id','secret_key','processor_id','processor_type','processor_entity_name','crop').order_by('-id')
                
                context["contracts"] = contracts
                context.update({
                    "selected_contract": None,
                    "milled_value": "None",
                    "selected_processor_sku_id_list":[],
                    "selected_destination": None,
                    "warehouse_name" : None,
                    "customer_name": None               
                })
              
                if request.method == "POST":
                    data = request.POST
                    selected_contract = request.POST.get('selected_contract') 
                    print(selected_contract)
                    contract = AdminProcessorContract.objects.get(id=int(selected_contract))                   
                    processor_id = contract.processor_id
                    processor_type = contract.processor_type
                    selected_sku_id = data.get('sender_sku_id')
                    destination_type = data.get('selected_destination')
                    destination_id = data.get('destination_id')
                    context.update({
                        "selected_contract":contract.id,
                        "contract":contract,                        
                        "selected_processor_id": processor_id,
                        "carrier_type": data.get('carrier_type'),                    
                        "outbound_type": data.get('outbound_type'),
                        "purchase_order_name":data.get('purchase_order_name'),
                        "purchase_order_number": data.get('purchase_order_number'),
                        "lot_number": data.get('lot_number'),
                        "sender_sku_id": selected_sku_id,
                        "selected_destination": destination_type,
                        "weight":data.get('weight'),
                        "gross_weight":data.get('gross_weight'),
                        "net_weight":data.get('net_Weight'),
                        "ship_quantity":data.get('ship_quantity'),
                        "status":data.get('status'),
                        "amount_unit":data.get('amount_unit') ,                     
                        
                    })
                    if destination_id:
                        context["destination_id"] = int(destination_id)
                    if processor_id and not data.get("save"): 
                    
                        if selected_sku_id:
                            context["milled_value"] =  calculate_milled_volume(int(processor_id), processor_type, selected_sku_id)
                            context["selected_sku"] = selected_sku_id
                        else:
                            context["milled_value"] =  calculate_milled_volume(int(processor_id), processor_type, selected_sku_id)
                        context["sender_sku_id_list"] = get_sku_list(int(processor_id),processor_type)["data"]
                        if destination_type == 'warehouse':
                            context['destination_list'] = Warehouse.objects.all().values('id','name')
                        if destination_type == 'customer':
                            context['destination_list'] = Customer.objects.all().values('id','name')
                        return render(request, 'distributor/create_outbound.html', context)
                    else:
                        if destination_type == 'warehouse':
                            warehouse_id = Warehouse.objects.get(id=int(context.get('destination_id'))).id
                            warehouse_name = Warehouse.objects.get(id=int(context.get('destination_id'))).name
                            customer_id = None
                            customer_name = None
                        else:
                            warehouse_id = None
                            warehouse_name = None
                            customer_id = Customer.objects.get(id=int(context.get('destination_id'))).id
                            customer_name = Customer.objects.get(id=int(context.get('destination_id'))).name

                        if data.get('carrier_type') == 'Truck/Trailer':
                            ship_quantity = data.get('ship_quantity')
                            gross_weight = float(data.get('gross_weight'))* int(ship_quantity)
                            if data.get('net_weight') not in [None, 'null', ' ', '']:
                                
                                net_weight = float(data.get('net_weight')) * int(ship_quantity)
                            else:
                                context["error_messages"] = "Please give net weight."
                                return render(request, 'distributor/create_outbound.html', context)
                        elif data.get('carrier_type') == 'Rail Car':
                            
                            gross_weight = 0
                            ship_quantity = 1
                            if data.get('weight') not in [None, 'null', ' ', '']:
                                net_weight = float(data.get('weight'))
                            else:
                                context["error_messages"] = "Please give weight."
                                return render(request, 'distributor/create_outbound.html', context)
                       
                        if contract.amount_unit == context.get('amount_unit'):
                            contract_weight_left = float(contract.contract_amount) - float(net_weight)
                        else:
                            if contract.amount_unit == "LBS" and context.get('amount_unit') == "MT":
                                net_weight_lbs = float(net_weight) * 2204.62
                                contract_weight_left = float(contract.contract_amount) - net_weight_lbs 
                            else:
                                net_weight_mt = float(net_weight) * 0.000453592
                                contract_weight_left = float(contract.contract_amount) - net_weight_mt                         
                        
                        outbound = ProcessorWarehouseShipment(
                            contract=contract,
                            processor_id=processor_id,
                            processor_type=processor_type,
                            processor_entity_name=contract.processor_entity_name,
                            processor_sku_list=[selected_sku_id],
                            carrier_type=context.get('carrier_type'),
                            outbound_type=context.get('outbound_type'),
                            purchase_order_name=context.get('purchase_order_name'),
                            purchase_order_number=context.get('purchase_order_number'),
                            lot_number=context.get('lot_number'),
                            gross_weight=gross_weight,
                            net_weight=net_weight,
                            weight_unit=context.get('amount_unit'),
                            ship_quantity=ship_quantity,
                            contract_weight_left=contract_weight_left,
                            status=context.get('status'),
                            customer_id=customer_id,
                            warehouse_id=warehouse_id,
                            customer_name=customer_name,
                            warehouse_name=warehouse_name
                        )
                        outbound.save()
                            
                        
                        carrier_id = data.get('carrier_id')
                        if carrier_id:
                            CarrierDetails.objects.create(shipment=outbound, carrier_id=carrier_id)
                        
                        files = request.FILES.getlist('files')
                        for file in files:
                            ProcessorWarehouseShipmentDocuments.objects.create(shipment=outbound, document_file=file)

                        ## Send notification to the Destination.
                        if outbound.warehouse_id not in [None, 'null', ' ', '']:                            
                            all_user = WarehouseUser.objects.filter(warehouse_id=outbound.warehouse_id)                           
                           
                            distributors = Distributor.objects.filter(warehouse__id=outbound.warehouse_id)                           
                         
                            distributor_users = DistributorUser.objects.filter(distributor__in=distributors)
                        else:                            
                            all_user = CustomerUser.objects.filter(customer_id=outbound.customer_id)
                            distributor_users = []                          
                        all_users = list(all_user) + list(distributor_users)
                        for user in all_users :
                            msg = f'A shipment has been sent of {outbound.net_weight}{outbound.weight_unit} under Contract ID - {outbound.contract.secret_key}'
                            get_user = User.objects.get(username=user.contact_email)
                            notification_reason = 'New Shipment'
                            redirect_url = "/warehouse/list-processor-shipment/"
                            save_notification = ShowNotification(user_id_to_show=get_user.id,msg=msg,status="UNREAD",redirect_url=redirect_url,
                                notification_reason=notification_reason)
                            save_notification.save()
                        
                    return redirect('list-processor-shipment')   

                return render(request, 'distributor/create_outbound.html', context)    
            elif request.user.is_processor:
                user = request.user
                processor_user = ProcessorUser.objects.filter(contact_email=user.email)
                processor =  Processor.objects.filter(id=processor_user.processor.id).first()
                processor_id =processor.id
                processor_type = 'T1'
                processor_entity_name = processor.entity_name
                contracts = AdminProcessorContract.objects.filter(processor_id=processor_id, processor_type=processor_type).values('id','secret_key','processor_id','processor_type','processor_entity_name','crop').order_by('-id')
                
                context["contracts"] = contracts
                context.update({
                    "selected_contract": None,
                    "milled_value": "None",
                    "selected_processor_sku_id_list":[],
                    "selected_destination": None,
                    "warehouse_name" : None,
                    "customer_name": None               
                })
                print(context)
                if request.method == "POST":
                    data = request.POST
                    selected_contract = request.POST.get('selected_contract') 
                    print(selected_contract)
                    contract = AdminProcessorContract.objects.get(id=int(selected_contract))                   
                    processor_id = contract.processor_id
                    processor_type = contract.processor_type
                    selected_sku_id = data.get('sender_sku_id')
                    destination_type = data.get('selected_destination')
                    destination_id = data.get('destination_id')
                    context.update({
                        "selected_contract":contract.id,
                        "contract":contract,                        
                        "selected_processor_id": processor_id,
                        "carrier_type": data.get('carrier_type'),                    
                        "outbound_type": data.get('outbound_type'),
                        "purchase_order_name":data.get('purchase_order_name'),
                        "purchase_order_number": data.get('purchase_order_number'),
                        "lot_number": data.get('lot_number'),
                        "sender_sku_id": selected_sku_id,
                        "selected_destination": destination_type,
                        "weight":data.get('weight'),
                        "gross_weight":data.get('gross_weight'),
                        "net_weight":data.get('net_Weight'),
                        "ship_quantity":data.get('ship_quantity'),
                        "status":data.get('status'),
                        "amount_unit":data.get('amount_unit') ,                     
                        
                    })
                    if destination_id:
                        context["destination_id"] = int(destination_id)
                    if processor_id and not data.get("save"): 
                    
                        if selected_sku_id:
                            context["milled_value"] =  calculate_milled_volume(int(processor_id), processor_type, selected_sku_id)
                            context["selected_sku"] = selected_sku_id
                        else:
                            context["milled_value"] =  calculate_milled_volume(int(processor_id), processor_type, selected_sku_id)
                        context["sender_sku_id_list"] = get_sku_list(int(processor_id),processor_type)["data"]
                        if destination_type == 'warehouse':
                            context['destination_list'] = Warehouse.objects.all().values('id','name')
                        if destination_type == 'customer':
                            context['destination_list'] = Customer.objects.all().values('id','name')
                        return render(request, 'distributor/create_outbound.html', context)
                    else:
                        if destination_type == 'warehouse':
                            warehouse_id = Warehouse.objects.get(id=int(context.get('destination_id'))).id
                            warehouse_name = Warehouse.objects.get(id=int(context.get('destination_id'))).name
                            customer_id = None
                            customer_name = None
                        else:
                            warehouse_id = None
                            warehouse_name = None
                            customer_id = Customer.objects.get(id=int(context.get('destination_id'))).id
                            customer_name = Customer.objects.get(id=int(context.get('destination_id'))).name

                        if data.get('carrier_type') == 'Truck/Trailer':
                            ship_quantity = data.get('ship_quantity')
                            gross_weight = float(data.get('gross_weight'))* int(ship_quantity)
                            if data.get('net_weight') not in [None, 'null', ' ', '']:
                                
                                net_weight = float(data.get('net_weight')) * int(ship_quantity)
                            else:
                                context["error_messages"] = "Please give net weight."
                                return render(request, 'distributor/create_outbound.html', context)
                        elif data.get('carrier_type') == 'Rail Car':
                            
                            gross_weight = 0
                            ship_quantity = 1
                            if data.get('weight') not in [None, 'null', ' ', '']:
                                net_weight = float(data.get('weight'))
                            else:
                                context["error_messages"] = "Please give weight."
                                return render(request, 'distributor/create_outbound.html', context)
                       
                        if contract.amount_unit == context.get('amount_unit'):
                            contract_weight_left = float(contract.contract_amount) - float(net_weight)
                        else:
                            if contract.amount_unit == "LBS" and context.get('amount_unit') == "MT":
                                net_weight_lbs = float(net_weight) * 2204.62
                                contract_weight_left = float(contract.contract_amount) - net_weight_lbs 
                            else:
                                net_weight_mt = float(net_weight) * 0.000453592
                                contract_weight_left = float(contract.contract_amount) - net_weight_mt                         
                        
                        outbound = ProcessorWarehouseShipment(
                            contract=contract,
                            processor_id=processor_id,
                            processor_type=processor_type,
                            processor_entity_name=contract.processor_entity_name,
                            processor_sku_list=[selected_sku_id],
                            carrier_type=context.get('carrier_type'),
                            outbound_type=context.get('outbound_type'),
                            purchase_order_name=context.get('purchase_order_name'),
                            purchase_order_number=context.get('purchase_order_number'),
                            lot_number=context.get('lot_number'),
                            gross_weight=gross_weight,
                            net_weight=net_weight,
                            weight_unit=context.get('amount_unit'),
                            ship_quantity=ship_quantity,
                            contract_weight_left=contract_weight_left,
                            status=context.get('status'),
                            customer_id=customer_id,
                            warehouse_id=warehouse_id,
                            customer_name=customer_name,
                            warehouse_name=warehouse_name
                        )
                        outbound.save()
                            
                        
                        carrier_id = data.get('carrier_id')
                        if carrier_id:
                            CarrierDetails.objects.create(shipment=outbound, carrier_id=carrier_id)
                        
                        files = request.FILES.getlist('files')
                        for file in files:
                            ProcessorWarehouseShipmentDocuments.objects.create(shipment=outbound, document_file=file)

                        ## Send notification to the Destination.
                        if outbound.warehouse_id not in [None, 'null', ' ', '']:                            
                            all_user = WarehouseUser.objects.filter(warehouse_id=outbound.warehouse_id)                           
                           
                            distributors = Distributor.objects.filter(warehouse__id=outbound.warehouse_id)                           
                         
                            distributor_users = DistributorUser.objects.filter(distributor__in=distributors)
                        else:                            
                            all_user = CustomerUser.objects.filter(customer_id=outbound.customer_id)
                            distributor_users = []                          
                        all_users = list(all_user) + list(distributor_users)
                        
                        for user in all_users :
                            msg = f'A shipment has been sent of {outbound.net_weight}{outbound.weight_unit} under Contract ID - {outbound.contract.secret_key}'
                            get_user = User.objects.get(username=user.contact_email)
                            notification_reason = 'New Shipment'
                            redirect_url = "/warehouse/list-processor-shipment/"
                            save_notification = ShowNotification(user_id_to_show=get_user.id,msg=msg,status="UNREAD",redirect_url=redirect_url,
                                notification_reason=notification_reason)
                            save_notification.save()

                    return redirect('list-processor-shipment') 
                return render(request, 'distributor/create_outbound.html', context) 
            elif request.user.is_processor2:
                user = request.user
                processor_user = ProcessorUser2.objects.filter(contact_email=user.email)
                processor =  Processor2.objects.filter(id=processor_user.processor2.id).first()
                processor_id = processor.id
                processor_type = processor.processor_type.first().type_name
                processor_entity_name = processor.entity_name
                contracts = AdminProcessorContract.objects.filter(processor_type=processor_type, processor_id=processor_id).values('id','secret_key','processor_id','processor_type','processor_entity_name','crop').order_by('-id')
                
                context["contracts"] = contracts
                context.update({
                    "selected_contract": None,
                    "milled_value": "None",
                    "selected_processor_sku_id_list":[],
                    "selected_destination": None,
                    "warehouse_name" : None,
                    "customer_name": None               
                })
                print(context)
                if request.method == "POST":
                    data = request.POST
                    selected_contract = request.POST.get('selected_contract') 
                    print(selected_contract)
                    contract = AdminProcessorContract.objects.get(id=int(selected_contract))                   
                    processor_id = contract.processor_id
                    processor_type = contract.processor_type
                    selected_sku_id = data.get('sender_sku_id')
                    destination_type = data.get('selected_destination')
                    destination_id = data.get('destination_id')
                    context.update({
                        "selected_contract":contract.id,
                        "contract":contract,                        
                        "selected_processor_id": processor_id,
                        "carrier_type": data.get('carrier_type'),                    
                        "outbound_type": data.get('outbound_type'),
                        "purchase_order_name":data.get('purchase_order_name'),
                        "purchase_order_number": data.get('purchase_order_number'),
                        "lot_number": data.get('lot_number'),
                        "sender_sku_id": selected_sku_id,
                        "selected_destination": destination_type,
                        "weight":data.get('weight'),
                        "gross_weight":data.get('gross_weight'),
                        "net_weight":data.get('net_Weight'),
                        "ship_quantity":data.get('ship_quantity'),
                        "status":data.get('status'),
                        "amount_unit":data.get('amount_unit') ,                     
                        
                    })
                    if destination_id:
                        context["destination_id"] = int(destination_id)
                    if processor_id and not data.get("save"): 
                    
                        if selected_sku_id:
                            context["milled_value"] =  calculate_milled_volume(int(processor_id), processor_type, selected_sku_id)
                            context["selected_sku"] = selected_sku_id
                        else:
                            context["milled_value"] =  calculate_milled_volume(int(processor_id), processor_type, selected_sku_id)
                        context["sender_sku_id_list"] = get_sku_list(int(processor_id),processor_type)["data"]
                        if destination_type == 'warehouse':
                            context['destination_list'] = Warehouse.objects.all().values('id','name')
                        if destination_type == 'customer':
                            context['destination_list'] = Customer.objects.all().values('id','name')
                        return render(request, 'distributor/create_outbound.html', context)
                    else:
                        if destination_type == 'warehouse':
                            warehouse_id = Warehouse.objects.get(id=int(context.get('destination_id'))).id
                            warehouse_name = Warehouse.objects.get(id=int(context.get('destination_id'))).name
                            customer_id = None
                            customer_name = None
                        else:
                            warehouse_id = None
                            warehouse_name = None
                            customer_id = Customer.objects.get(id=int(context.get('destination_id'))).id
                            customer_name = Customer.objects.get(id=int(context.get('destination_id'))).name

                        if data.get('carrier_type') == 'Truck/Trailer':
                            ship_quantity = data.get('ship_quantity')
                            gross_weight = float(data.get('gross_weight'))* int(ship_quantity)
                            if data.get('net_weight') not in [None, 'null', ' ', '']:
                                
                                net_weight = float(data.get('net_weight')) * int(ship_quantity)
                            else:
                                context["error_messages"] = "Please give net weight."
                                return render(request, 'distributor/create_outbound.html', context)
                        elif data.get('carrier_type') == 'Rail Car':
                            
                            gross_weight = 0
                            ship_quantity = 1
                            if data.get('weight') not in [None, 'null', ' ', '']:
                                net_weight = float(data.get('weight'))
                            else:
                                context["error_messages"] = "Please give weight."
                                return render(request, 'distributor/create_outbound.html', context)
                       
                        if contract.amount_unit == context.get('amount_unit'):
                            contract_weight_left = float(contract.contract_amount) - float(net_weight)
                        else:
                            if contract.amount_unit == "LBS" and context.get('amount_unit') == "MT":
                                net_weight_lbs = float(net_weight) * 2204.62
                                contract_weight_left = float(contract.contract_amount) - net_weight_lbs 
                            else:
                                net_weight_mt = float(net_weight) * 0.000453592
                                contract_weight_left = float(contract.contract_amount) - net_weight_mt                         
                        
                        outbound = ProcessorWarehouseShipment(
                            contract=contract,
                            processor_id=processor_id,
                            processor_type=processor_type,
                            processor_entity_name=contract.processor_entity_name,
                            processor_sku_list=[selected_sku_id],
                            carrier_type=context.get('carrier_type'),
                            outbound_type=context.get('outbound_type'),
                            purchase_order_name=context.get('purchase_order_name'),
                            purchase_order_number=context.get('purchase_order_number'),
                            lot_number=context.get('lot_number'),
                            gross_weight=gross_weight,
                            net_weight=net_weight,
                            weight_unit=context.get('amount_unit'),
                            ship_quantity=ship_quantity,
                            contract_weight_left=contract_weight_left,
                            status=context.get('status'),
                            customer_id=customer_id,
                            warehouse_id=warehouse_id,
                            customer_name=customer_name,
                            warehouse_name=warehouse_name
                        )
                        outbound.save()
                            
                        
                        carrier_id = data.get('carrier_id')
                        if carrier_id:
                            CarrierDetails.objects.create(shipment=outbound, carrier_id=carrier_id)
                        
                        files = request.FILES.getlist('files')
                        for file in files:
                            ProcessorWarehouseShipmentDocuments.objects.create(shipment=outbound, document_file=file)

                        ## Send notification to the Destination.
                        if outbound.warehouse_id not in [None, 'null', ' ', '']:                            
                            all_user = WarehouseUser.objects.filter(warehouse_id=outbound.warehouse_id)                           
                           
                            distributors = Distributor.objects.filter(warehouse__id=outbound.warehouse_id)                           
                         
                            distributor_users = DistributorUser.objects.filter(distributor__in=distributors)
                        else:                            
                            all_user = CustomerUser.objects.filter(customer_id=outbound.customer_id)
                            distributor_users = []                          
                        all_users = list(all_user) + list(distributor_users)

                        for user in all_users :
                            msg = f'A shipment has been sent of {outbound.net_weight}{outbound.weight_unit} under Contract ID - {outbound.contract.secret_key}'
                            get_user = User.objects.get(username=user.contact_email)
                            notification_reason = 'New Shipment'
                            redirect_url = "/warehouse/list-processor-shipment/"
                            save_notification = ShowNotification(user_id_to_show=get_user.id,msg=msg,status="UNREAD",redirect_url=redirect_url,
                                notification_reason=notification_reason)
                            save_notification.save()

                    return redirect('list-processor-shipment') 
                return render(request, 'distributor/create_outbound.html', context) 
        else:
            return redirect('login')        
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/create_outbound.html', context) 


@login_required()
def list_processor_shipment(request):
    context = {}
    try:
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            processors = []
            processor1 = Processor.objects.all().values('id', 'entity_name').order_by('entity_name')
            processor2 = Processor2.objects.all().values('id', 'entity_name', 'processor_type__type_name').order_by('entity_name')
            
            for pro1 in processor1:
                processors.append({
                    "id": pro1["id"],
                    "entity_name": pro1["entity_name"],
                    "type": "T1"
                })
                
            for pro2 in processor2:
                processors.append({
                    "id": pro2["id"],
                    "entity_name": pro2["entity_name"],
                    "type": pro2["processor_type__type_name"]  # Reduced query redundancy
                })
            
            context["processor"] = processors
            shipments = ProcessorWarehouseShipment.objects.all()
            selected_processor = request.GET.get('selected_processor','All')
            
            if selected_processor != 'All':
                processor_id, processor_type = selected_processor.split('_')
                context['selected_processor_id'] = int(processor_id)
                context['selected_processor_type'] = processor_type
            else:
                processor_id, processor_type = None, None
                context['selected_processor_id'] = None
                context['selected_processor_type'] = None

            if selected_processor and selected_processor != 'All':                
                shipments = shipments.filter(processor_id=int(processor_id))

            search_name = request.GET.get('search_name', '')

            if search_name and search_name is not None:
                shipments = shipments.filter(Q(warehouse_name__icontains=search_name) |
                                             Q(customer_name__icontains=search_name) |
                                             Q(contract__secret_key__icontains=search_name) |
                                             Q(outbound_type__icontains=search_name) |
                                             Q(carrier_type__icontains=search_name) |
                                             Q(status__icontains=search_name) |
                                             Q(purchase_order_name__icontains=search_name) |
                                             Q(lot_number__icontains=search_name) |
                                             Q(purchase_order_number__icontains=search_name))
                context['search_name'] = search_name
            else:
                context['search_name'] = None            
            
            shipments = shipments.order_by('-id')
            paginator = Paginator(shipments, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)             
            context['contracts'] = report
            return render(request, 'distributor/list_outbound.html', context)
        
        elif request.user.is_processor:
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor.id).id
            processor_type = "T1"

            shipments = ProcessorWarehouseShipment.objects.filter(processor_id=processor_id, processor_type=processor_type)
            shipments = shipments.order_by('-id')
            paginator = Paginator(shipments, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)             
            context['contracts'] = report
            return render(request, 'distributor/list_outbound.html', context)
        
        elif request.user.is_processor2:
            user_email = request.user.email
            p = ProcessorUser2.objects.get(contact_email=user_email)
            processor_id = Processor2.objects.get(id=p.processor2.id).id
            processor_type = Processor2.objects.get(id=p.processor2.id).processor_type.all().first().type_name

            shipments = ProcessorWarehouseShipment.objects.filter(processor_id=processor_id, processor_type=processor_type)
            shipments = shipments.order_by('-id')
            paginator = Paginator(shipments, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)             
            context['contracts'] = report
            return render(request, 'distributor/list_outbound.html', context)
        
        elif request.user.is_distributor:
            print('0000000000')
            user_email = request.user.email
            d = DistributorUser.objects.get(contact_email=user_email)
            distributor = Distributor.objects.get(id=d.distributor.id)
            warehouses = distributor.warehouse.all().values_list('id', flat=True)
            shipments = []
            for warehouse_id in warehouses:
                check_shipment = ProcessorWarehouseShipment.objects.filter(warehouse_id=warehouse_id).order_by('-id')
                if check_shipment:
                    shipments = shipments+list(check_shipment)
            paginator = Paginator(shipments, 100)
            print(paginator)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)             
            context['contracts'] = report
            print(context)
            return render(request, 'distributor/list_outbound.html', context)
        
        elif request.user.is_warehouse_manager:
            user_email = request.user.email
            w = WarehouseUser.objects.get(contact_email=user_email)
            warehouse_id = Warehouse.objects.get(id=w.warehouse.id).id
            shipments = ProcessorWarehouseShipment.objects.filter(warehouse_id=warehouse_id)
            shipments = shipments.order_by('-id')
            paginator = Paginator(shipments, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)             
            context['contracts'] = report
            return render(request, 'distributor/list_outbound.html', context)
        
        elif request.user.is_customer:
            user_email = request.user.email
            c = CustomerUser.objects.get(contact_email=user_email)
            customer_id = Customer.objects.get(id=c.customer.id).id
            shipments = ProcessorWarehouseShipment.objects.filter(customer_id=customer_id)
            shipments = shipments.order_by('-id')
            paginator = Paginator(shipments, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)             
            context['contracts'] = report
            return render(request, 'distributor/list_outbound.html', context)
        else:
            messages.error(request, "Not a valid request.")
            return redirect("dashboard")   
    except (ValueError, AttributeError, AdminProcessorContract.DoesNotExist) as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/list_outbound.html', context)


@login_required()
def processor_shipment_view(request, pk):
    context = {}
    try:
        shipment = ProcessorWarehouseShipment.objects.filter(id=pk).first()        
        carrier_details = CarrierDetails.objects.filter(shipment=shipment)
        context["shipment"] = shipment
        context["documents"] = [
            {
                "id": file.id,
                "file": file.document_file,
                "name": file.document_file.name.split("/")[-1]  # Extract only the file name
            }
            for file in ProcessorWarehouseShipmentDocuments.objects.filter(shipment=shipment)
        ]
        context["carriers"] = carrier_details
        logs = ProcessorShipmentLog.objects.filter(shipment=shipment).order_by('id')
        context['logs'] = logs
        return render (request, 'distributor/view_outbound.html', context)
    except (ValueError, AttributeError, AdminProcessorContract.DoesNotExist) as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/view_outbound.html', context)


@login_required()
def edit_processor_shipment(request, pk):
    context = {}
    # try:
    if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
        check_shipment = ProcessorWarehouseShipment.objects.filter(id=pk)
        
        shipment = check_shipment.first()
        gross_weight_per_unit = float(shipment.gross_weight) / int(shipment.ship_quantity)
        net_weight_per_unit = float(shipment.net_weight) / int(shipment.ship_quantity)
        context['gross_weight'] = gross_weight_per_unit
        context['net_weight'] = net_weight_per_unit
        carrier = CarrierDetails.objects.filter(shipment=shipment).first()
        if carrier:
            context['carrier_id'] = carrier.carrier_id
        context["files"] = [
            {
                "id": file.id,
                "name": file.document_file.name.split("/")[-1]  # Extract only the file name
            }
            for file in ProcessorWarehouseShipmentDocuments.objects.filter(shipment=shipment)
        ]
        context["shipment"] = shipment
        
        selected_contract = shipment.contract               
                                
        processor_id = shipment.contract.processor_id
        processor_type = shipment.contract.processor_type
        destination_type = 'customer' if shipment.customer_id is not None else 'warehouse'
        if destination_type == 'customer':
            destination_list = Customer.objects.all().values('id','name')
        else:
            destination_list = Warehouse.objects.all().values('id','name')
        destination_id = shipment.warehouse_id if shipment.warehouse_id not in [None,'',' ', 'null'] else shipment.customer_id
        print(destination_id)
        context.update({           
            "milled_value": "None",
            "selected_processor_sku_id_list":shipment.processor_sku_list,
            "selected_destination": destination_type,
            "warehouse_name" : shipment.warehouse_name,
            "customer_name": shipment.customer_name ,             
            "contract":selected_contract,                        
            "selected_processor_id": processor_id,
            'destination_list':destination_list,
            "destination_id" : destination_id           
        })
        
        if request.method == "POST":
            data = request.POST
            
            button_value = request.POST.getlist('remove_files')                
            if button_value:
                for file_id in button_value:
                    try:
                        file_obj = ProcessorWarehouseShipmentDocuments.objects.get(id=file_id)
                        file_obj.delete()
                    except ProcessorWarehouseShipmentDocuments.DoesNotExist:
                        pass          
            selected_sku_id = data.get('sender_sku_id')
            destination_type = data.get('selected_destination')
            print(data.get('border_receive_date'))
            context.update({                    
                "carrier_type": data.get('carrier_type'),                    
                "outbound_type": data.get('outbound_type'),
                "purchase_order_name":data.get('purchase_order_name'),
                "purchase_order_number": data.get('purchase_order_number'),
                "lot_number": data.get('lot_number'),
                "selected_processor_sku_id_list": [selected_sku_id],
                "selected_destination": destination_type,
                "weight":data.get('weight'),
                "gross_weight":data.get('gross_weight'),
                "net_weight":data.get('net_Weight'),
                "ship_quantity":data.get('ship_quantity'),
                "status":data.get('status'),
                "amount_unit":data.get('amount_unit') ,   
                "final_receive_date": data.get('final_receive_date'),
                "border_receive_date" : data.get('border_receive_date'),
                "border_leaving_date": data.get('border_leaving_date'),
                "final_leaving_date" : data.get('final_leaving_date'),
                "border_receive_date2": data.get('border_receive_date2'),
                "border_leaving_date2" : data.get('border_leaving_date2'),
                "processor_receive_date": data.get('processor_receive_date')             
                
            })
            print(data.get('border_receive_date'))
            if destination_id:
                context["destination_id"] = int(destination_id)
            if processor_id and not data.get("save"): 
            
                if selected_sku_id:
                    context["milled_value"] =  calculate_milled_volume(int(processor_id), processor_type, selected_sku_id)
                    context["selected_sku"] = selected_sku_id
                else:
                    context["milled_value"] =  calculate_milled_volume(int(processor_id), processor_type, selected_sku_id)
                context["sender_sku_id_list"] = get_sku_list(int(processor_id),processor_type)["data"]
                if destination_type == 'warehouse':
                    context['destination_list'] = Warehouse.objects.all().values('id','name')
                if destination_type == 'customer':
                    context['destination_list'] = Customer.objects.all().values('id','name')
                return render(request, 'distributor/create_outbound.html', context)
            else:
                if destination_type == 'warehouse':
                    warehouse_id = Warehouse.objects.get(id=int(context.get('destination_id'))).id
                    warehouse_name = Warehouse.objects.get(id=int(context.get('destination_id'))).name
                    customer_id = None
                    customer_name = None
                else:
                    warehouse_id = None
                    warehouse_name = None
                    customer_id = Customer.objects.get(id=int(context.get('destination_id'))).id
                    customer_name = Customer.objects.get(id=int(context.get('destination_id'))).name

                if data.get('carrier_type') == 'Truck/Trailer':
                    ship_quantity = data.get('ship_quantity')
                    gross_weight = float(data.get('gross_weight'))* int(ship_quantity)
                    if data.get('net_weight') not in [None, 'null', ' ', '']:
                        print('00000')
                        net_weight = float(data.get('net_weight')) * int(ship_quantity)
                    else:
                        context["error_messages"] = "Please give net weight."
                        return render(request, 'distributor/create_outbound.html', context)
                elif data.get('carrier_type') == 'Rail Car':
                    gross_weight = 0
                    ship_quantity = 1
                    if data.get('weight') not in [None, 'null', ' ', '']:
                        net_weight = float(context.get('weight'))
                    else:
                        context["error_messages"] = "Please give weight."
                        return render(request, 'distributor/create_outbound.html', context)
                
                if shipment.contract.amount_unit == context.get('amount_unit'):
                    contract_weight_left = float(shipment.contract.contract_amount) - float(net_weight)
                else:
                    if shipment.contract.amount_unit == "LBS" and context.get('amount_unit') == "MT":
                        net_weight_lbs = float(net_weight) * 2204.62
                        contract_weight_left = float(shipment.contract.contract_amount) - net_weight_lbs 
                    else:
                        net_weight_mt = float(net_weight) * 0.000453592
                        contract_weight_left = float(shipment.contract.contract_amount) - net_weight_mt 
                
                shipment.contract=shipment.contract
                shipment.processor_id=processor_id
                shipment.processor_type=processor_type
                shipment.processor_entity_name=shipment.contract.processor_entity_name
                shipment.processor_sku_list=[selected_sku_id]
                shipment.carrier_type=context.get('carrier_type')
                shipment.outbound_type=context.get('outbound_type')
                shipment.purchase_order_name=context.get('purchase_order_name')
                shipment.purchase_order_number=context.get('purchase_order_number')
                shipment.lot_number=context.get('lot_number')
                shipment.gross_weight=gross_weight
                shipment.net_weight=net_weight
                shipment.weight_unit=context.get('amount_unit')
                shipment.ship_quantity=ship_quantity
                shipment.contract_weight_left=contract_weight_left
                shipment.status= context.get('status')
                shipment.customer_id=customer_id
                shipment.warehouse_id=warehouse_id
                shipment.customer_name=customer_name
                shipment.warehouse_name=warehouse_name
                                                                        
                shipment.save()
                if data.get('border_receive_date') not in [None, '', ' ', 'null']:
                    border_receive_date = data.get('border_receive_date')
                    shipment.border_receive_date= border_receive_date
                if data.get('border_leaving_date') not in [None, '', ' ', 'null']:
                    border_leaving_date = data.get('border_leaving_date')
                    shipment.border_leaving_date=border_leaving_date
                if data.get('final_receive_date') not in [None, '', ' ', 'null']:
                    final_receive_date = data.get('final_receive_date')
                    shipment.distributor_receive_date=final_receive_date
                if data.get('final_leaving_date') not in [None, '', ' ', 'null']:
                    final_leaving_date = data.get('final_leaving_date')
                    shipment.distributor_leaving_date=final_leaving_date
                if data.get('border_receive_date2') not in [None, '', ' ', 'null']:
                    border_receive_date2 = data.get('border_receive_date2')
                    shipment.border_back_receive_date=border_receive_date2
                if data.get('border_leaving_date2') not in [None, '', ' ', 'null']:
                    border_leaving_date2 = data.get('border_leaving_date2')                    
                    shipment.border_back_leaving_date= border_leaving_date2, 
                if data.get('processor_receive_date') not in [None, '', ' ', 'null']:
                    processor_receive_date = data.get('processor_receive_date')
                    shipment.processor_receive_date=processor_receive_date
                
                shipment.save()
                carrier_id = data.get('carrier_id')
                if carrier_id:
                    # Get or create carrier details
                    carrier_details, created = CarrierDetails.objects.update_or_create(
                        shipment=shipment,
                        defaults={'carrier_id': carrier_id}
                    )
                else:
                    # Ensure that carrier details are not deleted if no carrier_id is provided
                    CarrierDetails.objects.filter(shipment=shipment).delete()
                
                files = request.FILES.getlist('files')
                for file in files:
                    ProcessorWarehouseShipmentDocuments.objects.create(shipment=shipment, document_file=file)

                
                descriptions = request.POST.getlist('description')

                # Validate and process each field
                for  description in  descriptions:
                    if  description:
                        
                        ProcessorShipmentLog.objects.create(
                            shipment=shipment,                           
                            description=description
                        )
                    else:
                        context["error_messages"] = f'PLease give description'
                        return render(request, 'distributor/edit_outbound.html', context)
            return redirect('list-processor-shipment')
            
        return render(request, 'distributor/edit_outbound.html', context)
                        
    # except (ValueError, AttributeError, AdminProcessorContract.DoesNotExist) as e:
    #     context["error_messages"] = str(e)
        return render(request, 'distributor/edit_outbound.html', context)


def create_warehouse_shipment(request):
    context = {}
    try:
        if request.user.is_authenticated:
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                contracts = AdminCustomerContract.objects.all().values('id','secret_key','customer_id','customer_name','crop').order_by('-id')                
                context["contracts"] = contracts
                context.update({
                    "selected_contract": None,                    
                    "customer_id": None,
                    "customer_name": None             
                })
              
                if request.method == "POST":
                    data = request.POST
                    selected_contract = request.POST.get('selected_contract') 
                    print(selected_contract)
                    contract = AdminProcessorContract.objects.get(id=int(selected_contract))                   
                    processor_id = contract.processor_id
                    processor_type = contract.processor_type
                    selected_sku_id = data.get('sender_sku_id')
                    destination_type = data.get('selected_destination')
                    destination_id = data.get('destination_id')
                    context.update({
                        "selected_contract":contract.id,
                        "contract":contract,                        
                        "selected_processor_id": processor_id,
                        "carrier_type": data.get('carrier_type'),                    
                        "outbound_type": data.get('outbound_type'),
                        "purchase_order_name":data.get('purchase_order_name'),
                        "purchase_order_number": data.get('purchase_order_number'),
                        "lot_number": data.get('lot_number'),
                        "sender_sku_id": selected_sku_id,
                        "selected_destination": destination_type,
                        "weight":data.get('weight'),
                        "gross_weight":data.get('gross_weight'),
                        "net_weight":data.get('net_Weight'),
                        "ship_quantity":data.get('ship_quantity'),
                        "status":data.get('status'),
                        "amount_unit":data.get('amount_unit') ,                     
                        
                    })
                    if destination_id:
                        context["destination_id"] = int(destination_id)
                    if processor_id and not data.get("save"): 
                    
                        if selected_sku_id:
                            context["milled_value"] =  calculate_milled_volume(int(processor_id), processor_type, selected_sku_id)
                            context["selected_sku"] = selected_sku_id
                        else:
                            context["milled_value"] =  calculate_milled_volume(int(processor_id), processor_type, selected_sku_id)
                        context["sender_sku_id_list"] = get_sku_list(int(processor_id),processor_type)["data"]
                        if destination_type == 'warehouse':
                            context['destination_list'] = Warehouse.objects.all().values('id','name')
                        if destination_type == 'customer':
                            context['destination_list'] = Customer.objects.all().values('id','name')
                        return render(request, 'distributor/create_outbound.html', context)
                    else:
                        if destination_type == 'warehouse':
                            warehouse_id = Warehouse.objects.get(id=int(context.get('destination_id'))).id
                            warehouse_name = Warehouse.objects.get(id=int(context.get('destination_id'))).name
                            customer_id = None
                            customer_name = None
                        else:
                            warehouse_id = None
                            warehouse_name = None
                            customer_id = Customer.objects.get(id=int(context.get('destination_id'))).id
                            customer_name = Customer.objects.get(id=int(context.get('destination_id'))).name

                        if data.get('carrier_type') == 'Truck/Trailer':
                            ship_quantity = data.get('ship_quantity')
                            gross_weight = float(data.get('gross_weight'))* int(ship_quantity)
                            if data.get('net_weight') not in [None, 'null', ' ', '']:
                                
                                net_weight = float(data.get('net_weight')) * int(ship_quantity)
                            else:
                                context["error_messages"] = "Please give net weight."
                                return render(request, 'distributor/create_outbound.html', context)
                        elif data.get('carrier_type') == 'Rail Car':
                            
                            gross_weight = 0
                            ship_quantity = 1
                            if data.get('weight') not in [None, 'null', ' ', '']:
                                net_weight = float(data.get('weight'))
                            else:
                                context["error_messages"] = "Please give weight."
                                return render(request, 'distributor/create_outbound.html', context)
                       
                        if contract.amount_unit == context.get('amount_unit'):
                            contract_weight_left = float(contract.contract_amount) - float(net_weight)
                        else:
                            if contract.amount_unit == "LBS" and context.get('amount_unit') == "MT":
                                net_weight_lbs = float(net_weight) * 2204.62
                                contract_weight_left = float(contract.contract_amount) - net_weight_lbs 
                            else:
                                net_weight_mt = float(net_weight) * 0.000453592
                                contract_weight_left = float(contract.contract_amount) - net_weight_mt                         
                        
                        outbound = ProcessorWarehouseShipment(
                            contract=contract,
                            processor_id=processor_id,
                            processor_type=processor_type,
                            processor_entity_name=contract.processor_entity_name,
                            processor_sku_list=[selected_sku_id],
                            carrier_type=context.get('carrier_type'),
                            outbound_type=context.get('outbound_type'),
                            purchase_order_name=context.get('purchase_order_name'),
                            purchase_order_number=context.get('purchase_order_number'),
                            lot_number=context.get('lot_number'),
                            gross_weight=gross_weight,
                            net_weight=net_weight,
                            weight_unit=context.get('amount_unit'),
                            ship_quantity=ship_quantity,
                            contract_weight_left=contract_weight_left,
                            status=context.get('status'),
                            customer_id=customer_id,
                            warehouse_id=warehouse_id,
                            customer_name=customer_name,
                            warehouse_name=warehouse_name
                        )
                        outbound.save()
                            
                        
                        carrier_id = data.get('carrier_id')
                        if carrier_id:
                            CarrierDetails.objects.create(shipment=outbound, carrier_id=carrier_id)
                        
                        files = request.FILES.getlist('files')
                        for file in files:
                            ProcessorWarehouseShipmentDocuments.objects.create(shipment=outbound, document_file=file)

                        ## Send notification to the Destination.
                        if outbound.warehouse_id not in [None, 'null', ' ', '']:                            
                            all_user = WarehouseUser.objects.filter(warehouse_id=outbound.warehouse_id)                           
                           
                            distributors = Distributor.objects.filter(warehouse__id=outbound.warehouse_id)                           
                         
                            distributor_users = DistributorUser.objects.filter(distributor__in=distributors)
                        else:                            
                            all_user = CustomerUser.objects.filter(customer_id=outbound.customer_id)
                            distributor_users = []                          
                        all_users = list(all_user) + list(distributor_users)
                        for user in all_users :
                            msg = f'A shipment has been sent of {outbound.net_weight}{outbound.weight_unit} under Contract ID - {outbound.contract.secret_key}'
                            get_user = User.objects.get(username=user.contact_email)
                            notification_reason = 'New Shipment'
                            redirect_url = "/warehouse/list-processor-shipment/"
                            save_notification = ShowNotification(user_id_to_show=get_user.id,msg=msg,status="UNREAD",redirect_url=redirect_url,
                                notification_reason=notification_reason)
                            save_notification.save()
                        
                    return redirect('list-processor-shipment')  
                return render(request, 'distributor/create_outbound.html', context) 
        else:
            return redirect('login')        
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/create_outbound.html', context)  