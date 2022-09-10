from django.urls import path
from django.shortcuts import redirect
from exp import views 


urlpatterns = [
    path('all/', views.HomeView.as_view(), name='exp_home_view'),
    
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('logout', views.logout_user, name='logout'),
    
    path('create/', views.CreateExperimentView.as_view(), name='exp_upload_view'),
    path('update/', views.update_experiments,
        name='update-experiments'),
]
