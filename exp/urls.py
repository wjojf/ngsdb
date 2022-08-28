from django.urls import path
from exp import views 


urlpatterns = [
    path('all/', views.HomeView.as_view(), name='exp_home_view'),
    path('upload/', views.UploadCSVView.as_view(), name='exp_upload_view'),
    path('<int:exp_id>', views.UpdateExperimentView.as_view(), name='exp_update_view'),
    path('create/', views.AddExperimentView.as_view(),
        name='exp_create_view'),
    path('import/', views.ImportCSVView.as_view(),
        name='exp_import_view'),
    #path('create-descriptor', views.DescriptorMapFormView.as_view(), name='create-descriptor'),
    
]
