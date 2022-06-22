from django.urls import path
from exp import views 

urlpatterns = [
    path('', views.home, name='exp-home'),
    path('all', views.allExperiments, name='exp-all'),
    path('<int:pk>', views.singeExperiment, name='exp-single'),
    
]