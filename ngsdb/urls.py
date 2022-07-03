from django.contrib import admin
from django.urls import path, include
from ngsdb.views import HomeView


urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('admin/', admin.site.urls),
    path('exp/', include('exp.urls')),
    path('plots/', include('plots.urls')),
]
