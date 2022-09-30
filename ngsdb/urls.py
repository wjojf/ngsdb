from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import StartView, MyLoginView, logout_user, ChangePasswordView


urlpatterns = [
    path('', StartView.as_view(), name='start_view'),
    path('admin/', admin.site.urls),

    path('login/', MyLoginView.as_view(), name='login'),
    path('logout', logout_user, name='logout'),
    path('change-password', ChangePasswordView.as_view(), name='password-change'),

    path('exp/', include('exp.urls')),
    path('plots/', include('plots.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
