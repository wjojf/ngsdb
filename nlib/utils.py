from django.urls import resolve, reverse
from django.db.models import Sum, Avg
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.encoding import smart_str


def build_tabs_dict(request, tabs):
    match = resolve(request.path)
    tab_dict = {}
    for tab,view in tabs.items():
        try:
            view_name, args, kwargs = view
            is_active = match.url_name == view_name
        except ValueError:
            is_active = match.url_name == view
            kwargs = None
            args = []
            view_name = view
        tab_dict[tab] = [reverse(view_name, args=args, kwargs=kwargs), is_active]
    return tab_dict

