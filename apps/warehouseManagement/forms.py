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
        fields = ['name', 'location', 'latitude', 'longitude','credit_terms', 'is_tax_payable', 'tax_percentage']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'cols': 30
            }),
            'latitude': forms.TextInput(attrs={'class': 'form-control'}),
            'longitude': forms.TextInput(attrs={'class': 'form-control'}), 
            'credit_terms': forms.Select(attrs={'class': 'form-control'}),
            'is_tax_payable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'tax_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),           
        }

    def clean(self):
        cleaned_data = super().clean()
        is_tax_payable = cleaned_data.get("is_tax_payable")
        tax_percentage = cleaned_data.get("tax_percentage")

        # If tax is payable, tax percentage must be provided
        if is_tax_payable and not tax_percentage:
            self.add_error('tax_percentage', "Tax percentage is required when tax is payable.")

        return cleaned_data
