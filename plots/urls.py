from django.urls import path
from plots import views as plt_views


urlpatterns = [
    path('volcano/<int:exp_id>', plt_views.VolcanoPlotView.as_view(), name='volcano-plot'),
    path('pca/<int:exp_id>', plt_views.PCAPlotView.as_view(), name='pca-plot'),
]
