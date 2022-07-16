import os
from django.views.generic import TemplateView, DetailView
from matplotlib.pyplot import title
from ngsdb.settings import STATIC_URL
from exp.models import Experiment

# Visual imports
import numpy as np
import pandas as pd
import dash_bio
import plotly.express as px
from sklearn.decomposition import PCA
from .generate_plots import generate_volcanoPlot


class PlotsNavgitaionView(TemplateView):
    template_name = 'plots/test-plots.html'


class PlotView(TemplateView):
    template_name = 'plots/plot.html'


class TestVolcanoPlotView(PlotView):

    def get_context_data(self, **kwargs):
        context = super(TestVolcanoPlotView, self).get_context_data(**kwargs)        
        df = pd.read_csv('https://git.io/volcano_data1.csv')
        figure = dash_bio.VolcanoPlot(
            dataframe=df,
            effect_size_line_width=4,
            genomewideline_width=2
        )
        
        context['graph'] = figure.to_html()
        return context
    

class TestPCAPlotView(PlotView):
    
    def get_context_data(self, **kwargs):
        context = super(TestPCAPlotView, self).get_context_data(**kwargs)

        df = px.data.iris()
        features = ["sepal_width", "sepal_length", "petal_width", "petal_length"]

        pca = PCA()
        components = pca.fit_transform(df[features])
        labels = {
            str(i): f"PC {i+1} ({var:.1f}%)"
            for i, var in enumerate(pca.explained_variance_ratio_ * 100)
        }       

        fig = px.scatter_matrix(
            components,
            labels=labels,
            dimensions=range(4),
            color=df["species"]
        )

        context['graph'] = fig.to_html()
        return context    


class VolcanoPlotView(DetailView):
    pk_url_kwarg = 'exp_id'
    model = Experiment
    context_object_name = 'exp'
    template_name = 'plots/plot.html'
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        data_filepath = os.path.join(STATIC_URL, self.get_object().data_filepath)
        volcano_div = generate_volcanoPlot(data_filepath)
        
        context['graph'] = volcano_div
        return context

