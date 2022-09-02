from django.shortcuts import redirect
from django.views.generic import list, edit
from django.views.generic.base import TemplateResponseMixin
from django.urls import reverse, reverse_lazy
from django.forms.models import modelform_factory
from django.http import HttpRequest

from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.forms import generic_inlineformset_factory

from nlib.utils import build_tabs_dict
from exp.models import Experiment, ModelOrganism, Project, PrepMethod, ExpPlatform, Sample
from exp.forms import UploadForm, ImportForm
from exp.filters import ExperimentFilter
import exp.parse_meta as exp_meta


EXP_TAB = {
    'Experiments': 'exp_home_view',
    'Create': 'exp_upload_view',
}


def logout_user(request):
    logout(request)
    return redirect('exp_home_view')


class MyLoginView(LoginView):
    template_name = 'login.html'


class CreateExperimentView(edit.BaseFormView, TemplateResponseMixin):
 
    template_name = 'exp/upload.html'
    form_class = UploadForm


    def get_context_data(self, **kwargs):
        context = super(CreateExperimentView, self).get_context_data(**kwargs)
        context['tabs'] = build_tabs_dict(self.request, EXP_TAB)
        
        if self.request.method == 'GET':
            context['submit_line'] = (
                {'name': 'clear', 'class': 'btn-default',},
                {'name': 'upload', 'class': 'btn-success', },
                )

        return context


    def post(self, request: HttpRequest, *args, **kwargs):
        
        exp_obj = Experiment.objects.create(
            metadata_filepath=request.FILES['metadata_file'],
            data_filepath=request.FILES['rawdata_file'],
            project=Project.objects.filter(pk=request.POST['project'])[0],
            organism=ModelOrganism.objects.filter(pk=request.POST['organism'])[0],
            platform=ExpPlatform.objects.filter(pk=request.POST['platform'])[0],
            prep_method=PrepMethod.objects.filter(pk=request.POST['prep_method'])[0],
        )
        exp_obj.users.set(
            User.objects.in_bulk([
                request.POST['users']
            ])
        )   # Any other options don't work

        files = request.FILES
        metadata_content = files['metadata_file'].open()

        exp_meta._parse_meta(metadata_content, exp_obj)
        
        return redirect('exp_home_view')
   
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

##########################################################################


class ImportExperimentsView(edit.BaseFormView, TemplateResponseMixin):
    '''
    Uploading multiple experiments. Idea:
        - Get GoogleDrive folder url / local folder (How?)
        - Find folders with patter 'DD_MM_YYYY_RNA-Seq' which haven't been seen yet. 
            (How can we know if the folder has already been checked?)
        
        for folder in found_folders:
            - Find MetaData file by pattern
                - Find RawData file pattern
                    - Create experiment obj (call UploadCSVView.post() from here?)

    ''' 
    template_name = 'exp/import.html'
    form_class = ImportForm

    def get_context_data(self, **kwargs):
        context = super(ImportExperimentsView, self).get_context_data(**kwargs)
        context['tabs'] = build_tabs_dict(self.request, EXP_TAB)

        if self.request.method == 'GET':
            context['submit_line'] = (
                {'name': 'clear', 'class': 'btn-default', },
                {'name': 'upload', 'class': 'btn-success', },
            )

        return context
    
    def post(self, request, *args, **kwargs):
        with open('debug.txt', 'w') as f:
            f.write(str(request.FILES))
        
        return super().post(request, *args, **kwargs)
    
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
            sample_qs = self.filterset_class(self.request.GET, queryset=Sample.objects.all()).qs
            
            exp_qs = sample_qs.values_list('experiment').distinct('experiment')
            return Experiment.objects.filter(pk__in=exp_qs)
             
        return super().get_queryset()        



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