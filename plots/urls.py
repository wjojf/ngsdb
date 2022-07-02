from django.urls import path
from plots import views as plt_views

urlpatterns = [
    path('', plt_views.PlotsNavgitaionView.as_view(), name='plots-navigation'),
    path('test-volcano/', plt_views.VolcanoPlotView.as_view(), name='test-volcano'),
    path('test-pcaplot', plt_views.PCAPlotView.as_view(), name='test-pcaplot'),
]
