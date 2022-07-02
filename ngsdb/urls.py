from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('exp/', include('exp.urls')),
    path('plots/', include('plots.urls')),
]
