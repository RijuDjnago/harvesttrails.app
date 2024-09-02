'''View Functions for Field app'''
import asyncio
import os
import pathlib
from asyncio import Semaphore, ensure_future
from dataclasses import field
import warnings
from django import forms
import pandas as pd
from apps.field.field_column import FieldColoumChoices
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseRedirect
from django.db.utils import IntegrityError
from django.db.models import Q, Count
import re
from apps.field.models import CsvToField, ShapeFileDataCo
# from apps.grower.models import Grower
from apps.farms.models import Farm
from apps.contracts.models import Contracts, SignedContracts, ContractsVerifiers, VerifiedSignedContracts, \
    GrowerContracts
from apps.grower.models import Consultant, Grower
from . import forms
import shapefile
from django.http import JsonResponse
import json
import requests
import datetime
import time
from datetime import date, timedelta, datetime
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from urllib.parse import urlparse
import geojson
import numpy as np
import geopandas as gpd
from apps.grower.signals import send_contract_verification_email
from apps.growersurvey.views import render_to_pdf
from docusign_esign import EnvelopesApi
from django.views.generic.base import RedirectView
from django.conf import settings as conf_settings
from django.urls import reverse
from django.contrib.staticfiles.storage import staticfiles_storage
import base64
from docusign_esign.client.api_client import ApiException
from docusign_esign import EnvelopesApi, RecipientViewRequest, Document, Signer, EnvelopeDefinition, SignHere, Tabs, \
    Recipients
from apps.docusign.utils import create_api_client
from apps.docusign.consts import authentication_method, demo_docs_path, pattern, signer_client_id
from apps.accounts.models import User, Role, SubSuperUser, ShowNotification
from apps.contracts.DocusignEmbedded import DocusignEmbeddedSigningController
import requests
import threading
from asgiref.sync import sync_to_async, async_to_sync
from apps.contracts.tasks import create_envelope_and_store
from django.contrib.auth.decorators import login_required
from apps.processor.models import Processor, ProcessorUser
from apps.processor2.models import Processor2, ProcessorUser2
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from apps.contracts.models import *
from apps.warehouseManagement.models import Customer, CustomerUser


warnings.simplefilter(action='ignore', category=FutureWarning)


# pylint: disable=no-member,expression-not-assigned, too-many-locals, too-many-ancestors, too-many-ancestors, bare-except


# class Eg001EmbeddedSigningController:
#     base_path = 'https://demo.docusign.net/restapi/'
#     account_id = 'ff270191-6865-46c0-b877-612897b757f8'
#     access_token = os.getenv('DOCUSIGN_ACCESS_TOKEN',
#                              'eyJ0eXAiOiJNVCIsImFsZyI6IlJTMjU2Iiwia2lkIjoiNjgxODVmZjEtNGU1MS00Y2U5LWFmMWMtNjg5ODEyMjAzMzE3In0.AQsAAAABAAUABwCA2cMeDGHaSAgAgBnnLE9h2kgCAP-kGvOW52dIntbCAV0jZ5wVAAEAAAAYAAEAAAAFAAAADQAkAAAANzQ4YzUyNzktOTc5NS00YjM5LWJkMTktNGRmNmI5OWU3ODRiIgAkAAAANzQ4YzUyNzktOTc5NS00YjM5LWJkMTktNGRmNmI5OWU3ODRiEgABAAAACwAAAGludGVyYWN0aXZlMAAAV8r8C2HaSDcA-1dAj9iZOE-7cToSPBcQGQ.pKBWrpfW8c7FqyEN4_kOpUvsE5N3Ew0FB-oP0L06KlEXDNqYWH_OlEmOhO_knU1GXZyKrpD1FsbJAnwhFCLmdEDBjwmQMp1qr3cgQb-5-7XaJ_rT2YFzuPeqWux0Pw4DN8x7zxSHuIgeo7a-JZmyPnW-KWm1pnt0qpZWhe1wHnGXnGzyu_KBgh5TNmC-J8WPNJNKaDzsoEqxCYdCNfwTI8AkzqdfGRGXn_DweKNNZ7bfgxiRMAIuJ2pdKM9s5-chFKO3_D8uDYoaoFk9vR93efbyZYb4Hl8qhDMt5aCqvbX2rN3uDPDknSv7wTJKx2E6VRCiAKH8fKNxyDZOQz04ug')
#     refresh_token = os.getenv('DOCUSIGN_REFRESH_TOKEN',
#                               'eyJ0eXAiOiJNVCIsImFsZyI6IlJTMjU2Iiwia2lkIjoiNjgxODVmZjEtNGU1MS00Y2U5LWFmMWMtNjg5ODEyMjAzMzE3In0.AQoAAAABAAgABwCA2cMeDGHaSAgAgFkoF5942kgCAP-kGvOW52dIntbCAV0jZ5wVAAEAAAAYAAEAAAAFAAAADQAkAAAANzQ4YzUyNzktOTc5NS00YjM5LWJkMTktNGRmNmI5OWU3ODRiIgAkAAAANzQ4YzUyNzktOTc5NS00YjM5LWJkMTktNGRmNmI5OWU3ODRiMAAAV8r8C2HaSDcA-1dAj9iZOE-7cToSPBcQGQ.G0iVE6LQiig_mpUHqkFiy1IDVV7FdJs2qPIPn0vWZSqN-Et8_64H4z5tFRW4PPpvYAdVX7FqToNrkcsYU3VI19v8XRPhRRakQImxqBVVsNtDriBDmVk07Y8N_ukzFXYYRxu0_dC6k9bzOK6J1jEq9ga-rKRMFCSpCjKkPPlF89MWE4L6EVI00D6NUbMioSJ_EpcjQ7Fao1O1uCFI548qVMuj0PfV1gxmeIZMvXDPdXZzdbF_vrSNDAm_zuADxtsWKuKbu-TGB4WmmOQeQbpbY1cIiduBrM4CwismPccD7mYep0VAVkHh9R5KqPnm-7RGqj28HPipT8bRr0KTNQZnow')
#     client_id = '748c5279-9795-4b39-bd19-4df6b99e784b'
#     redirect_uri = 'https://www.example.com/callback'
#
#     def __init__(self):
#         self.account_id = 'ff270191-6865-46c0-b877-612897b757f8'
#         self.base_path = 'https://demo.docusign.net/restapi/'
#
#     @classmethod
#     def get_args(cls, signer_email, signer_name, signer_client_id, session, contract, grower, request):
#         """Get request and session arguments"""
#         # More data validation would be a good idea here
#         # Strip anything other than characters listed
#         # 1. Parse request arguments
#         # signer_email = signer_email
#         # signer_name = signer_name
#         envelope_args = {
#             "signer_email": signer_email,
#             "signer_name": signer_name,
#             "signer_client_id": signer_client_id,
#             "ds_return_url": request.build_absolute_uri(
#                 reverse('docusign-contract-submit', kwargs={'contract_id': contract.id, 'grower_id': grower.id})),
#         }
#         args = {
#             "account_id": cls.account_id,
#             "base_path": cls.base_path,
#             "access_token": cls.access_token,
#             "envelope_args": envelope_args
#         }
#         return args
#
#     @classmethod
#     def create_envelope(cls, envelope_api, envelope_definition):
#         """
#         """
#         results = envelope_api.create_envelope(account_id=cls.account_id, envelope_definition=envelope_definition)
#         print(results)
#         return results
#
#     @classmethod
#     def create_recipient_view_request(cls, envelope_args):
#         """
#         """
#         recipient_view_request = RecipientViewRequest(
#             authentication_method=authentication_method,
#             client_user_id=envelope_args["signer_client_id"],
#             recipient_id="1",
#             return_url=envelope_args["ds_return_url"],
#             user_name=envelope_args["signer_name"],
#             email=envelope_args["signer_email"]
#         )
#         print(recipient_view_request)
#         return recipient_view_request
#
#     @classmethod
#     def create_recipient_view(cls, envelope_api, envelope_id, recipient_view_request):
#         """
#         """
#         results = envelope_api.create_recipient_view(
#             account_id=cls.account_id,
#             envelope_id=envelope_id,
#             recipient_view_request=recipient_view_request
#         )
#         print(results)
#         return results
#
#     @classmethod
#     def create_sender_view(cls, envelope_id, return_url):
#         """
#         """
#         api_client = create_api_client(base_path=cls.base_path, access_token=cls.access_token)
#         envelope_api = EnvelopesApi(api_client)
#         results = envelope_api.create_sender_view(
#             account_id=cls.account_id,
#             envelope_id=envelope_id,
#             return_url_request=return_url
#         )
#         print(results)
#         return results
#
#     @classmethod
#     def get_envelope(cls, envelope_id):
#         """
#         """
#         api_client = create_api_client(base_path=cls.base_path, access_token=cls.access_token)
#
#         envelope_api = EnvelopesApi(api_client)
#         results = envelope_api.get_envelope(
#             account_id=cls.account_id,
#             envelope_id=envelope_id
#         )
#         print(results)
#         return results
#
#     @classmethod
#     def get_document_file(cls, envelope_id, document_id):
#         """
#         """
#         api_client = create_api_client(base_path=cls.base_path, access_token=cls.access_token)
#
#         envelope_api = EnvelopesApi(api_client)
#         results = envelope_api.get_document(
#             account_id=cls.account_id,
#             envelope_id=envelope_id,
#             document_id=document_id
#         )
#         print(results)
#         return results
#
#     @staticmethod
#     def get_error_response_body(res):
#         error_body_json = res and hasattr(res, "body") and res.body
#         # we can pull the DocuSign error code and message from the response body
#         try:
#             error_body = json.loads(error_body_json)
#         except json.decoder.JSONDecodeError:
#             error_body = {}
#         return error_body
#
#     def get_auth_token(self, code):
#         url = "https://account-d.docusign.com/oauth/token"
#
#         # payload = f'code={code}&grant_type=authorization_code'
#         payload = f'grant_type=refresh_token&refresh_token={os.getenv("DOCUSIGN_REFRESH_TOKEN")}'
#         iKeyiSec = "748c5279-9795-4b39-bd19-4df6b99e784b:ec4e772b-6334-404d-b931-39cca6cd5be3"
#         b64Val = base64.b64encode(iKeyiSec.encode())
#         headers = {
#             'Authorization': f'Basic {b64Val}',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         }
#         response = requests.request("POST", url, headers=headers, data=payload)
#         data = response.json()
#         print(data)
#         access_token = data['access_token']
#         token_type = data['token_type']
#         refresh_token = data['refresh_token']
#         os.environ['DOCUSIGN_ACCESS_TOKEN'] = access_token
#         os.environ['DOCUSIGN_REFRESH_TOKEN'] = refresh_token
#
#     @classmethod
#     def get_code_from_url(cls, request):
#         print(request.build_absolute_uri(reverse('contract-list')))
#         url = f"https://account-d.docusign.com/oauth/auth?response_type=code&scope=signature&client_id={cls.client_id}&redirect_uri={request.build_absolute_uri(reverse('contract-list'))}"
#         response = requests.request("GET", url)
#         print(f'inside code from url {response}')
#         for i in response.history:
#             print(i.url)
#
#     @classmethod
#     def get_list_of_documents(cls, envelope_id, request):
#         """
#         """
#         try:
#             api_client = create_api_client(base_path=cls.base_path, access_token=cls.access_token)
#
#             envelope_api = EnvelopesApi(api_client)
#             results = envelope_api.list_documents(
#                 account_id=cls.account_id,
#                 envelope_id=envelope_id
#             )
#             print(results)
#             return results
#         except Exception as err:
#             print("inside get list documents")
#             if err.body and cls.get_error_response_body(err)['errorCode'] == 'USER_AUTHENTICATION_FAILED':
#                 print("inside exception USER_AUTHENTICATION_FAILED")
#             print(type(err))
#             print(err)
#
#     @classmethod
#     def get_document_tabs(cls, envelope_id, document_id):
#         """
#         """
#         api_client = create_api_client(base_path=cls.base_path, access_token=cls.access_token)
#
#         envelope_api = EnvelopesApi(api_client)
#         results = envelope_api.get_document_tabs(
#             account_id=cls.account_id,
#             envelope_id=envelope_id,
#             document_id=document_id
#         )
#         print(results)
#         return results
#
#     @classmethod
#     def recreate_recepient_view(cls, envelope_id, args):
#         """
#         1. Create the envelope request object
#         2. Send the envelope
#         3. Create the Recipient View request object
#         4. Obtain the recipient_view_url for the embedded signing
#         """
#         envelope_args = args["envelope_args"]
#         # 1. Create the envelope request object
#
#         # 2. call Envelopes::create API method
#         # Exceptions will be caught by the calling function
#         api_client = create_api_client(base_path=args["base_path"], access_token=args["access_token"])
#
#         envelope_api = EnvelopesApi(api_client)
#
#         # 3. Create the Recipient View request object
#         recipient_view_request = cls.create_recipient_view_request(envelope_args)
#         # 4. Obtain the recipient_view_url for the embedded signing
#         # Exceptions will be caught by the calling function
#         results = cls.create_recipient_view(envelope_api, envelope_id, recipient_view_request)
#         return {"envelope_id": envelope_id, "redirect_url": results.url}
#
#     @classmethod
#     def worker(cls, args):
#         """
#         1. Create the envelope request object
#         2. Send the envelope
#         3. Create the Recipient View request object
#         4. Obtain the recipient_view_url for the embedded signing
#         """
#         envelope_args = args["envelope_args"]
#         # 1. Create the envelope request object
#         envelope_definition = cls.make_envelope(envelope_args)
#
#         # 2. call Envelopes::create API method
#         # Exceptions will be caught by the calling function
#         api_client = create_api_client(base_path=args["base_path"], access_token=args["access_token"])
#
#         envelope_api = EnvelopesApi(api_client)
#         results = cls.create_envelope(envelope_api, envelope_definition)
#
#         envelope_id = results.envelope_id
#         envelope_uri = results.uri
#
#         # 3. Create the Recipient View request object
#         recipient_view_request = cls.create_recipient_view_request(envelope_args)
#         # 4. Obtain the recipient_view_url for the embedded signing
#         # Exceptions will be caught by the calling function
#         results = cls.create_recipient_view(envelope_api, envelope_id, recipient_view_request)
#         return {"envelope_id": envelope_id, "redirect_url": results.url, 'envelope_uri': envelope_uri}
#
#     @classmethod
#     def worker_envelope_id(cls, envelope_id, request, args):
#         """
#         1. Get envelop id
#         2. Send the envelope
#         3. Create the Recipient View request object
#         4. Obtain the recipient_view_url for the embedded signing
#         """
#         try:
#             envelope_args = args["envelope_args"]
#             # 1. Create the envelope request object
#             envelope_definition = cls.make_envelope_from_envelope_id(envelope_id, envelope_args, request)
#
#             # 2. call Envelopes::create API method
#             # Exceptions will be caught by the calling function
#             api_client = create_api_client(base_path=args["base_path"], access_token=args["access_token"])
#
#             envelope_api = EnvelopesApi(api_client)
#             results = cls.create_envelope(envelope_api, envelope_definition)
#
#             envelope_id = results.envelope_id
#             envelope_uri = results.uri
#
#             # 3. Create the Recipient View request object
#             recipient_view_request = cls.create_recipient_view_request(envelope_args)
#             # 4. Obtain the recipient_view_url for the embedded signing
#             # Exceptions will be caught by the calling function
#             results = cls.create_recipient_view(envelope_api, envelope_id, recipient_view_request)
#             return {"envelope_id": envelope_id, "redirect_url": results.url, 'envelope_uri': envelope_uri}
#         except Exception as ex:
#             print("inside worker using id")
#             print(ex)
#
#     @classmethod
#     def make_envelope_from_envelope_id(cls, envelope_id, args, request):
#         """
#         Creates envelope
#         args -- parameters for the envelope:
#         signer_email, signer_name, signer_client_id
#         returns an envelope definition
#         """
#
#         # document 1 (pdf) has tag /sn1/
#         #
#         # The envelope has one recipient.
#         # recipient 1 - signer
#         # Create the signer recipient model
#         try:
#
#             signer = Signer(
#                 # The signer
#                 email=args["signer_email"],
#                 name=args["signer_name"],
#                 recipient_id="1",
#                 routing_order="1",
#                 # Setting the client_user_id marks the signer as embedded
#                 client_user_id=args["signer_client_id"]
#             )
#
#             # document_list = cls.get_list_of_documents(envelope_id)
#             document_list = []
#             envelope_documents_list = cls.get_list_of_documents(envelope_id, request)
#             for envelope_document in envelope_documents_list.envelope_documents:
#                 if envelope_document.type == 'content':
#                     response = cls.get_document_file(envelope_id, envelope_document.document_id)
#                     with open(response, "rb") as file:
#                         content_bytes = file.read()
#                     base64_file_content = base64.b64encode(content_bytes).decode("ascii")
#                     document = Document(  # create the DocuSign document object
#                         document_base64=base64_file_content,
#                         name=envelope_document.name,  # can be different from actual file name
#                         file_extension=pathlib.Path(response).suffix,  # many different document types are accepted
#                         document_id=envelope_document.document_id  # a label used to reference the doc
#                     )
#                     document_list.append(document)
#                     signer.tabs = cls.get_document_tabs(envelope_id, envelope_document.document_id)
#
#             # Add the tabs model (including the sign_here tab) to the signer
#             # The Tabs object wants arrays of the different field/tab types
#             # signer.tabs = Tabs(sign_here_tabs=[sign_here])
#
#             # Next, create the top level envelope definition and populate it.
#             envelope_definition = EnvelopeDefinition(
#                 email_subject="Please sign this document sent from the Python SDK from envelope id",
#                 documents=document_list,
#                 # The Recipients object wants arrays for each recipient type
#                 recipients=Recipients(signers=[signer]),
#                 status="sent"  # requests that the envelope be created and sent.
#             )
#             return envelope_definition
#         except Exception as ex:
#             print("inside make envelope using id")
#             print(ex)
#
#     @classmethod
#     def make_envelope(cls, args):
#         """
#         Creates envelope
#         args -- parameters for the envelope:
#         signer_email, signer_name, signer_client_id
#         returns an envelope definition
#         """
#
#         # document 1 (pdf) has tag /sn1/
#         #
#         # The envelope has one recipient.
#         # recipient 1 - signer
#         filepath = staticfiles_storage.path('demo_documents/' + conf_settings.DS_CONFIG["doc_pdf"])
#         with open(filepath, "rb") as file:
#             content_bytes = file.read()
#         base64_file_content = base64.b64encode(content_bytes).decode("ascii")
#
#         # Create the document model
#         document = Document(  # create the DocuSign document object
#             document_base64=base64_file_content,
#             name="Example document",  # can be different from actual file name
#             file_extension="pdf",  # many different document types are accepted
#             document_id=1  # a label used to reference the doc
#         )
#
#         # Create the signer recipient model
#         signer = Signer(
#             # The signer
#             email=args["signer_email"],
#             name=args["signer_name"],
#             recipient_id="1",
#             routing_order="1",
#             # Setting the client_user_id marks the signer as embedded
#             client_user_id=args["signer_client_id"]
#         )
#
#         # Create a sign_here tab (field on the document)
#         sign_here = SignHere(
#             # DocuSign SignHere field/tab
#             anchor_string="/sn1/",
#             anchor_units="pixels",
#             anchor_y_offset="10",
#             anchor_x_offset="20"
#         )
#
#         # Add the tabs model (including the sign_here tab) to the signer
#         # The Tabs object wants arrays of the different field/tab types
#         signer.tabs = Tabs(sign_here_tabs=[sign_here])
#
#         # Next, create the top level envelope definition and populate it.
#         envelope_definition = EnvelopeDefinition(
#             email_subject="Please sign this document sent from the Python SDK",
#             documents=[document],
#             # The Recipients object wants arrays for each recipient type
#             recipients=Recipients(signers=[signer]),
#             status="sent"  # requests that the envelope be created and sent.
#         )
#
#         return envelope_definition


class UpdateDocumentSignedView(LoginRequiredMixin, RedirectView):
    '''Generic Class Based view to list all the field objects in database'''
    permanent = False
    query_string = True
    url = None

    def get_redirect_url(self, *args, **kwargs):
        url_parameters = re.findall(r'\d+', self.request.get_full_path())
        grower_contract = GrowerContracts.objects.get(contract_id=url_parameters[0], grower_id=url_parameters[1])

        if "ttl_expired" == self.request.GET.get("event"):
            embedded = DocusignEmbeddedSigningController()
            args = embedded.get_args(grower_contract.grower.email, grower_contract.grower.name,
                                     grower_contract.grower.id,
                                     self.request.session, grower_contract.contract, grower_contract.grower,
                                     self.request)
            self.request.META["QUERY_STRING"] = None
            self.url = embedded.recreate_recepient_view(grower_contract.envelope_id, args)["redirect_url"]
            parsed_uri = urlparse(self.url)
            self.request.META["PATH_INFO"] = parsed_uri.path
            self.request.META["HTTP_HOST"] = parsed_uri.netloc
        if "signing_complete" == self.request.GET.get("event"):
            grower_contract.is_signed = True
            grower_contract.save()
            self.request.META["QUERY_STRING"] = None
            self.url = reverse('contract-list')
        return super().get_redirect_url(*args, **kwargs)


class DocusignCallbackUrlForAuth(LoginRequiredMixin, ListView):
    """Generic Class Based view to list all the field objects in database"""

    def get_redirect_field_name(self):
        if self.request.GET.get("code"):
            print(self.request.GET.get("code"))
            url = "https://account-d.docusign.com/oauth/token"

            payload = f'code={self.request.GET.get("code")}&grant_type=authorization_code'
            iKeyiSec = "748c5279-9795-4b39-bd19-4df6b99e784b:ec4e772b-6334-404d-b931-39cca6cd5be3"
            b64Val = base64.b64encode(iKeyiSec.encode())
            headers = {
                'Authorization': f'Basic {b64Val}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            data = response.json()
            access_token = data['access_token']
            token_type = data['token_type']
            refresh_token = data['refresh_token']
            os.environ['DOCUSIGN_ACCESS_TOKEN'] = access_token


class ContractsListView(LoginRequiredMixin, ListView):
    """Generic Class Based view to list all the field objects in database"""
    model = Contracts
    context_object_name = 'Contracts'
    template_name = 'contracts/contracts_list.html'

    def get_queryset(self):
        if self.request.user.grower:
            grower_contracts = GrowerContracts.objects.filter(grower_id=self.request.user.grower.id).order_by(
                '-modified_date')
            data = [
                {'name': grower_contract.contract.name, 'signed_contract_count': 0, 'url': grower_contract.contract_url,
                 'is_signed': grower_contract.is_signed} for grower_contract in grower_contracts]
        else:
            contracts = Contracts.objects.all().order_by('-modified_date')
            data = [{'name': contract.name,
                     'signed_contract_count': GrowerContracts.objects.filter(contract=contract, is_signed=True).count(),
                     'envelope_id': contract.envelope_id} for contract in contracts]
        return data


def create_grower_save(contract, grower, results, created_by):
    grower_contract = GrowerContracts.objects.create(contract=contract,
                                                     contract_url=results['url'],
                                                     grower=grower,
                                                     created_by=created_by,
                                                     envelope_id=results['envelope_id']
                                                     )
    print(grower_contract)
    grower_contract.save()


async def get_envelope_results(grower, contract, request):
    try:
        args = DocusignEmbeddedSigningController.get_args(grower.email, grower.name,
                                                          grower.id, request.session, contract,
                                                          grower, request)
        results = DocusignEmbeddedSigningController.worker_envelope_id(contract.envelope_id, request, args)
        # await create_grower_save(contract, grower, results, request.user)
        grower_contract = GrowerContracts.objects.create(contract=contract,
                                                         contract_url=results['url'],
                                                         grower=grower,
                                                         created_by=request.user,
                                                         envelope_id=results['envelope_id']
                                                         )
        print(grower_contract)
        sync_to_async(grower_contract.save, thread_sensitive=True)
    except Exception as err:
        return print(err)


async def create_grower_contracts(growers, contract, request):
    for grower in growers:
        asyncio.ensure_future(get_envelope_results(grower, contract, request))  # fire and forget async_foo()


def loop_in_thread(loop, growers, contract, request):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(create_grower_contracts(growers, contract, request))


def get_envelope_id_and_save_in_db(grower, contract, request, document_list, tabs):
    try:
        args = DocusignEmbeddedSigningController.get_args(grower.email, grower.name,
                                                          grower.id, request.session, contract,
                                                          grower, request)
        results = DocusignEmbeddedSigningController.worker_envelope_id(document_list, tabs, args)
        grower_contract = GrowerContracts.objects.create(contract=contract,
                                                         contract_url=results['redirect_url'],
                                                         grower=grower,
                                                         created_by=request.user,
                                                         envelope_id=results['envelope_id']
                                                         )
        grower_contract.save()
    except Exception as err:
        return print(err)


class ContractsCreateView(LoginRequiredMixin, CreateView):
    """Generic Class Based view to create a new field"""
    model = Contracts
    # fields = "__all__"
    form_class = forms.ContractCreateForm
    template_name = 'contracts/contract_create.html'
    success_url = reverse_lazy('contract-list')

    def form_valid(self, form):
        """overriding this method to get a message after successfully creating new Field"""
        form.instance.created_by = self.request.user
        contract = form.save()


        # try:
        #     loop = asyncio.get_running_loop()
        #
        # except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        #     loop = asyncio.new_event_loop()
        #
        # t = threading.Thread(target=loop_in_thread, args=(loop, growers[:10], contract, self.request))
        # t.start()
        # try:
        #     embedded = DocusignEmbeddedSigningController()
        #     document_list, tabs = embedded.get_document_list_from_envelope_id_with_tabs(contract.envelope_id)
        # except Exception as err:
        #     return print(err)
        return_url = self.request.build_absolute_uri(
            reverse('docusign-contract-submit', kwargs={'contract_id': contract.id, 'grower_id': contract.id}))

        create_envelope_and_store.delay(contract.id, self.request.user.username, return_url)
        # for grower in growers: sync_to_async(get_envelope_id_and_save_in_db, thread_sensitive=True)(grower,
        # contract, self.request, document_list, tabs)
        messages.success(self.request, f'Contract Created Successfully!')
        return super(ContractsCreateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ContractsCreateView, self).get_context_data(**kwargs)
        context["is_create"] = True
        return context


class ContractsUpdateView(LoginRequiredMixin, UpdateView):
    model = Contracts
    # fields = "__all__"
    form_class = forms.ContractCreateForm
    template_name = 'contracts/contract_create.html'
    success_url = reverse_lazy('contract-list')

    def form_valid(self, form):
        """overriding this method to get a message after successfully creating new Field"""
        form.instance.created_by = self.request.user
        form.save()
        messages.success(self.request, f'Contract Updated Successfully!')
        return super(ContractsUpdateView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ContractsUpdateView, self).get_context_data(**kwargs)
        context["is_create"] = False
        return context


class SignedContractsListView(LoginRequiredMixin, ListView):
    '''Generic Class Based view to list all the field objects in database'''
    model = SignedContracts
    template_name = 'contracts/signed_contracts_list.html'

    def get_queryset(self):
        """overriding the queryset to return all the fields in the database when a superuser is logged in,
        and to get only the fields mapped to the logged in user's grower"""
        if 'Grower' in self.request.user.get_role() and not self.request.user.is_superuser:
            # do something grower
            # SustainabilitySurvey_data = SustainabilitySurvey.objects.filter(grower_id=request.user.grower.id)
            return self.model.objects.filter(grower_id=self.request.user.grower.id).order_by('-created_date')
            # return self.model.objects.all().order_by('-created_date')
        else:
            if self.request.user.is_consultant:
                # do something consultant
                consultant_id = Consultant.objects.get(email=self.request.user.email).id
                get_growers = Grower.objects.filter(consultant=consultant_id)
                grower_ids = [data.id for data in get_growers]
                grower_data = Grower.objects.filter(id__in=grower_ids)
                return self.model.objects.filter(grower__in=grower_data).order_by('-created_date')
            else:
                # do something allpower
                return self.model.objects.all().order_by('-created_date')


class ContractDetailView(LoginRequiredMixin, DetailView):
    """Generic Class Based View for user detail page"""
    model = Contracts
    template_name = 'contracts/contracts_detail.html'

    def get_context_data(self, **kwargs):
        context = super(ContractDetailView, self).get_context_data(**kwargs)
        is_signed = False
        signature = ""
        signatures = []
        if self.request.user.grower:
            singed_data = SignedContracts.objects.filter(
                contract_id=self.kwargs.get('pk'),
                grower_id=self.request.user.grower.id
            ).last()
            if singed_data:
                is_signed = True
                signature = singed_data.signature
        else:
            signatures = SignedContracts.objects.filter(
                contract_id=self.kwargs.get('pk'),
            ).values("signature", "grower__name")
            if signatures:
                is_signed = True
        context["is_signed"] = is_signed
        context["signature"] = signature
        context["signatures"] = signatures
        return context


class ContractsSignSaveView(LoginRequiredMixin, CreateView):
    @classmethod
    def post(cls, request):
        '''Default function for get request'''
        signature = request.POST.get('signature')
        grower_id = request.POST.get('grower_id')
        contract_id = request.POST.get('contract_id')

        # Adding signature to contracts
        signed_contract = SignedContracts.objects.create(
            signature=signature,
            contract_id=contract_id,
            grower_id=grower_id,
            created_by=request.user
        )

        # Updating Contracts is_signed Status
        Contracts.objects.filter(
            id=contract_id
        ).update(
            is_signed=True
        )

        # Sending Email to Verifiers
        verifiers = ContractsVerifiers.objects.filter(
            contract_id=contract_id
        )
        for verifier in verifiers:
            verified_signer = VerifiedSignedContracts.objects.create(
                name=verifier.name,
                email=verifier.email,
                signature="",
                signed_contracts=signed_contract,
                is_verified=False,
            )
            contract_verification_link = "http://traceableoutcomes.tech/contracts/signed/" + str(
                verified_signer.id) + "/details/"
            # Send Email Invite
            send_contract_verification_email(
                verifier,
                [verifier.email],
                request.user.grower.name,
                contract_verification_link
            )

        messages.success(request, f'Signed Contract Successfully!')
        return HttpResponseRedirect('/contracts/list/')


class SignedContractDetailView(DetailView):
    """Generic Class Based View for user detail page"""
    model = VerifiedSignedContracts
    template_name = 'contracts/signed_contract_details.html'

    def get_context_data(self, **kwargs):
        context = super(SignedContractDetailView, self).get_context_data(**kwargs)
        return context


class ContractsSignVerificationSaveView(CreateView):
    @classmethod
    def post(cls, request):
        '''Default function for get request'''
        signature = request.POST.get('signature')
        pk = request.POST.get('pk')

        # Adding signature to contracts
        VerifiedSignedContracts.objects.filter(
            id=pk
        ).update(
            signature=signature,
            is_verified=True
        )
        messages.success(request, f'Verification Successful!')
        return HttpResponseRedirect('/contracts/signed/' + str(pk) + '/details/')


class ContractPdfView(LoginRequiredMixin, ListView):
    @classmethod
    def get(cls, request, pk, **kwargs):
        contract_signers = []
        signed_contracts = SignedContracts.objects.get(id=pk)
        contract_title = signed_contracts.contract.name
        contract_details = signed_contracts.contract.contract
        grower_data = {
            "name": signed_contracts.grower.name,
            "signature": signed_contracts.signature,
        }
        contract_signers.append(grower_data)

        verified_contracts = VerifiedSignedContracts.objects.filter(
            signed_contracts=signed_contracts
        ).all()
        for i in verified_contracts:
            data = {
                "name": i.name,
                "signature": i.signature,
            }
            contract_signers.append(data)

        return render_to_pdf(
            'contracts/contract_pdf.html',
            {
                "contract_title": contract_title,
                "contract_details": contract_details,
                "contract_signers": contract_signers,
            }
        )
  

@login_required()
def admin_processor_contract_create(request):
    context = {}
    try:
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            # Get processors and add to context
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
            
            if request.method == "POST":
                print("post method is hit")
                # Extract data from the POST request
                selected_processor = request.POST.get('selected_processor')
                selected_crop = request.POST.get('crop')
                crop_type = request.POST.get('crop_type')
                contract_amount = request.POST.get('contract_amount')
                amount_unit = request.POST.get('amount_unit')
                contract_start_date = request.POST.get('contract_start_date')
                contract_period = request.POST.get('contract_period')
                status = request.POST.get('status')                
                print(selected_processor)
                # Ensure selected_processor is not empty and correctly formatted
                if selected_processor:
                    try:
                        processor_id, processor_type = selected_processor.split("_")
                    except ValueError:
                        context["error_messages"] = "Invalid processor selection."
                        return render(request, 'contracts/create_admin_processor_contract.html', context)
                    
                    # Retrieve the processor object
                    if processor_type == "T1":
                        processor = Processor.objects.filter(id=processor_id).first()
                    else:
                        processor = Processor2.objects.filter(id=processor_id).first()
                    
                    # Check if the processor exists
                    if not processor:
                        context["error_messages"] = "Selected processor does not exist."
                        return render(request, 'contracts/create_admin_processor_contract.html', context)
                    
                    contract = AdminProcessorContract.objects.create(                        
                        processor_id=processor_id, 
                        processor_type=processor_type,
                        processor_entity_name=processor.entity_name, 
                        crop=selected_crop,
                        crop_type = crop_type,
                        contract_amount=contract_amount, 
                        amount_unit=amount_unit,
                        contract_start_date=contract_start_date, 
                        contract_period=contract_period,
                        status=status, 
                        created_by_id=request.user.id
                    )

                    ## Send notification to the processor.
                    if processor_type == "T1":
                        all_processor_user = ProcessorUser.objects.filter(processor_id=processor_id)
                    else:
                        all_processor_user = ProcessorUser2.objects.filter(processor2_id=processor_id)
                    for user in all_processor_user :
                        msg = 'A new Contract has been initiated between Admin and you.'
                        get_user = User.objects.get(username=user.contact_email)
                        notification_reason = 'New Contract Assigned.'
                        redirect_url = "/contracts/admin-processor-contract-list/"
                        save_notification = ShowNotification(user_id_to_show=get_user.id,msg=msg,status="UNREAD",redirect_url=redirect_url,
                            notification_reason=notification_reason)
                        save_notification.save()

                    document_names = request.POST.getlist('document_name[]')                   
                    
                    for name in document_names:
                        AdminProcessorContractDocuments.objects.create(
                            contract=contract,
                            name=name                            
                        )
                    
                    return redirect('list-contract')
                else:
                    context["error_messages"] = "Processor must be selected."
            
            return render(request, 'contracts/create_admin_processor_contract.html', context)
        else:
            messages.error(request, "Not a valid request.")
            return redirect("dashboard")                                  
    except (ValueError, AttributeError, AdminProcessorContract.DoesNotExist) as e:
        context["error_messages"] = str(e)
    return render(request, 'contracts/create_admin_processor_contract.html', context)


@login_required()
def admin_processor_contract_list(request):
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
            
            contracts = AdminProcessorContract.objects.all()
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
                contracts = contracts.filter(processor_id=int(processor_id))
            search_name = request.GET.get('search_name', '')   
            if search_name and search_name is not None:
                contracts = contracts.filter(Q(secret_key__icontains=search_name)| Q(crop__icontains=search_name))
                context['search_name'] = search_name
            else:
                context['search_name'] = None            
            
            contracts = contracts.order_by('-id')
            paginator = Paginator(contracts, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)             
            context['contracts'] = report
            return render(request, 'contracts/admin_processor_contract_list.html', context)
        
        elif request.user.is_processor:
            user_email = request.user.email
            p = ProcessorUser.objects.get(contact_email=user_email)
            processor_id = Processor.objects.get(id=p.processor.id).id
            processor_type = "T1"
            contracts = AdminProcessorContract.objects.filter(processor_id=processor_id, processor_type=processor_type)
            contracts = contracts.order_by('-id')
            paginator = Paginator(contracts, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)             
            context['contracts'] = report
            return render(request, 'contracts/admin_processor_contract_list.html', context)
        
        elif request.user.is_processor2:
            user_email = request.user.email
            p = ProcessorUser2.objects.get(contact_email=user_email)
            processor_id = Processor2.objects.get(id=p.processor2.id).id
            processor_type = Processor2.objects.get(id=p.processor2.id).processor_type.all().first().type_name

            contracts = AdminProcessorContract.objects.filter(processor_id=processor_id, processor_type=processor_type)
            contracts = contracts.order_by('-id')
            paginator = Paginator(contracts, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)             
            context['contracts'] = report
            return render(request, 'contracts/admin_processor_contract_list.html', context)
    
        else:
            messages.error(request, "Not a valid request.")
            return redirect("dashboard")   
    except (ValueError, AttributeError, AdminProcessorContract.DoesNotExist) as e:
        context["error_messages"] = str(e)
    return render(request, 'contracts/admin_processor_contract_list.html', context)


@login_required()
def admin_processor_contract_view(request, pk):
    context ={}
    try:
        # Superuser................
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role() or request.user.is_processor or request.user.is_processor2:
            contract = AdminProcessorContract.objects.filter(id=pk).first()
            documents = AdminProcessorContractDocuments.objects.filter(contract=contract)
            context["contract"] = contract
            
            context["documents"] = documents
            return render (request, 'contracts/admin_processor_contract_view.html', context)
        else:
            return redirect('login') 
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'contracts/admin_processor_contract_view.html', context)


@login_required()
def edit_admin_processor_contract(request, pk):
    context = {}
    try:
        contract = get_object_or_404(AdminProcessorContract, id=pk)       

        # Retrieve processors
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
                "type": pro2["processor_type__type_name"]
            })

        # Retrieve the documents associated with this contract
        documents = AdminProcessorContractDocuments.objects.filter(contract=contract)
        

        context = {
            "contract": contract,
            "processor": processors,
            'selected_processor_id': contract.processor_id,
            'selected_processor_type': contract.processor_type,
            "selected_crop": contract.crop,
            'crop_type': contract.crop_type,
            "contract_amount": contract.contract_amount,
            "amount_unit": contract.amount_unit,
            "contract_start_date": contract.contract_start_date,
            "contract_period": contract.contract_period,
            "status": contract.status,
            "documents": documents,
        }

        if request.method == "POST":
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
                # Handle updates by admin or superuser
                selected_processor = request.POST.get('selected_processor')
                selected_crop = request.POST.get('crop')
                contract_amount = request.POST.get('contract_amount')
                amount_unit = request.POST.get('amount_unit')
                contract_start_date = request.POST.get('contract_start_date')
                contract_period = request.POST.get('contract_period')
                status = request.POST.get('status')
                
                if selected_processor:
                    try:
                        processor_id, processor_type = selected_processor.split("_")
                    except ValueError:
                        context["error_messages"] = "Invalid processor selection."
                        return render(request, 'contracts/edit_admin_processor_contract.html', context)

                    if processor_type == "T1":
                        processor = Processor.objects.filter(id=processor_id).first()
                    else:
                        processor = Processor2.objects.filter(id=processor_id).first()

                    if not processor:
                        context["error_messages"] = "Selected processor does not exist."
                        return render(request, 'contracts/edit_admin_processor_contract.html', context)

                    # Update contract details
                    contract.processor_id = processor_id
                    contract.processor_type = processor_type
                    contract.processor_entity_name = processor.entity_name
                    contract.crop = selected_crop
                    contract.contract_amount = contract_amount
                    contract.amount_unit = amount_unit
                    contract.contract_start_date = contract_start_date
                    contract.contract_period = contract_period
                    contract.status = status
                    contract.save()

                    delete_document_ids = request.POST.getlist('delete_document_ids[]')
                    print(delete_document_ids)
                    for document_id in delete_document_ids:
                        try:
                            document = AdminProcessorContractDocuments.objects.get(id=document_id)
                            document.delete()  # Delete the document from the database
                        except AdminProcessorContractDocuments.DoesNotExist:
                            pass

                    document_ids =  request.POST.getlist('document_ids')
                    for document_id in document_ids:
                        document_status = f'document_status_{document_id}'
                        if document_status in request.POST:                            
                            document_stat = request.POST.get(document_status)                         
                            
                            document = AdminProcessorContractDocuments.objects.filter(id=document_id).first()
                            document.document_status = document_stat  # Assign the file to the FileField
                            document.save()                                
                            
                    document_names = request.POST.getlist('document_name[]')  
                    if document_names:                      
                    
                        for i, name in enumerate(document_names):
                            # Check if there's a corresponding document ID
                            if i < len(document_ids):
                                document_id = document_ids[i]
                                # Update existing document
                                document = AdminProcessorContractDocuments.objects.filter(id=document_id).first()
                                if document:
                                    document.name = name  # Update the name
                                    document.save()
                            else:
                                # Create new document if the document ID does not exist
                                AdminProcessorContractDocuments.objects.create(contract=contract, name=name)

                return redirect('list-contract')
            
            elif request.user.is_processor or request.user.is_processor2:
                document_ids = request.POST.getlist('document_ids')        
                for document_id in document_ids:
                    file_field_name = f'document_file_{document_id}'
                    
                    if file_field_name in request.FILES:
                        uploaded_file = request.FILES[file_field_name]
                        
                        
                        # Handle the uploaded file
                        try:
                            document = AdminProcessorContractDocuments.objects.get(id=document_id)
                            document.document = uploaded_file  # Assign the file to the FileField
                            document.save()
                            
                        except AdminProcessorContractDocuments.DoesNotExist:
                            # Handle the case where the document does not exist
                            pass
                contract.status = "Under Review"
                contract.save()
                return redirect('list-contract')
        return render(request, 'contracts/edit_admin_processor_contract.html', context)
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        context["error_messages"] = str(e)
        return render(request, 'contracts/edit_admin_processor_contract.html', context)


@login_required()
def admin_customer_contract_create(request):
    context = {}
    try:
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role() or request.user.is_distributor:
            # Get customers and add to context
            customers = Customer.objects.all().values('id', 'name')          
            context["customers"] = customers
            
            if request.method == "POST":
                print("post method is hit")
                # Extract data from the POST request
                selected_customer = request.POST.get('selected_customer')
                selected_crop = request.POST.get('crop')
                crop_type = request.POST.get('crop_type')
                contract_amount = request.POST.get('contract_amount')
                amount_unit = request.POST.get('amount_unit')
                contract_start_date = request.POST.get('contract_start_date')
                contract_period = request.POST.get('contract_period')
                status = request.POST.get('status')                
                print(selected_customer)
                # Ensure selected_customer is not empty and correctly formatted
                if selected_customer:
                    customer = Customer.objects.filter(id=selected_customer).first()                   
                    
                    if not customer:
                        context["error_messages"] = "Selected customer does not exist."
                        return render(request, 'contracts/create_admin_customer_contract.html', context)
                    
                    contract = AdminCustomerContract.objects.create(                        
                        customer_id=customer.id,                         
                        crop=selected_crop,
                        crop_type = crop_type,
                        contract_amount=contract_amount, 
                        amount_unit=amount_unit,
                        contract_start_date=contract_start_date, 
                        contract_period=contract_period,
                        status=status, 
                        created_by_id=request.user.id
                    )

                    ## Send notification to the customer.                    
                    all_customer_user = CustomerUser.objects.filter(customer_id=customer.id)
                    
                    for user in all_customer_user :
                        msg = 'A new Contract has been initiated between Admin and you.'
                        get_user = User.objects.get(username=user.contact_email)
                        notification_reason = 'New Contract Assigned.'
                        redirect_url = "/contracts/admin-customer-contract-list/"
                        save_notification = ShowNotification(user_id_to_show=get_user.id,msg=msg,status="UNREAD",redirect_url=redirect_url,
                            notification_reason=notification_reason)
                        save_notification.save()

                    document_names = request.POST.getlist('document_name[]')                   
                    
                    for name in document_names:
                        AdminCustomerContractDocuments.objects.create(
                            contract=contract,
                            name=name                            
                        )
                    
                    return redirect('admin-customer-contract-list')
                else:
                    context["error_messages"] = "Customer must be selected."
            
            return render(request, 'contracts/create_admin_customer_contract.html', context)
        else:
            messages.error(request, "Not a valid request.")
            return redirect("dashboard")                                  
    except (ValueError, AttributeError, AdminCustomerContract.DoesNotExist) as e:
        context["error_messages"] = str(e)
    return render(request, 'contracts/create_admin_customer_contract.html', context)


@login_required()
def admin_customer_contract_list(request):
    context = {}
    try:
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role():
            customers = Customer.objects.all().values('id', 'name')           
                    
            context["customers"] = customers            
            contracts = AdminCustomerContract.objects.all()
            selected_customer = request.GET.get('selected_customer','All')
            
            if selected_customer != 'All':
                customer_id = int(selected_customer)
                context['selected_customer_id'] = int(customer_id)
                
            else:   
                customer_id = None             
                context['selected_customer_id'] = None
                
            if selected_customer and selected_customer != 'All':                
                contracts = contracts.filter(customer_id=int(customer_id))
            search_name = request.GET.get('search_name', '')   
            if search_name and search_name is not None:
                contracts = contracts.filter(Q(secret_key__icontains=search_name)| Q(crop__icontains=search_name))
                context['search_name'] = search_name
            else:
                context['search_name'] = None            
            
            contracts = contracts.order_by('-id')
            paginator = Paginator(contracts, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)             
            context['contracts'] = report
            return render(request, 'contracts/admin_customer_contract_list.html', context)
        
        elif request.user.is_customer:
            user_email = request.user.email
            c = CustomerUser.objects.get(contact_email=user_email)
            customer_id = Customer.objects.get(id=c.customer.id).id

            contracts = AdminCustomerContract.objects.filter(customer_id=customer_id)
            contracts = contracts.order_by('-id')
            paginator = Paginator(contracts, 100)
            page = request.GET.get('page')
            try:
                report = paginator.page(page)
            except PageNotAnInteger:
                report = paginator.page(1)
            except EmptyPage:
                report = paginator.page(paginator.num_pages)             
            context['contracts'] = report
            return render(request, 'contracts/admin_customer_contract_list.html', context)      
        
    
        else:
            messages.error(request, "Not a valid request.")
            return redirect("dashboard")   
    except (ValueError, AttributeError, AdminProcessorContract.DoesNotExist) as e:
        context["error_messages"] = str(e)
    return render(request, 'contracts/admin_processor_contract_list.html', context)


@login_required()
def admin_customer_contract_view(request, pk):
    context ={}
    try:
        # Superuser................
        if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role() or request.user.is_customer:
            contract = AdminCustomerContract.objects.filter(id=pk).first()
            documents = AdminCustomerContractDocuments.objects.filter(contract=contract)
            context["contract"] = contract
            context['customer'] = Customer.objects.filter(id=contract.customer_id).first().name
            
            context["documents"] = documents
            return render (request, 'contracts/admin_customer_contract_view.html', context)
        else:
            return redirect('login') 
    except Exception as e:
        context["error_messages"] = str(e)
        return render (request, 'contracts/admin_customer_contract_view.html', context)


@login_required()
def edit_admin_customer_contract(request, pk):
    context = {}
    try:
        contract = get_object_or_404(AdminCustomerContract, id=pk)      
        # Retrieve customers
        customers = Customer.objects.all().values('id', 'name')        
        # Retrieve the documents associated with this contract
        documents = AdminCustomerContractDocuments.objects.filter(contract=contract)        

        context = {
            "contract": contract,
            "customers": customers,
            'selected_customer_id': contract.customer_id,            
            "selected_crop": contract.crop,
            'crop_type': contract.crop_type,
            "contract_amount": contract.contract_amount,
            "amount_unit": contract.amount_unit,
            "contract_start_date": contract.contract_start_date,
            "contract_period": contract.contract_period,
            "status": contract.status,
            "documents": documents,
        }

        if request.method == "POST":
            if request.user.is_superuser or 'SubAdmin' in request.user.get_role() or 'SuperUser' in request.user.get_role() or request.user.is_distributor:
                # Handle updates by admin or superuser
                selected_customer = request.POST.get('selected_customer')
                selected_crop = request.POST.get('crop')
                contract_amount = request.POST.get('contract_amount')
                amount_unit = request.POST.get('amount_unit')
                contract_start_date = request.POST.get('contract_start_date')
                contract_period = request.POST.get('contract_period')
                status = request.POST.get('status')
                
                if selected_customer:                    
                    customer = Customer.objects.filter(id=int(selected_customer)).first()                   

                    if not customer:
                        context["error_messages"] = "Selected customer does not exist."
                        return render(request, 'contracts/edit_admin_customer_contract.html', context)

                    # Update contract details
                    contract.customer_id = customer.id                    
                    contract.crop = selected_crop
                    contract.contract_amount = contract_amount
                    contract.amount_unit = amount_unit
                    contract.contract_start_date = contract_start_date
                    contract.contract_period = contract_period
                    contract.status = status
                    contract.save()

                    delete_document_ids = request.POST.getlist('delete_document_ids[]')
                    print(delete_document_ids)
                    for document_id in delete_document_ids:
                        try:
                            document = AdminCustomerContractDocuments.objects.get(id=document_id)
                            document.delete()  # Delete the document from the database
                        except AdminCustomerContractDocuments.DoesNotExist:
                            pass

                    document_ids =  request.POST.getlist('document_ids')
                    for document_id in document_ids:
                        document_status = f'document_status_{document_id}'
                        if document_status in request.POST:                            
                            document_stat = request.POST.get(document_status)                         
                            
                            document = AdminCustomerContractDocuments.objects.filter(id=document_id).first()
                            document.document_status = document_stat  # Assign the file to the FileField
                            document.save()                                
                            
                    document_names = request.POST.getlist('document_name[]')  
                    if document_names:                     
                        for i, name in enumerate(document_names):
                            # Check if there's a corresponding document ID
                            if i < len(document_ids):
                                document_id = document_ids[i]
                                # Update existing document
                                document = AdminCustomerContractDocuments.objects.filter(id=document_id).first()
                                if document:
                                    document.name = name  # Update the name
                                    document.save()
                            else:
                                # Create new document if the document ID does not exist
                                AdminCustomerContractDocuments.objects.create(contract=contract, name=name)
                return redirect('admin-customer-contract-list')
                        
            elif request.user.is_customer:
                document_ids = request.POST.getlist('document_ids')        
                for document_id in document_ids:
                    file_field_name = f'document_file_{document_id}'
                    
                    if file_field_name in request.FILES:
                        uploaded_file = request.FILES[file_field_name]                       
                        
                        # Handle the uploaded file
                        try:
                            document = AdminCustomerContractDocuments.objects.get(id=document_id)
                            document.document = uploaded_file  # Assign the file to the FileField
                            document.save()
                            
                        except AdminCustomerContractDocuments.DoesNotExist:
                            # Handle the case where the document does not exist
                            pass
                contract.status = "Under Review"
                contract.save()
                return redirect('admin-customer-contract-list')
        return render(request, 'contracts/edit_admin_customer_contract.html', context)
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        context["error_messages"] = str(e)
        return render(request, 'contracts/edit_admin_customer_contract.html', context)
