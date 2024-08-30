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
                    warehouse_ids  = request.POST.getlist('warehouse ')
                    location = request.POST.get('location')
                    latitude  = request.POST.get('latitude ')
                    longitude = request.POST.get('longitude')                    
                
                    distributor = Distributor.objects.create(entity_name=entity_name,location=location,latitude =latitude ,longitude=longitude)
                    for warehouse_id in warehouse_ids:
                        warehouse = Warehouse.objects.filter(id=warehouse_id)
                        if warehouse:
                            distributor.warehouse.add(warehouse)
                                        
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
                warehouse = WarehouseUser.objects.all()
                if search_name:
                    warehouse = warehouse.filter(Q(contact_name__icontains=search_name) | Q(warehouse__name__icontains=search_name)| Q(contact_email__icontains=search_name))
                    context['search_name'] = search_name
            elif request.user.is_warehouse_user:
                warehouse_user= WarehouseUser.objects.filter(contact_email=request.user.email).first()
                entity_name = warehouse_user.warehouse
                warehouse = WarehouseUser.objects.filter(warehouse=entity_name)
                if search_name:
                    warehouse = warehouse.filter(Q(contact_name__icontains=search_name) | Q(warehouse__name__icontains=search_name)| Q(contact_email__icontains=search_name))
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


def create_processor_shipment(request):
    context = {}
    try:
        if request.user.is_authenticated:
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                contracts = AdminProcessorContract.objects.all().values('id','secret_key','processor_id','processor_type','processor_entity_name','crop')
                
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

                        print(context.get('carrier_type'),data.get('gross_weight'),  data.get('net_weight'),data.get('ship_quantity') )
                        if data.get('carrier_type') == 'Truck/Trailer':
                            gross_weight = float(data.get('gross_weight'))* int(data.get('ship_quantity'))
                            if data.get('net_weight') not in [None, 'null', ' ', '']:
                                print('00000')
                                net_weight = float(data.get('net_weight')) * int(data.get('ship_quantity'))
                            else:
                                context["error_messages"] = "Please give net weight."
                                return render(request, 'distributor/create_outbound.html', context)
                        elif data.get('carrier_type') == 'Rail Car':
                            gross_weight = 0
                            if data.get('weight') not in [None, 'null', ' ', '']:
                                net_weight = float(context.get('weight'))
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
                        outbound = ProcessorWarehouseShipment.objects.create(contract=contract, processor_id=processor_id, processor_type=processor_type, processor_entity_name=contract.processor_entity_name,
                                                                                processor_sku_list=[selected_sku_id],carrier_type=context.get('carrier_type'),outbound_type=context.get('outbound_type'),
                                                                                purchase_order_name=context.get('purchase_order_name'), purchase_order_number=context.get('purchase_order_number'), lot_number=context.get('lot_number'),
                                                                                gross_weight=gross_weight,net_weight=net_weight,weight_unit=context.get('amount_unit'), contract_weight_left=contract_weight_left,
                                                                                status= data.get('status'), customer_id=customer_id, warehouse_id=warehouse_id, customer_name=customer_name, warehouse_name=warehouse_name)
                        carrier_id = data.get('carrier_id')
                        if carrier_id:
                            CarrierDetails.objects.create(shipment=outbound, carrier_id=int(id))
                        
                        files = request.FILES.getlist('files')
                        for file in files:
                            ProcessorWarehouseShipmentDocuments.objects.create(shipment=outbound, document_file=file)

                        
                    return redirect('list-processor-shipment')   

                return render(request, 'distributor/create_outbound.html', context)    
            elif request.user.is_processor:
                user = request.user
                processor_user = ProcessorUser.objects.filter(contact_email=user.email)
                processor =  Processor.objects.filter(id=processor_user.processor.id).first()
                processor_id =processor.id
                processor_type = 'T1'
                processor_entity_name = processor.entity_name
                contracts = AdminProcessorContract.objects.filter(processor_id=processor_id, processor_type=processor_type).values('id','secret_key','processor_id','processor_type','processor_entity_name','crop')
                
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

                        print(context.get('carrier_type'),data.get('gross_weight'),  data.get('net_weight'),data.get('ship_quantity') )
                        if data.get('carrier_type') == 'Truck/Trailer':
                            gross_weight = float(data.get('gross_weight'))* int(data.get('ship_quantity'))
                            if data.get('net_weight') not in [None, 'null', ' ', '']:
                                print('00000')
                                net_weight = float(data.get('net_weight')) * int(data.get('ship_quantity'))
                            else:
                                context["error_messages"] = "Please give net weight."
                                return render(request, 'distributor/create_outbound.html', context)
                        elif data.get('carrier_type') == 'Rail Car':
                            gross_weight = 0
                            if data.get('weight') not in [None, 'null', ' ', '']:
                                net_weight = float(context.get('weight'))
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
                        outbound = ProcessorWarehouseShipment.objects.create(contract=contract, processor_id=processor_id, processor_type=processor_type, processor_entity_name=contract.processor_entity_name,
                                                                                processor_sku_list=[selected_sku_id],carrier_type=context.get('carrier_type'),outbound_type=context.get('outbound_type'),
                                                                                purchase_order_name=context.get('purchase_order_name'), purchase_order_number=context.get('purchase_order_number'), lot_number=context.get('lot_number'),
                                                                                gross_weight=gross_weight,net_weight=net_weight,weight_unit=context.get('amount_unit'), contract_weight_left=contract_weight_left,
                                                                                status= data.get('status'), customer_id=customer_id, warehouse_id=warehouse_id, customer_name=customer_name, warehouse_name=warehouse_name)
                        carrier_id = data.get('carrier_id')
                        if carrier_id:
                            CarrierDetails.objects.create(shipment=outbound, carrier_id=int(id))
                        
                        files = request.FILES.getlist('files')
                        for file in files:
                            ProcessorWarehouseShipmentDocuments.objects.create(shipment=outbound, document_file=file)

                        
                    return redirect('list-processor-shipment')
                return render(request, 'distributor/create_outbound.html', context) 
            elif request.user.is_processor2:
                user = request.user
                processor_user = ProcessorUser2.objects.filter(contact_email=user.email)
                processor =  Processor2.objects.filter(id=processor_user.processor2.id).first()
                processor_id = processor.id
                processor_type = processor.processor_type.first().type_name
                processor_entity_name = processor.entity_name
                contracts = AdminProcessorContract.objects.filter(processor_type=processor_type, processor_id=processor_id).values('id','secret_key','processor_id','processor_type','processor_entity_name','crop')
                
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

                        print(context.get('carrier_type'),data.get('gross_weight'),  data.get('net_weight'),data.get('ship_quantity') )
                        if data.get('carrier_type') == 'Truck/Trailer':
                            gross_weight = float(data.get('gross_weight'))* int(data.get('ship_quantity'))
                            if data.get('net_weight') not in [None, 'null', ' ', '']:
                                print('00000')
                                net_weight = float(data.get('net_weight')) * int(data.get('ship_quantity'))
                            else:
                                context["error_messages"] = "Please give net weight."
                                return render(request, 'distributor/create_outbound.html', context)
                        elif data.get('carrier_type') == 'Rail Car':
                            gross_weight = 0
                            if data.get('weight') not in [None, 'null', ' ', '']:
                                net_weight = float(context.get('weight'))
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
                        outbound = ProcessorWarehouseShipment.objects.create(contract=contract, processor_id=processor_id, processor_type=processor_type, processor_entity_name=contract.processor_entity_name,
                                                                                processor_sku_list=[selected_sku_id],carrier_type=context.get('carrier_type'),outbound_type=context.get('outbound_type'),
                                                                                purchase_order_name=context.get('purchase_order_name'), purchase_order_number=context.get('purchase_order_number'), lot_number=context.get('lot_number'),
                                                                                gross_weight=gross_weight,net_weight=net_weight,weight_unit=context.get('amount_unit'), contract_weight_left=contract_weight_left,
                                                                                status= data.get('status'), customer_id=customer_id, warehouse_id=warehouse_id, customer_name=customer_name, warehouse_name=warehouse_name)
                        carrier_id = data.get('carrier_id')
                        if carrier_id:
                            CarrierDetails.objects.create(shipment=outbound, carrier_id=int(id))
                        
                        files = request.FILES.getlist('files')
                        for file in files:
                            ProcessorWarehouseShipmentDocuments.objects.create(shipment=outbound, document_file=file)

                        
                    return redirect('list-processor-shipment')
                return render(request, 'distributor/create_outbound.html', context) 
        else:
            return redirect('login')        
    except Exception as e:
        context["error_messages"] = str(e)
        return render(request, 'distributor/create_outbound.html', context) 


def list_processor_shipment(request):
    context = {}
    try:
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            processors = []
            processor1 = Processor.objects.all().values('id', 'entity_name')
            processor2 = Processor2.objects.all().values('id', 'entity_name', 'processor_type__type_name')
            
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
                shipments = shipments.filter()
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
            customer_id = Warehouse.objects.get(id=w.warehouse.id).id
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


