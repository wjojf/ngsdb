from django import forms
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet
from exp.models import ModelOrganism, Descriptor, DescriptorMap, DescriptorValue


class PkToValueField(forms.CharField):
    '''
    Custom field used to render related objects in a textinput instead of select widget.
    Given a model will try to fetch an object with the given pk and display it instead of pk.
    Failing that, will simply display pk.
    '''

    def __init__(self, model=None, *args, **kwargs):
        self.model = model
        super(PkToValueField, self).__init__(*args, **kwargs)

    def prepare_value(self, value):
        if self.model == None:
            return value
        try:
            return self.model._default_manager.get(pk=int(value))
        except:
            return value


class ModelOrganismForm(ModelForm):
    
    class Meta:
        fields = '__all__'
        model = ModelOrganism


class DescriptorMapInline(ModelForm):
    desc_value = PkToValueField(
        model=DescriptorValue, widget=forms.TextInput(attrs={'size': 40, }))
    desc_name = PkToValueField(
        model=Descriptor, widget=forms.TextInput(attrs={'size': 30, }))

    class Meta:
        fields = '__all__'
        model = DescriptorMap

    def clean(self):
        '''
        Checks if the DescriptorValue of appropriate Descriptor exists
        in database. If it doesn't, creates a new one.
        '''
        lookup_params = {}
        name = self.cleaned_data['desc_name'].strip().lower()
        value = self.cleaned_data['desc_value'].strip().lower()
        lookup_params['value'] = value
        lookup_params['descriptor'], created = Descriptor.objects.get_or_create(
            name=name)
        # This is probably not good. But it works.
        # It would be more appropriate to create new FieldValue in manager.
        self.cleaned_data['desc_name'] = lookup_params['descriptor']
        val, created = DescriptorValue.objects.get_or_create(**lookup_params)
        self.cleaned_data['desc_value'] = val
        return self.cleaned_data
