from django.core.exceptions import FieldError
from django.urls import resolve, reverse
from django.http import HttpResponseRedirect
from django.views.generic import list, edit, base
from django.core.exceptions import FieldDoesNotExist
from django.forms.models import modelformset_factory
from django.utils.encoding import smart_str

ALLOWED_LOOKUP_TYPES = ('iexact', 'icontains', 'in', 'gt', 'gte', 'lt',
        'lte', 'istratswith', 'iendswith', 'range', 'isnull', 'iregex')


class BaseFormsetView(edit.ProcessFormView):
    '''
    A view that allows saving data from a (model) formset.
    '''
    success_url = None
    cancel_url = None
    formset_class = None
    
    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.cancel_url)

    def post(self, request, *args, **kwargs):
        formset = self.formset_class(request.POST)
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)

    def formset_valid(self, formset):
        self.objects = formset.save()
        return HttpResponseRedirect(self.success_url)

    def formsetinvalid(self, formset):
        return HttpResponseRedirect(self.cancel_url)


class FilteredModelView(list.ListView, edit.BaseFormView):
    '''
    List view subclass implementing  simple filtering via
    GET search form.
    
    Subclasses must define:
        - model
        - template_name
        - search_form_class

    '''

    search_form_class = None
    model = None
    
    def __init__(self, **kwargs):
        kwargs.update({'filters': {},})
        super(FilteredModelView, self).__init__(**kwargs)
        self.form_class = self.search_form_class

    def get(self, request, *args, **kwargs):
        # GET dictionary needs to be copied if we want to modify it
        params = request.GET.copy()
        params.pop('page', None)
        params.pop('_filter', None)
        opts = self.model._meta
        if '_clear' in params:
            # Filters need to be explicitly cleared
            self.filters.clear()
            self.initial.clear()
        else:
            self.initial = params
            for k, v in params.items():
                if not v:
                    # Get rid of empty parameters
                    self.filters.pop(k, None)
                    continue
                bits = k.split('__')
                if bits[-1] in ALLOWED_LOOKUP_TYPES:
                    self.filters.update({smart_str(k): v,})
                else:
                    # Deafult lookup type
                    # first item in bits will be the field name
                    try:
                        f = opts.get_field(bits[0])
                        self.filters.update({smart_str('%s__icontains' % k): v,})
                    except FieldDoesNotExist:
                        # ignore bogus fields
                        continue
        # This is from BaseListView
        self.object_list = self.get_queryset()
        self.allow_empty = self.get_allow_empty()
        if not self.allow_empty and len(self.object_list) == 0:
            raise Http404(u'Empty list and "%(class_name)s.allow_empty" is False.'
                    % {'class_name': self.__class__.__name__})
        context = self.get_context_data(object_list=self.object_list)
        return self.render_to_response(context)

    def get_queryset(self):
        try:
            qs = self.model._default_manager.filter(**self.filters)
        except FieldError:
            qs = self.model._default_manager.all()
            self.filters.clear()
        return qs

    def get_context_data(self, **kwargs):
        context = super(FilteredModelView, self).get_context_data(**kwargs)
        if self.search_form_class is not None:
            context['form'] = self.search_form_class(initial=self.initial)
        return context


class ActionListView(edit.FormView, list.MultipleObjectMixin):
    '''
    List view subclass that implements bulk actions on model instances.
    
    Subclasses must define:
        - model
        - success_url
        - actions: a dictionary of methods (each performing it's own
        action) and POST parameter (button name) that triggers that
        action.
        
    '''

    model = None
    actions = {}
    
    def post(self, request, *args, **kwargs):
        for k, v in self.actions.items():
            try:
                action = getattr(self, k)
                if callable(action) and v in request.POST:
                    sel_list = self.request.POST.getlist('_selected')
                    selected = self.model._default_manager.filter(pk__in=[int(i) for i in sel_list])
                    action(selected)
            except AttributeError:
                continue
        return HttpResponseRedirect(self.get_success_url())
