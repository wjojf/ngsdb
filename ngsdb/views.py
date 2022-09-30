from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth import logout
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect


class StartView(TemplateView):
    template_name = 'start.html'

class MyLoginView(LoginView):
    template_name = 'login.html'

def logout_user(request):
    logout(request)
    return redirect('exp_home_view')

class ChangePasswordView(PasswordChangeView):
    template_name = 'password.html'
    success_url = reverse_lazy('exp_home_view')