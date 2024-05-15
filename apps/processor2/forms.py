from django import forms
from . import models


class ProcessorForm2(forms.ModelForm):
    main_number = forms.IntegerField()
    main_fax=forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super(ProcessorForm2, self).__init__(*args, **kwargs)
        self.fields['fein'].required = True
        self.fields['entity_name'].required = True
        self.fields['billing_address'].required = True

    class Meta:
        model = models.Processor2

        fields = [
            'fein', 'entity_name', 'billing_address', 'shipping_address', 'main_number', 'main_fax',
            'website'
        ]
        widgets = {
            'billing_address': forms.TextInput(attrs={'class': 'form-control',}),
            'shipping_address': forms.TextInput(attrs={'class': 'form-control',}),
            'website': forms.TextInput(attrs={'class': 'form-control',}),
            
        }

