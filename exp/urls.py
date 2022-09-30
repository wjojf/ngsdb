from django.urls import path
from exp import views 


urlpatterns = [
    path('all/', views.HomeView.as_view(), name='exp_home_view'),    
    path('create/', views.CreateExperimentView.as_view(), name='exp_upload_view'),
    path('update/', views.update_experiments,
        name='update-experiments'),
    path('edit/<int:exp_id>', views.EditExperimentView.as_view(), name='edit-exp'),
]
