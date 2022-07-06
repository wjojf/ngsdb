from django.urls import path
from exp import views 

urlpatterns = [
    path('', views.HomeView.as_view(), name='exp-home'),
    path('all', views.ExperimentsView.as_view(), name='exp-all'),
    path('<int:exp_id>', views.ExperimentView.as_view(), name='exp-single'),
    path('create-descriptor', views.DescriptorMapFormView.as_view(), name='create-descriptor'),
    
]