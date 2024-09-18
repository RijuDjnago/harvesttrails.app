from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.conf import settings
from apps.quickbooks_integration.helpers import get_auth_client

def quickbooks_connect(request):
    auth_client = get_auth_client()
    authorization_url = auth_client.get_authorization_url(["scopes"])
    return redirect(authorization_url)

def quickbooks_callback(request):
    auth_client = get_auth_client()
    state = request.GET.get('state')
    code = request.GET.get('code')

    auth_client.get_bearer_token(code, realm_id=None)
    request.session['access_token'] = auth_client.access_token
    return redirect('some_view_after_auth')

from quickbooks import QuickBooks
from quickbooks.objects.customer import Customer

def get_customers(request):
    qb_client = QuickBooks(
        access_token=request.session['access_token'],
        company_id='Your Company ID'
    )
    customers = Customer.all(qb=qb_client)
    return customers

from quickbooks.objects.invoice import Invoice

def get_invoices(request):
    qb_client = QuickBooks(
        access_token=request.session['access_token'],
        company_id='Your Company ID'
    )
    invoices = Invoice.all(qb=qb_client)
    return invoices

