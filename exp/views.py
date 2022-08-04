from doctest import Example
from re import template
from telnetlib import EXOPL
from attr import fields
from django.shortcuts import redirect
from django.views.generic import list, edit
from django.views.generic.base import TemplateResponseMixin
from django.urls import reverse, reverse_lazy
from django.utils.encoding import smart_str


from django.forms.models import modelform_factory, modelformset_factory
from django.forms.formsets import formset_factory
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.forms import generic_inlineformset_factory

from nlib.views import FilteredModelView
from nlib.utils import build_tabs_dict

from exp.models import Experiment, Project, PrepMethod, ExpPlatform, Descriptor, DescriptorMap
from exp.forms import DescriptorMapInline, SearchForm, UploadForm, UpdateCommonForm, UpdateCustomForm, BaseUploadedFormSet
from exp.filters import ExperimentFilter
import exp.parse_meta as exp_meta


EXP_TAB = {
    'Experiments': 'exp_home_view',
    'Upload': 'exp_upload_view',
}


class UploadCSVView(edit.BaseFormView, TemplateResponseMixin):
    '''
    TODO:

    Handles uploading of a .csv file.
    First renders the template with UploadForm. When the form is POSTed
    uploads the file, parses its contents and stores it in `self.uploaded`.

    Then renders the formset using the data stored in `self.uploaded`
    as `initial`.

    Each form of the formset represents a record parsed from the .csv file.
    Custom fields are handled as GenericInlineFormsets associated with
    every form in the original formset.

    This formset(s) is then POSTed to another view, `ImportCSVView` that
    handles the actual saving of the imported itmes to the database.
    '''

    template_name = 'exp/upload.html'
    import_template_name = 'exp/import.html'
    form_class = UploadForm


    def get_context_data(self, **kwargs):
        context = super(UploadCSVView, self).get_context_data(**kwargs)
        context['tabs'] = build_tabs_dict(self.request, EXP_TAB)
        
        if self.request.method == 'GET':
            context['submit_line'] = (
                {'name': 'clear', 'class': 'btn-default',},
                {'name': 'upload', 'class': 'btn-success', },
                )

        return context


    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        
        exp_obj = Experiment.objects.create(
            metadata_filepath=request.FILES['metadata_file'],
            data_filepath=request.FILES['rawdata_file'],
            project=Project.objects.filter(pk=request.POST['project'])[0],
            platform=ExpPlatform.objects.filter(pk=request.POST['platform'])[0],
            prep_method=PrepMethod.objects.filter(pk=request.POST['prep_method'])[0],
        )
        exp_obj.users.set(
            User.objects.in_bulk([
                request.POST['users']
            ])
        )   # Any other options don't work
        
        obj_id = exp_obj.id
        content_type = ContentType.objects.get_for_model(exp_obj)
        files = request.FILES
        metadata_content = files['metadata_file'].open()

        exp_meta._parse_meta(metadata_content, obj_id, content_type)
        
        return redirect('exp_home_view')
   

class ImportCSVView(edit.FormView):
    '''
    Handles saving MuseumItems uploaded in a .csv file to database.
    '''
    template_name  = 'exp/import.html'


    def get(self, request, *args, **kwargs):
        formset_class = modelformset_factory(Experiment, formset=BaseUploadedFormSet, fields='__all__')
        formset = formset_class(data=request.POST, queryset=Experiment.objects.none())
        context = self.get_context_data(**kwargs)
        context['formset'] = formset
        context['tabs'] = build_tabs_dict(request, EXP_TAB)
        return self.render_to_response(context)


    def post(self, request, *args, **kwargs):
        formset_class = modelformset_factory(Experiment,formset=BaseUploadedFormSet, fields='__all__')
        formset = formset_class(data=request.POST, queryset=Experiment.objects.none())
        if formset.is_valid():
            self.objects = formset.save()
            return HttpResponseRedirect(reverse_lazy('exp_home_view'))
        else:
            return self.get(request, *args, **kwargs) 

##########################################################################

class BaseActionView(list.ListView, edit.BaseFormView):
    '''
    Common functionality to Admin action views updating common or
    custom fields on multiple MuseumItem instances.
    '''

    model = Experiment
    template_name = 'exp/bulk.html'
    idlist = []

    def get_success_url(self):
        url = reverse('admin:exp_experiment_changelist')
        return url

    def get(self, request, *args, **kwargs):
        self.idlist = request.GET.get('ids').split(',')
        self.object_list = self.get_queryset()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(object_list=self.object_list, form=form)
        return self.render_to_response(context)

    def get_queryset(self):
        self.queryset = Experiment.objects.filter(pk__in=self.idlist) or None
        return self.queryset

    def form_invalid(self, form):
        return self.get(self.request, form=form)


##########################################################################

class UpdateCommonView(BaseActionView):

    form_class = UpdateCommonForm

    def form_valid(self, form):
        if '_update' in self.request.POST:
            # Update self.queryset
            self.idlist = self.request.POST.getlist('selected')
            self.get_queryset()
            field = form.cleaned_data['field']
            new_value = form.cleaned_data['value']
            if field == 'author':
                new_value = Owner.objects.get(name=new_value)
            kwargs = { field: new_value, }
            self.queryset.update(**kwargs)
        return HttpResponseRedirect(self.get_success_url())

##########################################################################

class UpdateCustomView(BaseActionView):
    '''
    FIXME: This needs to be refactored to handle conditions and organism fields.

    Overrides get_form() to return formset of UpdateCustomForms
    form in POST handling therefore refers actually to this formset.
    '''

    form_class = UpdateCustomForm

    def get_form(self, form_class):
        formset_class = formset_factory(form_class, extra=3, max_num=3)
        return formset_class(**self.get_form_kwargs())

    def form_valid(self, form):
        if '_update' in self.request.POST:
            # Iterate through the formset and update fields
            self.idlist = self.request.POST.getlist('selected')
            self.get_queryset()
            fields = {}
            for the_form in form.forms:
                if the_form.cleaned_data:
                    field_name = str(the_form.cleaned_data['name'])
                    field_value = the_form.cleaned_data['value']
                    fields.update( {field_name: field_value,} )
            for item in self.queryset:
                DescriptorMap.objects.update_for_object(item, **fields)
        return HttpResponseRedirect(self.get_success_url())

##########################################################################

class DescriptorListView(list.ListView):
    model = Descriptor
    template_name = 'exp/descriptors.html'


    def get_context_data(self, **kwargs):
        context = super(DescriptorListView, self).get_context_data(**kwargs)
        context['tabs'] = build_tabs_dict(self.request, EXP_TAB)
        
        return context

##########################################################################

class HomeView(list.ListView):
    
    model = Experiment
    template_name = 'exp/home.html'
    filterset_class = ExperimentFilter
    paginate_by = 50
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['filter_obj'] = self.filterset_class(self.request.GET, queryset=self.model.objects.all())
        context['tabs'] = build_tabs_dict(self.request, EXP_TAB)
        context['submit_line'] = (
                {'tag': 'a', 'name': '+ Add item', 'href': reverse_lazy('museum_add_item_view'),  'class': 'btn-info',},
                {'tag': 'a', 'name': '+ Add descriptor', 'href': reverse_lazy('museum_add_descriptor_view'),  'class': 'btn-info',},
            )
        
        return context
    
    
    def get_queryset(self):
        if '_clear' not in self.request.GET:
            return self.filterset_class(self.request.GET, queryset=self.model.objects.all()).qs
            
        return super().get_queryset()        


class GenericInlineFormsetMixin(object):
    '''
    A mixin that provides a way to show and handle generic inline formset
    in a request.
    Done after FormMixin object.
    '''
    instance = None
    inline_form_class = None
    inline_model_class = None

    def get_instance(self):
        '''
        Returns the initial data to use for the formset on the view.
        Probably should not return None but raise an exception instead.
        '''
        if self.object:
            self.instance = self.object
        else:
            self.instance = self.model()
        return self.instance

    def get_inline_form_class(self):
        '''
        Returns ModelForm to be used in inlines.
        '''
        if self.inline_form_class:
            return self.inline_form_class
        else:
            if self.inline_model_class is not None:
                model = self.inline_model_class
        return modelform_factory(model)

    def get_inline_model_class(self):
        '''
        Returns the inline model class.
        '''
        return self.inline_model_class

    def get_formset_class(self):
        '''
        Returns a Formset class to be used in the view.
        '''
        kwargs = {
                'form': self.get_inline_form_class(),
                #'ct_field': 'content_type',
                #'fk_field': 'object_id',
                #'fields': '__all__',
                #'exclude': None,
                'extra': 3,
                #'can_order': False,
                #'can_delete': True,
                }
        return generic_inlineformset_factory(self.get_inline_model_class(), **kwargs)

    def get_formset(self, formset_class):
        '''
        Returns a formset instance to be used in the view.
        '''
        return formset_class(**self.get_formset_kwargs())

    def get_formset_kwargs(self):
        '''
        Returns the keyword arguments for instanciating the formset.
        '''
        kwargs = {'instance': self.get_instance(),}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                    'data': self.request.POST,
                    'files': self.request.FILES,
            })
        return kwargs

class AddExperimentView(edit.CreateView, GenericInlineFormsetMixin):

    model = Experiment
    inline_form_class = DescriptorMapInline
    inline_model_class = DescriptorMap
    fields = '__all__'
    template_name = 'exp/crud.html'

    def form_valid(self, form, formset):
        '''
        Handles both form AND formset.
        '''
        self.object.save()
        form.save_m2m()
        self.inlines = formset.save()
        return  HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        '''
        Replaces form_invalid to handle both form AND formset.
        '''
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_context_data(self, **kwargs):
        context = kwargs
        context['model'] = self.model._meta.verbose_name
        context['tabs'] = build_tabs_dict(self.request, EXP_TAB)
        context['submit_line'] = (
                {'name': 'back', 'class': 'btn-default',},
                {'name': 'save', 'class': 'btn-success', },
                )
        return context

    def get(self, request, *args, **kwargs):
        self.object = None
        self.inlines = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class) # Need to pass instance kwarg!
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def post(self, request, *args, **kwargs):
        self.object = None
        self.inlines = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            self.object = form.save(commit=False)
        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class)
        if formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

class UpdateExperimentView(edit.UpdateView, GenericInlineFormsetMixin):

    model = Experiment
    inline_form_class = DescriptorMapInline
    inline_model_class = DescriptorMap
    template_name = 'exp/crud.html'

    def form_valid(self, form, formset):
        '''
        Replaces form_valid to handle both form AND formset.
        '''
        form.save()
        formset.save()
        return  HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, formset):
        '''
        Replaces form_invalid to handle both form AND formset.
        '''
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def get_context_data(self, **kwargs):
        context = kwargs
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context['model'] = self.model._meta.verbose_name
        context['tabs'] = build_tabs_dict(self.request, EXP_TAB)
        return context

    def get_success_url(self):
        return reverse_lazy('exp_home_view')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # self.inlines = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.inlines = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset_class = self.get_formset_class()
        formset = self.get_formset(formset_class)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)


class AddFieldTaxonomyView(edit.CreateView):

    model = Descriptor
    fields = '__all__'
    template_name = 'exp/crud.html'

    def get_context_data(self, **kwargs):
        context = kwargs
        context['model'] = 'descriptor'
        context['tabs'] = build_tabs_dict(self.request, EXP_TAB)
        context['submit_line'] = (
                {'name': 'back', 'class': 'btn-default',},
                {'name': 'save', 'class': 'btn-success', },
                )
        return context

    def get_success_url(self):
        return reverse_lazy('exp_home_view')
