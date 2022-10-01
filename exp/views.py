from django.views.generic.base import TemplateResponseMixin
from django.views.generic import list, edit, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import HttpRequest
from django.urls import reverse, reverse_lazy

from exp.models import Experiment, ModelOrganism, Project, PrepMethod, ExpPlatform, Sample, ExperimentFile
from exp.file_handlers import ExperimentFileHandler, FileType, NextSeqFileHandler
from exp.utils import DEFAULT_DIRECTORY_OBJ
from exp.utils import refresh_experiments
from exp.filters import ExperimentFilter
from exp.forms import UploadForm

from nlib.utils import build_tabs_dict


EXP_TAB = {
    'Experiments': 'exp_home_view',
    'Create': 'exp_upload_view',
}


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
            exp_directory=DEFAULT_DIRECTORY_OBJ,
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

        metadata_file = files['metadata_file']
        NextSeqFileHandler.create_from_file_instance(metadata_file, exp_obj)

        rawdata_file = files['rawdata_file']
        ExperimentFileHandler.create_from_file_instance(rawdata_file, exp_obj, FileType.DESEQ.value)

        return redirect('exp_home_view')
   
##########################################################################

class DeleteExperimentView(DeleteView):
    model = Experiment
    pk_url_kwarg = 'exp_id'
    template_name = 'delete.html'
    success_url = reverse_lazy('exp_home_view')

##########################################################################


class HomeView(list.ListView):
    
    model = Experiment
    template_name = 'exp/home.html'
    filterset_class = ExperimentFilter
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['filter_obj'] = self.filterset_class(self.request.GET, queryset=self.model.objects.all())
        context['tabs'] = build_tabs_dict(self.request, EXP_TAB)
        
        return context
    
    
    def get_queryset(self):
        if '_clear' not in self.request.GET:
            sample_qs = self.filterset_class(self.request.GET, queryset=Sample.objects.all()).qs
            
            exp_qs = sample_qs.values_list('experiment').distinct('experiment')
            return Experiment.objects.filter(pk__in=exp_qs)
             
        return super().get_queryset()        


def update_experiments(request):
    refresh_experiments()
    return redirect('exp_home_view')


class EditExperimentView(UpdateView):
    model = Experiment
    pk_url_kwarg = 'exp_id'
    fields = ['project', 'platform', 'users', 'organism', 'prep_method']
    template_name = 'exp/upload.html'
    
    
    def get_success_url(self):
        return reverse('exp_home_view')
   
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['submit_line'] = (
                {'name': 'clear', 'class': 'btn-default', },
                {'name': 'update', 'class': 'btn-success', },
            )
        context['edit_page'] = True
        return context

    
    