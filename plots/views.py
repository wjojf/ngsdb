from django.views.generic import DetailView
from ngsdb.settings import MEDIA_ROOT
from exp.models import Experiment
import plotly.express as px
import numpy as np
import pandas as pd
import dash_bio
import os 


class VolcanoPlotView(DetailView):
    template_name = 'plots/plot.html'
    pk_url_kwarg = 'exp_id'
    model = Experiment
    context_object_name = 'exp'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            data_filepath = str(self.get_object().data_filepath)
            df = pd.read_csv(os.path.join(MEDIA_ROOT, data_filepath)).dropna()

            figure = dash_bio.VolcanoPlot(
                dataframe=df,
                effect_size='log2FoldChange',
                p='pvalue',
                snp=None,
                gene='Gene',
                title=f'{self.get_object()}'
            )

            context['graph'] = figure.to_html()
        
        except Exception:
            pass 
        
        return context


class PCAPlotView(DetailView):
    template_name = 'plots/plot.html'
    pk_url_kwarg = 'exp_id'
    model = Experiment
    context_object_name = 'exp'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_pca'] = True

        return context
