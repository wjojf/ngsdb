from django.forms import widgets
from django.utils.html import format_html

class InlineMixin(object):
    '''
    Input widget subclass that is wrapped in <div> to allow
    per-widget width control in bootstrap 3 inline forms.
    '''
    def __init__(self, attrs=None):
        if attrs is not None:
            self.css_class = attrs.pop('css_class', 'col-xs-3')
        super(InlineMixin, self).__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        inner_html = super(InlineMixin, self).render(name, value, attrs={'class': 'form-control'})
        return format_html('<div class="form-group {}">{}</div>', self.css_class, inner_html)
    
class InlineInput(InlineMixin, widgets.Input):
    pass

class InlineSelect(InlineMixin, widgets.Select):
    pass

class InlinePassword(InlineMixin, widgets.PasswordInput):
    pass
