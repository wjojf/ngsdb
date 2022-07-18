import os 
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, TemplateView, FormView
from exp.models import Experiment
from exp.forms import DescriptorMapInline
from plots.generate_plots import generate_volcanoPlot
from ngsdb.settings import STATIC_URL


# Create your views here.
class HomeView(TemplateView):
    template_name = 'exp/exp-home.html'


class ExperimentsView(ListView):
    model = Experiment
    context_object_name = 'experiments'
    template_name = 'exp/allExperiments.html'
    
    
class ExperimentView(DetailView):
    model = Experiment
    pk_url_kwarg = 'exp_id'
    context_object_name = 'exp'
    template_name = 'exp/singleExperiment.html'    


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data_filepath = os.path.join(STATIC_URL, self.get_object().data_filepath)
        context['volcanoPlot_div'] = generate_volcanoPlot(data_filepath)
        
        return context


class DescriptorMapFormView(FormView):
    template_name = 'exp/createDescriptor.html'
    form_class = DescriptorMapInline
    success_url = 'exp-all'

    
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        return super().form_valid(form)

    def get(self, request):
        return render(request, self.template_name, self.get_context_data(form=self.form_class))

    def post(self, request):
        #print(request.POST)
        form = self.form_class(request.POST)
        
        if self.form_valid(form):
            try:
                form.save()
                return redirect(self.success_url)
            except Exception as e: 
                return HttpResponse(e)
        
        return HttpResponse('An Error ocurred:(')

