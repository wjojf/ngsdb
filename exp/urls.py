from django.urls import path
from django.contrib.auth.decorators import login_required
from exp import views 


urlpatterns = [
    path('', views.HomeView.as_view(), name='exp-home'),
    path('all', views.ExperimentsView.as_view(), name='exp-all'),
    path('<int:exp_id>', login_required(views.ExperimentView.as_view(), login_url='login'), name='exp-single'),
    path('create-descriptor', login_required(views.DescriptorMapFormView.as_view(), login_url='login'), name='create-descriptor'),
    
]