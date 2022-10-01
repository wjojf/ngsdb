from django.urls import path
from exp import views 


urlpatterns = [
    path('all/', views.HomeView.as_view(), name='exp_home_view'),    
    path('create/', views.CreateExperimentView.as_view(), name='exp_upload_view'),
    path('edit/<int:exp_id>', views.EditExperimentView.as_view(), name='edit-exp'),
    path('update/', views.update_experiments,
        name='update-experiments'),
    path('delete/<int:exp_id>', views.DeleteExperimentView.as_view(), name='delete-exp'),
]
