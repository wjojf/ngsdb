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


def update_experiments(request):
    ''''''