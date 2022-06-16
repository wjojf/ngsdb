from django.urls import path
from exp import views 

urlpatterns = [
    path('', views.home, name='home'),
]