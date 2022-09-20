from plots import utils as plots_utils
from django.views.generic import DetailView
from exp.models import ExperimentFile


class VolcanoPlotView(DetailView):
    template_name = 'plots/plot.html'
    pk_url_kwarg = 'file_id'
    model = ExperimentFile
    context_object_name = 'exp'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['graph'] = plots_utils.get_volcano_plot_for_obj(self.get_object())
        except Exception:
            pass 
        
        return context


class PCAPlotView(DetailView):
    template_name = 'plots/plot.html'
    pk_url_kwarg = 'file_id'
    model = ExperimentFile
    context_object_name = 'exp'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_pca'] = True

        return context
