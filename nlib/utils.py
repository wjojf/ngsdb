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


def get_filters(params):
    '''
    Given a dictionary of lookup parameters (usually from query string),
    builds a dictionary that can be used for ORM lookup,
    `lookup_params` and a dictionary to be used in templates
    to render filters `ctx`
    '''

    lookup_params = {}
    ctx = {}
    for k, v in params.items():
        if k.startswith('page'):
            break
        if k.startswith('q'):
            lookup_params['%s__icontains' % smart_str(k[1:])] = v
            ctx['filter'] = '%s contains' % ' '.join(k[1:].split('__'))
        else:
            lookup_params['%s__exact' % smart_str(k)] = v
            ctx['filter'] = ' '.join(k.split('__'))
        ctx['filter_val'] = params[k]
    return lookup_params, ctx

