from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from ngsdb.views import HomeView


urlpatterns = [
    path('', HomeView.as_view(), name='start_view'),
    path('admin/', admin.site.urls),
    path('exp/', include('exp.urls')),
    path('plots/', include('plots.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
