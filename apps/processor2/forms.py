from django import forms
from apps.processor2.models import *
from django.utils.safestring import mark_safe


class DisabledOptionsRadioSelect(forms.RadioSelect):
    def __init__(self, disabled_choices=(), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.disabled_choices = [str(dc) for dc in disabled_choices]

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex=subindex, attrs=attrs)
        if str(value) in self.disabled_choices:
            option['attrs']['disabled'] = 'disabled'
        return option


class ProcessorForm2(forms.ModelForm):
    main_number = forms.IntegerField()
    main_fax = forms.IntegerField(required=False)
    main_email = forms.CharField()

    processor_type = forms.ModelChoiceField(
        queryset=ProcessorType.objects.all(),
        required=True,
        widget=forms.RadioSelect  # temporary, will replace in __init__
    )

    def __init__(self, *args, processor_type_name=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['fein'].required = True
        self.fields['entity_name'].required = True
        self.fields['billing_address'].required = True

        if processor_type_name:
            try:
                selected_type = ProcessorType.objects.get(type_name=processor_type_name)
                self.fields['processor_type'].initial = selected_type.id

                # all ids except the selected one should be disabled
                disabled_ids = ProcessorType.objects.exclude(id=selected_type.id).values_list("id", flat=True)

                # Replace widget and reattach choices
                self.fields['processor_type'].widget = DisabledOptionsRadioSelect(
                    disabled_choices=disabled_ids,
                    choices=self.fields['processor_type'].choices
                )

            except ProcessorType.DoesNotExist:
                pass

    class Meta:
        model = Processor2
        fields = [
            'fein', 'entity_name', 'billing_address', 'shipping_address',
            'main_number', 'main_fax', 'main_email', 'website', 'processor_type'
        ]
        widgets = {
            'billing_address': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_address': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.TextInput(attrs={'class': 'form-control'}),
        }



class Processor2LocationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(Processor2LocationForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['upload_type'].required = True
        self.fields['processor'].required = True
    class Meta:
        model = Processor2Location
        fields = '__all__'
        widgets = {
            'upload_type': forms.Select(attrs={'class': 'form-select',}),
        }
