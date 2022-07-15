from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.views.generic import ListView, DetailView, TemplateView, FormView
from exp.models import Experiment
from exp.forms import DescriptorMapInline


# Create your views here.
class HomeView(TemplateView):
    template_name = 'start.html'


class ExperimentsView(ListView):
    model = Experiment
    context_object_name = 'experiments'
    template_name = 'exp/home.html'
    
    
class ExperimentView(DetailView):
    model = Experiment
    pk_url_kwarg = 'exp_id'
    context_object_name = 'exp'
    template_name = 'exp/singleExperiment.html'    


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

