from django.shortcuts import render, HttpResponse
import requests, os
from requests_oauthlib import OAuth2Session
from django.shortcuts import redirect
from django.conf import settings
from quickbooks import QuickBooks

QUICKBOOKS_AUTHORIZATION_URL = "https://appcenter.intuit.com/connect/oauth2"
QUICKBOOKS_TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"


def create_customer(realm_id, access_token, customer_data):
    url = f'https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/customer'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    
    response = requests.post(url, headers=headers, json=customer_data)
    
    if response.status_code in (200, 201):
        return response.json()  # Return the created customer data
    else:
        # Log the error details for debugging
        print(f"Error creating customer: {response.status_code} - {response.text}")
        return None


def quickbooks_login(request):
    
    qb = OAuth2Session(
        client_id=settings.QUICKBOOKS_CLIENT_ID,
        redirect_uri=settings.QUICKBOOKS_REDIRECT_URI,
        scope=settings.QUICKBOOKS_SCOPES 
    )

    authorization_url, state = qb.authorization_url("https://appcenter.intuit.com/connect/oauth2")

    request.session['oauth_state'] = state

    return redirect(authorization_url)


def quickbooks_callback(request):
    
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    state = request.session.get('oauth_state')
    if not state:
        return HttpResponse("Error: 'oauth_state' not found in session.")

    qb = OAuth2Session(
        client_id=settings.QUICKBOOKS_CLIENT_ID,
        redirect_uri=settings.QUICKBOOKS_REDIRECT_URI,
        state=state  
    )
    try:
        token = qb.fetch_token(
            'https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer',
            client_secret=settings.QUICKBOOKS_CLIENT_SECRET,
            authorization_response=request.build_absolute_uri()
        )

        realm_id = request.GET.get('realmId')
        if not realm_id:
            return HttpResponse("Error: 'realmId' not found in the authorization response.")

        # Store token and realmId in session
        token['realmId'] = realm_id
        request.session['quickbooks_token'] = token

        return redirect('quickbooks_dashboard')
    except Exception as e:
        return HttpResponse(f"Error: {e}")


def quickbooks_dashboard(request):
    token = request.session.get('quickbooks_token')

    if not token:
        return redirect('quickbooks_login')

    # Ensure realmId exists in the session token
    realm_id = token.get('realmId')
    if not realm_id:
        return HttpResponse("Error: 'realmId' not found in session.")

    access_token = token['access_token']    

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
    }

    # Use the realmId for API requests
    url = f'https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/companyinfo/{realm_id}'
    response = requests.get(url, headers=headers)

    company_info = response.json()
    
    
    return render(request, 'dashboard.html', {'company_info': company_info})


def customer_create(request):
    token = request.session.get('quickbooks_token')
    print(token)

    if not token:
        return redirect('quickbooks_login')

    # Ensure realmId exists in the session token
    realm_id = token.get('realmId')
    if not realm_id:
        return HttpResponse("Error: 'realmId' not found in session.")

    access_token = token['access_token']
    print(access_token)

    customer_data = {
        "GivenName": "John",
        "FamilyName": "Doe",
        "DisplayName": "John Doe",
        "PrimaryEmailAddr": {
            "Address": "john.doe@example.com"
        },
        "PrimaryPhone": {
            "FreeFormNumber": "(123) 456-7890"
        },
        "BillAddr": {
            "Line1": "123 Main St",
            "City": "Anytown",
            "CountrySubDivisionCode": "CA",
            "PostalCode": "12345"
        },
        "ShipAddr": {
            "Line1": "456 Elm St",
            "City": "Anytown",
            "CountrySubDivisionCode": "CA",
            "PostalCode": "12345"
        }
    }

    # Create customer
    created_customer = create_customer(realm_id, access_token, customer_data)

    if created_customer:
        # Handle the response from creating the customer
        print("Customer created:", created_customer)
    else:
        # Handle errors appropriately
        print("Error creating customer")
    return render(request, 'dashboard.html', {'created_customer': created_customer})


from intuitlib.client import AuthClient
from quickbooks.objects.customer import Customer
def fetch_customers(request):
    token = request.session.get('quickbooks_token')
    print(token)

    if not token:
        return redirect('quickbooks_login')

    # Ensure realmId exists in the session token
    realm_id = token.get('realmId')
    if not realm_id:
        return HttpResponse("Error: 'realmId' not found in session.")

    access_token = token['access_token']
    refresh_token = token['refresh_token']
    print(access_token)

    auth_client = AuthClient(
        client_id=settings.QUICKBOOKS_CLIENT_ID,
        client_secret=settings.QUICKBOOKS_CLIENT_SECRET,
        access_token=access_token,  
        environment=settings.QUICKBOOKS_ENVIRONMENT,
        redirect_uri=settings.QUICKBOOKS_REDIRECT_URI,
    )
    client = QuickBooks(
        auth_client=auth_client,
        refresh_token=refresh_token,
        company_id=realm_id,
    )   
    try:
        customers = Customer.all(qb=client)
    except Exception as e:
        # Log the error and handle it gracefully
        print(f"Error fetching customers: {e}")
        customers = []  # Return an empty list in case of an error

    # Render the dashboard with the customers
    return render(request, "dashboard.html", {"customers": customers})


def refresh_token(token):
    refresh_url = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"

    refresh_payload = {
        'grant_type': 'refresh_token',
        'refresh_token': token['refresh_token'],
    }

    auth = (settings.QUICKBOOKS_CLIENT_ID, settings.QUICKBOOKS_CLIENT_SECRET)
    response = requests.post(refresh_url, data=refresh_payload, auth=auth)

    if response.status_code == 200:
        new_token = response.json()
        return new_token
    return None


def get_customer_details(request, pk):
    token = request.session.get('quickbooks_token')
    print(token)

    if not token:
        return redirect('quickbooks_login')

    # Ensure realmId exists in the session token
    realm_id = token.get('realmId')
    if not realm_id:
        return HttpResponse("Error: 'realmId' not found in session.")

    access_token = token['access_token']
    refresh_token = token['refresh_token']
    url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{realm_id}/customer/{pk}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()


def get_invoice(company_id, access_token, invoice_id):
    url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}/invoice/{invoice_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()


def get_vendor(company_id, access_token, vendor_id):
    url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}/vendor/{vendor_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_purchase(company_id, access_token, purchase_id):
    url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}/purchase/{purchase_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_item(company_id, access_token, item_id):
    url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}/item/{item_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()

def get_credit_memo(company_id, access_token, credit_memo_id):
    url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{company_id}/creditmemo/{credit_memo_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get(url, headers=headers)
    return response.json()