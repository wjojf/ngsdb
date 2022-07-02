import os
from django.views.generic import TemplateView
from ngsdb.settings import STATIC_URL

# Visual imports
import pandas as pd
import dash_bio
import plotly.express as px
from sklearn.decomposition import PCA


class PlotsNavgitaionView(TemplateView):
    template_name = 'plots/plots.html'


class PlotView(TemplateView):
    template_name = 'plots/plot.html'


class VolcanoPlotView(PlotView):

    def get_context_data(self, **kwargs):
        context = super(VolcanoPlotView, self).get_context_data(**kwargs)        
        df  = pd.read_csv(os.path.join(STATIC_URL, 'csv/volcano_data1.csv'))
        
        figure = dash_bio.VolcanoPlot(
            dataframe=df,
            point_size=10,
            effect_size_line_width=4,
            genomewideline_width=2
        )
        
        context['graph'] = figure.to_html()
        return context
    

class PCAPlotView(PlotView):
    
    def get_context_data(self, **kwargs):
        context = super(PCAPlotView, self).get_context_data(**kwargs)

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

