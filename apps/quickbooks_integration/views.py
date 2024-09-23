from django.shortcuts import render, HttpResponse
import requests, os
from requests_oauthlib import OAuth2Session
from django.shortcuts import redirect
from django.conf import settings

QUICKBOOKS_AUTHORIZATION_URL = "https://appcenter.intuit.com/connect/oauth2"
QUICKBOOKS_TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"


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
