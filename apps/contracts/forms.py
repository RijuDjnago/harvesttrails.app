from django import forms
from django.forms.widgets import NumberInput
from django.forms.widgets import ChoiceWidget

from . import models

class ContractCreateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(ContractCreateForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        # self.fields['name'].required = True
        # self.fields['contract'].required = True
        self.fields['name'].required = True
        self.fields['envelope_id'].required = True

    class Meta:
        model = models.Contracts
        fields = ("name", "envelope_id")
        labels = {
            "name": "Contract Name",
            "envelope_id": "Envelope Id"
        }
        widgets = {

        }


class SignedContractsCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super(SignedContractsCreateForm, self).__init__(*args, **kwargs)
        # there's a `fields` property now
        # self.fields['name'].required = True
        self.fields['signature'].required = True


    class Meta:
        model = models.SignedContracts
        fields = ("signature", )

        widgets = {

        }

