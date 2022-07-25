from django.utils.safestring import mark_safe
from django.template import Library, Node, TemplateSyntaxError, Variable

from exp.models import DescriptorMap

register = Library()

class CustomFieldsForObjectNode(Node):
    def __init__(self, obj, context_var):
        self.obj = Variable(obj)
        self.context_var = context_var

    def render(self, context):
        context[self.context_var] = DescriptorMap.objects.get_for_object(self.obj.resolve(context))
        return ''

@register.tag(name='custom_fields_for_object')
def do_custom_fields_for_object(parser, token):
    '''
    Retrieves a list of ``FieldTaxonomyMap`` objects and stores them in a context variable.

    Usage::

            {% custom_fields_for_object [object] as [varname] %}

    Example::

            {% custom_fields_for_object foo_strain as fields_list %}
    '''
    bits = token.contents.split()
    if len(bits) != 4:
        raise TemplateSyntaxError('%s tag requires exactly three arguments' % bits[0])
    if bits[2] != 'as':
        raise TemplateSyntaxError('second argument to %s tag must be "as"' % bits[0])
    return CustomFieldsForObjectNode(bits[1], bits[3])
