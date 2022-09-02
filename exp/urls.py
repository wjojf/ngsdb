from django.urls import path
from exp import views 


urlpatterns = [
    path('all/', views.HomeView.as_view(), name='exp_home_view'),
    
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('logout', views.logout_user, name='logout'),
    
    path('create/', views.CreateExperimentView.as_view(), name='exp_upload_view'),
    path('import/', views.ImportExperimentsView.as_view(),
        name='exp_import_view'),
]
