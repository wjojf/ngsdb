from django import forms
from django.forms import ModelForm
from django.forms.models import modelformset_factory, BaseModelFormSet
from django.contrib.auth.models import User
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet, generic_inlineformset_factory
from exp.models import Experiment, PrepMethod, Project, ExpPlatform, ModelOrganism, Descriptor, DescriptorMap


class UploadForm(forms.Form):

    metadata_file = forms.FileField(label=u'Metadata File to import (.csv)')
    rawdata_file = forms.FileField(label=u'Raw data File to import (.csv)')
    
    project = forms.ModelChoiceField(label='Project',
            queryset=Project.objects.all())
    
    organism = forms.ModelChoiceField(label=u'Model Organism', queryset=ModelOrganism.objects.all())
    
    
    platform = forms.ModelChoiceField(label='Platform',
            queryset=ExpPlatform.objects.all())
    
    prep_method = forms.ModelChoiceField(label='Preparation method',
            queryset=PrepMethod.objects.all())
    
    users = forms.ModelMultipleChoiceField(label='Users',
            queryset=User.objects.all())


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
        except Exception:
            return value

class DescriptorMapInlineForm(ModelForm):

    class Meta:
        model = DescriptorMap
        fields = '__all__'
        list_display = ('desc_name_value',)
   

class ModelOrganismForm(ModelForm):
    
    class Meta:
        fields = '__all__'
        model = ModelOrganism

class ExpPlatformForm(ModelForm):

    class Meta:
        fields = '__all__'
        model = ExpPlatform


