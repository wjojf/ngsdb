from django.urls import path
from exp import views 

urlpatterns = [
    path('all/', views.ExperimentsView.as_view(), name='exp_list_view'),
    path('<int:exp_id>', views.ExperimentView.as_view(), name='exp_details_view'),
    path('create/', views.ExperimentCreateView.as_view(),
        name='exp_create_view'),
    path('import/', views.ExperimentImportView.as_view(),
        name='exp_import_view'),
    path('create-descriptor', views.DescriptorMapFormView.as_view(), name='create-descriptor'),
    
]
