from .models import *
from django import forms

class DistributorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DistributorForm, self).__init__(*args, **kwargs)
        self.fields['entity_name'].required = True
        self.fields['location'].required = True

    class Meta:
        model = Distributor
        fields = [
            'entity_name', 'warehouse', 'location', 'latitude', 'longitude'
        ]
        widgets = {
            'entity_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,   # Set the number of rows
                'cols': 30   # Set the number of columns
            }),
            'latitude': forms.TextInput(attrs={'class': 'form-control'}),
            'longitude': forms.TextInput(attrs={'class': 'form-control'}),
            'warehouse': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class WarehouseForm(forms.ModelForm):
    distributor = forms.ModelMultipleChoiceField(
        queryset=Distributor.objects.all(),
        required=False,  # Make this field optional
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),  # SelectMultiple for multiple selection
        label="Select Distributor"
    )

    def __init__(self, *args, **kwargs):
        super(WarehouseForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['location'].required = True

        if self.instance.pk:
            self.fields['distributor'].initial = self.instance.distributor_set.all()

    class Meta:
        model = Warehouse
        fields = ['name', 'location', 'latitude', 'longitude', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'cols': 30
            }),
            'latitude': forms.TextInput(attrs={'class': 'form-control'}),
            'longitude': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
        }

        
class CustomerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CustomerForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['location'].required = True

    class Meta:
        model = Customer
        fields = ['name', 'location', 'latitude', 'longitude', 'credit_limit']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,   # Set the number of rows
                'cols': 30   # Set the number of columns
            }),
            'latitude': forms.TextInput(attrs={'class': 'form-control'}),
            'longitude': forms.TextInput(attrs={'class': 'form-control'}),
            'credit_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            
        }
