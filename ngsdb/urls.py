from django.contrib import admin
from django.urls import path, include
from ngsdb.views import HomeView, loginPage, logoutUser, registerPage


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', loginPage, name='login'),
    path('logout/', logoutUser, name='logout'),
    path('register/', registerPage, name='register'),
    path('admin/', admin.site.urls),
    path('exp/', include('exp.urls')),
    path('plots/', include('plots.urls')),
]
