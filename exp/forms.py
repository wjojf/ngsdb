from django import forms
from django.forms import ModelForm
from django.forms.models import modelformset_factory, BaseModelFormSet

from django.contrib.auth.models import User
from django.contrib.contenttypes.forms import BaseGenericInlineFormSet, generic_inlineformset_factory

from nlib.forms import InlineInput, InlineSelect
from exp.models import Experiment, PrepMethod, Project, ExpPlatform, ModelOrganism, Descriptor, DescriptorMap, DescriptorValue


class UploadForm(forms.Form):
    metadata_file = forms.FileField(label=u'Metadata File to import (.csv)')
    rawdata_file = forms.FileField(label=u'Raw data File to import (.csv)')
    # project = forms.ModelChoiceField(label='Project',
    #         queryset=Project.objects.all())
    # platform = forms.ModelChoiceField(label='Platform',
    #         queryset=ExpPlatform.objects.all())
    # prep_method = forms.ModelChoiceField(label='Preparation method',
    #         queryset=PrepMethod.objects.all())
    # users = forms.ModelMultipleChoiceField(label='Users',
    #         queryset=User.objects.all())


class SearchForm(forms.Form):
    '''
    Search form for museum item list.
    '''
    
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(),
        widget=InlineInput(attrs={
                'css_class': 'col-xs-2',
                'placeholder': 'project ...', 
            }
        ),
        required=False
    )

    platform = forms.ModelChoiceField(
        queryset=ExpPlatform.objects.all(),
        widget=InlineInput(attrs={
                'css_class': 'col-xs-2',
                'placeholder': 'platform ...', 
            }
        ),
        required=False
    )

    organism = forms.ModelChoiceField(
        queryset=ModelOrganism.objects.all(),
        widget=InlineInput(attrs={
                'css_class': 'col-xs-2',
                'placeholder': 'organism ...', 
            }
        ),
        required=False
    )

    qfield = forms.ModelChoiceField(queryset=Descriptor.objects.all(),
        widget=InlineSelect(attrs={
            'css_class': 'col-xs-2',
            }),
        required=False)
    qvalue = forms.CharField(max_length=255, required=False,
        widget=InlineInput(attrs={
            'css_class': 'col-xs-2',
            'placeholder': 'descriptor value...',}))


class UpdateCustomForm(forms.Form):
    '''
    Descriptor name and descriptor value for updating MuseumItem
    custom descriptors through admin actions.
    '''
    name = forms.ModelChoiceField(label=u'Descriptor name', queryset=Descriptor.objects.all())
    value = forms.CharField(label=u'', max_length=255, required=False)


class UpdateCommonForm(forms.Form):
    '''
    Field and value for bulk update Experiment from admin.
    '''
    field = forms.CharField(label=u'Field name', max_length=50)
    value = forms.CharField(label=u'New Value', max_length=255)

    def clean_field(self):
        '''
        Checks that the given field exists in Experiment.
        '''
        field_name = self.cleaned_data['field'].replace(' ', '_')
        model_fields = Experiment._meta.get_all_field_names()
        if field_name in model_fields:
            return field_name
        else:
            raise forms.ValidationError('Unknown common field %s.' % field_name)

    def clean(self):
        '''
        FIXME: Probably need a separate model for users, they are not
        necessarily the same as auth.User
        If the field is Experiment.author, performs lookup in the owners
        table for value and if found, returns its pk, so we can use it
        BulkUpdateView. Ugly, but working.
        '''
        cleaned_data = self.cleaned_data
        field_name = cleaned_data.get('field')
        if field_name == 'author':
            author_name = cleaned_data.get('value')
            try:
                author = User.objects.get(name=author_name)
            except:
                raise forms.ValidationError('Owner with name %s does not exist.' % author_name)

        return cleaned_data

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


class DescriptorMapInline(ModelForm):
    desc_value = PkToValueField(model=DescriptorValue, widget=forms.TextInput(attrs={'size':40,}))
    desc_name = PkToValueField(model=Descriptor, widget=forms.TextInput(attrs={'size':30,}))

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
        lookup_params['descriptor'], created = Descriptor.objects.get_or_create(name=name)
        # This is probably not good. But it works.
        # It would be more appropriate to create new FieldValue in manager.
        self.cleaned_data['desc_name'] = lookup_params['descriptor']
        val, created = DescriptorValue.objects.get_or_create(**lookup_params)
        self.cleaned_data['desc_value'] = val
        return self.cleaned_data

class BaseDescriptorFormSet(BaseGenericInlineFormSet):

    def __init__(self, data=None, files=None, instance=None, save_as_new=None,
             prefix=None, queryset=None, initial=None):
        # Avoid a circular import.
        from django.contrib.contenttypes.models import ContentType
        opts = self.model._meta
        self.instance = instance
        self.can_delete = False
        self.rel_name = '-'.join((
                opts.app_label, opts.object_name.lower(),
                self.ct_field.name, self.ct_fk_field.name,
                ))
        if self.instance is None or self.instance.pk is None:
            qs = self.model._default_manager.none()
        else:
            if queryset is None:
                queryset = self.model._default_manager
            qs = queryset.filter(**{
                    self.ct_field.name: ContentType.objects.get_for_model(self.instance),
                    self.ct_fk_field.name: self.instance.pk,
                    })
        super(BaseGenericInlineFormSet, self).__init__(
                queryset=qs, data=data, files=files,
                prefix=prefix, initial=initial
                )

DescriptorFormSet = generic_inlineformset_factory(
                                        DescriptorMap,
                                        form=DescriptorMapInline,
                                        formset=BaseDescriptorFormSet
                                        )

class BaseUploadedFormSet(BaseModelFormSet):

    def add_fields(self, form, index):
        super(BaseUploadedFormSet, self).add_fields(form, index)
        try:
            instance = self.get_queryset()[index]
            pk_value = instance.pk
        except IndexError:
            instance = None
            pk_value = hash(form.prefix)
        # Starting django 1.3 we can't pass {} to formset
        # because it will raise ValidationError. Pass None instead.
        if self.initial_extra:
            initial = self.initial_extra[index]['inlines']
        else:
            initial = None
        form.inlines = DescriptorFormSet(data=self.data or None,
                                        instance=instance,
                                        initial=initial, 
                                        prefix='DESC_%s' % pk_value)

    def is_valid(self):
        result = super(BaseUploadedFormSet, self).is_valid()
        for form in self.forms:
            if hasattr(form, 'inlines'):
                for inline in form.inlines:
                    result = result and inline.is_valid()
        return result

    def save_new(self, form, commit=True):
        instance = super(BaseUploadedFormSet, self).save_new(form, commit=commit)
        form.inlines.instance = instance
        form.inlines.save()
        return instance

    def save_all(self, commit=True):
        objects = self.save(commit=False)
        if commit:
            for o in objects:
                o.save()

        if not commit:
            self.save_m2m()

        for form in set(self.initial_forms + self.saved_forms):
            for inline in form.inlines:
                inline.save(commit=commit)


class ModelOrganismForm(ModelForm):
    
    class Meta:
        fields = '__all__'
        model = ModelOrganism

class ExpPlatformForm(ModelForm):

    class Meta:
        fields = '__all__'
        model = ExpPlatform

